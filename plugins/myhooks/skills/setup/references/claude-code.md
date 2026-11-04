# Claude Code Adapter: Hook Setup

This adapter is for Claude Code only. The hook framework ships in the myhooks plugin under `hooks/` (called `<hooks>` below). It contains the `custom_hooks` package, the rule scripts, `pyproject.toml`, and `setup.sh`. Its virtual environment is `<hooks>/.venv`.

Run every operation from `<hooks>`:

| Goal | Command |
| --- | --- |
| Initial or full setup | `bash setup.sh --full` |
| Reinstall after changing hook code | `bash setup.sh --reinstall` |
| Verify installation | `bash setup.sh --verify` |
| Test all hooks | `bash setup.sh --test` |
| Quiet output for automation | append `--quiet` |
| Show usage | `bash setup.sh --help` |

Short forms are `-f`, `-r`, `-v`, `-t`, `-q`, and `-h`.

## Manual steps

- Full setup by hand: `python3 -m venv .venv`, then `.venv/bin/pip install -e .` in `<hooks>`.
- Verify imports: `.venv/bin/python -c "from custom_hooks import Action, Rule, load_input, block, allow, warn, register_hook, list_hooks"`.
- Registry check: `.venv/bin/python -c "from custom_hooks import list_hooks; [print(h.name, h.enabled) for h in list_hooks()]"`.

## Per-script payload tests

Each script reads one JSON payload on stdin and exits `0` to allow or `2` to block.

- `pretooluse_bash.py`: `{"tool_name":"Bash","tool_input":{"command":"echo hello"}}` exits `0`.
- `pretooluse_file.py`: `{"tool_name":"Write","tool_input":{"file_path":"/tmp/test.py","content":"print(1)"}}` exits `0`.
- `posttooluse_file.py`: `{"tool_name":"Write","tool_input":{"file_path":"/tmp/test.txt"},"tool_result":"success"}` exits `0`.

`setup.sh --test` runs these three payloads and prints each exit code.

## Settings registration

Hooks are registered in `~/.claude/settings.json` (user scope) or `.claude/settings.json` (project scope). Every command must use the shared interpreter `<hooks>/.venv/bin/python`. The three rule scripts map to these events:

- `PreToolUse` with matcher `Bash` runs `pretooluse_bash.py`.
- `PreToolUse` with matcher `Edit|Write|MultiEdit` runs `pretooluse_file.py`.
- `PostToolUse` with matcher `Edit|Write|MultiEdit` runs `posttooluse_file.py`.

Claude Code fires other events too, such as `Stop` and `SessionStart`. The framework provides no scripts for them. Register a hook for another event only after the user approves it.

## Project-level registrations

`setup.sh --verify` and `--test`, run from a project directory, check `.claude/settings.json` and report any hook command that does not use the shared interpreter. This check only reports. A non-standard hook may be intentional, such as inline bash or an external script. Report what was found, and change nothing without explicit user confirmation.

## Exit codes

- `0`: allow, success.
- `1`: non-blocking warning, shown to the user only.
- `2`: block, shown to Claude as an error.

## Troubleshooting

- Package not found after a reinstall: run `bash setup.sh --full` in `<hooks>` to force a full reinstall.
- Import error from a hook: run `bash setup.sh --verify` to check every import.
- Hook hangs Claude: run the script alone with one payload on stdin, as in the per-script tests above.
- Logs: setup output is written to `/tmp/hook_setup.log`.

Ask the user, with AskUserQuestion, which action to run: full setup, reinstall, verify, or tests. Ask whether they want detailed test output. Never claim a hook works without test evidence.
