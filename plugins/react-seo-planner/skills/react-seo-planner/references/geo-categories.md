# GEO Audit Categories — Categories 17–24

Work through these after completing the 16 traditional SEO categories. These categories require BOTH code-level analysis
AND live-site analysis using WebFetch.

For live analysis to be possible the project must have a deployed URL. If no deployed URL is known, **record each GEO
category as "Code-Only Analysis" and note live analysis is blocked.** Still audit everything that can be checked in
code (robots.txt, llms.txt, structured data, rendering method).

---

## Category 17 — AI Crawler Access

Checks whether the site's `robots.txt` allows the AI crawlers that power AI search.

### Why This Matters

AI crawlers that are blocked in `robots.txt` cannot index or cite your content — regardless of content quality. Many
React apps inherit a restrictive `robots.txt` from a template that blocks all bots.

### Checks

| Crawler           | User-Agent          | Tier | Recommendation    | Severity if Blocked |
|-------------------|---------------------|------|-------------------|---------------------|
| GPTBot            | `GPTBot`            | 1    | ALLOW             | Critical            |
| OAI-SearchBot     | `OAI-SearchBot`     | 1    | ALLOW             | Critical            |
| ChatGPT-User      | `ChatGPT-User`      | 1    | ALLOW             | Critical            |
| ClaudeBot         | `ClaudeBot`         | 1    | ALLOW             | High                |
| PerplexityBot     | `PerplexityBot`     | 1    | ALLOW             | High                |
| Google-Extended   | `Google-Extended`   | 2    | ALLOW             | Medium              |
| GoogleOther       | `GoogleOther`       | 2    | ALLOW             | Medium              |
| Applebot-Extended | `Applebot-Extended` | 2    | ALLOW             | Medium              |
| Amazonbot         | `Amazonbot`         | 2    | ALLOW             | Low                 |
| FacebookBot       | `FacebookBot`       | 2    | ALLOW             | Low                 |
| CCBot             | `CCBot`             | 3    | Context-dependent | Low                 |
| anthropic-ai      | `anthropic-ai`      | 3    | Context-dependent | Low                 |
| Bytespider        | `Bytespider`        | 3    | BLOCK recommended | N/A                 |
| cohere-ai         | `cohere-ai`         | 3    | Context-dependent | Low                 |

**Scoring (0-100):**

| Component                                              | Points | How to Score                                           |
|--------------------------------------------------------|--------|--------------------------------------------------------|
| All 5 Tier 1 crawlers allowed                          | 50     | 10 points per Tier 1 crawler allowed                   |
| All 5 Tier 2 crawlers allowed                          | 25     | 5 points per Tier 2 crawler allowed                    |
| No blanket `User-agent: *` / `Disallow: /` blocking AI | 15     | Full 15 if no wildcard block; 0 if wildcard blocks all |
| llms.txt present (checked again here)                  | 5      | 5 if present at root                                   |
| Sitemap accessible to AI crawlers                      | 5      | 5 if sitemap.xml is not blocked                        |

**Recommended robots.txt additions** (insert into `public/robots.txt`):

```
# Tier 1 AI Search Crawlers — ALLOW
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GoogleOther
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: FacebookBot
Allow: /

# Tier 3 — BLOCK aggressive/low-value
User-agent: Bytespider
Disallow: /
```

---

## Category 18 — AI Citability

Evaluates whether content passages can be extracted and cited verbatim by AI systems.

### Why This Matters

Research from Princeton, Georgia Tech, and IIT Delhi (2024) found that GEO-optimized content achieves **30–115% higher
visibility** in AI-generated responses. AI systems preferentially extract passages that are 134–167 words,
self-contained, fact-rich, and answer-first.

**This is a live-site category.** Read content pages using WebFetch and score each.

### Scoring Rubric (0-100)

| Category                   | Weight | What to Measure                                                                                               |
|----------------------------|--------|---------------------------------------------------------------------------------------------------------------|
| Answer Block Quality       | 30%    | Every major section opens with a 1-2 sentence direct answer. Uses "X is..." or "X refers to..." patterns.     |
| Passage Self-Containment   | 25%    | 80%+ of content blocks can be understood without surrounding context. Explicit subject naming, not pronouns.  |
| Structural Readability     | 20%    | H1 > H2 > H3 hierarchy clean. Question-based H2/H3 headings. 2-4 sentence paragraphs. Tables for comparisons. |
| Statistical Density        | 15%    | 5+ specific statistics per 500 words. All claims backed by named sources or dates.                            |
| Uniqueness & Original Data | 10%    | First-party research, original surveys, proprietary data, or unique datasets.                                 |

**Score formula per content block:**

```
Block Score = (Answer * 0.30) + (SelfContain * 0.25) + (Structure * 0.20) + (Stats * 0.15) + (Unique * 0.10)
```

**Page-level score** = average of all block scores.

### Self-Containment Checklist (per paragraph)

1. Does the passage explicitly name its subject (not "it," "this," "they")?
2. Can someone understand the main point reading ONLY this passage?
3. Does the passage contain at least one specific fact, statistic, or named entity?
4. Is the passage between 50-200 words?
5. Does the passage avoid starting with conjunctions implying prior context?

### Answer Block Patterns (add to low-scoring pages)

- **Definition:** "X is [definition]." / "X refers to [explanation]."
- **Answer-first:** Answer in first sentence, supporting detail after.
- **Quantified:** "The average cost of X is $Y" not "Many factors affect the cost."
- **Comparison:** "X differs from Y in three ways: [list]."

### What Counts as a Statistic

- Specific percentages: "73% of marketers report..."
- Dollar amounts: "The average cost is $4,500 per month"
- Timeframes: "Implementation takes 6-8 weeks on average"
- Named studies: "According to the 2025 HubSpot State of Marketing Report..."
- Specific counts: "The platform integrates with 340+ tools"

### Code-Level Checks (auditable without deployed URL)

- Does the React component render meaningful text server-side? (see Cat 24)
- Are headings structured with question phrases for key pages?
- Is there a blog or resources section with long-form content?
- Are content components structured with clear paragraph delimiters?

---

## Category 19 — llms.txt

Checks for an `llms.txt` file at the site root — the emerging standard for AI system guidance.

### Why This Matters

As of early 2026, fewer than 5% of websites have an `llms.txt` file. It allows AI systems to understand site structure
and key content from a single file, improving citation accuracy and reducing AI hallucination about your business.

### Checks

| Element                                                  | Required    | Severity if Missing |
|----------------------------------------------------------|-------------|---------------------|
| `llms.txt` at `domain.com/llms.txt`                      | Yes         | High                |
| H1 title (business name)                                 | Yes         | High                |
| Blockquote description (< 200 chars, factual)            | Yes         | High                |
| At least one H2 section (`## Docs`, `## Products`, etc.) | Yes         | High                |
| 10-30 page entries with absolute URLs                    | Yes         | High                |
| Descriptions on every entry (10-30 words each)           | Yes         | Medium              |
| `## Key Facts` section with business info                | Recommended | Medium              |
| `## Contact` section with email at minimum               | Recommended | Low                 |
| `llms-full.txt` at root                                  | Optional    | Low                 |
| All listed URLs return 200 status                        | Yes         | High                |

### Required Format

```markdown
# [Business Name]

> [One-sentence description: what it does, who it serves, under 200 chars.]

## Docs

- [Most Important Page](https://domain.com/page): Description of the key content on this page.
- [Second Page](https://domain.com/page-2): What users and AI systems will find here.

## Products

- [Product A](https://domain.com/product): Core features, target users, and pricing model.

## Key Facts

- Founded in [year] by [name(s)]
- Headquartered in [City, Country]
- [Specific metric: e.g., "Serves 10,000+ businesses in 40 countries"]
- Industry: [Classification]

## Contact

- Website: https://domain.com
- Email: [primary contact email]
```

### Scoring (0-100)

| Component                                  | Points | How to Score                                     |
|--------------------------------------------|--------|--------------------------------------------------|
| `llms.txt` exists at root                  | 30     | 30 if found, 0 if not                            |
| Format valid (H1, blockquote, H2 sections) | 20     | 20 if all present, 10 if partial, 0 if malformed |
| 10+ page entries with descriptions         | 20     | 20 if 10+, 10 if 5-9, 0 if fewer                 |
| Key Facts section present                  | 15     | 15 if present, 0 if absent                       |
| All URLs valid (200 status)                | 10     | 10 if all valid, reduce by 1 per broken URL      |
| `llms-full.txt` also exists                | 5      | Bonus: 5 if present                              |

### Code-Level Fix

For React apps using Vite, place `llms.txt` in the `public/` directory — Vite copies it to `dist/` as-is during build.

---

## Category 20 — E-E-A-T & Content Quality

Evaluates Experience, Expertise, Authoritativeness, and Trustworthiness — Google's E-E-A-T framework now applies to *
*all competitive queries** (not just YMYL) as of December 2025.

**This is a live-site category.** Fetch key pages (homepage, blog, product/service pages, about page).

### E-E-A-T Scoring (100 points, 25 per dimension)

#### Experience (25 pts)

| Signal                                                     | Points |
|------------------------------------------------------------|--------|
| First-person accounts ("I tested...", "We implemented...") | 0-5    |
| Original research or proprietary data                      | 0-5    |
| Case studies with specific outcomes and numbers            | 0-4    |
| Screenshots, photos, or evidence of direct use             | 0-3    |
| Specific examples from personal experience                 | 0-4    |
| Demonstrations of process (not just outcome)               | 0-4    |

#### Expertise (25 pts)

| Signal                                                    | Points |
|-----------------------------------------------------------|--------|
| Author credentials visible (bio, degrees, certifications) | 0-5    |
| Technical depth appropriate to topic                      | 0-5    |
| Methodology explanation                                   | 0-4    |
| Data-backed claims with named sources                     | 0-4    |
| Industry-specific terminology used correctly              | 0-3    |
| Author page with detailed professional background         | 0-4    |

#### Authoritativeness (25 pts)

| Signal                                                | Points |
|-------------------------------------------------------|--------|
| Inbound citations from authoritative sources          | 0-5    |
| Author quoted or cited in press/media                 | 0-4    |
| Industry awards or recognition                        | 0-3    |
| Speaker credentials (conferences, events)             | 0-3    |
| Published in respected outlets                        | 0-4    |
| Comprehensive topic coverage                          | 0-3    |
| Brand mentioned on Wikipedia/authoritative references | 0-3    |

#### Trustworthiness (25 pts)

| Signal                                              | Points |
|-----------------------------------------------------|--------|
| Contact information visible (address, phone, email) | 0-4    |
| Privacy policy present and linked                   | 0-2    |
| Terms of service present                            | 0-1    |
| HTTPS with valid certificate                        | 0-2    |
| Editorial standards or corrections policy           | 0-3    |
| Transparent about business model and conflicts      | 0-3    |
| Reviews and testimonials from real customers        | 0-3    |
| Accurate claims (no detectable misinformation)      | 0-4    |
| Affiliate/sponsorship disclosures where applicable  | 0-3    |

#### Topical Authority Modifier

| Level      | Description                                   | Modifier |
|------------|-----------------------------------------------|----------|
| Authority  | 20+ pages covering core topic with clustering | +10      |
| Developing | 10-20 pages with some clustering              | +5       |
| Emerging   | 5-10 pages, limited clustering                | 0        |
| Thin       | < 5 pages, no clustering                      | -5       |

**Final score = E-E-A-T total + Topical modifier, capped at 100.**

### Word Count Benchmarks (floors, not targets)

| Page Type                       | Minimum | Ideal Range |
|---------------------------------|---------|-------------|
| Homepage                        | 500     | 500-1,500   |
| Blog post                       | 1,500   | 1,500-3,000 |
| Pillar content / Ultimate guide | 2,000   | 2,500-5,000 |
| Product page                    | 300     | 500-1,500   |
| Service page                    | 500     | 800-2,000   |
| About page                      | 300     | 500-1,000   |
| FAQ page                        | 500     | 1,000-2,500 |

### Low-Quality AI Content Signals (flag these)

- Generic openers: "In today's fast-paced world...", "It's important to note that..."
- No original insight — only rephrases widely available information
- Lack of first-hand experience — no anecdotes, case studies, or specific examples
- Hedging overload: "Generally speaking", "It depends on various factors" without specifying
- Missing human voice — no opinions, preferences, or professional judgment
- No data or sources — claims presented as facts without attribution

### Content Freshness

| Last Updated          | Rating     |
|-----------------------|------------|
| Within 3 months       | Excellent  |
| Within 6 months       | Good       |
| Within 12 months      | Acceptable |
| 12-24 months ago      | Warning    |
| No date or 24+ months | Critical   |

---

## Category 21 — Brand Authority Signals

Evaluates brand presence across platforms that AI models rely on for entity recognition.

### Why This Matters

Unlinked brand mentions correlate ~3x more strongly with AI visibility than traditional backlinks (Ahrefs, December
2025, 75K brands). The platforms where mentions appear matter more than the mentions themselves.

**This is a live-site category.** Use WebFetch to scan each platform.

### Composite Brand Authority Score Formula

```
Brand_Authority_Score = (YouTube * 0.25) + (Reddit * 0.25) + (Wikipedia * 0.20) + (LinkedIn * 0.15) + (Other * 0.15)
```

### Per-Platform Scoring

#### YouTube (25% weight) — Strongest AI Citation Signal (~0.737 correlation)

| Score  | Criteria                                                                           |
|--------|------------------------------------------------------------------------------------|
| 90-100 | Active channel, 10K+ subscribers, regular uploads, brand in 20+ third-party videos |
| 70-89  | Active channel, 1K+ subscribers, brand mentioned in 10-19 third-party videos       |
| 50-69  | Channel exists, brand mentioned in 5-9 third-party videos                          |
| 30-49  | Channel exists but inactive, 1-4 third-party video mentions                        |
| 10-29  | No channel or empty channel, 1-2 video mentions                                    |
| 0-9    | No YouTube presence                                                                |

**How to check:** WebFetch search `[brand name] site:youtube.com`; check `youtube.com/@[brand-name]` for official
channel.

#### Reddit (25% weight)

| Score  | Criteria                                                                                        |
|--------|-------------------------------------------------------------------------------------------------|
| 90-100 | Frequently recommended, positive sentiment, active official presence, own subreddit 5K+ members |
| 70-89  | Regularly mentioned, mostly positive, some official presence, multiple recommendation threads   |
| 50-69  | Mentioned in several threads, mixed sentiment, brand recognized                                 |
| 30-49  | Occasional mentions, 1-2 subreddits, no official presence                                       |
| 10-29  | Rare mentions, brand largely unknown                                                            |
| 0-9    | No Reddit presence                                                                              |

**How to check:** WebFetch search `"[brand name]" site:reddit.com`; check `reddit.com/r/[brand-name]`.

#### Wikipedia / Wikidata (20% weight)

**Use Python API check (most reliable):**

```bash
python3 -c "
import requests
from urllib.parse import quote_plus
brand = '[Brand_Name]'
api = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(brand)}&format=json'
r = requests.get(api, headers={'User-Agent': 'GEO-Audit/1.0'}, timeout=15)
results = r.json().get('query', {}).get('search', [])
if results and brand.lower() in results[0].get('title', '').lower():
    print(f'WIKIPEDIA EXISTS: https://en.wikipedia.org/wiki/{results[0][\"title\"].replace(\" \", \"_\")}')
else:
    print('No Wikipedia page found')
wd = requests.get(f'https://www.wikidata.org/w/api.php?action=wbsearchentities&search={quote_plus(brand)}&language=en&format=json', headers={'User-Agent': 'GEO-Audit/1.0'}, timeout=15).json()
entities = wd.get('search', [])
if entities:
    print(f'WIKIDATA: {entities[0].get(\"id\")} — {entities[0].get(\"description\", \"\")}')
"
```

| Score  | Criteria                                                                                         |
|--------|--------------------------------------------------------------------------------------------------|
| 90-100 | Detailed Wikipedia article (B-class+), Wikidata with full properties, founder has Wikipedia page |
| 70-89  | Wikipedia article exists (start-class+), Wikidata entry, mentioned in 2+ other articles          |
| 50-69  | Wikipedia stub exists, basic Wikidata entry                                                      |
| 30-49  | No Wikipedia article but mentioned in other articles or cited as reference                       |
| 10-29  | Brand mentioned in 1-2 articles as passing reference only                                        |
| 0-9    | No Wikipedia or Wikidata presence                                                                |

#### LinkedIn (15% weight)

| Score  | Criteria                                                                                                                 |
|--------|--------------------------------------------------------------------------------------------------------------------------|
| 90-100 | Active company page, 10K+ followers, leadership posts thought leadership, frequently mentioned by industry professionals |
| 70-89  | Active page, 5K+ followers, some employee thought leadership                                                             |
| 50-69  | Page exists, 1K+ followers, irregular posting                                                                            |
| 30-49  | Page exists but sparse or inactive                                                                                       |
| 10-29  | Basic company page with minimal information                                                                              |
| 0-9    | No LinkedIn company page                                                                                                 |

#### Other Platforms (15% weight)

| Platform       | Relevance          | Check                                   |
|----------------|--------------------|-----------------------------------------|
| Quora          | Moderate (B2C)     | `[brand] site:quora.com`                |
| Stack Overflow | High (dev tools)   | `[brand] site:stackoverflow.com`        |
| GitHub         | High (open-source) | `[brand] site:github.com`               |
| Hacker News    | Moderate (tech)    | `[brand] site:news.ycombinator.com`     |
| News/Press     | Moderate           | Search `"[brand]"` filter last 6 months |
| Podcasts       | Growing            | Check for podcast appearances           |

### Score Interpretation

| Score  | Rating                                                             |
|--------|--------------------------------------------------------------------|
| 85-100 | Dominant — AI systems highly likely to cite and recommend          |
| 70-84  | Strong — AI systems likely recognize and cite for relevant queries |
| 50-69  | Moderate — AI citation is inconsistent                             |
| 30-49  | Weak — AI systems may not recognize as distinct entity             |
| 0-29   | Minimal — AI systems unlikely to cite or recommend                 |

---

## Category 22 — Platform-Specific AI Optimization

Evaluates readiness across the 5 major AI search platforms.

**This is primarily a live-site category.** Code checks apply to structured data and meta tags.

Read [platform-optimization.md](platform-optimization.md) for the complete per-platform checklists and detailed scoring
rubrics.

### Quick Score Summary

| Platform            | How Selected                      | Top Priority                                | Score Max |
|---------------------|-----------------------------------|---------------------------------------------|-----------|
| Google AI Overviews | 92% from top-10 organic results   | Q&A structure, tables, direct answers       | 100       |
| ChatGPT Web Search  | Bing index + entity recognition   | Wikipedia, Wikidata, Bing Webmaster         | 100       |
| Perplexity AI       | Reddit 46.7% citations, freshness | Active Reddit, original research, freshness | 100       |
| Google Gemini       | Google index + Google properties  | YouTube, Knowledge Panel, Schema.org        | 100       |
| Bing Copilot        | Bing index + Microsoft ecosystem  | IndexNow, Bing WMT, LinkedIn, exact-match   | 100       |

**Combined Platform Score** = average of all 5 platform scores.

### Universal Wins (help ALL 5 platforms simultaneously)

1. Wikipedia / Wikidata entity presence
2. YouTube channel with topic-relevant content
3. Comprehensive structured content with clean headings
4. Schema.org Organization with complete `sameAs` array
5. Fast page load and clean server-rendered HTML
6. Author pages with credentials and `sameAs` links
7. Regular content updates with visible publication dates

---

## Category 23 — Structured Data: GEO Extensions

Supplements Category 7 (core structured data) with GEO-specific requirements. These checks are **code-auditable** — read
JSON-LD blocks in React components and `index.html`.

### sameAs Array (Single Highest-Impact Change)

The `sameAs` property connects your site to other platform entities. It is the most important structured data property
for AI entity recognition.

**Priority order for sameAs links:**

1. Wikipedia article — highest authority entity link
2. Wikidata item (e.g., `https://www.wikidata.org/wiki/Q12345`)
3. LinkedIn company page
4. YouTube channel URL
5. Twitter/X profile URL
6. Facebook page URL
7. Crunchbase profile (for startups/tech)
8. GitHub organization (for tech)
9. Google Scholar (for researchers/academics)
10. ORCID (for academics)
11. Instagram profile
12. Apple App Store / Google Play (for software)
13. BBB listing (for US businesses)

**Full Organization schema with GEO signals:**

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://domain.com/#organization",
  "name": "Company Name",
  "url": "https://domain.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://domain.com/logo.png",
    "width": 600,
    "height": 60
  },
  "description": "Concise description of what the company does.",
  "foundingDate": "2020-01-15",
  "founder": {
    "@type": "Person",
    "name": "Founder Name",
    "sameAs": "https://www.linkedin.com/in/founder"
  },
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "City",
    "addressRegion": "State",
    "addressCountry": "US"
  },
  "sameAs": [
    "https://en.wikipedia.org/wiki/Company_Name",
    "https://www.wikidata.org/wiki/Q12345",
    "https://www.linkedin.com/company/company-name",
    "https://www.youtube.com/@companyname",
    "https://twitter.com/companyname",
    "https://github.com/companyname",
    "https://www.crunchbase.com/organization/company-name"
  ],
  "knowsAbout": [
    "Topic 1",
    "Topic 2",
    "Topic 3"
  ]
}
```

### Author Schema with GEO Signals

For articles and blog posts, the Author schema is one of the strongest E-E-A-T signals:

```json
{
  "@type": "Person",
  "name": "Author Name",
  "url": "https://domain.com/author/author-name",
  "jobTitle": "Senior Engineer",
  "worksFor": {
    "@id": "https://domain.com/#organization"
  },
  "sameAs": [
    "https://www.linkedin.com/in/author",
    "https://twitter.com/author",
    "https://github.com/author"
  ],
  "knowsAbout": [
    "Topic A",
    "Topic B"
  ],
  "alumniOf": "University Name"
}
```

### speakable Property

Marks sections for voice/AI assistant consumption. Add to Article schemas:

```json
{
  "@type": "Article",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [
      ".article-summary",
      ".key-takeaway",
      ".faq-answer"
    ]
  }
}
```

### FAQPage Schema

While restricted from rich results (Google, Aug 2023), FAQPage schema **still helps AI platforms** parse Q&A content.
Add to pages with FAQ sections.

### SoftwareApplication Schema (for SaaS apps)

```json
{
  "@type": "SoftwareApplication",
  "name": "App Name",
  "applicationCategory": "BusinessApplication",
  "description": "What the app does",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "featureList": [
    "Feature 1",
    "Feature 2",
    "Feature 3"
  ],
  "operatingSystem": "Web"
}
```

### Scoring (0-100)

| Criterion                                                                        | Points |
|----------------------------------------------------------------------------------|--------|
| Organization schema with 5+ sameAs links                                         | 20     |
| Organization schema complete (logo, description, foundingDate, founder, address) | 15     |
| Article/BlogPosting with Author schema (full Person with sameAs)                 | 15     |
| knowsAbout property on Organization/Person (3+ topics)                           | 10     |
| speakable property on articles                                                   | 10     |
| SoftwareApplication schema (if SaaS)                                             | 10     |
| FAQPage schema (if FAQ sections present)                                         | 5      |
| BreadcrumbList on inner pages                                                    | 5      |
| JSON-LD format (not Microdata/RDFa)                                              | 5      |
| No deprecated schemas (SpecialAnnouncement, old VideoObject patterns)            | 5      |

---

## Category 24 — Server-Side Rendering for AI

Checks whether AI crawlers can read the site's content without JavaScript execution.

### Why This Matters (CRITICAL)

AI crawlers (GPTBot, ClaudeBot, PerplexityBot) do **NOT execute JavaScript**. A React SPA that renders client-side
produces an empty HTML shell. AI crawlers see no content at all — content quality is irrelevant if crawlers cannot read
it.

Even Googlebot, which does execute JavaScript, deprioritizes JS-rendered content due to crawl budget costs. There is a
2-4 week rendering lag for JS-only content.

### Detection Method

Compare raw HTML response vs. rendered DOM. Run this against the deployed URL:

```bash
# Check what AI crawlers actually see
curl -s https://[deployed-url] | grep -E '(h1|h2|h3|p|article|main)' | head -20
```

If the output is empty or shows only `<div id="root"></div>`, the site is entirely client-rendered.

### Checks

| Check                               | Pass Condition                                                  | Severity |
|-------------------------------------|-----------------------------------------------------------------|----------|
| Main content text in raw HTML       | Article body, product descriptions, page text visible in `curl` | Critical |
| H1, H2, H3 headings in raw HTML     | Headings present without JS                                     | Critical |
| JSON-LD structured data in raw HTML | Schema markup in `<head>` (not JS-injected)                     | High     |
| Meta tags in raw HTML               | `<title>`, `<meta name="description">`, OG tags visible         | High     |
| Navigation links in raw HTML        | `<nav>` and internal `<a href>` tags present                    | High     |
| Main navigation server-rendered     | Nav links visible in `curl` output                              | High     |

### Fix Options for React SPAs (Rule 1 compliant — no framework migration)

| Solution                | Effort | Description                                                                |
|-------------------------|--------|----------------------------------------------------------------------------|
| `prerender.io`          | Low    | Prerendering service; intercepts bot requests and serves pre-rendered HTML |
| `Netlify pre-rendering` | Low    | Built-in feature; enable in Netlify dashboard, no code changes             |
| `Vercel Edge Functions` | Medium | Pre-render specific routes at the edge                                     |
| `vite-prerender-plugin` | Medium | Generates static HTML snapshots at build time for Vite projects (free, npm package)          |
| `Cloudflare Workers`    | Medium | Pre-render at edge for bot User-Agents                                     |

**Do NOT suggest** migrating to Next.js, Gatsby, Remix, or any other framework (Rule 1).

### Scoring (0-100)

| Check                                         | Points |
|-----------------------------------------------|--------|
| Main content visible in raw HTML              | 40     |
| Headings visible in raw HTML                  | 20     |
| Meta tags + structured data in raw HTML       | 20     |
| Internal links in raw HTML                    | 10     |
| Pre-rendering solution deployed or documented | 10     |