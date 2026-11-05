# AGENTS.md

Instructions for agents working in this repository.

## No version numbers in any plugin manifest

No manifest carries a `version` field. This is intentional.
Plugins update in place on every commit.

| File | Rule |
|---|---|
| `plugins/<name>/.claude-plugin/plugin.json` | Never add `version`. |
| `.claude-plugin/marketplace.json` | Never add `version` to a plugin entry. |
| `plugins/<name>/plugin.json` | Never add `version`. |
| `plugins/<name>/.codex-plugin/plugin.json` | Never add `version`. |

### Why

- Claude Code reads the manifest `version` first, then the marketplace entry `version`.
- With neither set, it uses the commit SHA as the version.
- A pinned version freezes the cached copy. New commits never reach installed plugins.
- With no version, every commit is a new version. `install.sh` then updates each plugin.
- Source: [Versions and updates](https://code.claude.com/docs/en/plugins/loading.md).

### Codex

- Codex accepts a manifest with no `version`. It installs into a cache folder named `1.0.0`.
- Re-running `codex plugin add` re-copies the plugin files into that folder.
- `install.sh --codex` runs `codex plugin add` for every plugin, so Codex also updates in place.
- Checked with codex-cli 0.166.0 and a local marketplace. Re-check after a Codex upgrade.

### Shipping an update

1. Commit and push to `main`. The installer pulls from the remote, not from your folder.
2. Run `bash install.sh --claude`, or `--codex` for Codex.
3. Run `/reload-plugins` in Claude Code, or start a new Codex session.

## Commands

Run from the repo root. `make help` lists the targets.

| Command | What it does |
|---|---|
| `make test` | Runs every plugin suite below. |
| `make test-flow` | Runs the docsmith pytest suite (`plugins/flow/skills/docs/scripts/run_tests.sh`, via `uv`). |
| `make test-myhooks` | Runs the myhooks end-to-end rule tests (`plugins/myhooks/hooks/tests`). |
| `bash install.sh --claude` / `--codex` | Installs or updates every plugin. Add `uninstall` to remove them. |

Single test: there is no per-test target. From `plugins/myhooks/hooks`, run `uv run --with pytest --with ruff python -m pytest tests/test_rules.py::<name>`.

Current state, verified by running the targets:
- `make test-myhooks`: 25 passed.
- `make test-flow`: 47 failed, 400 passed. The failures are stale paths to `plugins/flow/commands/*.md`, which no longer exist. Fix the tests or the paths before relying on this suite.

No lint configuration exists at the repo root. Do not assume a lint command.

## Architecture

The repo is a marketplace of three plugins, published to Claude Code and Codex from the same tree.

- **Two marketplace files:** `.claude-plugin/marketplace.json` for Claude Code and `.agents/plugins/marketplace.json` for Codex. Both point at `./plugins/<name>`.
- **Two manifests per plugin:** `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/.codex-plugin/plugin.json`. A root `plugins/<name>/plugin.json` also exists.
- **Installer:** `install.sh` clones the repo to `~/.claude-assets` and calls `claude plugin marketplace` and `claude plugin install`, or the Codex equivalents. Its standalone-skill linking loops over a top-level `skills/` directory. This repo has none, so that step links nothing today.

### Plugins

- **`flow`:** a spec-driven workflow plus the docsmith documentation engine. The engine is `plugins/flow/skills/docs/scripts/docsmith.py` with its `docsmith_lib/` package. Hooks are declared in `plugins/flow/hooks/hooks.json`: a docs hook on edits (`skills/docs/scripts/hook/docsmith_hook.py`) and a plan-to-tasks hook on `ExitPlanMode`. The `project_templates/Makefile` under that skill is copied into other projects. It is not this repo's Makefile.
- **`myhooks`:** manages Claude Code hook rules. The hook scripts (`pretooluse_bash.py`, `pretooluse_file.py`, `posttooluse_file.py`) import the shared `custom_hooks` package:
  - `utils`: payload loading and the `allow`, `block`, and `warn` responses.
  - `dispatcher`: command categorization and rule application.
  - `nudge_once`: blocks the first time, allows repeats within a cooldown, and blocks again as a reminder after it expires. State lives in `~/.claude/hook_nudge_state.json`.
  - `registry`: register, enable, and disable named hooks.

  The hooks run from a venv at `plugins/myhooks/hooks/.venv`. `setup.sh` creates it and checks that the user's `settings.json` points at it. Tests pipe a payload into the real script and assert the exit code: 0 allows, 2 blocks.
- **`react-atomic-aesthetics`:** rules in `skills/ui-rulebook/references/RULES.md` and two agents, `architect` (plans) and `implementer` (builds). The `plan` and `review-ui` skills use the same rules.

### Where behavior lives

- Skill behavior is in each `SKILL.md`. Host-specific wording sits in its "Host adapters" section, which is why Claude Code and Codex variants appear side by side.
- Plugin docs sit in each plugin's `README.md`. The root `README.md` covers installation only.
