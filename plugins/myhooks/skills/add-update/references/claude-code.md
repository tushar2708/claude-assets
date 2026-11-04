# Claude Code Adapter: Add or Update Hook Rules

This adapter is for Claude Code only. It does not describe a portable hook API.

The hook framework ships in the myhooks plugin under `hooks/`. Call that directory `<hooks>`. Its virtual environment is `<hooks>/.venv`.

## Terminology

- **Claude hook**: a script registered in `settings.json`, such as `pretooluse_bash.py`.
- **Rule**: one check inside a script, such as `git-checkout`. A request to "add a hook" means a new rule in an existing script, not a new script file.

## Naming and routing

Existing generic tool scripts are deliberately consolidated:

| Script | Event and matcher | Add rules here when |
| --- | --- | --- |
| `pretooluse_bash.py` | `PreToolUse`, `Bash` | validating a shell command before it runs |
| `pretooluse_file.py` | `PreToolUse`, `Edit\|Write\|MultiEdit\|Update\|NotebookEdit` | validating a file edit before it is written |
| `posttooluse_file.py` | `PostToolUse`, `Edit\|Write\|MultiEdit\|Update\|NotebookEdit` | validating a file after it is written |

Do not create per-tool files such as `posttooluse_ruff.py`, `pretooluse_docker.py`, or `pretooluse_git.py`. Add a category to the existing Bash or file script instead. A new `pretooluse_<tool>.py` is allowed only for a new event and matcher combination, after explicit user approval.

## Registration and payloads

Claude Code registers command hooks in `~/.claude/settings.json` (user scope) or `.claude/settings.json` (project scope). Every command must use the shared interpreter `<hooks>/.venv/bin/python`. Ordinary rule changes must not edit registration.

The hook process reads JSON from standard input:

```json
{"tool_name":"Bash","tool_input":{"command":"git checkout main"}}
```

```json
{"tool_name":"Write","tool_input":{"file_path":"/path/file.py"},"tool_result":"success"}
```

```json
{"prompt":"User message","cwd":"/current/directory"}
```

## Exit codes and helpers

| Code | Meaning | Helper |
| --- | --- | --- |
| `0` | Allow | `allow()` |
| `1` | Warn, does not block | `warn(message)` |
| `2` | Block, message shown to Claude | `block(message)` |

## Action patterns

- `DENY`: always block with `block(message)`.
- `WARN`: block the first time, then allow during a cooldown, using `should_block_with_nudge()`.
- `CHECK`: run a validation and call `block()` only if it fails.

## Required evidence

Before editing, do all of the following:

1. List every registered hook with `list_hooks()` from `custom_hooks`, run with `<hooks>/.venv/bin/python`.
2. Read the target script and its `RULE_ENABLED` map.
3. Search the scripts for an existing rule with the same identifier or pattern.
4. Read the `settings.json` registration if the change touches registration.

Present the findings to the user with AskUserQuestion, and propose the location for the new rule.

## Adding a rule to an existing category

Example: add a `docker` rule to `pretooluse_bash.py`.

1. Add the identifier to `RULE_ENABLED` at the top of the script, with the value `True`. Identifiers must be unique.

   ```python
   RULE_ENABLED = {
       # ... existing rules ...
       "docker-rm-force": True,
   }
   ```

2. Add a `Rule` with the pattern, action, and message, in the existing category function.

   ```python
   Rule(
       id="docker-rm-force",
       pattern=r"docker\s+rm\s+-f",
       action=Action.WARN,
       message="docker rm -f removes containers without confirmation.",
   )
   ```

3. Add a dispatch check in `main()`, gated by `RULE_ENABLED`.
4. Reinstall with `bash setup.sh --reinstall` from `<hooks>`.
5. Test one allowed payload and one blocked payload. The allowed payload must exit `0`. The blocked payload must exit `2`.
6. Run the full suite with `bash setup.sh --test` from `<hooks>`.

Report the evidence before claiming the rule works.

## Adding a new hook script (rare)

Only for a new event and matcher combination, and only after the user approves it.

1. Create the script with the same structure as the existing scripts. It reads input with `load_input()`, checks it, and ends with `allow()`, `warn()`, or `block()`.
2. Reinstall with `bash setup.sh --reinstall`.
3. Test it with an echoed payload.
4. Register it with `register_hook(name=..., script_path=..., hook_type=..., matcher=..., description=...)` from `custom_hooks`.
5. Add it to `settings.json` only after every test passes. The command is `<hooks>/.venv/bin/python <hooks>/<script>.py`.

## Project-level hooks

User-level and project-level hooks run in parallel. Neither overrides the other.

- Project scripts live in `.claude/hooks/` in the project.
- A project `settings.json` entry uses the shared interpreter, with the script path relative to the project root.
- Ask the user to confirm the scope (user-level or project-level) before adding any hook.
- If `setup.sh --verify` reports an existing project hook that does not use the shared interpreter, report it. Do not convert it automatically. Convert only after explicit user confirmation, since the hook may be intentional.

## Shared library

`custom_hooks` exports:

- Types: `Action` (`DENY`, `WARN`, `CHECK`), `Rule`, `HookEntry`.
- I/O: `load_input`, `block`, `allow`, `warn`, `output`.
- Dispatch: `categorize_command`, `apply_rules`.
- Nudge: `should_block_with_nudge`, `NudgeResult`.
- Registry: `register_hook`, `get_hook`, `list_hooks`, `enable_hook`, `disable_hook`, `is_hook_enabled`, `unregister_hook`.

## Workflow summary

1. Review every registered hook and the relevant scripts.
2. Confirm with the user: scope, category or new script, action, pattern, and message.
3. Show the proposed code and wait for approval.
4. Edit the chosen script.
5. Reinstall, then test with one allowed and one blocked payload.
6. Run the full suite and report the results.
7. Register and update `settings.json` only for a new script, and only after the tests pass.
