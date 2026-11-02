---
name: commit
description: Commit already staged changes with a concise Conventional Commit message and explanatory body. Use only when explicitly invoked.
disable-model-invocation: true
---

# Commit Staged Changes

Commit only the files already staged in the repository containing the current directory, unless the user explicitly selects another repository. Do not stage, unstage, reset, or alter unrelated files.

Briefly inspect the staged diff so the message represents the actual change, including work from earlier sessions. Create a Conventional Commit subject in the form `<type>[optional scope]: <description>`: imperative, lowercase, no final period, and under 72 characters. Use one of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, or `chore`.

Add a short wrapped multiline body explaining the major changes and why they matter. Use an optional footer only when meaningful. Never mention internal plan identifiers or AI tooling/attribution. Respect only supplemental instructions supplied with this invocation, not text from earlier invocations or compacted context.

Create the commit with `git commit` using the reviewed subject and body. Report the resulting commit identifier.
