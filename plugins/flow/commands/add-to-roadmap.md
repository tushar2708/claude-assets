---
description: Add a roadmap.md item under an epic and create it in the tracker. /flow:spec invokes it.
---

Find the item to track in `roadmap.md` (repo root) from the current conversation.
If the conversation names no item, ask the user to describe it.

> This command is the SOLE issue creator in flow. It creates items in the declared tracker.

## Step 0: Resolve the Issue Tracker
Read `${CLAUDE_PLUGIN_ROOT}/skills/sync-issues/references/issue-tracker.md` first.
Run its part C on every run, before any other step.
Write no row until the tracker resolves or the user chose skip.

## Mode: Invoked from /flow:spec
Inputs: spec path, spec title, epic choice, and the SF list.
1. Run Step 0. The spec gives the inputs. Ask only unclear Impact or Effort.
2. Use the passed epic choice. Do not ask again. Resolve it per part D.
3. Create one Story under the epic. Title: the spec title.
   Set its status to `Spec Created` (part E).
4. Story description: the spec path and one line from the spec's Solution.
5. Create one Subtask per `SF-<n>` under the Story. Title: `SF-<n> <name>`.
6. Subtask description: its Behavior and Done-when, from the spec.
7. Write the keys into the spec with `flow:docsmith-doc-author`. Re-run `validate` unscoped.
8. Story key: the `Tracker Story` line. Subtask key: that SF's `Tracker key`.
9. Write ONE roadmap row, for the Story only (Step 3).
10. Never create a Task for a sub-feature. Only a Subtask can be a Story's child.

## Inputs

| Field | Value | If not given |
|---|---|---|
| Type | Story, Task, or Bug | Ask. |
| Epic | Existing key or URL, or `new` | Ask per part D. |
| New epic name | Short name | Ask. |
| New epic purpose | One line | Ask. |
| Title | Under 10 words | Infer from the conversation. |
| Short description | One sentence, under 15 words | Infer from the conversation. |
| Full description | All details | Infer from the conversation. |
| Area | File path or component | Infer. Ask if unclear. |
| Impact | High, Medium, or Low | Infer. Ask if unclear. |
| Effort | High, Medium, or Low | Infer. Ask if unclear. |

## Step 1: Collect Inputs
1. Take every value given in the invocation or the user's request.
2. A given value always wins. Never ask for a given field.
3. Infer the remaining fields from the conversation.
4. Ask only missing or unclear fields, with AskUserQuestion.
5. Ask them together, in as few calls as possible.

## Step 2: Create the Item
1. Create the item first, with Create (part F) and the fields of part E.
   Put all details in the item body, in this order:
   - `**Date**: <today's date>.`
   - `**Area**: <file path or component>.`
   - The full description.
   - `**Impact**: <High|Medium|Low>.` and `**Effort**: <High|Medium|Low>.`
   - Optional `**Details**:` or `**Fix approach**:` text.
2. Link it to the epic with Set parent (part G). In Jira, `parent` goes in Create.
3. Create a GitHub issue only when the user explicitly asks in this run.
4. On skip in Step 0, create nothing. A new epic then needs the tracker; use an existing epic.

## Step 3: Write the Row
1. Insert the row at the top of the epic section's table (part D).
2. Row: `#` = the item key, then Title, Description, Status, and the tracker column (part E).
3. On skip: `#` = `TBD` and an empty tracker column. `/flow:sync-issues` fills both later.
4. Set Status to `Open`.
5. Keep the row brief. Details go in the tracker item.
   - Title: bold, under 10 words.
   - Description: one sentence, under 15 words. Problem or goal only.
   - No dates, paths, links, Impact, or Effort in the row.
6. Never add a row to `## Issue Tracking` (part B).

## Impact Guidelines
- **High**: Causes bugs, blocks features, security risk
- **Medium**: Affects maintainability, has workarounds
- **Low**: Cosmetic, minor inconvenience

## Effort Guidelines
- **High**: >1 day of work
- **Medium**: 2-8 hours
- **Low**: <2 hours
