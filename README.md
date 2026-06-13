# Plugin `notebooklm`

[PL](README_PL.md)

[Claude Code](https://claude.com/claude-code) skills for working with **Google NotebookLM**
from inside Claude Code: managing notebooks, adding sources, asking questions
(Q&A with citations saved to a Markdown note), and fetching source transcripts.

Under the hood every skill calls the [`notebooklm-py`](https://github.com/teng-lin/notebooklm-py)
CLI (`python -m notebooklm`).

## Skills

| Skill | Purpose |
|-------|---------|
| **notebooklm-setup** | Install, Google account login, session verification (`login`, `doctor`, `profile`). Shared dependency of the family. |
| **notebooklm-refresh-login** | Refresh an expired Google session on a remote/headless server by copying `storage_state.json` from the desktop (no browser on the server). |
| **notebooklm-notebooks** | Manage notebooks: `list`, `create`, `rename`, `delete`, `use`, `summary`. |
| **notebooklm-sources** | Add and organize sources (URL, YouTube, PDF/MD, text, research agent). |
| **notebooklm-ask** | Ask a notebook → `.md` note with citations (script `ask_to_note.py`). |
| **notebooklm-transcripts** | Full source text (`source fulltext`) → separate notes (script `fetch_transcripts.py`). |

## Installation (two parts)

The plugin provides the skills, but they run on their own CLI backend. Install **both**:

```text
# 1) Skills — Claude Code marketplace
/plugin marketplace add lutencjusz/notebooklm-plugin
/plugin install notebooklm@notebooklm-plugin

# 2) Backend CLI (required)
uv tool install "notebooklm-py[browser]"
```

CLI alternative: `pipx install "notebooklm-py[browser]"`.
First use downloads Chromium (~170 MB). Skipping step 2 is the most common reason for
"I installed it but it doesn't work".

Verify:

```powershell
python -m notebooklm --version
```

## Configuration

Login is **interactive** (it opens a browser) — it cannot be done on the user's behalf.
The **notebooklm-setup** skill walks you through it:

```powershell
notebooklm login              # Google account login (interactive)
python -m notebooklm doctor   # check session/profile state
```

The Google session is stored **locally by `notebooklm-py`** (outside this repo) — the repo
contains no credentials and no `.env` file.

## Requirements

- **Python 3** with the `notebooklm-py` package (the `[browser]` extra).
- **Chromium** (downloaded automatically on first use).
- A signed-in **Google account** (session stored locally by `notebooklm login`).

## Saving notes (ask / transcripts)

The `notebooklm-ask` and `notebooklm-transcripts` skills save their output as Markdown notes:

- `notebooklm-ask` → `Concepts/NotebookLM-answers/` (answer + citations as wikilinks),
- `notebooklm-transcripts` → `Concepts/NotebookLM-transcripts/` (one note per source).

Paths are **relative to the current directory** — run from the root of your Obsidian vault,
or pass `--out` / `--vault`. The skills are Obsidian-friendly (frontmatter, wikilinks,
callouts), but they also work on plain `.md` files.

## ⚠️ Security

- **Do not send confidential/sensitive content to NotebookLM** (passwords, personal data,
  secrets). Adding a source uploads its content to the Google service.
- The repo holds no credentials — the Google session is kept locally by `notebooklm-py`.
- Destructive operations (`notebook delete`, `source delete`) require explicit confirmation.

## Tests

```powershell
python -m pytest skills/notebooklm-ask/scripts/tests
```

## License

[MIT](LICENSE)
