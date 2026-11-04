#!/bin/bash
set -euo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIGINAL_DIR="$(pwd)"
EXPECTED_PYTHON="$HOOKS_DIR/.venv/bin/python"

# Parse command-line options
ACTION="full"
QUIET=false
LOG_FILE="/tmp/hook_setup.log"

usage() {
    echo "Usage: setup.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --full, -f       Full setup: create venv, install package, verify (default)"
    echo "  --reinstall, -r  Reinstall package only (after code changes)"
    echo "  --verify, -v     Verify installation only (no install)"
    echo "  --test, -t       Run all hook tests with echo method"
    echo "  --quiet, -q      Minimal output"
    echo "  --help, -h       Show this help"
    echo ""
    echo "Examples:"
    echo "  ./setup.sh                  # Full setup"
    echo "  ./setup.sh --reinstall      # After modifying custom_hooks/*.py"
    echo "  ./setup.sh --verify         # Check if package is working"
    echo "  ./setup.sh --test           # Test all hooks safely"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --full|-f)
            ACTION="full"
            shift
            ;;
        --reinstall|-r)
            ACTION="reinstall"
            shift
            ;;
        --verify|-v)
            ACTION="verify"
            shift
            ;;
        --test|-t)
            ACTION="test"
            shift
            ;;
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

log() {
    if [ "$QUIET" = false ]; then
        echo "$1"
    fi
    echo "$1" >> "$LOG_FILE"
}

# Check project-level settings.json for correct venv usage
check_project_hooks() {
    local project_settings="$ORIGINAL_DIR/.claude/settings.json"

    if [ ! -f "$project_settings" ]; then
        log "  No project-level settings.json found (OK)"
        return 0
    fi

    log "  Found project settings: $project_settings"

    # Use Python to parse JSON and check hook commands
    local result
    result=$(PROJECT_SETTINGS="$project_settings" EXPECTED_PYTHON="$EXPECTED_PYTHON" .venv/bin/python << 'PYEOF'
import json
import sys
import os

settings_path = os.environ.get('PROJECT_SETTINGS')
expected_python = os.environ.get('EXPECTED_PYTHON')

try:
    with open(settings_path) as f:
        settings = json.load(f)
except (json.JSONDecodeError, FileNotFoundError) as e:
    print(f"  ERROR: Cannot parse {settings_path}: {e}")
    sys.exit(1)

hooks = settings.get('hooks', {})
if not hooks:
    print("  No hooks configured in project settings (OK)")
    sys.exit(0)

errors = []
checked = 0

for hook_type, hook_list in hooks.items():
    if not isinstance(hook_list, list):
        continue
    for entry in hook_list:
        if not isinstance(entry, dict):
            continue
        for hook in entry.get('hooks', []):
            if not isinstance(hook, dict):
                continue
            cmd = hook.get('command', '')
            checked += 1
            if not cmd.startswith(expected_python):
                errors.append(f"    {hook_type}: {cmd[:60]}...")

if errors:
    print(f"  WARN: {len(errors)} hook(s) not using shared venv:")
    for e in errors:
        print(e)
    print(f"  Expected prefix: {expected_python}")
    sys.exit(1)
else:
    print(f"  Checked {checked} hook command(s) - all use shared venv (OK)")
    sys.exit(0)
PYEOF
    )
    local exit_code=$?
    log "$result"
    return $exit_code
}

cd "$HOOKS_DIR"

# Clear log file
echo "=== Claude Hooks Setup ===" > "$LOG_FILE"
echo "" >> "$LOG_FILE"

case $ACTION in
    full)
        log "=== Claude Hooks Setup (Full) ==="
        log ""

        # Create venv if not exists or if it is incomplete (e.g. Docker named volume
        # mounted at .venv/ creates the directory but leaves it empty — bin/pip is
        # absent in that case, so we must run venv creation to populate the volume).
        if [ ! -f ".venv/bin/pip" ]; then
            log "Creating virtual environment..."
            python3 -m venv .venv
        else
            log "Virtual environment already exists."
        fi

        # Upgrade pip
        log "Upgrading pip..."
        .venv/bin/pip install --upgrade pip -q

        # Install package in editable mode
        log "Installing custom-hooks package..."
        .venv/bin/pip install -e . -q

        # Verify installation
        log "Verifying installation..."
        .venv/bin/python -c "from custom_hooks import Action, Rule, load_input, register_hook, list_hooks; print('  custom_hooks package installed successfully')"

        log ""
        log "=== Setup Complete ==="
        log ""
        log "Update ~/.claude/settings.json hooks to use:"
        log "  $HOOKS_DIR/.venv/bin/python $HOOKS_DIR/<script>.py"
        log ""
        log "Example:"
        log "  \"command\": \"$HOOKS_DIR/.venv/bin/python $HOOKS_DIR/pretooluse_bash.py\""
        ;;

    reinstall)
        log "=== Reinstalling custom-hooks package ==="
        log ""

        if [ ! -d ".venv" ]; then
            log "ERROR: Virtual environment not found. Run --full first."
            exit 1
        fi

        # Reinstall package
        log "Reinstalling package..."
        .venv/bin/pip install -e . -q

        # Verify
        log "Verifying..."
        .venv/bin/python -c "from custom_hooks import Action, Rule, load_input, register_hook, list_hooks; print('  Package reinstalled successfully')"

        log ""
        log "=== Reinstall Complete ==="
        ;;

    verify)
        log "=== Verifying Installation ==="
        log ""

        if [ ! -d ".venv" ]; then
            log "ERROR: Virtual environment not found."
            exit 1
        fi

        # Test imports
        log "Testing imports..."
        .venv/bin/python -c "
from custom_hooks import (
    Action, Rule, HookEntry,
    load_input, block, allow, warn, output,
    categorize_command, apply_rules,
    should_block_with_nudge, NudgeResult,
    register_hook, get_hook, list_hooks, enable_hook, disable_hook
)
print('  All imports successful')
"

        # List registered hooks
        log ""
        log "Registered hooks:"
        .venv/bin/python -c "
from custom_hooks import list_hooks
for h in list_hooks():
    status = 'enabled' if h.enabled else 'disabled'
    print(f'  {h.name}: {status}')
"

        # Check project-level hooks if run from a project directory
        log ""
        log "Checking project-level hooks..."
        check_project_hooks || log "  (Project hook check had warnings)"

        log ""
        log "=== Verification Complete ==="
        ;;

    test)
        log "=== Testing All Hooks ==="
        log ""

        if [ ! -d ".venv" ]; then
            log "ERROR: Virtual environment not found."
            exit 1
        fi

        # Test each hook
        log "Testing pretooluse_bash.py (allowed command)..."
        echo '{"tool_name": "Bash", "tool_input": {"command": "echo hello"}}' | .venv/bin/python pretooluse_bash.py
        log "  Exit code: $? (expected: 0)"

        log ""
        log "Testing pretooluse_file.py (allowed path)..."
        echo '{"tool_name": "Write", "tool_input": {"file_path": "/tmp/test.py", "content": "print(1)"}}' | .venv/bin/python pretooluse_file.py
        log "  Exit code: $? (expected: 0)"

        log ""
        log "Testing posttooluse_file.py (non-python file)..."
        echo '{"tool_name": "Write", "tool_input": {"file_path": "/tmp/test.txt"}, "tool_result": "success"}' | .venv/bin/python posttooluse_file.py
        log "  Exit code: $? (expected: 0)"


        # Check project-level hooks if run from a project directory
        log ""
        log "Checking project-level hooks..."
        check_project_hooks || log "  (Project hook check had warnings)"

        log ""
        log "=== All Tests Complete ==="
        ;;
esac

log ""
log "Log saved to: $LOG_FILE"
