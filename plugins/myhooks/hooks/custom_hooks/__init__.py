"""
custom_hooks - Unified Claude Code hook scripts library.

This package provides shared utilities for all Claude Code hooks.
"""

from custom_hooks.types import Action, Rule
from custom_hooks.utils import load_input, block, allow, warn, output
from custom_hooks.dispatcher import categorize_command, apply_rules
from custom_hooks.nudge_once import should_block_with_nudge, NudgeResult
from custom_hooks.registry import (
    HookEntry,
    register_hook,
    get_hook,
    list_hooks,
    enable_hook,
    disable_hook,
    is_hook_enabled,
    unregister_hook,
)

__all__ = [
    # Types
    "Action",
    "Rule",
    "HookEntry",
    # I/O utilities
    "load_input",
    "block",
    "allow",
    "warn",
    "output",
    # Dispatching
    "categorize_command",
    "apply_rules",
    # Nudge pattern
    "should_block_with_nudge",
    "NudgeResult",
    # Registry
    "register_hook",
    "get_hook",
    "list_hooks",
    "enable_hook",
    "disable_hook",
    "is_hook_enabled",
    "unregister_hook",
]