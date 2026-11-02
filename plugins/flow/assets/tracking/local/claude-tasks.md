# Local Tracker: Claude Code Tasks

Use Claude Code's native task tracker as the local representation.

| Flow concept | Claude Code representation |
| --- | --- |
| Epic | The matching `roadmap.md` Epic section; do not duplicate it as a local task |
| Story | A parent `TaskCreate` task linked to its roadmap row |
| Subtask | A child work item created in wave, stage, task order |
| Dependency | `TaskUpdate(addBlockedBy)` |
| Status | Native task state through `TaskUpdate` |

Create every Story and Subtask with the exact plan text, contracts, roadmap identifier, and cloud identifiers. Use `TaskList` after creation and after each wave. Mark a native task complete only after the same self-check, review, and cloud-tracker synchronization required by `README.md`.
