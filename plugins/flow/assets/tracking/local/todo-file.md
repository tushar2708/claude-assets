# Local Tracker: Todo File

Use this tracker in Codex and any host without a native dependency-aware task tracker.

## Location and shape

For `docs/specs/<plan filename without .md>/<plan filename>`, create `docs/tasks/<plan filename>`. Read `roadmap.md`, then create one `## Epic:` section and table in the task file for every Epic that the plan touches.

| Flow concept | Todo-file representation |
| --- | --- |
| Epic | `## Epic: <name> — <key>` section matching `roadmap.md` |
| Story | One row copied from the corresponding roadmap entry |
| Subtask | One `W<n>.T<n>`, verify, close, or final-close row with `Parent Story` |
| Dependency | `Dependencies` table cell plus the detailed section |
| Details | Anchored Markdown section linked by the table |

Start every new Story and Subtask at `⏳`. At work start set `🔄`; after verification set `✅`. Update the table and its linked section in the same edit.

## Blocking syntax

When a task is blocked by another task, use the serial numbers from that Epic table, not task titles or IDs. A task blocked by rows 1 and 4 must show this exact status in the table and linked section:

```markdown
⛔ #blocked by #1, #4
```

Also add `- Blocked by: #1, #4` to its linked section. Do not begin the task until every listed row is `✅`; then change its table and section status back to `⏳`.

For a non-task blocker, retain `⛔ — <reason>` and explain it in the linked section. Examples: a required owner decision, an owner-run verification, or a failed cloud-tracker update.

## Required table

Use this exact leading structure; columns may follow `Details` only when needed:

```markdown
| S. no. | Task | Parent Story | Title | Status | Dependencies | Details |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | W1.T1 | SF-1 | Title | ⏳ | `none` | [W1.T1](#w1-t1) |
```

The linked section copies every planned field verbatim: agent, plan headings, shared contracts, task description, done-when, self-check, dependency rationale, and cloud identifiers.
