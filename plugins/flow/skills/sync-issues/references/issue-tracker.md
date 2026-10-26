# Issue Tracker

The one source for tracker resolution and issue operations.

| Caller | When | Parts |
|---|---|---|
| `/flow:add-to-roadmap` | Step 0 | A to G. |
| `/flow:sync-issues` | Step 0 | A to G. |

## A. Read Rule

Read `roadmap.md` from disk on every run.
Never reuse a tracker value from memory, an earlier run, or the conversation.

Use the Read tool on `<repo root>/roadmap.md`, before any other step.

## B. Declaration Format

Put one `## Issue Tracking` section after the H1 title and intro paragraph.
Put it before the first epic section.

Example:

```
## Issue Tracking

| Key | Value |
|-----|-------|
| Tool | jira |
| Location | site=smritea.atlassian.net; project=SMRITEA |
| MCP server | atlassian |

All items are tracked in Jira. Create a GitHub issue only when the user explicitly asks.
```

| Key | Allowed value |
|---|---|
| `Tool` | `github`, `jira`, `asana`, or `other:<name>`. Lowercase. |
| `Location` | `github`: `repo=<owner>/<name>`. `jira`: `site=<host>; project=<KEY>`. `asana`: `workspace=<gid>; project=<gid>`. `other:<name>`: the user's free text. |
| `MCP server` | The `<server>` in `mcp__<server>__<tool>`. Examples: `atlassian`, `claude_ai_Asana`. `github` only: `none` means use `gh`. |

`Tool` not `github`: write the example's last line too, with the tool's name.
Then create a GitHub issue only when the user explicitly asks.
Only then use the `github` columns of parts F and G.

`## Issue Tracking` is not an item section. Never add or read entries in it.

## C. Resolution Algorithm

1. Read `roadmap.md` (part A).
2. Find `## Issue Tracking`. Parse its Key/Value table.
3. Treat the declaration as missing unless all three keys have allowed, non-empty values. Never guess a missing or malformed value.
4. If missing:
   1. Ask the tool with AskUserQuestion: GitHub, Jira, Asana, or Other.
   2. Ask the Location in the part B format.
   3. Ask the MCP server name. For GitHub, offer `none` (use `gh`).
   4. Run step 5.
   5. Write the section into `roadmap.md` with Edit, per part B. Replace a malformed section.
   6. Read `roadmap.md` again. Restart at step 2.
5. Check the connection:

   | Case | Check |
   |---|---|
   | Any named MCP server | Find `mcp__<server>__*` in the tool or deferred-tool list. Load them with ToolSearch. None found: not connected. |
   | `github` | Use the GitHub MCP if connected. Else run `gh auth status`; on success, use `gh`. |
   | `jira`, server `atlassian` | Call `getAccessibleAtlassianResources` once. Pick the cloudId that matches the Location `site`. No match: ask the user. |

6. If not connected:
   1. Tell the user which MCP server to add and to authenticate it with `/mcp`.
   2. Jira Cloud example: `claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp`.
   3. Other tools: name the vendor's MCP server. Never invent a URL.
   4. Ask with AskUserQuestion. Options: "I set it up — check again", "Skip issue work for this run".
   5. On check again, repeat step 5.
   6. On skip, do no issue work. Report the entry as unlinked. `/flow:sync-issues` backfills it later.

Never invent an MCP tool name. Use only names from ToolSearch or the server's discovery tool (for example, Atlassian `discover`).

## D. Epic Sections

Item sections are only `## Epic: <name> — <KEY>` sections.
Read and write entries only there.

```
## Epic: <epic name> — <EPIC-KEY>

<one-line purpose>

| # | Title | Description | Status | Jira |
|---|-------|-------------|--------|------|
| <ID> | **Title** | Description | Status | [<KEY>](https://<site>/browse/<KEY>) <Type> |
```

| Rule | Value |
|---|---|
| Choose the epic | Use the given epic. Else ask: existing epic (key or URL) or new epic. |
| Existing epic | Run Get epic (part G). No section yet: add one. |
| New epic | Run Create epic (part G). Add its section after the last epic section. |
| New row | Insert it at the top of the epic's table. |
| Empty epic | The section holds `No items yet.` Replace it with the table on the first row. |
| Jira labels | None. The type carries the meaning. |
| GitHub or Asana label | The type in lowercase: `story`, `task`, `bug`. |
| Other tools | Ask the label mapping with AskUserQuestion. |

## E. Item Fields and Row

| Field | Rule |
|---|---|
| Type | Story, Task, or Bug. A Subtask is only a Story's child. |
| Title | The entry Title without the surrounding `**`. |
| Body | All details. The roadmap row holds only a short line. |
| Priority (Jira) | From Impact: High, Medium, or Low. A P0 marker means Highest. No source: ask the user. |
| Parent | Story, Task, Bug: the epic. Subtask: its Story. |
| Row `#` | New row: the item key. Old rows keep their IDs (`TD12`, `G3`, `13`). |
| Tracker column | Jira: `[<KEY>](https://<site>/browse/<KEY>) <Type>`. Other tools: `[<id>](<url>) <Type>`. |
| Row shape | One line. No pipe inside a cell. |
| Row brevity | Title under 10 words. Description: one sentence, under 15 words. |
| `roadmap-id:` line | Not needed in new items. Old items keep theirs. |
| `**Issue**:` field | Legacy. Read it; never write it. |
| Extra GitHub issue | Only when the user explicitly asks. Ask the user where to link it. |

## F. Operations per Tool

Run every tracker call in the main context, not a subagent.
Find by marker serves legacy rows only.
It keeps only items with the exact line `roadmap-id: <ID>`. Never fuzzy-match.

| Operation | github (`gh`) | github (MCP) | jira (`atlassian` MCP) | asana (`claude_ai_Asana` MCP) | other |
|---|---|---|---|---|---|
| Create (Story, Task, Bug, Subtask) | `gh issue create --repo <repo> --title <title> --body <body> --label <type>`. Create a missing label first: `gh label create --repo <repo> <type>`. Capture the printed URL. Then run Set parent (part G). | The create-issue tool from ToolSearch. Same semantics as `gh`. | `createJiraIssue`: cloudId, projectKey, issueType = type, summary = title, description = body. Add `priority` and `parent` per part E. Type missing in the project: ask the user. URL = `https://<site>/browse/<issue key>`. | `asana_create_task`: project_id, name = title, notes = body plus a `label: <type>` line. URL = `permalink_url`; if missing, use `asana_get_task`. Then run Set parent (part G). | The create tool from ToolSearch or the discovery tool. |
| Get by key | `gh issue view <n> --repo <repo> --json number,url,labels,state`. | The get-issue tool. | `getJiraIssue`: cloudId, issueIdOrKey = key. | `asana_get_task`: task_id. | The get tool from ToolSearch or the discovery tool. |
| Find by marker | `gh issue list --repo <repo> --state all --search "\"roadmap-id: <ID>\" in:body" --json number,url,body,labels,state`. | The search-issue tool. | `searchJiraIssuesUsingJql`: `project = <KEY> AND description ~ "roadmap-id <ID>"`. | `asana_search_tasks`: workspace and projects_any from Location, text `roadmap-id: <ID>`. Leave `completed` unset. | The search tool from ToolSearch or the discovery tool. |
| Set label | `gh issue edit <n> --repo <repo> --add-label <l> --remove-label <old>`. | The update-issue tool. | Not used (part D). | `asana_update_task` (task_id): rewrite the `label:` line in notes. | Ask the user with AskUserQuestion. Never guess the mapping. |
| Set state (open/closed) | `gh issue close <n> --repo <repo>` or `gh issue reopen <n> --repo <repo>`. | The update-issue tool. | `transitionJiraIssue`. List transitions with `listJiraIssueTransitions` (via `discover` if not loaded). Close: target status category Done. Reopen: target category To Do. Zero or several matches: ask the user. | `asana_update_task` (task_id): `completed` true or false. | Ask the user with AskUserQuestion. Never guess the mapping. |
| List items | Per epic: `gh api --paginate repos/<owner>/<name>/issues/<epic number>/sub_issues`. Legacy: `gh issue list --repo <repo> --state all --search "roadmap-id in:body" --limit 1000 --json number,url,body,labels,state`. | The search-issue tool. | Per epic: `searchJiraIssuesUsingJql` with `parent = <EPIC-KEY>`. Legacy: `project = <KEY> AND description ~ "roadmap-id"`. | `asana_get_tasks`: project from Location, opt_fields `name,notes,parent,completed,permalink_url`. Keep epic children and marked tasks. | The search tool from ToolSearch or the discovery tool. |

Notes:

- `asana_search_tasks` needs a Premium workspace. On failure, ask the user with AskUserQuestion.
- Jira Subtask: check its exact type name with `listJiraProjectIssueTypesMetadata` (via `discover`).
- Some projects name it `Sub-task`. No such type: ask the user.
- The jira and asana tool names came from the session that wrote this file. Name not in ToolSearch: use the discovery tool (part C).

## G. Epics and Subtasks

Every Story, Task, and Bug goes under one epic, the tool's native parent.
A Subtask goes under its Story.

| Rule | Value |
|---|---|
| Epic name | Spec mode: the spec title. Else: the given name, or ask. |
| Purpose line | Spec mode: one Solution line. Else: the given line, or ask. |
| Epic body | Spec mode: the spec path. Else: the purpose line. |
| Epic row | None. The epic gets a section (part D), not a row. |
| Existing epic | Run Get epic on the user's key or URL. Not found: tell the user, ask again. |
| Missing call | Any call below unavailable: ask the user with AskUserQuestion. Never guess. |

| Operation | github (`gh`) | github (MCP) | jira (`atlassian` MCP) | asana (`claude_ai_Asana` MCP) | other |
|---|---|---|---|---|---|
| Create epic | Create a missing label: `gh label create --repo <repo> epic`. Then `gh issue create --repo <repo> --title <epic name> --body <epic body> --label epic`. Capture the URL. | The create-issue tool, label `epic`. | `createJiraIssue`: cloudId, projectKey, issueType `Epic`, summary = epic name, description = epic body. No `Epic` type: ask the user. URL = `https://<site>/browse/<epic key>`. | `asana_create_task`: project_id, name = epic name, notes = epic body. URL as in part F. | Ask the user with AskUserQuestion. Never guess the mapping. |
| Get epic | `gh issue view <n> --repo <repo> --json number,url,labels,state`. No `epic` label: ask the user. | The get-issue tool. | `getJiraIssue`: cloudId, issueIdOrKey = key or URL. Type not `Epic`: ask the user. | `asana_get_task`: task_id = epic GID. | The get tool from ToolSearch or the discovery tool. |
| Set parent (epic or Story) | Get the child's integer `id`, not its number: `gh api repos/<owner>/<name>/issues/<child number> --jq .id`. Then: `gh api --method POST repos/<owner>/<name>/issues/<parent number>/sub_issues -F sub_issue_id=<child id>`. | The sub-issue tool. None: use the `gh` column or ask the user. | Pass `parent` = epic or Story key in `createJiraIssue`. Existing issue: find the call with `discover`. None: ask the user. | `asana_set_parent_for_task`: task_id = child GID, parent = epic or Story GID. | The parent-link tool from ToolSearch or the discovery tool. None: ask the user. |
