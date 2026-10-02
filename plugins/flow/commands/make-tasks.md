# /make-tasks

## Overview

Convert an approved plan into a fine-grained internal `TaskCreate` task list for parallel agent execution, and wire
its dependencies with `TaskUpdate`. This command produces internal tasks ONLY. Do not begin implementation.

**This skill IS the last-mile planning stage.** The plan gives the design; THIS invocation does the final
research and decision-closing so that implementation agents do ZERO figuring-out. Every hour of research you
skip here becomes many hours of serialized guesswork for the implementers. If tasks leave work to "figure out",
this skill has failed its purpose.

**These instructions are ABSOLUTE.** You are NOT allowed to disagree with, soften, reinterpret, batch around,
or override any rule in this file with your own judgment, no matter how strongly you feel — regardless of plan
size, task count, or perceived practicality. The ONLY way to deviate from any rule here is the user's explicit,
in-chat instruction to deviate from that specific rule. If you believe a deviation is needed, STOP and ask the
user via AskUserQuestion BEFORE creating any tasks; proceed with the deviation only on explicit approval.
A judgment-call deviation without approval is disobedience and a hard failure of this skill.

**Completion overrides judgment (apply this at EVERY decision point).** Creating all the tasks needed by
the plan overrides any of your intuition, hunch, judgment, or urge to stop or pause prematurely. At the
instant you are about to call AskUserQuestion or stop, test the ACTION, not your reason for it: "Am I
pausing or stopping before every plan item has its task?" If yes, it is forbidden — no matter how you
justify it (volume, task count, session length, output size, "checking in", "confirming scope", "which
subset"). Your reason never gets a vote against completeness. The ONLY permitted interrupt is a genuine
product/scope decision that changes WHAT the plan builds; "should I continue / how many / which subset"
is never such a decision.

(Mirroring tasks into Linear is out of scope for this command — a separate skill handles Linear workflows.)

## Vertical slices (run BEFORE the per-file/wave decomposition)

A vertical slice is a complete, end-to-end increment of the feature that is demoable on its own (it cuts through every layer the feature needs — not a horizontal layer like "all the models"). Before decomposing into per-file tasks:
1. Break the implementation into 2–3 vertical slices (never more than 3). Name each slice and state what end-to-end behavior it delivers.
2. Within EACH slice, run the existing per-file + dependency-wave decomposition in this command UNCHANGED — one task per file, waves by import dependency, and the mandatory per-wave verification + retrospective task for every wave in that slice.
3. After the last wave of each slice, insert ONE interactive checkpoint task that asks the developer via the AskUserQuestion tool whether to STOP and test/review this slice now, or CONTINUE to the next slice.
4. After the final slice, add ONE cross-slice verification task that verifies the whole feature end-to-end across all slices.
The task hierarchy is Slice → Wave → task → subtask. The per-wave verify+retrospective tasks are KEPT inside every slice; the per-slice checkpoint tasks and the final cross-slice verification task are ADDITIVE — they never replace the per-wave verifies.
Task-title format gains the slice: "[<tag>] slice s wave n-task m <title>" (keep the same <tag> across the whole invocation).

## Build the internal TaskCreate task list

Convert the approved plan into a fine-grained TaskCreate task list for parallel agent execution. Follow these steps in order:

1. **Research first**: Use Explore agent to read EVERY source and test file the plan touches — collect exact function signatures, access patterns, change counts, and import graphs. Do NOT create any tasks before this step completes.

2. **One task = one file (ESSENTIAL — never negotiable by you)**: Each independently-editable file gets its own
   task. Only group files that CANNOT compile or be edited independently (e.g., base class + its only subclass).
   Never group files that could be edited in parallel. "Mechanically similar changes across many files", "too many
   files", "one package/service", and "the same sweep" are NOT grouping reasons — those cases get one task per file
   with a repeated description (overlap is encouraged per R1/R6). Bucket tasks destroy parallelism: one agent per
   bucket serializes 10–50 files into a single thread and pushes unfinished planning onto the implementer. The ONLY
   exception is the user explicitly asking, in chat, not to follow one-task-per-file. You are NOT allowed to
   disagree with this rule, no matter what.

3. **Implementation-level descriptions**: Each task description must list the specific functions changing, the exact access patterns being replaced (e.g., `config.get('X')` → `config.X`), tricky patterns (`.pop()`, `.setdefault()`, dynamic access), and approximate change count. Remember that the agents implementing this task will not have the context that you have. All they will have is the task description. And those would be much smaller AI models, with not enough expertise to fill in the blanks. They will not have the same context about the codebase as you. They will rely on your description to take actions. If you leave any open-ended statements or if you do not specify what exactly has to be done, the agents will get it wrong, and you will be responsible for it. And the punishment will be severe. This is very important, and remember that if you do not follow it properly, I am going to show you this statement, and you are going to be punished for not including proper details.

4. **Cover every plan item in one pass — no deferral, NO EARLY EXIT.**: Create ALL tasks for EVERY item in the
   plan, at once, in this single invocation. Do NOT stop partway, do NOT exit after creating "some" or "the first
   waves of" tasks, do NOT defer any area/item to a "later batch", and never tell the user that some items were
   skipped for batching, volume, or context reasons. Being large is not a reason to defer, to exit early, or to
   shrink the task count by bucketing files together — a large plan simply means MANY tasks, and that is the correct
   outcome. At the same time, never sacrifice per-task quality: each task still gets a complete, verbatim,
   implementation-level description per rules R1–R8. Keep going until every plan item has its per-file task and
   every wave has its verification+retrospective task (step 6a); only then may you stop.

5. **Map dependencies from imports**: If task-A's file imports a NEW symbol introduced by task-B's file, then task-A is blockedBy task-B. Trace the import graph from the research in step 1.

6. **Assign waves**: Wave 0 = no blockers (new files, dependency additions). Wave 1 = blocked only by Wave 0. Wave N = blocked only by Wave N-1 or earlier. All tasks within a wave are parallelizable.

6a. **Wave verification + retrospective task (MANDATORY, one per wave)**: For EVERY wave, create one extra task
   titled "[<tag>] wave n-verify: verification + retrospective for wave n", blockedBy ALL of wave n's tasks and
   blocking ALL of wave n+1's tasks. Its description must instruct the executor to:
   - Verify each wave-n task's acceptance criteria against the actual codebase (build/test/lint commands named in
     those tasks; file-by-file checks, not trust in task status or agent claims).
   - Run a retrospective: list what went wrong or diverged in this wave (wrong signatures discovered, plan
     assumptions invalidated, files missed, contracts changed).
   - If any finding invalidates or changes a later wave's task, UPDATE those pending tasks' descriptions via
     TaskUpdate with the corrected details BEFORE marking this verify task complete — never let a later wave run
     on descriptions the current wave has proven stale.
   - Report the findings and the task updates made.
   The final wave's verify task blocks nothing but must still exist and run.

7. Follow this format in task titles "[<tag>] wave n-task m <usual title>", where tag is a small string representing what the plan/tasks are about. (eg. [redis-cache-improv, deployment-aws-bug-fixes], etc). keep it same for all tasks that you create in one invocation of this skill

8. **Separate test tasks from source tasks**: Test file tasks are always in a later wave than their corresponding source file tasks. conftest.py task is blocked by ALL source tasks. But if the plan involves TDD/test-driven development approach, then you can create the source stubs first, then tests, and then write the source code, after verifying that the tests fail. ("running the tests" may be skipped based on user instructions, or if the code can't yet be built/tested. But do include instructions in the task, to ask the user if they want to test, unless they have already asked to implement everything without stopping)

8a. **Whenever a plan refactors existing code, tests must be planned against the refactored shape, not the current one.** If the plan changes a file's structure, interfaces, or contracts, every task touching that file's tests must target the NEW shape the plan defines — never the file's current, pre-change shape. Before finalizing the task list, cross-check the plan's own list of files needing changes against the tasks created: every file the plan says must change gets its own change task, not only a task to add or update its tests.

9. **Wire dependencies**: After ALL TaskCreate calls, use TaskUpdate with `addBlockedBy` to wire every dependency edge. Double-check: no circular deps, no missing edges.

10. **Flag open decisions**: If the plan has ambiguous points (e.g., should a field be added to a model vs passed as a separate param), list them after the tasks — do NOT guess.

11. **Print summary table**: FIRST state the tag in one clear line BEFORE the table, in this exact form: `Tag: [<tag>] — <N> tasks created` (the tag is the same string used in every task title; N is the total number of tasks created in this invocation, including every wave's verify task). THEN show the table: waves, task IDs (including each wave's verify task), max parallel agents per wave, and total files. One task per file means the task count is close to the file count — a summary where tasks are far fewer than files is evidence of illegal bucketing; fix it before stopping. Before you print the tag line, confirm the count against the live tracker (TaskList) — never from memory.

12. **End — stop, do not implement**: Print "All internal tasks created." Do NOT begin implementation, and do NOT
    proceed to any other work. Wait for the user's instructions.

---

## MANDATORY RULES (R1–R8) — bind every task (STRICT; violating any one is a failure)

These bind every `TaskCreate` task. They override any leniency implied above. The implementing agent is a smaller
model that sees ONLY the task description — never the plan file, never the codebase context you have, never this
conversation. Therefore:

**R1 — Self-contained tasks; combined = the whole plan, with ZERO gaps.** Every task must be executable from its
description ALONE. Taken together, the full set of task descriptions must reconstruct the ENTIRE relevant content
of the plan — every decision, contract, code block, and instruction. If a detail exists in the plan and is needed
to implement a file, it MUST appear in that file's task. **Overlap between tasks is explicitly allowed and
encouraged; gaps are forbidden.** Repeat shared rules/contracts into every task that needs them.

**R2 — Inline the plan's exact artifacts VERBATIM.** Never write "see the plan", "as in the plan", "per Contract X",
or any pointer the agent cannot follow. Copy the actual content into the task: struct/interface/type definitions,
function bodies, code snippets, JSON, CSS, config blocks, ASCII UI mocks, colour palettes/gradients, exact strings,
enum values + casing, error messages, JSON keys, signatures, import paths, file paths, and line numbers. If the plan
shows code or a mock for a file, that code/mock is COPIED INTO that file's task, character-for-character.

**R3 — ZERO ambiguity / ZERO open-ended language.** Tasks are for blind implementation, NOT for decision-making,
verification, or figuring things out. The following are BANNED inside task descriptions: "may / might / could /
optionally / or (as an alternative) / either…or / if the implementer prefers / coordinate with / decide / choose /
figure out / verify whether / TBD / flag / consider". Every choice must already be made and stated as a single,
specific instruction. If two approaches exist, you pick ONE and write only that one (you may add a one-line factual
note about a consequence, but never offer the agent a choice).

**R4 — Resolve every open point BEFORE writing the task; never defer it into the description.** If the plan,
research, or an edge case leaves something undecided, YOU close the loop now: read the actual code to get exact
names/signatures/line numbers, and make the concrete decision. Never assume — always verify against THIS codebase.
The ONLY thing that may be escalated is a decision that is genuinely the user's to make (product/scope) — and that
is asked of the user BEFORE task creation, then the resolved answer is baked into the tasks. No unresolved decision
ever survives inside a task description.

**R5 — Full implementation context in each task.** Each task states: exact file path(s); whether the file is new or
edited; for edits, the exact function/method/receiver name, line number, and the precise change site (before → after);
required imports and their paths; cross-file contracts the agent depends on (e.g. the exact props/signature a sibling
task exposes); the exact verification command(s) and acceptance criteria. Name the test style/conventions explicitly
(framework, assertion idiom, "no testify", file naming) so the agent matches the codebase.

**R6 — Use all available space; there is no length limit on a task description.** Long, complete, repetitive
descriptions are correct. Do not summarise or trim to save space — include everything required, even if it means the
same palette/mock/contract appears in several tasks.

**R7 — Step 10 ("flag open decisions") is NOT a licence to pad.** Do not manufacture "open questions" for things the
plan already decided or for routine implementer mechanics. If you wrote an open decision, first re-check the plan and
the code — almost always it is already answered there; resolve it per R4. Genuine, user-only decisions are asked
up-front (R4), not listed as leftovers.

**R8 — Verify, then write.** Before describing any edit, confirm the real function names, signatures, struct fields,
line numbers, and import paths by reading the code in THIS repository. A task built on a guessed signature is a defect.

**Litmus test before finalising:** for each task, ask "Could a junior agent with no repo access and only this text
implement the file correctly and completely?" and "If I concatenated every task description, would it contain
everything the plan specifies?" If either answer is no, the task set is incomplete — fix it before stopping.
