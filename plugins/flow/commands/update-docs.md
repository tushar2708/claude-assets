---
description: Process pending "[docsmith] update ..." documentation tasks — verify claims against code, rewrite invalidated sections wholesale, refresh frontmatter, validate and score to green.
disable-model-invocation: true
---

> Agents: when `[docsmith] update ...` tasks are pending in the session task list, OFFER this
> command to the user before committing — that is step 3 of the docsmith task-queue protocol.

Process every pending documentation task in your task tracker tool (not any todo files):

1. **Collect and group.** List the session tasks titled `[docsmith] update <doc path>`.
   Group tasks that touch the same doc: review them together and update that document in
   one go.

2. **Read everything first.** Per doc: read the doc itself, the code paths listed in the
   task bodies, and the doc's entries in `ai_docs/docsmith/docmap.json` (an entry's `reason`
   tells you why the mapping exists; a `message` carries custom update instructions that
   take precedence).

3. **Verify, then rewrite wholesale.** Check each of the doc's claims against the code —
   grep the cited `path#Symbol` anchors. Rewrite invalidated sections wholesale, as if
   authored today, per `${CLAUDE_PLUGIN_ROOT}/skills/docs/references/rules.md`:
   - Never append change-notes, changelogs, or "Update:" paragraphs (R1/R2).
   - NEVER degrade or drop diagrams, box drawings, flowcharts, or any other visual elements
     to save effort — update them so they stay true (R9).
   - Match the doc's altitude: high-level docs get key decisions and minimal pseudo-code so
     readers know what to look for in the real code — do not add verbose code to a doc that
     isn't already code-focused.

4. **Refresh frontmatter and index.** Set `stale_after` = today + the doc's category
   `stale_after_days` (from `ai_docs/docsmith/config.json`); update `generated:`
   (`by: <agent/model>`, `at: <ISO-8601 now>`); keep the index table under the H1 in sync
   with the sections.

5. **Validate and score.** Run, per doc:
   - `uv run ai_docs/docsmith/engine/docsmith.py validate --paths '<doc>'`
   - `uv run ai_docs/docsmith/engine/docsmith.py score --doc '<doc>'`
     (evergreen category docs only — decision/plan docs are not scored)

   Iterate until validate reports no errors for the doc and its score meets the freshness
   threshold.

6. **Close the loop.** Mark the processed `[docsmith]` tasks completed.

7. **Extend the docmap.** If this update documented code paths the docmap does not cover,
   add the missing entries under `map` in `ai_docs/docsmith/docmap.json`
   (`[{"path": "<doc>", "reason": "<one line>"}]`).
