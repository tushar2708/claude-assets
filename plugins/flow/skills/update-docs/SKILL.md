---
name: update-docs
description: Process pending docsmith update tasks, verify code claims, rewrite invalidated documentation, and validate it to green. Use only when explicitly invoked.
disable-model-invocation: true
---

# Update Docsmith Documentation

## Host adapters

- **Claude Code:** read its session task list; dispatch each document rewrite only to `flow:docsmith-doc-author` using the Task tool. Use `AskUserQuestion` if that agent is unavailable.
- **Codex:** inspect the active task context; use a documentation-author agent when available, otherwise rewrite the document directly. Use `request_user_input` for required input.
- **Other hosts:** inspect the available task list or user-supplied tasks; make the rewrite directly if no dedicated author agent exists.

## Resolve resources

For each resource, use the first existing candidate: project `.docsmith/engine/docsmith.py`, then `ai_docs/docsmith/engine/docsmith.py`, then this Flow skill's `../docs/scripts/docsmith.py`; data dir `.docsmith/` then `ai_docs/docsmith/`; and `../docs/references/rules.md`. Read the project pre-commit config and Makefile docsmith target when resolution is unclear.

## Workflow

1. Find tasks titled `[docsmith] update <doc path>` and group those for the same document.
2. For each document, read it, the task-specified code, and matching `docmap.json` entries.
3. Verify cited claims against the code, then rewrite invalidated sections wholesale. Preserve diagrams and document altitude; do not add changelogs or update paragraphs. Keep sentences and table cells under fifteen words; put larger updates in tables.
4. Refresh stale date, generated metadata, and the H1 index table within the same rewrite.
5. Run per-document validate and score for evergreen categories. Iterate to green; then run final unscoped validation and quote its output.
6. Complete processed tasks. Extend `docmap.json` when newly documented code is uncovered.
