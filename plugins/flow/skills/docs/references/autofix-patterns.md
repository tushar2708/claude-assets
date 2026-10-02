# docsmith autofix patterns

Deterministic, mechanical fixes for the findings `validate` reports. Each pattern below names
the check, the exact fix, and when to STOP and ask instead of guessing. Apply these directly —
do not re-derive the fix from first principles each time `validate` reports the same class of
finding.

| Pattern | Check | Fix |
|---------|-------|-----|
| [Missing frontmatter](#missing-frontmatter) | V1 | Add the standard block; category from dir_pattern or explicit `type:` |
| [Missing index table](#missing-index-table) | V1b | Insert the standard table under the H1 |
| [Drift: real stale citation](#drift-real-stale-citation) | V3 | Verify current path, rewrite the citation |
| [Drift: false positive](#drift-false-positive) | V3 | De-backtick, or `$`-prefix env-var pseudo-paths |
| [Coverage: dead glob](#coverage-dead-glob) | V5 | Remove the glob from `extra_gate_paths` once confirmed unused |
| [Decision non-compliance](#decision-non-compliance) | V7 | Numbering/filename fix; section restructure |
| [Concurrent-edit duplication](#concurrent-edit-duplication) | any | Re-read and diff after multi-agent migrations |

## Missing frontmatter

`[FAIL] <doc>: no frontmatter block` — the file has no YAML frontmatter, or it's unparseable.

Fix: add a block matching this shape (copy an existing compliant doc in the project as the
exact style reference — key order, quoting):

```yaml
---
type: <category key or alias>
title: "<derived from the H1>"
status: draft|stable|deprecated|superseded
tags:
  - <1-3 kebab-case tags>
stale_after: <YYYY-MM-DD>   # evergreen categories only: today + categories.<cat>.stale_after_days
generated:
  by: <agent/model>
  at: <ISO-8601 now>
---
```

- `type` must equal a category key (`tutorial`, `how-to`, `reference`, `explanation`,
  `runbook`, `decision`, `plan`, `external`) or one of that category's `type_aliases` in
  `.docsmith/config.json` — check the config, don't guess an alias.
- A file physically outside every category's `dir_patterns` still resolves via an explicit
  `type:` — this is the only way an `external`-category doc resolves, and it's also how you
  tag a file without moving it (see [Coverage: dead glob](#coverage-dead-glob) sibling case:
  moving isn't always required — an explicit `type:` is enough when relocation isn't in scope).
- `decision` and `plan` categories omit `stale_after`.
- Category ambiguous from filename alone → read the doc's actual content before picking.
  Rationale/design-intent content → `explanation`. Exhaustive facts/schema/flags →
  `reference`. Numbered operational steps for an operator under pressure → `runbook`. Records
  one decision with alternatives → `decision`. Genuinely still-open/in-flight work → `plan`
  (terminal, completed work described as a historical record is `explanation` or `reference`
  instead — a `plan` whose work is actually done just accrues a TTL warning for no benefit).

## Missing index table

`missing index table under H1` (V1b, when `validate.require_index_table` is on) — or just
R4 discipline even when the check is off.

Fix: insert directly under the H1, before the first other content:

```markdown
| Section | What it covers |
|---------|----------------|
| [Section Name](#section-name) | One line on what this section covers |
```

One row per H2 in the doc, in order. Anchor = GitHub slug of the heading text (lowercase,
spaces→hyphens, strip everything outside `[a-z0-9-_]`).

## Drift: real stale citation

`cited path '<X>' does not exist` where `<X>` really did move or get renamed.

Fix:
1. Verify the real current location with `find`/`grep`/`ls` — never guess or pattern-match
   off a naming convention.
2. Rewrite the citation to the real path.
3. If the cited thing was genuinely removed (not moved), rewrite the surrounding sentence to
   describe current reality (R1/R2) — do not leave a dead citation or add an "Update:" note.
4. If no current equivalent exists after actually searching, leave
   `<!-- TODO(docsmith): could not verify --> ` inline and flag it in your summary — never
   fabricate a plausible-looking path.

Common project-specific case: a repo flatten/rename (e.g. a `<subdir>/` prefix that used to
hold the whole project got dropped, or a Rust→Go port moved old sources to an `old_rust/`
style archive). Grep the old prefix across `docs/` in one pass to find every doc still citing
it before fixing file-by-file.

## Drift: false positive

`cited path '<X>' does not exist`, but `<X>` was never meant to resolve on disk — it's an
external identifier that merely *looks* path-shaped. The engine's ref extractor
(`docsmith_lib/refs.py`) flags any backtick code-span or link target containing `/` that
either has no file extension or has a recognized code/doc extension — with no exemption for
non-repo identifiers. Recognize this pattern by what `<X>` actually is:

- A third-party package/module import path: `spf13/viper`, `coder/websocket`,
  `glebarez/sqlite`, `google/uuid`.
- A GitHub Action or GitHub repo name used as prose, not a link: `actions/setup-go`, `cli/cli`.
- A generic language idiom mentioned without citing an actual directory in *this* repo:
  `` `internal/` `` used to explain a Go convention when the project has no `internal/` dir.
- A hostname+path describing an external HTTP endpoint without a scheme:
  `api.openai.com/v1/models`.
- A CI-only or build-only output path that never exists in the checked-out tree:
  `dist-bin/`, `dist/`.
- An env-var-prefixed pseudo-path meant as `$VAR` interpolation, not a literal path:
  `GATEWAY_HOME/config.yml`.

Fix, in order of preference:
1. **De-backtick to italics**: `` `spf13/viper` `` → `*spf13/viper*`. Removing the code span
   removes it from ref extraction entirely. Use this for names that are prose, not code.
2. **`$`-prefix env-var pseudo-paths and keep the backticks**: `` `GATEWAY_HOME/x.yml` `` →
   `` `$GATEWAY_HOME/x.yml` ``. The ref extractor's path regex requires the token to *start*
   with `[A-Za-z0-9_@]`; a leading `$` fails that match, so the whole backtick span no longer
   qualifies as a path candidate and the code formatting is preserved. Prefer this over
   de-backticking when the token is genuinely meant to read as code (an env var + suffix).
3. Never use `path_drift_severity`/`symbol_drift_severity` config overrides to silence these —
   that hides real drift for every doc, not just the false positive.

## Coverage: dead glob

`pattern matches no files` (V5) for an `extra_gate_paths` entry.

Fix: confirm the convention genuinely isn't used in this project (e.g. no per-subsystem
`docs/*/README.md` files exist and the project's actual structure doesn't call for any), then
remove that glob from `extra_gate_paths` in `.docsmith/config.json`. This is a mechanical
dead-config cleanup — the array element pointed at something this project's layout never
produces — not a policy change, and doesn't need the same review weight as changing what a
category means. If the convention IS meant to exist but just hasn't been created yet, create
one qualifying file instead of deleting the gate.

## Decision non-compliance

V7 findings on a `decision`-category doc: filename pattern, duplicate numbers, or missing
required sections (`Status`, `Context`, `Options Considered` with ≥2 `###` subsections,
`Decision`, `Consequences`).

- **Filename/numbering mismatch against pre-existing ADRs** (e.g. the project already has
  `ADR-0001.md`..`ADR-0012.md` — 4 digits — but `categories.decision.numbering.digits` is the
  engine default of 3): prefer changing `numbering.digits` in config to match the established
  convention over renumbering every existing file. If the existing files ALSO lack the
  required kebab-slug suffix, both a config fix (if needed) and a rename (via `git mv`, never
  Read+Write) are required — derive the slug from each ADR's own title.
- **Missing `## Options Considered` with ≥2 subsections**: if the doc only has a rejected
  "## Alternatives considered" bullet (a common pre-docsmith shape), synthesize the second
  option from the option that WAS actually chosen — pull its rationale out of the existing
  `## Decision` section into its own `### Option N: <chosen approach>` with **Pros:**/**Cons:**
  bullets. Never invent a fictional alternative that wasn't actually considered.
- Body `## Status` text maps to frontmatter `status`: Proposed→`draft`, Accepted→`stable`,
  Superseded→`superseded`, Rejected→`deprecated`. A "Partially accepted" or similar nuanced
  status still maps to `stable` in frontmatter (the four-value enum has no partial state) —
  keep the nuance in the body `## Status` section text itself.
- Preserve every substantive sentence of reasoning when restructuring — this is a reformat
  (headings, structure) not a rewrite of content, and decisions are immutable in substance.

## Concurrent-edit duplication

When a doc migration spans multiple parallel agents/forks (e.g. moving a whole `docs/site/`
tree while other agents touch adjacent top-level docs), two writers can land edits to the same
file in the same window, silently duplicating a section (a table appears twice, once with
stale link targets). Symptom: `validate` reports link-target failures pointing at old,
already-fixed-elsewhere filenames even though you fixed that exact link. Fix: re-read the
whole file (not just the diff you expect) and diff-scan for a duplicated heading or table
before trusting a single targeted edit; deduplicate, keeping the version with corrected links.
