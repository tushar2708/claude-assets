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

Keep a tiny legend on any diagram whose colors are not obvious from labels.

## Show real values, never placeholders alone

Every node and edge carries a concrete label from the running example: the real id (`entry-9f3c…`), the real number (`weight = 2.0`), the real operation (`P = 0.5 × 3/5 = 0.30`). A diagram of empty boxes teaches nothing. Where an id is long, show a truncated-but-real prefix and say so once.

## The three diagram types you will reuse

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

## Clickable stages

Wrap each pipeline stage in an `<a href="target.html#anchor">` so a reader can jump from the overview to the detail. Confirm every link resolves during Phase 7.

## Responsiveness

Set a `viewBox` and let the SVG scale (`svg { width:100%; height:auto }` is in the stylesheet). Keep diagrams within ~1000 user units wide so they fit a laptop without horizontal scroll; prefer taller-and-narrower over wide for pipelines.
