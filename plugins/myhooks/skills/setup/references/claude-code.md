# Claude Code Adapter: Hook Setup

This adapter is for Claude Code only. The shared hooks system is installed at `~/.claude/hooks/` and contains a Python package, hook scripts, a virtual environment, and `setup.sh`.

Run the requested operation from that root:

| Goal | Command |
| --- | --- |
| Initial/full setup | `bash setup.sh --full` |
| Reinstall after changing hook code | `bash setup.sh --reinstall` |
| Verify installation | `bash setup.sh --verify` |
| Test all hooks | `bash setup.sh --test` |
| Quiet automation | append `--quiet` |

The setup system's manually testable event payloads include `PreToolUse` with `Bash` or file-edit matchers, `PostToolUse` after file edits, `UserPromptSubmit`, `Notification`, and `SubagentStop`. Their registration belongs in `~/.claude/settings.json` (user scope) or `.claude/settings.json` (project scope). The shared configuration convention is command hooks calling the shared virtual environment and scripts.

Project-local registrations found during verify/test are informational. Do not change a non-standard local hook automatically: show the event, matcher, command, and risk; then wait for explicit approval. Setup output is logged at `/tmp/hook_setup.log`.
