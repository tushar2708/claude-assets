# docsmith Categories

| Category | Purpose in one line |
|----------|---------------------|
| [tutorial](#tutorial) | Teach a newcomer by building something end to end |
| [how-to](#how-to) | Get a task done: goal plus numbered steps |
| [reference](#reference) | Look up facts: APIs, schemas, flags, constants |
| [explanation](#explanation) | Understand the current design and why it is this way |
| [runbook](#runbook) | Operate under pressure: terse steps plus rollback |
| [decision](#decision) | Record one decision immutably (ADR-NNN) |
| [plan](#plan) | Drive work that is happening now; ephemeral |
| [external](#external) | Public-facing, non-code content |

Category names, `type_aliases`, `dir_patterns`, numbering, and TTLs all come from the
project's `.docsmith/config.json` — a project may rename or re-home any category.
Defaults below are the engine defaults.

## tutorial

- **Purpose**: learning-oriented — take a beginner through building something real, one
  observable step at a time, ending with "what you built".
- **Vs neighbors**: a tutorial teaches through a guided project (the author controls the
  path); a how-to solves one task for someone who already knows the system.
- **Frontmatter**: `type: tutorial` (default alias `Tutorial`); `stale_after` = today + 180.
- **Lifecycle**: evergreen — rewrite invalidated sections wholesale on every update.
- **Naming**: stable unnumbered kebab-case name (e.g. `getting-started.md`) under
  `docs/tutorials/`.

## how-to

- **Purpose**: task-oriented — one goal, numbered steps that accomplish it, minimal context.
- **Vs neighbors**: a how-to serves a developer at their desk with time to read; a runbook
  serves an operator during an incident (terse, zero explanation). If the reader is learning
  rather than doing, it is a tutorial.
- **Frontmatter**: `type: how-to` (default alias `Guide`); `stale_after` = today + 120.
- **Lifecycle**: evergreen.
- **Naming**: stable unnumbered kebab-case verb phrase (e.g. `rotate-api-keys.md`) under
  `docs/how-to/`.

## reference

- **Purpose**: information-oriented — exhaustive, structured facts: API surfaces, schemas,
  config keys, CLI flags, constants. Body tables shine here (comparable records).
- **Vs neighbors**: reference states WHAT IS; explanation covers HOW and WHY. Never mix
  rationale into a reference doc — link to the explanation or decision instead.
- **Frontmatter**: `type: reference` (default aliases `Reference`, `API`, `Spec`, `Index`,
  `Priming`); `stale_after` = today + 90.
- **Lifecycle**: evergreen; the shortest staleness window because facts drift fastest.
- **Naming**: stable unnumbered kebab-case topic name under `docs/reference/`.

## explanation

- **Purpose**: understanding-oriented — overview, how it works, and the design rationale for
  the CURRENT design. Historical "why we changed" narratives belong in decision records.
- **Vs neighbors**: if the reader will execute steps, it is a how-to; if they will look up a
  value, it is reference; if the content records a choice between options, it is a decision.
- **Frontmatter**: `type: explanation` (default alias `Overview`); `stale_after` = today + 240.
- **Lifecycle**: evergreen; the longest evergreen window because architecture moves slowest.
- **Naming**: stable unnumbered kebab-case concept name under `docs/explanation/`.

## runbook

- **Purpose**: operations procedure — preconditions, terse numbered steps, rollback.
  Zero explanation in the body; link out to explanation docs for background.
- **Vs neighbors**: a runbook is executed under pressure; if the procedure needs context to
  be understood, that context is a linked explanation, not inline prose.
- **Frontmatter**: `type: runbook` (default alias `Runbook`); `stale_after` = today + 90.
- **Lifecycle**: evergreen; must be re-verified against the live system when refreshed.
- **Naming**: stable unnumbered kebab-case action name (e.g. `restart-ingest.md`) under
  `docs/runbooks/`.

## decision

- **Purpose**: record one architecturally significant decision — context, options with
  pros/cons, the choice, and its consequences — at the moment it was made.
- **Vs neighbors**: explanation describes the current design; a decision record explains why
  one option beat the others at a point in time. Decisions are the ledger evergreen docs
  lean on when they drop history.
- **Frontmatter**: `type: decision` (default alias `ADR`). Body `## Status` maps to the
  frontmatter `status` field: Proposed → `draft`, Accepted → `stable`,
  Superseded → `superseded`, Rejected / dead-end → `deprecated`.
  Optional `supersedes` / `superseded_by` fields carry the chain (see below). No `stale_after`.
- **Lifecycle**: **immutable supersede-chain** — accepted decisions are never edited in
  substance. To change course, write a NEW numbered decision and link the two:
  set `supersedes: <old file>` on the new record and `superseded_by: <new file>` plus
  `status: superseded` (frontmatter) / `Superseded` (body) on the old one. Those status and
  link fields are the ONLY permitted edits to the old record.
- **Naming**: `ADR-{NNN}-{slug}.md` — prefix and digit count come from the config's
  `categories.decision.numbering` (`prefix`/`digits`, default `ADR-`/3); the next number is
  max(existing) + 1, zero-padded. The slug must be kebab-case starting with a letter or
  digit (the validator enforces the full pattern, uniqueness of numbers, and the required
  H2 sections: Status, Context, Options Considered with at least 2 `###` options, Decision,
  Consequences). Default directory `docs/decisions/`.

## plan

- **Purpose**: drive work that is happening now — stages, tasks, subtasks, a tracker table
  with ❌/⚠️/✅ statuses, and mandatory review stages.
- **Vs neighbors**: a plan is disposable by design; anything in it worth keeping forever
  should graduate into an evergreen doc or a decision record before the plan is archived.
- **Frontmatter**: `type: plan` (default alias `Plan`); `status: draft` while live, then a
  terminal status (`stable` executed-and-kept, `superseded`/`deprecated` replaced or
  abandoned). No `stale_after`.
- **Lifecycle**: **ephemeral TTL + archive** — after the category's `ttl_days` (default 45)
  past terminal status, the file belongs in the category's `archive_dir` (default
  `docs/plans/archive/`). The validator's plan-ttl check warns on any live (`draft`/`stable`)
  plan whose last commit is older than the TTL: move it to the archive or mark it superseded.
- **Naming — numbered prefix (apply without being asked)**: plans get a `{NN}-{slug}.md`
  name. If the doc is to be created in plans/ todos/ or any similar directory that has
  numbered-prefixed files, always add your file with a prefix of next-of-largest existing
  prefix (eg. 01-<>.md, 07-<>.md, 11-<>.md, etc). Do it without asking, or being asked
  (unless explicitly asked not to do this).
  - When the correct target directory is `docs/plan/tasks/`, create the file there with the
    next available numbered prefix and no other name collision.
  - To find the largest existing numeric prefix, use `ls <dir>/ | sort -n | tail -5` and
    read the last entry's prefix. NEVER use `grep -P` (not available on macOS). NEVER use
    alphabetical sort, which puts `99` after `100`. Always use numeric sort (`sort -n`).

## external

- **Purpose**: public-facing, non-code content — product descriptions, landing/marketing
  copy, feature announcements written for people who will never see the codebase.
- **Vs neighbors**: everything else in this table may cite code; external docs must not.
  No code refs, no internals, no architecture — feature-oriented language only.
- **Frontmatter**: `type: external` is MANDATORY — the category has no `dir_patterns` by
  default, so the frontmatter type is the only way a doc resolves to it.
  `stale_after` = today + 365.
- **Lifecycle**: evergreen, but excluded from the doc-site build (`site.include: false`).
- **Naming**: stable unnumbered kebab-case name; location is the project's choice (often
  outside `docs/`).
