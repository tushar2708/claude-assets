"""Tests for docsmith_lib.config — discovery, profiles, overrides, categories."""

import json
from pathlib import Path

import pytest

from docsmith_lib.config import (
    DEFAULT_CATEGORIES,
    DEFAULT_CONFIG,
    PROFILES,
    ConfigNotFoundError,
    find_project_root,
    load_config,
    resolve_category,
)


def _write_config(root: Path, config: dict) -> None:
    config_dir = root / ".docsmith"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")


def test_discovery_walks_up_from_nested_dir(fixture_project):
    nested = fixture_project / "src" / "deeply" / "nested"
    nested.mkdir(parents=True)
    root, config = load_config(start=nested)
    assert root == fixture_project
    assert config["project"]["name"] == "fixture"


def test_find_project_root_raises_outside_project(tmp_path):
    with pytest.raises(ConfigNotFoundError):
        find_project_root(tmp_path)


def test_load_config_raises_outside_project(tmp_path):
    with pytest.raises(ConfigNotFoundError):
        load_config(start=tmp_path)


def test_load_config_explicit_root_still_requires_file(tmp_path):
    with pytest.raises(ConfigNotFoundError):
        load_config(project_root=tmp_path)


def test_cli_exits_3_without_config(tmp_path, run_cli):
    exit_code, _ = run_cli(tmp_path, "validate", expect_json=False)
    assert exit_code == 3


def test_profile_minimal_disables_most_checks(tmp_path):
    _write_config(tmp_path, {"docsmith_version": 1, "profile": "minimal"})
    _, config = load_config(project_root=tmp_path)
    assert config["validate"]["frontmatter"] is True
    assert config["validate"]["docmap"] is True
    for check in ("links", "drift", "coverage", "plan_ttl", "decisions"):
        assert config["validate"][check] is False


def test_profile_full_requires_index_table(tmp_path):
    _write_config(tmp_path, {"docsmith_version": 1, "profile": "full"})
    _, config = load_config(project_root=tmp_path)
    assert config["validate"]["require_index_table"] is True
    assert config["validate"]["links"] is True


def test_profile_standard_defaults(tmp_path):
    _write_config(tmp_path, {"docsmith_version": 1})
    _, config = load_config(project_root=tmp_path)
    assert config["validate"]["require_index_table"] is False
    assert config["validate"]["plan_ttl"] is True


def test_explicit_validate_key_wins_over_profile(tmp_path):
    _write_config(
        tmp_path,
        {"docsmith_version": 1, "profile": "full", "validate": {"links": False}},
    )
    _, config = load_config(project_root=tmp_path)
    assert config["validate"]["links"] is False
    assert config["validate"]["drift"] is True


def test_dotted_override_applies_last(fixture_project):
    # The standard profile's default is False; the fixture's `overrides`
    # dotted path flips it to True and must win.
    assert PROFILES["standard"]["validate"]["require_index_table"] is False
    _, config = load_config(project_root=fixture_project)
    assert config["validate"]["require_index_table"] is True


def test_docsmith_version_mismatch_raises(tmp_path):
    _write_config(tmp_path, {"docsmith_version": 2})
    with pytest.raises(ValueError):
        load_config(project_root=tmp_path)


def test_resolve_category(fixture_project):
    _, config = load_config(project_root=fixture_project)
    # 1. fm_type equals a category key.
    assert resolve_category("docs/pipeline/overview.md", "explanation", config) == "explanation"
    # 2. fm_type equals a type alias (case-sensitive).
    assert resolve_category("docs/anything.md", "Guide", config) == "how-to"
    # 3. dir_pattern match (recursive **).
    assert resolve_category("docs/tutorials/deep/intro.md", None, config) == "tutorial"
    # 4. Nothing matches.
    assert resolve_category("notes/random.md", None, config) is None


@pytest.mark.parametrize(
    "rel_path, fm_type, expected",
    [
        pytest.param("docs/anything.md", "research", "research", id="type-research"),
        pytest.param("docs/anything.md", "Research", "research", id="alias-Research"),
        pytest.param("docs/anything.md", "plan", "plan", id="type-plan"),
        pytest.param("docs/anything.md", "Plan", "plan", id="alias-Plan"),
        pytest.param(
            "docs/specs/spec-01-x/research-output.md", "research", "research",
            id="research-in-a-spec-folder-resolves-by-type",
        ),
        pytest.param(
            "docs/specs/spec-01-x/spec-01-x.md", None, "plan",
            id="spec-doc-resolves-by-path",
        ),
        pytest.param(
            "docs/specs/INDEX.md", "Reference", "reference",
            id="specs-index-resolves-by-type-alias-not-path",
        ),
        pytest.param(
            "docs/specs/spec-01-x/research-output.md", None, "plan",
            id="untyped-doc-in-a-spec-folder-falls-back-to-plan",
        ),
        pytest.param(
            "docs/plans/x.md", None, None, id="old-plans-dir-is-no-longer-a-plan-dir"
        ),
        pytest.param(
            "docs/pipeline/research-output.md", None, None,
            id="research-has-no-dir-pattern",
        ),
    ],
)
def test_resolve_category_plan_and_research_on_defaults(
    tmp_path, rel_path, fm_type, expected
):
    _write_config(tmp_path, {"docsmith_version": 1})
    _, config = load_config(project_root=tmp_path)
    assert resolve_category(rel_path, fm_type, config) == expected


@pytest.mark.parametrize(
    "category, expected",
    [
        pytest.param(
            "plan",
            {
                "enabled": True,
                "lifecycle": "ephemeral",
                "dir_patterns": ["docs/specs/**"],
                "type_aliases": ["Plan"],
                "template": "plan.md",
                "site": {"include": True},
                "ttl_days": 45,
                "archive_dir": "docs/specs/archive",
            },
            id="plan-lives-under-docs-specs",
        ),
        pytest.param(
            "research",
            {
                "enabled": True,
                "lifecycle": "ephemeral",
                "dir_patterns": [],
                "type_aliases": ["Research"],
                "template": "research.md",
                "site": {"include": True},
            },
            id="research-is-type-only-and-has-no-ttl",
        ),
    ],
)
def test_default_categories_plan_and_research(category, expected):
    assert DEFAULT_CATEGORIES[category] == expected


def test_default_categories_order_puts_research_and_brainstorm_before_external():
    names = list(DEFAULT_CATEGORIES)
    assert names.index("plan") + 1 == names.index("research")
    assert names.index("research") + 1 == names.index("brainstorm")
    assert names.index("brainstorm") + 1 == names.index("external")
    assert len(names) == 11


@pytest.mark.parametrize(
    "rel_path, fm_type, expected",
    [
        pytest.param(
            "docs/anything.md", "brainstorm", "brainstorm", id="type-brainstorm"
        ),
        pytest.param(
            "docs/anything.md", "Brainstorm", "brainstorm", id="alias-Brainstorm"
        ),
        pytest.param(
            "docs/specs/brainstorm-01-x/brainstorm-01-x.md", "brainstorm", "brainstorm",
            id="brainstorm-in-its-folder-resolves-by-type",
        ),
        pytest.param(
            "docs/specs/brainstorm-01-x/spec-01-01-y/spec-01-01-y.md", None, "plan",
            id="spec-inside-a-brainstorm-resolves-by-path",
        ),
        pytest.param(
            "docs/specs/brainstorm-01-x/research-output.md", "research", "research",
            id="research-inside-a-brainstorm-resolves-by-type",
        ),
        pytest.param(
            "docs/specs/brainstorm-01-x/brainstorm-01-x.md", None, "plan",
            id="untyped-brainstorm-falls-back-to-plan-by-path",
        ),
        pytest.param(
            "docs/pipeline/brainstorm-01-x.md", None, None,
            id="brainstorm-has-no-dir-pattern",
        ),
    ],
)
def test_resolve_category_brainstorm_on_defaults(
    tmp_path, rel_path, fm_type, expected
):
    _write_config(tmp_path, {"docsmith_version": 1})
    _, config = load_config(project_root=tmp_path)
    assert resolve_category(rel_path, fm_type, config) == expected


def test_default_category_brainstorm():
    assert DEFAULT_CATEGORIES["brainstorm"] == {
        "enabled": True,
        "lifecycle": "ephemeral",
        "dir_patterns": [],
        "type_aliases": ["Brainstorm"],
        "template": "brainstorm.md",
        "site": {"include": True},
    }


def test_default_allowed_statuses_put_ready_right_after_draft():
    assert DEFAULT_CONFIG["frontmatter"]["allowed_statuses"] == [
        "draft",
        "ready",
        "stable",
        "partially-implemented",
        "implemented",
        "deprecated",
        "superseded",
    ]


@pytest.mark.parametrize("profile", sorted(PROFILES))
def test_every_profile_skips_draft_and_ready_in_the_drift_check(profile):
    assert PROFILES[profile]["validate"]["drift_skip_statuses"] == ["draft", "ready"]
