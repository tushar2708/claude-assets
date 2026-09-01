"""Shared pytest fixtures for the docsmith test suite."""

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
CLI = SKILL_DIR / "scripts" / "docsmith.py"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Make the library importable as `docsmith_lib` from unit tests.
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def _git_env(extra: Optional[dict] = None) -> dict:
    """Environment for hermetic git subprocess calls: the user's global and
    system git config (gpg signing, hooksPath, ...) must not leak in."""
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    if extra:
        env.update(extra)
    return env


def _git(root: Path, *args: str, extra_env: Optional[dict] = None) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        env=_git_env(extra_env),
    )


@dataclass
class GitProject:
    """Handle onto a git-initialized fixture project."""

    root: Path

    def commit_at(
        self,
        ts_iso: str,
        message: str,
        paths: Optional[list] = None,
    ) -> None:
        """Commit with author and committer dates forced to ts_iso (e.g.
        "2026-01-01T00:00:00"). Stages everything by default; when `paths`
        is given, stages only those paths."""
        if paths is None:
            _git(self.root, "add", "-A")
        else:
            _git(self.root, "add", "--", *paths)
        _git(
            self.root,
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            message,
            extra_env={"GIT_AUTHOR_DATE": ts_iso, "GIT_COMMITTER_DATE": ts_iso},
        )


@pytest.fixture
def fixture_project(tmp_path: Path) -> Path:
    """Fresh copy of the basic_project fixture tree."""
    dest = tmp_path / "proj"
    shutil.copytree(FIXTURES_DIR / "basic_project", dest)
    return dest


@pytest.fixture
def git_project(fixture_project: Path) -> GitProject:
    """fixture_project with a git repo whose initial commit is backdated to
    2026-01-01, plus a commit_at helper for further env-dated commits."""
    _git(fixture_project, "init", "-q")
    _git(fixture_project, "config", "user.email", "docsmith-tests@example.com")
    _git(fixture_project, "config", "user.name", "Docsmith Tests")
    project = GitProject(root=fixture_project)
    project.commit_at("2026-01-01T00:00:00", "initial fixture commit")
    return project


@pytest.fixture
def run_cli():
    """Run the docsmith CLI as a subprocess against a project root.

    Returns (exit_code, parsed_json_or_stdout_str). Stdout is parsed as JSON
    when expect_json is True and it parses; otherwise the raw string is
    returned. sys.executable already has pyyaml et al. because the suite is
    run via run_tests.sh (uv provides the deps).
    """

    def _run(root: Path, *args: str, expect_json: bool = True):
        proc = subprocess.run(
            [sys.executable, str(CLI), "--project-root", str(root), "--json", *args],
            capture_output=True,
            text=True,
        )
        if expect_json:
            try:
                return proc.returncode, json.loads(proc.stdout)
            except json.JSONDecodeError:
                return proc.returncode, proc.stdout
        return proc.returncode, proc.stdout

    return _run
