---
description: Process pending "[docsmith] update ..." documentation tasks — verify claims against code, rewrite invalidated sections wholesale, refresh frontmatter, validate and score to green.
disable-model-invocation: true
---

> Agents: when `[docsmith] update ...` tasks are pending in the session task list, OFFER this
> command to the user before committing — that is step 3 of the docsmith task-queue protocol.

**Step 0 — resolve paths first. Never assume a single hardcoded location; check all candidates.**
The docsmith engine, the docsmith data directory, and the rules file live in different places in
different repos. For EACH resource below, pick the FIRST candidate that actually exists — confirm
with `ls`, do not guess. The repo's own `.pre-commit-config.yaml` and its `docsmith` Makefile
target are the authoritative record of how docsmith is invoked here; read them (grep for
`docsmith`) whenever a candidate is unclear.

| Resource | Candidate locations, in order (use the first that exists) |
|----------|-----------------------------------------------------------|
| Engine script (`DOCSMITH`) | `${CLAUDE_PLUGIN_ROOT:-$(ls -dt "$HOME/.claude/plugins/cache/claude-assets/docsmith"/*/ 2>/dev/null \| head -1)}/skills/docsmith/scripts/docsmith.py`; then `.docsmith/engine/docsmith.py`; then `ai_docs/docsmith/engine/docsmith.py` |
| Data dir (`DOCSMITH_DIR`: `config.json`, `docmap.json`, `state.json`) | `.docsmith/`; then `ai_docs/docsmith/` |
| Rules file (`RULES`) | `<plugin-root>/skills/docsmith/references/rules.md` (same plugin-root as the engine); then `~/.claude/skills/docsmith/references/rules.md` |

The repo's Makefile already resolves the engine the same way (its `DOCSMITH` variable);
`make docsmith TARGET=validate|score` is the all-docs entry point. For a single doc, call the
resolved `DOCSMITH` script directly with `--paths`/`--doc` (step 5). Use the resolved
`$DOCSMITH`, `$DOCSMITH_DIR`, and `$RULES` in every step below.

Process every pending documentation task in your task tracker tool (not any todo files):

1. **Collect and group.** List the session tasks titled `[docsmith] update <doc path>`.
   Group tasks that touch the same doc: review them together and update that document in
   one go.

2. **Read everything first.** Per doc: read the doc itself, the code paths listed in the
   task bodies, and the doc's entries in `$DOCSMITH_DIR/docmap.json` (an entry's `reason`
   tells you why the mapping exists; a `message` carries custom update instructions that
   take precedence).

3. **Verify, then rewrite wholesale.** Check each of the doc's claims against the code —
   grep the cited `path#Symbol` anchors. Rewrite invalidated sections wholesale, as if
   authored today, per `$RULES`:
   - Never append change-notes, changelogs, or "Update:" paragraphs (R1/R2).
   - NEVER degrade or drop diagrams, box drawings, flowcharts, or any other visual elements
     to save effort — update them so they stay true (R9).
   - Match the doc's altitude: high-level docs get key decisions and minimal pseudo-code so
     readers know what to look for in the real code — do not add verbose code to a doc that
     isn't already code-focused.

4. **Refresh frontmatter and index.** Set `stale_after` = today + the doc's category
   `stale_after_days` (from `$DOCSMITH_DIR/config.json`); update `generated:`
   (`by: <agent/model>`, `at: <ISO-8601 now>`); keep the index table under the H1 in sync
   with the sections.

5. **Validate and score.** Run, per doc (from the repo root, using the `$DOCSMITH` resolved
   in step 0):
   - `uv run "$DOCSMITH" --project-root . validate --paths '<doc>'`
   - `uv run "$DOCSMITH" --project-root . score --doc '<doc>'`
     (evergreen category docs only — decision/plan docs are not scored)

   Iterate until validate reports no errors for the doc and its score meets the freshness
   threshold.

6. **Close the loop.** Mark the processed `[docsmith]` tasks completed.

7. **Extend the docmap.** If this update documented code paths the docmap does not cover,
   add the missing entries under `map` in `$DOCSMITH_DIR/docmap.json`
   (`[{"path": "<doc>", "reason": "<one line>"}]`).
