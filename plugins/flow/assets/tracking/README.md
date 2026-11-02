# Flow Tracker Model

`roadmap.md` is always maintained. It is the canonical Epic registry: every `## Epic:` section is one Epic, and every row in that Epic table is one Story.

Select exactly one local tracker and zero or more cloud trackers. Every tracker represents the same Epic → Story → Subtask graph and must keep identifiers, titles, parent links, dependencies, and status synchronized.

| Scope | Choices | Required file |
| --- | --- | --- |
| Local | Claude Code native tasks | `local/claude-tasks.md` |
| Local | File tracker for Codex or another host | `local/todo-file.md` |
| Cloud | Jira | `cloud/jira.md` |
| Cloud | GitHub | `cloud/github.md` |
| Cloud | Asana | `cloud/asana.md` |
| Cloud | Linear | `cloud/linear.md` |

Declare cloud trackers in `roadmap.md` with one row per tracker. Do not infer a tracker from tool availability.

```markdown
## Task Tracking

| Scope | Tool | Location | Integration |
| --- | --- | --- | --- |
| local | todo-file | docs/tasks/ | filesystem |
| cloud | jira | site=<host>; project=<key> | <MCP server> |
| cloud | github | repo=<owner>/<repo> | github or gh |
```

Before creating or changing work, read the selected local file and every declared cloud file. A cloud tracker is optional; the local tracker is not.

## Synchronization contract

1. Create or link the Epic, Story, and Subtask equivalents in every selected tracker.
2. Start an item locally and in all clouds together.
3. Complete it locally and in all clouds only after its self-check and review pass.
4. On any cloud failure, mark the local item `⛔`, record the failure in its details, and stop dependent work.
5. `roadmap.md` remains the cross-tracker Epic and Story index even when a cloud system has its own Epic or Project.
