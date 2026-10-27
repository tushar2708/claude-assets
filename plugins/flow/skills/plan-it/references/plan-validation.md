# Plan Validation

The one list of plan checks. Read by `/flow:plan-it` and `/flow:make-tasks`. Terms are defined in `wave-model.md`.

| Caller | When | On a failure |
|---|---|---|
| `/flow:plan-it` | After it writes the plan, before ExitPlanMode. | Fix the plan. Run all checks again. Repeat until all pass. |
| `/flow:make-tasks` | Before it creates any task. | STOP. Tell the user which check failed, with the plan line. Create no task. |

Exception: for `/flow:make-tasks`, a missing close task (V11) is no failure. Its rule M8 adds it.

## Checks

| ID | Check | Fails when |
|---|---|---|
| V1 | The compliance ledger exists with the columns of `wave-model.md`: skill, MUST rule, satisfied in, N/A reason. | The ledger is missing, or a column is missing. |
| V2 | A file belongs to at most one task in a stage. | One file appears in two tasks of one stage. |
| V3 | Every task has every field of `wave-model.md` "Task Fields". Post-wave tasks included. | A field is missing or empty for any task. |
| V4 | Every wave has exactly one verify task `W<n>.verify` with the fields of `wave-model.md` "Verify Task". | A wave has no verify task, or more than one. |
| V5 | Waves are serial. | A wave starts before the previous wave's verify task. |
| V6 | Every stage value is S1, S2, S3, or a sub-stage S<m>a, S<m>b. | Any other stage value. |
| V7 | Every `Agent` value is a row of the `wave-model.md` agent table. | An agent is not in the table. |
| V8 | No task or step commits. | A task or step commits or offers a commit. |
| V9 | Owner reminders, doc tasks, and feedback are post-wave tasks. Feedback is the last task. | One of them is inside a wave, or feedback is not last. |
| V10 | Every plan section that a wave's shared contracts name exists in the plan file. | A named section does not exist. |
| V11 | Each wave with a Subtask key has one `W<n>.close` per "Close Task". | A close task is missing, duplicated, or in a non-last split wave. |

## Procedure

1. List every task of the plan, verify and post-wave tasks included.
2. Run V1 to V11 in order.
3. For each check, record PASS or FAIL with the plan line of each failure.
4. Act on a failure as the caller row says.
