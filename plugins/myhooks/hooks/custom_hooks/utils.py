"""
Utility functions for Claude Code hooks.

Exit codes:
- 0: Allow (workflow continues)
- 1: Non-blocking error (stderr shown to user only, workflow continues)
- 2: Block (action blocked, stderr shown to Claude as error)
"""

import json
import sys
from typing import Any


def load_input() -> dict[str, Any]:
    """
    Load JSON input from stdin.

    Returns:
        Parsed JSON data from Claude Code hook input.

    Raises:
        SystemExit: With code 1 if JSON parsing fails.
    """
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)


def block(message: str) -> None:
    """
    Block the action and show message to Claude.

    Args:
        message: Error message to display.

    Note:
        This function exits with code 2 (blocking error).
    """
    print(message, file=sys.stderr)
    sys.exit(2)


def allow() -> None:
    """
    Allow the action to proceed.

    Note:
        This function exits with code 0.
    """
    sys.exit(0)


def warn(message: str) -> None:
    """
    Show warning to user (non-blocking).

    Args:
        message: Warning message to display.

    Note:
        This function exits with code 1 (non-blocking).
        Message is shown to user but Claude doesn't see it.
    """
    print(message, file=sys.stderr)
    sys.exit(1)


def output(message: str) -> None:
    """
    Output message to stdout (for INJECT pattern).

    Args:
        message: Content to inject into Claude's context.

    Note:
        Use this with exit code 0 to inject content.
    """
    print(message)