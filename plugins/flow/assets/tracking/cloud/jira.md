# Cloud Tracker: Jira

## Hierarchy

| Flow concept | Jira Cloud work item |
| --- | --- |
| Epic | Epic |
| Story | Story, parented to the Epic |
| Subtask | Subtask, parented to the Story |

Create the Epic from the matching `roadmap.md` Epic section. Create one Story for each roadmap row. Create planned `W<n>.T<n>`, verify, close, and final-close items as Story subtasks. Use the configured project and the exact available work-type names; discover them before creation and do not guess a custom scheme.

## Synchronization

Store Jira keys and URLs in the local task-detail section. On every local `🔄`, `✅`, or `⛔` transition, transition the corresponding Jira item to the mapped state. Keep blocked-by relationships in Jira when the available integration supports them; retain the complete dependency list in the local tracker regardless.
