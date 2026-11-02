---
name: create-priming
description: Analyze a repository and create or refresh portable agent-context documents for its major areas. Use only when explicitly invoked.
disable-model-invocation: true
---

# Create Portable Priming

## Host-specific questions

- **Claude Code:** use `AskUserQuestion` when it is available.
- **Codex:** use `request_user_input` when it is available.
- **Any other host:** ask the same questions in concise plain text.

Work sequentially: complete each step and report its result before beginning the next.

1. Confirm the repository root when unclear. Read `AGENTS.md`, `CLAUDE.md`, `README.md`, and relevant root Markdown files.
2. Map major areas—use case, development workflow, design, backend, frontend, infrastructure, domain, and integrations—by examining manifests, code, and configuration.
3. Inspect existing `docs/agent-context/` documents, identify coverage and gaps, then ask the user which areas to create, update, or skip.
4. For each selected area, document purpose, stack, structure, key components, patterns, workflows, configuration, interfaces, development practices, and concrete `path:line` examples.
5. Write each guide to `docs/agent-context/<area>.md` and create or refresh `docs/agent-context/INDEX.md`.

Each guide must be clear, concise, evidence-based, use tables or diagrams where useful, and cross-reference related guides. In the final report list created and updated files.

`docs/agent-context/` is the canonical portable material. If a project wants host entry points, update both `AGENTS.md` and `CLAUDE.md` to point to its index; do not generate host-specific slash-command files.
