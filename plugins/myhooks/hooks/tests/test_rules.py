"""
End-to-end tests for the migrated hook rules.

Each case pipes a Claude Code hook payload into the real hook script and checks
the exit code: 0 allows the action, 2 blocks it.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent


def run_hook(script: str, payload: dict) -> int:
    """Run one hook script with the payload on stdin and return its exit code."""
    env = {**os.environ, "PYTHONPATH": str(HOOKS_DIR)}
    result = subprocess.run(
        [sys.executable, str(HOOKS_DIR / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    return result.returncode


BASH_CASES = [
    ("git checkout main", 2),
    ("git -C /repo checkout main", 2),
    ("git reset --hard", 2),
    ("git -C /repo reset", 2),
    ("git add -A", 2),
    ("git add .", 2),
    ("git add src/main.go", 0),
    ("git add .gitignore", 0),
    ("git commit --no-verify -m msg", 0),
    ("git clean -fd", 2),
    ("git push --force origin main", 2),
    ("git rebase main", 2),
    ("git stash", 2),
    ("git status", 0),
    ("rm -rf build", 2),
    ("sed -i s/a/b/ file.txt", 2),
    ("sed s/a/b/ file.txt", 0),
    ("npm install left-pad", 2),
    ("npm install --save left-pad", 0),
    ("npm install", 0),
    ("make test", 2),
    ("make -f Makefile test", 2),
    ("echo hello", 0),
]


@pytest.mark.parametrize(("command", "expected"), BASH_CASES)
def test_pretooluse_bash(command: str, expected: int) -> None:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    assert run_hook("pretooluse_bash.py", payload) == expected


def test_pretooluse_file_cases(tmp_path: Path) -> None:
    existing = tmp_path / "existing.txt"
    existing.write_text("keep me\n")
    fresh = tmp_path / "fresh.txt"

    cases = [
        ("write existing file", {"tool_name": "Write", "tool_input": {"file_path": str(existing), "content": "x"}}, 2),
        ("write new file", {"tool_name": "Write", "tool_input": {"file_path": str(fresh), "content": "x"}}, 0),
        ("edit existing file", {"tool_name": "Edit", "tool_input": {"file_path": str(existing), "old_string": "keep", "new_string": "kept"}}, 0),
        ("autogen path", {"tool_name": "Edit", "tool_input": {"file_path": "/src/generated/api.py", "old_string": "a", "new_string": "b"}}, 2),
        ("autogen directory name", {"tool_name": "Edit", "tool_input": {"file_path": "/src/autogen/api.py", "old_string": "a", "new_string": "b"}}, 2),
        ("go blank last return", {"tool_name": "Edit", "tool_input": {"file_path": "/src/a.go", "old_string": "a", "new_string": "v, _ := m[k]"}}, 2),
        ("go nilnil return", {"tool_name": "Edit", "tool_input": {"file_path": "/src/a.go", "old_string": "a", "new_string": "return nil, nil"}}, 2),
        ("go nilnil in test file", {"tool_name": "Edit", "tool_input": {"file_path": "/src/a_test.go", "old_string": "a", "new_string": "return nil, nil"}}, 0),
        ("go nolint directive", {"tool_name": "Edit", "tool_input": {"file_path": "/src/a.go", "old_string": "a", "new_string": "x() //nolint:errcheck"}}, 2),
        ("go plain code", {"tool_name": "Edit", "tool_input": {"file_path": "/src/a.go", "old_string": "a", "new_string": "return v, nil"}}, 0),
    ]
    for name, payload, expected in cases:
        assert run_hook("pretooluse_file.py", payload) == expected, name


def test_posttooluse_python_cases(tmp_path: Path) -> None:
    bad_syntax = tmp_path / "bad_syntax.py"
    bad_syntax.write_text("def broken(:\n    pass\n")
    local_import = tmp_path / "local_import.py"
    local_import.write_text("def f():\n    import os\n    return os.name\n")
    nolint_import = tmp_path / "nolint_import.py"
    nolint_import.write_text(
        "def f():\n    # nolint:local_import_to_avoid_cycle\n    import os\n    return os.name\n"
    )
    clean = tmp_path / "clean.py"
    clean.write_text("import os\n\n\ndef f():\n    return os.name\n")
    text_file = tmp_path / "notes.txt"
    text_file.write_text("anything goes\n")

    cases = [
        ("python syntax error", bad_syntax, 2),
        ("python local import", local_import, 2),
        ("python local import with nolint", nolint_import, 0),
        ("clean python", clean, 0),
        ("non-python file", text_file, 0),
    ]
    for name, path, expected in cases:
        payload = {"tool_name": "Write", "tool_input": {"file_path": str(path)}, "tool_result": "success"}
        assert run_hook("posttooluse_file.py", payload) == expected, name
