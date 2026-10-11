---
description: Write a Product Requirements Document the docsmith way — prd category template, evergreen rules, frontmatter stamping, docmap entry, and validation.
disable-model-invocation: true
---

# Write Product Requirements Document (PRD)

> **MANDATORY: writer agent.** Every documentation file this command writes is written by the `flow:docsmith-doc-author` subagent (Task tool, `subagent_type: flow:docsmith-doc-author`). NEVER use `general-purpose`, an unnamed agent type, or any other agent to write files, and never write the doc yourself in the main thread. If the agent is unavailable, STOP and ask the user (AskUserQuestion); do not fall back. After the agent hands back, YOU re-run `validate` unscoped and quote its output; never accept an agent's "green" claim you have not reproduced.

This command authors a doc in the `prd` category.

1. **Gather context** from `#$ARGUMENTS` plus the current conversation.

2. **Ask the user these clarifying questions** via the `AskUserQuestion` tool, then fold the answers into the topic you hand off:
   - **PRD title** — what should the document be called?
   - **Scope** — small / medium / large / multi-phase.
   - **Target users** — B2C / B2D / B2B / internal.

3. **Dispatch to the `flow:docsmith-doc-author` subagent** (Task tool, `subagent_type: flow:docsmith-doc-author`) with `category: prd` and the assembled topic. The subagent applies the 20-section `prd.md` template, prd-category frontmatter (`type: prd`, evergreen, includes `stale_after`), placement under `docs/prd/`, a docmap entry if applicable, and validate/score-to-green.

4. **Verify (orchestrator)**: from the repo root run `uv run .docsmith/engine/docsmith.py validate` unscoped; it must print `FAILURES: 0`; quote the output; if there are failures re-dispatch the agent with the exact findings — do not fix them yourself.

#$ARGUMENTS