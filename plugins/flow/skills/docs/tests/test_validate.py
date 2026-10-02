"""CLI-level tests for `docsmith validate` (wave A2).

All tests drive the real CLI subprocess via the run_cli fixture; tests that
need git history (V6 plan-ttl) use git_project.
"""

import json
import shutil

BROKEN = "docs/pipeline/broken.md"
ADR = "docs/decisions/ADR-001-use-go.md"


def _results(payload, check=None, severity=None, path=None):
    results = payload["results"]
    if check is not None:
        results = [r for r in results if r["check"] == check]
    if severity is not None:
        results = [r for r in results if r["severity"] == severity]
    if path is not None:
        results = [r for r in results if r["path"] == path]
    return results


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
