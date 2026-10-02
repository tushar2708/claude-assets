---
description: Write an Architecture Decision Record (docsmith decision category) — config-driven directory and numbering, heavy researched content, immutable supersede-chain, validation.
disable-model-invocation: true
---

# Write Architecture Decision Record (ADR)

This command authors a doc in the `decision` category (an ADR).

1. Extract the decision topic from the arguments below (e.g. "create an adr for neo4j usage"
   → topic "Neo4j for Graph Storage").

2. **CRITICAL**: The ADR directory must be confirmed with the user — the full absolute path,
   via the AskUserQuestion tool — BEFORE any file is written. Instruct the subagent to perform
   this confirmation and wait for the user's answer before creating the ADR.

3. Dispatch to the `docsmith-doc-author` subagent via the Task tool (subagent_type
   `docsmith-doc-author`), passing `category: decision` and the extracted topic. The subagent
   handles ADR directory resolution (static prefix of `categories.decision.dir_patterns[0]`,
   default `docs/decisions/`), numbering (`ADR-{NNN}`, next = max existing + 1, zero-padded to
   `numbering.digits`), the required sections (Status / Context / Options Considered with at
   least 2 options / Decision / Consequences), researched substantial content (200-400 lines,
   not stubs), the immutable supersede-chain, and validating to green.

#$ARGUMENTS
