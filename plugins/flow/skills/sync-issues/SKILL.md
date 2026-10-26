---
name: sync-issues
description: Reconcile roadmap.md epic sections with the declared tracker. Backfill items, repair links, sync status. Never duplicates an item or guesses ownership.
disable-model-invocation: true
---

# sync-issues

Reconcile `roadmap.md` (repo root) with the declared tracker's issues. This skill reconciles; `/flow:add-to-roadmap` is the sole issue creator.

## Step 0: Resolve the Issue Tracker

Read `${CLAUDE_PLUGIN_ROOT}/skills/sync-issues/references/issue-tracker.md` first.
1. Run its part C on every run, before any other step.
2. On skip, stop and change nothing.
3. Read entries only from `## Epic:` sections (part D).
4. Treat a legacy `**Epic**:` field as an epic link, never as the entry's issue.

## Matching rule (never guess)

Match an entry to its item in this order:
1. the key in the tracker column (part E), else
2. the legacy `**Issue**:` URL, else
3. the exact `roadmap-id:` marker line in an item body (Find by marker, part F).

No signal: the entry is unlinked. Never fuzzy-match on title.

## Operations

Use the part F and G operations.

1. **Backfill** — for an unlinked entry, create its item per `/flow:add-to-roadmap` (parts D, E).
   - Write the tracker column. Replace a `TBD` in `#` with the key.
   - Create items only for existing unlinked rows. Never add a new entry.
2. **Repair links** — matched entry without a tracker column: write the column. Keep the old `#`.
   - A listed item (List items, part F) that matches no entry: report it. Never close it.
3. **Sync status** — set each item's state (Set state) from the entry's Status:
   - `Open`/`Planned`/`Pending`/`Deferred` → open (reopen if closed).
   - `Done`/`Closed` → close.
   - GitHub or Asana: also set the label per part D.
   - Report every change.

## Report

Print counts: backfilled, link-repaired, status-synced, and orphaned items.
