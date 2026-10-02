# flow

flow is a unified dev-workflow plugin. Its docs module is deterministic documentation governance — a Python
CLI that validates, scores, and site-builds documentation by category, plus a set of evergreen writing rules.

## Commands

- `/flow:write-doc` — write a category doc.
- `/flow:write-plan` — write an implementation plan.
- `/flow:write-adr` — write an ADR (architecture decision record).
- `/flow:write-prd` — write a PRD (product requirements document).
- `/flow:update-docs` — process pending doc-update tasks.

## What else ships

The plugin ships a `docsmith-doc-author` subagent that authors docs strictly per category and template, so
every document lands in the right place in the right shape. It also installs a PostToolUse hook that nudges
you to update docs when you edit code mapped in a project's `.docsmith/docmap.json`, keeping documentation in
step with the code it describes.

## Local install

```
claude plugin marketplace add /Users/tushar/Documents/tushar2708/claude-assets
claude plugin install flow@claude-assets --scope user
```

Local dev: during development flow lives at ~/.claude/plugins/flow.
