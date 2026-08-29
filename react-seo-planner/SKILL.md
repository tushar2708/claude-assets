---
name: react-seo-geo-planner
description: |
  Combined SEO + GEO (Generative Engine Optimization) audit and fix-planning skill for React.js
  applications. Use when:
  (1) Auditing a React app for SEO or GEO issues
  (2) Asked to "check SEO", "review SEO", "improve search ranking", or "fix SEO"
  (3) Asked about "AI search", "GEO", "AI Overviews", "ChatGPT visibility", "Perplexity ranking"
  (4) Preparing a prioritized plan to fix SEO/GEO issues in a React codebase
  (5) Reviewing a specific page or the whole app for SEO/GEO compliance
  (6) Setting up Google Analytics 4 in a React app
  (7) Checking Core Web Vitals (LCP, CLS, INP) or social sharing (Open Graph, Twitter Cards)
  (8) Checking structured data (JSON-LD), schema.org markup, or entity linking (sameAs)
  (9) Analyzing readiness for Google AI Overviews, ChatGPT web search, Perplexity, Gemini, Bing Copilot
  Performs a strict 24-category audit (16 core SEO + 8 GEO categories), scores each category, and
  produces a prioritized fix plan with exact file paths and code diffs. Applies fixes directly to the
  codebase. Includes GEO agent sub-analyses for platform readiness, schema validation, content E-E-A-T,
  technical AI visibility, and AI brand presence. Maintains a reports/seo_geo_scores/ folder with 11 fixed output files across all runs.
  Never suggests migrating to Next.js, Gatsby, Remix, or any other framework.
---

# React SEO + GEO Planner

## Mandatory Chain-of-Thought Process

Before ANY audit work, execute these steps IN ORDER. Do not skip or reorder.

### Step 0: Define Audit Scope

**FIRST ACTION** — Establish scope before reading any code:

```
Audit scope:
- Target: [ ] Whole app  [ ] Specific page(s): _______________
- Deployed URL (optional, for GEO analysis): _______________
- Router file:   _______________
- Entry HTML:    _______________
- Public dir:    _______________
```

If scope is not clear from the request, ask the user before proceeding.

**Output folder (fixed — do not deviate):** All output goes in `reports/seo_geo_scores/` at the frontend project root. Exactly 11 files allowed — no more, no fewer:

```
reports/seo_geo_scores/
├── SEO-AUDIT.md             — Cats 1-16 scores, issue log, PASS/WARN/FAIL per category
├── GEO-CITABILITY.md        — Block-level citability (per H2/H3), rewrite suggestions for blocks < 60
├── GEO-CRAWLERS.md          — 14-crawler access map, recommendations, robots.txt template
├── GEO-LLMSTXT.md           — llms.txt + llms-full.txt + /ai.txt analysis and/or generation
├── GEO-SCHEMA.md            — Structured data validation (JSON-LD, sameAs gaps)
├── GEO-PLATFORM.md          — 5-platform readiness (AIO, ChatGPT, Perplexity, Gemini, Copilot)
├── GEO-CONTENT.md           — E-E-A-T and content quality scoring + brand presence
├── GEO-TECHNICAL.md         — Technical health: SSR, CWV, security, mobile
├── GEO-CLIENT-REPORT.md     — Client-facing deliverable (business owner audience, 3K-6K words)
├── FIX-PLAN.md              — Wave-by-wave prioritized fix plan with code diffs
└── SCORE-HISTORY.md         — Scores appended each run (Score History table)
```

**Invocation mode** (detect from user's request keywords before starting):

| Keyword in request | Files generated |
|---|---|
| `full audit` / (default, no keyword) | All 11 files |
| `seo only` | SEO-AUDIT.md + FIX-PLAN.md |
| `geo only` | 8 GEO files + FIX-PLAN.md |
| `client report` | GEO-CLIENT-REPORT.md only (reads existing reports/seo_geo_scores/ data) |
| `crawlers` | GEO-CRAWLERS.md only |
| `citability` | GEO-CITABILITY.md only |
| `llmstxt` | GEO-LLMSTXT.md only |
| `schema` | GEO-SCHEMA.md only |
| `technical` | GEO-TECHNICAL.md only |
| `content` / `eeat` | GEO-CONTENT.md only |
| `platform` | GEO-PLATFORM.md only |
| `fix plan` | FIX-PLAN.md only (reads existing score files for context) |
| `pdf report` / `pdf` | All 11 files + `reports/seo_geo_scores/REPORT.pdf` via generate_pdf_report.py |

### Step 0.5: Check for Existing reports/seo_geo_scores/ Folder (Determines Run Mode)

**Before touching any source files**, look for the `reports/seo_geo_scores/` folder in the frontend project root.

```bash
# Check if a prior audit exists
ls <project-root>/reports/seo_geo_scores/SCORE-HISTORY.md
```

**If the folder DOES NOT exist** → this is a **First Run**:
- Perform the full 16-category audit from scratch
- Include the complete GA4 setup walkthrough (Step 7 of tools-and-analytics.md)
- Generate all `reports/seo_geo_scores/` files at the end (Step 8)

**If the folder EXISTS AND SCORE-HISTORY.md has at least 1 run entry** → this is a **Subsequent Run**:
- Read `reports/seo_geo_scores/SCORE-HISTORY.md` and the relevant existing score files
- **Load the User Decisions Log** (see Rule 18): parse the `## User Decisions Log` table if present. Build a map of `finding-id → decision` for all recorded decisions.
- Build the "already done" list from the Infrastructure Status table (✅ rows)
- Build the "outstanding issues" list from the Category Summary table (🔄 and ⏳ rows)
- **Skip any FIX that is already marked ✅ in the previous report**
- **Skip any finding whose `finding-id` appears in the decisions log** — display it as `⚪ Decision on record (Run N — [decision])` and do NOT include it in FIX-PLAN.md or count it toward the WARN/FAIL score
- **For GA4**: if the Infrastructure Status table shows GA4 as ✅ Done, do NOT re-explain setup. Instead, in the fix plan section for Category 10, say: "GA4 is already configured. Recommended next actions: [see below]" and provide specific things to check in the live GA4 dashboard (e.g., verify route-change events are firing, check CWV data in custom reports, look for pages with high bounce rate)
- Re-audit only the categories that had FAIL or WARN in the prior report, plus any categories the user specifically asked about
- At the end, update `reports/seo_geo_scores/` files with the new run's findings (increment Run #, update statuses, append to SCORE-HISTORY.md)

**Subsequent Run — GA4 actions to suggest instead of setup:**
- Check GA4 Realtime: are page_view events firing for every route change?
- Check Engagement: which pages have highest bounce rate? Those need title/description review.
- Check Core Web Vitals custom report: are `web_vitals` events coming in? What are LCP/CLS/INP ratings?
- Check Search Console (linked from GA4): impressions and clicks per page; which queries bring traffic?
- Check Conversions: are any conversion events configured? Suggest the next one to add.

### Step 1: Discover All Routes

Read the app's router config (typically `src/app/routes.tsx`, `src/routes.ts`, or `App.tsx`).

List every route path and its component:

```
| Route         | Component     | File Path                        |
|---------------|---------------|----------------------------------|
| /             | HomePage      | src/pages/HomePage.tsx           |
| /dashboard    | DashboardPage | src/pages/DashboardPage.tsx      |
| ...           | ...           | ...                              |
```

This page inventory drives the audit — every page must be checked.

### Step 2: Read the HTML Shell

Read `index.html` (or `public/index.html`) and record violations immediately in the Issue Log.

Checks:
- `<!DOCTYPE html>` is the very first line
- `<html lang="...">` has a real BCP-47 language code (e.g., `en`, `en-US`)
- `<meta charset="utf-8">` appears in `<head>` before any other content-bearing tags
- `<meta name="viewport" content="width=device-width, initial-scale=1">` is present
- Body contains a single root element (`<div id="root">`) with no extra markup

### Step 2.5: Live Site Fetch (GEO — Skip if No Deployed URL)

**Only execute this step if the user provides a deployed URL.**

This step activates the 8 GEO categories (17–24). Without a live URL, mark Cat 17-24 as 🔵 N/A in the report.

**2.5a — Fetch the live page:**

Use `WebFetch` to retrieve the deployed URL. Record:
- Whether the HTML body contains actual content tags (`<h1>`, `<h2>`, `<p>`, `<article>`) — if only `<div id="root"></div>` is visible, the site is 100% client-side rendered (CRITICAL GEO issue: AI crawlers see NOTHING)
- Business type detected (SaaS, local business, blog, e-commerce, portfolio)
- Canonical URL structure

**2.5b — Check GEO infrastructure files:**

Fetch these URLs in parallel (replace `yourdomain.com` with the actual domain):

| File | URL | Purpose |
|------|-----|---------|
| robots.txt | `https://yourdomain.com/robots.txt` | Check which AI crawlers are allowed |
| llms.txt | `https://yourdomain.com/llms.txt` | Cat 19 — AI content guide |
| llms-full.txt | `https://yourdomain.com/llms-full.txt` | Cat 19 — extended AI content guide |
| sitemap.xml | `https://yourdomain.com/sitemap.xml` | Cat 17 — crawler coverage |
| ai-plugin.json | `https://yourdomain.com/.well-known/ai-plugin.json` | OpenAI plugin manifest |
| /ai.txt | `https://yourdomain.com/ai.txt` | Emerging AI permissions standard |

For robots.txt, check ALL 14 AI crawlers organized by tier:

**Tier 1 — Critical (must ALLOW for AI search visibility):**
- GPTBot (OpenAI/ChatGPT Search — 300M+ users)
- OAI-SearchBot (ChatGPT search-only, no training use)
- ChatGPT-User (ChatGPT user-initiated browsing)
- ClaudeBot (Anthropic web search and analysis)
- PerplexityBot (Perplexity AI — best referral traffic AI search)

**Tier 2 — Important (ALLOW for broader AI ecosystem):**
- Google-Extended (Gemini training — does NOT affect Google Search ranking)
- GoogleOther (Google AI research crawls)
- Applebot-Extended (Apple Intelligence — 2B+ devices)
- Amazonbot (Alexa and Amazon AI features)
- FacebookBot (Meta AI across 3B+ users)

**Tier 3 — Training-only (context-dependent, no live AI search impact):**
- CCBot (Common Crawl training datasets)
- anthropic-ai (Anthropic training only — separate from ClaudeBot)
- Bytespider (ByteDance — BLOCK for Western businesses)
- cohere-ai (Cohere training — context-dependent)

Also check for:
- HTTP `X-Robots-Tag` headers on 3-5 key pages (can block AI access at page level). WebFetch does NOT return HTTP headers — use:
  ```bash
  curl -sI [PAGE_URL] | grep -i "x-robots-tag"
  ```
  If output is present, it's a potential AI crawler block. No output = header absent (safe).
- `<meta name="robots" content="noai">` tags on key pages (check in the HTML fetched by WebFetch)

**2.5b.1 — Multi-Page Sitemap Crawl (up to 50 pages):**

1. Parse all `<loc>` URLs from sitemap.xml (already fetched above).
2. Filter HTML pages only — exclude `.xml`, `.pdf`, `.jpg`, `.png`, `.gif`, `.svg`, `.webp`, `.ico` extensions.
3. Select up to 50 pages, prioritized in this order:
   - Homepage first
   - Product/service pages
   - Pricing page
   - About/Team pages
   - Blog/documentation (most recent content first)
4. For each selected page: fetch HTML, record SSR vs CSR status (CSR = body has only `<div id="root"></div>` with no meaningful content), record page type (product, blog, pricing, about, docs).
5. **Deduplication:** If a newly fetched page has >80% content similarity to any already-processed page (same paragraph blocks, boilerplate-only difference), skip it and move to the next URL in the sitemap.
6. Pass the deduplicated page sample to geo-ai-visibility agent (Step 2.5c below) for block-level citability scoring across representative pages rather than just the homepage.

**Rate limit:** 1 second between fetches. If sitemap is not found, analyze homepage + up to 5 pages discoverable from main navigation. Never crawl pages on external domains found in the sitemap (filter to same origin only).

**2.5c — Run GEO sub-agents:**

Invoke all 6 GEO agents in the order below, reading each agent file for the full execution protocol. Agents reference scripts in `scripts/` and schema templates in `schema/`.

1. Read and execute [geo-technical.md](agents/geo-technical.md) → writes `reports/seo_geo_scores/GEO-TECHNICAL.md`
2. Read and execute [geo-crawlers.md](agents/geo-crawlers.md) → writes `reports/seo_geo_scores/GEO-CRAWLERS.md`
3. Read and execute [geo-ai-visibility.md](agents/geo-ai-visibility.md) → writes `reports/seo_geo_scores/GEO-CITABILITY.md` + `reports/seo_geo_scores/GEO-LLMSTXT.md`
4. Read and execute [geo-content.md](agents/geo-content.md) → writes `reports/seo_geo_scores/GEO-CONTENT.md`
5. Read and execute [geo-schema.md](agents/geo-schema.md) → writes `reports/seo_geo_scores/GEO-SCHEMA.md`
6. Read and execute [geo-platform-analysis.md](agents/geo-platform-analysis.md) → writes `reports/seo_geo_scores/GEO-PLATFORM.md`
7. Read and execute [geo-client-report.md](agents/geo-client-report.md) → writes `reports/seo_geo_scores/GEO-CLIENT-REPORT.md` (runs LAST — reads all other output files to synthesize the client deliverable)

Each agent writes its output file directly. Collect all scores from those files for the report.

### Step 3: Run the 24-Category Audit

Read [audit-categories.md](references/audit-categories.md) and work through every category in order.

The file covers:
- **Categories 1–13**: Core SEO (HTML shell, titles, headings, images, links, routing, structured data, performance, mobile, analytics, robots/sitemap, SEO components, QA verification)
- **Category 14**: Core Web Vitals (LCP/CLS/INP)
- **Category 15**: Social Tags (Open Graph + Twitter Cards)
- **Category 16**: Advanced (Hreflang, CSP, Dynamic rendering)
- **Categories 17–24**: GEO — read [geo-categories.md](references/geo-categories.md) for full scoring rubrics

For each category:
1. Read the relevant source files (route components, `public/`, hooks, etc.)
2. Apply every check listed for that category
3. Record each finding in the Issue Log using the format below

**Do not skip any category.** If the codebase has no images, mark category 4 as PASS with note "No images found." For Cat 17–24 without a deployed URL, mark as 🔵 N/A.

### Step 4: Score Each Category

After all 24 categories, produce the Audit Score Table:

```
| # | Category                        | Score | Issues |
|---|---------------------------------|-------|--------|
| 1 | HTML Shell & Document Head      | PASS  | 0      |
| 2 | Page Titles & Meta Descriptions | FAIL  | 3      |
| 3 | Headings & Page Structure       | WARN  | 1      |
| 4 | Images: Alt, Size, Loading      | PASS  | 0      |
| 5 | Internal Links & Navigation     | WARN  | 2      |
| 6 | Routing, URLs & Status Codes    | PASS  | 0      |
| 7 | Structured Data                 | FAIL  | 1      |
| 8 | Performance Optimizations       | WARN  | 2      |
| 9 | Mobile Friendliness             | PASS  | 0      |
|10 | Analytics & Tracking (GA4)      | FAIL  | 1      |
|11 | Robots.txt & Sitemap.xml        | FAIL  | 2      |
|12 | Reusable SEO Components         | WARN  | 1      |
|13 | QA Verification Per Page        | FAIL  | 4      |
|14 | Core Web Vitals (LCP/CLS/INP)   | WARN  | 2      |
|15 | Social Tags (OG + Twitter Card) | FAIL  | 3      |
|16 | Advanced (Hreflang/CSP/Dynamic) | N/A   | 0      |
|17 | Technical GEO Signals           | FAIL  | 3      |
|18 | AI Crawler Access               | FAIL  | 2      |
|19 | llms.txt                        | FAIL  | 1      |
|20 | Content Citability & E-E-A-T    | WARN  | 2      |
|21 | Brand Presence (AI Platforms)   | WARN  | 1      |
|22 | Platform Readiness              | WARN  | 2      |
|23 | Schema & Structured Data (GEO)  | FAIL  | 2      |
|24 | Core Web Vitals (Field Data)    | N/A   | 0      |

SEO Overall: X PASS · Y WARN · Z FAIL (Cats 1–16)
GEO Overall: X PASS · Y WARN · Z FAIL (Cats 17–24)
```

Scores:
- **PASS** — All checks in the category pass
- **WARN** — Minor issues; not blocking but must be addressed
- **FAIL** — One or more critical checks fail

**GEO Composite Scores** (compute both and record in `reports/seo_geo_scores/SCORE-HISTORY.md`):

*Audit GEO Score* (technical completeness, equal-weight across signals):
```
GEO_Audit = (Citability×0.25) + (Brand×0.20) + (E-E-A-T×0.20) + (Technical×0.15) + (Schema×0.10) + (Platform×0.10)
```

*Client Report GEO Score* (business-impact weighted, emphasizes discoverability):
```
GEO_Client = (Platform×0.25) + (Content/E-E-A-T×0.25) + (Technical×0.20) + (Schema×0.15) + (Brand×0.15)
```

### Step 5: Build the Prioritized Fix Plan

Group all issues from the Issue Log by severity. For each issue, produce a fix entry:

```
### FIX-001 · Critical · Category 2

**Issue**: Missing <title> and <meta name="description"> on /dashboard route
**Why it matters**: Google uses the title tag as the primary identifier for a page in search
results. Missing titles cause machine-generated titles that hurt click-through rate.
**File**: src/pages/DashboardPage.tsx (line 8, the root return statement)

**Fix**:
// Before
export function DashboardPage() {
  return <div className="dashboard">...</div>;
}

// After
import { Helmet } from 'react-helmet-async';

export function DashboardPage() {
  return (
    <>
      <Helmet>
        <title>Dashboard · Acme Cloud</title>
        <meta name="description" content="Manage your AI apps, API keys, and memory usage." />
      </Helmet>
      <div className="dashboard">...</div>
    </>
  );
}
```

Number fixes sequentially (FIX-001, FIX-002, …). GEO fixes that require code changes (robots.txt entries, JSON-LD blocks, prerendering config) must include the exact content to write to the file.

### Step 6: Wave Plan

Group fixes into implementation waves based on dependencies and effort:

```
Wave 0 — Foundation (must complete first; all other waves depend on this)
  FIX-011  Install react-helmet-async
  FIX-012  Create shared <SeoHead> component

Wave 1 — Critical (directly blocking indexing or AI crawler access)
  FIX-001  Add title+description to /dashboard
  FIX-002  Add title+description to /apps/:id
  FIX-003  Fix robots.txt (currently blocking all crawlers)
  FIX-018  Allow GPTBot, ClaudeBot, PerplexityBot in robots.txt

Wave 2 — High Priority (significant ranking and AI visibility impact)
  FIX-004  Fix heading hierarchy on SettingsPage
  FIX-005  Add Organization JSON-LD with sameAs to root layout
  FIX-023  Add speakable property to Article schema

Wave 3 — Medium / Low (best-practice improvements)
  FIX-008  Add alt text to logo and hero images
  FIX-009  Add sitemap.xml
  FIX-010  Lazy-load below-the-fold route components
  FIX-019  Create /llms.txt
```

Wave 0 must always exist if any fix requires a new npm package or shared component.

### Step 7: Final Checklist

Before presenting the plan to the user, verify every item:

- [ ] All 24 categories audited (or marked 🔵 N/A for GEO cats without a deployed URL)
- [ ] Every FAIL category has at least one FIX entry
- [ ] Every FIX has: severity label, category number, exact file path + line, before/after code
- [ ] Wave 0 contains all new dependencies and shared SEO components
- [ ] Fix count in score table matches fix count in the wave plan
- [ ] No suggestion to migrate to Next.js, Gatsby, Remix, or any other framework
- [ ] GA4: first run = setup walkthrough; subsequent run = action suggestions only
- [ ] GEO fixes (robots.txt, JSON-LD, llms.txt, prerender config) have exact file content, not vague advice
- [ ] sameAs links reference real platform profile URLs, not placeholders (or use `[REPLACE: ...]` markers)
- [ ] No deprecated schemas recommended (FAQPage only for authority sites, HowTo removed Sep 2023)
- [ ] Score History row prepared for appending to `reports/seo_geo_scores/SCORE-HISTORY.md`
- [ ] Both GEO composite scores computed (GEO_Audit and GEO_Client formulas)
- [ ] All reports/seo_geo_scores/ files written (only the 11 pre-defined files — no additional files created)
- [ ] GEO-CLIENT-REPORT.md generated by geo-client-report.md agent (last agent to run)

### Step 8: Write or Update reports/seo_geo_scores/ Files

**This step is mandatory on every run.** After presenting the plan to the user, generate or update the files in `reports/seo_geo_scores/` in the frontend project root.

Read [report-format.md](references/report-format.md) for the exact template and status codes.

Rules for this step:
- **First run**: create `reports/seo_geo_scores/` folder and all applicable files from scratch
- **Subsequent run**: overwrite each score file with the new run's findings — except `SCORE-HISTORY.md` which is always **appended** (never overwritten)
- **SEO-AUDIT.md**: increment the Run number, update statuses for re-audited categories, keep all old resolved entries
- **Never downgrade a ✅ Complete row** to ⏳ Pending unless a fix was actively reverted
- **GEO files** (GEO-CITABILITY.md, GEO-CRAWLERS.md, etc.): overwrite with latest analysis results
- **SCORE-HISTORY.md**: append one row per run — never modify previous rows
- **FIX-PLAN.md**: overwrite with the current run's wave plan
- Both GEO composite scores (GEO_Audit and GEO_Client) must be written to SCORE-HISTORY.md
- The files must be self-contained: a developer reading them cold should understand what's done and what's outstanding with zero prior context
- **NEVER create files outside reports/seo_geo_scores/ or files not in the pre-defined 11.** This is a hard constraint.

### Step 8.5: Generate PDF Report

**This step is MANDATORY on every run** (see Rule 0). Generate it regardless of whether the user explicitly asked for it.

After all 10 markdown files are written to `reports/seo_geo_scores/`, construct a JSON data file from the audit scores and run:

```bash
uv run scripts/generate_pdf_report.py /tmp/seo_report_data.json reports/seo_geo_scores/REPORT.pdf > /tmp/pdf_report.log 2>&1
```

Scripts have PEP 723 inline metadata — `uv run` handles dependency installation automatically. No separate install step required.

---

### Step 9: Execute Code Fixes

After writing the `reports/seo_geo_scores/` files, ask the user:

```
The fix plan is ready. Would you like me to apply the fixes now?
I'll go wave by wave, showing each change before writing it.

Wave 0 (Foundation):  [N fixes — list them]
Wave 1 (Critical):    [N fixes — list them]
Wave 2 (High):        [N fixes — list them]
Wave 3 (Medium/Low):  [N fixes — list them]

Start with Wave 0? (yes/no)
```

**If the user says yes (or equivalent), apply fixes directly to the codebase:**

1. Work through fixes **one wave at a time**
2. For each fix, show the exact before/after diff, then write the change to the file using the Edit or Write tool
3. After completing each wave, pause and show a summary: "Wave N complete. N files changed. Ready for Wave N+1? (yes/no)"
4. After all waves, run a final verification pass: re-read each modified file and confirm the change is exactly what was intended
5. Update `reports/seo_geo_scores/SEO-AUDIT.md` statuses from ⏳ Pending to ✅ Complete for each applied fix

**For GEO code fixes** (robots.txt, JSON-LD schemas, llms.txt, prerender config):
- Write directly to the appropriate file in the project's `public/` directory or source tree
- Use schema templates from [schema/](schema/) directory as starting points for JSON-LD
- Never write JSON-LD directly into React components' render output — always use `react-helmet-async` or server-side injection

---

## Issue Log Format

Record findings as you audit in Step 3:

```
[SEV] CAT-N · <short description> · <file>:<line>
```

Severity codes: `CRITICAL` · `HIGH` · `MEDIUM` · `LOW`

Example:
```
[CRITICAL] CAT-2  · No <title> on /dashboard                       · src/pages/DashboardPage.tsx
[CRITICAL] CAT-11 · robots.txt disallows all crawlers               · public/robots.txt:2
[CRITICAL] CAT-18 · GPTBot blocked in robots.txt                    · public/robots.txt:5
[HIGH]     CAT-3  · Two <h1> tags on HomePage                       · src/pages/HomePage.tsx:12,47
[HIGH]     CAT-7  · No JSON-LD structured data anywhere             · (global — no file)
[HIGH]     CAT-23 · Organization schema missing sameAs property     · (global — no file)
[MEDIUM]   CAT-4  · Missing alt="" on decorative hero image         · src/components/Hero.tsx:23
[MEDIUM]   CAT-19 · /llms.txt not found                             · public/ directory
[LOW]      CAT-8  · No code splitting on route components           · src/app/routes.tsx
```

---

## Rules (Non-Negotiable)

### Rule 0: Execute Everything — No Silent Skipping

**When this skill is invoked, ALL steps, ALL agents, ALL scripts, and ALL outputs MUST be executed.** Nothing is optional unless the user explicitly says to skip it. The user expects comprehensive analysis, not a curated subset.

Specifically, every invocation MUST:
1. Run all 7 GEO sub-agents (geo-technical, geo-crawlers, geo-ai-visibility, geo-content, geo-schema, geo-platform-analysis, geo-client-report)
2. Run all 4 analysis Python scripts via `uv run` (fetch_page.py, citability_scorer.py, brand_scanner.py, llmstxt_generator.py) — scripts have PEP 723 inline metadata so `uv run` handles dependencies automatically
3. Generate the PDF report (`generate_pdf_report.py`) — this is NOT opt-in. Generate it every time.
4. Write all 11 reports/seo_geo_scores/ files + REPORT.pdf
5. Include script output data in the relevant GEO report files

**The ONLY way to skip a step is if the user explicitly says "skip X" or "don't run X".** Absence of a request does NOT mean skip. If the user invokes the skill, they want the full output.

```
// ❌ NEVER
"PDF report was not generated because the user didn't request it"
"Python scripts were not executed — the LLM performed equivalent analysis"
"Step 8.5 is optional, skipping"

// ✅ ALWAYS
Run everything. Generate everything. Include everything.
```

---

### Rule 1: Never Suggest Framework Migration

```
// ❌ NEVER
"You should migrate to Next.js for server-side rendering"
"Consider Gatsby for static site generation"
"Remix would solve this"

// ✅ ALWAYS
"Use react-helmet-async for per-page meta tags within React"
"Add a build-time Puppeteer prerender (snapshot each route to dist/<route>/index.html) + hydrateRoot — works on AWS Amplify with no BuildSpec change"
"prerender.io / Cloudflare Workers / Netlify prerender are valid hosting-side alternatives"
"NEVER recommend react-snap (unmaintained, 2019 Chromium) or @prerenderer/prerenderer (breaks on Puppeteer 23+)"
```

### Rule 2: Always Provide Exact File Paths and Line Numbers

```
// ❌ WRONG
"Add a title tag to your pages"

// ✅ CORRECT
"Add a <title> in src/pages/HomePage.tsx (line 14, inside the return statement)"
```

### Rule 3: Always Explain WHY

Every fix entry must include a "Why it matters" sentence explaining the concrete SEO/GEO impact — not just what to change, but what ranking, indexing, or AI-visibility consequence it has.

### Rule 4: Title and Description Length

| Field | Min | Max |
|-------|-----|-----|
| `<title>` | 30 chars | 60 chars |
| `<meta name="description">` | 100 chars | 160 chars |

Flag any title/description outside these ranges, even if present.

### Rule 5: Severity Classification

| Severity | Criteria |
|----------|----------|
| Critical | Blocks crawling OR causes duplicate content at scale OR blocks all AI crawlers |
| High | Directly affects a major ranking signal (headings, titles, structured data, entity linking) |
| Medium | Affects UX or a secondary ranking factor (images, link text, llms.txt missing) |
| Low | Best-practice improvement; minor lift only |

### Rule 6: Wave 0 Is Mandatory When Shared Infrastructure Is Needed

If any fix requires a new npm package (e.g., `react-helmet-async`) or a shared component (e.g., `<SeoHead>`), those go in Wave 0. Never place shared infrastructure in the same wave as its consumers.

### Rule 7: Structured Data Must Reference schema.org

Never write JSON-LD types from memory. Reference schema.org types explicitly. Use the template files in [schema/](schema/) as a starting point. Include a note to validate with Google's Rich Results Test.

### Rule 8: Exactly One `<h1>` Per Page

Zero or more than one `<h1>` on any page is always a FAIL, never a WARN. Every category 3 fix must restore exactly one `<h1>` per page.

### Rule 9: Verify Fix Compatibility with Existing Patterns

Before writing a fix, check how the existing codebase handles similar concerns. The fix must fit the existing pattern — not introduce a foreign pattern that will conflict.

### Rule 10: Open Graph and Twitter Cards Are Mandatory, Not Optional

`og:title`, `og:description`, `og:url`, `og:image`, `twitter:card` are not "nice-to-have". Always include these in the `<SeoHead>` component and flag missing ones as HIGH severity.

### Rule 11: Core Web Vitals Are a Google Ranking Signal (Since 2021)

LCP, CLS, and INP directly affect page ranking. Always audit Category 14. If Lighthouse reports LCP > 2.5s or CLS > 0.1, flag as HIGH. Note: **INP replaced FID in March 2024** — never reference FID as a current Core Web Vital.

### Rule 12: Third-Party Account Setup Is Interactive and Guided — Never a Wall of Text

Any setup that requires creating accounts, visiting external dashboards, or copying credentials MUST be done interactively, one confirmed step at a time. Never dump all setup instructions at once.

**Required pattern for all setup flows:**

1. **Show the skeleton first** — present a numbered list of all steps with one-line descriptions only
2. **Dive into step 1 in full detail** — explain exactly what to do, provide the exact URL as a clickable link
3. **Wait for the user to confirm** they completed the step before showing step 2
4. **Never advance** without explicit confirmation ("done", "ok", "next", etc.)
5. **Provide every external URL as a formatted clickable markdown link**

   > **Do NOT use chrome devtools MCP to open browser links.** Google and other auth-required services
   > detect automated browsers and block login. Always let the user open links in their own browser.

6. **On each step**, describe exactly where on the page the user should look and what to click

This rule applies to: GA4, Google Search Console, Facebook OG Debugger, LinkedIn Post Inspector, Screaming Frog, Ahrefs, Bing Webmaster Tools, Google Rich Results Test — any tool requiring browser interaction.

### Rule 13: GEO Code Fixes Are Applied Directly to Source Files

GEO fixes that require creating or modifying files in the codebase (robots.txt updates, JSON-LD schema blocks, llms.txt creation, prerendering configuration) must be written directly to the project's source files using the Edit or Write tool — not just described in prose. Every GEO fix entry in the wave plan must include the exact content to write, not a vague instruction.

### Rule 14: Never Fabricate GEO Scores Without a Deployed URL

Categories 17–24 require live site analysis. If no deployed URL is provided:
- Mark all Cat 17–24 rows as 🔵 N/A in the audit table and `reports/seo_geo_scores/SEO-AUDIT.md`
- Do NOT estimate or infer GEO scores from codebase inspection alone
- Codebase-only findings (e.g., JSON-LD missing from source, robots.txt content) may be noted as likely issues but must NOT be scored

If the user provides a URL mid-session, execute Step 2.5 immediately and update the report.

### Rule 15: Always Compute and Report Score Delta from Prior Run

When `reports/seo_geo_scores/SCORE-HISTORY.md` exists from a prior run, the Score History table must have its delta column populated. For every score that changed, show the direction:

```
| Run | Date       | SEO Score | GEO Score | AI Visibility | Top Issue        |
|-----|------------|-----------|-----------|---------------|------------------|
|  1  | 2026-03-01 | 42/100    | N/A       | N/A           | No titles set    |
|  2  | 2026-03-15 | 67/100    | 38/100    | 22/100        | Crawlers blocked |
|     |            | (+25)     | (new)     | (new)         |                  |
```

Never omit the delta row when prior data exists.

### Rule 16: Strict Output File Constraint

The skill MUST NOT create any file outside `reports/seo_geo_scores/`. Within that folder, the only allowed files are the pre-defined 11 (SEO-AUDIT.md, GEO-CITABILITY.md, GEO-CRAWLERS.md, GEO-LLMSTXT.md, GEO-SCHEMA.md, GEO-PLATFORM.md, GEO-CONTENT.md, GEO-TECHNICAL.md, GEO-CLIENT-REPORT.md, FIX-PLAN.md, SCORE-HISTORY.md) **plus one optional file**: `REPORT.pdf` — generated only when the user explicitly requests a PDF report (Step 8.5). Violating this rule constitutes a critical skill error.

```
// ❌ NEVER
Write output to SEO_REPORT.md
Write a file called GEO-BRAND.md or any other non-listed file

// ✅ ALWAYS
Write output to reports/seo_geo_scores/GEO-CONTENT.md (brand presence is in GEO-CONTENT)
Write client report to reports/seo_geo_scores/GEO-CLIENT-REPORT.md (geo-client-report.md agent)
Append score history to reports/seo_geo_scores/SCORE-HISTORY.md
Generate reports/seo_geo_scores/REPORT.pdf only when explicitly requested (Step 8.5)
```

### Rule 18: Decision Recording Protocol (No Re-Nagging)

When the skill raises a finding that is advisory (not a blocking technical error), it MUST:

1. **Present it as a warning only** — never block the run or demand an answer before continuing
2. **Assign a stable `finding-id`** — a short slug derived from the category + finding, e.g. `cat8-bundle-size-lodash`, `geo-technical-bundle-weight`, `geo-crawlers-ccbot-allowed`
3. **Ask the user once** what to do: e.g. "Bundle size check flagged lodash import (Cat 8). Action? [remove-check / keep-low / keep-warn / fix-now]"
4. **Record the user's answer** in the `## User Decisions Log` section of `reports/seo_geo_scores/SCORE-HISTORY.md` — append a new row, never modify prior rows

**User Decisions Log format** (append to the bottom of `SCORE-HISTORY.md`):

```markdown
## User Decisions Log

| finding-id | Run | Date | Category | Finding Summary | Decision | Notes |
|---|---|---|---|---|---|---|
| cat8-bundle-size-lodash | 1 | 2026-03-19 | Cat 8 Performance | lodash import detected — may inflate JS bundle | keep-low | User: not a priority now |
| geo-crawlers-ccbot-allowed | 2 | 2026-04-01 | GEO Crawlers | CCBot not blocked — training data risk | accept-risk | User: ok with training crawlers |
```

**Decision values** (standardized):
- `keep-low` — acknowledged, intentionally keeping as low priority, do not re-raise
- `keep-warn` — keep showing as a warning each run, but don't push to fix
- `accept-risk` — user is aware of the risk and explicitly accepts it
- `fix-now` — user wants this fixed; add to FIX-PLAN.md Wave 1
- `remove-check` — user wants this check removed from future audits entirely
- `defer` — re-raise after 30 days (use the date in SCORE-HISTORY to determine if 30 days have passed)

**On subsequent runs:**
- Load all rows from `## User Decisions Log`
- For any finding whose `finding-id` matches a row with decision `keep-low`, `accept-risk`, or `remove-check`: display as `⚪ Decision on record (Run N — [decision])`, do NOT flag as WARN/FAIL, do NOT include in FIX-PLAN.md
- For `keep-warn`: show the warning as usual but do NOT ask the user again
- For `defer`: suppress until the date in the row is 30+ days old, then re-raise once
- Never prompt the user for a decision on a finding that already has a recorded decision in the log

### Rule 17: Sitemap Crawl Limits

Multi-page sitemap crawl is capped at 50 pages. Rate limit: 1 second between fetches. Only crawl pages on the same origin as the deployed URL — filter out any external domain URLs found in the sitemap. If sitemap is absent, fall back to homepage + up to 5 navigation-discoverable pages.

### Rule 19: Mandatory Python Script Execution

All Python scripts in `scripts/` MUST be executed on every skill invocation. Scripts have PEP 723 inline dependency metadata and should be run via `uv run scripts/<name>.py` — this handles dependency installation automatically with no setup step required.

**Required script runs (every invocation):**

```bash
# 1. Full page analysis (page + robots + llms + sitemap)
uv run scripts/fetch_page.py <deployed_url> full > /tmp/seo_fetch_full.json

# 2. Citability scoring (algorithmic block-level analysis)
uv run scripts/citability_scorer.py <deployed_url> > /tmp/seo_citability.json

# 3. Brand mention scanning (YouTube, Reddit, Wikipedia, LinkedIn, etc.)
uv run scripts/brand_scanner.py "<brand_name>" <domain> > /tmp/seo_brand.json

# 4. llms.txt validation
uv run scripts/llmstxt_generator.py <deployed_url> validate > /tmp/seo_llmstxt.json

# 5. PDF report generation (ALWAYS — not optional)
uv run scripts/generate_pdf_report.py /tmp/<data>.json reports/seo_geo_scores/REPORT.pdf
```

Script output data must be incorporated into the corresponding GEO report files (e.g., citability scores into GEO-CITABILITY.md, brand scan results into GEO-CONTENT.md). The JSON outputs provide algorithmic precision that supplements the LLM's qualitative analysis.

---

## References

- [Audit Categories](references/audit-categories.md) — Complete 24-category checklist (16 SEO + 8 GEO)
- [GEO Categories](references/geo-categories.md) — Categories 17–24 with full scoring rubrics
- [Platform Optimization](references/platform-optimization.md) — 5-platform checklists (AIO, ChatGPT, Perplexity, Gemini, Copilot)
- [Tools, Analytics & GA4 Setup](references/tools-and-analytics.md) — Free SEO/GEO tools, web-vitals, GA4 walkthrough, GEO scripts
- [SEO Report Format](references/report-format.md) — Template and status codes for reports/seo_geo_scores/ files
- [GEO Agents](agents/) — 6 specialist agents for GEO sub-analysis:
  - [geo-technical.md](agents/geo-technical.md) — SSR detection, security headers, CWV field data → GEO-TECHNICAL.md
  - [geo-crawlers.md](agents/geo-crawlers.md) — 14-crawler access map, robots.txt template → GEO-CRAWLERS.md
  - [geo-ai-visibility.md](agents/geo-ai-visibility.md) — Block-level citability, llms.txt/llms-full.txt/ai.txt → GEO-CITABILITY.md + GEO-LLMSTXT.md
  - [geo-content.md](agents/geo-content.md) — E-E-A-T, readability, brand presence → GEO-CONTENT.md
  - [geo-schema.md](agents/geo-schema.md) — Schema detection, validation, JSON-LD generation → GEO-SCHEMA.md
  - [geo-platform-analysis.md](agents/geo-platform-analysis.md) — 5-platform readiness scores → GEO-PLATFORM.md
  - [geo-client-report.md](agents/geo-client-report.md) — Client-facing report synthesis → GEO-CLIENT-REPORT.md (runs last; reads all other output files)
- [Schema Templates](schema/) — Ready-to-use JSON-LD templates (organization, article, product, local-business, SaaS, website-searchaction)
- [Python Scripts](scripts/) — GEO analysis scripts (citability_scorer.py, brand_scanner.py, fetch_page.py, llmstxt_generator.py, generate_pdf_report.py — PDF generation from reports/seo_geo_scores/ folder)

---

## Troubleshooting

If any part of this skill produces unexpected results or an agent's instructions seem incomplete, check the following resources within this skill:

```bash
# Reference files in the skill directory:
ls skills/                   # GEO sub-skills (geo-audit, geo-content, etc.)
ls agents/                   # GEO agent files
ls scripts/                  # Python analysis scripts
```

All GEO categories and scoring logic are documented in the agent files and reference guides. When something doesn't work as expected, review the corresponding agent file in `agents/` or the reference files in `references/` to see the intended behavior.

---

## Report Registry

All outputs are written to `reports/seo_geo_scores/`. Here is a complete reference of every file, who it is for, and when it is generated:

| File | Audience | Purpose | Generated When |
|---|---|---|---|
| **SEO-AUDIT.md** | Developer | Cats 1-16 scores, issue log, PASS/WARN/FAIL per category | Every run |
| **GEO-CITABILITY.md** | Developer / Content team | Block-level citability scores per H2/H3, rewrite suggestions | Full audit / `citability` mode |
| **GEO-CRAWLERS.md** | Developer / DevOps | 14-crawler access map, robots.txt template | Full audit / `crawlers` mode |
| **GEO-LLMSTXT.md** | Developer | llms.txt + llms-full.txt + /ai.txt validation or generation | Full audit / `llmstxt` mode |
| **GEO-SCHEMA.md** | Developer | Schema.org JSON-LD validation, sameAs gaps, ready-to-use code | Full audit / `schema` mode |
| **GEO-PLATFORM.md** | Developer / Marketing | Per-platform scores (AIO, ChatGPT, Perplexity, Gemini, Copilot) | Full audit / `platform` mode |
| **GEO-CONTENT.md** | Content team | E-E-A-T scoring, brand presence, readability | Full audit / `content` mode |
| **GEO-TECHNICAL.md** | Developer | SSR, CWV, security headers, mobile, IndexNow | Full audit / `technical` mode |
| **GEO-CLIENT-REPORT.md** | Business owner / Stakeholders | 3K-6K word professional deliverable with dollar-value framing, executive summary, action plan | Full audit / `client report` mode |
| **FIX-PLAN.md** | Developer | Wave-by-wave code diffs, file paths, before/after fixes | Every run |
| **SCORE-HISTORY.md** | All audiences | Running history of scores per run with deltas; also contains the `## User Decisions Log` table for persisting acknowledged findings across runs | Appended every run |
| **REPORT.pdf** | Client / Stakeholders | Polished PDF version of all report files | Every run (mandatory per Rule 0) |

### Report Types at a Glance

**Developer-focused reports** (technical depth, file paths, code diffs):
- SEO-AUDIT.md, GEO-CITABILITY.md, GEO-CRAWLERS.md, GEO-LLMSTXT.md, GEO-SCHEMA.md, GEO-PLATFORM.md, GEO-CONTENT.md, GEO-TECHNICAL.md, FIX-PLAN.md, SCORE-HISTORY.md

**Client/stakeholder-facing reports** (business impact, dollar estimates, executive language):
- GEO-CLIENT-REPORT.md (always generated on full audits — the deliverable you send to a client)
- REPORT.pdf (polished PDF of all reports — request explicitly with `pdf report` keyword)
