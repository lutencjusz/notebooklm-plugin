---
name: notebooklm-setup
description: 'Konfiguruje i weryfikuje dostep do Google NotebookLM przez CLI notebooklm-py (python -m notebooklm) — sprawdza instalacje, prowadzi przez logowanie kontem Google i potwierdza autoryzacje. Uzywaj gdy uzytkownik prosi "skonfiguruj NotebookLM", "zaloguj do NotebookLM", "sprawdz czy NotebookLM dziala", "NotebookLM auth", albo gdy inny skill notebooklm-* zglosi blad autoryzacji. Wspolna zaleznosc rodziny notebooklm-*.'
---

# notebooklm-setup

Weryfikuje srodowisko i sesje Google NotebookLM. CLI to pakiet **notebooklm-py**,
wywolywany przez `python -m notebooklm`. Pozostale skille rodziny
(`[[notebooklm-notebooks]]`, `[[notebooklm-sources]]`, `[[notebooklm-ask]]`,
`[[notebooklm-transcripts]]`) przy bledzie autoryzacji odsylaja tutaj. Dla serwerow
zdalnych/headless (gdzie nie ma przegladarki do logowania) sesje odswieza
`[[notebooklm-refresh-login]]`.

## Kiedy uzyc

- Pierwsze uruchomienie / brak dzialajacego CLI
- Komunikat o wygaslej autoryzacji z innego skilla notebooklm-*
- Sprawdzenie, ktore konto/profil jest aktywne

## Procedura

**1. Sprawdz, czy CLI dziala:**

```powershell
python -m notebooklm --version
```

Jesli polecenie nie istnieje — CLI nie jest zainstalowane. Poinstruuj uzytkownika:

```powershell
uv tool install "notebooklm-py[browser]"
```

(alternatywa: `pipx install "notebooklm-py[browser]"`). Pierwsze uzycie pobiera
Chromium (~170 MB).

**2. Sprawdz autoryzacje:**

```powershell
python -m notebooklm doctor
```

`doctor` raportuje stan profilu, sesji i ewentualnej migracji
(`--json` dla wersji maszynowej, `--fix` by naprawic wykryte problemy).

**3. Logowanie (tylko gdy auth wygasl).** Logowanie jest **interaktywne** (otwiera
przegladarke) — NIE da sie go zrobic za uzytkownika. Poinstruuj go, by sam wykonal:

```powershell
notebooklm login
```

Organizacje wymagajace Edge: `notebooklm login --browser msedge`.
Ponowne uzycie istniejacej sesji przegladarki: `notebooklm login --browser-cookies chrome`.

**4. Profile (opcjonalnie).** Przelaczanie konta Google:

```powershell
python -m notebooklm profile list
python -m notebooklm profile switch <nazwa>
```

## Weryfikacja

Read-only, bez efektow ubocznych:

```powershell
python -m notebooklm doctor
python -m notebooklm list --json
```

Oczekiwane: `doctor` bez bledow auth, `list` zwraca JSON z notebookami.
Jesli blad autoryzacji — wroc do kroku 3.

## Uwagi

- Logowania nie wykonujemy za uzytkownika (konto Google, interaktywne).
- Nie wysylaj do NotebookLM tresci poufnych/wrazliwych (hasla, dane osobowe, sekrety).
