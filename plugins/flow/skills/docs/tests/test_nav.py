"""Tests for docsmith_lib.site.nav — subsystem-first navigation, hubs,
trailing Decisions/Plans/Uncategorized sections, and the legacy type-first
builder."""

import json
from pathlib import Path

from docsmith_lib import config as config_lib
from docsmith_lib.site import engine


def _enable_site(root: Path, extra_config: dict = None, **site_overrides) -> None:
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
    if extra_config:
        config.update(extra_config)
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def _add_doc(root: Path, rel_path: str, fm_type: str, title: str, status: str) -> None:
    doc_path = root / rel_path
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(
        f"---\ntype: {fm_type}\ntitle: {title}\nstatus: {status}\n---\n\n# {title}\n\nBody.\n",
        encoding="utf-8",
    )


def _render(root: Path):
    """Run the full render pipeline; returns (ctx, entries, sections)."""
    project_root, config = config_lib.load_config(project_root=root)
    ctx = engine.build_site_context(project_root, config)
    entries, sections, _link_warnings = engine.run_render_pipeline(ctx)
    return ctx, entries, sections


def _leaf_paths(nav_items: list) -> list:
    paths = []
    for item in nav_items:
        if "path" in item:
            paths.append(item["path"])
        else:
            paths.extend(_leaf_paths(item["children"]))
    return paths


_GENERATED_NAV_PATHS = ("decisions-index.md", "plans-index.md")


def _doc_leaf_paths(sections: list) -> list:
    """All leaf paths across sections, minus generated hub/index pages."""
    return [
        path
        for section in sections
        for path in _leaf_paths(section["nav_items"])
        if not path.startswith("_hubs/") and path not in _GENERATED_NAV_PATHS
    ]


def test_subsystem_first_grouping(fixture_project):
    _enable_site(fixture_project)
    _add_doc(
        fixture_project,
        "docs/plans/archive/00-archived-plan.md",
        "plan",
        "Archived Plan",
        "draft",
    )
    _add_doc(
        fixture_project,
        "docs/plans/02-superseded-plan.md",
        "plan",
        "Superseded Plan",
        "superseded",
    )
    ctx, entries, sections = _render(fixture_project)

    titles = [section["title"] for section in sections]
    assert titles == [
        "How To",
        "Pipeline",
        "Reference",
        "Runbooks",
        "Tutorials",
        "Decisions",
        "Plans",
        "Uncategorized",
    ]

    # Pipeline section: hub first, then path-sorted leaves.
    pipeline = next(s for s in sections if s["title"] == "Pipeline")
    assert pipeline["nav_items"][0] == {
        "title": "Overview",
        "path": "_hubs/pipeline/index.md",
    }
    assert [item["path"] for item in pipeline["nav_items"][1:]] == [
        "product/pipeline/broken.md",
        "product/pipeline/overview.md",
    ]

    # Hub page written with generated frontmatter, table, and site-absolute links.
    hub_text = (ctx.autogen_docs_dir / "_hubs" / "pipeline" / "index.md").read_text(
        encoding="utf-8"
    )
    assert hub_text.startswith("---\ngenerated:\n  by: docsmith\n  at: ")
    assert "| Doc | Category | Status | Updated |" in hub_text
    # Hub pages link RELATIVELY (mkdocs leaves absolute links unrewritten,
    # which 404 under directory-URL serving). Hub is at _hubs/pipeline/index.md,
    # so links to product/... resolve via ../../.
    assert "(../../product/pipeline/overview.md) | explanation | stable | - |" in hub_text
    assert "(../../product/pipeline/broken.md) | explanation | draft | - |" in hub_text

    # util-reference lands under its own subsystem section.
    reference = next(s for s in sections if s["title"] == "Reference")
    assert "product/reference/util-reference.md" in _leaf_paths(reference["nav_items"])

    # Decisions: trailing section, generated index first, then the ADR leaf.
    decisions = next(s for s in sections if s["title"] == "Decisions")
    assert decisions["nav_items"][0] == {"title": "Index", "path": "decisions-index.md"}
    assert [item["path"] for item in decisions["nav_items"][1:]] == [
        "product/decisions/ADR-001-use-go.md"
    ]
    decisions_index = (ctx.autogen_docs_dir / "decisions-index.md").read_text(encoding="utf-8")
    assert "| Number | Title | Status |" in decisions_index
    assert "| ADR-001 |" in decisions_index

    # Plans: active plan present; archived + superseded plans excluded.
    plans = next(s for s in sections if s["title"] == "Plans")
    plan_paths = _leaf_paths(plans["nav_items"])
    assert "product/plans/01-old-plan.md" in plan_paths
    assert not any("archive" in path for path in plan_paths)
    assert not any("superseded" in path for path in plan_paths)
    plans_index = (ctx.autogen_docs_dir / "plans-index.md").read_text(encoding="utf-8")
    assert "Old Plan" in plans_index
    assert "Archived Plan" not in plans_index
    assert "Superseded Plan" not in plans_index

    # Uncategorized: the discovered README (no category) is never dropped.
    uncategorized = next(s for s in sections if s["title"] == "Uncategorized")
    assert _leaf_paths(uncategorized["nav_items"]) == ["readmes/index.md"]

    # Nothing dropped: nav leaves == collected entries minus excluded plans.
    excluded_paths = {
        entry["output_path"]
        for entry in entries
        if "archive" in entry["output_path"] or "superseded" in entry["output_path"]
    }
    expected = sorted(
        entry["output_path"] for entry in entries if entry["output_path"] not in excluded_paths
    )
    assert sorted(_doc_leaf_paths(sections)) == expected


def test_section_order_pinning(fixture_project):
    _enable_site(
        fixture_project,
        nav={"style": "subsystem-first", "section_order": ["Tutorials", "Pipeline"]},
    )
    _ctx, _entries, sections = _render(fixture_project)
    titles = [section["title"] for section in sections]
    # Pinned first (in section_order order), remaining alphabetical,
    # trailing global sections still last.
    assert titles == [
        "Tutorials",
        "Pipeline",
        "How To",
        "Reference",
        "Runbooks",
        "Decisions",
        "Plans",
        "Uncategorized",
    ]


def test_subgrouping_by_category_over_threshold(fixture_project):
    _enable_site(
        fixture_project,
        nav={"style": "subsystem-first", "section_order": [], "subgroup_min_entries": 1},
    )
    _ctx, _entries, sections = _render(fixture_project)
    pipeline = next(s for s in sections if s["title"] == "Pipeline")
    # Hub first, then one category subgroup holding both explanation leaves.
    assert pipeline["nav_items"][0]["path"] == "_hubs/pipeline/index.md"
    subgroup = pipeline["nav_items"][1]
    assert subgroup["title"] == "Explanation"
    assert [item["path"] for item in subgroup["children"]] == [
        "product/pipeline/broken.md",
        "product/pipeline/overview.md",
    ]


def test_external_category_excluded_from_collection(fixture_project):
    _enable_site(fixture_project)
    _add_doc(
        fixture_project, "docs/pipeline/vendor-notes.md", "external", "Vendor Notes", "stable"
    )
    ctx, entries, sections = _render(fixture_project)
    # Filtered early: not in entries, not on disk, not in nav.
    assert not any(entry["title"] == "Vendor Notes" for entry in entries)
    assert not (ctx.autogen_docs_dir / "product" / "pipeline" / "vendor-notes.md").exists()
    assert "product/pipeline/vendor-notes.md" not in _doc_leaf_paths(sections)


def test_type_first_legacy_mode(fixture_project):
    allowed_types = [
        "decision",
        "tutorial",
        "how-to",
        "reference",
        "explanation",
        "runbook",
        "plan",
    ]
    _enable_site(
        fixture_project,
        extra_config={"okf_compat": {"allowed_types": allowed_types, "mapping_rules": []}},
        nav={"style": "type-first"},
    )
    ctx, entries, sections = _render(fixture_project)

    # Old shape: one section per OKF type (declaration order), trailing
    # Uncategorized for the README; no hubs, no generated index pages.
    titles = [section["title"] for section in sections]
    assert titles == allowed_types + ["Uncategorized"]

    explanation = next(s for s in sections if s["title"] == "explanation")
    assert [item["path"] for item in explanation["nav_items"]] == [
        "product/pipeline/broken.md",
        "product/pipeline/overview.md",
    ]

    assert not (ctx.autogen_docs_dir / "_hubs").exists()
    assert not (ctx.autogen_docs_dir / "decisions-index.md").exists()
    assert not (ctx.autogen_docs_dir / "plans-index.md").exists()

    # Legacy guarantee: every collected entry appears exactly once.
    assert sorted(_doc_leaf_paths(sections)) == sorted(e["output_path"] for e in entries)
