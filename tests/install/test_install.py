"""End-to-end tests for install.sh.

Each test runs the real script against a local bare git remote. A temporary HOME holds a
gitconfig that redirects the GitHub URL to that remote, and stub `claude` and `codex`
binaries log every call. Nothing touches the network or the real home directory.
"""

import os
import subprocess
from pathlib import Path

import pytest

INSTALL_SH = Path(__file__).resolve().parents[2] / "install.sh"
REPO_URL = "https://github.com/tushar2708/claude-assets.git"
MARKETPLACE_JSON = (
    '{"plugins": ['
    '{"name": "alpha", "source": "./plugins/alpha"}, '
    '{"name": "beta", "source": "./plugins/beta"}]}'
)

INSTALL_CLAUDE = [
    "claude plugin uninstall alpha@claude-assets --scope user --keep-data",
    "claude plugin uninstall beta@claude-assets --scope user --keep-data",
    "claude plugin marketplace remove claude-assets",
    "claude plugin marketplace add tushar2708/claude-assets",
    "claude plugin install alpha@claude-assets --scope user",
    "claude plugin install beta@claude-assets --scope user",
]
UNINSTALL_CLAUDE = [
    "claude plugin uninstall alpha@claude-assets --scope user",
    "claude plugin uninstall beta@claude-assets --scope user",
    "claude plugin marketplace remove claude-assets",
]
INSTALL_CODEX = [
    "codex plugin marketplace remove claude-assets",
    "codex plugin marketplace add tushar2708/claude-assets --sparse .agents/plugins --sparse plugins",
    "codex plugin add alpha@claude-assets",
    "codex plugin add beta@claude-assets",
]


class Sandbox:
    """A fake home, a bare remote, a work tree that pushes to it, and stub CLIs."""

    def __init__(self, root: Path):
        self.home = root / "home"
        self.bin = root / "bin"
        self.remote = root / "remote.git"
        self.work = root / "work"
        self.calls = root / "calls.log"
        self.clone = self.home / ".claude-assets"
        # Only these variables reach git and the script, so the real gitconfig never applies.
        self._env = {
            "PATH": os.environ["PATH"],
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.home / ".config"),
        }
        for directory in (self.home, self.bin, self.work):
            directory.mkdir()
        (self.home / ".gitconfig").write_text(
            "[user]\n\tname = Test\n\temail = test@example.com\n"
            f'[url "{self.remote}"]\n\tinsteadOf = {REPO_URL}\n'
        )
        for name in ("claude", "codex"):
            self._write_stub(name)
        self.git(root, "init", "--quiet", "--bare", str(self.remote))
        self.git(self.remote, "symbolic-ref", "HEAD", "refs/heads/main")
        self.git(self.work, "init", "--quiet")
        self.git(self.work, "checkout", "--quiet", "-b", "main")
        self.git(self.work, "remote", "add", "origin", str(self.remote))
        self.push_commit(
            "initial",
            {
                ".claude-plugin/marketplace.json": MARKETPLACE_JSON,
                ".gitignore": "*.log\n",
                "README.md": "v1\n",
            },
        )

    def git(self, cwd, *args, check=True):
        return subprocess.run(
            ["git", *args], cwd=cwd, env=self._env, check=check, capture_output=True, text=True
        )

    def _write_stub(self, name):
        stub = self.bin / name
        stub.write_text(
            "#!/usr/bin/env bash\n"
            f'echo "{name} $*" >> "{self.calls}"\n'
            'if [ -n "${STUB_FAIL:-}" ] && [[ "$*" == $STUB_FAIL* ]]; then exit 1; fi\n'
            "exit 0\n"
        )
        stub.chmod(0o755)

    def push_commit(self, message, files, amend=False):
        for relative, content in files.items():
            target = self.work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        self.git(self.work, "add", "-A")
        commit = ["commit", "--quiet", "-m", message]
        self.git(self.work, *(commit + ["--amend"] if amend else commit))
        self.git(self.work, "push", "--quiet", "--force", "origin", "main")

    def clone_remote(self):
        self.git(self.home, "clone", "--quiet", str(self.remote), str(self.clone))

    def remote_head(self):
        return self.git(self.remote, "rev-parse", "main").stdout.strip()

    def clone_head(self):
        return self.git(self.clone, "rev-parse", "HEAD").stdout.strip()

    def clone_status(self):
        return self.git(self.clone, "status", "--porcelain", "--ignored").stdout

    def recorded_calls(self):
        return self.calls.read_text().splitlines() if self.calls.exists() else []

    def run(self, *argv, env=None):
        environment = {
            **self._env,
            "PATH": f"{self.bin}{os.pathsep}{self._env['PATH']}",
            **(env or {}),
        }
        return subprocess.run(
            ["bash", str(INSTALL_SH), *argv],
            cwd=self.home,
            env=environment,
            capture_output=True,
            text=True,
        )


@pytest.fixture
def sandbox(tmp_path):
    return Sandbox(tmp_path)


def clone_absent(sb):
    pass


def clone_behind(sb):
    sb.clone_remote()
    sb.push_commit("second", {"README.md": "v2\n"})


def clone_diverged(sb):
    """The reported bug: the remote history was rewritten and the clone also has a local commit."""
    sb.clone_remote()
    (sb.clone / "local.txt").write_text("local\n")
    sb.git(sb.clone, "add", "-A")
    sb.git(sb.clone, "commit", "--quiet", "-m", "local only")
    sb.push_commit("initial, amended", {"README.md": "v1 amended\n"}, amend=True)
    sb.git(sb.clone, "fetch", "--quiet", "origin")
    is_ancestor = sb.git(sb.clone, "merge-base", "--is-ancestor", "HEAD", "origin/main", check=False)
    assert is_ancestor.returncode == 1, "scenario is not diverged, so it would test nothing"


def clone_dirty(sb):
    sb.clone_remote()
    (sb.clone / "README.md").write_text("edited locally\n")
    (sb.clone / "stray.txt").write_text("untracked\n")
    (sb.clone / "build.log").write_text("ignored\n")


CLONE_SCENARIOS = pytest.mark.parametrize(
    "setup",
    [clone_absent, clone_behind, clone_diverged, clone_dirty],
    ids=["absent", "behind", "diverged", "dirty"],
)


@CLONE_SCENARIOS
def test_install_claude_matches_remote_and_reinstalls(sandbox, setup):
    setup(sandbox)

    result = sandbox.run("--claude")

    assert result.returncode == 0, result.stderr
    assert sandbox.clone_head() == sandbox.remote_head()
    assert sandbox.clone_status() == ""
    assert sandbox.recorded_calls() == INSTALL_CLAUDE


@CLONE_SCENARIOS
def test_uninstall_claude_works_on_any_clone_state(sandbox, setup):
    setup(sandbox)

    result = sandbox.run("--claude", "uninstall")

    assert result.returncode == 0, result.stderr
    assert sandbox.clone_head() == sandbox.remote_head()
    assert sandbox.recorded_calls() == UNINSTALL_CLAUDE


@CLONE_SCENARIOS
def test_install_codex_matches_remote_and_reinstalls(sandbox, setup):
    setup(sandbox)

    result = sandbox.run("--codex")

    assert result.returncode == 0, result.stderr
    assert sandbox.clone_head() == sandbox.remote_head()
    assert sandbox.recorded_calls() == INSTALL_CODEX


@pytest.mark.parametrize(
    "failing_call",
    ["plugin uninstall", "plugin marketplace remove", "plugin uninstall alpha"],
)
def test_install_continues_when_removal_fails(sandbox, failing_call):
    """Removal fails on a fresh machine where nothing is installed yet. That must not stop the install."""
    result = sandbox.run("--claude", env={"STUB_FAIL": failing_call})

    assert result.returncode == 0, result.stderr
    assert sandbox.recorded_calls() == INSTALL_CLAUDE


@pytest.mark.parametrize(
    "failing_call, calls_before_stop",
    [
        ("plugin marketplace add", 4),
        ("plugin install alpha", 5),
        ("plugin install beta", 6),
    ],
)
def test_install_stops_when_adding_or_installing_fails(sandbox, failing_call, calls_before_stop):
    result = sandbox.run("--claude", env={"STUB_FAIL": failing_call})

    assert result.returncode != 0
    assert sandbox.recorded_calls() == INSTALL_CLAUDE[:calls_before_stop]


@pytest.mark.parametrize(
    "argv, expected_present, expected_absent",
    [
        (("--claude",), {"foo", "bar"}, {"gone"}),
        (("--claude", "uninstall"), set(), {"foo", "bar", "gone"}),
    ],
    ids=["install", "uninstall"],
)
def test_skill_links_are_managed_and_others_left_alone(
    sandbox, argv, expected_present, expected_absent
):
    sandbox.push_commit(
        "skills",
        {"skills/foo/SKILL.md": "foo\n", "skills/bar/SKILL.md": "bar\n"},
    )
    sandbox.clone_remote()
    skills = sandbox.home / ".claude" / "skills"
    skills.mkdir(parents=True)
    (skills / "foo").symlink_to(sandbox.clone / "skills" / "foo")
    (skills / "gone").symlink_to(sandbox.clone / "skills" / "gone")
    (skills / "own").mkdir()
    (skills / "own" / "SKILL.md").write_text("mine\n")
    foreign_target = sandbox.home / "elsewhere"
    foreign_target.mkdir()
    (skills / "foreign").symlink_to(foreign_target)

    result = sandbox.run(*argv)

    assert result.returncode == 0, result.stderr
    for name in expected_present:
        assert (skills / name).is_symlink()
        assert (skills / name).resolve() == (sandbox.clone / "skills" / name).resolve()
    for name in expected_absent:
        assert not (skills / name).is_symlink() and not (skills / name).exists()
    assert (skills / "own" / "SKILL.md").read_text() == "mine\n"
    assert (skills / "foreign").resolve() == foreign_target.resolve()


def test_dry_run_changes_nothing_on_a_diverged_clone(sandbox):
    clone_diverged(sandbox)
    head_before = sandbox.clone_head()

    result = sandbox.run("--claude", env={"DRY_RUN": "1"})

    assert result.returncode == 0, result.stderr
    assert sandbox.clone_head() == head_before
    assert sandbox.recorded_calls() == []
