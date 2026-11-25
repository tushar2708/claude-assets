---
name: execution-status
description: Report where a Flow execution stands, in the words of a stakeholder update. It says what the plan is for, which waves are built, verified and closed, what has been achieved, what is not done, and any detours, checked against the code and not only against the tracker. Use whenever the developer asks for the status or progress of a plan that execute is running, or asks "where are we", "what is done" or "what is left". Do not answer such a question from memory or from the task you are working on.
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

## Host adapters

- **Claude Code:** read the native tracker with `TaskList`, and use `TaskGet` only for an item whose subject does not tell you its wave. Use `AskUserQuestion` for questions.
- **Codex:** read the file tracker `docs/tasks/<plan filename>`. Use `request_user_input` for questions.
- **Other hosts:** read the file tracker, and ask concise plain-text questions.

# Execution Status

Answer the question "where does this execution stand?" the way you would tell a stakeholder: what the work is for, what has been achieved towards it, what is not done yet, and what went off the straight path. Never read the task list back. A stakeholder does not want to hear about 100 tasks, and a tracker can be stale, so check it against the code.

## Words

| Word | Meaning |
|---|---|
| **Built** | Every stage task of the wave is complete. It says nothing about whether the verify task passed |
| **Verified** | The wave is built, and its verify task passed or the developer chose to skip it |
| **Closed** | The wave is verified, and its close task updated the tracker. Only waves with a tracker Subtask can be closed |
| **Mismatch** | A wave whose tracker state differs from what the code shows |
| **Detour** | A departure from the plan's straight path, recorded in the run log |
| **Run log** | The plain file `run-log.txt` in the plan's folder, written by `execute` |

Never call a wave "implemented": that word is the spec's final status.

## Rules

1. The update is read-only. The one exception is the tracker sync in step 7, and only after the developer says yes.
2. Never run tests or gate commands, never commit, and never start sub-agents. Keep the check cheap: use `git status` and searches, not full reads.
3. Name no task numbers, wave numbers or tracker symbols in the update, unless the developer asks for them.
4. Ask the developer nothing while you work, except the question in step 1 when the plan is unclear, and the question in step 7.

## Procedure

### 1. Find the plan

The plan is the one this conversation is executing: `execute` finds it at `docs/specs/<plan filename without .md>/<plan filename>`, or for a sprint spec at `docs/specs/brainstorm-<NN>-<slug>/<plan filename without .md>/<plan filename>`. The folder that holds the plan file is the plan's folder. A sub-plan or detail plan made along the way is part of the same plan: include its waves.

If the conversation is not executing a plan, look for one in progress. If there is exactly one, use it. Otherwise ask once, through the question tool, which plan to report on.

### 2. Read what you do not already hold

- **The tracker, always, fresh.** Native tracker: `TaskList`. File tracker: the table statuses in `docs/tasks/<plan filename>`, and the reason of each `⛔ — <reason>` row in its linked section. If you cannot read it, say so in step 6 and go on without it.
- **The run log**, if `<plan folder>/run-log.txt` exists. If it does not exist, do the analysis yourself in steps 3 and 4 and say nothing about the missing log.
- **The plan and the goal**, only if you have not already read them in this conversation (after a compaction, you have not). For each wave, take its name, its tasks' `Files` and `Changes`, and its done-when. The goal is the first sentence of the spec's Problem Statement or Solution. A plan with no spec uses the plan's title.

### 3. Check the code

For each wave, collect the planned files (the `Files` of its tasks) and the planned symbols (the names in its `Changes`).

1. Run `git status --short` once.
2. Skip any file you read or wrote in this conversation, as long as no compaction has happened since. Re-read a file when `git status` lists it and you did not touch it yourself.
3. For a planned file that is neither changed nor listed by `git status`, it may already be committed. Search it for the planned symbols instead.
4. Search each planned file for its planned symbols.
5. Give each wave a code result: **found** (all planned files changed or present, all symbols present), **partial** (some, say how many), or **absent** (none).

### 4. Work out each wave's state

Take the tracker state: **not started**, **in progress**, **built**, **verified**, or **closed**, using the words above. A verify task skipped by the developer's choice counts as verified, and the update says it was skipped.

Then compare it with the code result:

| The tracker says | The code shows | Report |
|---|---|---|
| built, verified or closed | partial | in progress, and a mismatch |
| built, verified or closed | absent | not started, and a mismatch |
| not started | found or partial | in progress, unrecorded, and a mismatch |
| anything else | anything consistent | the tracker state |

The more cautious state wins whenever the tracker claims more than the code shows. When the code shows more than the tracker, never raise the wave to built: the self-check and review are not on record.

### 5. Choose the status word

Take the first rule that holds. A dependency wait (`⛔ #blocked by …`, or a pending task with `blockedBy`) is never a stop.

| Word | Rule |
|---|---|
| **Done** | The final close task is complete and there is no mismatch |
| **Blocked** | A stop with a cause other than the developer: a `⛔ — <reason>` for a failed cloud update or a failed check, or a run log detour tagged `blocked`. A log line that ends with `— resolved:` is no longer a stop |
| **Waiting on you** | A stop that needs the developer: a `⛔ — <reason>` for a decision or an owner-run test, a verify or close question not yet answered, or a detour tagged `needs you` that does not end with `— resolved:` |
| **Not started** | Every wave is not started and the code shows nothing |
| **On track** | None of the above |

### 6. Write the update

Use this shape, one block, no tables, no symbols:

```
Goal: <what the plan is for, one sentence>.
Status: <word>. <B> of <N> waves built, <V> verified, <C> closed. <M> differ from the tracker.
<Wave, named by what it delivers>: <state in words>. <what it achieved, one sentence>.
Not started: <wave names>.
Left: <what the developer still does not have, in terms of the goal>.
Detours: <short notes, one clause each> | none.
Ask me for: the detail of a wave, the files that changed, or what was skipped.
```

- Leave out "<M> differ from the tracker" when there is no mismatch.
- Name each wave by what it delivers, from the plan's sub-feature name, never `W2` or `SF-2`.
- Take a wave's achievement from its run log line. With no log line, describe what the code check found in plain words, for example "3 of 4 planned files changed".
- For a mismatch, say it on the wave's line, for example "The tracker says complete, but the importer file is untouched."
- Group the waves not started on one line. Leave out `Not started:` when there are none.
- State what is left as outcomes, from the done-when of the waves not yet built, not as tasks.
- Take detours from the run log, from stops visible in the tracker, and from the developer's choices. Repeat none.
- Aim for about ten lines. Do not pad it, and do not list tasks.

**Not this:** "Tasks 1.1 to 1.4 and 2.1 are complete. 2.2 is in progress."

**This:** "Goal: let users import their contacts. Status: On track. 2 of 3 waves built, 1 verified, none closed. Import service: built and verified. Imports run end to end for the sample file. Duplicate detection: built, not verified. Duplicates are merged by email. Notifications: not started. Left: telling the user when an import finishes. Detours: verify skipped for duplicate detection at your choice."

Edge states:

- **Tracker unreadable:** write `Status: Tracker unreadable.` Report each wave from the run log and the code, and mark each line "unconfirmed".
- **Everything done:** use Done, say what was achieved, and leave out `Left:`.
- **Nothing started:** use Not started, give the goal, and list the planned waves on one line.

### 7. Offer the tracker sync

If there is at least one mismatch, ask once through the question tool, after the update: "The tracker disagrees with the code for <M> waves. Update it to match?" with "Update the tracker (Recommended)" and "Leave it as is". Ask nothing when there is no mismatch.

On yes, update the local tracker as `execute` does for a state change, then every configured cloud tracker through its file under `assets/tracking/cloud/`:

- For a wave the tracker overstates, set the items whose planned files are missing back to `🔄` or `⏳` (native: `in_progress` or `pending`).
- For a wave whose planned work the code shows but the tracker has not started, set its items to `🔄` (native: `in_progress`).
- Never delete an item and never mark one complete.
- Append `plan detour (off plan): tracker synced to the code for <M> waves.` to the run log.
