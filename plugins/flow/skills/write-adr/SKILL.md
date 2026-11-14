---
name: write-adr
description: Write and validate a docsmith Architecture Decision Record. Use only when explicitly invoked.
disable-model-invocation: true
---
# Write Architecture Decision Record

## Host adapters

- **Claude Code:** use `AskUserQuestion` to confirm the absolute ADR directory (default docs/adr), then dispatch writing only to `flow:docsmith-doc-author`.
- After the agent's hand-back, run `/humanizer` on each listed file, then re-run docsmith validate.
- **Codex:** use `request_user_input` to confirm the directory; use a documentation-author agent when available, otherwise author the ADR directly.
- **Other hosts:** obtain the same confirmation in plain text; author directly when no specialist exists.

## Workflow

1. Extract a normalized decision topic from the invocation and current conversation.
2. Before any write, confirm the complete absolute ADR directory with the user.
3. Author the `decision` category document using the first static prefix of `categories.decision.dir_patterns[0]` (default `docs/decisions/`). Use next available zero-padded `ADR-{NNN}` number, required Status, Context, at least two Options Considered, Decision, and Consequences sections, substantial researched content, and immutable supersede-chain rules.
4. Run unscoped `uv run .docsmith/engine/docsmith.py validate`; it must report `FAILURES: 0`. If it fails, correct the ADR through the selected authoring path, then rerun validation and quote final output.

## When to disuss an ADR with the user?

1. There are any major architectural decisions being taken. (not features, something that decides how a bunch of present and future features will have to be built)
2. Anything that needs to be followed across the codebase as a pattern (only new patterns being decided. Eg. We follow strict domain driven design)
3. Non functional constriants. Eg. We can't use AWS lambda for the service X, because it requires in-memory caching and long-running backgrund threads. Serverless functions will break it.
4. Anything that won't be obvious to a new intern or a smaller AI model, with little context.