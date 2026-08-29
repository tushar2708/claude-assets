# SEO_REPORT.md — Template and Usage Guide

## Status Codes

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete — issue fully resolved and verified |
| 🔄 | In Progress — fix partially applied; some items remain |
| ⏳ | Pending — not yet started; in the fix plan |
| ❌ | Blocked / Failed — attempted but could not be applied |
| 🔵 | N/A — category does not apply to this project |

---

## Full SEO_REPORT.md Template

Copy this template exactly when creating the file on first run. Fill in all `{{placeholders}}`.

---

```markdown
# SEO Audit Report — {{App Name}}

**Project**: {{project root path}}
**First audited**: {{YYYY-MM-DD}}
**Last updated**: {{YYYY-MM-DD}}
**Audit run**: #{{N}}
**Auditor**: react-seo-planner skill

---

## Infrastructure Status

One-time setup items. Once ✅, never re-audited — only improved.

| Component | Status | Date | Notes |
|-----------|--------|------|-------|
| `react-helmet-async` installed | ⏳ Pending | — | Required for all title/meta fixes |
| `<SeoHead>` component created | ⏳ Pending | — | Shared wrapper for all SEO head tags |
| `web-vitals` npm package | ⏳ Pending | — | Required for CWV measurement |
| `vite-plugin-sitemap` (or equivalent) | ⏳ Pending | — | Generates sitemap.xml at build time |
| Google Analytics 4 property created | ⏳ Pending | — | Measurement ID: (add when done) |
| GA4 gtag.js in index.html | ⏳ Pending | — | |
| GA4 RouteTracker component | ⏳ Pending | — | src/app/RouteTracker.tsx |
| web-vitals → GA4 pipeline | ⏳ Pending | — | src/app/vitals.ts |
| Google Search Console verified | ⏳ Pending | — | Property URL: |
| Sitemap submitted to Search Console | ⏳ Pending | — | |
| robots.txt | ⏳ Pending | — | |
| `og:image` default created | ⏳ Pending | — | 1200×630px at /og-default.png |

---

## Category Summary

| # | Category | Status | Issues Found | Issues Fixed | Details |
|---|----------|--------|-------------|-------------|---------|
| 1 | HTML Shell & Document Head | ⏳ | — | — | [→ details](#cat-1-html-shell) |
| 2 | Page Titles & Meta Descriptions | ⏳ | — | — | [→ details](#cat-2-page-titles) |
| 3 | Headings & Page Structure | ⏳ | — | — | [→ details](#cat-3-headings) |
| 4 | Images: Alt, Size, Loading | ⏳ | — | — | [→ details](#cat-4-images) |
| 5 | Internal Links & Navigation | ⏳ | — | — | [→ details](#cat-5-links) |
| 6 | Routing, URLs & Status Codes | ⏳ | — | — | [→ details](#cat-6-routing) |
| 7 | Structured Data | ⏳ | — | — | [→ details](#cat-7-structured-data) |
| 8 | Performance Optimizations | ⏳ | — | — | [→ details](#cat-8-performance) |
| 9 | Mobile Friendliness | ⏳ | — | — | [→ details](#cat-9-mobile) |
| 10 | Analytics & Tracking (GA4) | ⏳ | — | — | [→ details](#cat-10-analytics) |
| 11 | Robots.txt & Sitemap.xml | ⏳ | — | — | [→ details](#cat-11-robots-sitemap) |
| 12 | Reusable SEO Components | ⏳ | — | — | [→ details](#cat-12-seo-components) |
| 13 | QA Verification Per Page | ⏳ | — | — | [→ details](#cat-13-qa) |
| 14 | Core Web Vitals (LCP/CLS/INP) | ⏳ | — | — | [→ details](#cat-14-cwv) |
| 15 | Social Tags (OG + Twitter Card) | ⏳ | — | — | [→ details](#cat-15-social) |
| 16 | Advanced (Hreflang/CSP/Dynamic) | 🔵 N/A | — | — | [→ details](#cat-16-advanced) |
| 17 | AI Crawler Access | 🔵 N/A | — | — | [→ details](#cat-17-ai-crawlers) |
| 18 | AI Citability | 🔵 N/A | — | — | [→ details](#cat-18-citability) |
| 19 | llms.txt Compliance | 🔵 N/A | — | — | [→ details](#cat-19-llmstxt) |
| 20 | E-E-A-T Content Quality | 🔵 N/A | — | — | [→ details](#cat-20-eeat) |
| 21 | Brand Authority | 🔵 N/A | — | — | [→ details](#cat-21-brand) |
| 22 | Platform-Specific (AIO/ChatGPT/…) | 🔵 N/A | — | — | [→ details](#cat-22-platforms) |
| 23 | Structured Data — GEO Extensions | 🔵 N/A | — | — | [→ details](#cat-23-schema-geo) |
| 24 | SSR for AI Crawlers | 🔵 N/A | — | — | [→ details](#cat-24-ssr) |

**Overall SEO**: — PASS · — WARN · — FAIL
**Overall GEO**: — (requires live URL — mark N/A until deployed URL provided)

---

## Fix Plan Summary

| Fix ID | Severity | Category | Description | Status | Wave |
|--------|----------|----------|-------------|--------|------|
| FIX-001 | Critical | 2 | {{description}} | ⏳ | 1 |
| FIX-002 | High | 3 | {{description}} | ⏳ | 2 |

_Full fix details in the category sections below._

---

## Detailed Findings

### Cat 1: HTML Shell {#cat-1-html-shell}

**Score**: ⏳ Pending (not yet audited)

| Check | Result | File | Notes |
|-------|--------|------|-------|
| DOCTYPE present | — | index.html:1 | |
| `lang` attribute | — | index.html | |
| charset meta | — | index.html | |
| viewport meta | — | index.html | |
| Single root element | — | index.html | |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 2: Page Titles {#cat-2-page-titles}

**Score**: ⏳ Pending (not yet audited)

**Per-page title audit**:

| Route | Has Title | Length | Unique | Has Description | Desc Length |
|-------|-----------|--------|--------|----------------|-------------|
| / | — | — | — | — | — |
| /dashboard | — | — | — | — | — |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 3: Headings {#cat-3-headings}

**Score**: ⏳ Pending (not yet audited)

**Per-page heading audit**:

| Route | h1 count | Hierarchy OK | Notes |
|-------|----------|-------------|-------|
| / | — | — | |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 4: Images {#cat-4-images}

**Score**: ⏳ Pending (not yet audited)

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 5: Internal Links {#cat-5-links}

**Score**: ⏳ Pending (not yet audited)

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 6: Routing & URLs {#cat-6-routing}

**Score**: ⏳ Pending (not yet audited)

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 7: Structured Data {#cat-7-structured-data}

**Score**: ⏳ Pending (not yet audited)

| Schema | Present | Valid JSON | Validator Link |
|--------|---------|-----------|----------------|
| WebSite | — | — | https://validator.schema.org |
| Organization | — | — | |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 8: Performance {#cat-8-performance}

**Score**: ⏳ Pending (not yet audited)

| Check | Result | Notes |
|-------|--------|-------|
| Code splitting (React.lazy) | — | |
| font-display: swap | — | |
| Layout shift prevention | — | |
| Render-blocking scripts | — | |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 9: Mobile {#cat-9-mobile}

**Score**: ⏳ Pending (not yet audited)

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 10: Analytics & GA4 {#cat-10-analytics}

**Score**: ⏳ Pending (not yet audited)

**GA4 Setup Status**: ⏳ Not started (first run)

_After GA4 is configured, this section will track:_
- Measurement ID in use
- Whether route-change page_view events fire correctly
- Whether web-vitals custom events appear in GA4
- Search Console link status
- Key metrics to review on next run

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 11: Robots.txt & Sitemap {#cat-11-robots-sitemap}

**Score**: ⏳ Pending (not yet audited)

| Item | Present | Valid | Notes |
|------|---------|-------|-------|
| robots.txt | — | — | |
| sitemap.xml | — | — | |
| Sitemap in robots.txt | — | — | |
| Sitemap submitted to GSC | — | — | |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 12: SEO Components {#cat-12-seo-components}

**Score**: ⏳ Pending (not yet audited)

| Component | Exists | File | OG tags included | Twitter tags included |
|-----------|--------|------|-----------------|----------------------|
| `<SeoHead>` | — | — | — | — |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 13: QA Per Page {#cat-13-qa}

**Score**: ⏳ Pending (not yet audited)

| Page | Title | Desc | H1 | Hierarchy | Linked | OG image |
|------|-------|------|----|-----------|--------|----------|
| / | — | — | — | — | — | — |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 14: Core Web Vitals {#cat-14-cwv}

**Score**: ⏳ Pending (not yet audited)

| Metric | Lab Result (Lighthouse) | Field Result (CrUX/PSI) | Rating |
|--------|------------------------|------------------------|--------|
| LCP | — | — | — |
| CLS | — | — | — |
| INP | — | — | — |

**Lighthouse URL**: https://pagespeed.web.dev/analysis?url={{your-url}}

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 15: Social Tags {#cat-15-social}

**Score**: ⏳ Pending (not yet audited)

| Tag | Present | Notes |
|-----|---------|-------|
| og:title | — | |
| og:description | — | |
| og:url | — | |
| og:image | — | 1200×630px required |
| og:type | — | |
| og:site_name | — | |
| twitter:card | — | |
| twitter:title | — | |
| twitter:description | — | |
| twitter:image | — | |

**Validation links**:
- Facebook Debugger: https://developers.facebook.com/tools/debug/?q={{your-url}}
- LinkedIn Inspector: https://www.linkedin.com/post-inspector/inspect/{{your-url}}

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 16: Advanced {#cat-16-advanced}

**Score**: 🔵 N/A — no multi-language, CSP, or dynamic rendering requirements identified

_Re-evaluate if: (a) app goes multi-language, (b) CSP policy is added, (c) SEO traffic disappoints despite other fixes_

---

## GEO Score Summary

_Populate only when a deployed URL is available. Skip on first run if no live URL provided._

| Component | Score | Run #1 | Run #2 | Delta |
|-----------|-------|--------|--------|-------|
| AI Visibility Score | —/100 | — | — | — |
| ↳ Citability (35%) | —/100 | — | — | — |
| ↳ Brand Mentions (30%) | —/100 | — | — | — |
| ↳ Crawler Access (25%) | —/100 | — | — | — |
| ↳ llms.txt (10%) | —/100 | — | — | — |
| Content Score (E-E-A-T) | —/100 | — | — | — |
| Schema Score | —/100 | — | — | — |
| Technical Score | —/100 | — | — | — |
| Platform Readiness Avg | —/100 | — | — | — |
| ↳ Google AIO | —/100 | — | — | — |
| ↳ ChatGPT Web Search | —/100 | — | — | — |
| ↳ Perplexity AI | —/100 | — | — | — |
| ↳ Google Gemini | —/100 | — | — | — |
| ↳ Bing Copilot | —/100 | — | — | — |

Formula: `AI_Visibility = (Citability * 0.35) + (Brand_Mentions * 0.30) + (Crawler_Access * 0.25) + (LLMS_TXT * 0.10)`

---

## GEO Infrastructure Status

| Item | Status | Date | Notes |
|------|--------|------|-------|
| `llms.txt` created | ⏳ Pending | — | Root of domain at /llms.txt |
| `llms-full.txt` created | ⏳ Pending | — | Optional extended version |
| AI crawlers allowed in robots.txt | ⏳ Pending | — | GPTBot, ClaudeBot, PerplexityBot |
| Organization schema + sameAs | ⏳ Pending | — | Wikipedia, LinkedIn, YouTube, etc. |
| Author/Person schema | ⏳ Pending | — | With sameAs cross-links |
| speakable property | ⏳ Pending | — | On content pages |
| IndexNow protocol | ⏳ Pending | — | For Bing Copilot + ChatGPT |
| Bing Webmaster Tools | ⏳ Pending | — | |
| SSR / prerendering configured | ⏳ Pending | — | Build-time Puppeteer prerender + hydrateRoot (NOT react-snap) |
| Wikipedia entity | ⏳ Pending | — | Requires notability criteria |
| Wikidata entity | ⏳ Pending | — | |

---

### Cat 17: AI Crawler Access {#cat-17-ai-crawlers}

**Score**: 🔵 N/A (requires live URL)

| Crawler | Status | Notes |
|---------|--------|-------|
| GPTBot | — | |
| ClaudeBot | — | |
| PerplexityBot | — | |
| OAI-SearchBot | — | |
| Google-Extended | — | |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 18: AI Citability {#cat-18-citability}

**Score**: 🔵 N/A (requires live URL)

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 19: llms.txt {#cat-19-llmstxt}

**Score**: 🔵 N/A (requires live URL)

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 20: E-E-A-T Content Quality {#cat-20-eeat}

**Score**: 🔵 N/A (requires live URL)

| Dimension | Score | Key Signals |
|-----------|-------|------------|
| Experience | —/25 | |
| Expertise | —/25 | |
| Authoritativeness | —/25 | |
| Trustworthiness | —/25 | |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 21: Brand Authority {#cat-21-brand}

**Score**: 🔵 N/A (requires live URL)

| Platform | Status | Score |
|----------|--------|-------|
| Wikipedia | — | —/30 |
| Reddit | — | —/20 |
| YouTube | — | —/15 |
| LinkedIn | — | —/10 |
| Industry | — | —/25 |

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 22: Platform-Specific {#cat-22-platforms}

**Score**: 🔵 N/A (requires live URL)

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 23: Schema — GEO Extensions {#cat-23-schema-geo}

**Score**: 🔵 N/A (requires live URL + code review)

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

### Cat 24: SSR for AI Crawlers {#cat-24-ssr}

**Score**: 🔵 N/A (requires live URL + code review)
**Rendering type detected**: —
**AI crawlers see content**: —

**Issues found this run**: _none_
**Fixes applied this run**: _none_

---

## Score History

| Run | Date | SEO Score | GEO Score | AI Visibility | Top Issue | Notes |
|-----|------|-----------|-----------|--------------|-----------|-------|
| #1 | {{YYYY-MM-DD}} | —/100 | N/A | N/A | — | First audit |

---

## Audit History

| Run | Date | Categories Audited | Issues Found | Issues Resolved | Notes |
|-----|------|--------------------|-------------|-----------------|-------|
| #1 | {{YYYY-MM-DD}} | All 16 SEO + GEO if URL available | {{N}} | {{N}} | First audit |
```

---

## How to Update on Subsequent Runs

When `SEO_REPORT.md` already exists, follow this update pattern:

1. **Header**: Update `Last updated` date and increment `Audit run` number
2. **Infrastructure Status**: Change ⏳ rows to ✅ for anything completed; add new rows if new packages/components were added
3. **Category Summary**: Update Status, Issues Found, and Issues Fixed counts for re-audited categories. Do NOT reset ✅ categories unless regression detected.
4. **Fix Plan Summary**: Add new FIX-XXX rows; update Status of existing rows that were resolved
5. **Detailed sections**: Append new findings under the affected category section with a `**Run #N findings:**` header. Keep prior run findings intact above it.
6. **Audit History**: Add a new row at the bottom of the table

### Example: Updating a category that had issues resolved

```markdown
### Cat 2: Page Titles {#cat-2-page-titles}

**Score**: 🔄 In Progress (3 of 5 pages fixed)

... (existing content from run #1 unchanged above) ...

**Run #2 findings (2024-02-10)**:
- Fixed: /dashboard — title and description added via <SeoHead> ✅
- Fixed: /apps/:id — title and description added ✅
- Fixed: /settings — title added; description still missing 🔄
- Outstanding: /profile — not yet addressed ⏳
- Outstanding: /billing — not yet addressed ⏳
```
