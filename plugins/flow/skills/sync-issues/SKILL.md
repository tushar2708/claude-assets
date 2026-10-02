---
name: sync-issues
description: Reconcile roadmap.md with GitHub issues — backfill missing issues, repair entry↔issue links, and sync labels/status. Never creates a duplicate issue; never guesses ownership.
disable-model-invocation: true
---

# sync-issues

Reconcile `roadmap.md` (repo root) with the repository's GitHub issues. This skill is a RECONCILER, not the primary creator — `/flow:add-to-roadmap` is the sole issue creator.

## Matching rule (never guess)

Every roadmap entry that already has an issue carries an inline `**Issue**: <url>.` field (written by `/flow:add-to-roadmap`), and the issue body carries a `roadmap-id: <ID>` marker line. Match an entry to its issue by:
1. the `**Issue**:` URL on the entry, else
2. the `roadmap-id:` marker in an issue body.

Because the URL is written onto the entry at creation time, this reconciler NEVER guesses which issue belongs to which entry. If neither signal is present, treat the entry as unlinked — never fuzzy-match on title.

## Operations

1. **Backfill** — for a roadmap entry with NO `**Issue**:` link and NO matching `roadmap-id:` issue, create one issue using the exact `/flow:add-to-roadmap` creation rule (title from the entry, body + `roadmap-id: <ID>` marker, label from the section) and write the URL back into the entry. This is the only case where sync-issues creates an issue, and only for already-existing unlinked roadmap rows — never a brand-new entry.
2. **Repair links** — where an entry's `**Issue**:` URL is missing but a `roadmap-id:` issue exists, write the URL back onto the entry. Where an issue exists for an ID no longer in `roadmap.md`, report it (do not auto-close).
3. **Sync labels/status** — align each issue's label with its section (same section→label map as `/flow:add-to-roadmap`) and reflect the entry's Status: `Open`/`Planned`/`Pending`/`Deferred` → issue stays OPEN; `Done`/`Closed` → close the issue. Report every change.

All GitHub reads/writes use `gh` (issue list/create/edit, label) in the current repo; `gh` runs in the invoking main context.

## Report

Print counts of: backfilled, link-repaired, label/status-synced, and orphaned-issue entries.
