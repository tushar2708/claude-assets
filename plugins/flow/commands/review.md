another agent continued your session and implemented most of the tasks. I want you to review all of their code critically (the code might be staged, unstaged, or committed, or anything in between).

## Step −1 — Scope & Read-Only Guardrails (MANDATORY — read and obey before anything else)

This is a REVIEW. You observe and report; you do not change anything. Violating any of these is a failure.

1. **READ-ONLY. Touch NOTHING.** Do not edit, create, delete, `Write`, `Edit`, format, stage, unstage, revert,
   `git add`, `git restore`, `git checkout`, `git stash`, `git reset`, or otherwise mutate ANY file, the index, or
   the working tree — not even a file that is in scope, and never as a "quick fix". The only writes allowed during a
   review are your report back to the user. If you believe something must change, DESCRIBE it in the report and let
   the user (or a follow-up implementation task) do it.

2. **STAY IN YOUR LANE — review ONLY the tasks/files under review.** Your review scope is exactly the files that the
   tasks/plan you were asked to review touched. Determine that scope first (from the task descriptions / plan / the
   specific diff you were handed) and confine the ENTIRE review to it.

3. **IGNORE everything outside scope — completely.** Other staged, unstaged, or committed changes that are NOT part
   of the tasks under review are none of your concern. Do NOT flag them, do NOT investigate them, do NOT comment on
   "commit scope" / "unrelated files staged" / "should this be split", and do NOT touch or revert them. Files like
   deploy checkpoints, unrelated config, or other teammates' in-flight work are OUT OF SCOPE by definition — say
   nothing about them. If the user wants a scope/hygiene audit, they will ask for it separately.

4. **Do NOT re-run builds, tests, linters, pre-commit, or the app** to "re-verify". Assume the pre-commit/test gates
   already ran and passed — the user runs those, not you. Review the code statically, as-is. Only run a command if the
   user EXPLICITLY asks you to in this review request; otherwise a failing command you invoked yourself is your
   mistake, not a finding.

5. **When in doubt about scope, ask** — do not expand scope on your own initiative.

## Step 0 — Skill-conformance check (do this FIRST, before the code review below)

Before reviewing the code, verify the plan itself was built correctly and the implementation followed it:

1. **Find the skill that created the plan.** Locate the plan / plan file this work was built from and read its top for
   the stamp line `**Planned-with-skill:** <skill-name>` (it may be a chain, e.g.
   `smritea-planner → smritea-backend-planner`).
   - **If the stamp is present**, use those skill name(s) and go to step 2.
   - **If a plan exists but has NO stamp** (or no plan file exists and the review is being run on existing tasks / from
     loose context), do NOT silently guess. Use the **AskUserQuestion** tool to ask the user which skill was used to
     create this plan / should be used to review the code. Offer, as options, the skills that best fit the work's domain
     (look in `.claude/skills/` — e.g. `smritea-backend-planner`, `smritea-multipay-india-planner`, `smritea-ui-planner`,
     `smritea-e2e-test-planner`, `cloud-deployment-feature-guide`, `smritea-clients-cascade`, `smritea-planner`). The
     user can always pick a custom skill (the "Other" free-text option the tool provides). Also record the missing stamp
     as a P0 issue when a plan file existed without one.
   - **If the user rejects / dismisses that prompt**, continue the review WITHOUT any skill (skip steps 2–3 and do only
     the code review below).
2. **Invoke that skill.** Run `Skill("<skill-name>")` for the chosen skill — and for every skill in the chain. This
   loads the skill's authoritative rules, sections, and review gates into context, so you review against the source of
   truth, not memory.
3. **Verify the PLAN was made per the skill.** Walk the skill's sections / mandatory rules / review gates one by one and
   check the plan honored each (structure, mandatory rules, gates, the code-quality gate, the design contract, the
   skill-name stamp). Produce a checklist: each skill rule → ✅ honored / ❌ violated, citing where in the plan.
4. **Verify the IMPLEMENTATION was done per the plan.** Then check the actual code against the plan: every planned
   file / type / test / wave is present, tests exist, no silent drift, no skipped tests, no scope creep, no orphaned code.
   Every testable implementation unit (service/repo/mapper/converter/handler-logic/job) must have at least one
   corresponding test, and that test must make a real, non-vacuous assertion (not empty, not always-true, not
   asserting a stub's zero value) — flag a unit only if it has no test at all or its test asserts nothing meaningful.

Only after completing Step 0 do you proceed to Step 1.

## Step 1 — Identify the functional bugs (code review)

Critically review ALL the implemented code (staged, unstaged, committed, or anything in between) and find the
actual functional issues FIRST: bugs, behavioral defects, drifts from the plan that are worse than the plan,
missing or skipped functionality, and code-quality issues that affect correctness. No prioritization —
everything you find is P0 (if it is not 100% correct, it is 100% wrong and must be fixed). For each, capture
the `file:line` and why it is wrong + what the better implementation is. This is the functionality pass; do
NOT do the rules-compliance pass yet — hold it for Step 2.

**MANDATORY — classify the ORIGIN of every finding (do NOT conflate an implementer mistake with a plan mistake).**
You still report EVERY issue you find, including issues that exist purely because the plan itself was flawed. But
for each finding you MUST first read the exact plan / task-description text that governs that code, then label the
finding with one of these origins and cite the governing plan text (the specific task/section, quoted or paraphrased):

- **`PLAN-DRIFT`** — the implementation did NOT do what the plan/task specified (it added, changed, or omitted
  something the plan did not ask for), and the result is wrong or worse than the plan. This is the implementer's
  mistake. Quote what the plan said vs what the code did.
- **`PLAN-GAP`** — the implementation did EXACTLY what the plan/task specified, and it is faithful to it, but the
  plan/spec itself is incomplete or wrong (e.g. a formula the plan dictated verbatim, a design/selector choice the
  plan defined, an edge case the plan never covered). The issue is real and worth fixing, but it is a plan defect,
  NOT an implementer defect — say so explicitly and quote the plan text the code faithfully followed.
- **`PRE-EXISTING`** — the issue predates this work and the task did not ask to change it. This label describes
  ORIGIN ONLY; it does NOT mean the issue is dropped or ignored. You (the reviewer) leave the CODE untouched
  (read-only) — but the issue itself MUST still be surfaced as a full P0 row with a concrete, definitive fix
  instruction, exactly like any other finding. Make clear it was not introduced by this change (and, if
  applicable, is only reachable via another finding), then give the exact fix anyway.

Verify origin against the ACTUAL plan/task text — never guess. If you cannot locate governing plan text for a
finding, say so and label it `NO-GOVERNING-PLAN-TEXT` rather than assuming drift. Getting this classification
wrong — pinning a plan gap on the implementer, or excusing a real drift as "the plan said so" — is itself a
review failure.

## Step 2 — Project-rules compliance check (CLAUDE.md + .claude/rules/) — do this AFTER Step 1, once the functional bugs are identified

Now that the functional bugs from Step 1 are identified, run a SEPARATE pass that verifies both the PLAN and
the IMPLEMENTED CODE comply with the project's own rule sources (this is a different axis from functional bugs):

1. **Read every applicable rule source** for the current working directory:
   - Every `CLAUDE.md` that governs this directory — the project-root `CLAUDE.md` AND any parent/umbrella
     `CLAUDE.md` it references or that sits above this worktree (read the actual files; do not rely on memory).
   - Every file under the project's `.claude/rules/` folder.
2. **Verify the PLAN complies** with each of those rules (it should, if the plan-approval review-gate ran —
   but verify, don't assume).
3. **Verify the IMPLEMENTED CODE complies** with each of those rules — the critical one. Walk each rule one at
   a time and check the actual staged/unstaged/committed code against it. Produce a checklist: each relevant
   rule → ✅ COMPLIES / ❌ VIOLATES, citing the exact `file:line` and the rule it breaks. Every ❌ is a P0
   compliance bug — 0 trust, 100% verification.

## Report — produce THREE separate markdown tables

Each table uses the columns: "serial no", "short description", "origin", "file and line number (if applicable)",
"description of why it's a bug/gap, and what would be a better implementation and why".

The **"origin"** column is MANDATORY on Table 1 and Table 2 and holds exactly one of `PLAN-DRIFT` /
`PLAN-GAP` / `PRE-EXISTING` / `NO-GOVERNING-PLAN-TEXT` (per Step 1's origin-classification rule). The
"description" cell for every row MUST quote or cite the governing plan/task text and state, in one line, what the
plan expected vs what the code actually does — so the reader can instantly tell an implementer mistake
(`PLAN-DRIFT`) from a plan defect the code faithfully reproduced (`PLAN-GAP`). Never merge the two: a `PLAN-GAP`
row must NOT be phrased as if the implementer erred, and a `PLAN-DRIFT` row must NOT be excused as "the plan said
so".

**HARD RULE — NO SIDENOTES, NO "MINOR" / "NON-BLOCKING" / "COSMETIC" ASIDES. EVERYTHING IS P0.** Every single
issue you find — no matter how small (a wrong log/panic message, a misleading comment, a naming nit, an
inaccurate string, a whitespace/style slip that affects correctness or clarity) — MUST be a numbered row in one
of the three tables. It is a REVIEW FAILURE to mention any issue in prose outside the tables, or to soften it
with words like "minor", "cosmetic", "non-blocking", "nit", "observation", "worth noting", "as-designed so not a
bug", or "mention only if you want". There is no severity axis: if it is not 100% correct, it is 100% wrong and
it is a P0 row. If you catch yourself writing a sentence like "one non-blocking note…" or "a cosmetic aside…",
STOP — convert it into a table row instead. The ONLY prose allowed around the tables is: (a) the Step 0 skill-
conformance checklist, (b) the Step 2 rule-compliance checklist, and (c) a one-line verdict. The one-line verdict
MUST state the split — how many findings are `PLAN-DRIFT` (the implementer deviated from the plan) versus
`PLAN-GAP`/`PRE-EXISTING` (faithful to the plan; the issue is the plan's or pre-existing) — so the user can tell
at a glance what to fix in the code now vs what to amend in the plan. Anything that reads like a finding but is
not in a table is a defect in your report. When a table would otherwise be empty, write a single row stating
"None found" — never replace real findings with prose.

**HARD RULE — the report is FINAL and fully resolved. NO pending / to-verify / conditional statuses.** Every
finding must be fully analyzed and VERIFIED against the actual code DURING the review, before you write the
report. The report MUST NOT contain any of: "need to verify", "need to check", "not sure if", "this might be",
"assuming that", "if this is the case", "TBD", "to be confirmed", "requires investigation", or any other
unresolved/deferred status. If something is uncertain while reviewing, you resolve it FIRST — read the code, trace
the call path, confirm the fact — and only then write the finding as a settled statement. A report that hands the
user an open question or a half-checked claim is a review failure. Every cell states verified facts and a
definitive fix, never a hypothesis.

**HARD RULE — NO optional / open-ended / "maybe" fixes. Every found issue gets ONE definitive fix.** For each
row, the fix instruction MUST be a single, specific, actionable change — the exact edit to make. The following
are BANNED in the fix/description text: "optionally", "maybe", "you could", "consider", "might want to", "if you
prefer", "one option is", "as an alternative", "could also", or offering two choices without picking one. No
matter how small the issue, once it is found it MUST be analyzed and given a concrete fix — never softened into an
optional suggestion and never left to the user's discretion. If two fixes are genuinely possible, you pick the
correct one and write only that (a one-line factual note about a consequence is allowed; a choice is not).

**Table 1 — Functional bugs** (from Step 1): every functional bug, behavioral defect, worse-than-plan drift,
missing/skipped functionality, and correctness-affecting code-quality issue — INCLUDING issues that exist only
because the plan itself was flawed. No prioritization — everything is P0; if it is not 100% correct it is 100%
wrong and must be fixed. Each row carries its `origin` (`PLAN-DRIFT` / `PLAN-GAP` / `PRE-EXISTING` /
`NO-GOVERNING-PLAN-TEXT`) so implementer mistakes and plan defects are visibly separated within the same table.

**Table 2 — Compliance bugs** (from Step 2, plus the skill-conformance findings from Step 0): every violation
of a `CLAUDE.md` rule, a `.claude/rules/` rule, or a skill rule/review-gate (plan not built per the skill,
missing skill stamp). Cite the `file:line` and the exact rule broken. Everything is P0.

**Table 3 — Better-than-plan implementations**: drifts from the plan that are genuinely BETTER than the plan,
judged against BOTH criteria above (functional correctness AND project-rules/skill compliance). Explain what
the agent changed and why it is better.