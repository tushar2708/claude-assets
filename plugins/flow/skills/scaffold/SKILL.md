---
name: scaffold
description: Scaffold the complete docsmith stack into the current project. Use only when explicitly invoked.
disable-model-invocation: true
---

# Scaffold Docsmith

Set up the complete stack by default: full profile, doc-site, project hook where supported, and pre-commit wiring. The engine creates scaffold files; never hand-write its generated outputs.

## Host adapters

- **Claude Code:** use `AskUserQuestion`; enable the project `.claude` PostToolUse hook when selected.
- **Codex:** use `request_user_input`; do not claim hook installation because Codex has no shipped docsmith hook adapter. Offer the portable pre-commit and Makefile policy instead.
- **Other hosts:** ask concise plain-text questions and use the portable pre-commit and Makefile policy.

## Procedure

1. Resolve `ROOT` with `git rev-parse --show-toplevel`, falling back to the working directory.
2. If `ROOT/.docsmith/config.json` exists, stop unless the user explicitly requests `--force` or `--sync-engine`.
3. Detect `ROOT/docs/` or Markdown files with frontmatter; use `--adopt` when either exists.
4. Ask one question confirming complete setup. Only after a user asks to customize, ask which components to omit; all components default to included.
5. Write `/tmp/docsmith-scaffold-answers.json` with full defaults: `profile: "full"`, `site_enabled: true`, `install_hook: true` only on Claude Code, and `wire_precommit: true`.
6. Resolve the installed Flow plugin root without hardcoding a host-specific environment variable: locate this skill's `../docs/scripts/docsmith.py`, then run it with `scaffold --project-root "$ROOT" --non-interactive --answers /tmp/docsmith-scaffold-answers.json`, plus selected `--adopt`, `--force`, or `--sync-engine` flags.
7. Report the engine's written, skipped, and notices output; enumerate its project state, pre-commit wiring, Makefile targets, `.gitignore` updates, and category directories. Recommend `make setup`, then validation and site commands.
8. Run `uv run "$ROOT/.docsmith/engine/docsmith.py" --project-root "$ROOT" validate` unscoped and report its full output. Do not fix adoption findings in this skill; direct users to `fix-findings` and `init`.
