---
name: plan-it
description: Write an approved plan split into sub-feature waves, stages, and tasks, from session context, a spec file, or both.
disable-model-invocation: true
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

Write a plan in the wave model, ready for `make-tasks` (`/flow:make-tasks` in Claude Code).

Read `references/wave-model.md` first. It defines every term and schema.

## Procedure

1. Create a plan artifact and write at its top: "Re-read `references/wave-model.md` before steps 8 and 11, and `references/plan-validation.md` before step 11."
2. Read the sources: session context, a spec file, or both.
2a. **Check the open items.** For each spec file among the sources, read its `status` and its `Open Questions` section. If the status is not `ready` and any row is `Open`, remind the user in the chat: name the spec and list each open item. Then ask through the host's question tool: "Resolve them first (Recommended)" and "Continue anyway". On the first, stop, and tell the user to run `/flow:grill` on the spec's layout or feature. On the second, go on, and list the open items at the top of the plan artifact. This is a reminder, not a gate. Never refuse to continue.
3. Set the sub-features. With a spec, keep its order. Split a sub-feature into `SF-<n>a`/`SF-<n>b` when it does not fit one wave. Never merge. Never reorder. Without a spec, derive the sub-features from the session context.
4. Invoke each skill the user named.
5. Scan each invoked skill for other skills it requires. Invoke those too. Repeat until no new skill appears. Skip none.
6. Translate every rule that asks for one wave per TDD phase into stages S1/S2/S3 of the sub-feature wave. This plan's tasks satisfy any rule that defers task creation.
7. Write the compliance ledger: each MUST rule of each invoked skill → where it is satisfied, or N/A with a reason.
8. Write the waves, stages, and tasks per the reference. Apply the ownership rule. Apply the sub-stage split rule. Add each wave's close task per the reference.
9. Set the agent for each task from the agent table.
10. Plan each wave so that it ends compiling, testing green, and passing pre-commit.
11. After the plan is written, run every check of `references/plan-validation.md`. Fix each failure and repeat until all pass.
12. Obtain the user's approval, then call the Skill tool with `make-tasks`.

## Rules

| ID | Rule | Check |
|---|---|---|
| P1 | Never plan a commit step. | No task or step commits. |
| P2 | Invoke every named skill and every skill they require, recursively. Skip none. | Every invoked skill has rows in the compliance ledger. |
| P3 | Every task has every field from the reference. | No task field is missing or empty. |
| P4 | A file belongs to at most one task in a stage. | No file appears in two tasks of one stage. |
| P5 | Set the agent from the agent table only. | Every `Agent` value is a row of the agent table. |
| P6 | Use only stages S1, S2, S3, and sub-stages. | No other stage value. |
| P7 | Every wave has one verify task. | One `W<n>.verify` per wave. |
| P8 | Plan owner reminders, doc tasks, and feedback as post-wave tasks. | Each follows the reference. |
| P9 | Use the reference's ledger columns. | Ledger columns match the reference. |
| P10 | Write each finished step and skill result to the plan file at once. Never hold decisions in context. | The plan file holds every finished part. |
| P11 | Validate the plan with `references/plan-validation.md` only. | Step 11 ran every check of that file and all pass. |
| P12 | Every wave with a Subtask key has one close task. | One `W<n>.close` per such wave, after `W<n>.verify`. |
