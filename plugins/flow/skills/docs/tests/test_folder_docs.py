"""Tests for folder-doc collection: readme_discovery collects README.md,
AGENTS.md and CLAUDE.md with deterministic, collision-free output names, and
markdown_tree skips all three names so nothing is collected twice."""

from pathlib import Path

import pytest

from docsmith_lib.site.collectors import collect_markdown_tree, collect_readme_discovery
from docsmith_lib.site.collectors.readme_discovery import FOLDER_DOC_FILENAMES

_DESTINATION = "readmes"


class _Symlink:
    """Marks a tree entry as a symlink to `target` (relative to the link's folder)."""

    def __init__(self, target: str) -> None:
        self.target = target


def _build_tree(root: Path, files: dict) -> None:
    """Create `files` under root: str values are file contents, _Symlink values are links."""
    for rel_path, spec in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(spec, _Symlink):
            path.symlink_to(spec.target)
            continue
        path.write_text(spec, encoding="utf-8")


def _readme_source(exclude: list) -> dict:
    return {"id": "readmes", "paths": ["."], "destination": _DESTINATION, "exclude": exclude}


def _source_to_output(entries: list, repo_root: Path) -> dict:
    return {
        Path(entry["source_path"]).relative_to(repo_root).as_posix(): entry["output_path"]
        for entry in entries
    }


@pytest.mark.parametrize(
    "files, source_exclude, exclude_filenames, expected",
    [
        pytest.param(
            {"pkg/svc/AGENTS.md": "# Svc agents\n"},
            [],
            [],
            {"pkg/svc/AGENTS.md": "readmes/pkg/svc.md"},
            id="agents-only-folder-takes-parent-name",
        ),
        pytest.param(
            {"pkg/svc/README.md": "# Svc\n", "pkg/svc/AGENTS.md": "# Svc agents\n"},
            [],
            [],
            {
                "pkg/svc/README.md": "readmes/pkg/svc.md",
                "pkg/svc/AGENTS.md": "readmes/pkg/svc-agents.md",
            },
            id="readme-and-agents-folder-get-distinct-outputs",
        ),
        pytest.param(
            {
                "pkg/svc/README.md": "# Svc\n",
                "pkg/svc/AGENTS.md": "# Svc agents\n",
                "pkg/svc/CLAUDE.md": "# Svc claude\n",
            },
            [],
            [],
            {
                "pkg/svc/README.md": "readmes/pkg/svc.md",
                "pkg/svc/AGENTS.md": "readmes/pkg/svc-agents.md",
                "pkg/svc/CLAUDE.md": "readmes/pkg/svc-claude.md",
            },
            id="all-three-regular-files-get-distinct-outputs",
        ),
        pytest.param(
            {"pkg/svc/AGENTS.md": "# Svc agents\n", "pkg/svc/CLAUDE.md": _Symlink("AGENTS.md")},
            [],
            [],
            {"pkg/svc/AGENTS.md": "readmes/pkg/svc.md"},
            id="symlinked-claude-is-skipped",
        ),
        pytest.param(
            {"pkg/svc/CLAUDE.md": "# Svc claude\n", "pkg/svc/AGENTS.md": _Symlink("CLAUDE.md")},
            [],
            [],
            {"pkg/svc/CLAUDE.md": "readmes/pkg/svc-claude.md"},
            id="symlinked-agents-is-skipped",
        ),
        pytest.param(
            {"pkg/svc/README.md": "# Svc\n", "pkg/svc/CLAUDE.md": "# Svc claude\n"},
            [],
            [],
            {
                "pkg/svc/README.md": "readmes/pkg/svc.md",
                "pkg/svc/CLAUDE.md": "readmes/pkg/svc-claude.md",
            },
            id="regular-claude-is-collected",
        ),
        pytest.param(
            {"pkg/svc/CLAUDE.md": "# Svc claude\n"},
            [],
            [],
            {"pkg/svc/CLAUDE.md": "readmes/pkg/svc-claude.md"},
            id="claude-only-folder-keeps-claude-suffix",
        ),
        pytest.param(
            {"README.md": "# Root\n", "AGENTS.md": "# Root agents\n", "CLAUDE.md": "# Root claude\n"},
            [],
            [],
            {"README.md": "readmes/index.md", "AGENTS.md": "readmes/agents.md", "CLAUDE.md": "readmes/claude.md"},
            id="root-folder-docs",
        ),
        pytest.param(
            {"AGENTS.md": "# Root agents\n", "CLAUDE.md": _Symlink("AGENTS.md")},
            [],
            [],
            {"AGENTS.md": "readmes/agents.md"},
            id="root-agents-without-readme-and-symlinked-claude",
        ),
        pytest.param(
            {"python/README.md": "# Python\n", "python/AGENTS.md": "# Python agents\n"},
            [],
            [],
            {"python/README.md": "readmes/python.md", "python/AGENTS.md": "readmes/python-agents.md"},
            id="single-parent-segment",
        ),
        pytest.param(
            {"cloud_backend/core_svc/AGENTS.md": "# Core agents\n"},
            [],
            [],
            {"cloud_backend/core_svc/AGENTS.md": "readmes/cloud-backend/core_svc.md"},
            id="leading-segments-hyphenated-last-segment-kept",
        ),
        pytest.param(
            {"pkg/svc/README.md": "# Svc\n", "pkg/svc/AGENTS.md": "# Svc agents\n"},
            ["pkg/svc/README.md"],
            [],
            {"pkg/svc/AGENTS.md": "readmes/pkg/svc.md"},
            id="readme-excluded-by-source-glob-frees-parent-name",
        ),
        pytest.param(
            {
                "pkg/svc/README.md": "# Svc\n",
                "pkg/svc/AGENTS.md": "# Svc agents\n",
                "pkg/svc/CLAUDE.md": "# Svc claude\n",
            },
            [],
            ["README.md", "CLAUDE.md"],
            {"pkg/svc/AGENTS.md": "readmes/pkg/svc.md"},
            id="shared-exclude-filenames-are-honoured",
        ),
    ],
)
def test_readme_discovery_collects_folder_docs(tmp_path, files, source_exclude, exclude_filenames, expected):
    repo_root = tmp_path / "repo"
    autogen_docs_dir = tmp_path / "autogen"
    _build_tree(repo_root, files)

    entries = collect_readme_discovery(
        _readme_source(source_exclude), repo_root, autogen_docs_dir, {"filenames": exclude_filenames}
    )

    assert _source_to_output(entries, repo_root) == expected
    output_paths = [entry["output_path"] for entry in entries]
    assert len(output_paths) == len(set(output_paths))
    for source_rel, output_rel in expected.items():
        copied = (autogen_docs_dir / output_rel).read_text(encoding="utf-8")
        assert copied == (repo_root / source_rel).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "files, expected_titles",
    [
        pytest.param(
            {"pkg/payment_svc/AGENTS.md": "No heading.\n"},
            {"pkg/payment_svc/AGENTS.md": "Payment Svc"},
            id="agents-only-falls-back-to-parent-name",
        ),
        pytest.param(
            {
                "pkg/payment/README.md": "No heading.\n",
                "pkg/payment/AGENTS.md": "No heading.\n",
                "pkg/payment/CLAUDE.md": "No heading.\n",
            },
            {
                "pkg/payment/README.md": "Payment",
                "pkg/payment/AGENTS.md": "Payment Agents",
                "pkg/payment/CLAUDE.md": "Payment Claude",
            },
            id="folder-docs-of-one-folder-get-distinct-fallback-titles",
        ),
        pytest.param(
            {"README.md": "No heading.\n", "AGENTS.md": "No heading.\n", "CLAUDE.md": "No heading.\n"},
            {"README.md": "Readme", "AGENTS.md": "Agents", "CLAUDE.md": "Claude"},
            id="root-fallback-titles",
        ),
        pytest.param(
            {"pkg/payment/AGENTS.md": "---\ntype: Overview\n---\n\n# Payment Service\n"},
            {"pkg/payment/AGENTS.md": "Payment Service"},
            id="h1-heading-wins-over-fallback",
        ),
    ],
)
def test_readme_discovery_folder_doc_titles(tmp_path, files, expected_titles):
    repo_root = tmp_path / "repo"
    _build_tree(repo_root, files)

    entries = collect_readme_discovery(_readme_source([]), repo_root, tmp_path / "autogen", {})

    titles = {
        Path(entry["source_path"]).relative_to(repo_root).as_posix(): entry["title"] for entry in entries
    }
    assert titles == expected_titles


_MIXED_TREE = {
    "docs/sub/README.md": "# Sub\n",
    "docs/sub/AGENTS.md": "# Sub agents\n",
    "docs/sub/CLAUDE.md": "# Sub claude\n",
    "docs/sub/guide.md": "# Guide\n",
}


@pytest.mark.parametrize(
    "source, expected_output_paths",
    [
        pytest.param(
            {"id": "docs", "path": "docs", "destination": "product"},
            ["product/sub/guide.md"],
            id="directory-mode",
        ),
        pytest.param(
            {"id": "docs", "paths": sorted(_MIXED_TREE), "destination": "flat"},
            ["flat/guide.md"],
            id="discrete-files-mode",
        ),
    ],
)
def test_markdown_tree_skips_every_folder_doc_name(tmp_path, source, expected_output_paths):
    repo_root = tmp_path / "repo"
    _build_tree(repo_root, _MIXED_TREE)

    entries = collect_markdown_tree(source, repo_root, tmp_path / "autogen", {})

    assert sorted(entry["output_path"] for entry in entries) == expected_output_paths
    collected_names = {Path(entry["source_path"]).name for entry in entries}
    assert collected_names.isdisjoint(FOLDER_DOC_FILENAMES)


def test_folder_docs_are_collected_exactly_once_across_collectors(tmp_path):
    repo_root = tmp_path / "repo"
    autogen_docs_dir = tmp_path / "autogen"
    _build_tree(
        repo_root,
        {
            "README.md": "# Root\n",
            "AGENTS.md": "# Root agents\n",
            "CLAUDE.md": _Symlink("AGENTS.md"),
            "notes.md": "# Notes\n",
            "pkg/svc/README.md": "# Svc\n",
            "pkg/svc/AGENTS.md": "# Svc agents\n",
            "pkg/svc/CLAUDE.md": "# Svc claude\n",
            "pkg/svc/design.md": "# Design\n",
        },
    )

    tree_entries = collect_markdown_tree(
        {"id": "all", "path": ".", "destination": "repository"}, repo_root, autogen_docs_dir, {}
    )
    folder_doc_entries = collect_readme_discovery(_readme_source([]), repo_root, autogen_docs_dir, {})

    all_entries = tree_entries + folder_doc_entries
    source_paths = [entry["source_path"] for entry in all_entries]
    output_paths = [entry["output_path"] for entry in all_entries]
    assert len(source_paths) == len(set(source_paths))
    assert len(output_paths) == len(set(output_paths))
    assert sorted(_source_to_output(tree_entries, repo_root)) == ["notes.md", "pkg/svc/design.md"]
    assert sorted(_source_to_output(folder_doc_entries, repo_root)) == [
        "AGENTS.md",
        "README.md",
        "pkg/svc/AGENTS.md",
        "pkg/svc/CLAUDE.md",
        "pkg/svc/README.md",
    ]
