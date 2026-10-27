---
description: Process pending "[docsmith] update ..." documentation tasks — verify claims against code, rewrite invalidated sections wholesale, refresh frontmatter, validate and score to green.
disable-model-invocation: true
---

> **MANDATORY: writer agent.** Every documentation file this command writes is written by the `flow:docsmith-doc-author` subagent (Task tool, `subagent_type: flow:docsmith-doc-author`). NEVER use `general-purpose`, an unnamed agent type, or any other agent to write files, and never write the doc yourself in the main thread. If the agent is unavailable, STOP and ask the user (AskUserQuestion); do not fall back. After the agent hands back, YOU re-run `validate` unscoped and quote its output; never accept an agent's "green" claim you have not reproduced.

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
| Engine script (`DOCSMITH`) | `${CLAUDE_PLUGIN_ROOT:-$(ls -dt "$HOME/.claude/plugins/cache/claude-assets/flow"/*/ 2>/dev/null \| head -1)}/skills/docs/scripts/docsmith.py`; then `.docsmith/engine/docsmith.py`; then `ai_docs/docsmith/engine/docsmith.py` |
| Data dir (`DOCSMITH_DIR`: `config.json`, `docmap.json`, `state.json`) | `.docsmith/`; then `ai_docs/docsmith/` |
| Rules file (`RULES`) | `${CLAUDE_PLUGIN_ROOT}/skills/docs/references/rules.md` (same plugin-root as the engine); then `<plugin-root>/skills/docs/references/rules.md` |

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

3. **Verify claims (main thread), then dispatch the rewrite.** The main thread checks each
   of the doc's claims against the code — grep the cited `path#Symbol` anchors — and gathers
   the inputs for the rewrite. It does NOT rewrite the doc itself: the wholesale rewrite is
   done by one `flow:docsmith-doc-author` dispatch per doc (Task tool, `subagent_type:
   flow:docsmith-doc-author`). Dispatch independent docs in parallel; tasks touching the same
   doc are grouped into one dispatch. Give each dispatch: the doc path, the category, the code
   paths and docmap entries to check, and the update instructions. The agent rewrites
   invalidated sections wholesale, as if authored today, per `$RULES`:
   - Never append change-notes, changelogs, or "Update:" paragraphs (R1/R2).
   - NEVER degrade or drop diagrams, box drawings, flowcharts, or any other visual elements
     to save effort — update them so they stay true (R9).
   - Match the doc's altitude: high-level docs get key decisions and minimal pseudo-code so
     readers know what to look for in the real code — do not add verbose code to a doc that
     isn't already code-focused.
   - Brevity (give the agent these lines verbatim):
     - Use the minimum words. Add no filler, recap, or restated context.
     - Keep every sentence under 15 words. Table cells count.
     - A small update adds at most 3 lines. Put a larger one in a table.

4. **Refresh frontmatter and index (in the same dispatch).** The `flow:docsmith-doc-author`
   dispatch also sets `stale_after` = today + the doc's category `stale_after_days` (from
   `$DOCSMITH_DIR/config.json`); updates `generated:` (`by: <agent/model>`,
   `at: <ISO-8601 now>`); and keeps the index table under the H1 in sync with the sections.

5. **Validate and score.** Run, per doc (from the repo root, using the `$DOCSMITH` resolved
   in step 0):
   - `uv run "$DOCSMITH" --project-root . validate --paths '<doc>'`
   - `uv run "$DOCSMITH" --project-root . score --doc '<doc>'`
     (evergreen category docs only — decision/plan docs are not scored)

   Iterate until validate reports no errors for the doc and its score meets the freshness
   threshold.

   Then count the words of every changed sentence and table cell.
   15 or more: send it back to the agent.

   Then, after all docs are processed, the main thread runs a final unscoped validate from the
   repo root — `uv run "$DOCSMITH" --project-root . validate` — which must print `FAILURES: 0`;
   quote its output.

6. **Close the loop.** Mark the processed `[docsmith]` tasks completed.

7. **Extend the docmap.** If this update documented code paths the docmap does not cover,
   add the missing entries under `map` in `$DOCSMITH_DIR/docmap.json`
   (`[{"path": "<doc>", "reason": "<one line>"}]`).
