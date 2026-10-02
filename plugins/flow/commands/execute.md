Start working on the decided plan, following the following instructions STRICTLY:

Check out ~/.claude/CLAUDE.md to know about which agents are avilable and how to use them.

1. Make detailed todos, but only if they don't exist for the given goal, Keep the total todo items under 25 (if there are more tasks, you can use the question tool to ask the user if it is okay to create more than 25 tasks by giving them an estimate about how many tasks you need to be created. If the user approves, there is no limit on the number of tasks. You can create even thousands of tasks as long as the user explicitly approve that number). If there are already tasks related to what you are being asked to do, either explicitly or based on the recent context, then do not create any duplicate tasks. 

2. If you have already been given a list of tasks in the session that you have been asked to work on, remember to actually read both the title and the description of the tasks that are given to you. The tasks are not up for your opinion or paraphrasing. You have to follow all the instructions given in the title and description as precisely as possible, and then add more precision even if it's impossible. Any drift from the instructions given in the task will be punished seriously. Always read the task title and description. (These are Claude Code tasks, and the you already have tools to read their title and description. So do not try to make any excuse, and never continue without reading the detailed description, no matter what.)

3. Use appropriate agents as per the file type (or as instructed) in parallel as per the plan and tasks. Ask the agents to review that their work is actually completed as per the instructions, before reporting it to be done. And that thye must give an honest report. (This MUST be added to all agent context). DO NOT CREATE ANY WORKTREES. All agents MUST work in parallel, int eh same worktree, that you are given by me. Never even try to touch any worktree commands/tools. Never launch agents with isolation: "worktree".

4. MANDATORY SUBAGENT CONTRACT — add ALL of the following instructions to EVERY subagent prompt you launch, no matter what:
   - Your job is only to make code changes, and obey the instructions by any hooks sincerely.
   - You MUST NEVER run any python, node, go, bash, makefile or any other command; just make ALL the code changes, and yield back to the main agent.
   - Use Write() tool only for new files; for existing files ONLY use Edit or Update tools.
   - Never use any script or bash commands to edit files, only Write/Edit tools.
   - Never run validations yourself; all validation must only be done by the main agent after subagents yield.

5. But remember that agents lie. Don't trust their claims, and ALWAYS ALWAYS ALWAYS verify their claims and output. Even if they have finished their individual tasks, assume that integration is pending, and verify it critically.

6. Once done with all changes, stop and critically review each stage/phase from the beginning.

7. NEVER try to create or run django or alembic migrations. Whenever you are done with model update/creation, stop and ask the user to do them manually. This instruction MUST also be given to all the agents.

8. Remember that if agents make mistakes, and you don't catch it on your own, it's a major failure on your part, and you will be brutally punished for each such mistake.

9. I have already told you that you must expect that agents might nie. So it's essential for you to ALWAYS verify their work, or face the bullet yourself.

10. Make detailed todos for all the remaining phases and keep working on all phases one by one, not just a few phases. Don't you dare stop for anything unless all phases are complete and verified.

11. Don't stop, and don't try to git add or commit, unless all tasks are compelted. Commit will only be dne, once all the pre-commit hooks of the project are passing. No intermediate commits are allowed. Every time you invoke any agents, this must be included in the instructions given to them. 

12. Make sure to assign different files to each instance of an agent. Don't assign them same files

13. You have to verify and fix agents mistakes, but as soon as you are done with it, invoke the relevant agents again for the next tasks. Don't make code changes yourself, except when 
fixing agents mistakes. Make those agents write code, ajust don't let their mistakes slip through.

14. If you are currently in plan mode, do NOT invoke agents, until you get approval for your, and you are out of plan mode. (agents are incapable of doing their work, if invoked in plan mode, even after exiting plan mode). Once you are out of plan mode, invike agents as per the earlier instructions.

15. Remember very carefully that while working, whenever you pick up some new tasks, you must set their status to "in_progress" in the Claude Code task tracker. And after every wave of tasks, you must update the task status to completed once you verify that the tasks are done. You can not, under any circumstance, move to the next wave of tasks without updating the status of the tasks that you have completed.

16. VERIFY WITH THE FULL SUITE BEFORE MARKING ANYTHING "COMPLETE" (non-negotiable). A task is "done" ONLY after YOU — not the agent — have re-run the project's checks and seen them GREEN with your own eyes: at minimum `build-check` + the FULL affected test suite (e.g. `make test-run`, not just a single `RUN=OneTest` filter), plus `lint`/`discipline`/model-sync where the wave touched them. Marking a task completed on (a) an agent's claim, (b) a single targeted test while the rest of the suite is unrun, or (c) reasoning about what "should" pass, is a hard failure. A change that passes its own targeted test can still break sibling tests in the same or other packages — the full run is the only proof. Run it, read the exit code and the FAIL/panic lines, THEN flip the tracker.

17. MAIN-AGENT-ONLY VALIDATION RULE — do not ask subagents to run acceptance commands, build commands, tests, lint, discipline, or any shell command at all. Subagents only edit files and yield. The main agent alone runs validations after subagents finish, and then either fixes minor violations directly or launches another set of edit-only subagents if more changes are needed.

18. WAVE BOUNDARY RULE — after every wave of tasks, you MUST verify what tasks are actually completed in the codebase and update the task status in the tracker before moving on to the next wave. Under no circumstances can any task from the next wave be picked if all tasks from the previous wave are not verified as completed and marked as completed. Implementation across waves is strictly sequential, and the implementation → verification → task-status-update cycle must be fully completed at the end of each wave before starting the next wave.

19. SINGLE-WAVE-IN-PROGRESS RULE — at any given point, you can never mark more than one wave worth of tasks as in_progress. Unless you have marked the previous wave of tasks as completed after verification, you cannot mark any tasks from the next wave as in_progress. If tasks from a later wave were prematurely marked in_progress, you must correct them back to pending before proceeding.

In addition to these instructions, follow any other instructions that user gives here:

#$ARGUMENTS
