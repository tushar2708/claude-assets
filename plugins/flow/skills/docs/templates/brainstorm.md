---
type: brainstorm
title: "<Idea> Brainstorm Layout"
status: draft
tags:
  - brainstorm
  - <tag-2>
# generated: stamped by the authoring command
#   by: <agent/model>
#   at: <ISO-8601 timestamp>
---

<!-- This doc is the layout of an effort that is split into sprints. It is written by the
     /flow:brainstorm skill and kept current by later grill and spec sessions. It is saved as
     docs/specs/brainstorm-{NN}-{slug}/brainstorm-{NN}-{slug}.md, beside research-output.md and the
     sprint specs. NN is the next-of-largest numeric prefix among the spec-<NN>-* and
     brainstorm-<NN>-* folders in docs/specs/, zero-padded.
     It resolves ONLY via `type: brainstorm` (it has no directory pattern). Live status: draft.
     Terminal statuses: stable (every sprint finalized, kept as the record), superseded/deprecated.
     The rules for sections, sprint states, open questions and revisions are in the brainstorm
     skill, file references/layout-format.md. Write external names and URLs in *italics* or plain
     link syntax, never as backticked tokens that contain a slash. -->

# <Idea> Brainstorm Layout

| Section | What it covers |
|---------|----------------|
| [Goal and scope](#goal-and-scope) | What the effort is for, and what it leaves out |
| [High-level design](#high-level-design) | The agreed overall shape, each point with its source |
| [Sprints](#sprints) | Every sprint, its type, its state, and its spec |
| [Sprint dependencies](#sprint-dependencies) | What each sprint passes to the next |
| [Open questions](#open-questions) | Everything not yet decided, and every decision made |
| [Revisions](#revisions) | Decisions that changed after they were made |
| [References](#references) | The research and specs behind this layout |

## Goal and scope

<!-- Two short paragraphs. First: the goal, in the user's words, and the outcome that shows it is
     reached. Second: what is in scope, then what is out of scope, as two short lists. -->

## High-level design

<!-- The shape the interview agreed on: the main parts, the boundaries between them, and the
     decisions already made. One bullet per point. End each bullet with its source: a research
     finding ID such as TEC-2, or "interview". Do not design below the sprint level here. -->

- <Point> (<source>)

## Sprints

<!-- Three or four rows, in dependency order. Type is research, POC, or implementation.
     Goal: one sentence. Exit criteria: what a person can check to say the sprint is done.
     Depends on: sprint numbers, or "none". Status: proposed, grilling, or finalized.
     Spec: a link to each spec that covers the sprint, or "none". -->

| # | Sprint | Type | Goal | Exit criteria | Depends on | Status | Spec |
|---|--------|------|------|---------------|------------|--------|------|
| 1 | <Name> | <research, POC, or implementation> | <Goal> | <Exit criteria> | none | proposed | none |
| 2 | <Name> | <Type> | <Goal> | <Exit criteria> | 1 | proposed | none |

## Sprint dependencies

<!-- One block for each row in the Depends on column. Name the edge, then fill both lines.
     If you cannot say what passes between two sprints, they do not depend on each other:
     remove the edge from the Sprints table. -->

### Sprint 1 → Sprint 2

- **Passes on:** <what sprint 2 takes from sprint 1: a decision, a fact, or an artifact>
- **If it changes:** <what in sprint 2 must be re-checked when that changes>

## Open questions

<!-- One row per question. IDs run Q-1, Q-2, ... and are never reused. Sprint: the number of the
     sprint that must settle it. Why it matters: one line. Status: Open or Resolved.
     Decision: empty while Open. When Resolved, one sentence with the decision. After the sprint
     has a spec, add a link to it at the end of the sentence. A layout that comes from a promoted
     grilling session can start with Resolved rows, one for each decision already made. -->

| ID | Sprint | Question | Why it matters | Status | Decision |
|----|--------|----------|----------------|--------|----------|
| Q-1 | <Sprint number> | <Question> | <Why it matters> | Open | |

## Revisions

<!-- Add a row when a decision that is already Resolved changes. Leave the table with only its
     header row while nothing has changed. -->

| Date | What changed | Was | Now | Files changed |
|------|--------------|-----|-----|---------------|

## References

<!-- The research file and every sprint spec, one per line: "[<title>](<path>) - <what it covers>". -->

- [<Title>](<path>) - <what it covers>
