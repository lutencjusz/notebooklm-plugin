---
name: notebooklm-transcripts
description: 'Pobiera transkrypty (fulltext) zrodel z notebooka Google NotebookLM przez CLI notebooklm-py i zapisuje je jako osobne notatki .md (jedna na zrodlo) w Concepts/NotebookLM-transcripts/. Uzywaj gdy uzytkownik prosi o "pobierz transkrypcje z NotebookLM", "wyciagnij transkrypty z notebooka", "sciagnij fulltext zrodel", "zapisz transkrypcje filmu z notatki NotebookLM" lub podaje nazwe/ID notebooka i chce miec jego tresc w vaultcie. Skill uruchamia gotowy skrypt Python — nie pisz wlasnego kodu.'
---

# NotebookLM transcripts

Wyciaga **pelny tekst zrodel** (`source fulltext`) z wybranego notebooka Google
NotebookLM i zapisuje kazde zrodlo jako osobna notatke Markdown w
`Concepts/NotebookLM-transcripts/`. "Transkrypt" = oczyszczona tresc, ktora
NotebookLM zindeksowal ze zrodla (transkrypt filmu YouTube, tekst PDF, tresc
strony WWW).

Korzysta z CLI `notebooklm` (pakiet **notebooklm-py**, wywolywany przez
`python -m notebooklm`).

## Kiedy uzyc

- Uzytkownik chce miec transkrypcje/tresc zrodel z konkretnego notebooka w vaultcie
- Chce zasilic istniejaca notatke trescia z transkryptu (najpierw sciagnij transkrypt, potem analizuj)
- Pyta jakie zrodla sa w notebooku (tryb `--list`)

## Przeplyw

Calosc robi skrypt `scripts/fetch_transcripts.py`. Domyslnie zapisuje do podkatalogu
`Concepts/NotebookLM-transcripts/` wzgledem biezacego katalogu — uruchamiaj go z katalogu
glownego swojego vaultu Obsidian, albo wskaz vault jawnie flaga `--vault <sciezka>`.

**1. Ustal notebook.** Jesli uzytkownik nie podal nazwy/ID — wypisz dostepne notebooki:

```powershell
python "$env:CLAUDE_PLUGIN_ROOT\skills\notebooklm-transcripts\scripts\fetch_transcripts.py" --list
```

Pokaz liste uzytkownikowi i zapytaj, ktory notebook. Mozna podac **fragment tytulu
lub fragment ID** (CLI dopasowuje prefiks ID i podciag tytulu).

**2. (Opcjonalnie) podejrzyj zrodla** przed pobraniem:

```powershell
python "$env:CLAUDE_PLUGIN_ROOT\skills\notebooklm-transcripts\scripts\fetch_transcripts.py" "<notebook>" --list
```

**3. Pobierz transkrypty** (jedna notatka na zrodlo do `Concepts/NotebookLM-transcripts/`):

```powershell
python "$env:CLAUDE_PLUGIN_ROOT\skills\notebooklm-transcripts\scripts\fetch_transcripts.py" "<notebook>"
```

Przydatne flagi:
- `--source <prefix>` — tylko wybrane zrodla po prefiksie ID (mozna powtarzac)
- `--format text` — wymus zwykly tekst (markdown wymaga `pip install "notebooklm-py[markdown]"`; skrypt i tak sam zrobi fallback do text)
- `--force` — nadpisz istniejace notatki (domyslnie istniejace sa pomijane)
- `--out <sciezka>` — inny katalog docelowy niz domyslny

Skrypt na koniec wypisuje podsumowanie JSON (`sources`, `written`, `files`).

**4. (Opcjonalnie) sprawdz formatowanie.** Jesli korzystasz z Obsidiana, mozesz
po zapisaniu zweryfikowac/poprawic frontmatter, wikilinki i callouty zgodnie
z konwencja swojego vaultu.

## Format notatki

Kazda notatka ma frontmatter (`title`, `tags: [transcript]`, `source_url`,
`notebook`, `notebook_source_id`, `date`, `description`), naglowek `# <tytul>`,
callout `[!info]` ze zrodlem oraz sekcje `## Transkrypt` z trescia.
Nazwa pliku: `YYYY-MM-DD_<slug-tytulu>.md`.

## Autoryzacja

CLI wymaga zalogowanej sesji Google. Jesli skrypt zwroci
**"Autoryzacja NotebookLM wygasla. Uruchom: notebooklm login"** — poinformuj
uzytkownika, ze musi sam wykonac (otwiera przegladarke):

```
notebooklm login
```

Nie da sie zalogowac za uzytkownika — to interaktywne logowanie kontem Google.
Weryfikacja: `notebooklm auth check --test`.

## Reczny fallback (gdy skrypt zawiedzie)

Kluczowe komendy CLI, gdyby trzeba bylo zrobic cos recznie:

```powershell
python -m notebooklm list --json                          # notebooki
python -m notebooklm source list -n <notebook-id> --json  # zrodla w notebooku
python -m notebooklm source fulltext <source-id> -n <notebook-id> -o out.md  # transkrypt
```

`source fulltext` przyjmuje pelne UUID lub prefiks ID zrodla.

## Uwagi

- Skill dotyczy tylko pobierania tresci z NotebookLM — nie generuje audio/video/quizow (do tego sluza komendy `notebooklm generate ...`).
- Domyslny katalog `Concepts/NotebookLM-transcripts/` jest tworzony automatycznie.

## Powiazania

Czesc rodziny **notebooklm-***: `[[notebooklm-setup]]` (autoryzacja),
`[[notebooklm-notebooks]]` (wybor notebooka), `[[notebooklm-sources]]`
(dodawanie zrodel), `[[notebooklm-ask]]` (pytania -> notatki).
