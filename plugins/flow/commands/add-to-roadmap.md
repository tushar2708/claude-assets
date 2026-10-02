Analyze the current conversation to identify an item that should be documented in `roadmap.md` (repo root) — in ANY of its sections, not just Tech Debt.

> This command is the SOLE GitHub-issue creator in flow: after writing the roadmap entry it creates exactly one GitHub issue for that entry (see Step 4). No other flow command creates issues.

## Step 1: Infer from Context
Extract from the conversation:
- **Project**: Which repo was discussed (smritea, smritea-cloud, etc.)
- **Area**: File path or component mentioned
- **Description**: The technical issue or shortcut identified
- **Impact**: Infer based on discussion tone and scope
- **Effort**: Estimate based on complexity discussed

## Step 2: Clarify with User
Use the AskUserQuestion tool to confirm your inferences:
- Ask about Impact if unclear (High/Medium/Low)
- Ask about Effort if unclear (High/Medium/Low)
- Ask for any additional context needed

## Step 3: Add Entry
Add a row to the appropriate section's table in `roadmap.md` (repo root). There is no separate document.
The entry can go into ANY roadmap section, not just Tech Debt. Each section has its own ID scheme:

roadmap.md sections and their ID schemes:
- "## P0 — Critical"  → ID prefix P0-<n>
- "## Features"  → plain integer <n> (rows count DOWN; use max+1)
- "## Performance Improvements"  → P<n>
- "## Future Enhancements"  → FE<n>
- "## Architecture Refactors"  → A<n>
- "## Ranking Signal Weighting"  → W<n>
- "## Known Gaps / Bugs"  → G<n>
- "## Tech Debt"  → TD<n>
- "## Testing & Sandbox Validation"  → derive the prefix from that section's existing rows at run time

Rule: infer the section from the conversation; if ambiguous, ask the user via AskUserQuestion. Auto-increment
the ID by scanning that section's existing rows for the highest number of its scheme and using the next.
Each section's table header is `| # | Title | Description | Status |`. Keep the whole row on one line; never
put a `|` inside a cell.

1. Determine the target section and auto-increment its ID per the scheme above
2. Insert the new row at the TOP of that section's table (newest first), directly under the header separator row
3. Row format: `| <ID> | **Title** | Description | Status |`
4. In the Description cell, start with `**Date**: <today's date>.`, then put the project and priority level
   (based on Impact) as `**Priority**: <project> / <High|Medium|Low> Priority.`, then `**Area**: <file path
   or component>.`, then the description of the issue, then `**Impact**: <High|Medium|Low>.` and
   `**Effort**: <High|Medium|Low>.` (add `**Details**:` / `**Fix approach**:` text inline if needed; keep
   the whole row on one line, and never use a `|` character inside a cell)
5. Set Status to `Open`

## Step 4: Create the GitHub Issue (this command is the SOLE issue creator in flow)
4. Create exactly ONE GitHub issue (this command is the only issue creator in flow): run `gh issue create` in
   the current repo with --title = the entry Title (strip surrounding `**` markdown), --body = the entry
   Description followed by a line `roadmap-id: <the entry ID>` (exact — `/flow:sync-issues` matches on it),
   and --label derived from the section (P0→priority:P0; Features→feature; Performance Improvements→performance;
   Future Enhancements→enhancement; Architecture Refactors→refactor; Ranking Signal Weighting→ranking;
   Known Gaps / Bugs→bug; Tech Debt→tech-debt; create the label with `gh label create` if missing). Capture the
   printed issue URL. (`gh` runs in the invoking main context, not a subagent.)
5. Append ` **Issue**: <url>.` to the end of that row's Description cell (one line, no `|` inside the cell),
   linking the entry to its issue at creation time.

## Impact Guidelines
- **High**: Causes bugs, blocks features, security risk
- **Medium**: Affects maintainability, has workarounds
- **Low**: Cosmetic, minor inconvenience

## Effort Guidelines
- **High**: >1 day of work
- **Medium**: 2-8 hours
- **Low**: <2 hours

If no tech debt was discussed in the conversation, ask the user to describe the issue they want to track.
