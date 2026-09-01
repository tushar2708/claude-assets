# React Atomic Aesthetics — Canonical Rules

Single source of truth for every UI/UX rule in this plugin. The architect and implementer agents and the plan/review skills reference this file by number; they never copy its text. This document is a LIVING document — new rules are appended over time. Target stack: React (JSX/TSX) + Tailwind CSS + shadcn/ui + lucide-react.

## Part A — Aesthetic Discipline (Rules A1–A20)

**Color & tokens**
- A1. Never use Tailwind's default named colors (indigo, slate, zinc, emerald, sky, etc.) as the primary or accent color. Discover the project's existing semantic design tokens first (search for a theme file / CSS variables / tailwind theme extension). Invent a new accent ONLY if the project has no existing design system. If the project has more than two named theme/mode variants (e.g. a `data-theme` attribute with values beyond a simple light/dark), do not infer which value maps to which palette from the variant's name — read the actual CSS block each value selects and confirm the mapping directly (see F2). A theme named "light" is not guaranteed to be the paler of two palettes.
- A2. Use one saturated accent, applied sparingly. One deliberate accent used with restraint is the polished look; color everywhere is not.
- A3. All color flows through semantic tokens (e.g. bg-background, text-foreground, bg-primary, or CSS variables like bg-[var(--panel-surface)]). Never hardcode hex values or use raw Tailwind color-scale classes (bg-slate-900, text-zinc-200) in components.

**Typography**
- A4. Establish a real type pairing by overriding the default font stack (--font-sans / --font-display). Do not ship default Inter/system-sans as the finished type choice.
- A5. Express hierarchy with only 2–3 type sizes. More sizes flatten hierarchy instead of building it.

**Hierarchy, spacing, containment**
- A6. Try whitespace first as the grouping and hierarchy tool. Add a bordered/background container only when spacing alone cannot separate a group (NN/g Principle of Common Region: borders are a strong but overused signal).
- A7. Give the single most important element more space than everything around it.
- A8. Cap contrast at ~3 levels. If everything is emphasized, nothing stands out.
- A9. Use consistent spacing scale tokens (the Tailwind spacing scale: gap-1..gap-8, p-*, m-*). Never ad-hoc pixel values.

**Depth & signature**
- A10. Use subtle shadows/gradients as depth cues, sparingly — enough to differentiate layers, never as decoration.
- A11. Add at least one signature detail the default stack does not ship (a signature shadow, a texture, a distinctive radius) so the UI reads as intentional, not templated.
- A12. Differentiate at the layout level, not just by swapping a color. A custom accent on the stock hero→features→pricing template still reads as generic.

**Motion**
- A13. Every micro-interaction must serve a function (acknowledge input, communicate state). No decorative animation.
- A14. Scale motion to action weight: subtle feedback for frequent/minor actions, more substantial for rare/major actions. Over-animating is lethal (KISS).
- A15. Default to CSS/Tailwind transitions for motion. Recommend a motion library (e.g. framer-motion) ONLY when richer layout/gesture motion is genuinely needed, and justify the added dependency when doing so.

**States & feedback**
- A16. Design all four states for every async surface: empty, loading, error, success. The happy path is never the only path.
- A17. Use skeleton screens that mirror the final layout for content-loading states, not bare spinners.

**Accessibility (non-negotiable)**
- A18. Every icon-only control ships with an accessible label (aria-label, or visually-hidden sr-only text). Never rely on the SVG icon alone to name the control.
- A19. Keyboard operability and WCAG-AA contrast for every interactive element, in every theme it renders in.

**Verification**
- A20. Before calling UI work done, view it rendered and judge aesthetic quality (not just "it works"). If it looks flat or generic, revise once, then report. Never let aesthetic polish mask a real usability defect (aesthetic-usability effect).

**Card hover feedback**
- A21. Every card-shaped surface built anywhere in the UI — a bounded, visually-distinct block (grid tile, list item, pricing tier, dashboard panel), whether or not it is itself clickable — gets a hover state: a small lift (translate the element up ~2–4px) plus a stronger shadow/elevation on hover, transitioning only compositor-safe properties (`transform`, `box-shadow`), matching A13–A15's motion rules. A pointer-tracked highlight/glow following the cursor within the card is a reasonable enhancement on top of the lift, never a replacement for it. Respect `prefers-reduced-motion` (drop the transition duration to ~0, or drop the lift and keep only the shadow change). Apply this ONLY to the innermost bounded card element — never to a full-bleed/edge-to-edge page wrapper that surrounds it: a wrapper spanning the full viewport has no room to visibly "lift," and animating it shifts the whole page on any hover, which is a defect, not a stylistic choice. When a layout nests a card inside a full-bleed container (e.g. a photo-panel layout, a hero band), put the hover-lift on the card, not the container.

**Image loading hints**
- A22. Every image in the UI — decorative or content-bearing — declares its layout footprint and load priority explicitly: `width`/`height` attributes or a CSS `aspect-ratio`, always, so the image reserves its space before it loads (prevents CLS). Then set loading behavior by role: the single largest/first-paint-critical image on a page (the LCP candidate — typically a hero image, a full-panel photo, or a logo above the fold) gets `loading="eager"` and `fetchpriority="high"`; every other image gets `loading="lazy"`. This applies to all images, not only ones already covered by E1–E4's decorative-content rules — a genuinely content-bearing image with no sizing/priority hints is exactly as much of a CLS/LCP regression as an unhinted decorative one.

**Single-purpose page layout**
- A23. A single-purpose task page — login, signup, a one-step checkout, a single onboarding step — fits within the viewport with zero page-level scroll at every breakpoint. There is no content reason to scroll past a login form; if it scrolls, that is a layout defect, not a content constraint. If content genuinely cannot fit at a very small viewport height, scope the scroll to one inner container (e.g. the form column), never let the whole page grow past the viewport.

## Part B — Atomic Structure (migrated verbatim from the retired smrut-atomic-design skill)

### B1. Component Classification

Atoms (components/ui/): single HTML element or simple composition; no child component composition beyond styling; no business logic; no external state. Examples: Button, Badge, Input, Label, Progress. useState for UI only (hover, focus, open); NO useEffect with external dependencies.

Molecules (components/compounds/): compose 2+ atoms into a reusable pattern; single UI responsibility; local state only (hover, expanded, selected); NO Redux, NO API calls. Examples: EntityBadge, ScoreBar, ConfigField, DataCard.

Organisms (components/features/{domain}/): compose molecules into feature sections; can read Redux state; can trigger thunks (API calls); domain-specific logic. Examples: ChatPanel, ExtractionTab, SearchResultCard.

Pages (app/pages/ or routes): full page layouts; route-level data fetching; error boundaries; compose multiple organisms.

Classification decision tree: Is it a single HTML element or simple styled wrapper? YES → ATOM. NO → Does it compose 2+ atoms into a reusable pattern? YES → Does it have Redux/API dependencies? YES → ORGANISM / NO → MOLECULE. NO → Does it represent a full page section? YES → ORGANISM / NO → reconsider, might be an atom.

Promotion: Atom→Molecule when it needs to compose 2+ atoms. Molecule→Organism when it needs Redux or API access. Local molecule→Shared molecule when used in 2+ organisms. Organism→Page when it becomes a route component.

### B2. Non-Negotiable Rules

Rule 1 — No Hardcoded Colors: use bg-background / text-foreground / bg-[var(--panel-surface)], never bg-[#1a1a1a] text-[#ffffff]. (Reinforced by A1–A3.)

Rule 2 — Props Interface Required: every component declares a typed props interface with JSDoc on each prop.

Rule 3 — Accessibility Baseline: icon-only Buttons require aria-label; Inputs require an associated <Label htmlFor>; Expandables require aria-expanded; Loading requires aria-busy="true". (Reinforced by A18–A19.)

Rule 4 — Import Order: (1) React, (2) external libraries, (3) atoms, (4) molecules, (5) utilities and types.

Rule 5 — State Boundaries: Atom = UI-only state, no Redux, no API. Molecule = UI-only state, no Redux, no API. Organism = complex UI state, may read Redux, may call APIs via thunks.

Rule 6 — Testing: Molecules and Organisms each require a Storybook story and a unit test.

Rule 7 — Performance: React.memo() for molecules receiving object props; useMemo() for expensive calculations; useCallback() for handlers passed to children.

Rule 8 — CSS Classes: compose classNames with the cn() utility (base classes, conditional classes, passthrough className).

Rule 9 — Decorative Media Support: any shared/reusable image or media-rendering atom (e.g. an `<Image>` or CDN-image wrapper component) must accept and forward a way to mark an instance as decorative (`aria-hidden`, and an `alt` prop that accepts an empty string). Do not assume a project's existing image wrapper already supports this — check its actual current prop list before relying on it (reinforced by A18–A19, E3).

### B3. Styling approach (REPLACES the retired "CSS Modules or styled-components" rule)

Use Tailwind utility classes plus shadcn/ui primitives, with all colors/spacing expressed through semantic design tokens (Part A: A1–A3, A9) and composed via cn(). Do NOT use CSS Modules or styled-components. Follow mobile-first responsive design. Avoid inline styles except for genuinely dynamic values (e.g. a computed transform). Icons come from lucide-react. All theme/design-token CSS (colors, spacing, typography, keyframes) lives in exactly ONE canonical stylesheet per project — discover it first (it is usually already imported once, project-wide, from the app's entry point) and add to it; never create a second theme/tokens file, a component-scoped stylesheet, or a duplicate set of custom properties. Existing fragmentation found in a project (multiple pre-existing token files) is not this rule's problem to fix — only avoid adding to it.

### B4. Design Tokens

Semantic color tokens (shadcn/ui base): --background, --foreground, --card, --card-foreground, --popover, --popover-foreground, --primary, --primary-foreground, --secondary, --secondary-foreground, --muted, --muted-foreground, --accent, --accent-foreground, --destructive, --destructive-foreground, --border, --input, --ring. Extended semantic tokens to add in theme.css: --success, --success-foreground, --warning, --warning-foreground, --info, --info-foreground.

Spacing tokens: gap-1 (0.25rem tight inline), gap-2 (0.5rem default), gap-3 (0.75rem card padding), gap-4 (1rem section), gap-6 (1.5rem major break), gap-8 (2rem page section).

Typography tokens: text-xs (badges/labels), text-sm (secondary), text-base (body), text-lg (subheadings), text-xl (headings), text-2xl (page titles); font-normal/medium/semibold/bold.

Adding new tokens: define in theme.css under :root and .dark; use HSL without the hsl() wrapper for Tailwind opacity support (e.g. --primary: 220 90% 56%; used as bg-primary/50); prefix domain tokens (--entity-*, --score-*, --panel-*).

Validation before committing: grep for hardcoded hex (grep -rE "#[0-9a-fA-F]{3,6}" components/) and non-semantic Tailwind colors (grep -rE "(bg|text)-(slate|gray|zinc|neutral)-" components/). Only semantic classes should appear.

### B5. INDEX.md inventory

Every project using this plugin maintains an INDEX.md at the UI project root inventorying atoms/molecules/organisms/pages/hooks. Updating INDEX.md is the FINAL step of any component work. Sort entries alphabetically within each section; update the timestamp on every modification; remove deleted components; add new ones under the correct classification.

## Part C — Dependency Requirement

This plugin targets React + Tailwind CSS + shadcn/ui + lucide-react. Before doing UI work, the implementer detects whether Tailwind, shadcn/ui, and lucide-react are installed (inspect package.json and components.json). If any is absent, it offers to install/bootstrap them; it does not silently assume their presence, and does not hard-block.

## Part D — Role Checklists

Every agent MUST run its checklist before yielding and report each box as pass/fail. Each item cites the rule number that defines it (Parts A/B/C/E/F are the single source; these boxes are a terse actionable index, not a re-statement). Rules are APPEND-ONLY — add A21+/B6+/E-next/F-next rather than renumbering, or these citations misalign. A wholly new discipline not covered by any existing Part's letter gets its own new top-level Part with the next unused letter (as Parts E and F were added), rather than being force-fit under an existing one. When you add a rule, add a matching box to the relevant checklist(s) here.

### D1. Architect planning checklist (react-atomic-aesthetics:architect — run before returning a plan)

- [ ] A1 — accent chosen by discovering the project's existing tokens (or deliberately picked only if none exist); never a default Tailwind named color
- [ ] A4 — a real type pairing is specified (not default Inter/system sans)
- [ ] A5 — hierarchy uses only 2–3 type sizes
- [ ] A6 — grouping is whitespace-first; a container is planned only where spacing alone cannot separate a group
- [ ] A7 — the single most important element is given the most space
- [ ] A8 — at most ~3 contrast levels
- [ ] A10 — depth cues (shadow/gradient) planned sparingly, if at all
- [ ] A11 — at least one signature detail is defined
- [ ] A12 — differentiation happens at the layout level, not just a swapped color
- [ ] A16 — all four async states (empty/loading/error/success) are designed for every surface
- [ ] A21 — every card-shaped surface is planned with a hover-lift + shadow state, applied to the innermost card, never a full-bleed wrapper
- [ ] A22 — every planned image has an explicit width/height or aspect-ratio, and a stated loading/fetchpriority per its role (LCP candidate vs. everything else)
- [ ] A23 — any single-purpose task page (login/signup/checkout-step/onboarding-step) is planned to fit the viewport with zero page-level scroll
- [ ] B1 — every component is classified atom / molecule / organism / page
- [ ] B4 — the plan uses the project's real design tokens
- [ ] E1 — any decorative image/illustration/background art is stated to depict a real product concept, not generic filler
- [ ] E2 — decorative intensity is calibrated: full ornamental treatment only planned for high-emotion brand moments, restrained/geometric treatment for task-oriented surfaces
- [ ] E4 — perf budget considered for any planned decorative image or ambient/background animation (CLS/LCP/FCP, compositor-only properties)
- [ ] E6 — a coordinated set of visual assets (multiple theme variants, matched families) is planned with one reusable generation approach, not one-off per-asset prompts
- [ ] E7 — motion timing values (durations/stagger/easing) are planned by reusing what's already discovered in the codebase, not invented fresh
- [ ] F1 — no plan states a convention/mechanism exists ("the project already has X") without having verified it by reading the actual file
- [ ] F2 — if the project has 3+ named theme/mode variants, the plan states the verified (not inferred) mapping from each variant's literal value to its actual palette
- [ ] Existing-pattern analysis done; the plan states which existing patterns it matches, INCLUDING any existing asset/build/image pipeline (not just component/token patterns)

### D2. Implementer execution checklist (react-atomic-aesthetics:implementer — run before yielding)

- [ ] A3 — all color flows through semantic tokens; no hardcoded hex, no default named-color accent
- [ ] A9 — spacing uses scale tokens; no ad-hoc pixel values
- [ ] A13 — every micro-interaction is functional; no decorative motion
- [ ] A14 — motion is scaled to action weight
- [ ] A15 — CSS/Tailwind transitions by default; a motion library only when justified
- [ ] A17 — content-loading uses skeletons mirroring final layout, not bare spinners
- [ ] A18 — every icon-only control has an aria-label or sr-only text
- [ ] A19 — keyboard-operable and WCAG-AA contrast in every theme
- [ ] A20 — rendered UI viewed and judged; if flat/generic, revised once, then reported
- [ ] A21 — every card-shaped surface has the hover-lift + shadow state implemented, on the innermost card, never a full-bleed wrapper; respects prefers-reduced-motion
- [ ] A22 — every image has width/height or aspect-ratio set, and loading="eager"+fetchpriority="high" (LCP candidate) or loading="lazy" (everything else)
- [ ] A23 — single-purpose task pages fit the viewport with zero page-level scroll at every breakpoint
- [ ] B2 Rule 9 — any shared image/media atom touched or introduced supports marking an instance decorative (aria-hidden, empty-string-capable alt)
- [ ] B2 — typed props interface, import order, state boundaries, memo/useMemo/useCallback, cn()
- [ ] B3 — Tailwind + shadcn/ui; no CSS Modules / styled-components; icons from lucide-react; all new theme/token CSS added to the ONE existing canonical stylesheet, no new stylesheet created
- [ ] B5 — INDEX.md updated as the final step
- [ ] Part C — Tailwind/shadcn/lucide presence checked; offered to bootstrap if any is missing
- [ ] E3 — every decorative image/animation element is aria-hidden with empty alt, and never the sole carrier of information
- [ ] E4 — decorative images/animation implemented with CLS/LCP-safe practices (reserved dimensions, no render-blocking chain, no lazy-load above the fold, compositor-only animated properties)
- [ ] E5 — any external site/product cited as inspiration during implementation is not literally copied (asset files, exact palettes) unless explicitly confirmed as the project owner's own IP
- [ ] E7 — new motion reuses an existing timing value found in the codebase where one exists, rather than an invented number
- [ ] F1 — no code comment or report claims an existing mechanism/convention was "extended" without having actually found and read it first

### D3. Reviewer audit checklist (react-atomic-aesthetics:review — verify each; findings go in the four category tables)

- [ ] UI/UX category — A2, A6, A7, A8, A11, A12, A16, E1, E2: hierarchy, affordances, states, signature detail, non-generic layout, decorative content relevance and intensity calibration
- [ ] Micro-interactions category — A13, A14, A15, A17, A21, E4, E7: functional + weight-scaled motion, prefers-reduced-motion fallback, skeleton loading, card hover-lift present on the innermost card (never a full-bleed wrapper), decorative/ambient motion perf-safety, timing-value consistency with the rest of the codebase
- [ ] A11y category — A18, A19, E3: labeled icon controls, keyboard operability, roles/state, WCAG-AA contrast in every theme, decorative images/animation aria-hidden and never sole information carrier
- [ ] Responsive category — B3, A22, A23: mobile-first, no overflow at 320px, ≥44px touch targets, grids reflow; every image sized/prioritized correctly; single-purpose task pages have zero page-level scroll at every breakpoint
- [ ] Structure — B1, B2, B2 Rule 9, B5: atomic classification, props/state/imports/cn(), decorative-media support on shared image atoms, INDEX.md current
- [ ] Color & type — A1, A3, A4, A5, A9: no default/hardcoded colors, real type pairing, ≤3 type sizes, token-based spacing
- [ ] A20 — no real usability defect is masked by a polished surface
- [ ] F1, F2 — no unverified "existing convention" claims found in the plan or code; theme-variant-to-palette mapping verified, not inferred, if 3+ named variants exist

## Part E — Decorative Content, Ambient Motion & Micro-interactions (Rules E1–E7)

Part A's Motion rules (A13–A15) govern INTERACTIVE feedback — motion that responds to a user action. This Part
governs the adjacent, previously-uncovered territory: non-interactive decorative imagery (illustration,
background art, ambient glows, ornamental motifs) and ambient/entrance motion (scroll reveals, background
animation) that plays with no direct user trigger. Both are common in a polished UI; both have their own
failure modes distinct from interactive-feedback motion.

**Relevance & calibration**
- E1. Decorative imagery, illustration, and background art must depict the product's real concepts or information architecture — never generic/stock/library iconography chosen only to fill space. Before adding any decorative visual asset, state what specific concept it represents; if you cannot name one, do not add it. (NN/g: purely decorative graphics add no value and users learn to skip them.)
- E2. Reserve maximal ornamental/expressive visual treatment for high-emotion brand moments (hero, onboarding, empty/success/error states, sign-in/sign-up) and use restrained, geometric, or purely functional treatment on task-oriented, evaluation-focused surfaces (pricing, docs, dashboards, settings, checkout). Not every surface earns equal decorative intensity — calibrate it by the emotional weight of the moment, not uniformly across the product.

**Accessibility & performance**
- E3. Every decorative image or background animation element must be excluded from the accessibility tree (`aria-hidden="true"`, empty `alt=""`) and must never be the sole carrier of information a sighted user also receives some other way. (See B2 Rule 9 for the component-support requirement this implies.)
- E4. Decorative images and ambient/background animation must not regress Core Web Vitals: never gate them behind a render-blocking stylesheet dependency chain; reserve explicit `width`/`height` or `aspect-ratio` to prevent layout shift; never lazy-load an above-the-fold decorative element; animate only compositor-friendly properties (`transform`, `opacity`), never layout- or paint-triggering ones (`width`, `height`, `box-shadow`, `top`/`left`).

**Asset generation & provenance**
- E5. When a plan cites an external site or product as inspiration, state explicitly for each one whether it is the project owner's own IP (freely reusable — mechanism and content both) or a third party's (technique/category inspiration only — never copy its literal assets, exact palette, or layout into the shipped product without explicit, separately confirmed authorization).
- E6. When commissioning a coordinated SET of visual assets (multiple theme variants, a matched icon family, mirrored/paired panels), use one consistent, reusable generation prompt/template with reference images attached, not a fresh one-off prompt per asset — inconsistent stroke weight or style between separately generated assets reads as unpolished, not intentional.

**Motion timing consistency**
- E7. New ambient, entrance, or scroll-triggered motion must reuse existing timing values (durations, stagger delays, easing curves) already present in the codebase where a comparable existing pattern exists — grep for existing `transition`/`animation`/stagger-delay values before inventing a new number. Consistency of tempo across a product matters as much as consistency of color, and costs nothing extra to get right.

## Part F — Verification Discipline (Rules F1–F2)

These two rules apply to every agent and every phase (planning, implementation, review) — they are about HOW
a claim gets made, not what the claim is about, which is why they sit in their own Part rather than under A/B/E.

- F1. Never state that a convention, pattern, or global mechanism already exists in the target project ("the project already has a reduced-motion block to extend," "tests use `.test.ts`," "there's already a CDN pipeline for this") without having actually read the file that would contain it. If asked to extend or match an existing thing, confirm it is actually present first; if it is not, say so plainly and propose creating it rather than assuming and building on a false premise.
- F2. When a project uses named theme/mode variants beyond a simple boolean light/dark (a `data-theme` attribute, a multi-brand theming system, etc.), verify by reading the actual CSS/token file which literal attribute or class value maps to which visual palette — never infer the mapping from the variant's name. A theme literally named "light" or "bright" is not guaranteed to be the paler or the more saturated of the set; read the block, don't guess from the label.
