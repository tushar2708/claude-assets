---
description: Create a structured implementation plan (docsmith plan category) — stages/tasks/subtasks, tracker table, mandatory review stages, numbered-prefix filename, frontmatter, validation.
disable-model-invocation: true
---

This command authors a doc in the **`plan`** category.

Gather the plan scope from `#$ARGUMENTS`. Before dispatching, ask the user these three
questions via the **AskUserQuestion** tool:

1. **Context source** — existing doc path / paste content / conversation context
2. **Scope** — 2-3 stages / 4-5 stages / 6+ stages / determine from context
3. **Review depth** — checklist only / +testing / full review

Then dispatch to the **`docsmith-doc-author`** subagent (Task tool, `subagent_type:
docsmith-doc-author`) with `category: plan` and the topic (scope + the three answers). The
subagent owns everything: the plan template (stages → tasks → subtasks, tracker table with
legend, mandatory review stages), numbered-prefix filename placement, plan-category
frontmatter (`type: plan`, no `stale_after`), docmap if applicable, and validate-to-green.

#$ARGUMENTS
