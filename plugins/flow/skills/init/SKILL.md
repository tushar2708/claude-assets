---
name: init
description: Initialize flow in a project — scaffold the docsmith .docsmith/ layout and append an idempotent flow-pattern block to the project's AGENTS.md (or CLAUDE.md), describing the flow lifecycle and command names.
disable-model-invocation: true
---

# init

Make a repository "flow-ready" in one invocation.

## Step 1 — scaffold docsmith into the project

Invoke `/flow:scaffold` (the renamed docsmith scaffold command), which runs the docsmith engine scaffolder to create the project's `.docsmith/` layout (config.json, docmap.json, state.json, engine). Do NOT reimplement scaffolding here — delegate to `/flow:scaffold`.

## Step 2 — append the idempotent flow-pattern block

Pick the project's agent-facing instructions file: `AGENTS.md` at repo root if it exists, else `CLAUDE.md`; if neither exists, create `AGENTS.md`. Write the block BETWEEN idempotent markers so a re-run rewrites in place instead of duplicating:

```
<!-- BEGIN flow:pattern -->
...block content...
<!-- END flow:pattern -->
```

On re-run: if the markers exist, replace the content between them; else append the whole block at the end of the file.

Block content (agent-facing, concise): state that this repo follows the flow dev-workflow, and list the lifecycle + commands:
- `/flow:grill` (interview) → `/flow:spec` (governed spec in docs/plans) → the project's own plan-mode skills → `/flow:make-tasks` (vertical slices → waves → per-file tasks) → `/flow:execute` (parallel edit-only agents) → `/flow:review` (read-only three-table review).
- `/flow:add-to-roadmap` (roadmap entry + the one GitHub issue) and `/flow:sync-issues` (reconcile roadmap ↔ GitHub).
- docs commands: `/flow:write-doc`, `/flow:write-plan`, `/flow:write-adr`, `/flow:write-prd`, `/flow:update-docs`.

This block is AGENT-FACING and belongs in AGENTS.md / CLAUDE.md, NEVER in a README.

## Report

Print what was scaffolded and which file the block was written to.
