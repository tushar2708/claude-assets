# Cloud Tracker: Linear

## Hierarchy

Linear has Issues and parent/sub-issues rather than a distinct Story work type. `roadmap.md` remains the Epic registry.

| Flow concept | Linear representation |
| --- | --- |
| Epic | `roadmap.md` Epic section; optionally a Linear Project for planning |
| Story | Parent Issue |
| Subtask | Child Issue whose parent is the Story Issue |

Create one parent Issue per roadmap Story. Create planned work as child Issues in wave order. Use Linear issue relations for blocking relationships when available, while retaining the exact list in the local tracker.

## Synchronization

Store Linear issue URLs and identifiers in the local detail section. Map local completion to the team's completed workflow state. Keep `⛔` in a non-completed state and add the blocker to the Issue. Discover the workspace's actual status names and available integration operations; do not assume them.
