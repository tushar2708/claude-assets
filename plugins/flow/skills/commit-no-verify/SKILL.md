---
name: commit-no-verify
description: Commit already staged changes with a Conventional Commit message while explicitly skipping commit hooks. Use only when explicitly invoked.
disable-model-invocation: true
---

# Commit Staged Changes Without Verification

Commit only the files already staged in the repository containing the current directory, unless the user explicitly selects another repository. Briefly inspect the staged diff; do not stage, unstage, reset, or alter unrelated files.

Create a Conventional Commit subject in the form `<type>[optional scope]: <description>`: imperative, lowercase, no final period, and under 72 characters. Use `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, or `chore`. Add a short wrapped multiline body explaining the major changes and why they matter. Never include AI attribution, internal plan identifiers, or previous invocation arguments.

Use `git commit --no-verify` only because the user explicitly invoked this skill. Report the commit identifier and that commit hooks were skipped.
