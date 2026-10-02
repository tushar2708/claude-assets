---
description: Write a documentation file the docsmith way — category template, evergreen rules, frontmatter stamping, docmap entry, and validation.
disable-model-invocation: true
---

Write a documentation file in one of these 5 evergreen categories: **tutorial**, **how-to**,
**reference**, **explanation**, or **runbook**.

1. From the user request in `#$ARGUMENTS`, determine which of the 5 categories the doc is.
2. If the category is ambiguous (e.g. how-to vs tutorial vs explanation), use the
   AskUserQuestion tool to confirm the category with the user before proceeding.
3. Dispatch to the `docsmith-doc-author` subagent via the Task tool
   (`subagent_type: docsmith-doc-author`), passing:
   - `category`: the resolved category
   - `topic`: the content of `#$ARGUMENTS`
   The subagent handles template selection, the evergreen writing rules, frontmatter
   stamping, correct file placement, the docmap entry, and running validate/score to green.

#$ARGUMENTS
