---
type: research
title: "<Feature or Use-Case> Research"
status: draft
tags:
  - research
  - <tag-2>
# generated: stamped by the authoring command
#   by: <agent/model>
#   at: <ISO-8601 timestamp>
---

<!-- This doc is ephemeral and has no ttl_days: it is the saved output of the /grill web-research
     phase (now the /flow:research skill), stored beside the spec it informed as
     docs/specs/spec-{NN}-{slug}/research-output.md, or beside the layout of a brainstorm as
     docs/specs/brainstorm-{NN}-{slug}/research-output.md.
     It resolves ONLY via `type: research` (it has no directory pattern). Live status: draft.
     Terminal statuses: stable (kept as the record behind the spec), superseded/deprecated.
     Write external names and URLs in *italics* or plain link syntax, never as backticked tokens
     that contain a slash.

     Two variants exist. Researched: use the sections below. Declined: when the developer declined
     research at the gate, keep ONLY the frontmatter, the H1, an index table with one row
     (Research declined) and the section below, and delete everything else:

     ## Research declined

     The developer declined web research for this spec at the research gate of /flow:grill. No
     best practices, pitfalls or sources were gathered, so there are no recommendations to decide.
-->

# <Feature or Use-Case> Research

| Section | What it covers |
|---------|----------------|
| [Scope](#scope) | The feature researched, the domains covered, and how decisions are recorded |
| [Business](#business) | Business findings, sources, recommendations and decisions |
| [Product](#product) | Product findings, sources, recommendations and decisions |
| [UX](#ux) | UX findings, sources, recommendations and decisions |
| [Technical / Architecture](#technical--architecture) | Technical findings, sources, recommendations and decisions |
| [Codebase and sources](#codebase-and-sources) | Findings from this codebase, or from documents and repositories the developer named |
| [References](#references) | Every source consulted and the findings it backs |

## Scope

<!-- One short paragraph: the feature or use-case, then which of Business, Product, UX,
     Technical / architecture, and Codebase and sources were researched. Delete the sections of any
     domain that was not researched, and delete its row in the index table. Keep the second
     paragraph below as is. -->

The Decision column starts empty. The interview fills it as each decision is final: `Adopted`, `Dropped`, or `Adopted — <comment>`.

## Business

<!-- One row per finding. 3-6 best practices and 3-6 pitfalls. IDs run BUS-1, BUS-2, ...
     Type is "Best practice" or "Pitfall". Source is a link: [source-domain](URL).
     Recommendation: one line, what this feature should do with the finding.
     Leave the Decision cell empty. -->

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| BUS-1 | <Best practice or Pitfall> | <Finding> | [<source-domain>](<URL>) | <Recommendation> | |

## Product

<!-- Same columns. IDs run PRD-1, PRD-2, ... -->

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| PRD-1 | <Best practice or Pitfall> | <Finding> | [<source-domain>](<URL>) | <Recommendation> | |

## UX

<!-- Same columns. IDs run UX-1, UX-2, ... -->

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| UX-1 | <Best practice or Pitfall> | <Finding> | [<source-domain>](<URL>) | <Recommendation> | |

## Technical / Architecture

<!-- Same columns. IDs run TEC-1, TEC-2, ... -->

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| TEC-1 | <Best practice or Pitfall> | <Finding> | [<source-domain>](<URL>) | <Recommendation> | |

## Codebase and sources

<!-- Findings from this codebase, or from documents and repositories the developer named, such as a
     library that is being evaluated. Same columns. IDs run SRC-1, SRC-2, ...
     Type is "Existing pattern", "Constraint", "Reuse candidate", or "Pitfall".
     Source is a link or a repository path in plain text, with the line when it helps.
     A repository path is written without backticks when it contains a slash. -->

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| SRC-1 | <Existing pattern, Constraint, Reuse candidate, or Pitfall> | <Finding> | <Link or path> | <Recommendation> | |

## References

<!-- Every page consulted, one per line: "[<page title>](<URL>) — findings: <IDs>". -->

- [<Page title>](<URL>) — findings: <IDs>
