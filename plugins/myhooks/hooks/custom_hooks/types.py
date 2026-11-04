"""
Type definitions for Claude Code hooks.
"""

from enum import Enum
from dataclasses import dataclass


class Action(Enum):
    """Action to take when a rule matches."""

    DENY = "deny"  # Always block (exit 2)
    WARN = "warn"  # Block first time, allow after (nudge_once pattern)
    CHECK = "check"  # Validate post-execution, block on failure


@dataclass
class Rule:
    """A validation rule for hook scripts."""

    id: str  # Unique rule identifier (e.g., "git-checkout")
    pattern: str  # Regex pattern to match
    action: Action  # Action to take on match
    message: str  # Message to display when rule triggers
