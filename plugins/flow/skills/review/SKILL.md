---
name: review
description: Critically review a scoped implementation without modifying files, tests, staging, or repository state. Use only when explicitly invoked.
disable-model-invocation: true
---

# Review Implementation

## Guardrails

This is read-only. Do not edit, create, delete, format, stage, unstage, restore, reset, stash, or run builds, tests, linters, pre-commit, or the app. Review only files within the user-provided task, plan, or diff scope; ignore all other changes.

## Host adapters

- **Claude Code:** use `AskUserQuestion` when scope or the governing planning skill is unknown; load declared skills with Claude Code skill invocation when available.
- **Codex:** use `request_user_input` when scope or the governing planning skill is unknown; read declared local skill instructions directly.
- **Other hosts:** ask concise plain-text questions; read the named skill instructions if accessible.

## Review sequence

1. Locate the governing plan and its `**Planned-with-skill:**` stamp. If no stamp exists, ask which planning skill applies; record a missing stamp as a compliance finding when a plan exists. If the user dismisses the question, proceed without a planning-skill comparison.
2. Check the plan against every mandatory rule and gate in the selected planning skill, then check the implementation against every planned file, unit, test, and wave.
3. Perform the functional pass before rules compliance. For every issue, read its governing plan/task text and classify it exactly as `PLAN-DRIFT`, `PLAN-GAP`, `PRE-EXISTING`, or `NO-GOVERNING-PLAN-TEXT`.
4. Then read applicable `CLAUDE.md`, `AGENTS.md`, and project rule files, and separately assess plan and implementation compliance.

## Report

Produce three markdown tables with columns: serial no, short description, origin, file and line number, and definitive fix rationale.

1. Functional bugs, including plan gaps and pre-existing defects.
2. Compliance bugs, including skill-conformance failures.
3. Better-than-plan implementations.

Every real issue is P0, includes a verified location and one definitive fix. Empty tables contain one `None found` row. End with one verdict line that counts `PLAN-DRIFT` separately from `PLAN-GAP` and `PRE-EXISTING` findings.
