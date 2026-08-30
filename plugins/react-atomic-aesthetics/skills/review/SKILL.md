---
name: review
description: |
  Review an existing or just-built React UI for clean, intentional UI/UX against this plugin's canonical rules.
  Use when:
  (1) Auditing a React screen/component for visual quality and consistency
  (2) Checking a just-implemented UI before calling it done
  (3) Asked to "review the UI", "does this look generic", or "check the frontend aesthetics"
  Audits against RULES.md (aesthetics, atomic structure, accessibility) and reports concrete findings.
---

# Review UI

This skill audits a React UI against the plugin's canonical rules and reports concrete, actionable findings.

## Step 0 — Read the rules

Read ${CLAUDE_PLUGIN_ROOT}/RULES.md. Judge the UI against it; cite the specific rule number for every finding.

## Step 1 — Gather the rendered UI

View the UI rendered, not just the source (run/preview it, or screenshot it). Aesthetic quality (RULES A20) cannot be judged from source alone.

## Step 2 — Audit against each rule group

For the target component(s)/screen, check and record a pass/fail with the rule number for each:
- Color & tokens: no default Tailwind named colors as accent (A1); one deliberate accent used sparingly (A2); all color via semantic tokens, no hardcoded hex (A3).
- Typography: real type pairing, not default sans (A4); only 2–3 type sizes (A5).
- Hierarchy/spacing: whitespace-first, containers only where needed (A6); most-important element gets most space (A7); ≤3 contrast levels (A8); spacing scale tokens, no ad-hoc px (A9).
- Depth/signature: subtle depth cues, sparingly (A10); at least one signature detail (A11); layout-level differentiation, not just color (A12).
- Motion: functional-only (A13); scaled to action weight (A14); CSS/Tailwind default (A15).
- States: empty/loading/error/success all designed (A16); skeletons not bare spinners (A17).
- Accessibility: icon-only controls have aria-label/sr-only (A18); keyboard + WCAG-AA in every theme (A19).
- Structure: correct atomic classification (B1); props interface, import order, state boundaries, cn() (B2); Tailwind + shadcn/ui, no CSS Modules/styled-components (B3); INDEX.md updated (B5).

## Step 3 — Report

Produce a findings list. For each finding: the rule number, the specific location (file + element), what fails, and the concrete fix. Rank by severity (accessibility and broken states first). Never let good aesthetics mask a real usability defect — call out any usability defect explicitly even if the surface looks polished (RULES A20).

## Step 4 — Optional fix handoff

If asked to fix, hand the findings to the react-atomic-aesthetics:implementer agent, which applies fixes and performs its own aesthetic self-check.
