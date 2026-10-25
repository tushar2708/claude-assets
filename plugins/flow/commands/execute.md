---
description: Run the tracker's tasks wave → stage → task with each task's planned agent; verify each wave after asking the user.
---

# /execute

Run the tracker's tasks wave → stage → task. Make no design decision.

Read `${CLAUDE_PLUGIN_ROOT}/skills/plan-it/references/wave-model.md` first.

> **MANDATORY: writer agent.** Spawn only the agent in the task's Agent field. Documentation tasks name `flow:docsmith-doc-author`. Never delegate to `general-purpose` or any generic or unnamed agent. If the named agent is unavailable, stop and ask the user (AskUserQuestion). Never fall back.

## Procedure

1. For each wave in order, for each stage in order:
   1. TaskGet every task in the stage.
   2. Mark them in_progress.
   3. Spawn one agent per task, in parallel, of the type in its Agent field. The main thread does a `main-thread` task.
   4. Each agent makes the changes, runs its Self-check, and returns the evidence.
   5. Read every changed file. Check it against the task. Fix gaps.
   6. Mark the stage's tasks completed.
2. Run the wave's verify task exactly as the reference's verify procedure says. Extra gate commands come from the plan (example: the project's coverage target).
3. Start the next wave.

## Subagent prompt

Add these lines to every subagent prompt:

1. Make only the task's changes. Obey every hook.
2. Run only the task's Self-check command. Run no other command.
3. Use Write only for new files. Use Edit for existing files.
4. Never edit files with scripts or shell commands.
5. Review your work against the task before you report. Report honestly.
6. Never create or use a worktree.
7. Never create or run migrations.
8. Never commit.

## Rules

| ID | Rule | Check |
|---|---|---|
| E1 | Only one stage in progress at a time. | in_progress tasks belong to one stage |
| E2 | Assign each file to one agent per stage. | No file appears in two agent prompts of one stage |
| E3 | Never choose an agent. | Spawned type equals the Agent field |
| E4 | Read every changed file and check it against its task before marking the task completed. Agents can lie. Verify every claim. | Each completed task has a file read after its agent returned |
| E5 | Never commit. Never offer or suggest a commit. Commit only when the user asks. | No `git add`, no `git commit`, no commit offer |
| E6 | The verify question is the only planned stop. | No other planned AskUserQuestion |
| E7 | After the last wave, review all waves against the plan once. Fix every gap. | Review done before the final report |
| E8 | Follow each task's title and description exactly. Never paraphrase. | Agent prompt carries the task text verbatim |
| E9 | Add the subagent prompt lines to every subagent prompt. | Each prompt contains all eight lines |
| E10 | Never spawn agents in Plan Mode. Spawn only after the plan is approved and Plan Mode is exited. | No spawn while in Plan Mode |
| E11 | Never launch an agent with `isolation: "worktree"`. | No worktree parameter |
| E12 | After a model change, ask the user to run migrations. | No migration command run |
| E13 | The main thread runs every check except Self-check. | No other command in agent evidence |
| E14 | The main thread edits code only for `main-thread` tasks and to fix agent gaps. | Main-thread edits map to one of the two cases |
| E15 | Never create a duplicate task. | No two tracker tasks share a title |

Follow any other instructions the user gives here:

#$ARGUMENTS
