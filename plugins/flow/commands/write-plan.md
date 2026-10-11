---
description: Create a structured implementation plan (docsmith plan category) — stages/tasks/subtasks, tracker table, mandatory review stages, numbered-prefix filename, frontmatter, validation.
disable-model-invocation: true
---

> **MANDATORY: writer agent.** Every documentation file this command writes is written by the `flow:docsmith-doc-author` subagent (Task tool, `subagent_type: flow:docsmith-doc-author`). NEVER use `general-purpose`, an unnamed agent type, or any other agent to write files, and never write the doc yourself in the main thread. If the agent is unavailable, STOP and ask the user (AskUserQuestion); do not fall back. After the agent hands back, YOU re-run `validate` unscoped and quote its output; never accept an agent's "green" claim you have not reproduced.

This command authors a doc in the **`plan`** category.

Gather the plan scope from `#$ARGUMENTS`. Before dispatching, ask the user these three
questions via the **AskUserQuestion** tool:

1. **Context source** — existing doc path / paste content / conversation context
2. **Scope** — 2-3 stages / 4-5 stages / 6+ stages / determine from context
3. **Review depth** — checklist only / +testing / full review

Then dispatch to the **`flow:docsmith-doc-author`** subagent (Task tool, `subagent_type:
flow:docsmith-doc-author`) with `category: plan` and the topic (scope + the three answers). The
subagent owns everything: the plan template (stages → tasks → subtasks, tracker table with
legend, mandatory review stages), numbered-prefix filename placement, plan-category
frontmatter (`type: plan`, no `stale_after`), docmap if applicable, and validate-to-green.

Verify (orchestrator): from the repo root run `uv run .docsmith/engine/docsmith.py validate`
unscoped; it must print `FAILURES: 0`; quote the output; if there are failures re-dispatch the
agent with the exact findings — do not fix them yourself.

#$ARGUMENTS
