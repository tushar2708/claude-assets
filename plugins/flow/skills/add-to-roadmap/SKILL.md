---
name: add-to-roadmap
description: Add one roadmap.md item under an epic and create its matching tracker item. Use only when explicitly invoked.
disable-model-invocation: true
---

# Add to Roadmap

Use the request and current conversation as input. Never create a subtask unless invoked by `spec` with a specification.

## Host adapters

- **Claude Code:** use `AskUserQuestion` for missing fields and its configured tracker integration for tracker operations.
- **Codex:** use `request_user_input` for missing fields and a connected tracker tool or `gh` only when that tracker is configured.
- **Other hosts:** ask concise plain-text questions. If no configured tracker operation exists, stop before creating anything and tell the user what integration is needed.

## Procedure

1. Read `../sync-issues/references/issue-tracker.md`; run its tracker-resolution part before every other step. On skip, create nothing.
2. Find the requested item in root `roadmap.md`. If absent from the conversation, ask for it.
3. Collect type, epic, new-epic name/purpose when relevant, title, short and full descriptions, area, impact, and effort. Given values win; infer the rest; ask only missing or unclear fields together.
4. Resolve the epic per the reference. Create the tracker item first using its create and parent operations. Its body contains date, area, full description, impact, effort, and optional details or fix approach. Create no subtask here; place proposed subtasks in the body. Create a GitHub issue only when explicitly requested.
5. Insert one concise `Open` row at the top of the epic table: item key, bold title under ten words, description under fifteen words, status, and tracker column. Never add rows to `## Issue Tracking`.

## Invocations from `spec`

When `spec` supplies a spec path, title, epic choice, and SF list:

1. Use its epic selection; ask only unclear impact or effort.
2. Create one Story with status `Spec Created`; its body includes the spec path and one Solution line.
3. Create one Subtask per `SF-<n>` with its Behavior and Done-when.
4. Write the returned story and subtask keys into the spec through the documentation-author workflow, then run unscoped validation.
5. Add exactly one roadmap row for the Story. Never create a Task as a Story child.

Impact: High blocks features, causes bugs, or risks security; Medium affects maintainability with workarounds; Low is cosmetic. Effort: High exceeds one day; Medium is two to eight hours; Low is under two hours.
