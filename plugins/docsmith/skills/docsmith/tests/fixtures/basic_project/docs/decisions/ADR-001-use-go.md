---
type: decision
title: "ADR-001: Use Go"
status: stable
---

# ADR-001: Use Go

## Status

Accepted.

## Context

The fixture project needs one implementation language for its entry point
and helpers. The team maintaining the fixture is small, and the code must
stay trivially buildable on every contributor's machine.

## Options Considered

### Option 1: Go

Pros:

- Single static binary, no runtime dependency to install.
- Fast compile times keep the fixture cheap to rebuild.

Cons:

- More verbose than a scripting language for tiny programs.

### Option 2: Python

Pros:

- No compile step at all.
- Familiar to everyone on the team.

Cons:

- Requires an interpreter and dependency management at runtime.
- No compile-time symbol checking for the docs to cite.

## Decision

Use Go for all fixture source code, starting with `src/main.go`.

## Consequences

- All source files under `src/` are Go files.
- Docs cite Go symbols (e.g. `src/main.go#HandleThing`) that tooling can
  verify against the source.

## Mitigation

If the verbosity cost ever matters, helper generation can be scripted
without changing the decision.

## References

- `src/main.go`
- `docs/pipeline/overview.md`
