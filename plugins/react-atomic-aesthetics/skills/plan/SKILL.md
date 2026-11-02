---
name: plan
description: |
  Plan a clean, aesthetically intentional React UI/UX before implementation. Use when:
  (1) Starting a new UI feature, page, or component in a React/Tailwind/shadcn project
  (2) Redesigning existing UI
  (3) Any non-mechanical UI change (anything beyond renames, reference updates, or copy-only edits)
  Maps journeys, analyzes existing patterns for consistency, and produces an implementation plan that complies
  with this plugin's canonical UI rules.
---

# Plan UI

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

This skill plans a React UI/UX change against the plugin's canonical rules before any code is written.

## Step 0 — Read the rules

Call the Skill tool with "ui-rulebook". All planning decisions must comply with its rules. Reference rules by number (A1–A20, B1–B5, Part C, E1–E7, F1–F2).

Also read the canonical planner role at `../../references/roles/architect.md`. It is the sole semantic definition of the planner role.

## Step 1 — Produce a plan before implementation

Do not implement while planning. Obtain approval for the implementation plan before implementation. Do NOT use this skill for bug fixes or for purely mechanical edits (renames, reference updates, copy-only changes).

## Step 2 — Plan the UI change

Use the canonical architect role for this analysis. **Claude Code:** delegate to the named `architect` wrapper; it loads `../../references/roles/architect.md`. **Codex:** read that canonical role file and apply it directly, or give its copied canonical role context to a generic planning worker. **Other hosts:** follow the unsupported-host rule above. Provide the feature goal, target UI project path, and known constraints. The planner will:
1. Read RULES.md.
2. Analyze the existing codebase patterns (component structure, design tokens/theme, spacing rhythm, existing atoms/molecules/organisms, AND any existing asset/image pipeline or motion-timing vocabulary — RULES E7, F1) and state which it will match for consistency, verified by actually reading the relevant files, not assumed.
3. Map the user journey including all four async states (empty, loading, error, success — RULES A16) and accessibility (A18–A19).
4. Define the atomic component hierarchy (RULES B1) and the aesthetic direction: the single deliberate accent discovered from existing tokens (A1–A2, verified against the actual theme file per F2 if the project has 3+ named theme variants), 2–3 type sizes (A5), whitespace-first grouping (A6), depth/signature (A10–A11), and layout-level differentiation (A12).
5. If the feature includes any decorative imagery, illustration, or ambient/background motion, plan it against RULES E1–E2 (what real concept it depicts, how much ornamental intensity the surface earns) and E5–E6 (inspiration provenance disclosure; one consistent generation approach for a coordinated asset set).
6. Produce a prioritized, parallelizable implementation plan with exact files, props interfaces, styling approach (Tailwind + semantic tokens, RULES A3/B3 — one canonical theme stylesheet), lucide-react icons and their aria-labels (A18), any decorative-content accessibility/perf requirements (E3–E4), and per-component acceptance criteria.

## Step 3 — Skip condition

Skip re-running the planning analysis if its findings (existing patterns, tokens, plan) are already in context. Reuse those findings instead of re-analyzing.

## Step 4 — Hand off

Hand the approved plan to implementation-capable agents or the main agent, depending on host capabilities. See the review-ui skill for post-build review. Do not implement inside this skill.
