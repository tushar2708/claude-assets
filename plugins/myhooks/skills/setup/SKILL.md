---
name: setup
description: Set up, reinstall, verify, or test the Claude Code hooks system. When used in Codex, explain the lack of an equivalent adapter and offer a portable policy alternative. Use only when explicitly invoked.
disable-model-invocation: true
---

# Set Up Hook Rules

## Select the host branch

- **Claude Code:** read [the Claude adapter](references/claude-code.md), then ask the user whether to run full setup, reinstall, verify, or tests.
- **Codex:** no equivalent hook adapter is shipped. Do not install a Claude hook system or modify Codex configuration. Offer a portable policy implementation in `AGENTS.md`, a checked-in pre-commit/CI/Makefile check, or a GitHub issue requesting the lifecycle event and payload the user needs.

## Claude Code workflow

1. Identify the requested action: full setup, reinstall after a code change, verification, or safe tests.
2. Run the corresponding shared setup command from the installed hook root.
3. Report findings. If project-local hook configuration is non-standard, describe it and request explicit approval before changing it.
4. When testing, show either concise output or full output according to the user's choice.

The exit contract is `0` allow/success, `1` non-blocking warning, and `2` block. Never claim registration or a working hook without verification evidence.
