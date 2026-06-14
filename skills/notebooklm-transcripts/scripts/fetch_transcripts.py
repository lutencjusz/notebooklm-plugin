#!/usr/bin/env python3
"""Pobiera transkrypty (fulltext) zrodel z notebooka Google NotebookLM
i zapisuje je jako osobne notatki .md (jedna na zrodlo) w vaultcie Obsidian.

Uzywa CLI `notebooklm` (pakiet notebooklm-py). Wywolanie:

    python fetch_transcripts.py "<notebook>" [opcje]

gdzie <notebook> to fragment ID lub fragment tytulu notebooka.
Bez argumentu notebooka skrypt wypisze liste dostepnych notebookow i zakonczy.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import tempfile

# Komenda bazowa CLI. Na Windows `notebooklm` bywa poza PATH, wiec domyslnie
# wywolujemy modul przez biezacy interpreter. Mozna nadpisac przez NOTEBOOKLM_CMD.
_DEFAULT_CMD = os.environ.get("NOTEBOOKLM_CMD", f"{sys.executable} -m notebooklm")
BASE_CMD = _DEFAULT_CMD.split()


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        BASE_CMD + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def fail(msg: str, code: int = 1):
    print(f"BLAD: {msg}", file=sys.stderr)
    sys.exit(code)


def parse_json(stdout: str, context: str):
    stdout = stdout.strip()
    if not stdout:
        fail(f"Pusta odpowiedz przy: {context}")
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        fail(f"Nie-JSON przy {context}:\n{stdout[:500]}")
    # Wykryj komunikat o wygaslej autoryzacji.
    if isinstance(data, dict) and data.get("error"):
        msg = data.get("message", "")
        if "login" in msg.lower() or "auth" in msg.lower():
            fail("Autoryzacja NotebookLM wygasla. Uruchom: notebooklm login")
        fail(f"CLI zwrocilo blad przy {context}: {msg}")
    return data


def pick(d: dict, *keys, default=""):
    """Zwraca pierwsza obecna i niepusta wartosc sposrod podanych kluczy."""
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def slugify(text: str, maxlen: int = 60) -> str:
    text = (text or "bez-tytulu").strip().lower()
    # Spolszczone znaki -> ASCII na potrzeby nazwy pliku.
    repl = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
    text = text.translate(repl)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return (text[:maxlen].rstrip("-")) or "bez-tytulu"


def list_notebooks() -> list[dict]:
    res = run(["list", "--json"])
    data = parse_json(res.stdout or res.stderr, "list --json")
    if isinstance(data, dict):
        data = data.get("notebooks") or data.get("items") or []
    return data


def resolve_notebook(query: str, notebooks: list[dict]) -> dict:
    q = query.lower()
    by_id = [nb for nb in notebooks
             if str(pick(nb, "id", "notebook_id", "notebookId")).lower().startswith(q)]
    by_title = [nb for nb in notebooks
                if q in str(pick(nb, "title", "name", "emoji_title")).lower()]
    matches = by_id or by_title
    # Deduplikacja po id.
    seen, uniq = set(), []
    for nb in matches:
        nid = pick(nb, "id", "notebook_id", "notebookId")
        if nid not in seen:
            seen.add(nid)
            uniq.append(nb)
    if not uniq:
        fail(f"Nie znaleziono notebooka pasujacego do '{query}'.")
    if len(uniq) > 1:
        lines = "\n".join(
            f"  - {pick(nb, 'title', 'name')} [{pick(nb, 'id', 'notebook_id')}]"
            for nb in uniq
        )
        fail(f"Niejednoznaczne '{query}'. Pasuje wiele notebookow:\n{lines}")
    return uniq[0]


def list_sources(nb_id: str) -> list[dict]:
    res = run(["source", "list", "-n", nb_id, "--json"])
    data = parse_json(res.stdout or res.stderr, "source list --json")
    if isinstance(data, dict):
        data = data.get("sources") or data.get("items") or []
    return data


def fetch_fulltext(nb_id: str, src_id: str, fmt: str) -> str | None:
    """Zwraca tekst transkryptu albo None gdy nie udalo sie pobrac."""
    # mktemp zwraca sciezke bez tworzenia pliku — CLI musi sam go stworzyc.
    # NamedTemporaryFile tworzy pusty plik z gory, co na Windows blokuje zapis przez subprocess.
    tmp = tempfile.mktemp(suffix=".txt")
    try:
        args = ["source", "fulltext", src_id, "-n", nb_id, "-o", tmp]
        if fmt == "markdown":
            args += ["-f", "markdown"]
        res = run(args)
        try:
            with open(tmp, encoding="utf-8") as fh:
                content = fh.read().strip()
        except FileNotFoundError:
            content = ""
        if not content:
            # Markdown wymaga extry (notebooklm-py[markdown]); sprobuj plain text.
            if fmt == "markdown":
                return fetch_fulltext(nb_id, src_id, "text")
            stderr = (res.stderr or "").strip()
            if stderr:
                print(f"  ! pominieto {src_id}: {stderr[:160]}", file=sys.stderr)
            return None
        return content
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def write_note(out_dir: str, date: str, source: dict, nb_title: str,
               body: str, force: bool, fname: str) -> str | None:
    title = pick(source, "title", "name", default="bez tytulu")
    src_id = pick(source, "id", "source_id", "sourceId")
    url = pick(source, "url", "source_url", "uri")
    stype = str(pick(source, "type", "source_type", "kind", default=""))
    # Normalizuj wyciekly repr enuma, np. "SourceType.YOUTUBE" -> "youtube".
    if "." in stype:
        stype = stype.rsplit(".", 1)[-1]
    stype = stype.lower()

    path = os.path.join(out_dir, fname)
    if os.path.exists(path) and not force:
        print(f"  = pominieto (istnieje): {fname}")
        return None

    fm = ["---", f'title: "{str(title).replace(chr(34), chr(39))}"', "tags:",
          "  - transcript"]
    if stype:
        fm.append(f"source_type: {stype}")
    if url:
        fm.append(f"source_url: {url}")
    fm += [
        f'notebook: "{nb_title.replace(chr(34), chr(39))}"',
        f"notebook_source_id: {src_id}",
        f"date: {date}",
        f'description: "Transkrypt zrodla \'{str(title)[:80]}\' z notebooka '
        f'NotebookLM {nb_title[:40]}."',
        "---",
        "",
        f"# {title}",
        "",
        f"> [!info] Zrodlo transkryptu",
        f"> Pobrane z notebooka NotebookLM **{nb_title}** przez `notebooklm source fulltext`.",
    ]
    if url:
        fm.append(f"> Oryginal: {url}")
    fm += ["", "## Transkrypt", "", body, ""]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(fm))
    print(f"  + zapisano: {fname}")
    return path


def main():
    # Konsola Windows (cp1250) wywala sie na emoji w tytulach — wymus UTF-8 na stdout.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Pobierz transkrypty zrodel z NotebookLM.")
    ap.add_argument("notebook", nargs="?", help="Fragment ID lub tytulu notebooka")
    ap.add_argument("--out", default=os.path.join("Concepts", "NotebookLM-transcripts"),
                    help="Katalog docelowy (wzgledem --vault)")
    # Domyslny vault liczony od polozenia skryptu (.../<vault>/AI/skills/
    # notebooklm-transcripts/scripts/fetch_transcripts.py), nie od cwd —
    # cwd procesu bywa rozny i nie jest wiarygodny.
    default_vault = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    ap.add_argument("--vault", default=default_vault, help="Sciezka bazowa vaultu")
    ap.add_argument("--format", choices=["markdown", "text"], default="markdown")
    ap.add_argument("--source", action="append", default=[],
                    help="Pobierz tylko zrodla o tym prefiksie ID (mozna podac wiele razy)")
    ap.add_argument("--force", action="store_true", help="Nadpisz istniejace notatki")
    ap.add_argument("--list", action="store_true", help="Tylko wypisz notebooki/zrodla")
    args = ap.parse_args()

    notebooks = list_notebooks()
    if not args.notebook or (args.list and not args.notebook):
        print("Dostepne notebooki:")
        for nb in notebooks:
            print(f"  - {pick(nb, 'title', 'name')} "
                  f"[{pick(nb, 'id', 'notebook_id')}]")
        print("\nPodaj fragment ID lub tytulu jako pierwszy argument.")
        return

    nb = resolve_notebook(args.notebook, notebooks)
    nb_id = pick(nb, "id", "notebook_id", "notebookId")
    nb_title = str(pick(nb, "title", "name", default=nb_id))
    sources = list_sources(nb_id)
    if args.source:
        prefixes = tuple(args.source)
        sources = [s for s in sources
                   if str(pick(s, "id", "source_id")).startswith(prefixes)]

    print(f"Notebook: {nb_title} [{nb_id}] — zrodel: {len(sources)}")
    if args.list:
        for s in sources:
            print(f"  - {pick(s, 'title', 'name')} [{pick(s, 'id', 'source_id')}]")
        return
    if not sources:
        fail("Brak zrodel do pobrania.")

    out_dir = os.path.join(args.vault, args.out)
    os.makedirs(out_dir, exist_ok=True)
    date = _dt.date.today().isoformat()

    # Wylicz nazwy plikow z gory; przy kolizji skrotu dodaj fragment ID zrodla,
    # zeby dwa rozne zrodla o podobnym tytule nie nadpisaly sie / nie zostaly pominiete.
    slug_counts: dict[str, int] = {}
    for s in sources:
        slug_counts[slugify(str(pick(s, "title", "name")))] = \
            slug_counts.get(slugify(str(pick(s, "title", "name"))), 0) + 1

    written = []
    for s in sources:
        src_id = pick(s, "id", "source_id", "sourceId")
        title = pick(s, "title", "name", default=src_id)
        slug = slugify(str(title))
        if slug_counts.get(slug, 0) > 1:
            slug = f"{slug}-{str(src_id)[:6]}"
        fname = f"{date}_{slug}.md"
        print(f"- {title}")
        body = fetch_fulltext(nb_id, src_id, args.format)
        if not body:
            continue
        p = write_note(out_dir, date, s, nb_title, body, args.force, fname)
        if p:
            written.append(os.path.relpath(p, args.vault))

    print("\n" + json.dumps(
        {"notebook": nb_title, "sources": len(sources),
         "written": len(written), "files": written},
        ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
