---
description: Scaffold docsmith into the current project — create .docsmith/ (config, docmap, vendored engine), install the project-level PostToolUse hook, wire pre-commit, and create the category directories.
disable-model-invocation: true
---

Set up docsmith for THIS project. This is a one-time bootstrap that runs the docsmith engine's
`scaffold` command; the engine creates every file — never hand-write any of them yourself.

**Guiding principle — set up EVERYTHING.** The goal is a fully-governed project, so enable every
piece by default: the full profile, the doc-site, the project-level hook, and pre-commit wiring.
Only leave a piece out when the user EXPLICITLY declines it. Never present skipping as the default,
and never recommend the minimal path — the recommended choice is always the most complete setup.

Do the following in order:

1. **Resolve the project root.** Run `git rev-parse --show-toplevel`; if that fails, use the current
   working directory. Call it `ROOT`. Everything scaffolds into `ROOT`.

2. **Check if it is already scaffolded.** If `ROOT/.docsmith/config.json` already exists, tell the user
   the project is already set up and STOP — unless they explicitly want to re-scaffold (`--force`) or only
   refresh the vendored engine (`--sync-engine`, which re-copies `ROOT/.docsmith/engine/` and bumps the
   recorded `engine_version` without touching config/docmap).

3. **Detect an existing docs tree.** If `ROOT/docs/` already exists or the repo already has markdown files
   with YAML frontmatter, plan to pass `--adopt` (adopt-in-place instead of a fresh tree). Otherwise omit it.

4. **Confirm the full setup with the user** via the AskUserQuestion tool. Do NOT ask four separate
   yes/no questions that invite skipping. Ask ONE question: "Set up the complete docsmith stack for this
   project?" with these options, recommended first:
   - **"Yes — set up everything (Recommended)"** → full profile + doc-site + project hook + pre-commit.
     This is the default; pick it unless the user says otherwise.
   - **"Let me choose what to include"** → only then ask a follow-up (one AskUserQuestion, multi-select)
     listing the four pieces — Full profile, Doc-site, Project hook, Pre-commit — with ALL FOUR
     pre-described as recommended, and treat anything the user does not explicitly remove as included.
   For every individual piece, the recommended answer is always to include it. The project-level hook is
   written into `ROOT/.claude/settings.json` + `ROOT/.claude/hooks/docsmith_hook.py`, so it fires ONLY in
   this project (nothing global) — always include it unless the repo already has its own docsmith hook.
   Keep `docs_dir` as `docs` unless the user asks otherwise.

5. **Write an answers file** at `/tmp/docsmith-scaffold-answers.json` (via the Write tool). Default every
   toggle to the fullest setup — `profile: "full"`, `site_enabled: true`, `install_hook: true`,
   `wire_precommit: true` — and flip a value to `false` (or a smaller profile) ONLY for a piece the user
   explicitly declined in step 4:
   `{"project_name": "<ROOT dir basename>", "repo_url": "<`git remote get-url origin` or null>", "docs_dir": "docs", "profile": "full", "site_enabled": true, "site_name": "<project_name> Docs", "install_hook": true, "wire_precommit": true}`

6. **Run the engine scaffold, non-interactively** (the interactive wizard's prompts cannot run here, so
   `--non-interactive --answers` is required). The engine lives in the installed plugin:
   ```
   uv run "${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/flow}/skills/docs/scripts/docsmith.py" \
     scaffold --project-root "ROOT" --non-interactive --answers /tmp/docsmith-scaffold-answers.json
   ```
   Append `--adopt` if step 3 detected an existing docs tree. Append `--force` ONLY when the user chose to
   re-scaffold an already-set-up project. Append `--profile <choice>` is unnecessary — the profile comes
   from the answers file.

7. **Report the engine's summary verbatim** (the `written / skipped / notices` lines it prints), then tell
   the user what it created and the next steps:
   - `ROOT/.docsmith/{config.json, docmap.json, state.json}` and the vendored engine at `ROOT/.docsmith/engine/`.
   - The project PostToolUse hook (if chosen).
   - The pre-commit config (if chosen) — `ROOT/.pre-commit-config.yaml`, created from a shipped template
     when absent, or the docsmith hooks appended idempotently when it already exists.
   - The `ROOT/Makefile` (targets: `setup`, `validate`, `score`, `docs-render`, `docs-build`, `docs-serve`,
     `precommit`, `clean`), and — when the site is enabled — `ROOT/.docsmith/site-requirements.txt` (the
     mkdocs toolchain declared as ordinary Python deps) and `ROOT/.docsmith/setup.sh` (the idempotent
     bootstrap).
   - The `.gitignore` additions (state, site autogen, the site venv `.docsmith/site/.venv/`, and the built
     site `.docsmith/site/site/`).
   - The category directories under `docs/`.
   - **First real step: run `make setup`** — the idempotent bootstrap installs uv (if missing), creates the
     doc-site venv with the mkdocs toolchain, and installs the pre-commit hooks. Then `make validate`,
     `make docs-build` / `make docs-serve`. (Everything the site needs is carried by the project; no manual
     `pip install mkdocs` step.)
   - Author docs with `/flow:write-doc`, `/flow:write-plan`, `/flow:write-adr`,
     `/flow:write-prd`; review `ROOT/.docsmith/config.json` (categories, dir_patterns) any time.

If the engine prints a NOTICE (e.g. `.claude/settings.json` was not valid JSON, or a `Makefile` already
exists without the docsmith targets), relay that notice to the user with the manual step it suggests.

#$ARGUMENTS
