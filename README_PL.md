# Plugin `notebooklm`

[EN](README.md)

Skille [Claude Code](https://claude.com/claude-code) do obsługi **Google NotebookLM**
z poziomu Claude Code: zarządzanie notebookami, dodawanie źródeł, zadawanie pytań
(Q&A z cytatami zapisywane do notatki Markdown) oraz pobieranie transkryptów źródeł.

Pod spodem każdy skill woła CLI [`notebooklm-py`](https://github.com/teng-lin/notebooklm-py)
(`python -m notebooklm`).

## Skille

| Skill | Zastosowanie |
|-------|--------------|
| **notebooklm-setup** | Instalacja, logowanie kontem Google, weryfikacja sesji (`login`, `doctor`, `profile`). Wspólna zależność rodziny. |
| **notebooklm-notebooks** | Zarządzanie notebookami: `list`, `create`, `rename`, `delete`, `use`, `summary`. |
| **notebooklm-sources** | Dodawanie i porządkowanie źródeł (URL, YouTube, PDF/MD, tekst, agent research). |
| **notebooklm-ask** | Pytanie do notebooka → notatka `.md` z cytatami (skrypt `ask_to_note.py`). |
| **notebooklm-transcripts** | Pełny tekst źródeł (`source fulltext`) → osobne notatki (skrypt `fetch_transcripts.py`). |

## Instalacja (dwuczęściowa)

Plugin dostarcza skille, ale pracują one na własnym backendzie CLI. Zainstaluj **oba**:

```text
# 1) Skille — marketplace Claude Code
/plugin marketplace add lutencjusz/notebooklm-plugin
/plugin install notebooklm@notebooklm-plugin

# 2) Backend CLI (wymagany)
uv tool install "notebooklm-py[browser]"
```

Alternatywa dla CLI: `pipx install "notebooklm-py[browser]"`.
Pierwsze użycie pobiera Chromium (~170 MB). Pominięcie kroku 2 to najczęstszy powód
„zainstalowałem, a nie działa".

Weryfikacja:

```powershell
python -m notebooklm --version
```

## Konfiguracja

Logowanie jest **interaktywne** (otwiera przeglądarkę) — nie da się go wykonać za
użytkownika. Przeprowadza je skill **notebooklm-setup**:

```powershell
notebooklm login          # logowanie kontem Google (interaktywne)
python -m notebooklm doctor   # sprawdzenie stanu sesji/profilu
```

Sesja Google jest zapisywana **lokalnie przez `notebooklm-py`** (poza tym repo) — w repo
nie ma żadnych poświadczeń ani pliku `.env`.

## Wymagania

- **Python 3** z pakietem `notebooklm-py` (ekstras `[browser]`).
- **Chromium** (pobierany automatycznie przy pierwszym użyciu).
- Zalogowane **konto Google** (sesja zapisana lokalnie przez `notebooklm login`).

## Zapis notatek (ask / transcripts)

Skille `notebooklm-ask` i `notebooklm-transcripts` zapisują wyniki jako notatki Markdown:

- `notebooklm-ask` → `Concepts/NotebookLM-answers/` (odpowiedź + cytaty jako wikilinki),
- `notebooklm-transcripts` → `Concepts/NotebookLM-transcripts/` (jedna notatka na źródło).

Ścieżki są **względne do bieżącego katalogu** — uruchamiaj z katalogu głównego swojego
vaultu Obsidian, albo podaj `--out` / `--vault`. Skille są przyjazne Obsidianowi
(frontmatter, wikilinki, callouty), ale działają też na zwykłych plikach `.md`.

## ⚠️ Bezpieczeństwo

- **Nie wysyłaj do NotebookLM treści poufnych/wrażliwych** (hasła, dane osobowe, sekrety).
  Dodanie źródła wysyła jego treść do usługi Google.
- W repo nie ma poświadczeń — sesja Google jest trzymana lokalnie przez `notebooklm-py`.
- Operacje destrukcyjne (`notebook delete`, `source delete`) wymagają jawnego potwierdzenia.

## Testy

```powershell
python -m pytest skills/notebooklm-ask/scripts/tests
```

## Licencja

[MIT](LICENSE)
