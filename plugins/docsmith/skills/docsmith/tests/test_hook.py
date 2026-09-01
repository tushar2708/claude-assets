"""Tests for the generic PostToolUse hook (scripts/hook/docsmith_hook.py)
and its parity with the hidden `hook-check` CLI subcommand (wave A4).

The generic hook is exercised as a real subprocess with the PostToolUse
JSON payload on stdin, run from an arbitrary cwd (the hook must locate the
project from the edited file's path, never from cwd). Mapped-file cases
use the basic_project fixture copied to tmp (src/main.go is mapped via the
"src/" prefix key; main.go carries a custom message).
"""

import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CLI = SKILL_DIR / "scripts" / "docsmith.py"
HOOK = SKILL_DIR / "scripts" / "hook" / "docsmith_hook.py"


def _run_hook(file_path, cwd: Path, payload=None) -> subprocess.CompletedProcess:
    if payload is None:
        payload = {"tool_input": {"file_path": str(file_path)}}
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


def _run_hook_check(root: Path, file_path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--project-root",
            str(root),
            *extra,
            "hook-check",
            "--file",
            str(file_path),
        ],
        capture_output=True,
        text=True,
    )


# --- generic hook behavior ---------------------------------------------------


def test_mapped_file_edit_blocks_with_message(fixture_project, tmp_path):
    proc = _run_hook(fixture_project / "src" / "main.go", tmp_path)
    assert proc.returncode == 2
    assert "DOCSMITH: you edited code that is mapped to documentation." in proc.stderr
    assert "task-queue protocol" in proc.stderr
    assert "docs/pipeline/overview.md (pipeline docs)" in proc.stderr
    # The src/ entry has no custom message.
    assert "CUSTOM UPDATE INSTRUCTIONS" not in proc.stderr


def test_mapped_file_with_custom_message(fixture_project, tmp_path):
    proc = _run_hook(fixture_project / "main.go", tmp_path)
    assert proc.returncode == 2
    assert "--- CUSTOM UPDATE INSTRUCTIONS ---" in proc.stderr
    assert "For docs/pipeline/overview.md:" in proc.stderr
    assert "update the entry-point section" in proc.stderr


def test_md_file_exits_zero_silent(fixture_project, tmp_path):
    proc = _run_hook(fixture_project / "docs" / "pipeline" / "overview.md", tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert proc.stdout == ""


def test_unmapped_file_exits_zero(fixture_project, tmp_path):
    proc = _run_hook(fixture_project / "tools" / "unmapped.go", tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_file_outside_any_project_exits_zero(tmp_path):
    outside = tmp_path / "elsewhere" / "code.go"
    outside.parent.mkdir(parents=True)
    outside.write_text("package main\n", encoding="utf-8")
    proc = _run_hook(outside, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_missing_file_path_exits_zero(tmp_path):
    proc = _run_hook(None, tmp_path, payload={"tool_input": {}})
    assert proc.returncode == 0
    proc = _run_hook(None, tmp_path, payload={})
    assert proc.returncode == 0


def test_hook_disabled_in_config_exits_zero(fixture_project, tmp_path):
    config_path = fixture_project / ".docsmith" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["hook"] = {"enabled": False}
    config_path.write_text(json.dumps(config), encoding="utf-8")

    proc = _run_hook(fixture_project / "src" / "main.go", tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_docmap_bad_version_exits_zero(fixture_project, tmp_path):
    docmap_path = fixture_project / ".docsmith" / "docmap.json"
    docmap = json.loads(docmap_path.read_text(encoding="utf-8"))
    docmap["version"] = 2
    docmap_path.write_text(json.dumps(docmap), encoding="utf-8")

    proc = _run_hook(fixture_project / "src" / "main.go", tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_prefix_and_exact_dedupe_by_path(fixture_project, tmp_path):
    # src/util/helper.go matches BOTH "src/" and "src/util/"; the two keys
    # map to different docs, so both appear, each exactly once.
    proc = _run_hook(fixture_project / "src" / "util" / "helper.go", tmp_path)
    assert proc.returncode == 2
    assert proc.stderr.count("docs/pipeline/overview.md") == 1
    assert proc.stderr.count("docs/reference/util-reference.md") == 1


# --- hook-check parity -------------------------------------------------------


def test_parity_mapped_files(fixture_project, tmp_path):
    for rel in ("src/main.go", "main.go", "src/util/helper.go"):
        target = fixture_project / rel
        hook_proc = _run_hook(target, tmp_path)
        check_proc = _run_hook_check(fixture_project, target)
        assert hook_proc.returncode == 2, rel
        assert check_proc.returncode == 2, rel
        assert hook_proc.stderr.rstrip() == check_proc.stdout.rstrip(), rel


def test_parity_unmapped_file(fixture_project, tmp_path):
    target = fixture_project / "tools" / "unmapped.go"
    hook_proc = _run_hook(target, tmp_path)
    check_proc = _run_hook_check(fixture_project, target)
    assert hook_proc.returncode == 0
    assert check_proc.returncode == 0
    assert hook_proc.stderr.rstrip() == check_proc.stdout.rstrip() == ""


def test_parity_md_file_exit_codes(fixture_project, tmp_path):
    # hook-check prints "skipped (.md)" by design; only exit codes must match.
    target = fixture_project / "docs" / "how-to" / "run-it.md"
    hook_proc = _run_hook(target, tmp_path)
    check_proc = _run_hook_check(fixture_project, target)
    assert hook_proc.returncode == 0
    assert check_proc.returncode == 0
    assert "skipped (.md)" in check_proc.stdout


# --- hook-check --json -------------------------------------------------------


def test_hook_check_json_mapped(fixture_project):
    proc = _run_hook_check(fixture_project, fixture_project / "main.go", "--json")
    assert proc.returncode == 2
    payload = json.loads(proc.stdout)
    assert payload["matched"] == [
        {
            "path": "docs/pipeline/overview.md",
            "reason": "",
            "message": "update the entry-point section",
        }
    ]
    assert payload["message"].startswith(
        "DOCSMITH: you edited code that is mapped to documentation."
    )
    assert "--- CUSTOM UPDATE INSTRUCTIONS ---" in payload["message"]


def test_hook_check_json_md_and_unmapped(fixture_project):
    for rel in ("docs/how-to/run-it.md", "tools/unmapped.go"):
        proc = _run_hook_check(fixture_project, fixture_project / rel, "--json")
        assert proc.returncode == 0, rel
        assert json.loads(proc.stdout) == {"matched": []}, rel
