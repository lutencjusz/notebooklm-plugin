---
name: notebooklm-sources
description: 'Zarzadza zrodlami w notebooku Google NotebookLM przez CLI (python -m notebooklm) — dodaje zrodla (URL, YouTube, plik, wklejony tekst, agent research), listuje, pobiera streszczenie (guide), usuwa i zmienia nazwy. Uzywaj gdy uzytkownik prosi "dodaj zrodlo do NotebookLM", "wrzuc ten link/film/PDF do notebooka", "pokaz zrodla w notebooku", "usun zrodlo", "zasil notebook trescia". Czesc rodziny notebooklm-*.'
---

# notebooklm-sources

Dodaje i zarzadza zrodlami w notebooku Google NotebookLM. Notebook-id ustal przez
`[[notebooklm-notebooks]]`; autoryzacja przez `[[notebooklm-setup]]`. Do pobierania
pelnego tekstu zrodel sluzy `[[notebooklm-transcripts]]`.

> ⚠️ **Bezpieczenstwo:** NIE wysylaj do NotebookLM tresci poufnych/wrazliwych
> (hasla, dane osobowe, sekrety).

## Dodawanie zrodel

CLI samo wykrywa typ (url/youtube/plik/tekst). Przyklady:

```powershell
python -m notebooklm source add <notebook> "https://przyklad.pl/artykul"
python -m notebooklm source add <notebook> "https://www.youtube.com/watch?v=..."
python -m notebooklm source add <notebook> "C:\sciezka\plik.pdf"
python -m notebooklm source add <notebook> --text "wklejona tresc"
```

Agent wyszukujacy (web/drive) z auto-importem wynikow:

```powershell
python -m notebooklm source add-research <notebook> "<zapytanie>"
```

Po dodaniu zrodlo moze sie przetwarzac — zaczekaj:

```powershell
python -m notebooklm source wait <source> -n <notebook>
```

## Przegladanie i porzadkowanie

```powershell
python -m notebooklm source list -n <notebook> --json
python -m notebooklm source get <source> -n <notebook>
python -m notebooklm source guide <source> -n <notebook>   # streszczenie + slowa kluczowe
python -m notebooklm source rename <source> "<nowa nazwa>" -n <notebook>
```

**Usuniecie zrodla — wymagaj potwierdzenia** (pokaz tytul/ID), potem:

```powershell
python -m notebooklm source delete <source> -n <notebook>
```

## Obsluga bledow

- Brak CLI / auth wygasl → `[[notebooklm-setup]]`.
- Brak notebooka → `[[notebooklm-notebooks]]` (`list`).
- Fraza nie pasuje do zrodla → pokaz `source list`, zapytaj ktore.
- Proba dodania pliku z trescia poufna/wrazliwa → odmow.

## Weryfikacja

```powershell
python -m notebooklm source list -n <notebook> --json
```

Oczekiwane: JSON z lista zrodel (read-only).
