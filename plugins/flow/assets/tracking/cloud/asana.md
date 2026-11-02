# Cloud Tracker: Asana

## Hierarchy

| Flow concept | Asana representation |
| --- | --- |
| Epic | Project |
| Story | Task in that Project |
| Subtask | Subtask of the Story task |

Create or select one Asana Project for each `roadmap.md` Epic section. Create one task per roadmap Story, then create planned work as subtasks. Use project sections for Wave ordering when useful, but sections do not replace the Story → Subtask parent relationship.

## Synchronization

Store each Asana permalink in the local detail section. Map `✅` to `completed: true`; map `⏳`, `🔄`, and `⛔` to incomplete, with the current state and blocker in task notes or a comment. Preserve the local dependency list because Asana subtasks express containment, not every Flow dependency.
