"""Structural smoke checks for the `flow` plugin.

Verifies that the plugin loads, every /flow:* command and skill resolves, and
every skill/command carries valid frontmatter. This does NOT test prose behavior
(the prose skills are verified by invoking them). Co-located with the docsmith
engine suite so it runs under the same run_tests.sh (uv provides pytest+pyyaml).
"""

import json
from pathlib import Path

import yaml

# tests/ -> docs -> skills -> PLUGIN_ROOT (flow)
PLUGIN_ROOT = Path(__file__).resolve().parents[3]

EXPECTED_SKILLS = [
    "docs",
    "grill",
    "grilling",
    "spec",
    "diagnosing-bugs",
    "handoff",
    "prototype",
    "sync-issues",
    "init",
]

EXPECTED_COMMANDS = [
    "make-tasks.md",
    "execute.md",
    "review.md",
    "add-to-roadmap.md",
    "write-doc.md",
    "write-plan.md",
    "write-adr.md",
    "write-prd.md",
    "update-docs.md",
    "scaffold.md",
    "fix-findings.md",
]

# Lifecycle/roadmap skills the spec requires to be user-invoked only.
# grilling is intentionally EXEMPT (spec: "Edit: none").
USER_ONLY_SKILLS = ["grill", "spec", "sync-issues", "init"]


def _parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---"), f"{path} has no frontmatter fence"
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"{path} frontmatter is not closed"
    data = yaml.safe_load(parts[1])
    assert isinstance(data, dict), f"{path} frontmatter is not a mapping"
    return data


def test_manifest_names_flow():
    manifest = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    assert manifest.exists(), "plugin.json missing"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["name"] == "flow", f"plugin name is {data['name']!r}, want 'flow'"


def test_expected_skills_present_with_valid_frontmatter():
    skills_dir = PLUGIN_ROOT / "skills"
    present = {p.name for p in skills_dir.iterdir() if p.is_dir()}
    for name in EXPECTED_SKILLS:
        assert name in present, f"skill dir missing: {name}"
    for skill_md in skills_dir.glob("*/SKILL.md"):
        fm = _parse_frontmatter(skill_md)
        assert fm.get("name"), f"{skill_md} frontmatter missing non-empty name"
        assert fm.get("description"), f"{skill_md} frontmatter missing non-empty description"


def test_expected_commands_present_and_frontmatter_parses():
    commands_dir = PLUGIN_ROOT / "commands"
    present = {p.name for p in commands_dir.glob("*.md")}
    for name in EXPECTED_COMMANDS:
        assert name in present, f"command missing: {name}"
    for cmd in commands_dir.glob("*.md"):
        text = cmd.read_text(encoding="utf-8")
        assert text.strip(), f"{cmd} is empty"
        if text.startswith("---"):
            parts = text.split("---", 2)
            assert len(parts) >= 3, f"{cmd} frontmatter is not closed"
            assert isinstance(yaml.safe_load(parts[1]), dict), f"{cmd} frontmatter invalid"


def test_user_only_skills_disable_model_invocation():
    for name in USER_ONLY_SKILLS:
        fm = _parse_frontmatter(PLUGIN_ROOT / "skills" / name / "SKILL.md")
        assert fm.get("disable-model-invocation") is True, (
            f"skill {name} must set disable-model-invocation: true"
        )


def test_no_stale_docsmith_references():
    stale = ["skills/docsmith", "/docsmith:"]
    self_path = Path(__file__).resolve()
    offenders = []
    for path in PLUGIN_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.resolve() == self_path:
            continue  # this test file names the forbidden strings on purpose
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for needle in stale:
            if needle in text:
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)} contains {needle!r}")
    assert not offenders, "stale docsmith references found:\n" + "\n".join(offenders)
