---
name: init
description: Initialize flow in a project — verify docsmith is scaffolded (the user runs the user-only /flow:scaffold), write the project's AGENTS.md with an idempotent flow-pattern block, and link CLAUDE.md to AGENTS.md so both point at the same flow lifecycle and command names.
disable-model-invocation: true
---

# init

Make a repository "flow-ready" once the user has run `/flow:scaffold`.

> **MANDATORY: writer agent.** This skill writes `AGENTS.md` itself, in the main thread: no purpose-built agent exists for it. NEVER delegate file writing to `general-purpose` or any other generic agent. Documentation files under docs/ are only ever written by the `flow:docsmith-doc-author` agent.

## Step 1 — verify docsmith is scaffolded

`/flow:scaffold` is a user-only command (`disable-model-invocation: true`); you cannot invoke it and must NOT replicate its work by other means. Check whether `.docsmith/config.json` exists. If it exists, go to Step 2. If it does not, tell the user to run `/flow:scaffold` themselves and STOP; resume only after they confirm and you have verified the file now exists.

## Step 2 — the instructions file and the CLAUDE.md soft link

Write the agent-facing instructions file and link `CLAUDE.md` to it. Pick and handle the files by this table:

| Starting state | Action |
| --- | --- |
| Neither AGENTS.md nor CLAUDE.md exists | Create `AGENTS.md` containing the block between the markers, then from the repo root create the soft link with `ln -s AGENTS.md CLAUDE.md` (relative target) |
| AGENTS.md exists as a regular file, CLAUDE.md absent | Write or replace the block in AGENTS.md; create the link `ln -s AGENTS.md CLAUDE.md` from the repo root |
| CLAUDE.md is a link that resolves to AGENTS.md (compare resolved paths, not the `readlink` text) | Leave the link; write or replace the block in AGENTS.md |
| CLAUDE.md is a link to a missing AGENTS.md | Create `AGENTS.md` with the block; leave the link |
| AGENTS.md is a link to CLAUDE.md | Leave both; write or replace the block in CLAUDE.md, the real file |
| CLAUDE.md is a regular file and AGENTS.md is absent | Write the block into CLAUDE.md; create nothing else |
| Both exist as regular files | STOP and ask the user (AskUserQuestion): write the block into both files, or into AGENTS.md only; NEVER overwrite or replace CLAUDE.md |
| CLAUDE.md is a link that resolves anywhere else | STOP and ask the user (AskUserQuestion) |

Run `ln -s` from the repo root. If it fails (for example a filesystem without symlinks), STOP and report; do NOT copy the file. Verify the link with `readlink CLAUDE.md` (must print `AGENTS.md`). Re-runs are idempotent: if the markers exist replace the content between them, otherwise append the block at the end; never duplicate the block and never recreate an existing correct link.

Write the block BETWEEN idempotent markers:

```
<!-- BEGIN flow:pattern -->
...block content...
<!-- END flow:pattern -->
```

Block content (agent-facing, concise): state that this repo follows the flow dev-workflow, and list the lifecycle + commands:
- `/flow:grill` (interview) → `/flow:spec` (governed spec with sub-features) → `/flow:plan-it` (Plan Mode plan: sub-feature waves → stages → tasks) → `/flow:make-tasks` (copies the plan into tasks) → `/flow:execute` (runs wave → stage → task) → `/flow:review` (read-only three-table review).
- `/flow:add-to-roadmap` (roadmap entry + its issue in the declared tracker) and `/flow:sync-issues` (reconcile roadmap ↔ tracker).
- docs commands: `/flow:write-doc`, `/flow:write-adr`, `/flow:write-prd`, `/flow:update-docs`.
- Documentation files are written only by the `flow:docsmith-doc-author` agent; never use `general-purpose` or any generic agent to write files.

This block is AGENT-FACING and belongs in AGENTS.md / CLAUDE.md, NEVER in a README.

## Report

After Step 2, run the project's validator UNSCOPED from the repo root — `uv run .docsmith/engine/docsmith.py validate` — and print its full output. The repository counts as "flow-ready" only when it prints `FAILURES: 0`; otherwise list the findings and tell the user to run `/flow:fix-findings` (user-only). Also print what was verified and written, which file the block was written to, and the result of `readlink CLAUDE.md`. Projects scaffolded before the validator fixes carry an older vendored engine in `.docsmith/engine/`; tell the user to run `/flow:scaffold` and choose the engine refresh (`--sync-engine`) to receive the fixes.
