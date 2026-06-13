---
name: notebooklm-notebooks
description: 'Zarzadza notebookami Google NotebookLM przez CLI (python -m notebooklm) — listuje, tworzy, zmienia nazwe, usuwa notebooki, ustawia biezacy kontekst i pobiera AI-podsumowanie. Uzywaj gdy uzytkownik prosi "pokaz moje notebooki NotebookLM", "utworz notebook", "zmien nazwe notebooka", "usun notebook", "ktory notebook jest aktywny", albo gdy inny skill potrzebuje ID notebooka. Czesc rodziny notebooklm-*.'
---

# notebooklm-notebooks

Zarzadza notebookami w Google NotebookLM. Daje ID notebooka, ktorego uzywaja
`[[notebooklm-sources]]`, `[[notebooklm-ask]]` i `[[notebooklm-transcripts]]`.
Autoryzacja: `[[notebooklm-setup]]`.

## Wybor notebooka

CLI obsluguje **dopasowanie czesciowe** — wystarczy fragment tytulu lub prefiks ID.
Gdy uzytkownik nie poda — najpierw wypisz liste i zapytaj.

## Operacje

**Lista notebookow:**

```powershell
python -m notebooklm list --json
```

**Utworz notebook:**

```powershell
python -m notebooklm create "<tytul>" --json
```

**Zmien nazwe:**

```powershell
python -m notebooklm rename <notebook> "<nowy tytul>"
```

**Ustaw biezacy kontekst** (kolejne komendy bez `-n`):

```powershell
python -m notebooklm use <notebook>
python -m notebooklm status
```

**AI-podsumowanie notebooka:**

```powershell
python -m notebooklm summary -n <notebook>
```

**Usun notebook — OPERACJA NIEODWRACALNA.** Wymagaj jawnego potwierdzenia
uzytkownika (pokaz tytul + ID), dopiero potem:

```powershell
python -m notebooklm delete <notebook>
```

## Obsluga bledow

- Brak dzialajacego CLI / auth wygasl → `[[notebooklm-setup]]`.
- Fraza nie pasuje do zadnego notebooka → pokaz `list --json`, zapytaj ktory.

## Weryfikacja

```powershell
python -m notebooklm list --json
```

Oczekiwane: JSON z lista notebookow (read-only).