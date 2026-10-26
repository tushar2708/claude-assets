#!/usr/bin/env python3
"""PostToolUse hook for ExitPlanMode: review the approved plan, then run /flow:make-tasks."""

import json
import sys

INSTRUCTION = """The plan is approved. Do not create tasks yet.

Step 1. Review the plan against the project rules.
- Read every CLAUDE.md and AGENTS.md that applies to this directory.
- Read every file under the project's .claude/rules/ folder.
- List each relevant rule as COMPLIES or VIOLATES, with the plan location.
- For each violation, ask the user with AskUserQuestion if it is intended.
- Fix the plan per the answers. Never proceed on an unapproved violation.

Step 2. Only after the plan complies, invoke the Skill tool with skill flow:make-tasks."""


def main() -> None:
    sys.stdin.read()
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": INSTRUCTION,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
