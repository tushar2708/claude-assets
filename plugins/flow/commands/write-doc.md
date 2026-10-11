---
description: Write a documentation file the docsmith way — category template, evergreen rules, frontmatter stamping, docmap entry, and validation.
disable-model-invocation: true
---

> **MANDATORY: writer agent.** Every documentation file this command writes is written by the `flow:docsmith-doc-author` subagent (Task tool, `subagent_type: flow:docsmith-doc-author`). NEVER use `general-purpose`, an unnamed agent type, or any other agent to write files, and never write the doc yourself in the main thread. If the agent is unavailable, STOP and ask the user (AskUserQuestion); do not fall back. After the agent hands back, YOU re-run `validate` unscoped and quote its output; never accept an agent's "green" claim you have not reproduced.

Write a documentation file in one of these 5 evergreen categories: **tutorial**, **how-to**,
**reference**, **explanation**, or **runbook**.

1. From the user request in `#$ARGUMENTS`, determine which of the 5 categories the doc is.
2. If the category is ambiguous (e.g. how-to vs tutorial vs explanation), use the
   AskUserQuestion tool to confirm the category with the user before proceeding.
3. Dispatch to the `flow:docsmith-doc-author` subagent via the Task tool
   (`subagent_type: flow:docsmith-doc-author`), passing:
   - `category`: the resolved category
   - `topic`: the content of `#$ARGUMENTS`
   The subagent handles template selection, the evergreen writing rules, frontmatter
   stamping, correct file placement, the docmap entry, and running validate/score to green.
4. Verify (orchestrator): from the repo root run `uv run .docsmith/engine/docsmith.py validate`
   unscoped; it must print `FAILURES: 0`; quote the output; if there are failures re-dispatch the
   agent with the exact findings — do not fix them yourself.

#$ARGUMENTS
