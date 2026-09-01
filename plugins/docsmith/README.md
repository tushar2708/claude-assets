# docsmith

docsmith is deterministic documentation governance — a Python CLI that validates, scores, and site-builds
documentation by category, plus a set of evergreen writing rules, packaged as a Claude Code plugin.

## Commands

- `/docsmith:write-doc` — write a category doc.
- `/docsmith:write-plan` — write an implementation plan.
- `/docsmith:write-adr` — write an ADR (architecture decision record).
- `/docsmith:write-prd` — write a PRD (product requirements document).
- `/docsmith:update-docs` — process pending doc-update tasks.

## What else ships

The plugin ships a `docsmith-doc-author` subagent that authors docs strictly per category and template, so
every document lands in the right place in the right shape. It also installs a PostToolUse hook that nudges
you to update docs when you edit code mapped in a project's `.docsmith/docmap.json`, keeping documentation in
step with the code it describes.

## Local install

```
claude plugin marketplace add /Users/tushar/Documents/tushar2708/dev-env/ai-coding/claude_home/plugins-local/docsmith
claude plugin install docsmith@docsmith --scope user
```
