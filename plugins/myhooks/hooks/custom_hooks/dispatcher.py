"""
Command categorization and rule dispatching for Claude Code hooks.
"""

import re
import sys
from typing import Any

from custom_hooks.types import Action, Rule


def categorize_command(command: str) -> str:
    """
    Categorize a bash command by its prefix.

    Args:
        command: The bash command string.

    Returns:
        Category string: "git", "go", "npm", "pip", "uv", "python", or "general".
    """
    command_lower = command.strip().lower()

    prefixes = [
        ("git ", "git"),
        ("go ", "go"),
        ("gofmt", "go"),
        ("golangci-lint", "go"),
        ("npm ", "npm"),
        ("pip ", "pip"),
        ("pip3 ", "pip"),
        ("uv ", "uv"),
        ("python ", "python"),
        ("python3 ", "python"),
        ("rm ", "general"),
        ("sed ", "general"),
    ]

    for prefix, category in prefixes:
        if command_lower.startswith(prefix):
            return category

    return "general"


def apply_rules(
    command: str,
    rules: list[Rule],
    input_data: dict[str, Any],
) -> None:
    """
    Check command against rules and exit with appropriate code.

    Args:
        command: The bash command to validate.
        rules: List of rules to check against.
        input_data: Full hook input data (for nudge_once pattern).

    Note:
        This function calls sys.exit() if a rule matches with DENY action.
        For WARN action, it uses the nudge_once pattern (to be implemented).
    """
    for rule in rules:
        if re.search(rule.pattern, command, re.IGNORECASE):
            if rule.action == Action.DENY:
                print(rule.message, file=sys.stderr)
                sys.exit(2)
            elif rule.action == Action.WARN:
                # TODO: Implement nudge_once pattern
                # For now, treat as DENY
                print(rule.message, file=sys.stderr)
                sys.exit(2)

    # No rules matched - allow
    sys.exit(0)