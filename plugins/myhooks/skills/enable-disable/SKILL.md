---
name: enable-disable
description: Enable or disable an individual Claude Code hook rule without changing registration or whole hook scripts. When used in Codex, explain the lack of an equivalent adapter and offer a portable policy alternative. Use only when explicitly invoked.
disable-model-invocation: true
---

# Enable or Disable Hook Rules

## Select the host branch

- **Claude Code:** read [the Claude adapter](references/claude-code.md), then identify and toggle an individual rule.
- **Codex:** no equivalent hook adapter is shipped. Do not edit Codex configuration or imply a Claude rule can control Codex actions. Offer a portable policy in `AGENTS.md`, a checked-in pre-commit/CI/Makefile check, or a GitHub issue proposing the missing lifecycle capability.

## Claude Code workflow

1. List enabled and disabled individual rule identifiers from all relevant hook scripts.
2. Search for the requested rule. If several rules match, ask the user to select the exact identifiers.
3. Toggle only those identifiers in the rule-enable map. Do not change hook registration, disable a whole script, or reinstall the package merely for a boolean rule change.
4. Re-read the changed map and report the final state plus the behavior the rule permits or blocks.

Treat “hook” as a single rule/check in this workflow, not an entire hook script.
