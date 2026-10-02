---
description: Run docsmith validate and mechanically fix every finding using the known autofix patterns — no re-analysis, no per-finding explanation.
disable-model-invocation: true
---

Resolve every `validate` error and warning in this project by applying
`${CLAUDE_SKILL_DIR}/references/autofix-patterns.md` directly. That reference is the
authority on HOW to fix each finding shape — read it once at the start of this command, then
apply its fixes without re-deriving them or narrating the fix for each individual finding.

1. **Run the baseline.**
   `uv run .docsmith/engine/docsmith.py validate --json > /tmp/docsmith-findings.json`
   Group findings by check (`frontmatter`, `links`, `drift`, `docmap`, `coverage`, `plan-ttl`,
   `decisions`).

2. **Fix in this order** (later checks can depend on earlier ones landing first — e.g. a
   file that needs both frontmatter added and a citation fixed should get frontmatter first
   so category resolution is correct for any category-dependent fix):
   - `frontmatter` → [Missing frontmatter](references/autofix-patterns.md#missing-frontmatter)
     and [Missing index table](references/autofix-patterns.md#missing-index-table).
   - `decisions` → [Decision non-compliance](references/autofix-patterns.md#decision-non-compliance).
   - `drift` → classify each finding as
     [a real stale citation](references/autofix-patterns.md#drift-real-stale-citation) or
     [a false positive](references/autofix-patterns.md#drift-false-positive) before fixing —
     never apply the false-positive fix to a citation that's actually just stale.
   - `links` → resolve the target's real current path (a prior step in this same run may have
     moved it); fix the relative link.
   - `coverage` → [Coverage: dead glob](references/autofix-patterns.md#coverage-dead-glob).
   - `docmap` → fix `.docsmith/docmap.json` keys/entries per the error message.
   - `plan-ttl` → move the doc to its category's `archive_dir` or set `status: superseded`,
     per the plan category's lifecycle rules in `SKILL.md`.

3. **If any fix requires relocating a file** (a category doc physically outside its category's
   `dir_patterns`, being brought into the right directory rather than just tagged with an
   explicit `type:`), use `git mv`, never Read+Write, and fix every internal relative link in
   every file you touch — both the moved file's own links and any other doc's links pointing
   at it. See [Concurrent-edit duplication](references/autofix-patterns.md#concurrent-edit-duplication)
   if this command's fixes run alongside other agents touching the same tree.

4. **Re-run validate after each batch of fixes for the checks you touched**, not just once at
   the end — a fix for one finding can introduce or reveal another (a rewritten citation that's
   itself stale, a newly-added frontmatter block that fails a field rule). Iterate until:
   `uv run .docsmith/engine/docsmith.py validate` reports `FAILURES: 0 / WARNINGS: 0`.

5. **STOP and ask** (via AskUserQuestion, not a guess) only for the cases the reference
   explicitly calls out as needing input: a citation with no verifiable current equivalent
   after actually searching, a category choice that depends on reading content you're unsure
   how to classify, or an ADR renumbering decision with no established convention in the repo
   to follow. Every other finding in the closed set the reference covers gets fixed directly.

6. **Report a summary, not a running commentary**: counts of findings fixed per check, any
   `<!-- TODO(docsmith): could not verify -->` markers left behind, and the final validate
   exit status. Do not explain each individual fix unless the user asks.

#$ARGUMENTS
