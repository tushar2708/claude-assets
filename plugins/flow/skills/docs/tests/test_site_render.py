"""Tests for the mkdocs.yml render (minify plugin options) and for the
version pins in the site-requirements project template."""

import re
from pathlib import Path

import pytest

from docsmith_lib.site import engine

SKILL_DIR = Path(__file__).resolve().parent.parent
SITE_REQUIREMENTS = SKILL_DIR / "scripts" / "project_templates" / "site-requirements.txt"

MINIFY_PLUGIN = "  - minify:"
HTMLMIN_OPTS = "htmlmin_opts:"


def _render(tmp_path: Path, plugins: dict) -> str:
    """Render mkdocs.yml for a sparse config with the given site.plugins."""
    workdir = tmp_path / "site"
    ctx = engine.SiteContext(
        project_root=tmp_path,
        workdir=workdir,
        autogen_docs_dir=workdir / "autogen" / "docs",
        site_dir=workdir / "autogen" / "site",
        config={"site": {"plugins": plugins}},
    )
    rendered_path = engine.render_mkdocs_config(ctx, [])
    return rendered_path.read_text(encoding="utf-8")


MINIFY_CASES = [
    pytest.param({}, True, "minify_html: false", False, id="default-keeps-js-css-minify-html-off"),
    pytest.param({"minify": True}, True, "minify_html: false", False, id="minify-on-html-default-off"),
    pytest.param(
        {"minify": True, "minify_html": False}, True, "minify_html: false", False,
        id="html-explicitly-off",
    ),
    pytest.param(
        {"minify": True, "minify_html": True}, True, "minify_html: true", True,
        id="html-explicitly-on-adds-htmlmin-opts",
    ),
    pytest.param({"minify": False}, False, None, False, id="minify-off-no-plugin"),
]


@pytest.mark.parametrize("plugins,plugin_present,html_line,has_opts", MINIFY_CASES)
def test_minify_plugin_render(tmp_path, plugins, plugin_present, html_line, has_opts):
    rendered = _render(tmp_path, plugins)

    assert (MINIFY_PLUGIN in rendered) is plugin_present
    if html_line is not None:
        assert html_line in rendered
        assert "minify_js: true" in rendered
        assert "minify_css: true" in rendered
    assert (HTMLMIN_OPTS in rendered) is has_opts


def _requirement_lines() -> list:
    lines = SITE_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def test_site_requirements_template_has_requirements():
    assert _requirement_lines(), "site-requirements.txt template lists no packages"


@pytest.mark.parametrize("requirement", _requirement_lines())
def test_site_requirements_are_exact_pins(requirement):
    assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*==\d+(\.\d+)*", requirement), (
        f"{requirement!r} is not an exact `name==version` pin"
    )
