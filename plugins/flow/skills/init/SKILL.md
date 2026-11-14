---
name: init
disable-model-invocation: true
description: "Initialize Flow onboarding: scaffold or refresh docsmith, create the portable roadmap registry, configure task tracking, and write idempotent agent guidance. Use only when explicitly invoked."
---

# Initialize Flow

Make the current repository flow-ready in one onboarding workflow.

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

## Host adapters

- **Claude Code:** use `AskUserQuestion`; include the project-level Docsmith PostToolUse hook when selected. Claude users invoke `/flow:init` directly; no Claude onboarding manifest is claimed.
- **Codex:** use `request_user_input`; do not claim a Docsmith hook adapter. Use portable pre-commit and Makefile policy instead.
- **Other hosts:** ask concise plain-text questions and use the portable pre-commit and Makefile policy.

## 1. Resolve the repository

Run `git rev-parse --show-toplevel`; if it fails, use the current working directory as `ROOT`. All paths below are relative to `ROOT`.

## 2. Scaffold or refresh Docsmith

The engine creates its own scaffold outputs; never hand-write them.

1. Detect an existing documentation tree (`ROOT/docs/` or Markdown files with YAML frontmatter). Use `--adopt` for an initial scaffold when either exists.
2. If `ROOT/.docsmith/config.json` exists, refresh the vendored engine with `--sync-engine` without replacing configuration or docmap. That refresh leaves `config.json` and the project files as they are, so tell the developer that `/flow:update` brings those up to date too. Otherwise scaffold the full profile, doc-site, pre-commit wiring, and category directories.
3. Ask one confirmation for the complete setup. Ask a follow-up only when the user requests customization; all components default to included.
4. Write `/tmp/docsmith-scaffold-answers.json` with `profile: "full"`, `site_enabled: true`, `wire_precommit: true`, and `install_hook: true` only for Claude Code. Codex and fallback hosts use `install_hook: false`.
5. Locate `../docs/scripts/docsmith.py` relative to this skill, then run its `scaffold` command with `--project-root "$ROOT" --non-interactive --answers /tmp/docsmith-scaffold-answers.json`, plus initial-scaffold `--adopt` or existing-project `--sync-engine` as applicable. Add `--force` only after explicit user approval.
6. Report the engine's written, skipped, and notice output. Then run the bootstrap immediately with `bash "$ROOT/.docsmith/setup.sh"`. It installs uv if missing, creates the doc-site venv at `.docsmith/site/.venv`, installs `.docsmith/site-requirements.txt` (mkdocs, its plugins, and their dependencies), and installs pre-commit with its git hook. Report its full output. A non-zero exit stops init and is reported as a failure. Afterward, `make validate`, `make docs-build`, and `make docs-serve` are available.

## 3. Initialize the shared roadmap and local tracker

Read `../../assets/tracking/README.md` before editing `roadmap.md`.

1. Select exactly one local tracker: Claude Code defaults to `claude-tasks` with location `Claude Code session` and integration `native TaskCreate/TaskUpdate`; Codex defaults to `todo-file` with location `docs/tasks/` and integration `filesystem`. On another host, ask the user to select a supported local tracker.
2. If `ROOT/roadmap.md` is absent, copy the shared template at `../../assets/roadmap/roadmap.md`, replacing `{{LOCAL_TOOL}}`, `{{LOCAL_LOCATION}}`, and `{{LOCAL_INTEGRATION}}` with the selected values.
3. If `ROOT/roadmap.md` exists, preserve all existing Epic sections and rows. Add the missing `## Task Tracking` heading and its exact table header only when absent. Add one local declaration row only when none exists; never infer or add cloud trackers from available tools.
4. Keep the tracking table columns exactly `Scope`, `Tool`, `Location`, and `Integration`. Optional cloud declarations use the same table and follow `assets/tracking/README.md`.
5. Retain the template's `## Epic:` and table format for new Epics. `roadmap.md` remains the cross-tracker Epic and Story index.

## 4. Write portable agent guidance idempotently

Write the Flow block between these exact markers, replacing only marker contents on repeat runs:

```markdown
<!-- BEGIN flow:pattern -->
This repository follows the Flow development workflow.
`grill` → `spec` → `plan-it` → `make-tasks` → `execute` → `review`.
Use `/flow:init` for onboarding, `/flow:add-to-roadmap` for tracked work, and `/flow:sync-issues` for reconciliation.
Use `/flow:write-doc`, `/flow:write-adr`, `/flow:write-prd`, and `/flow:update-docs` for documentation.
Documentation authoring uses the configured documentation-author role; never use a generic writer when that role is available.
<!-- END flow:pattern -->
```

Handle `AGENTS.md` and `CLAUDE.md` as follows:

| Starting state | Action |
| --- | --- |
| Neither exists | Create `AGENTS.md` with the block and create relative `CLAUDE.md → AGENTS.md` symlink. |
| AGENTS.md regular; CLAUDE.md absent | Update AGENTS.md block and create that relative symlink. |
| CLAUDE.md resolves to AGENTS.md | Update AGENTS.md block; preserve link. |
| CLAUDE.md links to missing AGENTS.md | Create AGENTS.md block; preserve link. |
| AGENTS.md links to CLAUDE.md | Update the real CLAUDE.md block; preserve links. |
| CLAUDE.md regular; AGENTS.md absent | Update CLAUDE.md block; create nothing else. |
| Both regular files | Ask whether to update both or AGENTS.md only; never overwrite either outside its markers. |
| CLAUDE.md resolves elsewhere | Ask before modifying either file. |

Create the symlink from `ROOT` with `ln -s AGENTS.md CLAUDE.md`. If it fails, report and stop; never copy the file. Verify an expected link using `readlink CLAUDE.md` and report its result.

## 5. Validate and report

Run `uv run "$ROOT/.docsmith/engine/docsmith.py" --project-root "$ROOT" validate` unscoped and print its full output. A repository is flow-ready only when it reports `FAILURES: 0`; otherwise report findings and direct the user to `fix-findings`. State the Docsmith action, selected local tracker, whether roadmap was created or preserved, guidance file action, and symlink result.
