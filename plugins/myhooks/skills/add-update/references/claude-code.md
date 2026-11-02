# Claude Code Adapter: Add or Update Hook Rules

This adapter is for Claude Code only. It does not describe a portable hook API.

## Naming and routing

Existing generic tool hook scripts are deliberately consolidated:

| Script | Event and matcher | Add rules here when |
| --- | --- | --- |
| `pretooluse_bash.py` | `PreToolUse`, `Bash` | validating a command before execution |
| `pretooluse_file.py` | `PreToolUse`, `Edit|Write|MultiEdit|Update|NotebookEdit` | validating a file edit before writing |
| `posttooluse_file.py` | `PostToolUse`, `Edit|Write|MultiEdit|Update|NotebookEdit` | validating after a file edit |
| `userpromptsubmit.py` | `UserPromptSubmit` | adding prompt context |
| `notification.py` | `Notification` | handling Claude notifications |
| `subagentstop.py` | `SubagentStop` | cleanup after a subagent completes |

Do not create files such as `posttooluse_ruff.py`, `pretooluse_docker.py`, or `pretooluse_git.py`; add a category to the existing Bash or file script. A new `pretooluse_<tool>.py` is allowed only for a new Claude event/matcher after explicit user approval.

## Registration and payloads

Claude Code registers command hooks in `~/.claude/settings.json` or a project's `.claude/settings.json`. Prefer the existing shared hook architecture at `~/.claude/hooks/`; ordinary rule changes must not edit registration directly.

The hook process receives JSON through standard input. Typical payloads are:

```json
{"tool_name":"Bash","tool_input":{"command":"git checkout main"}}
```

```json
{"tool_name":"Write","tool_input":{"file_path":"/path/file.py"},"tool_result":"success"}
```

```json
{"prompt":"User message","cwd":"/current/directory"}
```

Use exit code `0` to allow, `1` to warn without blocking, and `2` to block. The shared helpers are `allow()`, `warn(message)`, and `block(message)`.

## Required evidence

Before editing, inspect all relevant scripts, their `RULE_ENABLED` maps, matching patterns, and the hooks configuration. Search for duplicate rule identifiers and patterns. New rules belong in `RULE_ENABLED` and must have a unique identifier.

After modifying the shared hooks, run `cd ~/.claude/hooks && bash setup.sh --reinstall`; test one allowed and one blocked JSON payload through the target script; then run `cd ~/.claude/hooks && bash setup.sh --test`.
