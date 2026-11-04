# Diagram grammar

Diagrams carry as much of the explanation as the prose, so they follow one fixed grammar across every page and every run. A reader who has seen one of your diagrams can read the next without relearning the shapes or colors.

## Use hand-authored inline SVG — not a diagram library

Write the diagram as inline `<svg>` in the HTML. Do not depend on a runtime library (mermaid, etc.): a library may fail to render, is themed differently each time, and hides the real values. Inline SVG renders everywhere, looks identical across pages, and lets you place exact numbers on edges and nodes. The `assets/style.css` already sizes `svg text`.

## Fixed color and shape vocabulary

Reuse these for the same meaning every time (the CSS tokens match `assets/style.css`):

| Element | Shape | Fill / stroke | Use for |
|---|---|---|---|
| Primary data node | circle | blue `#e8f0fd` / `#2f6fde` | the main entity/record kind |
| Secondary data node | rounded rect | purple `#f0ecfb` / `#7a4fd0` | the other node/record kind (e.g. a document/passage) |
| A relationship | solid line | orange `#e07a1f` | an edge/link between two primary nodes |
| A weak/derived link | dashed line | purple `#7a4fd0` | a secondary connection |
| A highlighted/seed element | circle/rect | red `#fde7e7` / `#c62828` | the thing the current step acts on |
| A result/output | rounded rect | green `#e6f4ea` / `#2e7d32` | what the flow returns |
| A persisted store/graph | rounded rect | amber `#ffe3c2` / `#e07a1f` | an on-disk artifact |
| A process step/stage | rounded rect | slate `#eef0f4` / `#5a5a66` | one control-flow step (a CLI step, an Ansible task, a deploy scope) |
| A decision/branch | diamond (polygon) | yellow `#fff4e0` / `#a35a00` | a branch point (an `if`, a preset/condition that forks the flow) |
| A parallel fan-out | thin bar + fanned arrows | grey `#5a5a66` | steps that run concurrently from one point |
| An external service | rounded rect, 2px double stroke | teal `#e0f3f1` / `#0f766e` | a third-party/cloud system the code calls (App Runner, Cloudflare, Secrets Manager) |
| An actor/role lane | labelled band behind nodes | grey `#f2f2f5` / `#d0d0d8` | the host, role, or service the enclosed steps belong to (a swimlane) |

Keep a tiny legend on any diagram whose colors are not obvious from labels.

## Name the mechanism, label every arrow (C4 rigor)

Every box names **what kind of thing it is**, not just what it does: an Ansible role, a CloudFormation stack, a systemd unit, an HTTP call, a CLI step. Every arrow is **labelled** (what passes, or what triggers the next step) and **unidirectional** — a return is its own labelled arrow, never a double-headed line. A box with no type, or an unlabelled arrow, hides exactly the fact the reader needs.

## Show real values, never placeholders alone

Every node and edge carries a concrete label from the running example: the real id (`entry-9f3c…`), the real number (`weight = 2.0`), the real operation (`P = 0.5 × 3/5 = 0.30`). A diagram of empty boxes teaches nothing. Where an id is long, show a truncated-but-real prefix and say so once.

## The diagram types you will reuse

### 1. The end-to-end pipeline (vertical)

For the landing page / feature overview. Lay stages **top to bottom** so the whole flow fits the page width. Each stage is a box; arrows connect consecutive stages; the box links to the section that explains it (`<a href="…">` around the stage group). Put the core formula or value in each box. If one flow feeds another (e.g. a build step produces an artifact a later step consumes), draw a labeled dashed arrow between them.

```html
<a href="s3-store.html"><rect x="110" y="48" width="400" height="56" rx="8" fill="#e8f0fd" stroke="#2f6fde"/>
  <text x="126" y="72">1. parse the request</text>
  <text x="126" y="92" class="small">str → Request struct (handler.go:40)</text></a>
<line x1="310" y1="104" x2="310" y2="128" stroke="#5a5a66" marker-end="url(#ar)"/>
```

### 2. The record/array diagram

To show exactly what one record, struct, or array slot holds. Draw it as a labeled box with one line per field, and annotate what each field is. For an array, draw indexed cells with the real value in each and the index + label beneath, so "slot i corresponds to element i" is visible, not asserted.

### 3. The node-and-edge diagram

To show how concepts connect (e.g. a record becomes an edge between two other nodes). Draw the nodes with the fixed shapes/colors, label every edge with its kind and weight, and highlight the one element the current step touches.

### 4. The sequence / collaboration diagram (runtime interactions)

To show how separate actors collaborate at runtime for one story — a request, a deploy, a job — when the interesting thing is the **order of calls between components**, not one component's internals. This is the C4 *dynamic* diagram. Draw one lane (actor/role lane) per actor and **number every interaction** (`1`, `2`, `2.1`) so the order is explicit; label each arrow with the call and show the real value it carries; draw a return as its own numbered, labelled arrow. Use it **sparingly** — only where a set of interactions is genuinely complicated or recurring (c4model.com/diagrams/dynamic); a straight-line flow belongs in the pipeline diagram instead.

### 5. The state-transition table (retries, idempotency, resume)

To show behavior that depends on **state and events**, not a straight line — a retry loop, an idempotent step that skips when already done, a checkpoint the process resumes from. Prefer a table with one row per transition and these columns: **State · Trigger (the event) · Guard (the condition) · Next state · Action**. Document the trigger **and** the guard on every transition, not just the state. Pair the table with a small state diagram only when there are ~6 states or fewer; above that, split into independent sub-machines rather than one unreadable diagram.

## Clickable stages

Wrap each pipeline stage in an `<a href="target.html#anchor">` so a reader can jump from the overview to the detail. Confirm every link resolves during Phase 7.

## Responsiveness

Set a `viewBox` and let the SVG scale (`svg { width:100%; height:auto }` is in the stylesheet). Keep diagrams within ~1000 user units wide so they fit a laptop without horizontal scroll; prefer taller-and-narrower over wide for pipelines.
