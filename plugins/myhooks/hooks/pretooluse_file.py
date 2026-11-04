#!/usr/bin/env python3
"""
PreToolUse hook for file edit commands (Edit/Write/MultiEdit).

Validates file paths and content before editing.

Exit codes:
- 0: Allow
- 2: Block (message shown to Claude)
"""

import os
import re

from custom_hooks import load_input, block, allow


# =============================================================================
# RULE ENABLED CONFIG - Toggle individual rules True/False
# =============================================================================

RULE_ENABLED = {
    "autogen-files": True,
    "go-error-suppression": True,
    "go-nilnil-return": True,    # Block 'return nil, nil' when last return is error
    "go-nolint-ban": True,       # Block ANY //nolint directive in .go added content
    "write-existing-file": True,  # Block Write tool on existing files
}


# =============================================================================
# GO VALIDATIONS
# =============================================================================


def check_go_error_suppression(content: str, file_path: str) -> None:
    """
    Check Go code for blank identifier _ as last field before := or =.

    This is a simple heuristic - the actual type check happens in pre-commit hooks
    which cannot be fooled by nolint comments.
    """
    source_lines = content.splitlines()
    violations = []

    # Pattern: ..., _ := or ..., _ =
    # Check each line
    for line_num, line in enumerate(source_lines, start=1):
        # Match pattern: ... , _ := or ... , _ =
        # Only matches when _ is the LAST variable before := or =
        if re.search(r",\s*_\s*[:=]", line):
            violations.append(f"  Line {line_num}: {line.strip()}")

    if violations:
        block(
            f"BLOCKED: Blank identifier (_) detected as last return value in {file_path}\n\n"
            f"The following lines use _ as the last return value:\n"
            + "\n".join(violations) +
            "\n\n"
            "RULE: every function MUST return an error or a boolean as its LAST return\n"
            "value — this is mandatory, even for a function that always returns an error.\n"
            "A boolean last return (e.g. the ok of a comma-ok, a 'found'/'exists' flag)\n"
            "carries the same meaning as an error and MUST be checked exactly like one.\n\n"
            "Therefore the last return value — error OR boolean — must NEVER be discarded\n"
            "with _. Assign it to a named variable and act on it:\n"
            "  v, ok := m[k]\n"
            "  if !ok { /* handle the missing case explicitly */ }\n"
            "  res, err := doThing()\n"
            "  if err != nil { return fmt.Errorf(\"ctx: %w\", err) }\n\n"
            "nolint is banned in this codebase. Fix the code, never the linter."
        )


def check_go_nilnil_return(content: str, file_path: str) -> None:
    """
    Check Go code for 'return nil, nil' where the last return value is an error.

    This is the nilnil anti-pattern: returning nil for both value and error makes
    it impossible for callers to distinguish 'nothing found' from 'success'.
    The nilnil linter flags this, but we catch it before the edit is written.

    Exempt _test.go files: a test double that deliberately returns (nil, nil)
    to exercise a function's own documented handling of that case (e.g. a
    contract test for a "nil value with nil error is rejected" rule) is not
    the production ambiguity this check exists to catch. This exemption is
    test-code only — never applies to a non-test .go file.
    """
    if file_path.endswith("_test.go"):
        return

    source_lines = content.splitlines()
    violations = []

    for line_num, line in enumerate(source_lines, start=1):
        stripped = line.strip()
        # Skip comments
        if stripped.startswith("//"):
            continue
        # Match ONLY: return nil, nil  (both value AND error are nil)
        # The trailing nil must be the last value — not followed by another comma+value.
        # This blocks the nilnil anti-pattern while allowing:
        #   return someVal, nil        (valid success)
        #   return nil, someErr        (valid error)
        #   return nil, nil, someErr   (valid — last item is a real error)
        if re.search(r'\breturn\s+nil\s*,\s*nil\s*(?://.*)?$', line):
            violations.append(f"  Line {line_num}: {line.strip()}")

    if violations:
        block(
            f"BLOCKED: 'return nil, nil' detected in {file_path}\n\n"
            "Returning nil for both value and error is FORBIDDEN in this codebase.\n"
            "When a function's last return type is error, returning nil error hides\n"
            "the absence of a value — the caller cannot distinguish 'not found' from 'success'.\n\n"
            "The following lines violate this rule:\n"
            + "\n".join(violations) + "\n\n"
            "FIX: Return a sentinel error declared in the package:\n"
            "  var ErrNotFound = errors.New(\"not found\")\n"
            "  return nil, ErrNotFound\n\n"
            "The CALLER must then handle the sentinel:\n"
            "  result, err := someFunc(ctx, id)\n"
            "  if errors.Is(err, ErrNotFound) {\n"
            "      // handle not-found — do NOT ignore it\n"
            "  }\n\n"
            "NEVER suppress the nilnil linter. Fix the root cause.\n"
            "A function must not decide what 'nothing' means on behalf of its caller."
        )


def check_go_nolint_ban(content: str, file_path: str) -> None:
    """
    Block ANY //nolint directive in Go content. nolint is banned — no exceptions.

    Covers both the no-space form (//nolint:...) that golangci parses and the
    spaced form (// nolint:...). The fix is always to correct the code, never to
    silence the linter. There is NO sanctioned nolint escape in this codebase.
    """
    source_lines = content.splitlines()
    violations = []

    for line_num, line in enumerate(source_lines, start=1):
        if re.search(r"//\s*nolint", line):
            violations.append(f"  Line {line_num}: {line.strip()}")

    if violations:
        block(
            f"BLOCKED: nolint directive detected in {file_path}\n\n"
            "nolint is banned in this codebase — no exceptions.\n\n"
            "The following lines add a nolint:\n"
            + "\n".join(violations) + "\n\n"
            "Fix the underlying code, never silence the linter. Examples:\n"
            "  - comma-ok: assign the boolean to a variable and CHECK it\n"
            "    (v, ok := m[k]; if !ok { ... }) — never discard it with _.\n"
            "  - unchecked error: handle or return it\n"
            "    (if err != nil { return fmt.Errorf(\"ctx: %w\", err) })."
        )


def check_go_file(file_path: str, content: str) -> None:
    """
    Run all Go-specific validations on a file.

    Args:
        file_path: Path to the Go file
        content: File content to validate
    """
    # Check for error suppression
    if RULE_ENABLED.get("go-error-suppression", True):
        check_go_error_suppression(content, file_path)

    # Check for nilnil returns
    if RULE_ENABLED.get("go-nilnil-return", True):
        check_go_nilnil_return(content, file_path)

    # Block any nolint directive
    if RULE_ENABLED.get("go-nolint-ban", True):
        check_go_nolint_ban(content, file_path)


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
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        allow()

    # Block Write tool on existing files (with path exceptions)
    if RULE_ENABLED.get("write-existing-file", True):
        # Paths where Write() on existing files is allowed
        write_existing_allowlist = [
            os.path.expanduser("~/.claude/plans/"),
        ]
        is_allowed = any(
            os.path.expanduser(file_path).startswith(prefix)
            for prefix in write_existing_allowlist
        )
        if tool_name == "Write" and os.path.exists(file_path) and not is_allowed:
            block(
                f"BLOCKED: Write() on existing file is DANGEROUS - will corrupt {file_path}\n"
                "Write() replaces entire contents. Use Read() first, then targeted Edit()/Update()."
            )

    # Block edits to autogenerated files
    if RULE_ENABLED.get("autogen-files", True):
        if re.search(r"/(generated|autogen|autogenerated)/", file_path):
            block(
                "BLOCKED: Cannot modify autogenerated file.\n"
                f"Path: {file_path}\n\n"
                "Autogenerated files are managed by code generators.\n"
                "Modify the source/template instead."
            )

    # Go file validations
    if file_path.endswith(".go"):
        # Collect all new content snippets being written (handles Write, Edit, MultiEdit)
        go_contents = []

        if "new_content" in tool_input:
            # Write tool: full file content
            go_contents.append(tool_input["new_content"])
        elif "new_string" in tool_input:
            # Edit tool: replacement string
            go_contents.append(tool_input["new_string"])
        elif "edits" in tool_input:
            # MultiEdit tool: list of {old_string, new_string} dicts
            for edit in tool_input.get("edits", []):
                ns = edit.get("new_string")
                if ns:
                    go_contents.append(ns)

        for content in go_contents:
            if content:
                check_go_file(file_path, content)

    allow()


if __name__ == "__main__":
    main()
