---
name: write-prd
description: Write and validate a docsmith Product Requirements Document. Use only when explicitly invoked.
disable-model-invocation: true
---

# Write Product Requirements Document

## Host adapters

- **Claude Code:** use `AskUserQuestion`, then dispatch writing only to `flow:docsmith-doc-author` with the Task tool.
- After the agent's hand-back, run `/humanizer` on each listed file, then re-run docsmith validate.
- **Codex:** use `request_user_input`; use a documentation-author agent when available, otherwise author directly.
- **Other hosts:** ask the same concise plain-text questions and author directly when no specialist exists.

## Workflow

1. Gather current-conversation context and ask for PRD title, scope (small, medium, large, or multi-phase), and target users (B2C, B2D, B2B, or internal).
2. Author the `prd` category document with the 20-section PRD template, category frontmatter including `type: prd`, evergreen status and `stale_after`, placement under `docs/prd/`, and a docmap entry where applicable.
3. Run validate and score to green, then unscoped `uv run .docsmith/engine/docsmith.py validate`. Correct through the selected authoring path until it reports `FAILURES: 0`; quote final output.
