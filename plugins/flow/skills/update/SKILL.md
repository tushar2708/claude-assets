---
name: update
disable-model-invocation: true
description: "Bring a project that already has Flow and docsmith installed up to date with the installed plugin: compare the vendored engine, config.json, project files, hook and guidance block with what the plugin ships, report what is outdated, and apply targeted edits after confirmation. Use only when explicitly invoked, for example after the plugin was updated, or when docsmith validation flags documents that look valid."
---

# Update Flow

Make an existing Flow install current. `/flow:init` sets a project up. This skill brings a project that is already set up in line with the plugin version that is installed now.

Use it after the plugin is updated. Use it also when `docsmith validate` ends with the hint to run `/flow:update`: a project that predates a release can reject documents that the newer rules accept. For example, an older `config.json` has its own list of allowed statuses, so a spec with `status: ready` fails validation until that list is updated.

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

## Host adapters

- **Claude Code:** use `AskUserQuestion`. Check and update the project-level docsmith hook.
- **Codex:** use `request_user_input`. Skip the hook checks: Codex has no docsmith hook adapter.
- **Other hosts:** ask concise plain-text questions, and skip the hook checks.

## Rules

1. **Never copy a file over a project file.** The only wholesale replacement is the vendored engine in `.docsmith/engine/`, which the plugin owns, and it is done by the engine's own `--sync-engine`. Every other change is a targeted edit: add a block that is missing, change one value, or apply one hunk of a diff. A project file may hold project-specific content, such as a Makefile with the team's own targets, and a copy would destroy it.
2. **Never run `scaffold` without `--sync-engine`, and never use `--force`.** A full scaffold regenerates `config.json`.
3. **Touch only the files in the table below.** Never change documents under `docs/`, and never change `roadmap.md`.
4. **Change nothing before the developer confirms.** Additions are confirmed together. A change to something that already exists is confirmed one item at a time, with the old and the new text shown.
5. **Never commit.**

| File | Update method |
|---|---|
| `.docsmith/engine/` | Replace, through `scaffold --sync-engine` only |
| `.docsmith/config.json` | Targeted edits for the rules in `references/migrations.md` only |
| `Makefile` | Add each missing docsmith target as a block. Change one target's recipe only when it differs from the shipped one, and the developer approves. Never replace the file |
| `.pre-commit-config.yaml` | Add each missing docsmith hook by `id`. Change one hook's `entry` line only when it differs, and the developer approves. Never replace the file |
| `.docsmith/setup.sh`, `.docsmith/site-requirements.txt` | Apply the differing hunks one at a time, after approval. Create the file only when it is absent |
| `.claude/hooks/docsmith_hook.py` | Apply the differing hunks one at a time, after approval |
| `.claude/settings.json` | Add the docsmith `PostToolUse` entry if it is missing. Change nothing else in it |
| `.gitignore` | Append the docsmith lines that are missing |
| Flow block in `AGENTS.md` or `CLAUDE.md` | Replace only the text between the `flow:pattern` markers |

## 1. Resolve the repository and check the install

1. Run `git rev-parse --show-toplevel`; if it fails, use the current working directory as `ROOT`. All paths below are relative to `ROOT`.
2. If `ROOT/.docsmith/config.json` does not exist, STOP. Tell the developer to run `/flow:init`, and wait. This skill updates an install. It does not create one.
3. The shipped files are in `../docs/scripts/` relative to this skill. Call that folder `SHIPPED`. Check that `SHIPPED/docsmith.py` exists.

## 2. Record a baseline

From `ROOT`, run `uv run .docsmith/engine/docsmith.py validate` unscoped, with its output written to a file. Keep the failures and warnings. After the update, the report shows what it fixed.

## 3. Analyze, read-only

Run every check below. Change nothing in this step.

**A. Engine.**

- Compare `SHIPPED/docsmith_lib/` with `.docsmith/engine/docsmith_lib/`, ignoring `__pycache__`. List every file that differs, is missing, or is extra.
- Compare `SHIPPED/docsmith.py` with `.docsmith/engine/docsmith.py`, ignoring the first line of the installed file when it starts with `# VENDORED by docsmith scaffold`.
- Do not use the engine version number to decide. The number does not change with every release, so only the file comparison counts.

**B. Config.** Read `.docsmith/config.json` and `references/migrations.md` in full. Check every rule against the file. Report each rule as outdated or current, with its mode.

**C. Makefile.** Parse the shipped `SHIPPED/project_templates/Makefile` into units: the `DOCSMITH :=` variable, the names on its `.PHONY` line, and each target (the `name:` line with its `##` help text, and the tab-indented recipe lines under it). Parse `ROOT/Makefile` the same way. For each shipped target report: `missing`, `current` (same recipe), or `differs` (a different recipe). If `ROOT/Makefile` does not exist, report that. If it uses `$(DOCSMITH)` in a block you would add, check that the variable is defined.

**D. Pre-commit.** The shipped hook ids are `docsmith-validate` and, when `site.enabled` is true in the config, `docsmith-collect-render`. Their `entry` lines are in `SHIPPED/project_templates/pre-commit-config.yaml` and in the function `_collect_render_entry` of `SHIPPED/docsmith_lib/scaffold.py`. For each id in `ROOT/.pre-commit-config.yaml` report: `missing`, `current`, or `differs` in its `entry` line. If the file does not exist, report that.

**E. Setup files.** Compare `.docsmith/setup.sh` and `.docsmith/site-requirements.txt` with the files of the same name in `SHIPPED/project_templates/`. Report each as `current`, `differs`, or `missing`, and keep the diff.

**F. Hook (Claude Code only).** If `.claude/hooks/docsmith_hook.py` exists, compare it with `SHIPPED/hook/docsmith_hook.py` and keep the diff. Check `.claude/settings.json` for a `PostToolUse` entry whose command contains `docsmith_hook.py`. If `.claude/hooks/posttooluse_file.py` already handles doc sync, report that as a notice and do not touch the hook.

**G. Gitignore.** The docsmith lines are the list `_GITIGNORE_LINES` in `SHIPPED/docsmith_lib/scaffold.py`. Report each line that `.gitignore` lacks.

**H. Flow block.** Find the text between `<!-- BEGIN flow:pattern -->` and `<!-- END flow:pattern -->` in `AGENTS.md` or `CLAUDE.md`. Compare it with the block in section 4 of `../init/SKILL.md`. If no block exists, report that and suggest `/flow:init`. Do not add one.

## 4. Report, then confirm

Show one table: item, state (`current`, `outdated`, `missing`, `customized`), and the action. Split the actions into two groups:

- **Additions:** the engine replacement, an `Auto` migration, a missing Makefile target, a missing pre-commit hook, a missing `.gitignore` line, a missing hook entry in `settings.json`, a missing setup file.
- **Changes to what exists:** an `Ask` migration, a differing recipe or `entry`, a differing hunk of a file, a differing Flow block.

If nothing is outdated, say so, run step 6, and stop.

Ask one question through the host's question tool: "Apply the additions?" with "Apply the additions (Recommended)", "Choose one by one", and "Report only". On "Report only", stop after step 6. For each change to what exists, ask one question: show the old and the new text, with "Apply" and "Keep mine". A kept item is recorded as kept in the final report and is not asked again.

## 5. Apply

Apply in this order. After each group, tell the developer what you changed.

1. **Engine.** From `ROOT`, run the shipped `docsmith.py scaffold --project-root "$ROOT" --non-interactive --sync-engine`. It replaces `.docsmith/engine/` and stamps `engine_version` in `config.json`. It also writes `config.json` back with 2-space indentation, so a hand-formatted array may be reflowed onto several lines. It changes no value besides `engine_version`. Report its output.
2. **Config.** Edit `.docsmith/config.json` with targeted edits, one rule at a time, as `references/migrations.md` says. Keep the file's key order and its 2-space indentation.
3. **Makefile.** For each missing target, append its shipped block at the end of the file, with one blank line before it, and keep the tabs of the recipe. Add the target's name to the existing `.PHONY` line. If there is none, add one above the block. Add the `DOCSMITH := uv run .docsmith/engine/docsmith.py` line near the top only when a block you added uses it and the variable is not defined. For a `differs` target the developer approved, replace only that target's recipe lines.
4. **Pre-commit.** For each missing hook, insert its block under the `hooks:` list of the existing `repo: local` entry, with the same indentation as the hooks already there. If there is no `repo: local` entry, append one. Use the block shape of `_precommit_block` in `SHIPPED/docsmith_lib/scaffold.py`. For a `differs` hook the developer approved, replace only its `entry:` line.
5. **Setup files.** For each approved hunk, edit that hunk into the project file. Never copy the shipped file over it. If a file is missing, create it from the shipped file, and keep `.docsmith/setup.sh` executable.
6. **Hook.** Apply each approved hunk of `.claude/hooks/docsmith_hook.py`. Add the `PostToolUse` entry to `.claude/settings.json` with the matcher and command of `_merge_settings` in `SHIPPED/docsmith_lib/scaffold.py`, keeping every other key.
7. **Gitignore.** Append each missing line.
8. **Flow block.** Follow section 4 of `../init/SKILL.md`, including its table for `AGENTS.md` and `CLAUDE.md`. Replace only the text between the markers.

## 6. Validate and report

1. Run `uv run .docsmith/engine/docsmith.py validate` unscoped again, with its output written to a file, and print it. Compare it with the baseline from step 2.
2. Report: which items were updated, which were kept as they were, and which findings the update fixed. If a finding is new, say so and name the change that probably caused it.
3. If failures remain, list them and direct the developer to `fix-findings`. A failure that a migration cannot explain is a real document problem, not an outdated install. Do not invent a change to hide it.
