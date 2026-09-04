# Progressive Web App — Compliance Checklist

The single source of truth for **both** uses:

1. **Plan-time (compliance):** every frontend plan MUST include a task for each applicable item
   below. A plan that touches a layer without covering its checklist items is incomplete.
2. **Post-implementation (review):** after code is written, re-verify each applicable item and mark
   it **PASS / FAIL** with **pasted evidence** (a command log, an assertion result, or a screenshot).
   No item is "done" on a claim — only on evidence.

Scope tags: **[L1]** = responsive foundation (always applies to any UI change). **[L2]** = PWA
(applies when install/offline/manifest/service-worker work is in scope). Level 2 items are only
checked once the Level 1 items pass.

Each item: `ID · rule · how to verify (deterministic)`. Record results in `reports/pwa_scores/`
(see the skill's report section). **This file is a pointer list** — the full explanation of every
item (the *why* and the exact Tailwind / shadcn / PWA *how*) lives in `SKILL.md`, whose section
headings mirror the groups below. If an item here has no explanation in `SKILL.md`, that is a gap to
fix — keep the two in sync.

---

## PREREQUISITE — Tooling (verify before any work; install if missing — see SKILL.md "Prerequisite")
- [ ] **PRE-1 Node 18+ / npx** present. *Verify:* `node -v && npx -v`.
- [ ] **PRE-2 Playwright + Chromium** installed (L1 suite + L2 CDP check). *Verify:* `npx playwright --version` then `npx playwright install chromium`.
- [ ] **PRE-3 Lighthouse CLI** available (L2). *Verify:* `npx lighthouse --version`.
- [ ] **PRE-4 `vite-plugin-pwa`** in the project (L2, when shipping a SW). *Verify:* `npm ls vite-plugin-pwa`.
- [ ] **PRE-5 `sharp`** icon rasteriser (L2, when generating icons). *Verify:* `node -e "require('sharp')"`.
- [ ] **PRE-6 `lighthouse@11`** resolvable on demand for the classic PWA report (no install). *Verify:* `npx -y lighthouse@11 --version`.

A missing tool is installed then re-checked; a tool that cannot be installed is **FAIL/BLOCKED**, never PASS.

---

## LEVEL 1 — Responsive (gate for Level 2)

### L1-A · Layout system
- [ ] **L1-A1 Mobile-first** — base (unprefixed) classes target the phone; only `sm:`/`md:`/`lg:`/`xl:` add desktop. *Verify:* grep for desktop-first `max-*:` overrides; none should shrink layout down.
- [ ] **L1-A2 One `<Container>` (max 1024)** — a single container primitive caps content width + responsive gutters; no per-section `max-w-[…]` re-hardcoding. *Verify:* grep `max-w-\[[0-9]{3,}px\]` → only the Container defines it.
- [ ] **L1-A3 Grid** — known-count layouts use explicit responsive columns; variable-count use `auto-fit minmax()`. *Verify:* no fixed multi-col grid without a `grid-cols-1` mobile base.
- [ ] **L1-A4 Fluid type** — headings scale via `clamp()`. *Verify:* read heading classes.

### L1-B · Navigation
- [ ] **L1-B1 Marketing nav → hamburger `Sheet` below `md`** — links never just disappear; primary CTA stays visible. *Verify:* Playwright at 320/375 — trigger visible, opens, links reachable.
- [ ] **L1-B2 Dashboard sidebar = shadcn `Sidebar`, off-canvas below `md`** — persistent ≥ md via `SidebarInset`; NOT a hand-rolled `<aside>`. *Verify:* grep no `w-64`/`<aside`; component uses `SidebarProvider`/`Sidebar`.
- [ ] **L1-B3 Topbar hosts `SidebarTrigger` on mobile** — the off-canvas sidebar is always summonable; breadcrumbs collapse to current segment below md; search → icon. *Verify:* Playwright — trigger opens sidebar at 375.
- [ ] **L1-B4 Nothing orphaned** — org switcher, all nav groups, account/theme live inside the `Sidebar`. *Verify:* read the sidebar component.

### L1-C · Content patterns
- [ ] **L1-C1 Primary data tables → stacked cards below `md`** — `<table className="hidden md:table">` + a `md:hidden` label:value card list; no data silently dropped on desktop. *Verify:* read each primary table; Playwright no overflow at 320.
- [ ] **L1-C2 Dialogs → `Drawer` on mobile / `Dialog` on desktop** — branch with `useIsMobile()`; shared body (no duplicated JSX); `AlertDialog`s stay as-is. *Verify:* grep each modal for the `useIsMobile()` branch.
- [ ] **L1-C3 Media / code windows** — `img { max-w-full h-auto }`; code blocks scroll internally, never widen the page. *Verify:* read.

### L1-D · Touch & widths
- [ ] **L1-D1 48px touch targets** — every interactive control ≥ `min-h-12` on mobile (shadcn defaults are smaller). *Verify:* grep interactive controls for `min-h-12` on touch.
- [ ] **L1-D2 No viewport-exceeding fixed widths** — no `w-[NNNpx]`/`min-w-[NNNpx]` wider than 320. *Verify:* grep `w-\[[0-9]` / `min-w-\[[0-9]`.

### L1-E · Theming orthogonality
- [ ] **L1-E1 Responsive adds no breakpoints to theme CSS** — `@media` stays out of the theme/token layer; no per-theme responsive variant. *Verify:* grep the theme CSS for `@media` → none.
- [ ] **L1-E2 Holds in every theme** — layout is identical across all themes (light/dark/…); per-theme difference is a token, not a media query. *Verify:* Playwright/manual at each theme.

### L1-F · Verification gate (HARD)
- [ ] **L1-F1 Zero horizontal overflow at 320px on every route.** *Verify:* Playwright asserts `document.documentElement.scrollWidth <= clientWidth`.
- [ ] **L1-F2 Playwright viewport suite exists + green** across 320/375/768/1024/1280, with an **idempotent** `webServer` (`reuseExistingServer: true`). *Verify:* run the suite; paste the pass log.
- [ ] **L1-F3 Manual eye spot-check** of key pages (automation can't judge feel). *Verify:* screenshot.

---

## LEVEL 2 — PWA (requires L1 passing)

### L2-A · Installable
- [ ] **L2-A1 Web app manifest** with `name`, `short_name` (≤12), `description`, `id`, `start_url` `/`, `scope` `/`, `display: standalone`, `theme_color`, `background_color`, `icons`. Generated by the plugin, not hand-written. *Verify:* parse `/manifest.json`.
- [ ] **L2-A2 Raster icons** — `icon-192.png`, `icon-512.png`, `icon-512-maskable.png` (logo in inner 80% safe zone), `apple-touch-icon.png` (180). No SVG-only. *Verify:* assert files exist at declared sizes.
- [ ] **L2-A3 `<meta name="theme-color">` present in served HTML AND equal to `manifest.theme_color`.** *Verify:* `scripts/pwa-checks.mjs` L2-A3 rows PASS.
- [ ] **L2-A4 Installability** — Chrome offers install. *Verify:* `node scripts/pwa-checks.mjs <url>` — CDP `Page.getAppManifest` returns no installability errors (never a manual DevTools check).

### L2-B · Offline-capable
- [ ] **L2-B1 Service worker via `vite-plugin-pwa` (or Serwist on Next.js)** — never hand-written; precaches hashed build output; **actually controls the page** (`navigator.serviceWorker.controller`) with **scope covering `start_url`**. *Verify:* `dist/sw.js` exists; `scripts/pwa-checks.mjs` SW rows PASS.
- [ ] **L2-B2 Caching strategies per resource type** — HTML/navigations = NetworkFirst (+ navigateFallback); hashed JS/CSS = precache; images = SWR; fonts = CacheFirst; API GET = NetworkFirst; API writes = NetworkOnly. **Never CacheFirst on HTML.** *Verify:* read the plugin config.

### L2-C · Updatable
- [ ] **L2-C1 Update flow** — `registerType: autoUpdate` (content) or `prompt` (dashboards, show a reload toast); the update + `offlineReady` events are handled. *Verify:* read registration code.

### L2-D · iOS
- [ ] **L2-D1 iOS metas** — `apple-touch-icon` + `apple-mobile-web-app-*`; manual "Add to Home Screen" hint when iOS + not standalone; SW cache treated as non-durable. *Verify:* read `index.html` + install-hint code.

### L2-E · Audit & determinism (all headless CLI — no SaaS, no manual DevTools)
- [ ] **L2-E1 Lighthouse CLI — performance / accessibility / best-practices only (NOT SEO)** against the production build served locally. *Verify:* run; save JSON+HTML to `reports/pwa_scores/`.
- [ ] **L2-E2 Deterministic numbers** — median-of-3 (or Sitespeed.io); Unlighthouse for multi-route. *Verify:* saved run.
- [ ] **L2-E3 Report written (MANDATORY every run — audit AND post-impl; TABULAR)** — `level1-responsive.json`, `lighthouse.report.*`, `pwa-checks.json`, `PWA_REPORT.md` in `reports/pwa_scores/`. `PWA_REPORT.md` core is a per-item markdown table (columns: **ID · rule · state · evidence · verdict** [PASS/FAIL/GAP/NOT-RUN]), grouped by section. Prose-only findings = incomplete. Printing to chat instead of writing the file = FAIL. *Verify:* files exist; `PWA_REPORT.md` has the per-item table with evidence.
- [ ] **L2-E4 Deterministic PWA check script run** — `node scripts/pwa-checks.mjs <url>` executed against the locally-served build; JSON output + exit code pasted; `reports/pwa_scores/pwa-checks.json` written. *Verify:* pasted log.
- [ ] **L2-E5 Classic Lighthouse PWA report** — `npx -y lighthouse@11 <url> --only-categories=pwa` run; `reports/pwa_scores/lighthouse-pwa.*` saved + PWA scores pasted. *Verify:* saved report + pasted scores.

---

## Honesty rule (applies to every item, both uses)
A tick requires **pasted, reproducible evidence** — a real command log with its exit code, an
assertion result, or a screenshot. "Should pass", "looks correct", or reasoning about the code is
NOT evidence and is treated as a FAIL. If a check was skipped or blocked, record it as **FAIL /
BLOCKED**, never as PASS.

## No-skip / no-lie rule (mandatory — applies to every item)
- **Action every applicable item.** You may not silently skip, drop, or mark "N/A" an item that applies.
- **If you discover an item you did NOT actually work on** (or ticked without doing the work): (1)
  **surface it to the user explicitly** — name the item ID and state it was not done; (2) mark it
  **FAIL**; (3) **go back and do it** per the `SKILL.md` instructions before the run is considered complete.
- **Never claim an item is done without having run the skill's exact steps for it and captured the
  required evidence.** Overstating or fabricating completion is a critical skill violation.
- A run is **complete** only when every applicable item is either PASS-with-evidence or explicitly
  reported to the user as FAIL/BLOCKED with a reason — nothing left silently unverified or unsurfaced.
