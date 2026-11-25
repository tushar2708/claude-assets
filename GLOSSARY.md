# Flow execution reporting

_Type_: supporting

How a running Flow execution is described to the developer: the plan's waves, their tasks, and the departures from the plan.

## Language

**Wave**:
One sub-feature of the plan, built through its stage tasks, then verified, then closed.

**Built**:
A wave whose stage tasks are all complete. It says nothing about whether the verify task passed.
_Avoid_: implemented, done

**Verified**:
A built wave whose verify task passed, or that the developer chose to skip.
_Avoid_: tested, checked

**Closed**:
A verified wave whose tracker Subtask was updated by its close task. A wave without a tracker Subtask cannot be closed.
_Avoid_: finished

**Implemented**:
The final status of a spec, set by the final close task after every wave is done. It is never used for a single wave.

**Plan**:
The one unit a status update covers. A sub-plan or detail plan made along the way is part of the same plan.

**Run log**:
A plain text file in the plan's folder, one per plan, for every tracker. It holds one short line per wave for its outcome and a line for each detour. It is a quick status record, not documentation.

**Status update**:
The reply that tells the developer where an execution stands, in the words of a stakeholder update. It has a fixed order: goal, headline, one line per wave, what is left, detours, follow-ups. It names no task numbers unless asked.

**Headline**:
The first line of a status update: a status word, chosen by a stated rule, and the counts of waves built, verified and closed.

**Status word**:
One of five words in the headline, chosen by a stated rule from the tracker states: Not started, On track, Waiting on you, Blocked, Done.

**Mismatch**:
A wave whose tracker state differs from what the code shows, for example a wave marked complete whose planned file is untouched. The update reports the more cautious state and counts the mismatch in the headline.

**Detour**:
A departure from the plan's straight path that execute records in the run log: a block or failure, a choice the developer made, or an outcome that differs from the plan. A wait for the dependencies of a task is not a detour.
