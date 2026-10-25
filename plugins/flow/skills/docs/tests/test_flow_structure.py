"""Structural smoke checks for the `flow` plugin.

Verifies that the plugin loads, every /flow:* command and skill resolves, and
every skill/command carries valid frontmatter. This does NOT test prose behavior
(the prose skills are verified by invoking them); the only exception is the
"prose pins" section at the bottom, which pins required rule text. Co-located with the docsmith
engine suite so it runs under the same run_tests.sh (uv provides pytest+pyyaml).
"""

import json
import re
from pathlib import Path

import pytest
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
    "plan-it",
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
USER_ONLY_SKILLS = ["grill", "spec", "sync-issues", "init", "plan-it"]


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


# --- prose pins ---------------------------------------------------------------
# The docstring above says prose behavior is not tested; these are the narrow
# exception. They pin REQUIRED RULE TEXT in specific skill/command/agent files
# so that it cannot silently regress or be edited away. They check that the
# text is present, not that the prose is good.

_WRITER_RULE_FILES = [
    "skills/spec/SKILL.md",
    "skills/init/SKILL.md",
    "commands/write-doc.md",
    "commands/write-plan.md",
    "commands/write-adr.md",
    "commands/write-prd.md",
    "commands/update-docs.md",
    "commands/fix-findings.md",
    "commands/execute.md",
]

_QUALIFIED_AGENT_FILES = [
    "skills/spec/SKILL.md",
    "commands/write-doc.md",
    "commands/write-plan.md",
    "commands/write-adr.md",
    "commands/write-prd.md",
    "commands/update-docs.md",
]

_FAILURES_ZERO_COMMAND_FILES = [
    "commands/write-doc.md",
    "commands/write-plan.md",
    "commands/write-adr.md",
    "commands/write-prd.md",
    "commands/update-docs.md",
]

# rule name -> (PLUGIN_ROOT-relative files, substrings EACH file must contain)
_REQUIRED_TEXT_PINS: dict[str, tuple[list[str], list[str]]] = {
    "writer-rule": (_WRITER_RULE_FILES, ["MANDATORY: writer agent", "general-purpose"]),
    "qualified-agent": (_QUALIFIED_AGENT_FILES, ["flow:docsmith-doc-author"]),
    "init": (["skills/init/SKILL.md"], ["ln -s AGENTS.md CLAUDE.md", "readlink"]),
    "spec": (
        ["skills/spec/SKILL.md"],
        [".docsmith/config.json", "/flow:scaffold", "validate"],
    ),
    "author": (
        ["agents/docsmith-doc-author.md"],
        [".docsmith/config.json", "exit code"],
    ),
    "spec-index": (
        ["skills/spec/SKILL.md"],
        ["FAILURES: 0", "docs/plans/INDEX.md", "Never hand-write the index"],
    ),
    "writer-failures-zero": (_FAILURES_ZERO_COMMAND_FILES, ["FAILURES: 0"]),
    "init-link-cases": (
        ["skills/init/SKILL.md"],
        [
            "AGENTS.md is a link to CLAUDE.md",
            "CLAUDE.md is a link to a missing AGENTS.md",
            "Both exist as regular files",
            "repo root",
            "do NOT copy the file",
            "--sync-engine",
        ],
    ),
    "scaffold-sync-engine": (["commands/scaffold.md"], ["--sync-engine"]),
    # wave model (spec 186): sub-feature waves -> stages -> tasks
    "wave-model": (
        ["skills/plan-it/references/wave-model.md"],
        [
            "S1 contracts",
            "S2 tests",
            "S3 implementation",
            "A file belongs to at most one task in a stage.",
            "Run for this wave",
            "Run for every wave",
            "Skip for every wave",
            "If the user said run, run. If the user said skip, skip. No exceptions.",
            "Never commit. Never offer or suggest a commit. Commit only when the user asks.",
            "| Title |",
            "| Wave |",
            "| Stage |",
            "| Files |",
            "| Changes |",
            "| Shared contracts |",
            "| Test cases |",
            "| Self-check |",
            "| Agent |",
            "| Done-when |",
            "| Blocked by |",
            "Never use general-purpose.",
        ],
    ),
    "plan-it": (
        ["skills/plan-it/SKILL.md"],
        [
            "references/wave-model.md",
            "End with ExitPlanMode.",
            "compliance ledger",
            "Translate every rule that asks for one wave per TDD phase into stages S1/S2/S3 of the sub-feature wave.",
        ],
    ),
    "make-tasks-wave-model": (
        ["commands/make-tasks.md"],
        [
            "skills/plan-it/references/wave-model.md",
            "A file belongs to at most one task in a stage.",
            "Never use agents to create tasks.",
            "Never commit.",
        ],
    ),
    "execute-wave-model": (
        ["commands/execute.md"],
        [
            "skills/plan-it/references/wave-model.md",
            "Only one stage in progress at a time.",
            "Never commit. Never offer or suggest a commit. Commit only when the user asks.",
            "The verify question is the only planned stop.",
        ],
    ),
    "spec-sub-features": (
        ["skills/spec/SKILL.md"],
        ["## Sub-features", "skills/plan-it/references/wave-model.md"],
    ),
    "grill-flow-spec": (["skills/grill/SKILL.md"], ["/flow:spec"]),
}

# rule name -> (PLUGIN_ROOT-relative file, substring it must NOT contain)
_FORBIDDEN_TEXT_PINS: dict[str, tuple[str, str]] = {
    "spec-no-init-fallback": ("skills/spec/SKILL.md", "or `/flow:init`"),
    # wave model (spec 186): sub-feature waves -> stages -> tasks
    "make-tasks-no-one-file-rule": ("commands/make-tasks.md", "One task = one file"),
    "make-tasks-no-slices": ("commands/make-tasks.md", "ertical slices"),  # "Vertical"/"vertical"
    "execute-no-todo-cap": ("commands/execute.md", "under 25"),
    "execute-no-end-commit": ("commands/execute.md", "No intermediate commits"),
    "grill-no-to-spec": ("skills/grill/SKILL.md", "/to-spec"),
    "make-tasks-no-absolute": ("commands/make-tasks.md", "ABSOLUTE"),
    "execute-no-absolute": ("commands/execute.md", "ABSOLUTE"),
    "plan-it-no-absolute": ("skills/plan-it/SKILL.md", "ABSOLUTE"),
    "wave-model-no-absolute": ("skills/plan-it/references/wave-model.md", "ABSOLUTE"),
}

_REQUIRED_TEXT_CASES = [
    pytest.param(rel_path, needle, id=f"{rule}:{rel_path}:{needle}")
    for rule, (rel_paths, needles) in _REQUIRED_TEXT_PINS.items()
    for rel_path in rel_paths
    for needle in needles
]

_FORBIDDEN_TEXT_CASES = [
    pytest.param(rel_path, needle, id=f"{rule}:{rel_path}")
    for rule, (rel_path, needle) in _FORBIDDEN_TEXT_PINS.items()
]

# `subagent_type: docsmith-doc-author`, `subagent_type="docsmith-doc-author"`,
# or the colon-less "subagent_type\n`docsmith-doc-author`" (any mix of colon,
# equals, whitespace/newlines, backticks, quotes or bold markers in between)
# names the agent WITHOUT the `flow:` plugin qualifier, which does not resolve
# when the plugin is installed. `subagent_type: flow:docsmith-doc-author` does
# not match: the qualifier's "flow:" sits between the separators and the name.
_BARE_AGENT_RE = re.compile(r"subagent_type[\s:=\"'`*]*docsmith-doc-author")

_PROSE_FILES = (
    sorted(PLUGIN_ROOT.glob("commands/*.md"))
    + sorted(PLUGIN_ROOT.glob("skills/*/SKILL.md"))
    + sorted(PLUGIN_ROOT.glob("agents/*.md"))
    + sorted(PLUGIN_ROOT.glob("skills/docs/references/*.md"))
)


@pytest.mark.parametrize("rel_path, needle", _REQUIRED_TEXT_CASES)
def test_prose_pin_required_text_present(rel_path: str, needle: str):
    text = (PLUGIN_ROOT / rel_path).read_text(encoding="utf-8")
    assert needle in text, f"{rel_path} must contain {needle!r}"


@pytest.mark.parametrize("rel_path, forbidden", _FORBIDDEN_TEXT_CASES)
def test_prose_pin_forbidden_text_absent(rel_path: str, forbidden: str):
    text = (PLUGIN_ROOT / rel_path).read_text(encoding="utf-8")
    assert forbidden not in text, f"{rel_path} must not contain {forbidden!r}"


@pytest.mark.parametrize(
    "sample, should_match",
    [
        pytest.param("subagent_type: docsmith-doc-author", True, id="colon"),
        pytest.param('subagent_type="docsmith-doc-author"', True, id="equals-quoted"),
        pytest.param("subagent_type\n`docsmith-doc-author`", True, id="newline-backtick-no-colon"),
        pytest.param("`subagent_type`: `docsmith-doc-author`", True, id="backticked-key"),
        pytest.param("subagent_type: flow:docsmith-doc-author", False, id="qualified-colon"),
        pytest.param("subagent_type\n`flow:docsmith-doc-author`", False, id="qualified-newline"),
    ],
)
def test_bare_agent_regex_classifies_samples(sample: str, should_match: bool):
    assert bool(_BARE_AGENT_RE.search(sample)) is should_match


@pytest.mark.parametrize(
    "prose_file",
    [pytest.param(p, id=str(p.relative_to(PLUGIN_ROOT))) for p in _PROSE_FILES],
)
def test_prose_pin_no_bare_doc_author_agent_name(prose_file: Path):
    text = prose_file.read_text(encoding="utf-8")
    match = _BARE_AGENT_RE.search(text)
    assert match is None, (
        f"{prose_file.relative_to(PLUGIN_ROOT)} names the agent without the "
        f"'flow:' qualifier: {match.group(0)!r}"
    )
