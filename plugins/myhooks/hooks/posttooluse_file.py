#!/usr/bin/env python3
"""
PostToolUse hook for file edit commands (Edit/Write/MultiEdit).

Validates Python files after editing:
1. Syntax check (py_compile)
2. Local import detection (AST-based)

Exit codes:
- 0: All checks passed
- 1: Non-blocking error (shown to user only)
- 2: Block (message shown to Claude - should fix the issue)
"""

import ast
import subprocess
import sys
from pathlib import Path

from custom_hooks import load_input, block, allow, warn


# =============================================================================
# RULE ENABLED CONFIG - Toggle individual rules True/False
# =============================================================================

RULE_ENABLED = {
    "python-syntax": True,
    "python-local-imports": True,
}


# =============================================================================
# LOCAL IMPORT DETECTOR (ported from check-local-imports.py)
# =============================================================================


class LocalImportDetector(ast.NodeVisitor):
    """AST visitor to detect local imports inside functions/methods/classes."""

    # Nolint comment directive that suppresses local import warnings
    NOLINT_DIRECTIVE = "nolint:local_import_to_avoid_cycle"

    def __init__(self, source_lines: list[str]):
        self.local_imports = []
        self.context_stack = []
        self.source_lines = source_lines

    def _has_nolint_comment(self, lineno: int) -> bool:
        """Check if the import line has a nolint comment.

        Checks both:
        1. Same line: import foo  # nolint:local_import_to_avoid_cycle
        2. Previous line: # nolint:local_import_to_avoid_cycle
        """
        # lineno is 1-indexed, convert to 0-indexed
        idx = lineno - 1

        # Check same line (inline comment)
        if idx < len(self.source_lines):
            if self.NOLINT_DIRECTIVE in self.source_lines[idx]:
                return True

        # Check previous line (standalone comment)
        if idx > 0:
            prev_line = self.source_lines[idx - 1].strip()
            if prev_line.startswith("#") and self.NOLINT_DIRECTIVE in prev_line:
                return True

        return False

    def _in_local_context(self) -> bool:
        """Check if we're currently inside a function, method, or class."""
        return len(self.context_stack) > 0

    def _get_context_info(self) -> str:
        """Get description of current context."""
        if not self.context_stack:
            return "module level"
        return " -> ".join(self.context_stack)

    def visit_FunctionDef(self, node):
        """Visit function definition."""
        self.context_stack.append(f"function '{node.name}'")
        self.generic_visit(node)
        self.context_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition."""
        self.context_stack.append(f"async function '{node.name}'")
        self.generic_visit(node)
        self.context_stack.pop()

    def visit_ClassDef(self, node):
        """Visit class definition."""
        self.context_stack.append(f"class '{node.name}'")
        self.generic_visit(node)
        self.context_stack.pop()

    def visit_Import(self, node):
        """Visit import statement."""
        if self._in_local_context():
            # Skip if nolint comment is present
            if not self._has_nolint_comment(node.lineno):
                imports = [alias.name for alias in node.names]
                self.local_imports.append({
                    "line": node.lineno,
                    "context": self._get_context_info(),
                    "statement": f"import {', '.join(imports)}",
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit from...import statement."""
        if self._in_local_context():
            # Skip if nolint comment is present
            if not self._has_nolint_comment(node.lineno):
                module = node.module or "."
                imports = [alias.name for alias in node.names]
                self.local_imports.append({
                    "line": node.lineno,
                    "context": self._get_context_info(),
                    "statement": f"from {module} import {', '.join(imports)}",
                })
        self.generic_visit(node)


def check_local_imports(code: str) -> list[dict]:
    """
    Check for local imports in Python code using AST.

    Returns:
        List of local import violations found.
    """
    try:
        source_lines = code.splitlines()
        tree = ast.parse(code)
        detector = LocalImportDetector(source_lines)
        detector.visit(tree)
        return detector.local_imports
    except SyntaxError:
        # Syntax errors are handled separately
        return []


# =============================================================================
# SYNTAX CHECK
# =============================================================================


def check_syntax(file_path: str) -> tuple[bool, str]:
    """
    Check Python syntax using py_compile.

    Returns:
        (passed, error_message)
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", file_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False, result.stderr
    return True, ""


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:
    """Main entry point."""
    input_data = load_input()
    file_path = input_data.get("tool_input", {}).get("file_path", "")

    if not file_path:
        allow()

    # Only check Python files
    if not file_path.endswith(".py"):
        allow()

    # Check if file exists
    if not Path(file_path).exists():
        allow()

    # 1. Syntax check
    if RULE_ENABLED.get("python-syntax", True):
        syntax_ok, syntax_error = check_syntax(file_path)
        if not syntax_ok:
            block(
                f"SYNTAX ERROR in {file_path}:\n"
                f"{syntax_error}\n\n"
                "Fix the syntax error before continuing."
            )

    # 2. Local import check
    if RULE_ENABLED.get("python-local-imports", True):
        try:
            code = Path(file_path).read_text()
            local_imports = check_local_imports(code)

            if local_imports:
                violations = "\n".join(
                    f"  Line {v['line']}: {v['statement']} (in {v['context']})"
                    for v in local_imports
                )
                block(
                    f"LOCAL IMPORTS DETECTED in {file_path}:\n"
                    f"{violations}\n\n"
                    "Move imports to module level for better performance and readability.\n"
                    "If module-level import would cause an import cycle, add:\n"
                    "  # nolint:local_import_to_avoid_cycle\n"
                    "(add this nolint comment ONLY IF module-level import leads to import cycle,\n"
                    " and not as a shortcut to silence the hook - always try making it module-level import, first)"
                )
        except Exception as e:
            # Non-blocking error for local import check
            warn(f"Warning: Could not check local imports: {e}")

    # All checks passed
    print(f"{file_path}: syntax OK, no local imports")
    allow()


if __name__ == "__main__":
    main()
