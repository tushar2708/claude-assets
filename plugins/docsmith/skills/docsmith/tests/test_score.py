"""CLI-level tests for `docsmith score` (wave A2).

Scoring depends on git history, so every test uses git_project (initial
commit backdated to 2026-01-01) and drives the real CLI via run_cli.
"""

import json
import re

OVERVIEW = "docs/pipeline/overview.md"
BROKEN = "docs/pipeline/broken.md"
UTIL_REF = "docs/reference/util-reference.md"


def _doc(payload, path):
    return next(doc for doc in payload["docs"] if doc["path"] == path)


def _touch_code(git_project, ts_iso):
    """Modify src/main.go and commit ONLY that file at ts_iso."""
    main_go = git_project.root / "src" / "main.go"
    main_go.write_text(
        main_go.read_text(encoding="utf-8") + "\n// touched for the age tests\n",
        encoding="utf-8",
    )
    git_project.commit_at(ts_iso, "touch entry point", paths=["src/main.go"])


# --- output shape ------------------------------------------------------------


def test_score_json_shape(git_project, run_cli):
    exit_code, payload = run_cli(git_project.root, "score", "--all")
    assert exit_code == 0
    assert payload["command"] == "score"
    assert payload["threshold"] == 70
    # 6 evergreen category docs; plan (ephemeral) and ADR (immutable) excluded.
    assert payload["summary"]["scored"] == 6
    assert (
        payload["summary"]["fresh"]
        + payload["summary"]["stale"]
        + payload["summary"]["error"]
        == 6
    )
    for doc in payload["docs"]:
        assert set(doc) == {"path", "score", "components", "verdict"}
    # Sorted by score ascending.
    scores = [doc["score"] for doc in payload["docs"]]
    assert scores == sorted(scores)


# --- age component (A) -------------------------------------------------------


def test_age_100_when_doc_and_code_share_commit(git_project, run_cli):
    _, payload = run_cli(git_project.root, "score")
    assert _doc(payload, OVERVIEW)["components"]["age"] == 100


def test_age_about_50_when_code_15_days_newer(git_project, run_cli):
    _touch_code(git_project, "2026-01-16T00:00:00")  # doc @ 01-01, grace 30d
    _, payload = run_cli(git_project.root, "score")
    age = _doc(payload, OVERVIEW)["components"]["age"]
    assert 45 <= age <= 55


def test_age_0_when_code_60_days_newer(git_project, run_cli):
    _touch_code(git_project, "2026-03-02T00:00:00")  # 60 days past the doc
    _, payload = run_cli(git_project.root, "score")
    assert _doc(payload, OVERVIEW)["components"]["age"] == 0


def test_age_omitted_and_renormalized_when_doc_unmapped(git_project, run_cli):
    # Drop the docmap key that maps util-reference so C(D) becomes empty.
    docmap_path = git_project.root / ".docsmith" / "docmap.json"
    docmap = json.loads(docmap_path.read_text(encoding="utf-8"))
    del docmap["map"]["src/util/"]
    docmap_path.write_text(json.dumps(docmap), encoding="utf-8")

    _, payload = run_cli(git_project.root, "score")
    components = _doc(payload, UTIL_REF)["components"]
    assert "age" not in components
    assert "ttl" in components
    assert "drift" in components


# --- ttl and drift components ------------------------------------------------


def test_ttl_zero_when_stale_after_in_past(git_project, run_cli):
    overview_path = git_project.root / OVERVIEW
    text = overview_path.read_text(encoding="utf-8")
    overview_path.write_text(
        text.replace("stale_after: 2027-06-30", "stale_after: 2026-01-15"),
        encoding="utf-8",
    )
    _, payload = run_cli(git_project.root, "score")
    assert _doc(payload, OVERVIEW)["components"]["ttl"] == 0


def test_drift_broken_scores_below_overview(git_project, run_cli):
    _, payload = run_cli(git_project.root, "score")
    assert _doc(payload, BROKEN)["components"]["drift"] == 0
    assert _doc(payload, OVERVIEW)["components"]["drift"] == 100
    assert _doc(payload, BROKEN)["score"] < _doc(payload, OVERVIEW)["score"]


# --- threshold / --fail-under / --doc ----------------------------------------


def test_threshold_override_flips_verdict(git_project, run_cli):
    _, payload = run_cli(git_project.root, "score")
    assert _doc(payload, OVERVIEW)["verdict"] == "fresh"
    exit_code, payload = run_cli(git_project.root, "score", "--threshold", "101")
    assert exit_code == 0  # threshold alone never changes the exit code
    assert payload["threshold"] == 101
    assert _doc(payload, OVERVIEW)["verdict"] == "stale"


def test_fail_under_101_exits_1(git_project, run_cli):
    exit_code, _ = run_cli(git_project.root, "score", "--fail-under", "101")
    assert exit_code == 1


def test_doc_flag_restricts_scored_set(git_project, run_cli):
    exit_code, payload = run_cli(git_project.root, "score", "--doc", OVERVIEW)
    assert exit_code == 0
    assert [doc["path"] for doc in payload["docs"]] == [OVERVIEW]


def test_doc_flag_outside_scored_set_exits_2(git_project, run_cli):
    # The plan is ephemeral, so it is never in the scored set.
    exit_code, _ = run_cli(
        git_project.root, "score", "--doc", "docs/plans/01-old-plan.md",
        expect_json=False,
    )
    assert exit_code == 2


# --- --update-state and caching ----------------------------------------------


def test_update_state_writes_state_file(git_project, run_cli):
    state_path = git_project.root / ".docsmith" / "state.json"
    # Pre-seed a validate key: score must preserve it verbatim.
    state_path.write_text(json.dumps({"validate": {"marker": True}}), encoding="utf-8")

    exit_code, _ = run_cli(git_project.root, "score", "--update-state")
    assert exit_code == 0

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["version"] == 1
    assert re.fullmatch(r"[0-9a-f]{40,64}", state["last_scan"]["git_head"])
    assert state["last_scan"]["timestamp"]
    assert state["validate"] == {"marker": True}

    entry = state["scores"][OVERVIEW]
    assert isinstance(entry["doc_commit"], int)
    assert isinstance(entry["code_commit"], int)
    assert entry["verdict"] in ("fresh", "stale")
    assert set(entry["components"]) <= {"age", "ttl", "drift"}


def test_second_run_reuses_cached_entries(git_project, run_cli):
    state_path = git_project.root / ".docsmith" / "state.json"

    _, first_payload = run_cli(git_project.root, "score", "--update-state")
    first_scores = json.loads(state_path.read_text(encoding="utf-8"))["scores"]

    _, second_payload = run_cli(git_project.root, "score", "--update-state")
    second_scores = json.loads(state_path.read_text(encoding="utf-8"))["scores"]

    # Cached entries are reused verbatim: computed_at (set at compute time)
    # round-trips unchanged, proving no recompute happened.
    assert second_scores == first_scores
    assert second_payload["docs"] == first_payload["docs"]
