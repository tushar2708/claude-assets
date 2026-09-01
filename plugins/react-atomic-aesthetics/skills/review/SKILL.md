---
name: review
description: |
  Review an existing or just-built React UI for clean, intentional UI/UX against this plugin's canonical rules.
  Use when:
  (1) Auditing a React screen/component for visual quality and consistency
  (2) Checking a just-implemented UI before calling it done
  (3) Asked to "review the UI", "does this look generic", or "check the frontend aesthetics"
  Runs a READ-ONLY two-lens audit (design + code) against RULES.md and consolidates findings into four
  all-P0 category tables: UI/UX, micro-interactions, a11y, responsive.
---

# Review UI

Audit a React UI for UI/UX quality against this plugin's canonical rules, and consolidate the findings into four category tables. You (the main agent) orchestrate two specialist reviewers — the react-atomic-aesthetics:architect and the react-atomic-aesthetics:implementer agents — then VERIFY their findings yourself. This is a READ-ONLY audit: observe and report, never change code.

ARGUMENTS: an optional scope hint (a path, route, screen, or component). If none is given, default the scope to the project's web frontend root. If the argument names something that does not exist, say so and ask for the correct scope instead of guessing.

## Step −1 — Read-only guardrails (MANDATORY — obey before anything else)

1. **READ-ONLY. Touch NOTHING.** Do not edit, create, delete, `Write`, `Edit`, format, stage, unstage, revert, or run any migration/build/format command that mutates files. The ONLY thing you write is your report. Every fix you find is DESCRIBED, never applied. If the user wants fixes applied, that is a separate follow-up (hand off to react-atomic-aesthetics:implementer).
2. **Do NOT run the app, tests, linters, or a build to "verify".** Verify findings by reading the actual source (components, the theme/tokens file, the design system). A command you broke is your mistake, not a finding.
3. **Both reviewer agents are ALSO read-only.** Tell each explicitly: "You are reviewing, not implementing. Do not edit, create, or delete any file, and run no shell/build/test/format command. Read the code and return findings only."
4. **Stay in scope.** Review only files under the resolved scope (Step 0). Do not comment on backend code or unrelated config.

## Step 0 — Resolve scope and load the rule sources

1. **Resolve scope** from ARGUMENTS; print the exact directory/files you will review.
2. **Read the rule sources** (read the ACTUAL files, not memory):
   - `${CLAUDE_PLUGIN_ROOT}/RULES.md` — the plugin's canonical UI/UX + atomic-structure rules (A1–A20, B1–B5, Part C, E1–E7, F1–F2). These are the authoritative rules; cite rule numbers. You MUST verify every box of checklist D3 (Reviewer audit checklist) in RULES.md — each box maps to one of the four categories below, and its findings go in that category's table.
   - Every `CLAUDE.md` that governs the frontend (project root + any nested app-level one), and any `.claude/rules/` files touching the frontend.
   - The project's real theme/design tokens (e.g. `globals.css` / `theme.css` / the Tailwind config): learn the actual token names, keyframes, and any `prefers-reduced-motion` block BEFORE flagging a color/motion issue — never invent a token. This is RULES F1 in practice: never assume a convention (a reduced-motion block, a specific token) exists without having read the file. If the project has 3+ named theme/mode variants, verify which literal value maps to which palette by reading the CSS directly, never by inferring from the variant's name (RULES F2) — a reviewer who inherits this exact mistake from a flawed plan must still catch it here.

## Step 1 — Launch the two reviewers (in parallel)

Launch **both** agents in a single message so they run concurrently. Give EACH the resolved scope, the four categories below, RULES.md, and the read-only instruction from Step −1.3. Ask each for a structured findings list; for every finding: exact `file:line`, its category, the specific rule/heuristic violated (name or quote it, with the RULES rule number where it maps), and the single concrete fix.

- **react-atomic-aesthetics:architect** (design/journey lens): reviews the SCREENS and FLOWS in scope — broken or confusing journeys, missing empty/loading/error states (A16), weak affordances/signifiers, poor visual hierarchy (A6–A8), inconsistent patterns across screens, generic/templated layout (A12), journey-level a11y/responsive gaps, whether any decorative imagery depicts a real concept and its ornamental intensity fits the moment (E1–E2), and whether any inspiration source cited in prior planning/commit context had its provenance disclosed (E5). Looks at the experience, not one component.
- **react-atomic-aesthetics:implementer** (component/code lens): reviews the COMPONENTS in scope at code level — markup, Tailwind classes and semantic tokens (A1–A3, A9), event handlers, ARIA attributes (A18), focus handling, transition/animation classes (A13–A15), breakpoint utilities, touch-target sizing, atomic classification (B1), `cn()`/state boundaries (B2, including Rule 9 decorative-media support), decorative image/animation `aria-hidden` markup and compositor-safe animated properties (E3–E4), and whether new motion timing values match an existing pattern in the codebase rather than being invented (E7). Flags the exact class or attribute that is wrong or missing.

Both must map every finding to one of these four categories:

1. **UI/UX issues** — affordance/signifier failures (a control that doesn't look interactive), weak or wrong visual hierarchy (A6–A8), aesthetic-not-strictly-WCAG low contrast, inconsistent styling across similar elements, default-named or hardcoded colors used as accent (A1–A3), missing empty/loading/error/disabled states (A16), a templated/no-signature look (A11–A12), confusing copy, dead ends in a flow, silent fire-and-forget failures with no user feedback, decorative imagery/illustration that is generic filler rather than depicting a real product concept (E1), and decorative/ornamental intensity that is miscalibrated for the surface — e.g. full brand ornamentation on a task-oriented settings/checkout page, or a flat/bare treatment on a genuine high-emotion moment (E2).
2. **Missing micro-interactions** — interactive elements with no hover / active(press) / focus feedback; state changes (open/close, select, add/remove, success/error) that snap with no transition; no `:focus-visible` ring; no loading/skeleton/optimistic feedback on async actions (A17); a dropdown/menu/toggle with no open indicator (e.g. a caret that doesn't rotate); decorative motion or motion not scaled to action weight (A13–A14); any motion added WITHOUT a `motion-reduce:` / `prefers-reduced-motion` fallback — a violation, not a nicety (A15); ambient/background/entrance animation implemented with non-composited properties (animating `width`/`height`/`box-shadow`/position instead of `transform`/`opacity`) that risks layout-shift jank (E4); newly-added motion with a timing value (duration/stagger/easing) that doesn't match an existing, discoverable pattern already used elsewhere in the same codebase for a comparable interaction (E7).
3. **A11y violations** — non-semantic interactive elements (`div`/`span` used as a button), icon-only controls without `aria-label` (A18), custom widgets missing roles/state (`aria-haspopup`, `aria-expanded`, `role="listbox"/"option"`, `aria-selected`, `aria-current`), no keyboard operability (Enter/Space/Esc/arrows) (A19), modals with no focus trap or no Esc-to-close, missing/incorrect `alt`, form controls with no associated label, genuine WCAG-AA contrast failures verified against the token's real color in every theme (A19), and any decorative image/background-animation element that is NOT `aria-hidden`/empty-`alt` — or, worse, is the only place a piece of real information appears (E3).
4. **Responsive design issues** — fixed pixel widths/heights that overflow small screens, layouts that are not mobile-first (B3), horizontal scroll on narrow viewports, touch targets under ~44px, text/controls that clip or overlap when a sidebar/drawer is open, dropdowns that render off-screen, grids that don't reflow. Verify against the actual Tailwind breakpoint utilities present.

## Step 2 — Consolidate and VERIFY (main agent, before writing the report)

The reviewers can be wrong or vague — trust nothing, verify everything against the real source:

1. **Open each cited `file:line` and confirm the defect is actually present** as described. Discard any finding you cannot confirm; never pass through a hallucinated line number, class name, or token.
2. **Dedup** — the two agents will overlap. Merge duplicates into one row (keep the sharpest `file:line` and fix).
3. **Resolve every finding fully** — no "might", "needs checking", "TBD". If uncertain, read the code and settle it before it goes in the table.
4. **Pick ONE definitive fix per finding** — the exact class/attribute/markup change to make, using the project's real tokens and the plugin's rules. No "optionally / consider / you could / or".

## Report — produce FOUR markdown tables, one per category

Columns for every table: **"serial no"**, **"component / screen"**, **"file:line"**, **"rule violated"** (name or quote the checklist rule, with the RULES rule number where it maps), **"why it's a violation + the exact fix"** (one line: what is wrong and the single concrete change to make, using real project tokens/utilities).

Table 1 — **UI/UX issues**
Table 2 — **Missing micro-interactions**
Table 3 — **A11y violations**
Table 4 — **Responsive design issues**

HARD RULES for the report:

- **Everything is P0. No severity axis, no "minor/cosmetic/nit/non-blocking/observation".** If it is not 100% correct it is 100% wrong and it is a numbered row. It is a failure to soften a finding or to mention any issue in prose outside the tables.
- **No sidenotes.** The ONLY prose allowed around the tables is: (a) the resolved scope line, (b) a one-line-per-category count, and (c) the single-line verdict. Anything that reads like a finding must be a table row.
- **The report is FINAL and fully resolved.** No "need to verify / not sure / this might be / assuming / requires investigation". Every cell is a verified fact and a definitive fix.
- **No optional / open-ended fixes.** Each row's fix is one specific, actionable change; banned words: "optionally, maybe, you could, consider, might want to, if you prefer, one option is, could also, or".
- When a category has no verified findings, write a single row for that table stating **"None found"** — never replace real findings with prose.
- **One-line verdict** at the end: total verified findings and the per-category split (e.g. "12 findings — UI/UX 4, micro-interactions 5, a11y 2, responsive 1").

Never let good aesthetics mask a real usability defect — call out any usability defect explicitly even if the surface looks polished (RULES A20). Do NOT implement any fix. Stop after the four tables and the verdict, and wait for the user to decide what to fix.
