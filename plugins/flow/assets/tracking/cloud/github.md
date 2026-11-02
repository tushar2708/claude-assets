# Cloud Tracker: GitHub

## Hierarchy

`roadmap.md` remains the Epic registry. In GitHub, create one parent Issue per roadmap Story and create every planned work item as its sub-issue.

| Flow concept | GitHub representation |
| --- | --- |
| Epic | `roadmap.md` Epic section, optionally linked to a GitHub Project |
| Story | Parent Issue |
| Subtask | Child Issue / sub-issue of the Story |

GitHub supports nested sub-issues, but Flow keeps the Epic in `roadmap.md` so the mapping stays compatible with every cloud tracker. Add dependency relations when supported; always retain the dependency list in the local tracker.

## Synchronization

Record each Issue URL in the local detail section. Move Issue state with the local status: `⏳` and `🔄` are open, `✅` is closed, and `⛔` stays open with a blocking comment. Use the configured GitHub MCP or `gh`; discover available operations before use.
