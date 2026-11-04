"""
Nudge-once utility for WARN pattern.

Implements "block first time, allow after" pattern:
- First time seeing rule+context: BLOCK, show message, record timestamp
- Already warned (within cooldown): ALLOW, no message
- Cooldown expired: BLOCK again, show "Reminder"

State stored in ~/.claude/hook_nudge_state.json
"""

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class NudgeResult:
    """Result of nudge check."""

    should_block: bool
    message: str
    reason: str  # "first_warning", "reminder", "allowed"


STATE_FILE = Path.home() / ".claude" / "hook_nudge_state.json"
DEFAULT_COOLDOWN_MINUTES = 30
CLEANUP_PROBABILITY = 0.1  # 10% chance to run cleanup
MAX_AGE_DAYS = 7


def _load_state() -> dict:
    """Load state from file."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {"warnings": {}}
    return {"warnings": {}}


def _save_state(state: dict) -> None:
    """Save state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _cleanup_old_entries(state: dict) -> dict:
    """Remove entries older than MAX_AGE_DAYS."""
    now = time.time()
    max_age_seconds = MAX_AGE_DAYS * 24 * 60 * 60

    cleaned = {"warnings": {}}
    for key, entry in state.get("warnings", {}).items():
        if now - entry.get("timestamp", 0) < max_age_seconds:
            cleaned["warnings"][key] = entry

    return cleaned


def should_block_with_nudge(
    rule_id: str,
    context_key: str,
    message: str,
    session_id: Optional[str] = None,
    cooldown_minutes: int = DEFAULT_COOLDOWN_MINUTES,
) -> NudgeResult:
    """
    Check if we should block with a nudge warning.

    Args:
        rule_id: Unique rule identifier (e.g., "github-actions-injection")
        context_key: Context-specific key (e.g., file path or command)
        message: Warning message to show
        session_id: Optional session ID (not currently used)
        cooldown_minutes: Minutes before re-warning

    Returns:
        NudgeResult with should_block, message, and reason
    """
    state = _load_state()

    # Probabilistic cleanup
    if random.random() < CLEANUP_PROBABILITY:
        state = _cleanup_old_entries(state)
        _save_state(state)

    # Create unique key for this rule+context
    key = f"{rule_id}:{context_key}"

    warnings = state.get("warnings", {})
    entry = warnings.get(key)

    now = time.time()
    cooldown_seconds = cooldown_minutes * 60

    if entry is None:
        # First time - block and record
        warnings[key] = {
            "timestamp": now,
            "rule_id": rule_id,
            "context_key": context_key,
            "warn_count": 1,
        }
        state["warnings"] = warnings
        _save_state(state)

        return NudgeResult(
            should_block=True,
            message=message,
            reason="first_warning",
        )

    # Check if cooldown expired
    time_since_warning = now - entry.get("timestamp", 0)

    if time_since_warning > cooldown_seconds:
        # Cooldown expired - block again with reminder
        entry["timestamp"] = now
        entry["warn_count"] = entry.get("warn_count", 0) + 1
        warnings[key] = entry
        state["warnings"] = warnings
        _save_state(state)

        return NudgeResult(
            should_block=True,
            message=f"Reminder: {message}",
            reason="reminder",
        )

    # Within cooldown - allow
    return NudgeResult(
        should_block=False,
        message="",
        reason="allowed",
    )


def clear_warning(rule_id: str, context_key: str) -> bool:
    """
    Clear a specific warning entry.

    Returns:
        True if entry was cleared, False if not found
    """
    state = _load_state()
    key = f"{rule_id}:{context_key}"

    if key in state.get("warnings", {}):
        del state["warnings"][key]
        _save_state(state)
        return True

    return False
