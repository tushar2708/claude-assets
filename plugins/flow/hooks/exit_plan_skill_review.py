#!/usr/bin/env python3
"""PreToolUse hook for ExitPlanMode: verify the plan complies with the skills used to build it.

A plan built with a planning skill stamps itself with a `Planned-with-skill:` line (the skill's
own convention). When such a plan is finalized without a `Skill-compliance: verified` marker, this
hook adds a non-blocking reminder asking the agent to re-invoke each stamped skill and verify the
plan against that skill's own rules, gates and checklists. It NEVER blocks plan mode. Once the
marker is present (or the plan has no skill stamp), the hook stays silent, so it can be satisfied
and passed. The existing PostToolUse ExitPlanMode hook runs the project-rules review and
/flow:make-tasks after approval.

Exit 0 with no output = nothing to remind. Otherwise a PreToolUse additionalContext reminder.
"""

import json
import sys

STAMP = "planned-with-skill"
VERIFIED = "skill-compliance: verified"

REMINDER = (
    "Reminder (a strong nudge, not a block): this plan carries a `Planned-with-skill:` stamp but "
    "no `Skill-compliance: verified` marker. Before you finalize it, verify it against the skill(s) "
    "that built it:\n"
    "1. Invoke the Skill tool for EVERY skill on the `Planned-with-skill:` line, in order. (Even if you have invoked it before )\n"
    "2. Walk that skill's rules, gates and checklists against the plan; mark each COMPLIES or "
    "VIOLATES with the exact plan location.\n"
    "3. Fix every violation; for one you believe is intended, ask the user with AskUserQuestion.\n"
    "4. Once you have honestly done this, add a line to the plan: "
    "`Skill-compliance: verified — <skill names>`. That marker silences this reminder.\n"
    "If you have already done this verification, ignore this reminder and proceed."
)


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return  # allow: cannot parse input, do not block the user

    # The plan text lives in the ExitPlanMode tool input; scan the whole input defensively so the
    # exact field name never matters.
    blob = json.dumps(data.get("tool_input", data)).lower()

    if STAMP not in blob:
        return  # allow: no planning skill was used, nothing to verify
    if VERIFIED in blob:
        return  # allow: compliance already verified

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": REMINDER,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
