import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ask_to_note import build_note, slugify, _parse_cli_json  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "ask_sample.json"


def test_parse_cli_json_strips_matched_prefix():
    raw = 'Matched: 309db161-24f... (Nowosci AI)\n{"answer": "x", "references": []}'
    assert _parse_cli_json(raw) == {"answer": "x", "references": []}


def test_parse_cli_json_plain():
    assert _parse_cli_json('{"answer": "y", "references": []}') == {
        "answer": "y", "references": []}


def test_slugify_basic():
    assert slugify("Co laczy n8n z digestem?") == "co-laczy-n8n-z-digestem"


def test_slugify_caps_length():
    assert len(slugify("slowo " * 50)) <= 80


def test_build_note_has_frontmatter_and_sections():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    md = build_note(
        question="O czym jest notebook?",
        data=data,
        notebook="Testy",
        date="2026-06-11",
        source_titles=None,
    )
    assert md.startswith("---\n")
    assert "title:" in md
    assert "tags:" in md
    assert 'notebook: "Testy"' in md
    assert "# O czym jest notebook?" in md
    assert "## Odpowiedz" in md
    assert "## Cytaty / Zrodla" in md
    assert data["answer"] in md
    for ref in data["references"]:
        assert f"[{ref['citation_number']}]" in md
        assert ref["cited_text"][:30] in md


def test_build_note_maps_source_titles_to_wikilinks():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sid = data["references"][0]["source_id"]
    md = build_note(
        question="Pyt",
        data=data,
        notebook="Testy",
        date="2026-06-11",
        source_titles={sid: "Claude Fable 5 omowienie"},
    )
    assert "[[Claude Fable 5 omowienie]]" in md


def test_build_note_quotes_yaml_values_with_colon():
    md = build_note(
        question="Co to jest: test?",
        data={"answer": "Odp: tak.", "references": []},
        notebook="AI: 2026",
        date="2026-06-11",
        source_titles=None,
    )
    fm = yaml.safe_load(md.split("---")[1])
    assert fm["notebook"] == "AI: 2026"
    assert fm["title"] == "Co to jest: test"
    assert fm["description"] == "Odp: tak."


def test_build_note_no_references():
    md = build_note(
        question="Puste",
        data={"answer": "Inna odpowiedz.", "references": []},
        notebook="Testy",
        date="2026-06-11",
        source_titles=None,
    )
    assert "## Cytaty / Zrodla" in md
    assert "Inna odpowiedz." in md
    assert "_Brak cytowanych zrodel._" in md
