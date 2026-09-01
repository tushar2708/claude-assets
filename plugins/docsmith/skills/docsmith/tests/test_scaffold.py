"""CLI-level tests for `docsmith scaffold` (wave A4).

Scaffold does its own root resolution, so these tests build throwaway git
repos in tmp via `git init` (NOT the basic_project fixture) and drive the
real CLI subprocess.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CLI = SKILL_DIR / "scripts" / "docsmith.py"

_MINIMAL_PRECOMMIT = (
    "repos:\n"
    "  - repo: local\n"
    "    hooks:\n"
    "      - id: existing-hook\n"
    "        name: existing\n"
    "        entry: echo hi\n"
    "        language: system\n"
)


def _git_env() -> dict:
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return env


def _make_repo(tmp_path: Path, name: str = "proj") -> Path:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(root), "init", "-q"],
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    return root


def _scaffold(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(CLI),
            "scaffold",
            "--project-root",
            str(root),
            "--non-interactive",
            *args,
        ],
        capture_output=True,
        text=True,
    )


def _hook_entry_count(settings: dict) -> int:
    return sum(
        1
        for entry in settings.get("hooks", {}).get("PostToolUse", [])
        for hook in entry.get("hooks", [])
        if "docsmith_hook.py" in hook.get("command", "")
    )


# --- fresh scaffold ----------------------------------------------------------


def test_fresh_scaffold_creates_everything(tmp_path):
    root = _make_repo(tmp_path)
    proc = _scaffold(root)
    assert proc.returncode == 0, proc.stderr

    ai = root / ".docsmith"
    config = json.loads((ai / "config.json").read_text(encoding="utf-8"))
    assert config["docsmith_version"] == 1
    assert config["project"]["name"] == "proj"
    assert config["project"]["docs_dir"] == "docs"
    assert config["profile"] == "standard"
    assert config["engine_version"]

    docmap = json.loads((ai / "docmap.json").read_text(encoding="utf-8"))
    assert docmap["version"] == 1
    assert docmap["map"] == {}

    state = json.loads((ai / "state.json").read_text(encoding="utf-8"))
    assert state == {"version": 1, "last_scan": None, "scores": {}, "validate": None}

    engine_cli = ai / "engine" / "docsmith.py"
    assert engine_cli.is_file()
    assert engine_cli.read_text(encoding="utf-8").startswith(
        "# VENDORED by docsmith scaffold"
    )
    assert (ai / "engine" / "docsmith_lib" / "config.py").is_file()
    assert (ai / "engine" / "docsmith_lib" / "scaffold.py").is_file()
    assert not (ai / "engine" / "docsmith_lib" / "__pycache__").exists()

    assert (root / ".claude" / "hooks" / "docsmith_hook.py").is_file()
    settings = json.loads(
        (root / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    assert _hook_entry_count(settings) == 1

    gitignore_lines = (root / ".gitignore").read_text(encoding="utf-8").split("\n")
    assert ".docsmith/state.json" in gitignore_lines
    assert ".docsmith/site/autogen/" in gitignore_lines

    for rel in (
        "docs/tutorials",
        "docs/how-to",
        "docs/reference",
        "docs/explanation",
        "docs/runbooks",
        "docs/decisions",
        "docs/plans",
        "docs/plans/archive",
    ):
        assert (root / rel / ".gitkeep").is_file(), rel


def test_rerun_without_force_exits_2(tmp_path):
    root = _make_repo(tmp_path)
    assert _scaffold(root).returncode == 0
    proc = _scaffold(root)
    assert proc.returncode == 2
    assert "--force" in proc.stderr


def test_rerun_with_force_succeeds(tmp_path):
    root = _make_repo(tmp_path)
    assert _scaffold(root).returncode == 0
    proc = _scaffold(root, "--force")
    assert proc.returncode == 0, proc.stderr


# --- --sync-engine -----------------------------------------------------------


def test_sync_engine_restores_vendored_engine(tmp_path):
    root = _make_repo(tmp_path)
    assert _scaffold(root).returncode == 0
    vendored = root / ".docsmith" / "engine" / "docsmith.py"
    original = vendored.read_text(encoding="utf-8")

    vendored.write_text(original + "\n# LOCAL DRIFT MARKER\n", encoding="utf-8")
    proc = _scaffold(root, "--sync-engine")
    assert proc.returncode == 0, proc.stderr

    restored = vendored.read_text(encoding="utf-8")
    assert "# LOCAL DRIFT MARKER" not in restored
    assert restored == original

    config = json.loads(
        (root / ".docsmith" / "config.json").read_text(encoding="utf-8")
    )
    assert config["engine_version"]


def test_sync_engine_requires_existing_config(tmp_path):
    root = _make_repo(tmp_path)
    proc = _scaffold(root, "--sync-engine")
    assert proc.returncode == 2
    assert "config.json" in proc.stderr


# --- settings.json merge -----------------------------------------------------


def test_settings_merge_idempotent_and_preserving(tmp_path):
    root = _make_repo(tmp_path)
    settings_path = root / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True)
    preexisting = {
        "permissions": {"allow": ["Bash(ls)"]},
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": []}]},
    }
    settings_path.write_text(json.dumps(preexisting), encoding="utf-8")

    assert _scaffold(root).returncode == 0
    assert _scaffold(root, "--force").returncode == 0

    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    assert settings["permissions"] == preexisting["permissions"]
    assert settings["hooks"]["PreToolUse"] == preexisting["hooks"]["PreToolUse"]
    assert _hook_entry_count(settings) == 1


# --- adopt mode --------------------------------------------------------------


def test_adopt_migrates_legacy_map(tmp_path):
    root = _make_repo(tmp_path)
    legacy_dir = root / ".claude" / "hooks"
    legacy_dir.mkdir(parents=True)
    legacy = {
        "_comment": "metadata that must be dropped",
        "src/": [{"path": "docs/a.md", "reason": "core", "message": ""}],
        "main.go": ["docs/b.md"],
    }
    (legacy_dir / "doc_sync_map.json").write_text(json.dumps(legacy), encoding="utf-8")

    proc = _scaffold(root)  # adopt auto-detected from the legacy map
    assert proc.returncode == 0, proc.stderr
    assert "legacy map migrated" in proc.stdout

    docmap = json.loads(
        (root / ".docsmith" / "docmap.json").read_text(encoding="utf-8")
    )
    assert docmap["version"] == 1
    assert not any(key.startswith("_") for key in docmap["map"])
    assert docmap["map"]["src/"] == [
        {"path": "docs/a.md", "reason": "core", "message": ""}
    ]
    assert docmap["map"]["main.go"] == [
        {"path": "docs/b.md", "reason": "", "message": ""}
    ]


def test_adopt_harvests_sources_yml(tmp_path):
    root = _make_repo(tmp_path)
    site_dir = root / "docs-site"
    site_dir.mkdir()
    (site_dir / "sources.yml").write_text(
        "site:\n"
        "  name: Legacy KB\n"
        "  description: Legacy docs\n"
        "  repo_url: https://github.com/acme/legacy\n"
        "  edit_branch: main\n"
        "exclude:\n"
        "  dir_basenames: [.git, node_modules]\n"
        "okf:\n"
        "  allowed_types: [ADR, Guide]\n"
        "  mapping_rules:\n"
        "    - {match: all, type: Overview, status: draft, tags: []}\n"
        "sources:\n"
        "  - id: docs\n"
        "    title: Docs\n"
        "    collector: markdown_tree\n"
        "    path: docs\n"
        "    destination: product\n",
        encoding="utf-8",
    )

    proc = _scaffold(root)  # adopt auto-detected from sources.yml
    assert proc.returncode == 0, proc.stderr

    config = json.loads(
        (root / ".docsmith" / "config.json").read_text(encoding="utf-8")
    )
    assert config["site"]["enabled"] is True
    assert config["site"]["workdir"] == "docs-site"
    assert config["site"]["name"] == "Legacy KB"
    assert config["site"]["description"] == "Legacy docs"
    assert config["site"]["repo_url"] == "https://github.com/acme/legacy"
    assert config["site"]["exclude"] == {"dir_basenames": [".git", "node_modules"]}
    assert config["site"]["sources"][0]["id"] == "docs"
    assert config["okf_compat"]["allowed_types"] == ["ADR", "Guide"]
    assert config["okf_compat"]["mapping_rules"] == [
        {"match": "all", "type": "Overview", "status": "draft", "tags": []}
    ]


# --- pre-commit wiring -------------------------------------------------------


def test_precommit_insertion_idempotent(tmp_path):
    root = _make_repo(tmp_path)
    precommit_path = root / ".pre-commit-config.yaml"
    precommit_path.write_text(_MINIMAL_PRECOMMIT, encoding="utf-8")

    assert _scaffold(root).returncode == 0
    text = precommit_path.read_text(encoding="utf-8")
    assert text.count("id: docsmith-validate") == 1
    assert "uv run .docsmith/engine/docsmith.py validate" in text
    assert "id: existing-hook" in text
    # Sibling-hook indentation preserved (existing hooks use 6 spaces).
    assert "      - id: docsmith-validate" in text
    # Site is enabled by default: the collect-render hook is wired exactly once.
    assert text.count("id: docsmith-collect-render") == 1

    assert _scaffold(root, "--force").returncode == 0
    reran = precommit_path.read_text(encoding="utf-8")
    assert reran.count("id: docsmith-validate") == 1
    assert reran.count("id: docsmith-collect-render") == 1


def test_precommit_without_repo_local_appends_block(tmp_path):
    root = _make_repo(tmp_path)
    precommit_path = root / ".pre-commit-config.yaml"
    precommit_path.write_text(
        "repos:\n"
        "  - repo: https://github.com/psf/black\n"
        "    rev: 24.1.0\n"
        "    hooks:\n"
        "      - id: black\n",
        encoding="utf-8",
    )
    proc = _scaffold(root)
    assert proc.returncode == 0, proc.stderr
    content = precommit_path.read_text(encoding="utf-8")
    # A `repo: local` block with the docsmith hooks is APPENDED (not a notice).
    assert "repo: local" in content
    assert "id: docsmith-validate" in content
    # The pre-existing hook is preserved.
    assert "id: black" in content
    # Idempotent: re-running does not duplicate.
    assert _scaffold(root, "--force").returncode == 0
    assert precommit_path.read_text(encoding="utf-8").count("id: docsmith-validate") == 1


def test_precommit_created_when_absent(tmp_path):
    """The exact regression: wire_precommit=True but no .pre-commit-config.yaml
    must CREATE the file (previously it was silently skipped)."""
    root = _make_repo(tmp_path)
    precommit_path = root / ".pre-commit-config.yaml"
    assert not precommit_path.exists()
    proc = _scaffold(root)
    assert proc.returncode == 0, proc.stderr
    assert precommit_path.is_file(), "pre-commit config must be created, not skipped"
    content = precommit_path.read_text(encoding="utf-8")
    assert "id: docsmith-validate" in content
    # Site enabled by default -> collect-render hook present exactly once.
    assert content.count("id: docsmith-collect-render") == 1


def test_scaffold_creates_makefile_requirements_and_setup(tmp_path):
    root = _make_repo(tmp_path)
    proc = _scaffold(root)
    assert proc.returncode == 0, proc.stderr
    makefile = root / "Makefile"
    setup = root / ".docsmith" / "setup.sh"
    reqs = root / ".docsmith" / "site-requirements.txt"
    assert makefile.is_file()
    assert "uv run .docsmith/engine" in makefile.read_text(encoding="utf-8")
    assert setup.is_file()
    assert setup.stat().st_mode & 0o111, "setup.sh must be executable"
    assert reqs.is_file()
    assert "mkdocs-material" in reqs.read_text(encoding="utf-8")


def test_scaffold_gitignores_site_venv_and_build(tmp_path):
    root = _make_repo(tmp_path)
    assert _scaffold(root).returncode == 0
    gi = (root / ".gitignore").read_text(encoding="utf-8")
    assert ".docsmith/site/.venv/" in gi
    assert ".docsmith/site/site/" in gi


def test_makefile_not_clobbered_when_present(tmp_path):
    root = _make_repo(tmp_path)
    makefile = root / "Makefile"
    makefile.write_text("custom:\n\techo hi\n", encoding="utf-8")
    proc = _scaffold(root)
    assert proc.returncode == 0, proc.stderr
    # An existing Makefile without the docsmith marker is preserved untouched.
    assert makefile.read_text(encoding="utf-8") == "custom:\n\techo hi\n"


def test_scaffold_site_enabled_configures_docs_source(tmp_path):
    # A site-enabled scaffold must configure a source over the docs tree, or
    # `collect build` produces an empty site (only the autogen landing page).
    root = _make_repo(tmp_path)
    proc = _scaffold(root)
    assert proc.returncode == 0, proc.stderr
    config = json.loads((root / ".docsmith" / "config.json").read_text())
    sources = config["site"]["sources"]
    assert sources, "site.sources must not be empty when the site is enabled"
    src = sources[0]
    assert src["collector"] == "markdown_tree"
    assert src["path"] == "docs"
    assert src["destination"] == "."


# --- vendored engine smoke ---------------------------------------------------


def test_vendored_engine_runs_validate(tmp_path):
    root = _make_repo(tmp_path)
    assert _scaffold(root).returncode == 0
    engine_cli = root / ".docsmith" / "engine" / "docsmith.py"

    proc = subprocess.run(
        [
            sys.executable,
            str(engine_cli),
            "--project-root",
            str(root),
            "validate",
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["command"] == "validate"
    assert payload["summary"]["errors"] == 0
