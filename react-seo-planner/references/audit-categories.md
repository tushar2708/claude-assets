# Audit Categories — 24-Category SEO + GEO Checklist

Work through every category in order during Step 3 of the skill workflow.
For each check: ✅ PASS · ⚠️ WARN · ❌ FAIL — record FAILs and WARNs in the Issue Log.

**Categories 1–16**: Traditional SEO (code-level codebase analysis)
**Categories 17–24**: GEO — Generative Engine Optimization (live site + codebase analysis)
→ Full GEO checklists, scoring rubrics, and fix guidance: [geo-categories.md](geo-categories.md)
→ Platform-specific checklists (AIO, ChatGPT, Perplexity, Gemini, Copilot): [platform-optimization.md](platform-optimization.md)

---

## Category 1 — HTML Shell & Document Head

Read `index.html` (or `public/index.html`).

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| DOCTYPE | `<!DOCTYPE html>` is the very first line | Critical |
| Language | `<html lang="xx">` has a valid BCP-47 code | High |
| Charset | `<meta charset="utf-8">` is first in `<head>` | High |
| Viewport | `<meta name="viewport" content="width=device-width, initial-scale=1">` | High |
| Root element | Body has a single `<div id="root">` with no extra markup | Medium |

---

## Category 2 — Page Titles & Meta Descriptions

Check every route component from the page inventory.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Title present | Every route sets a `<title>` via react-helmet-async (or equivalent) | Critical |
| Title length | 30–60 characters | High |
| Title unique | No two routes share the same title string | High |
| Description present | Every route sets `<meta name="description">` | High |
| Description length | 100–160 characters | Medium |
| Description unique | No two routes share the same description | Medium |

If no helmet library is used at all, mark entire category FAIL (Critical) and flag it as the first dependency to add in Wave 0.

---

## Category 3 — Headings & Page Structure

Check every route component's rendered JSX.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Exactly one `<h1>` | Every page has exactly one `<h1>` | FAIL (Critical) |
| Heading hierarchy | No skipped levels (e.g., `<h1>` → `<h3>` without `<h2>`) | High |
| `<h1>` content | Contains the page's primary keyword, not a logo or icon | Medium |
| Semantic HTML | Main content in `<main>`, navigation in `<nav>`, footer in `<footer>` | Medium |

Zero `<h1>` tags or more than one `<h1>` is always FAIL — never WARN.

---

## Category 4 — Images: Alt Text, Size, and Loading

Grep for `<img` across all component files.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Alt attribute | Every `<img>` has an `alt` attribute (empty string `alt=""` is valid for decorative) | High |
| Descriptive alt | Meaningful images have descriptive alt text (not "image" or filename) | High |
| Width + Height | `<img>` elements have explicit `width` and `height` to prevent layout shift | Medium |
| Modern formats | Images use webp or avif where possible | Low |
| Lazy loading | Below-the-fold images have `loading="lazy"` | Medium |

If no `<img>` tags exist in the codebase, mark PASS with note "No images found."

---

## Category 5 — Internal Links & Navigation

Grep for `<a` and `<Link` across all component files.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Descriptive link text | No "click here", "read more", "learn more" anchor text | High |
| Href present | No `<a>` without `href` (except intentional buttons) | High |
| No orphan pages | Every important page is reachable by at least one internal link | High |
| No broken `<Link to="">` | All `<Link>` targets match a route in the router config | Critical |

---

## Category 6 — Routing, URLs & Status Codes

Check the router config and any custom server config.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Clean URLs | No query-string-only navigation for primary routes (use path segments) | Medium |
| 404 route | A catch-all `*` route renders a proper 404 page | High |
| Canonical tags | Duplicate content routes (e.g., `/app` and `/app/`) have `<link rel="canonical">` | Medium |
| Trailing slash consistency | App consistently uses or avoids trailing slashes (not mixed) | Medium |
| No hash routing | `BrowserRouter`/`createBrowserRouter` used, not `HashRouter` | High |

---

## Category 7 — Structured Data

Check for JSON-LD blocks in components or the HTML shell.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| WebSite schema | Root layout or `index.html` contains `@type: "WebSite"` JSON-LD | High |
| Organization schema | Root layout contains `@type: "Organization"` with name, url, logo | High |
| Valid JSON | All JSON-LD blocks are valid JSON (no trailing commas, proper quotes) | Critical |
| schema.org types | Types reference schema.org (not made-up types) | High |
| Rich result opportunities | Pages like articles, FAQs, or products have appropriate schemas | Low |

Validate every JSON-LD block via the Rich Results Test API — use WebFetch:
```
https://search.google.com/test/rich-results?url=[ENCODED_PAGE_URL]
```
Or use WebFetch on the Schema Markup Validator:
```
https://validator.schema.org/#url=[ENCODED_PAGE_URL]
```
If the page is not publicly deployed, validate by manually checking:
1. Is the JSON parseable? (No trailing commas, all strings quoted, balanced braces)
2. Does `@type` match a known schema.org type?
3. Are required properties present for that type?

---

## Category 8 — Performance Optimizations

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Code splitting (client-side routing only) | In `src/app/routes.tsx` (or equivalent `createBrowserRouter` file): route components use `React.lazy()` + `<Suspense>` for code splitting. ⚠️ **DO NOT use lazy() in build-time SSR scripts** (e.g., `src/prerender.tsx`) — SSR requires direct imports to render pages during build. | High |
| Font display | Web fonts use `font-display: swap` in CSS | Medium |
| No layout shift | Images and embeds have explicit dimensions | Medium |
| No render-blocking scripts | `<script>` in `index.html` use `defer` or `async` | Medium |
| Bundle size | No obvious oversized imports (lodash full bundle, moment.js, etc.) — check with: `Grep "from 'lodash'" OR "from 'moment'" OR "require('lodash')" across src/ files`. Also check `package.json` for these packages as direct dependencies. | Low |

---

## Category 9 — Mobile Friendliness

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Viewport meta | Already covered in Category 1 — confirm no override | Critical |
| Text readability | Base font size ≥ 16px in CSS | High |
| Tap targets | Interactive elements ≥ 44×44px (check CSS or Tailwind classes) | High |
| No horizontal scroll | No fixed-width containers wider than 100vw | High |
| Responsive layout | Layout uses relative units or Tailwind responsive prefixes | Medium |

---

## Category 10 — Analytics & Tracking

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Analytics present | Google Analytics, Plausible, or equivalent is installed | High |
| Async loading | Analytics scripts load with `async` or `defer` | Medium |
| Not in `<head>` blocking | Tracking pixels don't block HTML parse | Medium |
| Privacy compliance | Cookie consent banner present if analytics use cookies (GDPR regions) | Medium |

If no analytics exist, mark FAIL (High) and include a note that it's required for measuring SEO impact.

---

## Category 11 — Robots.txt & Sitemap.xml

Check `public/robots.txt` and `public/sitemap.xml` (or a sitemap generator).

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| robots.txt exists | File present at `/robots.txt` | High |
| Not blocking all | `Disallow: /` is absent (or only under non-Googlebot agents) | Critical |
| Sitemap referenced | `Sitemap:` directive in robots.txt points to sitemap URL | High |
| sitemap.xml exists | File present or dynamically generated | High |
| Sitemap includes all pages | Every important route appears in sitemap | High |
| Sitemap valid XML | Valid XML with `<urlset>` root and `<loc>` entries | High |

---

## Category 12 — Reusable SEO Components

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| `<SeoHead>` component exists | A shared component wraps react-helmet-async for consistent meta tags | Medium |
| Consistent usage | All route components use `<SeoHead>` (not ad-hoc Helmet blocks) | Medium |
| Default fallbacks | `<SeoHead>` has sensible default title/description for pages that forget to pass props | Low |
| Open Graph tags | `<SeoHead>` outputs `og:title`, `og:description`, `og:url` at minimum | Medium |
| Twitter Card tags | `<SeoHead>` outputs `twitter:card` and `twitter:title` | Low |

If no `<SeoHead>` exists, mark WARN and recommend creating one in Wave 0 as the foundation for all title/description fixes.

---

## Category 13 — QA Verification Per Page

Final cross-check for every page in the route inventory.

For **each** page in the page inventory table, verify:

| Check | Pass Condition |
|-------|---------------|
| Title set and unique | ✅ / ❌ |
| Description set and unique | ✅ / ❌ |
| Exactly one `<h1>` | ✅ / ❌ |
| Correct heading hierarchy | ✅ / ❌ |
| Internal link from at least one other page | ✅ / ❌ |

Produce a per-page QA table:

```
| Page         | Title | Desc | H1 | Hierarchy | Linked |
|--------------|-------|------|----|-----------|--------|
| /            | ✅    | ✅   | ✅ | ✅        | N/A    |
| /dashboard   | ❌    | ❌   | ✅ | ✅        | ✅     |
| /apps/:id    | ❌    | ❌   | ⚠️ | ✅        | ✅     |
| /settings    | ✅    | ✅   | ❌ | ❌        | ✅     |
```

Any ❌ in this table must have a corresponding FIX entry in the plan.

---

## Category 14 — Core Web Vitals (LCP, CLS, INP)

Google's Page Experience ranking signal since 2021. Measure using one of these methods:

**Option A — chrome-devtools-mcp tool (if browser is available):**
Use the `lighthouse_audit` tool with `mode: "navigation"` and `device: "desktop"` (then repeat with `device: "mobile"`).

**Option B — PageSpeed Insights API (no browser required):**
Use WebFetch:
```
https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=[ENCODED_URL]&strategy=desktop
```
The response JSON contains `lighthouseResult.categories.performance.score` (multiply by 100 for 0-100 score) and `lighthouseResult.audits['largest-contentful-paint'].displayValue` for LCP.

**Option C — Static code analysis only (if no deployed URL):**
Assess risk from the code patterns listed below — flag as "estimated risk" not measured score.

These are real ranking factors, not just nice-to-have.

| Metric | Full Name | Good Threshold | Poor Threshold | Severity if Poor |
|--------|-----------|---------------|----------------|------------------|
| LCP | Largest Contentful Paint | ≤ 2.5s | > 4s | High |
| CLS | Cumulative Layout Shift | ≤ 0.1 | > 0.25 | High |
| INP | Interaction to Next Paint | ≤ 200ms | > 500ms | High |

### What to check in code:

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| LCP element identified | Lighthouse identifies LCP element; it's a real content element (not a spinner) | High |
| Images have dimensions | `<img>` with explicit `width`/`height` prevents layout shift during load | High |
| No FOUC | Fonts load with `font-display: swap`; no flash of invisible text | Medium |
| No dynamic content injection | No ads, embeds, or late-injecting banners that shift layout above the fold | High |
| Heavy route components lazy-loaded (client-side only) | In `src/app/routes.tsx`: use `React.lazy()` + `<Suspense>` for large routes (keeps initial bundle small → better LCP). ⚠️ **NOT for build-time SSR scripts** — those must use direct imports. | Medium |
| Long tasks avoided | No synchronous operations > 50ms in event handlers (INP) | Medium |

### How to instrument in React:

Install the `web-vitals` library (free, Google-maintained) to measure CWV in real user sessions:

```bash
npm install web-vitals
```

```tsx
// src/app/vitals.ts
import { onCLS, onINP, onLCP } from 'web-vitals';

export function reportWebVitals() {
  onCLS(console.log);   // replace with your analytics send() call
  onINP(console.log);
  onLCP(console.log);
}
```

```tsx
// src/main.tsx
import { reportWebVitals } from './app/vitals';
// ... after ReactDOM.createRoot().render()
reportWebVitals();
```

Send the metric objects to GA4 as custom events (see tools-and-analytics.md for the full GA4 setup).

---

## Category 15 — Social Tags (Open Graph + Twitter Cards)

When a URL is shared on Slack, LinkedIn, Twitter/X, iMessage, or WhatsApp, the social platform reads Open Graph meta tags to build the link preview. Missing or wrong OG tags produce ugly unfurled links — a direct conversion hit.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| `og:title` | Present on every page; matches `<title>` or is slightly longer (social allows more chars) | High |
| `og:description` | Present on every page; matches or expands `meta description` | High |
| `og:url` | Canonical URL of the page (no trailing slash inconsistency) | High |
| `og:image` | Absolute URL to a 1200×630px image (minimum); served over HTTPS | High |
| `og:type` | `"website"` for most pages; `"article"` for blog posts | Medium |
| `og:site_name` | App/company name | Low |
| `twitter:card` | `"summary_large_image"` for pages with a meaningful image | High |
| `twitter:title` | Same as `og:title` (some scrapers prefer explicit Twitter tags) | Medium |
| `twitter:description` | Same as `og:description` | Medium |
| `twitter:image` | Same absolute URL as `og:image` | Medium |

### Example `<SeoHead>` with full OG + Twitter tags:

```tsx
import { Helmet } from 'react-helmet-async';

interface SeoHeadProps {
  title: string;
  description: string;
  canonicalUrl: string;
  ogImage?: string;
}

const DEFAULT_OG_IMAGE = 'https://yourdomain.com/og-default.png';

export function SeoHead({ title, description, canonicalUrl, ogImage = DEFAULT_OG_IMAGE }: SeoHeadProps) {
  const fullTitle = `${title} · Acme Cloud`;
  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={canonicalUrl} />

      {/* Open Graph */}
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="Acme Cloud" />

      {/* Twitter / X */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />
    </Helmet>
  );
}
```

### Validation tools (free):
- **Facebook / Meta Sharing Debugger**: https://developers.facebook.com/tools/debug/ — paste any URL to see exactly how Facebook/Instagram would render the preview
- **Twitter Card Validator**: https://cards-dev.twitter.com/validator — deprecated but still works; use browser inspect of Twitter share for current check
- **LinkedIn Post Inspector**: https://www.linkedin.com/post-inspector/ — checks LinkedIn-specific OG rendering

---

## Category 16 — Optional Advanced Checks

Score this category as **N/A** if none of the triggers apply. Only audit if the app specifically uses these features.

### 16a. Hreflang (Multi-Language Sites)

Apply only if the app serves content in more than one language or for more than one geographic region.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| `hreflang` present | `<link rel="alternate" hreflang="xx" href="...">` for each language variant | High |
| `x-default` present | One `hreflang="x-default"` pointing to the fallback URL | High |
| Self-referencing | Each page includes its own URL in the hreflang set | High |
| Consistent across variants | All language variants point to each other reciprocally | High |

### 16b. Content Security Policy (CSP)

CSP doesn't directly affect rankings, but it affects trust signals and can prevent drive-by crawlers from poisoning your link graph.

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| CSP header present | `Content-Security-Policy` header set in server or CDN config | Low |
| No `unsafe-inline` scripts | CSP uses nonces or hashes instead of `unsafe-inline` | Medium |
| Reporting endpoint | `report-uri` or `report-to` directive logs violations | Low |

### 16c. JavaScript-Heavy Pages & Dynamic Rendering

React SPAs serve an empty HTML shell to crawlers. Googlebot can render JavaScript, but there is a 2-4 week rendering lag compared to HTML-first content. If the app has important SEO content inside JS-rendered components:

| Check | Pass Condition | Severity if Failing |
|-------|---------------|----------------------|
| Critical text in initial HTML | Key headings and content visible in `curl` response (no JS required) | High |
| Dynamic rendering available | Prerender.io, Rendertron, or Netlify pre-rendering configured for bot traffic | Medium |
| SSR considered | If dynamic rendering is not configured AND content is JS-only, note as High risk | High |

### 16d. Additional Structured Data Opportunities

Beyond the mandatory WebSite and Organization schemas (Category 7), flag these when applicable:

| Schema Type | When to Add | schema.org URL |
|-------------|-------------|----------------|
| `BreadcrumbList` | Pages deeper than 2 levels in hierarchy | schema.org/BreadcrumbList |
| `FAQPage` | Pages with FAQ sections | schema.org/FAQPage |
| `Article` | Blog posts or documentation | schema.org/Article |
| `Product` | Product listing pages | schema.org/Product |
| `Review` | Review sections on pages | schema.org/Review |
| `HowTo` | Step-by-step instructional content | schema.org/HowTo |

Always validate with https://search.google.com/test/rich-results before including in the fix plan.

---

## Categories 17–24 — GEO (Generative Engine Optimization)

These categories require a **deployed URL** in addition to codebase analysis. Run them in Step 2.5 (Live Site Fetch) after the user provides the live URL. Full scoring rubrics and fix guidance are in [geo-categories.md](geo-categories.md).

| # | Category | Requires Live URL | Key Metric | Agent File |
|---|----------|------------------|------------|------------|
| 17 | AI Crawler Access | Yes | Crawler Access Score /100 | — |
| 18 | AI Citability | Yes | Citability Score /100 | agents/geo-ai-visibility.md |
| 19 | llms.txt Compliance | Yes | llms.txt Score /100 | agents/geo-ai-visibility.md |
| 20 | E-E-A-T Content Quality | Yes + code | Content Score /100 | agents/geo-content.md |
| 21 | Brand Authority | Yes | Brand Mention Score /100 | agents/geo-ai-visibility.md |
| 22 | Platform-Specific (AIO/ChatGPT/Perplexity/Gemini/Copilot) | Yes | Platform Readiness /100 each | agents/geo-platform-analysis.md |
| 23 | Structured Data — GEO Extensions | Yes + code | Schema Score /100 | agents/geo-schema.md |
| 24 | SSR for AI Crawlers | Yes + code | SSR Score /100 | agents/geo-technical.md |

### AI Visibility Composite Score
`AI_Visibility = (Citability * 0.35) + (Brand_Mentions * 0.30) + (Crawler_Access * 0.25) + (LLMS_TXT * 0.10)`

Interpretation: 0–20 Critical · 21–40 Poor · 41–60 Fair · 61–80 Good · 81–100 Excellent

### Scripts available for GEO categories
- `scripts/citability_scorer.py <url>` — Score every content block for AI citation readiness
- `scripts/brand_scanner.py <brand_name> [domain]` — Check brand presence across AI-cited platforms
- `scripts/fetch_page.py <url>` — Fetch and parse HTML for analysis
- `scripts/llmstxt_generator.py <url>` — Generate/validate llms.txt
- Install requirements: `pip install -r requirements.txt` (beautifulsoup4, requests, lxml, validators)

### React SPA constraint for Cat 24
**Never** suggest migrating to Next.js, Gatsby, Remix, or any other framework for SSR fixes.

**Recommended SSR fix for a Vite/React SPA (verified working, incl. on AWS Amplify):** a **build-time Puppeteer
prerender** — after `vite build`, a small script serves `dist/` on a local static server (with SPA fallback),
launches the current `puppeteer` package, navigates each public route, waits for a route-specific selector, captures
`page.content()`, and writes `dist/<route>/index.html`. Chain it into the build target so local and CI/CD run the
identical command. Pair it with a tool-agnostic entry: `hydrateRoot(root, <App/>)` when `#root.hasChildNodes()`
(prerendered), else `createRoot(root).render(<App/>)`. This needs **no** framework migration and **no** Amplify
BuildSpec change (Amplify resolves Puppeteer's Chromium during `npm ci`). Use only the stable Puppeteer APIs
(`goto`/`waitForSelector`/`content`).

**Do NOT recommend `react-snap`** — it is unmaintained and bundles a 2019 Chromium that cannot parse modern JS (build
fails with `SyntaxError: Unexpected token '?'`). Also avoid `@prerenderer/prerenderer` (breaks on Puppeteer 23+ with
`ProtocolError: Promise was collected`). prerender.io / Cloudflare Workers / Netlify prerender / Vercel Edge remain
valid *hosting-side* alternatives, but the build-time Puppeteer approach above is the preferred in-repo fix.

**Common pitfall to check when a build-time prerender already exists:** if every route serves the *home* page's
markup, the prerender is likely (a) overwriting the SPA-fallback shell (`dist/index.html`) with the first route's
output, so later routes snapshot stale markup, and/or (b) waiting on a generic `h1` that already exists in the served
markup under `hydrateRoot`. Fix: serve the fallback from a pristine shell copy and wait on a route-specific marker.
