"""Tests for docsmith_lib.frontmatter_spec — parsing, field rules, index table."""

import copy
import datetime

from docsmith_lib.config import DEFAULT_CONFIG
from docsmith_lib.frontmatter_spec import check_fields, has_index_table, parse_frontmatter


def _config(require_title: bool = False) -> dict:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config["frontmatter"]["require_title"] = require_title
    return config


def _messages(findings, severity):
    return [message for found_severity, message in findings if found_severity == severity]


def test_parse_frontmatter_ok():
    fm, error = parse_frontmatter("---\ntype: how-to\ntitle: T\n---\n\n# T\n")
    assert error is None
    assert fm == {"type": "how-to", "title": "T"}


def test_parse_frontmatter_missing_block():
    fm, error = parse_frontmatter("# Just a heading\n\nBody text.\n")
    assert fm is None
    assert error == "no frontmatter block"


def test_parse_frontmatter_unclosed_block():
    fm, error = parse_frontmatter("---\ntype: plan\n")
    assert fm is None
    assert error is not None


def test_parse_frontmatter_non_dict():
    fm, error = parse_frontmatter("---\n- a\n- b\n---\n")
    assert fm is None
    assert error is not None


def test_unresolvable_category_is_error():
    findings = check_fields({"type": "mystery", "title": "T"}, _config(), None)
    assert ("error", "type 'mystery' does not resolve to any category") in findings


def test_missing_title_warning_by_default():
    findings = check_fields({"type": "how-to"}, _config(require_title=False), "how-to")
    assert any("title" in message for message in _messages(findings, "warning"))
    assert not any("title" in message for message in _messages(findings, "error"))


def test_missing_title_error_when_required():
    findings = check_fields({"type": "how-to"}, _config(require_title=True), "how-to")
    assert any("title" in message for message in _messages(findings, "error"))


def test_bad_status_is_error():
    fm = {"type": "how-to", "title": "T", "status": "bogus"}
    findings = check_fields(fm, _config(), "how-to")
    assert any("status" in message for message in _messages(findings, "error"))


def test_tags_must_be_list():
    fm = {"type": "how-to", "title": "T", "tags": "not-a-list"}
    findings = check_fields(fm, _config(), "how-to")
    assert any("tags" in message for message in _messages(findings, "error"))


def test_malformed_stale_after_is_error():
    fm = {"type": "how-to", "title": "T", "stale_after": "someday"}
    findings = check_fields(fm, _config(), "how-to")
    assert any("stale_after" in message for message in _messages(findings, "error"))


def test_past_stale_after_is_warning():
    fm = {"type": "how-to", "title": "T", "stale_after": "2020-01-01"}
    findings = check_fields(fm, _config(), "how-to")
    assert any("stale_after" in message for message in _messages(findings, "warning"))
    assert not any("stale_after" in message for message in _messages(findings, "error"))


def test_future_stale_after_date_object_is_clean():
    # PyYAML hands over datetime.date objects for unquoted YYYY-MM-DD scalars.
    future = datetime.date.today() + datetime.timedelta(days=30)
    fm = {"type": "how-to", "title": "T", "stale_after": future}
    assert check_fields(fm, _config(), "how-to") == []


def test_generated_missing_at_is_error():
    fm = {"type": "how-to", "title": "T", "generated": {"by": "docsmith"}}
    findings = check_fields(fm, _config(), "how-to")
    assert any("generated" in message for message in _messages(findings, "error"))


def test_generated_valid_is_clean():
    fm = {
        "type": "how-to",
        "title": "T",
        "generated": {"by": "docsmith", "at": "2026-08-25T00:00:00+00:00"},
    }
    assert check_fields(fm, _config(), "how-to") == []


def test_has_index_table_true_for_overview(fixture_project):
    text = (fixture_project / "docs" / "pipeline" / "overview.md").read_text(encoding="utf-8")
    assert has_index_table(text) is True


def test_has_index_table_false_for_broken(fixture_project):
    text = (fixture_project / "docs" / "pipeline" / "broken.md").read_text(encoding="utf-8")
    assert has_index_table(text) is False
