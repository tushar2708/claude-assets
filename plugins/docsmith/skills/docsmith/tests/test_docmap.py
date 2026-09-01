"""Tests for docsmith_lib.docmap — matching semantics ported from the
smritea posttooluse hook's find_matching_docs."""

import pytest

from docsmith_lib.docmap import (
    find_matching_docs,
    load_docmap,
    migrate_legacy,
    normalize_entries,
)


@pytest.fixture
def doc_map(fixture_project):
    return load_docmap(fixture_project)["map"]


def test_load_docmap_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_docmap(tmp_path)


def test_load_docmap_bad_version_raises(tmp_path):
    docmap_dir = tmp_path / ".docsmith"
    docmap_dir.mkdir(parents=True)
    (docmap_dir / "docmap.json").write_text('{"version": 2, "map": {}}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_docmap(tmp_path)


def test_prefix_match(doc_map):
    docs = find_matching_docs("src/anything.py", doc_map)
    assert [doc["path"] for doc in docs] == ["docs/pipeline/overview.md"]
    assert docs[0]["reason"] == "pipeline docs"


def test_exact_match(doc_map):
    docs = find_matching_docs("main.go", doc_map)
    assert len(docs) == 1
    assert docs[0]["path"] == "docs/pipeline/overview.md"
    assert docs[0]["message"] == "update the entry-point section"


def test_no_match(doc_map):
    assert find_matching_docs("other.txt", doc_map) == []


def test_multi_key_dedupe_first_seen_wins(doc_map):
    doc_map = dict(doc_map)
    doc_map["src/deep/"] = [
        {"path": "docs/pipeline/overview.md", "reason": "second reason", "message": "later"}
    ]
    docs = find_matching_docs("src/deep/file.go", doc_map)
    # Both "src/" and "src/deep/" match; one entry per doc path survives.
    assert [doc["path"] for doc in docs] == ["docs/pipeline/overview.md"]
    # Keys iterate in sorted order, so "src/" is seen first and its
    # reason/message win.
    assert docs[0]["reason"] == "pipeline docs"


def test_legacy_string_entry_normalized(doc_map):
    docs = find_matching_docs("src/util/x.go", doc_map)
    paths = [doc["path"] for doc in docs]
    assert "docs/pipeline/overview.md" in paths  # from "src/"
    assert "docs/reference/util-reference.md" in paths  # legacy string under "src/util/"
    legacy = next(doc for doc in docs if doc["path"] == "docs/reference/util-reference.md")
    assert legacy == {"path": "docs/reference/util-reference.md", "reason": "", "message": ""}


def test_normalize_entries_skips_pathless():
    entries = normalize_entries([{"reason": "no path"}, "docs/a.md", {"path": "docs/b.md"}])
    assert entries == [
        {"path": "docs/a.md", "reason": "", "message": ""},
        {"path": "docs/b.md", "reason": "", "message": ""},
    ]


def test_migrate_legacy_drops_underscore_keys():
    legacy = {
        "_comment": "ignore me",
        "src/": ["docs/a.md"],
        "b.go": [{"path": "docs/b.md", "reason": "r"}],
    }
    migrated = migrate_legacy(legacy, "2026-08-25T00:00:00+00:00")
    assert migrated["version"] == 1
    assert migrated["updated_at"] == "2026-08-25T00:00:00+00:00"
    assert "_comment" not in migrated["map"]
    assert migrated["map"]["src/"] == [{"path": "docs/a.md", "reason": "", "message": ""}]
    assert migrated["map"]["b.go"] == [{"path": "docs/b.md", "reason": "r", "message": ""}]
