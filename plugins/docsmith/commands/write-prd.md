---
description: Write a Product Requirements Document the docsmith way — prd category template, evergreen rules, frontmatter stamping, docmap entry, and validation.
disable-model-invocation: true
---

# Write Product Requirements Document (PRD)

This command authors a doc in the `prd` category.

1. **Gather context** from `#$ARGUMENTS` plus the current conversation.

2. **Ask the user these clarifying questions** via the `AskUserQuestion` tool, then fold the answers into the topic you hand off:
   - **PRD title** — what should the document be called?
   - **Scope** — small / medium / large / multi-phase.
   - **Target users** — B2C / B2D / B2B / internal.

3. **Dispatch to the `docsmith-doc-author` subagent** (Task tool, `subagent_type: docsmith-doc-author`) with `category: prd` and the assembled topic. The subagent applies the 20-section `prd.md` template, prd-category frontmatter (`type: prd`, evergreen, includes `stale_after`), placement under `docs/prd/`, a docmap entry if applicable, and validate/score-to-green.

#$ARGUMENTS