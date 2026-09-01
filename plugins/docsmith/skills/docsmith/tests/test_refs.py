"""Tests for docsmith_lib.refs — extraction table and resolution states."""

from docsmith_lib.refs import Ref, extract, resolve


def _triples(refs):
    return [(ref.path, ref.symbol, ref.line_no) for ref in refs]


# --- extraction: positives ---------------------------------------------------


def test_extract_backtick_path():
    assert _triples(extract("See `src/main.go` for details.\n")) == [("src/main.go", None, 1)]


def test_extract_backtick_with_symbol():
    assert _triples(extract("Call `src/main.go#HandleThing` now.\n")) == [
        ("src/main.go", "HandleThing", 1)
    ]


def test_extract_link_target():
    assert _triples(extract("See [overview](docs/pipeline/overview.md).\n")) == [
        ("docs/pipeline/overview.md", None, 1)
    ]


# --- extraction: negatives ---------------------------------------------------


def test_extract_rejects_http_url():
    assert extract("Visit `http://x.com/a.md` or [site](http://x.com/a.md).\n") == []


def test_extract_rejects_bare_word():
    assert extract("The `main` function does the work.\n") == []


def test_extract_rejects_dotted_identifiers_and_hosts():
    # No '/' -> never a path: Go/Python dotted identifiers, config keys,
    # hostnames, IPs, version numbers must not be treated as file refs.
    for token in (
        "service.name", "django.contrib.contenttypes", "cfg.Jobs.Enable",
        "prod.smritea.ai", "100.64.1.2", "99.9", "main.go", "config.yaml",
    ):
        assert extract(f"See `{token}` here.\n") == [], token


def test_extract_slashed_extension_allowlist():
    # With a '/', a known code/doc extension or no extension qualifies; an
    # unknown "extension" (a symbol or version segment) does not.
    assert [r.path for r in extract("`cloud_backend/studio-api/main.go`\n")] == [
        "cloud_backend/studio-api/main.go"
    ]
    assert [r.path for r in extract("`cloud_backend/studio-api`\n")] == [
        "cloud_backend/studio-api"
    ]
    assert extract("`pkg/store.HandleThing`\n") == []  # slash + unknown ext
    assert extract("`api/v1.0`\n") == []  # slash + version, not a file


def test_extract_rejects_anchor_link():
    assert extract("Jump to [section](#entry-point).\n") == []


def test_extract_ignores_fenced_code_blocks():
    text = (
        "Intro line.\n"
        "```go\n"
        "path := `src/main.go`\n"
        "```\n"
        "After the fence `src/util/helper.go` remains.\n"
    )
    assert _triples(extract(text)) == [("src/util/helper.go", None, 5)]


def test_extract_dedupes_identical_refs():
    refs = extract("Both `src/main.go` and `src/main.go` again.\n")
    assert _triples(refs) == [("src/main.go", None, 1)]


# --- resolution --------------------------------------------------------------


def test_resolve_ok_file(fixture_project):
    assert resolve(Ref(path="src/main.go", symbol=None, line_no=1), fixture_project) == "ok"


def test_resolve_ok_symbol(fixture_project):
    ref = Ref(path="src/main.go", symbol="HandleThing", line_no=1)
    assert resolve(ref, fixture_project) == "ok"


def test_resolve_ok_directory_with_trailing_slash(fixture_project):
    assert resolve(Ref(path="src/util/", symbol=None, line_no=1), fixture_project) == "ok"


def test_resolve_missing_path(fixture_project):
    ref = Ref(path="src/gone.go", symbol=None, line_no=1)
    assert resolve(ref, fixture_project) == "missing_path"


def test_resolve_missing_symbol(fixture_project):
    ref = Ref(path="src/main.go", symbol="VanishedSymbol", line_no=1)
    assert resolve(ref, fixture_project) == "missing_symbol"


def test_resolve_doc_relative_path(fixture_project):
    # A doc under docs/pipeline/ cites a sibling file by a path that exists
    # relative to the doc's own directory but NOT relative to the repo root.
    doc_dir = fixture_project / "docs" / "pipeline"
    (doc_dir / "sibling.go").write_text("package pipeline\n", encoding="utf-8")
    (doc_dir / "child.md").write_text(
        "See [sibling](sibling.go) for details.\n", encoding="utf-8"
    )
    ref = Ref(path="sibling.go", symbol=None, line_no=1)
    # Resolved against the doc's own directory: found.
    assert resolve(ref, fixture_project, "docs/pipeline/child.md") == "ok"
    # Resolved against the repo root only (no doc path): missing.
    assert resolve(ref, fixture_project) == "missing_path"
