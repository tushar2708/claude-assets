"""CLI-level tests for `docsmith validate` (wave A2).

All tests drive the real CLI subprocess via the run_cli fixture; tests that
need git history (V6 plan-ttl) use git_project.
"""

import json
import shutil

import pytest

from docsmith_lib import config as config_lib
from docsmith_lib import validate as validate_lib

BROKEN = "docs/pipeline/broken.md"
ADR = "docs/decisions/ADR-001-use-go.md"

DEFAULT_GATE_PATTERNS = config_lib.DEFAULT_CONFIG["extra_gate_paths"]


def _results(payload, check=None, severity=None, path=None):
    results = payload["results"]
    if check is not None:
        results = [r for r in results if r["check"] == check]
    if severity is not None:
        results = [r for r in results if r["severity"] == severity]
    if path is not None:
        results = [r for r in results if r["path"] == path]
    return results


def _set_extra_gate_paths(root, patterns):
    cfg_path = root / ".docsmith" / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["extra_gate_paths"] = list(patterns)
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")


# --- full run on the pristine fixture ----------------------------------------


def test_full_run_errors_are_exactly_brokens(fixture_project, run_cli):
    exit_code, payload = run_cli(fixture_project, "validate")
    assert exit_code == 1
    errors = _results(payload, severity="error")
    assert errors, "broken.md must produce errors"
    assert {r["path"] for r in errors} == {BROKEN}


def test_full_run_counts_all_examined_files(fixture_project, run_cli):
    # 8 category docs + 2 extra-gate files (CLAUDE.md, README.md).
    _, payload = run_cli(fixture_project, "validate")
    assert payload["summary"]["checked"] == 10


def test_submodule_files_excluded_from_validation(fixture_project, run_cli):
    # A declared git submodule's own markdown must never be swept into this
    # project's validate run, even when an extra_gate_paths glob would
    # otherwise match its path (here, "src/**/README.md" would match a
    # README nested under src/vendor/thirdparty without the exclusion).
    submodule_dir = fixture_project / "src" / "vendor" / "thirdparty"
    submodule_dir.mkdir(parents=True)
    (submodule_dir / "README.md").write_text(
        "# Thirdparty\n\nSource: `src/vendor/thirdparty/gone.go`\n"
    )
    (fixture_project / ".gitmodules").write_text(
        '[submodule "src/vendor/thirdparty"]\n'
        "\tpath = src/vendor/thirdparty\n"
        "\turl = git@example.com:example/thirdparty.git\n"
    )
    _, payload = run_cli(fixture_project, "validate")
    paths_checked = {r["path"] for r in payload["results"]}
    assert "src/vendor/thirdparty/README.md" not in paths_checked
    # Baseline is 10 (8 category docs + CLAUDE.md + README.md); the new
    # .gitmodules file and the submodule's own README must not add to it.
    assert payload["summary"]["checked"] == 10


def test_broken_v2_link_error(fixture_project, run_cli):
    _, payload = run_cli(fixture_project, "validate")
    link_errors = _results(payload, check="links", severity="error", path=BROKEN)
    assert len(link_errors) == 1
    assert "nowhere.md" in link_errors[0]["message"]


def test_broken_v3_drift_warnings_by_default(fixture_project, run_cli):
    # Drift feeds the freshness score, so by default both a missing path and a
    # missing symbol are warnings (staleness signals, not build-breakers).
    _, payload = run_cli(fixture_project, "validate")
    assert _results(payload, check="drift", severity="error", path=BROKEN) == []
    drift_warnings = _results(payload, check="drift", severity="warning", path=BROKEN)
    messages = " ".join(w["message"] for w in drift_warnings)
    assert "src/gone.go" in messages
    assert "VanishedSymbol" in messages


def test_v3_path_drift_escalates_to_error_when_configured(fixture_project, run_cli):
    # validate.path_drift_severity="error" makes a missing path on an evergreen
    # doc a hard error again.
    cfg_path = fixture_project / ".docsmith" / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg.setdefault("validate", {})["path_drift_severity"] = "error"
    cfg_path.write_text(json.dumps(cfg))
    _, payload = run_cli(fixture_project, "validate")
    drift_errors = _results(payload, check="drift", severity="error", path=BROKEN)
    assert any("src/gone.go" in e["message"] for e in drift_errors)


def test_broken_v1b_index_table_warning(fixture_project, run_cli):
    # The fixture's overrides flip validate.require_index_table to true.
    _, payload = run_cli(fixture_project, "validate")
    warnings = _results(payload, check="frontmatter", severity="warning", path=BROKEN)
    assert any("missing index table" in r["message"] for r in warnings)


def test_overview_has_no_index_table_warning(fixture_project, run_cli):
    _, payload = run_cli(fixture_project, "validate")
    assert _results(payload, check="frontmatter", path="docs/pipeline/overview.md") == []


@pytest.mark.parametrize(
    "doc_text, expected_messages",
    [
        pytest.param(
            "See `src/gone.go`.\n",
            [
                "cited path 'src/gone.go' does not exist "
                "(if 'src/gone.go' is an external name, "
                "write it in italics instead of backticks)"
            ],
            id="missing-file-path",
        ),
        pytest.param(
            "See `vendor-sdk/client`.\n",
            [
                "cited path 'vendor-sdk/client' does not exist "
                "(if 'vendor-sdk/client' is an external name, "
                "write it in italics instead of backticks)"
            ],
            id="missing-directory-style-path",
        ),
        pytest.param(
            "See `src/main.go#VanishedSymbol`.\n",
            ["symbol 'VanishedSymbol' not found in 'src/main.go'"],
            id="missing-symbol-keeps-its-message-without-hint",
        ),
        pytest.param(
            "See `src/main.go`.\n",
            [],
            id="existing-path-yields-no-finding",
        ),
    ],
)
def test_v3_drift_message_hints_italics_only_for_missing_path(
    fixture_project, run_cli, doc_text, expected_messages
):
    (fixture_project / "README.md").write_text(doc_text, encoding="utf-8")

    _, payload = run_cli(fixture_project, "validate", "--only", "drift")

    drift = _results(payload, check="drift", path="README.md")
    assert [r["message"] for r in drift] == expected_messages
    assert {r["severity"] for r in drift} <= {"warning"}


@pytest.mark.parametrize(
    "frontmatter_lines, skip_override, expect_drift",
    [
        pytest.param(["status: draft"], None, False, id="draft-is-skipped-by-default"),
        pytest.param(["status: stable"], None, True, id="stable-is-checked"),
        pytest.param(["status: deprecated"], None, True, id="deprecated-is-checked"),
        pytest.param(["title: No Status"], None, True, id="no-status-key-is-checked"),
        pytest.param(
            ["status: draft"], [], True, id="empty-skip-list-checks-draft"
        ),
        pytest.param(
            ["status: deprecated"], ["deprecated"], False,
            id="configured-skip-status-is-skipped",
        ),
    ],
)
def test_v3_drift_skips_docs_by_frontmatter_status(
    fixture_project, run_cli, frontmatter_lines, skip_override, expect_drift
):
    if skip_override is not None:
        cfg_path = fixture_project / ".docsmith" / "config.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg.setdefault("validate", {})["drift_skip_statuses"] = skip_override
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    (fixture_project / "README.md").write_text(
        "---\n" + "\n".join(frontmatter_lines) + "\n---\n\n"
        "See `src/gone.go` and `src/main.go#VanishedSymbol`.\n",
        encoding="utf-8",
    )

    _, payload = run_cli(fixture_project, "validate", "--only", "drift")

    drift = _results(payload, check="drift", path="README.md")
    messages = " ".join(r["message"] for r in drift)
    if not expect_drift:
        assert drift == []
        return
    assert {r["severity"] for r in drift} == {"warning"}
    assert "src/gone.go" in messages
    assert "VanishedSymbol" in messages


# --- extra-gate files: de-duplication by real path ----------------------------

_DRIFTING_GATE_TEXT = "See `src/gone.go`.\n"
_GATE_NAMES = {"AGENTS.md", "CLAUDE.md"}


@pytest.mark.parametrize(
    "gate_patterns, symlink, expected_reported_paths",
    [
        pytest.param(
            ["CLAUDE.md", "AGENTS.md"], ("CLAUDE.md", "AGENTS.md"), ["AGENTS.md"],
            id="claude-symlink-listed-first-keeps-real-agents",
        ),
        pytest.param(
            ["AGENTS.md", "CLAUDE.md"], ("CLAUDE.md", "AGENTS.md"), ["AGENTS.md"],
            id="claude-symlink-listed-last-keeps-real-agents",
        ),
        pytest.param(
            ["AGENTS.md", "CLAUDE.md"], ("AGENTS.md", "CLAUDE.md"), ["CLAUDE.md"],
            id="agents-symlink-keeps-real-claude",
        ),
        pytest.param(
            ["CLAUDE.md"], ("CLAUDE.md", "AGENTS.md"), ["CLAUDE.md"],
            id="lone-symlink-is-still-validated",
        ),
        pytest.param(
            ["CLAUDE.md", "AGENTS.md"], None, ["AGENTS.md", "CLAUDE.md"],
            id="distinct-regular-files-are-both-validated",
        ),
    ],
)
def test_gate_files_deduplicate_by_real_path_preferring_non_symlink(
    fixture_project, run_cli, gate_patterns, symlink, expected_reported_paths
):
    _set_extra_gate_paths(fixture_project, gate_patterns)
    for name in _GATE_NAMES:
        (fixture_project / name).unlink(missing_ok=True)
        (fixture_project / name).write_text(_DRIFTING_GATE_TEXT, encoding="utf-8")
    if symlink is not None:
        alias, target = symlink
        (fixture_project / alias).unlink()
        (fixture_project / alias).symlink_to(target)

    _, payload = run_cli(fixture_project, "validate", "--only", "drift")

    gate_drift = [
        r for r in _results(payload, check="drift") if r["path"] in _GATE_NAMES
    ]
    assert sorted(r["path"] for r in gate_drift) == expected_reported_paths


def _write_drifting_files(root, rel_paths):
    """(Re)create each rel path as a regular file citing a missing path."""
    for rel in rel_paths:
        (root / rel).unlink(missing_ok=True)
        (root / rel).write_text(_DRIFTING_GATE_TEXT, encoding="utf-8")


def _replace_with_symlink(root, alias, target):
    (root / alias).unlink()
    (root / alias).symlink_to(target)


# --- --paths through a symlink alias ------------------------------------------

_OVERVIEW = "docs/pipeline/overview.md"
# Fixture: 8 category docs; the alias pair contributes one real gate file.
_FIXTURE_CATEGORY_DOC_COUNT = 8


@pytest.mark.parametrize(
    "paths_args, expected_drift_paths, expected_checked",
    [
        pytest.param(
            ["--paths", "CLAUDE.md"], ["CLAUDE.md"], 1,
            id="scoped-to-the-symlink-spelling-still-validates-the-file",
        ),
        pytest.param(
            ["--paths", "AGENTS.md"], ["AGENTS.md"], 1,
            id="scoped-to-the-real-spelling-validates-the-file",
        ),
        pytest.param(
            [], ["AGENTS.md"], _FIXTURE_CATEGORY_DOC_COUNT + 1,
            id="unscoped-reports-the-real-file-once-not-twice",
        ),
        pytest.param(
            ["--paths", _OVERVIEW], [], 1,
            id="scoped-to-another-doc-yields-nothing-from-the-pair",
        ),
    ],
)
def test_paths_filter_works_through_symlink_alias(
    fixture_project, run_cli, paths_args, expected_drift_paths, expected_checked
):
    _set_extra_gate_paths(fixture_project, ["CLAUDE.md", "AGENTS.md"])
    _write_drifting_files(fixture_project, ["AGENTS.md", "CLAUDE.md"])
    _replace_with_symlink(fixture_project, "CLAUDE.md", "AGENTS.md")

    _, payload = run_cli(fixture_project, "validate", "--only", "drift", *paths_args)

    gate_drift = [
        r for r in _results(payload, check="drift") if r["path"] in _GATE_NAMES
    ]
    assert [r["path"] for r in gate_drift] == expected_drift_paths
    assert payload["summary"]["checked"] == expected_checked


# --- gate symlink pointing at a category doc ------------------------------------

_CATEGORY_DOC = "docs/reference/x.md"
_CATEGORY_DOC_TEXT = (
    "---\ntype: reference\ntitle: X\nstatus: stable\n---\n\n# X\n\n"
    + _DRIFTING_GATE_TEXT
)


@pytest.mark.parametrize(
    "paths_args, expected_drift_paths, expected_checked",
    [
        pytest.param(
            [], [_CATEGORY_DOC], _FIXTURE_CATEGORY_DOC_COUNT + 1 + 1,
            id="unscoped-reports-the-category-doc-once",
        ),
        pytest.param(
            ["--paths", "README.md"], ["README.md"], 1,
            id="scoped-to-the-gate-alias-validates-through-the-alias",
        ),
    ],
)
def test_gate_symlink_to_category_doc_is_validated_once(
    fixture_project, run_cli, paths_args, expected_drift_paths, expected_checked
):
    # checked (unscoped) = 8 fixture docs + x.md + CLAUDE.md; the README.md
    # alias of x.md must not add a second count or a second finding.
    (fixture_project / _CATEGORY_DOC).write_text(_CATEGORY_DOC_TEXT, encoding="utf-8")
    _replace_with_symlink(fixture_project, "README.md", _CATEGORY_DOC)

    _, payload = run_cli(fixture_project, "validate", "--only", "drift", *paths_args)

    x_drift = [
        r
        for r in _results(payload, check="drift")
        if r["path"] in {_CATEGORY_DOC, "README.md"}
    ]
    assert [r["path"] for r in x_drift] == expected_drift_paths
    assert payload["summary"]["checked"] == expected_checked


# --- extra_gate_files ordering / stability ---------------------------------------


@pytest.mark.parametrize(
    "gate_patterns, symlink, collapse, expected_ordered_paths",
    [
        pytest.param(
            ["CLAUDE.md", "README.md", "AGENTS.md"], ("CLAUDE.md", "AGENTS.md"), True,
            ["AGENTS.md", "README.md"],
            id="real-file-replaces-symlink-in-the-first-slot",
        ),
        pytest.param(
            ["README.md", "AGENTS.md", "CLAUDE.md"], ("CLAUDE.md", "AGENTS.md"), True,
            ["README.md", "AGENTS.md"],
            id="real-file-listed-first-keeps-its-slot",
        ),
        pytest.param(
            ["AGENTS.md", "CLAUDE.md", "README.md"], ("AGENTS.md", "CLAUDE.md"), True,
            ["CLAUDE.md", "README.md"],
            id="reversed-alias-direction-keeps-the-non-symlink-in-slot-zero",
        ),
        pytest.param(
            ["CLAUDE.md", "README.md", "AGENTS.md"], ("CLAUDE.md", "AGENTS.md"), False,
            ["CLAUDE.md", "README.md", "AGENTS.md"],
            id="uncollapsed-keeps-every-spelling-in-pattern-order",
        ),
    ],
)
def test_extra_gate_files_order_and_kept_path(
    fixture_project, gate_patterns, symlink, collapse, expected_ordered_paths
):
    _set_extra_gate_paths(fixture_project, gate_patterns)
    _write_drifting_files(fixture_project, ["AGENTS.md", "CLAUDE.md", "README.md"])
    alias, target = symlink
    _replace_with_symlink(fixture_project, alias, target)
    root, config = config_lib.load_config(project_root=fixture_project)

    gated = validate_lib.extra_gate_files(root, config, collapse=collapse)

    assert gated == expected_ordered_paths


# --- --paths / --only / --strict ---------------------------------------------


def test_paths_filter_excluding_broken_passes(fixture_project, run_cli):
    exit_code, payload = run_cli(
        fixture_project, "validate", "--paths", "docs/pipeline/overview.md"
    )
    assert exit_code == 0
    assert payload["summary"]["errors"] == 0
    assert payload["summary"]["checked"] == 1


def test_only_frontmatter_skips_link_errors(fixture_project, run_cli):
    exit_code, payload = run_cli(fixture_project, "validate", "--only", "frontmatter")
    assert exit_code == 0  # frontmatter findings are warnings only
    assert _results(payload, check="links") == []
    assert _results(payload, check="drift") == []
    assert _results(payload, check="frontmatter", severity="warning")


def test_strict_turns_warnings_into_exit_1(fixture_project, run_cli):
    # Same invocation as the passing --paths run, plus --strict: the V5
    # coverage warning ('src/**/README.md' matches nothing) now fails it.
    exit_code, payload = run_cli(
        fixture_project, "validate", "--paths", "docs/pipeline/overview.md", "--strict"
    )
    assert exit_code == 1
    assert payload["summary"]["errors"] == 0
    assert payload["summary"]["warnings"] >= 1


def test_only_rejects_unknown_token(fixture_project, run_cli):
    exit_code, _ = run_cli(
        fixture_project, "validate", "--only", "nonsense", expect_json=False
    )
    assert exit_code == 2


# --- V4 docmap ---------------------------------------------------------------


def test_docmap_entry_with_nonexistent_path_errors(fixture_project, run_cli):
    docmap_path = fixture_project / ".docsmith" / "docmap.json"
    docmap = json.loads(docmap_path.read_text(encoding="utf-8"))
    docmap["map"]["src/"].append({"path": "docs/does-not-exist.md"})
    docmap_path.write_text(json.dumps(docmap), encoding="utf-8")

    exit_code, payload = run_cli(fixture_project, "validate", "--only", "docmap")
    assert exit_code == 1
    errors = _results(payload, check="docmap", severity="error")
    assert len(errors) == 1
    assert "docs/does-not-exist.md" in errors[0]["message"]


def test_docmap_clean_on_pristine_fixture(fixture_project, run_cli):
    exit_code, payload = run_cli(fixture_project, "validate", "--only", "docmap")
    assert exit_code == 0
    assert _results(payload, check="docmap") == []


# --- V5 coverage -------------------------------------------------------------


def test_coverage_warns_on_pattern_matching_no_files(fixture_project, run_cli):
    _, payload = run_cli(fixture_project, "validate", "--only", "coverage")
    warnings = _results(payload, check="coverage", severity="warning")
    assert [r["path"] for r in warnings] == ["src/**/README.md"]
    assert warnings[0]["message"] == "pattern matches no files"


@pytest.mark.parametrize(
    "extra_patterns, create, remove, expected_warning_paths",
    [
        pytest.param(
            [], [], ["CLAUDE.md", "README.md"], [],
            id="default-patterns-matching-nothing-are-silent",
        ),
        pytest.param(
            ["NOTES.md"], [], [], ["NOTES.md"],
            id="project-added-pattern-matching-nothing-warns",
        ),
        pytest.param(
            ["docs/**/GUIDE.md"], [], [], ["docs/**/GUIDE.md"],
            id="project-added-glob-matching-nothing-warns",
        ),
        pytest.param(
            ["NOTES.md"], ["NOTES.md"], [], [],
            id="project-added-pattern-matching-a-file-is-silent",
        ),
        pytest.param(
            ["NOTES.md", "docs/**/GUIDE.md"], ["NOTES.md"], ["README.md"],
            ["docs/**/GUIDE.md"],
            id="mixed-only-unmatched-project-pattern-warns",
        ),
    ],
)
def test_coverage_warns_only_for_unmatched_project_added_patterns(
    fixture_project, run_cli, extra_patterns, create, remove, expected_warning_paths
):
    _set_extra_gate_paths(fixture_project, [*DEFAULT_GATE_PATTERNS, *extra_patterns])
    for rel in remove:
        (fixture_project / rel).unlink()
    for rel in create:
        (fixture_project / rel).write_text("# Notes\n", encoding="utf-8")

    _, payload = run_cli(fixture_project, "validate", "--only", "coverage")

    coverage = _results(payload, check="coverage")
    assert [r["path"] for r in coverage] == expected_warning_paths
    assert {r["severity"] for r in coverage} <= {"warning"}
    assert {r["message"] for r in coverage} <= {"pattern matches no files"}


# --- V6 plan-ttl (needs git history) -----------------------------------------


def test_plan_ttl_expired_warning(git_project, run_cli):
    # Initial commit is backdated to 2026-01-01; the plan category ttl is
    # 45 days, so the plan is long expired by now.
    exit_code, payload = run_cli(git_project.root, "validate", "--only", "plan-ttl")
    assert exit_code == 0  # warnings only
    warnings = _results(payload, check="plan-ttl", severity="warning")
    assert [r["path"] for r in warnings] == ["docs/plans/01-old-plan.md"]
    assert "plan expired" in warnings[0]["message"]
    assert "docs/plans/archive" in warnings[0]["message"]


def test_plan_ttl_skips_archived_plans(git_project, run_cli):
    root = git_project.root
    shutil.move(
        str(root / "docs" / "plans" / "01-old-plan.md"),
        str(root / "docs" / "plans" / "archive" / "01-old-plan.md"),
    )
    git_project.commit_at("2026-01-01T00:00:00", "archive the plan")
    _, payload = run_cli(root, "validate", "--only", "plan-ttl")
    assert _results(payload, check="plan-ttl") == []


# --- V7 decisions ------------------------------------------------------------


def test_decisions_adr001_passes(fixture_project, run_cli):
    exit_code, payload = run_cli(fixture_project, "validate", "--only", "decisions")
    assert exit_code == 0
    assert _results(payload, check="decisions") == []


def test_decisions_bad_filename_errors(fixture_project, run_cli):
    source = fixture_project / ADR
    bad = fixture_project / "docs" / "decisions" / "adr-2-bad.md"
    bad.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code, payload = run_cli(fixture_project, "validate", "--only", "decisions")
    assert exit_code == 1
    errors = _results(payload, check="decisions", severity="error")
    assert [r["path"] for r in errors] == ["docs/decisions/adr-2-bad.md"]
    assert "does not match" in errors[0]["message"]


def test_decisions_duplicate_number_errors(fixture_project, run_cli):
    source = fixture_project / ADR
    twin = fixture_project / "docs" / "decisions" / "ADR-001-use-rust.md"
    twin.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code, payload = run_cli(fixture_project, "validate", "--only", "decisions")
    assert exit_code == 1
    errors = _results(payload, check="decisions", severity="error")
    assert len(errors) == 1
    assert "duplicate decision number '001'" in errors[0]["message"]


def test_decisions_draft_missing_section_errors(fixture_project, run_cli):
    adr_path = fixture_project / ADR
    text = adr_path.read_text(encoding="utf-8")
    text = text.replace("status: stable", "status: draft")
    text = text.replace("## Consequences\n", "")
    adr_path.write_text(text, encoding="utf-8")

    exit_code, payload = run_cli(fixture_project, "validate", "--only", "decisions")
    assert exit_code == 1
    errors = _results(payload, check="decisions", severity="error", path=ADR)
    assert len(errors) == 1
    assert "'## Consequences'" in errors[0]["message"]


def test_decisions_stable_missing_section_is_grandfathered_warning(
    fixture_project, run_cli
):
    adr_path = fixture_project / ADR
    text = adr_path.read_text(encoding="utf-8").replace("## Consequences\n", "")
    adr_path.write_text(text, encoding="utf-8")

    exit_code, payload = run_cli(fixture_project, "validate", "--only", "decisions")
    assert exit_code == 0  # stable docs are grandfathered to warnings
    warnings = _results(payload, check="decisions", severity="warning", path=ADR)
    assert len(warnings) == 1
    assert "'## Consequences'" in warnings[0]["message"]
