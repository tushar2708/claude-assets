# Platform-Specific AI Search Optimization

Reference for Category 22 of the GEO audit. Work through each platform checklist when the deployed URL is available.

**Key Insight:** Only 11% of domains are cited by BOTH ChatGPT and Google AI Overviews for the same query. Each AI search platform uses different indexes, ranking logic, and source preferences. Platform-specific optimization is mandatory for serious GEO strategy.

---

## Platform 1: Google AI Overviews (AIO)

### How AIO Selects Sources
- 92% of AIO citations come from pages already ranking in the **top 10 organic results** — traditional SEO is the gateway
- 47% of citations come from pages ranking **below position 5** — AIO has its own selection logic favoring clarity and directness over raw rank
- Featured snippet optimization has ~70% overlap with AIO optimization
- AIO prefers **concise, factual, unambiguous answers** — hedging and filler reduce citation probability

### Checklist (score each item)

1. **Question-Based Headings**: H2/H3 headings phrased as questions matching real user queries. Check Google's "People Also Ask" for the target topic and mirror those phrasings.
2. **Direct Answer in First Paragraph**: After each question heading, provide a clear 1-2 sentence answer immediately, then expand. The first sentence should be a standalone citation candidate.
3. **Tables and Structured Comparisons**: AIO heavily cites tables. Convert any comparison, pricing, specification, or feature data into HTML tables with clear column headers.
4. **Ordered and Unordered Lists**: Step-by-step processes use ordered lists. Feature lists use unordered lists. AIO extracts these directly.
5. **FAQ Sections**: Add a dedicated FAQ section with 5-10 real questions using H3 headings for each. FAQPage schema (though restricted from rich results) still helps AIO extraction.
6. **Definitions and Glossary Boxes**: For industry-specific terms, provide clear definitions. Format: "**[Term]** is [concise definition]." AIO frequently cites definitions.
7. **Statistics with Sources**: Include specific numbers with attribution: "According to [Source], [statistic]." AIO prefers citable, specific claims over vague assertions.
8. **Publication Date**: Include visible publication date and last-updated date. AIO deprioritizes undated content.
9. **Author Byline**: Display author name with credentials, linked to an author page with bio, credentials, and sameAs links.
10. **Page Depth**: Keep target pages within 3 clicks of homepage. AIO rarely cites deep, orphaned content.

### Scoring Rubric (0-100)

| Criterion | Points | How to Score |
|-----------|--------|--------------|
| Ranks in top 10 for target queries | 20 | 20 if yes, 10 if top 20, 0 if beyond |
| Question-based headings present | 10 | 2 points per question heading, max 10 |
| Direct answers after headings | 15 | 3 points per direct answer, max 15 |
| Tables present for comparison data | 10 | 10 if used appropriately, 5 if partial, 0 if absent |
| Lists for processes/features | 10 | 10 if present, 5 if partial |
| FAQ section with 5+ questions | 10 | 10 if 5+, 5 if 1-4, 0 if none |
| Statistics with citations | 10 | 2 points per cited stat, max 10 |
| Publication/updated date visible | 5 | 5 if both dates, 3 if one, 0 if none |
| Author byline with credentials | 5 | 5 if full byline, 3 if name only, 0 if none |
| Clean URL + heading hierarchy | 5 | 5 if clean H1>H2>H3, 3 if minor issues, 0 if broken |

---

## Platform 2: ChatGPT Web Search

### How ChatGPT Selects Sources
- Uses **Bing's search index** as its foundation (not Google)
- Top citation sources by domain share: **Wikipedia (47.9%)**, Reddit (11.3%), YouTube, major news outlets
- Heavily weights **entity recognition** — brands that exist as structured entities (Wikipedia, Wikidata, Crunchbase) are far more likely to be cited
- Prefers **authoritative, well-established sources** over new or niche sites
- Longer, more comprehensive articles (2000+ words) get cited more often
- Tends to cite **the most canonical source** for a claim rather than the original discoverer

### Checklist (score each item)

1. **Wikipedia Presence**: Verify brand has a Wikipedia article. If not, assess notability criteria. If article exists, ensure accuracy and currency.
2. **Wikidata Entity**: Verify entity exists on Wikidata. If not, create a Wikidata item with: instance of, official website, social media links, founding date, headquarters location.
3. **Bing Webmaster Tools**: Verify the site is registered. Submit sitemap. Check for crawl errors.
4. **Bing Index Coverage**: Use `site:domain.com` on Bing to verify key pages are indexed. Bing may differ from Google's index.
5. **Reddit Authority**: Check for brand mentions on Reddit. Identify relevant subreddits. Assess authentic participation in discussions.
6. **YouTube Presence**: Verify YouTube channel exists with relevant content. Video descriptions should contain full URLs and entity information.
7. **Authoritative Backlinks**: ChatGPT/Bing weight `.edu`, `.gov`, and major publication backlinks heavily.
8. **Entity Consistency**: Brand name, founding date, leadership, and key facts must be **consistent** across Wikipedia, Crunchbase, LinkedIn, and official website.
9. **Comprehensive Content**: Pages targeting ChatGPT citation should be **2000+ words** with thorough topic coverage.
10. **Clear Attribution**: Include "About" sections, company descriptions, and founding stories for entity grounding.

### Scoring Rubric (0-100)

| Criterion | Points | How to Score |
|-----------|--------|--------------|
| Wikipedia article exists and is accurate | 20 | 20 if exists, 10 if stub, 0 if none |
| Wikidata entity with 5+ properties | 10 | 10 if complete, 5 if basic, 0 if none |
| Bing index coverage of key pages | 10 | 10 if full, 5 if partial, 0 if poor |
| Reddit brand mentions (positive) | 10 | 10 if active discussions, 5 if mentions, 0 if none |
| YouTube channel with relevant content | 10 | 10 if active, 5 if present but sparse, 0 if none |
| Authoritative backlinks (.edu, .gov, press) | 15 | 3 points per authoritative backlink category, max 15 |
| Entity consistency across platforms | 10 | 10 if consistent, 5 if minor discrepancies, 0 if major |
| Content comprehensiveness (2000+ words) | 10 | 10 if thorough, 5 if adequate, 0 if thin |
| Bing Webmaster Tools configured | 5 | 5 if verified, 0 if not |

---

## Platform 3: Perplexity AI

### How Perplexity Selects Sources
- Top citation sources: **Reddit (46.7%)**, Wikipedia, YouTube, major publications
- Places the **heaviest emphasis on community validation** of all AI search platforms
- Strongly favors **discussion threads** where claims are debated, validated, or expanded
- Prefers recent content — publication date is a strong ranking signal
- Cites **multiple sources per answer** (typically 5-15), more opportunity for mid-authority sites
- Uses its own crawling infrastructure in addition to search APIs

### Checklist (score each item)

1. **Active Reddit Presence**: Brand or representatives participating authentically in relevant subreddit discussions. Not promotional — helpful, specific, and community-oriented.
2. **Reddit AMAs and Threads**: Participate in AMAs, detailed discussion threads, and community Q&As. Perplexity treats these as high-signal content.
3. **Forum and Community Presence**: Beyond Reddit — Hacker News, Stack Overflow, Quora, and niche industry forums. Perplexity indexes these heavily.
4. **Discussion-Friendly Content**: Opinion pieces, research findings, contrarian takes, original data. Content that gets shared and debated in communities ranks higher.
5. **Freshness Signals**: Publish content with clear dates. Update content regularly. Perplexity deprioritizes stale content more aggressively than other platforms.
6. **Multiple Source Validation**: Claims in content should be supported by other sources. Perplexity cross-references and prefers claims verifiable from multiple origins.
7. **YouTube Video Content**: Create video content that Perplexity can reference. Ensure video titles, descriptions, and transcripts contain target information.
8. **Direct, Quotable Passages**: Write paragraphs that stand alone as citations. Each paragraph should make one clear point with supporting evidence.
9. **Original Data and Research**: Publish original surveys, benchmarks, case studies, or datasets. Perplexity heavily favors primary sources.
10. **Perplexity Pages**: Check if Perplexity has created a "Page" about your topic/brand. These curated summaries influence future citations.

### Scoring Rubric (0-100)

| Criterion | Points | How to Score |
|-----------|--------|--------------|
| Active Reddit presence in relevant subreddits | 20 | 20 if active contributor, 10 if mentioned, 0 if absent |
| Forum/community mentions (HN, SO, Quora) | 10 | 10 if multiple platforms, 5 if one, 0 if none |
| Content freshness (updated within 6 months) | 10 | 10 if recent, 5 if within year, 0 if older |
| Original research/data published | 15 | 15 if original research, 10 if case studies, 5 if some data, 0 if none |
| YouTube content with transcripts | 10 | 10 if active channel, 5 if some videos, 0 if none |
| Quotable, standalone paragraphs | 10 | 2 points per well-structured quotable paragraph, max 10 |
| Multi-source claim validation | 10 | 10 if claims well-sourced, 5 if some sourcing, 0 if none |
| Discussion-generating content | 10 | 10 if content gets shared/discussed, 5 if some engagement, 0 if none |
| Wikipedia/Wikidata presence | 5 | 5 if present, 0 if absent |

---

## Platform 4: Google Gemini

### How Gemini Selects Sources
- Uses **Google's search index** plus strong weighting toward **Google-owned properties**
- YouTube content is weighted significantly more heavily than in standard Google Search
- Google Business Profile data is directly accessible to Gemini
- Uses Google's Knowledge Graph directly — entity presence in Knowledge Graph is a major advantage
- Structured data (Schema.org) is consumed directly by Gemini for entity understanding
- Multi-modal: can reference images, videos, and text together

### Checklist (score each item)

1. **Google Knowledge Panel**: Check if the brand has a Google Knowledge Panel. If not, claim through Google Business Profile or structured data. Ensure all information is accurate.
2. **Google Business Profile**: Complete and optimize GBP with all fields: hours, services, photos, posts, Q&A. Gemini pulls directly from GBP for local queries.
3. **YouTube Strategy**: Create YouTube content for every key topic. Optimize titles, descriptions, timestamps, and closed captions. Gemini cites YouTube more than any other AI platform.
4. **YouTube Chapters and Timestamps**: Use chapters (timestamps in description) so Gemini can reference specific video segments.
5. **Google Merchant Center**: For e-commerce, ensure products are in Google Merchant Center. Gemini references product data directly.
6. **Structured Data (Schema.org)**: Implement comprehensive Schema.org markup (see Cat 23). Gemini uses this for entity understanding more aggressively than other platforms.
7. **Google Sites Ecosystem**: Ensure presence across Google ecosystem: Google Scholar (for research), Google News (for publishers), Google Maps (for local).
8. **Image Optimization**: Gemini is multi-modal. Use descriptive alt text, structured image filenames, and high-quality images with every piece of content.
9. **Google E-E-A-T Signals**: Author pages, about pages, editorial policies, and expertise demonstrations with extra weight.
10. **Chrome Web Store / Google Workspace Marketplace**: For software companies, presence on Google platforms adds entity signals.

### Scoring Rubric (0-100)

| Criterion | Points | How to Score |
|-----------|--------|--------------|
| Google Knowledge Panel exists | 15 | 15 if complete, 10 if partial, 0 if none |
| Google Business Profile complete | 10 | 10 if fully optimized, 5 if basic, 0 if none |
| YouTube channel with topic-relevant content | 20 | 20 if active with chapters, 10 if present, 0 if none |
| Schema.org structured data implemented | 15 | 15 if comprehensive, 10 if basic, 5 if minimal, 0 if none |
| Google ecosystem presence (Scholar, News, Maps) | 10 | 10 if 3+, 5 if 1-2, 0 if none |
| Image optimization (alt text, filenames) | 10 | 10 if all images optimized, 5 if partial, 0 if none |
| E-E-A-T signals (author pages, about, editorial) | 10 | 10 if strong, 5 if partial, 0 if weak |
| Google Merchant Center (if e-commerce) | 5 | 5 if applicable and active, N/A otherwise |
| Multi-modal content (text + images + video) | 5 | 5 if rich multi-modal, 3 if some, 0 if text-only |

---

## Platform 5: Bing Copilot

### How Copilot Selects Sources
- Uses **Bing's search index** (shared infrastructure with ChatGPT but different ranking/selection)
- Supports **IndexNow protocol** for near-instant indexing of new and updated content
- Tends to cite **fewer sources per answer** (typically 3-5) but gives more prominent attribution
- Microsoft ecosystem integration: LinkedIn, GitHub, Microsoft Learn content is weighted
- Prefers pages with clear, structured markup and fast load times

### Checklist (score each item)

1. **Bing Webmaster Tools**: Register and verify site. Submit XML sitemap. Review and fix any crawl issues.
2. **IndexNow Implementation**: Implement IndexNow to notify Bing of content changes in real-time. Submit a key file at `/.well-known/indexnow-key.txt` and ping the IndexNow API on content publish/update. Key for ChatGPT (uses Bing index) AND Bing Copilot.
3. **LinkedIn Company Page**: Ensure the company LinkedIn page is complete with accurate description, employee connections, and regular posts. Copilot indexes LinkedIn content.
4. **GitHub Presence**: For tech companies, maintain an active GitHub presence. Copilot references GitHub repos, documentation, and README files.
5. **Microsoft Learn / Documentation**: If relevant, contribute to Microsoft Learn or ensure documentation is compatible with Microsoft's documentation standards.
6. **Bing Places for Business**: Equivalent to Google Business Profile. Complete all fields for local search visibility in Copilot.
7. **Clear Meta Descriptions**: Bing/Copilot weights meta descriptions more heavily than Google does. Compelling, keyword-rich meta descriptions for every page.
8. **Social Signals**: Bing has historically weighted social signals (shares, likes, engagement) more than Google. Maintain active social media presence.
9. **Exact-Match Keywords**: Bing's algorithm is more literal about keyword matching. Include exact target phrases in titles, headings, and body content.
10. **Fast Page Load**: Copilot deprioritizes slow pages. Target sub-2-second load time.

### Scoring Rubric (0-100)

| Criterion | Points | How to Score |
|-----------|--------|--------------|
| Bing Webmaster Tools verified + sitemap | 15 | 15 if verified, 5 if partial, 0 if not |
| IndexNow protocol implemented | 15 | 15 if active, 0 if not |
| Bing index coverage of key pages | 10 | 10 if full, 5 if partial, 0 if poor |
| LinkedIn company page (complete) | 10 | 10 if complete, 5 if basic, 0 if none |
| GitHub presence (if applicable) | 5 | 5 if active, N/A if not applicable |
| Meta descriptions optimized | 10 | 10 if all key pages, 5 if partial, 0 if missing |
| Social media engagement signals | 10 | 10 if active engagement, 5 if present, 0 if none |
| Exact-match keywords in titles/headings | 10 | 10 if well-optimized, 5 if partial, 0 if not |
| Page load speed < 2 seconds | 10 | 10 if < 2s, 5 if < 4s, 0 if > 4s |
| Bing Places configured (if local) | 5 | 5 if complete, N/A if not local |

---

## Cross-Platform Priority Matrix

### Platform-Specific Top 4 Priorities
| Priority | Google AIO | ChatGPT | Perplexity | Gemini | Copilot |
|----------|-----------|---------|-----------|-------|---------|
| **#1** | Top-10 ranking | Wikipedia | Reddit presence | YouTube | IndexNow |
| **#2** | Q&A structure | Entity graph (Wikidata) | Original research | Knowledge Panel | Bing WMT |
| **#3** | Tables/lists | Bing SEO | Freshness | Schema.org | LinkedIn |
| **#4** | FAQ structure | Reddit + YouTube | Community forums | GBP | Meta descriptions |

### AI Citation Source Share by Platform (2025 data)
| Source | Google AIO | ChatGPT | Perplexity | Gemini | Copilot |
|--------|-----------|---------|-----------|-------|---------|
| Wikipedia | High | 47.9% | High | High | High |
| Reddit | Medium | 11.3% | 46.7% | Low | Low |
| YouTube | Medium | Medium | Medium | **Very High** | Low |
| News | Medium | Medium | Medium | Medium | Medium |
| LinkedIn | Low | Low | Low | Low | **High** |
