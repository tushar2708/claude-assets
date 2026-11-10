---
plan: "../specs/<plan filename without .md>/<plan filename>"
status: active
---

# Tasks — <plan title>

Plan: [<plan title>](../specs/<plan filename without .md>/<plan filename>)

`roadmap.md` is the Epic registry. This file is the local task tracker.

## Epic: <epic name> — <epic key or local id>

Roadmap: [<epic name>](../../roadmap.md#epic-<anchor>)

| S. no. | Task | Parent Story | Title | Status | Dependencies | Details |
| ---: | --- | --- | --- | --- | --- |
| 1 | Story SF-1 | — | <story title from roadmap> | ⏳ | `none` | [SF-1](#sf-1) |
| 2 | W1.T1 | SF-1 | <task title> | ⏳ | `none` | [W1.T1](#w1-t1) |
| 3 | W1.T2 | SF-1 | <dependent task title> | ⛔ #blocked by #2 | `#2` | [W1.T2](#w1-t2) |

## Wave 1

### <a id="sf-1"></a>Story SF-1 — <story title>

- Status: ⏳
- Epic: <epic name>
- Roadmap row: `<story id>`

<Copy the roadmap Story details verbatim.>

### <a id="w1-t1"></a>Task W1.T1 — <task title>

- Status: ⏳
- Dependencies: `none`
- Agent: `<planned agent>`
- Plan sections: `<exact headings>`
- Shared contracts: `<contract-file path>`

<Copy every planned task field here verbatim.>

#### Done when

<Copy the plan's done-when field verbatim.>

#### Self-check

<Copy the plan's self-check field verbatim.>

### <a id="w1-t2"></a>Task W1.T2 — <dependent task title>

- Status: ⛔ #blocked by #2
- Blocked by: #2

<Copy every remaining planned field here verbatim.>
