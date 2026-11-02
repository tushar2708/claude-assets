---
name: fix-findings
description: Run docsmith validation and mechanically resolve every known finding. Use only when explicitly invoked.
disable-model-invocation: true
---

# Fix Docsmith Findings

Read `../docs/references/autofix-patterns.md` first. It is the authority for each finding shape: apply its prescribed fix without re-analysis or individual narration.

## Host adapters

- **Claude Code:** use `AskUserQuestion` for a reference-defined blocking choice; dispatch documentation edits only to `flow:docsmith-doc-author` when direct work is not appropriate.
- **Codex:** use `request_user_input` for that choice; use an available documentation-author agent, otherwise perform the mechanical documentation edit directly.
- **Other hosts:** ask concise plain-text questions; make direct mechanical documentation edits when no specialized agent exists.

## Workflow

1. Run `uv run .docsmith/engine/docsmith.py validate --json > /tmp/docsmith-findings.json` and group findings by check.
2. Fix in this order: `frontmatter`, `decisions`, `drift`, `links`, `coverage`, `docmap`, then `plan-ttl`.
3. For drift, distinguish a real stale citation from a false positive before applying the corresponding reference fix.
4. For a relocation, use `git mv` and repair all internal relative links in every touched document.
5. Re-run validation after each affected batch. Continue until unscoped validation reports `FAILURES: 0 / WARNINGS: 0`.
6. Ask only when the reference requires input: no verifiable citation equivalent, genuinely uncertain category, or ADR renumbering without a repository convention.
7. Report only counts fixed by check, remaining `<!-- TODO(docsmith): could not verify -->` markers, and final validation status.
