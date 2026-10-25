---
name: plan-it
description: Write a Plan Mode plan split into sub-feature waves, stages, and tasks, from session context, a spec file, or both.
disable-model-invocation: true
---

Write a plan in the wave model, ready for `/flow:make-tasks`.

Read `${CLAUDE_SKILL_DIR}/references/wave-model.md` first. It defines every term and schema.

## Procedure

1. Enter Plan Mode.
2. Read the sources: session context, a spec file, or both.
3. Set the sub-features. With a spec, keep its order. Split a sub-feature into `SF-<n>a`/`SF-<n>b` when it does not fit one wave. Never merge. Never reorder. Without a spec, derive the sub-features from the session context.
4. Invoke each skill the user named.
5. Scan each invoked skill for other skills it requires. Invoke those too. Repeat until no new skill appears. Skip none.
6. Translate every rule that asks for one wave per TDD phase into stages S1/S2/S3 of the sub-feature wave.
7. Write the compliance ledger: each MUST rule of each invoked skill → where it is satisfied, or N/A with a reason.
8. Write the waves, stages, and tasks per the reference. Apply the ownership rule. Apply the sub-stage split rule.
9. Set the agent for each task from the agent table.
10. Plan each wave so that it ends compiling, testing green, and passing pre-commit.
11. End with ExitPlanMode.

## Rules

| ID | Rule | Check |
|---|---|---|
| P1 | Never plan a commit step. | No task or step commits. |
| P2 | Invoke every named skill and every skill they require, recursively. Skip none. | Every invoked skill has rows in the compliance ledger. |
| P3 | Every task has every field from the reference. | No task field is missing or empty. |
| P4 | A file belongs to at most one task in a stage. | No file appears in two tasks of one stage. |
| P5 | Set the agent from the agent table only. | Every `Agent` value is a row of the agent table. |
