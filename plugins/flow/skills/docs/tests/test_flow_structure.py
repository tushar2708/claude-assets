"""Tests for the `flow` plugin hook scripts.

Runs each hook script as a subprocess and checks what it prints. Co-located with the
docsmith engine suite so it runs under the same run_tests.sh.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# tests/ -> docs -> skills -> PLUGIN_ROOT (flow)
PLUGIN_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "needle",
    ["flow:make-tasks", "AskUserQuestion", ".claude/rules/", "Do not create tasks yet."],
)
def test_exit_plan_hook_output(needle: str):
    proc = subprocess.run(
        [sys.executable, str(PLUGIN_ROOT / "hooks" / "exit_plan_make_tasks.py")],
        input='{"tool_name": "ExitPlanMode"}',
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "PostToolUse"
    assert needle in out["additionalContext"]
