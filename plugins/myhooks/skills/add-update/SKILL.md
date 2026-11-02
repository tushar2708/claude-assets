---
name: add-update
description: Add or update a Claude Code hook rule after reviewing existing rules and confirming scope, action, and test evidence. When used in Codex, explain the lack of an equivalent adapter and offer a portable policy alternative. Use only when explicitly invoked.
disable-model-invocation: true
---

# Add or Update Hook Rules

## Select the host branch

- **Claude Code:** read [the Claude adapter](references/claude-code.md) before inspecting or changing hooks. It contains the supported events, matchers, payloads, file conventions, registration rules, and test procedure.
- **Codex:** no equivalent hook adapter is shipped. Do not invent a Codex hook, edit Codex configuration, or claim that the Claude registration will run. Offer the user one of these portable alternatives:
  1. put the behavioral rule in the repository `AGENTS.md`;
  2. enforce it with a checked-in Makefile target, pre-commit hook, or CI check;
  3. file a GitHub issue proposing a lifecycle hook, including the desired event, payload, action, and a minimal reproducible workflow.

## Claude Code workflow

1. Review all registered hooks, relevant scripts, their rule identifiers, and the hook configuration before proposing a change.
2. Check for an existing rule that already provides the requested behavior.
3. Ask the user to confirm the scope (user or project), existing category versus new event/matcher, action (`DENY`, `WARN`, or `CHECK`), exact pattern, message, edge cases, and proposed code.
4. Add a rule to the existing matching script whenever possible. Create a new hook script only for a genuinely new event/matcher combination and only after explicit approval.
5. Make every rule independently configurable through its script's rule-enable map.
6. Reinstall when required, test an allowed input and a blocked input, then run the full hook test suite. Report the evidence before registering or claiming success.

Do not modify registration configuration directly for ordinary rule additions. Do not create category-specific standalone scripts for commands that an existing command or file hook already covers.
