# docsmith Writing Rules (R1-R12)

| Rule | Statement |
|------|-----------|
| [R1](#r1-current-state-only) | Docs describe current state only; no changelogs or dated notes |
| [R2](#r2-rewrite-invalidated-sections-wholesale) | Rewrite invalidated sections wholesale, never patch around them |
| [R3](#r3-claims-cite-real-code-refs) | Every code claim cites a real `path` or `path#Symbol` in backticks |
| [R4](#r4-table-as-index) | Every doc opens with an index table right under the H1 |
| [R5](#r5-layer-cake-headings) | Descriptive, front-loaded headings; H2/H3 only |
| [R6](#r6-progressive-disclosure) | Defer rare-case detail out of the main flow |
| [R7](#r7-body-tables-for-records-only) | Body tables only for comparable records with terse cells |
| [R8](#r8-mermaid-only-structural-diagrams) | Mermaid only, structural only, C4 L1/L2 altitude |
| [R9](#r9-preserve-visuals-on-update) | Never degrade or drop existing diagrams when updating |
| [R10](#r10-no-empty-scaffolds) | Structure only where content exists |
| [R11](#r11-readme-audience-rule) | READMEs are external-user-facing only |
| [R12](#r12-every-word-earns-its-place) | To-the-point and precise; cut filler |
| [Frontmatter contract](#frontmatter-contract) | The exact fields and allowed values |

## R1: current-state only

Docs describe the system as it is today; git history and decision records are the only ledger —
never append a changelog section, an "Update:" note, or a dated paragraph.

- Wrong: `Update (2026-03-01): the queue is now Redis-backed.`
- Right: `The queue is Redis-backed.` (the old sentence is gone entirely)

## R2: rewrite invalidated sections wholesale

When a change invalidates any sentence in a section, rewrite the whole section as if authored
today — the urge to append is the signal to restructure.

- Wrong: leaving a stale paragraph and adding `Note: the above no longer applies since v2.`
- Right: replacing the section body so no sentence describes a former state.

## R3: claims cite real code refs

Every factual claim about code cites a repo-relative `path` or `path#Symbol` in backticks
(or as a markdown link target); the engine's drift check resolves each citation.

- Wrong: `The dispatcher lives in the main file.` (nothing machine-checkable)
- Right: ``The dispatcher lives in `src/main.go#HandleThing`.``

Exact syntax the engine parses:

1. The ref must sit in an inline code span (single backticks) or be a markdown link target.
   Refs inside fenced code blocks are ignored — they are NOT checked.
2. Path charset: letters, digits, `_`, `.`, `@`, `/`, `-`; the first character must be a
   letter, digit, `_`, or `@`. No spaces; no URLs (`http...`, `mailto:` are skipped).
3. A candidate only counts as a path when it contains a `/` OR ends with a file extension
   (a trailing `.` + letters/digits, e.g. `.go`, `.py`).
4. The optional `#Symbol` suffix (one `#`, then the symbol) must occur as a whole word in
   the target file, or the check reports symbol drift.

## R4: table-as-index

Every doc opens with a glanceable index table that summarizes the document and links to every
section below it. The validator's window is 40 lines after the H1 — put the table directly
under the H1, before any prose.

- Header: `| Section | What it covers |`
- One row per H2, in document order, each linking `[Section Name](#anchor)`
- Anchors are GitHub-slugged: lowercase, spaces to `-`, strip every character outside
  `a-z`, `0-9`, `-`, `_` (the link check verifies fragments against real headings)

Wrong: opening with three paragraphs of prose and burying a table mid-document.
Right: H1, index table, then the body (prose, diagrams, and body tables where apt).

## R5: layer-cake headings

Headings are descriptive and front-loaded — a reader knows what a section holds without
reading it — and nest to H2/H3 only.

- Wrong: `## Miscellaneous`, `#### Deep subsection`
- Right: `## Quota Enforcement Flow`, `### Redis counter keys`

## R6: progressive disclosure

Keep rare-case or deep detail out of the main flow — defer it to a late section (linked from
the index table) or a `<details>` collapsible, so the common path reads uninterrupted.

- Wrong: 40 lines of edge-case handling in the middle of the happy-path walkthrough.
- Right: the happy path in its section; `## Edge cases` as its own linked section.

## R7: body tables for records only

Tables in the body only for homogeneous, comparable records with terse cells — never
multi-sentence cells, never a table as a container for prose.

- Wrong: a two-column table whose right column holds paragraphs of explanation.
- Right: prose paragraphs; or a table of short, directly comparable facts.

## R8: mermaid-only structural diagrams

Diagrams are mermaid only, and only when they encode structure or flow that text cannot;
keep C4 context/container (L1/L2) altitude — never code-level, never decorative.

- Wrong: a mermaid class diagram mirroring every struct field of one package.
- Right: a container diagram showing two services and the HTTP bridge between them.

## R9: preserve visuals on update

When updating a doc, never degrade or drop existing diagrams, box drawings, flowcharts, or
any other visual elements to save effort — update them so they stay true.

- Wrong: replacing a stale mermaid flow with a one-line prose summary.
- Right: editing the mermaid nodes and edges so the flow matches the current code.

## R10: no empty scaffolds

Create structure only where content exists — delete template sections you have nothing to
say in; never ship placeholder headings.

- Wrong: shipping `## Monitoring` followed by `TBD`.
- Right: omitting the section; add it back the day there is monitoring content.

## R11: README audience rule

Every README.md is external-user-facing only — the what, why, and how of USING the project
(install, commands, configuration, public behavior); internal implementation detail belongs
in CLAUDE.md / AGENTS.md, never in a README.

- Wrong: a README section explaining why the package is CommonJS instead of ESM.
- Right: that rationale in the package's AGENTS.md; the README documents commands and options.

## R12: every word earns its place

Docs are to-the-point and precise — cut filler, hedges, and repetition; when a line runs
long, move the detail into its own section and link it from the index table.

- Wrong: `It should be noted that, generally speaking, the service will usually retry.`
- Right: `The service retries 3 times.`

## Frontmatter contract

Every governed doc starts with a YAML block at line 1 (`---` ... `---`) with these fields:

| Field | Authoring convention | Engine enforcement |
|-------|----------------------|--------------------|
| `type` | always set; the category key or one of its `type_aliases` | must resolve to a configured category (dir_patterns also resolve by location) — else error |
| `title` | always set; the doc's human title | non-empty string required — else error |
| `status` | always set; `draft` on creation | when present, must be one of `draft`, `stable`, `deprecated`, `superseded` |
| `tags` | 2-4 topical tags, YAML block list (never inline `[a, b]`) | when present, must be a YAML list |
| `stale_after` | evergreen docs: today + the category's `stale_after_days`; refresh on every substantive update | when present, must be `YYYY-MM-DD`; a past date warns "document is stale" |
| `generated` | set/update whenever an agent authors or updates the doc | when present, must be a mapping with a non-empty string `by` and an ISO-8601 `at` |

Decision docs additionally use optional `supersedes` / `superseded_by` fields (see
`references/categories.md`); decision and plan docs omit `stale_after` (their lifecycles are
governed by the supersede chain and the plan TTL, not a staleness date).
