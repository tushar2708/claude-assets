---
type: plan
title: "<Plan Title>"
status: draft
tags:
  - plan
  - <tag-2>
# generated: stamped by the authoring command
#   by: <agent/model>
#   at: <ISO-8601 timestamp>
---

<!-- This doc is ephemeral: after the category's ttl_days (default 45) past terminal status
     it belongs in the category's archive_dir (default docs/plans/archive/). Terminal
     statuses: stable (executed, kept as record), superseded/deprecated (replaced/abandoned).
     File name gets a numbered prefix: {NN}-{slug}.md, next-of-largest existing prefix. -->

# Plan: <Title>

| Section | What it covers |
|---------|----------------|
| [Tracker](#tracker) | Every stage/task/subtask with live status |
| [Details](#details) | Per-stage context the tracker rows link to |

> **Progress Tracking**: Mark items as you work:
> - ❌ = Not started
> - ⚠️ = In progress / Partially done
> - ✅ = Complete

## Tracker

| ID | Item | Status | Est. | Notes |
|----|------|--------|------|-------|
| **1** | **Stage: <Name>** | ❌ | X days | |
| 1.1 | Task: <Name> | ❌ | X days | |
| 1.1.1 | <Subtask description> | ❌ | Xhr | |
| 1.1.2 | <Subtask description> | ❌ | Xhr | |
| 1.2 | Task: <Name> | ❌ | X days | |
| 1.2.1 | <Subtask description> | ❌ | Xhr | |
| **1-R** | **Review: Stage 1** | ❌ | 0.5d | |
| 1-R.1 | Verify deliverables | ❌ | | |
| 1-R.2 | Tests passing | ❌ | | |
| 1-R.3 | Docs updated | ❌ | | |
| **2** | **Stage: <Name>** | ❌ | X days | Needs 1-R ✅ |
| 2.1 | Task: <Name> | ❌ | X days | |
| 2.1.1 | <Subtask description> | ❌ | Xhr | |

## Details

### Stage 1: <Name>

**1.1 <Task Name>** — <!-- brief context only when a tracker row needs more than 1-2 lines -->

**1.2 <Task Name>** — <!-- headings stay at H2/H3 (R5); tasks are bold entries under their stage -->

### Stage 1-R: Review

- Verify all Stage 1 deliverables
- Confirm tests passing
- Update documentation
- Confirm ready for Stage 2

### Stage 2: <Name>
