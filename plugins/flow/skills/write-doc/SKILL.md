---
name: write-doc
description: Write and validate a docsmith evergreen documentation file. Use only when explicitly invoked.
disable-model-invocation: true
---

# Write Docsmith Documentation

## Host adapters

- **Claude Code:** use `AskUserQuestion` for category ambiguity, then dispatch writing only to `flow:docsmith-doc-author` with the Task tool.
- After the agent's hand-back, run `/humanizer` on each listed file, then re-run docsmith validate.
- **Codex:** use `request_user_input` for ambiguity; use a documentation-author agent when available, otherwise author directly.
- **Other hosts:** ask the same concise plain-text question and author directly when no specialist exists.

## Workflow

1. Classify the requested document as tutorial, how-to, reference, explanation, or runbook. Ask only when category remains ambiguous.
2. Apply its category template, evergreen rules, frontmatter, correct location, and docmap entry.
3. Run validate and score as applicable. Run unscoped `uv run .docsmith/engine/docsmith.py validate`; correct through the selected authoring path until it reports `FAILURES: 0`, then quote its output.
