"""Pyta NotebookLM (ask --json) i zapisuje odpowiedz jako notatke Obsidian.

Uruchamiaj z katalogu vaultu, np.:
    python AI/skills/notebooklm-ask/scripts/ask_to_note.py "<pytanie>" -n "<notebook>"
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

DEFAULT_OUT = Path("Concepts/NotebookLM-answers")
SLUG_MAX = 80


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    text = text[:SLUG_MAX].strip("-")
    return text or "pytanie"


def _yaml_str(value: str) -> str:
    """Zwroc wartosc YAML w cudzyslowach, eskejpujac znaki specjalne."""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_note(question: str, data: dict, notebook: str, date: str,
               source_titles: dict | None = None) -> str:
    """Zbuduj notatke Markdown z odpowiedzi `ask --json`.

    source_titles: opcjonalna mapa source_id -> tytul zrodla (z `source list`).
    Gdy podana, tytul pojawia sie jako wikilink [[tytul]] przy cytacie.
    """
    source_titles = source_titles or {}
    answer = (data.get("answer") or "").strip()
    refs = data.get("references") or []
    title = question.rstrip("?").replace("\n", " ").strip()
    desc = answer.replace("\n", " ")
    if len(desc) > 140:
        desc = desc[:137] + "..."

    lines = [
        "---",
        f"title: {_yaml_str(title)}",
        "tags: [notebooklm]",
        f"notebook: {_yaml_str(notebook)}",
        f"date: {date}",
        f"description: {_yaml_str(desc)}",
        "---",
        "",
        f"# {question}",
        "",
        "## Odpowiedz",
        "",
        answer,
        "",
        "## Cytaty / Zrodla",
        "",
    ]
    if refs:
        for ref in sorted(refs, key=lambda r: r.get("citation_number", 0)):
            n = ref.get("citation_number", "?")
            sid = ref.get("source_id", "")
            cited = (ref.get("cited_text") or "").strip().replace("\n", " ")
            title_ = source_titles.get(sid)
            if title_:
                safe = title_.replace("|", " ").replace("]]", "")
                head = f"**[{n}]** [[{safe}]]"
            else:
                head = f"**[{n}]** `{sid[:8]}`"
            lines.append(head)
            if cited:
                lines.append(f"> {cited}")
            lines.append("")
    else:
        lines.append("_Brak cytowanych zrodel._")
        lines.append("")
    return "\n".join(lines)


def _run_json(args_list: list) -> dict:
    cmd = [sys.executable, "-m", "notebooklm", *args_list, "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        err = (proc.stderr or "").lower()
        if "login" in err or "auth" in err or "expired" in err:
            sys.exit("Autoryzacja NotebookLM wygasla. Uruchom: notebooklm login")
        sys.exit(f"Blad CLI notebooklm:\n{proc.stderr}")
    try:
        return _parse_cli_json(proc.stdout)
    except json.JSONDecodeError as exc:
        sys.exit(f"Nieprawidlowy JSON z notebooklm: {exc}\n"
                 f"Stdout: {proc.stdout[:200]!r}")


def _parse_cli_json(stdout: str) -> dict:
    """Sparsuj JSON z wyjscia CLI.

    Przy dopasowaniu czesciowym ID CLI poprzedza JSON linia
    `Matched: <id>... (<tytul>)`, wiec szukamy poczatku obiektu/tablicy.
    """
    start = stdout.find("{")
    alt = stdout.find("[")
    if start == -1 or (alt != -1 and alt < start):
        start = alt
    if start == -1:
        raise json.JSONDecodeError("brak JSON w wyjsciu CLI", stdout or "", 0)
    return json.loads(stdout[start:])


def fetch_source_titles(notebook: str) -> dict:
    """Mapa source_id -> tytul, z `source list -n <notebook> --json`."""
    try:
        data = _run_json(["source", "list", "-n", notebook])
    except SystemExit as exc:
        print(f"Uwaga: nie pobrano listy zrodel ({exc}); cytaty bez wikilinkow.",
              file=sys.stderr)
        return {}
    return {s["id"]: s.get("title", s["id"]) for s in data.get("sources", [])}


def main() -> None:
    ap = argparse.ArgumentParser(description="NotebookLM ask -> notatka Obsidian")
    ap.add_argument("question")
    ap.add_argument("-n", "--notebook", required=True)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    data = _run_json(["ask", args.question, "-n", args.notebook])
    source_titles = fetch_source_titles(args.notebook)
    date = _dt.date.today().isoformat()
    md = build_note(args.question, data, args.notebook, date, source_titles)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{date}_{slugify(args.question)}.md"
    if path.exists() and not args.force:
        sys.exit(f"Notatka juz istnieje (uzyj --force): {path}")
    path.write_text(md, encoding="utf-8")
    print(json.dumps({"file": str(path),
                      "references": len(data.get("references") or [])},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
