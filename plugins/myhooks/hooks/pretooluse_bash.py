#!/usr/bin/env python3
"""
PreToolUse hook for Bash commands.

Validates git, npm, make, rm, and sed commands before they run.

Exit codes:
- 0: Allow
- 2: Block (message shown to Claude)
"""

import os
import re
import sys
from pathlib import Path

from custom_hooks import load_input, block, allow
from custom_hooks.types import Action, Rule


# =============================================================================
# RULE ENABLED CONFIG - Toggle individual rules True/False
# =============================================================================

RULE_ENABLED = {
    # Git rules
    "git-checkout": True,
    "git-reset": True,
    "git-add-all": True,
    "git-no-verify": False,  # DISABLED: Allow --no-verify flag
    "git-destructive": True,
    "git-stash": True,
    # General rules
    "rm-command": True,
    "sed-command": True,
    # Special handlers
    "npm-no-save": True,
    "make-no-makefile": True,
}


# Widespread-`git add` matcher, shared by the hard guard in main() and the
# git-add-all Rule. Requirements it satisfies:
#   - matches `git add` even when git is NOT the first token: variable-assignment
#     prefixes, `cd && git ...`, path-prefixed git (`/usr/bin/git`), and global
#     options before the subcommand (`git -C <path> add ...`, `git -c k=v add`).
#   - the offending arg (-A / -a / --all / bare `.`) must end at a shell boundary
#     (whitespace, end-of-string, or a separator `; & | ) < >`), so `git add -A;`
#     is caught, while a real dotfile/path (`git add .gitignore`, `git add ./src`)
#     and selective adds (`git add src/main.go`) are NOT matched.
GIT_ADD_ALL_PATTERN = (
    r"\bgit\b\s+(?:[^\s;&|]+\s+)*?add\s+(?:-A|-a|--all|\.)(?=[\s;&|)<>]|$)"
)


# Shared prefix matching `git` followed by any global options (e.g. `-C <path>`,
# `-c k=v`) before the subcommand. Prepend it to every git rule's subcommand so the
# rule ALSO catches the `git -C <path> <subcommand>` form, not just `git <subcommand>`.
# Mirrors the lazy token-skipping of GIT_ADD_ALL_PATTERN.
GIT_PREFIX = r"\bgit\b\s+(?:[^\s;&|]+\s+)*?"


# =============================================================================
# RULE DEFINITIONS
# =============================================================================


def get_git_rules() -> list[Rule]:
    """Git command validation rules."""
    return [
        Rule(
            id="git-checkout",
            pattern=GIT_PREFIX + r"checkout\b",
            action=Action.DENY,
            message=(
                "BLOCKED: git checkout is NOT allowed!\n\n"
                "STOP PANIC CHECKOUT!\n"
                "Do NOT revert changes without talking to the user first.\n\n"
                "If you think changes need to be reverted:\n"
                "1. STOP and ask the user\n"
                "2. Explain what went wrong\n"
                "3. Wait for user guidance"
            ),
        ),
        Rule(
            id="git-reset",
            pattern=GIT_PREFIX + r"reset\b",
            action=Action.DENY,
            message=(
                "BLOCKED: git reset is NOT allowed (in ANY form, incl. git -C <path>)!\n\n"
                "git reset can unstage or discard work. Do NOT revert with git.\n"
                "To undo your own edits, use the Edit tool to reverse them.\n"
                "If a reset is truly needed, STOP and ask the user."
            ),
        ),
        Rule(
            id="git-add-all",
            pattern=GIT_ADD_ALL_PATTERN,
            action=Action.DENY,
            message=(
                "BLOCKED: Widespread git add is NOT allowed!\n"
                "FORBIDDEN: git add -A, git add -a, git add --all, git add .\n"
                "USE SELECTIVE ADDS ONLY: git add <specific-file-path>\n"
                "Example: git add src/main.go config/app.json"
            ),
        ),
        Rule(
            id="git-no-verify",
            pattern=GIT_PREFIX + r"(?:commit|push)\b.*(?:--no-verify|-n\s)",
            action=Action.DENY,
            message=(
                "BLOCKED: Cannot skip pre-commit hooks!\n\n"
                "FORBIDDEN:\n"
                "  - git commit --no-verify (skips pre-commit hook)\n"
                "  - git commit -n (skips pre-commit hook)\n"
                "  - git push --no-verify (skips pre-push hook)\n\n"
                "Pre-commit hooks exist for a reason. Fix the underlying issue instead."
            ),
        ),
        Rule(
            id="git-destructive",
            pattern=GIT_PREFIX + r"(?:clean(?:\s|$)|push\s+(?:--force|-f)|rebase)",
            action=Action.DENY,
            message=(
                "BLOCKED: DESTRUCTIVE git command NOT allowed!\n\n"
                "FORBIDDEN:\n"
                "  - git reset --hard (loses all changes)\n"
                "  - git clean (deletes untracked files)\n"
                "  - git push --force (destroys remote history)\n"
                "  - git rebase (can cause serious issues)\n\n"
                "NEVER run these without EXPLICIT user permission."
            ),
        ),
        Rule(
            id="git-stash",
            pattern=GIT_PREFIX + r"stash\b",
            action=Action.DENY,
            message=(
                "BLOCKED: git stash is not allowed.\n"
                "Commit your work or discuss with user about uncommitted changes."
            ),
        ),
    ]


def get_general_rules() -> list[Rule]:
    """General command validation rules."""
    return [
        Rule(
            id="rm-command",
            pattern=r"^rm\s+",
            action=Action.DENY,
            message=(
                "BLOCKED: rm command not allowed.\n"
                "Ask user before deleting files."
            ),
        ),
        Rule(
            id="sed-command",
            pattern=r"^sed\s+-i(?:\s|'|\"|\.|$)|^sed\s+\S.*\s-i(?:\s|'|\"|\.|$)",
            action=Action.DENY,
            message=(
                "BLOCKED: sed -i (in-place edit) not allowed.\n"
                "Use the Edit tool instead for file modifications."
            ),
        ),
    ]


# =============================================================================
# SPECIAL HANDLERS (complex logic that can't be a simple regex)
# =============================================================================


def handle_npm(command: str) -> None:
    """
    Handle npm install commands.

    Allows:
    - npm install (from package.json)
    - npm install --save <pkg>
    - npm install --save-dev <pkg>
    - npm install -g <pkg>

    Blocks:
    - npm install <pkg> (without --save flags)
    """
    # Not an npm install command
    if not re.search(r"npm\s+(install|i)(\s|$)", command):
        return

    # Plain "npm install" - allowed
    if re.search(r"npm\s+(install|i)\s*$", command):
        return

    # Has proper flags - allowed
    if re.search(r"(--save|--save-dev|-S|-D|--global|-g|--production|--only=prod)", command):
        return

    # Block: installing packages without proper flags
    block(
        "BLOCKED: npm install with packages must include --save or --save-dev flag.\n\n"
        "Use:\n"
        "  npm install --save <package>      (for dependencies)\n"
        "  npm install --save-dev <package>  (for dev dependencies)\n\n"
        "Plain 'npm install' (to install from package.json) is allowed."
    )


def handle_make(command: str) -> None:
    """
    Handle make commands - requires absolute paths.

    REQUIRES:
    - cd /absolute/path && make target
    - OR make -f /absolute/path/Makefile target
    - OR make -C /absolute/path target

    REJECTS:
    - make target (no path specified)
    - cd ../relative && make (relative paths)
    - make -f ../Makefile (relative paths)

    Always verifies the target path exists.
    """
    # Pattern 1: make -f /absolute/path/Makefile
    match = re.search(r"-f\s+(\S+)", command)
    if match:
        makefile_path = Path(match.group(1))
        if not makefile_path.is_absolute():
            block(
                f"BLOCKED: Relative path in -f flag not allowed.\n\n"
                f"Current command: {command.strip()}\n\n"
                f"REQUIREMENT: Use absolute path for -f flag\n"
                f"Example: make -f /absolute/path/to/Makefile target\n\n"
                f"Current path (relative): {makefile_path}"
            )
            return

        if not makefile_path.exists():
            block(
                f"BLOCKED: Specified Makefile does not exist.\n\n"
                f"Current command: {command.strip()}\n"
                f"File not found: {makefile_path}\n\n"
                f"Please verify the Makefile path."
            )
            return

        # File exists and is absolute - allow
        return

    # Pattern 3: make -C /absolute/path
    match = re.search(r"\bmake\s+-C\s+(\S+)", command)
    if match:
        target_dir = Path(match.group(1))
        if not target_dir.is_absolute():
            block(
                f"BLOCKED: Relative path in -C flag not allowed.\n\n"
                f"Current command: {command.strip()}\n\n"
                f"REQUIREMENT: Use absolute path for -C flag\n"
                f"Example: make -C /absolute/path/to/project target\n\n"
                f"Current path (relative): {target_dir}"
            )
            return

        has_makefile = (target_dir / "Makefile").exists() or (target_dir / "makefile").exists()
        if not has_makefile:
            block(
                f"BLOCKED: No Makefile found in specified directory.\n\n"
                f"Current command: {command.strip()}\n"
                f"Directory checked: {target_dir}\n\n"
                f"Please verify the Makefile exists at: {target_dir}/Makefile"
            )
            return

        return

    # Pattern 4: No path specified - reject
    if re.search(r"\bmake\b", command):
        block(
            f"BLOCKED: make command requires absolute path specification.\n\n"
            f"Current command: {command.strip()}\n\n"
            f"REQUIRED FORMAT (choose one):\n"
            f"  1) make -f /absolute/path/to/Makefile target\n"
            f"  2) make -C /absolute/path/to/project target\n\n"
            f"Do NOT use cd && make — use -C or -f flags instead.\n"
            f"Relative paths are NOT allowed."
        )


def is_make_command(command: str) -> bool:
    """
    Check if this is a make command (not just "make" in arguments).

    Handles:
    - make target
    - cd /path && make target
    - ./path/make target
    - /abs/path/make target

    Returns False for:
    - gh pr edit ... (with "make" in body text)
    - echo "make something"
    """
    # Remove any cd ... && prefix to get the actual command
    cmd = command.strip()

    # Check for cd ... && pattern
    cd_match = re.search(r"cd\s+\S+\s*&&\s*(.+)", cmd)
    if cd_match:
        cmd = cd_match.group(1).strip()

    # Get first word (command name)
    first_word = cmd.split()[0] if cmd.split() else ""

    # Check if it's make (possibly with path prefix)
    # Matches: make, ./make, ../make, /abs/path/make
    return re.search(r"(^|/)make$", first_word) is not None


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:
    """Main entry point."""
    # Skip hooks if running under Cursor
    is_cursor = (
        os.environ.get("CURSOR") == "1"
        or os.environ.get("CURSOR_AGENT") == "1"
        or bool(os.environ.get("CURSOR_TRACE_ID"))
        or os.environ.get("TERM_PROGRAM", "").lower() == "cursor"
    )
    if is_cursor:
        allow()

    input_data = load_input()
    command = input_data.get("tool_input", {}).get("command", "")

    if not command:
        allow()

    # HARD GUARD (runs on EVERY command, regardless of form) — widespread `git add`
    # must NEVER run, even when `git` is not the first token: variable-assignment
    # prefixes (`C=/x; git -C $C add -A`), `cd && git ...`, path-prefixed git, or
    # `git -C <path> add ...`. All of these slip past the `startswith("git ")`
    # dispatch below, so this check is intentionally placed BEFORE it and matches
    # anywhere in the command via re.search. The trailing (?=\s|$) makes the bare
    # `.` (current dir) match `git add .` but NOT `git add .gitignore`/`git add ./x`.
    if RULE_ENABLED.get("git-add-all", True) and re.search(
        GIT_ADD_ALL_PATTERN,
        command,
        re.IGNORECASE,
    ):
        block(
            "BLOCKED: Widespread git add is NOT allowed (in ANY command form)!\n"
            "FORBIDDEN: git add -A, git add -a, git add --all, git add .\n"
            "Claude: never run these commands. This guard also catches them behind a\n"
            "variable assignment, `cd &&`, a path prefix, or `git -C <path>`.\n"
            "USE SELECTIVE ADDS ONLY: git add <specific-file-path>\n"
            "Example: git add src/main.go config/app.json"
        )

    # HARD GUARD (runs on EVERY command form) — destructive reverts that must NEVER
    # run, including behind `git -C <path>`, a path-prefixed git, `cd &&`, or a
    # variable-assignment prefix. These discard or rewrite work; the user reverts by
    # hand, never the agent. To undo its own edits the agent uses the Edit tool.
    for _subcmd, _label in ((r"checkout\b", "git checkout"), (r"reset\b", "git reset")):
        if re.search(GIT_PREFIX + _subcmd, command, re.IGNORECASE):
            block(
                f"BLOCKED: {_label} is NOT allowed (in ANY command form, incl. git -C <path>).\n"
                "Do NOT revert or discard changes with git. To undo your own edits, use the\n"
                "Edit tool to reverse them. If changes must be reverted, STOP and ask the user."
            )

    # Categorize and apply rules
    command_lower = command.strip().lower()

    # Git commands
    if command_lower.startswith("git "):
        for rule in get_git_rules():
            if RULE_ENABLED.get(rule.id, True) and re.search(rule.pattern, command, re.IGNORECASE):
                block(rule.message)
        allow()

    # NPM commands
    if command_lower.startswith("npm "):
        if RULE_ENABLED.get("npm-no-save", True):
            handle_npm(command)
        allow()

    # Make commands
    if is_make_command(command):
        if RULE_ENABLED.get("make-no-makefile", True):
            handle_make(command)
        allow()

    # General rules (rm, sed)
    for rule in get_general_rules():
        if RULE_ENABLED.get(rule.id, True) and re.search(rule.pattern, command, re.IGNORECASE):
            block(rule.message)

    # No rules matched - allow
    allow()


if __name__ == "__main__":
    main()
