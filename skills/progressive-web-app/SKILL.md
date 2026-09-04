---
name: progressive-web-app
description: Checklist-driven, two-level web-app quality skill. LEVEL 1 = responsive foundation (mobile→desktop with Tailwind + shadcn/ui: 320px zero-overflow, reachable nav, 48px touch targets, Playwright viewport suite) — run first, store a report. LEVEL 2 = TRUE PWA (web app manifest, PNG/maskable/apple-touch icons, vite-plugin-pwa service worker + offline caching, update flow, install UX) with verification tracks that run LOCAL DETERMINISTIC audits (Lighthouse CLI for performance/accessibility/best-practices, plus manifest/icon/service-worker/installability checks) and save a report into the project. On first invocation ensure Level 1; on later invocations focus on Level 2 (gated on a passing Level 1 report); optionally run both by asking the user at the start. Use for any responsive review OR any install/offline/manifest/service-worker/PWA-icon work. Does NOT cover SEO — that is owned by the react-seo-planner skill.
---

# Progressive Web App

This skill takes a web app to production-grade in **two ordered levels**:

- **Level 1 — Responsive foundation**: the app must work on every screen before it is packaged as
  an app. Every rule is a checklist item in `CHECKLIST.md`; this skill explains each one in detail
  below. Produces a stored responsive report.
- **Level 2 — Progressive Web App**: manifest, icons, service worker + offline, update flow,
  install UX, plus verification tracks that run local deterministic audits and save a report.

Levels are ordered and **gated**: Level 2 must not start until a Level 1 report exists and passes.
SEO is explicitly out of scope — defer to the `react-seo-planner` skill.

## How this skill runs (systematic, task-driven, evidence-based)

`CHECKLIST.md` (in this skill folder) is the compliance spine — every run is driven by it, and every
plan and review is measured against it. Reports live in a project-local `reports/pwa_scores/` folder
(the shared `reports/` parent also holds SEO → `reports/seo_geo_scores/`), so state persists across
sessions and CI.

Run the steps below **in order, one at a time** — do not batch; each step has a concrete deliverable.

**Prerequisite — Tooling (verify BEFORE Step 0; install anything missing, then re-check).**
This skill is CLI-driven — its tools MUST be present or nothing below can produce evidence. Run each
check; for any MISSING tool run the paired install, then re-run the check until it passes. Paste the
version output as evidence. Do NOT proceed to Step 0 until the tools for the chosen level exist.

```bash
# Base — Node 18+ and npx (must print versions)
node -v && npx -v || { echo "Install Node 18+ from https://nodejs.org"; exit 1; }

# Playwright runner + Chromium (Level 1 viewport suite AND Level 2 CDP installability check)
npx playwright --version 2>/dev/null || npm i -D @playwright/test
npx playwright install chromium                     # idempotent — downloads the browser if absent

# Lighthouse CLI (Level 2 quality audit: performance / accessibility / best-practices)
npx lighthouse --version 2>/dev/null || npm i -D lighthouse

# vite-plugin-pwa (Level 2 app-ification — only when the app will ship a manifest + service worker)
npm ls vite-plugin-pwa >/dev/null 2>&1 || npm i -D vite-plugin-pwa

# sharp — icon rasteriser for the 192 / 512 / maskable / apple-touch PNGs (zero system deps)
node -e "require('sharp')" 2>/dev/null || npm i -D sharp

# Legacy Lighthouse PWA category (v11) — NO install needed; run on demand to reproduce the classic
# PWA report (v12+ deleted the category). Sanity-check it resolves:
npx -y lighthouse@11 --version

# OPTIONAL (install only if you use them):
#   npm i -D sitespeed.io      # deterministic multi-run medians
#   npm i -D unlighthouse       # whole-site crawl + audit
```

If a tool cannot be installed (offline / policy), record that check as **FAIL/BLOCKED** (never PASS)
and stop — the skill cannot generate evidence without its tools.

## How this skill runs — ONE command, audit-first (do these in order)

The whole flow: scaffold the audit tooling, then run a SINGLE command that builds, audits, and writes
`PWA_REPORT.html`. You never run the audit sub-scripts by hand and you never hand-write the report — the
command does both. The report IS the gap analysis: read it, fix what it flags, re-run the SAME command
until it is green.

**1 — Install tooling if missing.** Run the Prerequisite checks above; install anything absent.

**2 — Ensure the anchor `ai_skill_anchors/pwa.json` exists** (it is the single source of truth — the scripts
read every project-specific value from it, so nothing is hardcoded in the scaffolded code). If it does not
exist, do NOT ask blindly and do NOT default a path silently — first **analyze the project** and form a
reasonable recommendation for each field, then use the **AskUserQuestion** tool to confirm each with the user:
   - `project` — the app's package/display name (read the app's `package.json`).
   - `app_dir` — the Vite app root that holds `index.html` + `package.json` (`verify-pwa.mjs` builds it and
     `audit-lighthouse.mjs` runs from it). Find it by locating `index.html` + `vite.config.*`.
   - `routes` — the PUBLIC routes to audit for responsiveness. **Derive these from the app's router**
     (e.g. the route table / `<Route>` definitions), NOT by copying the template's example — every project
     differs. Exclude auth-gated routes. Recommend the list you found, then confirm.
   - `scripts_dir` — where the 6 audit scripts will live.
   - `reports_root` — reports go to `<reports_root>/pwa_scores`; NEVER a root-level or cwd folder.
   - `production_url` — the deployed origin to optionally audit later (or `null`).
   Create `ai_skill_anchors/pwa.json` from `templates/pwa.template.json` with the confirmed values. Use ONLY
   the keys in the template. Code reads `reports_root`, `app_dir`, and `routes`; the rest is the
   skill↔project bridge / documentation.

**3 — Scaffold anything missing, per `pwa.json` (check ALL of it).** Verify every file the anchor lists
exists; scaffold each missing one from its matching template **byte-for-byte** (1:1 template↔file — the
templates read `app_dir`/`routes`/`reports_root` from the anchor, so there is NOTHING to fill inside the
scripts; all project-specific values live in `pwa.json`):
   - the 6 scripts in `<scripts_dir>/`: `create-reports-directory.mjs`, `verify-pwa.mjs`,
     `audit-responsive.mjs`, `audit-pwa.mjs`, `audit-lighthouse.mjs`, `generate-reports.mjs`.
   - the **entry point**: a `verify-app` npm script (`node <scripts_dir>/verify-pwa.mjs`) AND a Makefile
     target that calls it. There is NO Makefile template — add this sample target to the project's
     existing Makefile (or create a Makefile if the project has none), adapting the app path:
     ```make
     .PHONY: verify-pwa
     verify-pwa:  ## PWA audit + report. Pass PWA_TARGET=<url> to audit a deployed origin.
     	@npm --prefix <path-to-app> run verify-app -- $(PWA_TARGET)
     ```

**4 — Read the existing report FIRST and tell the user its state.** If
`<reports_root>/pwa_scores/PWA_REPORT.html` (or its JSONs) already exists, summarise for the user which
issues it currently lists — or state plainly that there is no report yet, or that it shows 0 issues. Do
this before running anything.

**5 — Run the ONE command to find current issues.** `make verify-pwa` (or `… PWA_TARGET=<url>` to audit a
deployed origin). It builds, serves a local preview, runs responsive + pwa + lighthouse, and
(re)generates `PWA_REPORT.html`.

**6 — Read `PWA_REPORT.html` and find the bugs/gaps.** It names failing responsive routes (with the
offending element), the PWA installability checks, and the Lighthouse scores. Anything missing from the
app itself — manifest, service worker, icons, update prompt, iOS metas, host headers — shows up here as a
failure; that is your implementation to-do list.

**7 — Fix the flagged issues, then re-run the ONE command.**

**8 — Repeat step 7 until the report is all green.** Never close an item on reasoning — only on a green
re-run (the Honesty rule in `CHECKLIST.md`).

**9 — Offer a production audit.** Once local is green, if `pwa.json` has a `production_url`, use the
**AskUserQuestion** tool to ask whether to also audit the deployed origin: `make verify-pwa
PWA_TARGET=<production_url>` — the SAME one command, pointed at production. (Remote runs can flag issues
the local build can't, e.g. host headers or a locale-specific layout; note the client→server latency
inflates Lighthouse performance.)

Single deliverable: `<reports_root>/pwa_scores/PWA_REPORT.html` — a self-styled entry point that links to
the two full Lighthouse HTML reports. Do NOT hand-write it and do NOT run the audit sub-scripts one by one.

---

# LEVEL 1 — Responsive foundation (run first; gate for Level 2)

> This section is the detailed explanation of every Level-1 item in `CHECKLIST.md` (§ "LEVEL 1").
> "Done" = the 320px hard gate + the scaffolded `audit-responsive.mjs` viewport sweep passing. It records
> the outcome in `<reports_root>/pwa_scores/responsive-audit.json` (the Level 1 gate result) before Level 2.

## Responsive Web Design

Build adaptive interfaces for every screen size. The stack these rules assume is **Tailwind (v4) +
shadcn/ui**, so every rule is stated as a **principle** (portable — the "why") followed by its
**Tailwind/shadcn mapping** (the "how"). When a rule names a shadcn primitive (`Sidebar`, `Sheet`,
`Drawer`, `Dialog`, `useIsMobile`), install it with the shadcn CLI —
`npx shadcn@latest add sidebar sheet drawer dialog` (this also generates the `useIsMobile` hook and
the `cn` helper). Never hand-roll a primitive the kit provides.

## Stack context — how "responsive" is done here

- **Utility-first, mobile-first.** Base (unprefixed) classes describe the phone; add
  `sm:`/`md:`/`lg:`/`xl:` to enhance upward. Never write desktop-first with overrides that shrink
  down — it fights Tailwind's cascade and hides mobile bugs.
- **Reuse shadcn primitives.** shadcn/ui already ships the responsive machinery:
  `Sidebar` (+ `SidebarProvider`, `SidebarTrigger`, `SidebarInset`, `SidebarHeader`,
  `SidebarContent`, `SidebarFooter`, `SidebarMenu`, `SidebarMenuItem`, `SidebarMenuButton`,
  `useSidebar`, …), `Sheet`, `Drawer`, and the `useIsMobile()` hook — install them with the shadcn
  CLI (`npx shadcn@latest add sidebar sheet drawer dialog`). Do not reimplement off-canvas / hamburger logic.
- **CSS handles layout; JS handles behavior.** Prefer Tailwind responsive classes for anything
  expressible in CSS. Reserve `useIsMobile()` for behavior CSS can't do — e.g. rendering a
  `Drawer` vs a `Dialog`.

## Theming is orthogonal — never fork responsive per theme

If the project has a token-based theme system (e.g. `light`/`dark`, applied via `<html data-theme>` or a `.dark`
class, defined in a theme/tokens CSS file), keep responsiveness and theming as **independent axes composed on the
same element, never nested**:

- **Responsive = layout**, expressed as Tailwind variants on components (`md:`/`lg:`, container width, grid collapse,
  hamburger `Sheet`, touch sizing). It is theme-agnostic — a card stacks identically in every theme — and it should
  add **zero** breakpoints to the theme CSS. Keep `@media` out of the theme / token layer.
- **Theme = tokens**, swapped under the theme selector and consumed by write-once utility classes / component styles.
  Themes carry no breakpoints.
- If a responsive surface must look different per theme, encode that difference as a **token** (e.g. `--section-y`,
  `--radius-card`), never a per-theme media query. The component reads the token; the breakpoint stays constant.

Do NOT add a per-theme responsive variant or a scoped responsive stylesheet. A component composes both at once —
themed-surface classes for colour + Tailwind responsive variants for layout: `class="<themed-surface> md:grid lg:grid-cols-3"`.

## Breakpoint model

Use Tailwind's **named ladder** as the default system so the whole app stays consistent:

| Token  | Min width | Meaning |
|--------|-----------|--------------------------|
| (base) | 0         | phone |
| `sm`   | 640px     | large phone / small tablet |
| `md`   | 768px     | tablet — **below this, the marketing nav collapses to a hamburger AND the dashboard sidebar goes off-canvas** |
| `lg`   | 1024px    | desktop — roomy multi-column content |
| `xl`   | 1280px    | wide desktop |

**Content-driven escape hatch:** if a *specific* component demonstrably wraps at an off-ladder
width, use an arbitrary variant (`min-[920px]:`) **for that component only**, with a one-line
comment saying why. Don't scatter arbitrary breakpoints as a habit — the named ladder is the
default precisely because consistency is easier to reason about and review.

## Container

There is **one** container width. Content caps at **1024px** (equal to `lg`, the desktop hinge)
and is centered with responsive gutters. Use a single `<Container>` primitive so the width lives
in one place — never re-hardcode `max-w-[…]` per section.

```tsx
// Principle: one max-width, centered, gutters that grow with the viewport.
<div className="mx-auto w-full max-w-[1024px] px-4 sm:px-6 lg:px-8">…</div>
```

## Grid

Default to **explicit responsive columns** for designed layouts where the count is known
(e.g. a 3-card pricing row) — you keep exact control:

```tsx
<div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">…</div>
```

Use **auto-fit `minmax()`** only where the item count is variable (app lists, example galleries)
and you want reflow without breakpoints:

```tsx
<div className="grid gap-4 [grid-template-columns:repeat(auto-fit,minmax(280px,1fr))]">…</div>
```

## Fluid typography

Scale headings smoothly with `clamp()`:

```tsx
<h1 className="[font-size:clamp(1.75rem,4vw,3rem)]">…</h1>
```

## Responsive media & code windows

```tsx
<img className="h-auto max-w-full" … />
```

Shiki code windows must not force page-wide horizontal scroll — let the code block scroll
internally and shrink its font on small screens:

```tsx
<pre className="overflow-x-auto text-[12px] sm:text-[13px]">…</pre>
```

## Marketing top nav (Header)

The public `Header` is a horizontal nav on desktop. **Below `md` it collapses to a hamburger that
opens a `Sheet`** — the nav links must NOT simply disappear.

- Keep the **primary CTA** (Sign up / Dashboard) visible at every width; only the link cluster
  collapses into the sheet.
- The sheet reuses the same `NavLink`s + active-pill styling; close it on route change, on
  backdrop tap, and on Esc; trap focus while open.
- Import `Sheet`, `SheetTrigger`, `SheetContent` from your shadcn components (`npx shadcn@latest add sheet`).

```tsx
<nav className="hidden items-center gap-6 md:flex">…</nav>        {/* desktop links */}
<SheetTrigger className="md:hidden" aria-label="Open menu">…</SheetTrigger>  {/* mobile */}
```

## Dashboard: Sidebar + Topbar (the "both bars" rules)

The authenticated dashboard has BOTH a left **sidebar** and a top **context bar**. They have
**orthogonal roles**, and only ONE owns "primary navigation" at a given width:

- **Sidebar = primary section navigation** (Dashboard, Apps, Memory, …). Build it on the shadcn
  `Sidebar` primitive (`npx shadcn@latest add sidebar`)
  (`SidebarProvider` → `Sidebar` → `SidebarHeader`/`SidebarContent`/`SidebarFooter` +
  `SidebarMenu`/`SidebarMenuItem`/`SidebarMenuButton`), NOT a hand-rolled `<aside>`.
- **Topbar = context** (breadcrumbs, search, page actions, account) — never primary nav.

Responsive behavior:

- **≥ `md` (768px):** sidebar **persistent** on the left; the topbar spans only the content
  column (use `SidebarInset`), not the full width.
- **Below `md`:** sidebar goes **off-canvas** (rendered as a `Sheet`). The **topbar becomes the
  only persistent chrome** and MUST host the `SidebarTrigger` (hamburger, left) + a collapsed
  page title / back affordance + the account menu (right); search collapses to an icon.
- Everything the desktop sidebar holds (org switcher, all nav groups, account/theme) lives
  **inside** the `Sidebar` so nothing is orphaned on mobile.
- **One overlay at a time** — the mobile sidebar sheet must not coexist with the command palette.
  Z-order: content < sticky topbar < sidebar sheet + backdrop < command-palette / toasts.
- **Breadcrumbs:** show only the current segment (or a back chevron) below `md`; full trail at `md+`.

**Implementation note — breakpoint (unified at `md`/768):** adopt the shadcn `Sidebar` primitive
AS-IS. It uses the shared `useIsMobile()` hook, which flips at **768px (`md`)** — the SAME breakpoint
as the Dialog→Drawer switch. The sidebar therefore goes off-canvas below `md` with **no hook override
needed**; tablets (768–1023) keep the persistent sidebar. One breakpoint everywhere is the point.

## Data tables on mobile

Wide tables must not force horizontal page scroll. For the **primary data tables** (plan
comparison, payment history, memory rows), switch to a **stacked card / label:value** layout below
`md`; keep the `<table>` grid at `md+`.

```tsx
<table className="hidden md:table">…</table>                     {/* desktop */}
<ul className="space-y-3 md:hidden">                             {/* mobile cards */}
  <li className="rounded-lg border p-4">
    <div className="flex justify-between">
      <span className="text-muted-foreground">Plan</span><span>Pro</span>
    </div>
    …
  </li>
</ul>
```

Secondary / less-critical tables may instead hide non-essential columns (`hidden md:table-cell`).

## Dialogs & modals on mobile

Center-screen dialogs are cramped on phones. Render a **`Drawer` (bottom sheet) on mobile and a
`Dialog` on desktop** — the "responsive dialog" pattern. Both are shadcn primitives
(`npx shadcn@latest add drawer dialog`); branch with `useIsMobile()`:

```tsx
const isMobile = useIsMobile();
return isMobile ? <Drawer …/> : <Dialog …/>;
```

## Touch, hit areas, and fixed widths

- **Minimum 48×48px touch targets** for every interactive control on touch screens. shadcn
  defaults are smaller (default Button ≈36px, `sm` ≈32px) — bump them on touch to at least 48px
  (`min-h-12`). Hover-only affordances must have a tap equivalent.
- **Kill viewport-exceeding fixed widths.** A fixed `w-[320px]`/`max-w-[380px]` wider than the
  phone viewport causes overflow — make it fluid: `w-full sm:w-[320px]`.
- **Line length 45–75 characters** for readable prose.

## Verification (required)

- **Hard gate:** **zero horizontal overflow at 320px** on every route. Nothing may push the page
  wider than the viewport at the smallest supported width.
- **Automated viewport sweep** across **320 / 375 / 768 / 1024 / 1280** that, per route, asserts (a) no
  horizontal overflow (`document.documentElement.scrollWidth <= clientWidth`) and (b) — on the marketing
  route at mobile widths — the hamburger OPENS and reveals the nav links. This runs as the L1 layer of
  the single verify-pwa command (the scaffolded `audit-responsive.mjs`) and its results land in the one
  `PWA_REPORT.html`. It is the regression guard.
- Automation can't judge visual feel; still spot-check the key pages by eye at least once.

### L1 is the scaffolded `audit-responsive.mjs` — do NOT build a separate Playwright project

**The viewport sweep already ships as one of the six scaffolded scripts** (`audit-responsive.mjs`, from
`templates/audit-responsive.template.mjs`). It is the SINGLE responsive implementation feeding the SINGLE
`PWA_REPORT.html` — the former standalone Playwright test project (`playwright.config.ts` + an `e2e/` spec)
has been MERGED into it. Do not re-create a Playwright config or spec from scratch; scaffold this script
(Step 3) and drive everything through it. It uses Playwright's `chromium` as a library and, for each route
in the anchor's `routes`, sweeps 320/375/768/1024/1280. It is robust by construction:

- **Idempotent server** — reuses a server already serving the base URL, else auto-starts `npm run dev`
  and tears it down after (mirrors Playwright's `webServer` + `reuseExistingServer`).
- **Self-signed HTTPS** — every context uses `ignoreHTTPSErrors`; readiness is probed with a
  cert-tolerant browser navigation (Node `fetch` rejects the dev cert, so it can't be used).
- **Resilient navigation** — waits for `'load'` (not `'networkidle'`, which never settles while the dev
  HMR socket is open) and retries the first cold-compile load once, so a slow on-demand Vite transform is
  never mistaken for a layout defect.
- **Anchor-driven, nothing hardcoded** — routes come from `pwa.json` `routes`; the optional mobile
  hamburger check comes from `pwa.json` `mobile_nav_check` (`{route, trigger_label, reveal_link}`) — omit
  that key for apps with no hamburger.
- **Feeds the one report** — writes `responsive-audit.json` (naming the offending element on overflow),
  which `generate-reports.mjs` folds into `PWA_REPORT.html`. It runs as LAYER 1 of the single verify-pwa
  command (before the L2 PWA + Lighthouse layers) — there is NO separate responsive command to wire.
- **Authenticated routes** — list only public routes in `routes`; private routes need a logged-in
  `storageState` fixture, which this script does not set up — cover them manually or extend the script.

## Best practices (summary)

- Mobile-first; base = phone, enhance upward.
- Fluid units (`%`, `rem`, `vw`, `clamp()`) over fixed px; reserve fixed px for genuinely fixed things.
- One `<Container>` (max 1024) — never re-hardcode section widths.
- Reuse `Sidebar` / `Sheet` / `Drawer` / `useIsMobile` from shadcn (`npx shadcn@latest add sidebar sheet drawer dialog`).
- CSS Grid for 2D, Flexbox for 1D / nav.
- 48px touch targets; 45–75ch measure.
- Prove it: 320px no-overflow via the scaffolded `audit-responsive.mjs` viewport sweep.

## Resources

- [MDN Flexbox Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout)
- [MDN Grid Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [Anthropic — Build responsive web layouts](https://claude.com/blog/build-responsive-web-layouts)

---

# LEVEL 2 — Progressive Web App (requires a passing Level 1 report)

A "true PWA" is three hard gates: **installable** (manifest + icon set + HTTPS), **offline-capable**
(a service worker precaching the app shell), and **updatable** (a defined new-deploy flow). Level 1
makes it work on every screen; Level 2 makes it installable and offline — orthogonal axes. Every rule
in the tracks below is a checklist item in `CHECKLIST.md` (§ "LEVEL 2"), explained here in detail.

Canonical machinery: **`vite-plugin-pwa`** (wraps Workbox); on Next.js use **Serwist** (`@serwist/next`).
Never hand-write the service worker or a manual `manifest.json` when the plugin can generate both.
HTTPS is mandatory (localhost exempt in dev) — Netlify/Vercel already provide it. **No Cloudflare /
edge / backend is needed for offline**: a Service Worker runs in the browser on the user's device,
not on a server — do not confuse it with a Cloudflare Worker (same name, unrelated).

## Track 1 — App-ification (implementation)

### Manifest (single source of truth = plugin config, not a hand-written file)
Required: `name`, `short_name` (≤12 chars), `description`, `id`, `start_url` (`/`), `scope` (`/`),
`display: "standalone"`, `theme_color`, `background_color`, and an `icons` array. Keep `theme_color`
in sync with `<meta name="theme-color">`.

### Icons (what most audits fail on — raster PNGs, not SVG)
Generate from the brand SVG; reference in the manifest:
- `icon-192.png` (192×192, `purpose:"any"`)
- `icon-512.png` (512×512, `purpose:"any"`)
- `icon-512-maskable.png` (512×512, `purpose:"maskable"` — logo within the inner 80% safe zone, full-bleed brand background)
- `apple-touch-icon.png` (180×180) + `<link rel="apple-touch-icon" href="…">` (iOS ignores the manifest for this)

Automate as an `npm run icons` script (sharp / rsvg-convert / ImageMagick) — never hand-export.

### Service worker + caching (`vite-plugin-pwa`)
- `registerType`: `autoUpdate` (content/marketing) OR `prompt` (dashboards — show a "New version — Reload"
  toast via `useRegisterSW` from `virtual:pwa-register/react`). Always handle the update + `offlineReady` events.
- Precache the hashed build output automatically; add `workbox.runtimeCaching` per resource type:

  | Resource | Strategy | Why |
  |---|---|---|
  | HTML / navigations | NetworkFirst (+ `navigateFallback: '/index.html'`) | reflect latest deploy; offline shell |
  | hashed JS/CSS (build output) | precache (auto) | immutable, content-hashed |
  | images (same-origin) | StaleWhileRevalidate (cap entries + maxAge) | fast + self-heal |
  | fonts | CacheFirst (long maxAge) | rarely change |
  | API GET | NetworkFirst (short timeout) or SWR for non-critical | freshness vs offline |
  | API writes (POST/PUT) | NetworkOnly (+ optional Background Sync) | never serve stale writes |

- **Never** serve HTML/navigations with CacheFirst — users get stuck on an old deploy forever.

### iOS specifics
`apple-touch-icon` + `apple-mobile-web-app-capable` / `-status-bar-style` / `-title` metas. No install
prompt on iOS — detect iOS + not-standalone and show manual "Share → Add to Home Screen". The SW cache
may be evicted after ~7 days idle; treat it as a performance/offline layer, not durable storage.

## Track 2 — Audit & report (local, deterministic; saved into the repo)

**Lighthouse removed the PWA category in v12 (Oct 2025)** — so PWA installability is no longer a
Lighthouse audit. Split verification into a quality audit + explicit PWA checks:

1. **Build + serve the production build locally** (no deploy needed):
   `npm run build && npm run preview` → e.g. `http://localhost:4173` (or point at the deployed URL).
2. **Lighthouse CLI — quality only, NO SEO** (SEO is owned by `react-seo-planner`, which goes deeper):
   ```bash
   npx lighthouse http://localhost:4173 \
     --only-categories=performance,accessibility,best-practices \
     --output=json --output=html --output-path=./reports/pwa_scores/lighthouse \
     --chrome-flags="--headless=new" --quiet
   ```
   Lighthouse's only scored categories are **performance, accessibility, best-practices, seo** — pick
   the ones you want (here: the first three). Beyond categories the CLI also supports
   `--only-audits`/`--skip-audits`, performance budgets (`--budget-path`), `--preset=desktop`,
   CSV output, treemap/bundle data (`--save-assets`), and third-party **plugins** that add extra
   categories; user-flow (timespan/snapshot) audits are Node-API only. Accessibility is axe-core under the hood.
3. **MANDATORY — deterministic PWA checks via a headless Playwright + CDP script.** This REPLACES the
   removed Lighthouse PWA category and is **not optional**: you MUST create the script below, run it,
   and paste its JSON output + exit code as the evidence for the L2-A/B/D checklist items. Write it to
   `scripts/pwa-checks.mjs`:

   ```js
   // scripts/pwa-checks.mjs — headless PWA installability/offline audit (Playwright + CDP)
   import { chromium } from '@playwright/test';
   import fs from 'node:fs';

   const url = process.argv[2] || 'http://localhost:4173';
   const results = [];
   const rec = (id, ok, detail = {}) => results.push({ id, ok, detail });

   const browser = await chromium.launch();
   const page = await browser.newPage();
   await page.goto(url, { waitUntil: 'networkidle' });
   await page.reload({ waitUntil: 'networkidle' }); // 2nd load so the SW actually controls the page

   // Manifest + installability errors (the exact signal Chrome uses for the install prompt)
   const cdp = await page.context().newCDPSession(page);
   const app = await cdp.send('Page.getAppManifest');
   let manifest = {};
   try { manifest = JSON.parse(app.data || '{}'); } catch {}
   rec('L2-A4 installable (no CDP errors)', (app.errors ?? []).length === 0, { errors: app.errors });

   // Required manifest fields
   const need = ['name','short_name','start_url','scope','display','theme_color','background_color','icons'];
   rec('L2-A1 manifest fields', need.every((k) => k in manifest), { missing: need.filter((k) => !(k in manifest)) });

   // Raster icons: 192, 512, 512-maskable, apple-touch
   const icons = manifest.icons ?? [];
   const hasIcon = (sz, purpose) => icons.some((i) => (i.sizes||'').includes(sz) && (!purpose || (i.purpose||'').includes(purpose)));
   rec('L2-A2 icon-192', hasIcon('192x192'));
   rec('L2-A2 icon-512', hasIcon('512x512'));
   rec('L2-A2 icon-512-maskable', hasIcon('512x512','maskable'));
   rec('L2-D1 apple-touch-icon <link>', (await page.locator('link[rel="apple-touch-icon"]').count()) > 0);

   // <meta name="theme-color"> present in the served HTML AND matching the manifest
   const metaTheme = await page.locator('meta[name="theme-color"]').first().getAttribute('content').catch(() => null);
   rec('L2-A3 <meta theme-color> present', !!metaTheme, { metaTheme });
   rec('L2-A3 theme-color matches manifest', !!metaTheme && metaTheme.toLowerCase() === String(manifest.theme_color||'').toLowerCase(), { metaTheme, manifest: manifest.theme_color });

   // Service worker: registered, ACTIVE, controls the page, and scope covers start_url
   const sw = await page.evaluate(async () => {
     const reg = await navigator.serviceWorker.getRegistration();
     return { controller: !!navigator.serviceWorker.controller, active: !!reg?.active, scope: reg?.scope ?? null };
   });
   const startUrl = new URL(manifest.start_url || '/', url).href;
   rec('L2-B1 SW controls page', sw.controller && sw.active, sw);
   rec('L2-B1 SW scope covers start_url', !!sw.scope && startUrl.startsWith(sw.scope), { scope: sw.scope, startUrl });

   await browser.close();
   fs.mkdirSync('reports/pwa_scores', { recursive: true });
   fs.writeFileSync('reports/pwa_scores/pwa-checks.json', JSON.stringify({ url, results }, null, 2));
   const fail = results.filter((r) => !r.ok);
   console.log(JSON.stringify({ pass: results.length - fail.length, fail: fail.length, results }, null, 2));
   process.exit(fail.length ? 1 : 0);
   ```

   Run it against the locally-served production build (Step 1) and paste the output:
   ```bash
   node scripts/pwa-checks.mjs http://localhost:4173
   ```
   A non-zero exit = one or more PWA gates FAIL — fix, then re-run. **Never** hand-inspect the DevTools
   Application panel in place of this script.

4. **Classic Lighthouse PWA report (pinned `lighthouse@11`) — reproduce the full PWA category from the
   CLI.** Lighthouse 12+ deleted the PWA category, but **v11 is the last version that still has it**, so
   pinning it is the sanctioned CLI way to regenerate the exact classic PWA report (installable,
   splash-screen/512-PNG, apple-touch-icon, maskable, SW-controls-`start_url`, theme-color, viewport):
   ```bash
   npx -y lighthouse@11 http://localhost:4173 --only-categories=pwa \
     --output=json --output=html --output-path=./reports/pwa_scores/lighthouse-pwa \
     --chrome-flags="--headless=new" --quiet
   ```
   Run this in ADDITION to the Step-3 script: the Step-3 script is the forward-compatible source of
   truth; the v11 report is the familiar visual PWA card. Paste the resulting PWA scores as evidence.

5. **Determinism (all CLI / headless — never a hosted service or manual browser):** Lighthouse perf
   timings vary run-to-run (simulated throttling). For stable numbers run **median-of-3**, or use
   **Sitespeed.io** (open-source CLI, self-hosted — NOT a SaaS; real browsers + real network throttling +
   N-run medians, the most reproducible option; can also run the underlying Lighthouse audits). For
   multi-route apps, **Unlighthouse** (CLI) crawls every route and audits them in one pass.

### Audit scripts + anchor (Level 2 — scaffold from skill templates)

Every project scaffolds these files from the skill's templates. Once scaffolded they run standalone (no
runtime dependency on the skill). The ONLY thing the skill leaves behind that they read is the anchor
`ai_skill_anchors/pwa.json`. Scaffold each file with the SAME name minus `.template` (a byte-for-byte copy
— the scripts read every project-specific value from the anchor, so there is NOTHING to edit inside them).

| Scaffold into the project | From template | Customize |
|---------------------------|---------------|-----------|
| `ai_skill_anchors/pwa.json` | `templates/pwa.template.json` | all fields — analyze the project, then **confirm with the user** (Step 2): `project`, `app_dir`, `routes`, `scripts_dir`, `reports_root`, `production_url` |
| `<scripts_dir>/create-reports-directory.mjs` | `templates/create-reports-directory.template.mjs` | none (reads anchor) |
| `<scripts_dir>/verify-pwa.mjs` | `templates/verify-pwa.template.mjs` | none (reads `app_dir` from anchor) |
| `<scripts_dir>/audit-responsive.mjs` | `templates/audit-responsive.template.mjs` | none (reads `routes` from anchor) |
| `<scripts_dir>/audit-pwa.mjs` | `templates/audit-pwa.template.mjs` | none (reads anchor) |
| `<scripts_dir>/audit-lighthouse.mjs` | `templates/audit-lighthouse.template.mjs` | none (reads `app_dir` from anchor) |
| `<scripts_dir>/generate-reports.mjs` | `templates/generate-reports.template.mjs` | none (reads anchor) |

**Reports location is anchor-driven — never hardcode it.** Every audit script imports
`create-reports-directory.mjs`, which reads `reports_root` from `ai_skill_anchors/pwa.json` and writes to
`<reports_root>/pwa_scores`. Scripts MUST NOT hardcode a reports path or fall back to a root-level /
cwd-relative folder. **ASK THE USER for `reports_root` when scaffolding — do not guess it.**

**The anchor `ai_skill_anchors/pwa.json` is REQUIRED and MUST be scaffolded from `templates/pwa.template.json`.**
Use ONLY the keys in that template — do not invent others. It is the skill↔project bridge AND the single
source of truth the scripts read: `reports_root`, `app_dir`, and `routes` are consumed by code; the rest
(`project`, `scripts_dir`, `production_url`, the `scripts` map) documents the scaffold. Keep it minimal.
(The `.mjs`/code files must NOT mention the skill; the anchor `pwa.json` is the single place that references
both skill and project.)

**First run:** analyze the project and confirm every anchor field with the user (Step 2), scaffold the files
above byte-for-byte, then run the orchestrator (Makefile target / npm script). With no target it builds +
serves a preview on :4173; pass an external URL (e.g. `PWA_TARGET=<url>`) to audit a deployed/production
origin instead.

### Report files (written to `<reports_root>/pwa_scores/`)
```
responsive-audit.json                  # L1 gate result + detail (prints the offending element on overflow, clip-aware)
pwa-checks.json                        # manifest / icons / SW / installability pass-fail
lighthouse.report.{json,html}          # performance / accessibility / best-practices (v12)
lighthouse-pwa.report.{json,html}      # classic PWA category (pinned lighthouse@11)
verify-app-report.json                 # unified orchestrator report
PWA_REPORT.md                          # TABULAR scored summary (1 row/checklist item) + prioritized fixes
```
The audit architecture inventory now lives in `ai_skill_anchors/pwa.json` (NOT in the reports folder).

## Tooling (Level 2 devDeps — all CLI, headless-automatable)
`vite-plugin-pwa` (or `@serwist/next`), `lighthouse` (or `@lhci/cli`), `@playwright/test`
(already a Level 1 dep — reused for the `scripts/pwa-checks.mjs` CDP check), and `sharp`
(icon rasteriser). Run on demand with no install: `lighthouse@11` via `npx -y` (classic PWA category).
Optional: `sitespeed.io` (deterministic multi-run), `unlighthouse` (whole-site). Install/verify all of
these up front via the **Prerequisite — Tooling** step at the top of this skill. Every check runs
headless from the CLI — no manual DevTools inspection, no hosted/SaaS dashboards.

## Anti-patterns (reject in review)
- SVG-only manifest icons; maskable icon with no safe zone.
- CacheFirst on HTML/navigations (permanently stale app after deploys).
- Hand-rolled service worker when `vite-plugin-pwa`/Serwist suffices.
- Registering the SW but ignoring the update event (users stuck on old bundles).
- Treating the SW cache as durable user storage (esp. iOS eviction).
- Auditing PWA with `--only-categories=pwa` on the LATEST Lighthouse (removed in v12 — errors out).
  To regenerate the classic PWA-category report, pin `npx -y lighthouse@11 --only-categories=pwa` (Track 2, step 4).
- Relying on a manual DevTools/browser check or a hosted/SaaS dashboard for verification — every
  audit must be a headless CLI step reproducible in CI (drive the browser via Playwright/Lighthouse).
- Running SEO here — defer to `react-seo-planner`.

## Resources (Level 2)
- vite-plugin-pwa · Workbox strategies · web.dev/learn/pwa · MDN Web App Manifest · Serwist (Next.js)
- Sitespeed.io (deterministic multi-run CLI) · Unlighthouse (whole-site CLI) · Playwright CDP `Page.getAppManifest` · Lighthouse CLI
