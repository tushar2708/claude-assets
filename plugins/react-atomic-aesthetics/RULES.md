# React Atomic Aesthetics — Canonical Rules

Single source of truth for every UI/UX rule in this plugin. The architect and implementer agents and the plan/review skills reference this file by number; they never copy its text. This document is a LIVING document — new rules are appended over time. Target stack: React (JSX/TSX) + Tailwind CSS + shadcn/ui + lucide-react.

## Part A — Aesthetic Discipline (Rules A1–A20)

**Color & tokens**
- A1. Never use Tailwind's default named colors (indigo, slate, zinc, emerald, sky, etc.) as the primary or accent color. Discover the project's existing semantic design tokens first (search for a theme file / CSS variables / tailwind theme extension). Invent a new accent ONLY if the project has no existing design system.
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

### B3. Styling approach (REPLACES the retired "CSS Modules or styled-components" rule)

Use Tailwind utility classes plus shadcn/ui primitives, with all colors/spacing expressed through semantic design tokens (Part A: A1–A3, A9) and composed via cn(). Do NOT use CSS Modules or styled-components. Follow mobile-first responsive design. Avoid inline styles except for genuinely dynamic values (e.g. a computed transform). Icons come from lucide-react.

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
