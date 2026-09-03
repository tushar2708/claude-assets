---
name: docsmith
description: Deterministic documentation governance for any project. Use when writing or updating technical documentation of any kind, processing "[docsmith] update ..." documentation tasks from the task queue, checking documentation freshness or staleness, writing ADRs / decision records, plans, runbooks, tutorials, how-tos, reference or explanation docs, governing README content, building or publishing the doc site, maintaining docmap.json or anything under .docsmith/, or whenever the user or a hook mentions "docsmith".
---

# docsmith

| Section | What it covers |
|---------|----------------|
| [What docsmith is](#what-docsmith-is) | Scope and where per-project state lives |
| [Categories](#categories) | The 8 doc categories, lifecycles, and templates |
| [Evergreen writing rules](#evergreen-writing-rules) | Condensed R-rules for all doc work |
| [CLI](#cli) | Subcommands, engine locations, exit codes |
| [State files](#state-files) | config.json / docmap.json / state.json |
| [Doc-task protocol](#doc-task-protocol) | The task-queue rules the hook enforces |
| [Maintaining docmap.json](#maintaining-docmapjson) | Keeping the code-to-doc map current |
| [Fixing validate findings](#fixing-validate-findings) | Apply known fixes mechanically, no re-analysis |
| [Testing](#testing) | Running the engine test suite |

## What docsmith is

Deterministic, config-driven documentation governance: category templates, evergreen writing
rules, and a Python engine (validate / score / collect / scaffold) with no LLM calls. Per-project
state lives in `.docsmith/`: `config.json` (human-reviewed), `docmap.json`
(agent-maintained), `state.json` (machine-only — never hand-edit). The skill and its commands
write ONLY at project level; they never modify user-level or machine-global state.

## Categories

| Category | Lifecycle | Mutability | Template | Scored |
|----------|-----------|------------|----------|--------|
| tutorial | evergreen | rewrite invalidated sections in place | tutorial.md | yes |
| how-to | evergreen | rewrite invalidated sections in place | how-to.md | yes |
| reference | evergreen | rewrite invalidated sections in place | reference.md | yes |
| explanation | evergreen | rewrite invalidated sections in place | explanation.md | yes |
| runbook | evergreen | rewrite invalidated sections in place | runbook.md | yes |
| decision | immutable | never edited in substance — supersede with a new numbered ADR-NNN | decision.md | no |
| plan | ephemeral | editable while live; archived after ttl_days past terminal status | plan.md | no |
| external | evergreen | rewrite in place; public-facing, non-code, skipped by the doc site | external.md | yes |

Rules bind to the **lifecycle**, not the name: projects may rename categories in their
`.docsmith/config.json` (via `type_aliases` and `dir_patterns`); the engine resolves each
doc to a category and applies that category's lifecycle rules. Per-category guidance (purpose,
neighbors, naming, supersede chains): `references/categories.md`.

## Evergreen writing rules

Condensed from `references/rules.md` (R1-R12 — read it before writing any doc):

1. Docs describe CURRENT STATE only. Git and decision records are the ledger — never append
   a changelog, "Update:" note, or dated paragraph.
2. When a change invalidates a sentence, rewrite the whole section as if authored today.
   The urge to append is the signal to restructure.
3. Every claim about code cites a real repo path or `path#Symbol` in backticks — the engine
   resolves these and flags drift.
4. Every doc opens with an index table right under the H1: `| Section | What it covers |`,
   one row per H2, `[Section](#anchor)` links.
5. Body tables only for homogeneous comparable records; terse cells, never prose in cells.
6. Diagrams: mermaid only, and only when they encode structure/flow that text cannot
   (C4 context/container altitude, never code-level). Never degrade or drop existing visuals.
7. READMEs are external-user-facing only; internal detail goes to CLAUDE.md / AGENTS.md.
8. No empty scaffolds; every word must earn its place.

## CLI

| Subcommand | Purpose |
|------------|---------|
| `validate` | Run checks V1-V7 (frontmatter, links, drift, docmap, coverage, plan-ttl, decisions) |
| `score` | Score evergreen doc freshness (age/ttl/drift weighted; default threshold 70) |
| `collect` | Doc-site pipeline (render, build, serve, check, clean, package, publish, deploy) |
| `scaffold` | Bootstrap a project: config, docmap, vendored engine, hook, pre-commit wiring |
| `hook-check` | (hidden) Gate one edited file against the docmap — used by the PostToolUse hook |

Inside a scaffolded project, run the vendored engine:
`uv run .docsmith/engine/docsmith.py <subcommand>`. The skill master copy is
`${CLAUDE_SKILL_DIR}/scripts/docsmith.py`; refresh a project's vendored copy with
`scaffold --sync-engine`. Exit codes: 0 pass, 1 errors found / threshold failed,
2 internal error, 3 config not found.

## Link handling (collect / doc-site build)

The `collect` link transform classifies every relative Markdown link before the strict
MkDocs build, so the build fails ONLY on broken links to other DOCUMENTS — never on links
to code. The three classes:

- **Link to a collected doc** → repointed to that doc's in-site page (kept as a working
  link), even when the flattened `autogen/docs/` tree renamed/moved it.
- **Link to a Markdown/doc target** (`.md` / `.markdown` / `.mdx`) that exists nowhere → a
  genuinely broken document link: left in place so `mkdocs --strict` fails, and reported as
  an `unresolved document link`. This is the ONLY link class that fails the build.
- **Link to anything else** — source code (`.go`, `.py`, `.jinja2`, …), config, an
  extensionless path, or a planning target not written yet — is a NON-document reference:
  it is **de-linked** in the collected copy (visible text kept, the `[..](..)` wrapper
  dropped) so the build never errors on it. The ORIGINAL source markdown is untouched, so it
  stays a real, clickable relative link in the repo / GitHub / IDE view (a static site cannot
  serve on-disk code, so these render as plain text in the built HTML — that is intended).

Fixing a failing build: an `unresolved document link` / mkdocs "not found" error is ALWAYS a
broken link to another **document** — fix the doc→doc path or the missing doc. NEVER convert
or delete a code/config reference to satisfy the build; those are skipped by design and can
never be the cause of a link failure.

## State files

`config.json` — the project's contract (categories, profile, validators); humans review changes.
`docmap.json` — the code-to-doc map; agents maintain it as docs are authored (see below).
`state.json` — score cache written by `score --update-state`; machine-only, gitignored,
never hand-edit.

## Doc-task protocol

The project's PostToolUse hook fires when you edit code mapped in `docmap.json`. Follow its
task-queue protocol exactly:

1. If a task titled "[docsmith] update <doc path>" already exists in your task list, update its
   description to also cover this change. Otherwise create ONE task NOW, titled
   "[docsmith] update <doc path>", with a body listing: the code file you just edited and
   what changed (one line).
2. Do NOT write documentation now. Create the task, then IMMEDIATELY return to the work
   you were doing.
3. Before committing, offer the user to run /docsmith:update-docs to process pending doc tasks.

Skip entirely if your change is trivial (formatting, comments, renames with no behavior change).

## Maintaining docmap.json

- When you author a doc that documents code, add its code-to-doc mapping yourself: keys are
  source file paths or directory prefixes ending in `/`; values are lists of
  `{"path": "<doc>", "reason": "<one line>", "message": "<optional custom instructions>"}`.
- When you create new source directories, check the map covers them; extend it when any doc
  describes them.
- `validate` (V4) errors on map keys or doc paths that no longer exist — fix the map entries,
  do not delete the coverage.

## Fixing validate findings

`validate` findings fall into a small, closed set of recurring shapes — missing frontmatter,
a missing index table, a stale citation, a citation that only *looks* like a repo path,
a dead `extra_gate_paths` glob, or a decision doc that doesn't match the ADR template. Look
up the finding's shape in `references/autofix-patterns.md` and apply that fix directly —
don't re-derive the fix from scratch or stop to explain the finding before fixing it. Ask
first only when a fix in that reference explicitly says to (a genuinely unverifiable
citation, a category call that depends on reading the doc's content, an ADR
digit-count/renumbering choice with no established convention to follow). The
`/docsmith:fix-findings` command runs this end to end.

## Testing

Engine or content changes must keep the suite green:
`bash ${CLAUDE_SKILL_DIR}/scripts/run_tests.sh`
