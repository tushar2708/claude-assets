"""CLI-level tests for `docsmith collect` — render, check, clean, disabled
handling, and graceful build failure when mkdocs is absent."""

import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CLI = SKILL_DIR / "scripts" / "docsmith.py"


def _enable_site(root: Path, **site_overrides) -> None:
    """Enable the site pipeline on a COPY of the fixture config (mutates the
    copied config.json in tmp, never the checked-in fixture)."""
    config_path = root / ".docsmith" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    site = {
        "enabled": True,
        "workdir": ".docsmith/site",
        "name": "Fixture KB",
        "sources": [
            {
                "id": "docs",
                "title": "Docs",
                "collector": "markdown_tree",
                "path": "docs",
                "destination": "product",
                "follow_symlinks": False,
            },
            {
                "id": "readmes",
                "title": "READMEs",
                "collector": "readme_discovery",
                "paths": ["."],
                "destination": "readmes",
            },
        ],
    }
    site.update(site_overrides)
    config["site"] = site
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def _workdir(root: Path) -> Path:
    return root / ".docsmith" / "site"


def test_collect_render_writes_mkdocs_yml(fixture_project, run_cli):
    _enable_site(fixture_project)
    exit_code, _out = run_cli(fixture_project, "collect", "render", expect_json=False)
    assert exit_code == 0

    mkdocs_yml = _workdir(fixture_project) / "mkdocs.yml"
    assert mkdocs_yml.is_file()
    rendered = mkdocs_yml.read_text(encoding="utf-8")
    assert "Fixture KB" in rendered
    assert "nav:" in rendered
    assert "Pipeline" in rendered
    assert "product/pipeline/overview.md" in rendered

    autogen_docs = _workdir(fixture_project) / "autogen" / "docs"
    landing = (autogen_docs / "index.md").read_text(encoding="utf-8")
    assert "# Fixture KB" in landing
    assert "docsmith collect build" in landing

    # Every source-map entry carries the resolved docsmith category.
    source_map = json.loads((autogen_docs / "source-map.json").read_text(encoding="utf-8"))
    assert source_map and all("category" in entry for entry in source_map)
    assert (autogen_docs / "manifest.json").is_file()


def test_collect_render_landing_title_override(fixture_project, run_cli):
    _enable_site(fixture_project, landing_title="Custom Landing")
    exit_code, _out = run_cli(fixture_project, "collect", "render", expect_json=False)
    assert exit_code == 0
    landing = (_workdir(fixture_project) / "autogen" / "docs" / "index.md").read_text(
        encoding="utf-8"
    )
    assert "# Custom Landing" in landing
    # mkdocs site_name still comes from site.name.
    rendered = (_workdir(fixture_project) / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Fixture KB" in rendered


def test_collect_render_is_deterministic(fixture_project, run_cli):
    _enable_site(fixture_project)
    exit_code, _out = run_cli(fixture_project, "collect", "render", expect_json=False)
    assert exit_code == 0
    first = (_workdir(fixture_project) / "mkdocs.yml").read_bytes()

    exit_code, _out = run_cli(fixture_project, "collect", "render", expect_json=False)
    assert exit_code == 0
    second = (_workdir(fixture_project) / "mkdocs.yml").read_bytes()

    assert first == second


def test_collect_check_passes_on_rendered_tree(fixture_project, run_cli):
    _enable_site(fixture_project)
    exit_code, _out = run_cli(fixture_project, "collect", "render", expect_json=False)
    assert exit_code == 0
    exit_code, out = run_cli(fixture_project, "collect", "check", expect_json=False)
    assert exit_code == 0
    assert "FAILURES: 0" in out


def test_collect_check_fails_without_render(fixture_project, run_cli):
    _enable_site(fixture_project)
    exit_code, out = run_cli(fixture_project, "collect", "check", expect_json=False)
    assert exit_code == 1
    assert "[FAIL]" in out


def test_collect_clean_removes_autogen(fixture_project, run_cli):
    _enable_site(fixture_project)
    exit_code, _out = run_cli(fixture_project, "collect", "render", expect_json=False)
    assert exit_code == 0
    assert (_workdir(fixture_project) / "autogen").exists()
    assert (_workdir(fixture_project) / "mkdocs.yml").exists()

    exit_code, _out = run_cli(fixture_project, "collect", "clean", expect_json=False)
    assert exit_code == 0
    assert not (_workdir(fixture_project) / "autogen").exists()
    assert not (_workdir(fixture_project) / "mkdocs.yml").exists()


def test_site_disabled_render_exits_0_with_notice(fixture_project, run_cli):
    # The checked-in fixture config has site.enabled=false.
    exit_code, out = run_cli(fixture_project, "collect", "render", expect_json=False)
    assert exit_code == 0
    assert "disabled" in out
    assert not (_workdir(fixture_project) / "mkdocs.yml").exists()


def test_site_disabled_build_exits_2(fixture_project, run_cli):
    exit_code, _out = run_cli(fixture_project, "collect", "build", expect_json=False)
    assert exit_code == 2


def test_collect_build_exits_2_without_mkdocs(fixture_project, tmp_path):
    """`collect build` fails gracefully (exit 2, clear message) when no
    mkdocs binary is resolvable — forced deterministically by pointing PATH
    at an empty directory."""
    _enable_site(fixture_project)
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()
    env = os.environ.copy()
    env["PATH"] = str(empty_bin)

    proc = subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(fixture_project), "collect", "build"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 2
    assert "mkdocs binary not found" in proc.stderr


def test_site_workdir_override(fixture_project, run_cli):
    _enable_site(fixture_project)
    exit_code, _out = run_cli(
        fixture_project,
        "collect",
        "render",
        "--site-workdir",
        "custom/site",
        expect_json=False,
    )
    assert exit_code == 0
    assert (fixture_project / "custom" / "site" / "mkdocs.yml").is_file()
    assert not (_workdir(fixture_project) / "mkdocs.yml").exists()
