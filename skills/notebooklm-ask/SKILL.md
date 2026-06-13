---
name: notebooklm-ask
description: 'Zadaje pytanie do notebooka Google NotebookLM i zapisuje odpowiedz z cytatami jako notatke .md w Concepts/NotebookLM-answers/. Uzywaj gdy uzytkownik prosi "zapytaj NotebookLM o...", "co notebook mowi na temat...", "zrob research w NotebookLM i zapisz odpowiedz", "zadaj pytanie notebookowi i wrzuc do vaultu". Skill uruchamia gotowy skrypt ask_to_note.py — nie pisz wlasnego kodu. Czesc rodziny notebooklm-*.'
---

# notebooklm-ask

Zadaje pytanie do wybranego notebooka Google NotebookLM i zapisuje odpowiedz **z cytatami**
jako notatke Markdown w `Concepts/NotebookLM-answers/`. Notebook-id ustal przez
`[[notebooklm-notebooks]]`; autoryzacja przez `[[notebooklm-setup]]`.

Calosc robi skrypt `scripts/ask_to_note.py`. Uruchamiaj go z katalogu glownego
swojego vaultu Obsidian (biezacy katalog = vault), zeby `--out` wskazywal poprawnie.

## Przeplyw

**1. Ustal notebook.** Jesli uzytkownik nie podal — wypisz liste
(`python -m notebooklm list --json`) i zapytaj. Mozna podac fragment tytulu/prefiks ID.

**2. (Opcjonalnie) podejrzyj odpowiedz** bez zapisu:

```powershell
python -m notebooklm ask "<pytanie>" -n "<notebook>" --json
```

**3. Zapisz odpowiedz jako notatke:**

```powershell
python "$env:CLAUDE_PLUGIN_ROOT\skills\notebooklm-ask\scripts\ask_to_note.py" "<pytanie>" -n "<notebook>"
```

Flagi:
- `--out <sciezka>` — inny katalog docelowy (domyslnie `Concepts/NotebookLM-answers/`)
- `--force` — nadpisz istniejaca notatke

Skrypt wypisuje JSON (`file`, `references`).

**4. (Opcjonalnie) sprawdz formatowanie.** Jesli korzystasz z Obsidiana, mozesz dodatkowo
sprawdzic/poprawic frontmatter, wikilinki i callouty wg konwencji swojego vaultu.

## Format notatki

Frontmatter (`title`, `tags: [notebooklm]`, `notebook`, `date`, `description`),
naglowek `# <pytanie>`, sekcja `## Odpowiedz`, sekcja `## Cytaty / Zrodla`
(zrodla jako wikilinki [[tytul]] gdy znane). Nazwa pliku: `YYYY-MM-DD_<slug-pytania>.md`.

## Obsluga bledow

- `Autoryzacja NotebookLM wygasla` → `[[notebooklm-setup]]` (`notebooklm login`).
- Brak notebooka → `[[notebooklm-notebooks]]`.
- `Notatka juz istnieje` → dodaj `--force`.

## Uwagi

- Skill tylko pyta i zapisuje odpowiedz; dodawanie zrodel to `[[notebooklm-sources]]`,
  pobieranie pelnego tekstu zrodel to `[[notebooklm-transcripts]]`.
- Nie wysylaj do NotebookLM tresci poufnych/wrazliwych (hasla, dane osobowe, sekrety).
