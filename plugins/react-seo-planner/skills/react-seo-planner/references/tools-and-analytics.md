# Tools, Analytics & GA4 Setup

## Table of Contents
1. [Free SEO Measurement Tools](#1-free-seo-measurement-tools)
2. [Free npm Libraries](#2-free-npm-libraries)
3. [Google Analytics 4 Setup Walkthrough](#3-google-analytics-4-setup-walkthrough)
4. [Sending web-vitals to GA4](#4-sending-web-vitals-to-ga4)

---

## 1. Free SEO Measurement Tools

These tools quantify SEO health with zero cost. Use them to validate findings from the code audit and to provide a before/after comparison when the fix plan is implemented.

| Tool | URL | What It Measures | Best For |
|------|-----|-----------------|----------|
| **Google PageSpeed Insights** | pagespeed.web.dev | Core Web Vitals (field + lab), performance, Lighthouse score | Single-URL CWV check, shows real-user data from CrUX |
| **Lighthouse (Chrome DevTools)** | Built into Chrome → F12 → Lighthouse | Performance, SEO, Accessibility, Best Practices — 0–100 scores | Fast in-browser audit without any setup |
| **Google Search Console** | search.google.com/search-console | Indexing status, coverage errors, Core Web Vitals from real users, search impressions | Authoritative indexing and ranking data; shows crawl errors |
| **Google Rich Results Test** | search.google.com/test/rich-results | JSON-LD structured data validity and rich result eligibility | Validate every structured data fix before deploying |
| **Schema Markup Validator** | validator.schema.org | Full schema.org JSON-LD correctness | Deep schema validation beyond rich results |
| **Screaming Frog SEO Spider** | screamingfrog.co.uk/seo-spider | Crawls up to 500 URLs for free; titles, metas, h1s, redirects, status codes | Full site crawl to find missing titles, duplicate metas, broken links |
| **Ahrefs Webmaster Tools** | ahrefs.com/webmaster-tools | Backlinks, broken links, on-page SEO issues for your own verified sites | Free tier; reveals backlink profile and crawl issues |
| **web.dev Measure** | web.dev/measure | Lighthouse score + CWV for any public URL | Quick external Lighthouse run without local Chrome |
| **Facebook Sharing Debugger** | developers.facebook.com/tools/debug | How Facebook/Instagram renders OG tags for a URL | Validate OG image, title, description before sharing |
| **LinkedIn Post Inspector** | linkedin.com/post-inspector | How LinkedIn renders OG tags | LinkedIn-specific OG check |
| **Robots.txt Tester** | search.google.com/search-console/robots-testing-tool | Whether Googlebot can crawl specific URLs | Verify robots.txt rules don't accidentally block pages |
| **XML Sitemap Validator** | xmlsitemapvalidator.com | Syntax, URL count, lastmod dates in sitemap.xml | Validate sitemap before submitting to Search Console |

### How to run a full Lighthouse audit in Chrome

1. Open the page in Chrome
2. Open DevTools: `F12` or `Cmd+Option+I`
3. Click the **Lighthouse** tab
4. Select: **Navigation**, device **Desktop** (run mobile separately)
5. Check: Performance, Accessibility, Best practices, SEO
6. Click **Analyze page load**
7. Save the HTML report for before/after comparison

SEO score of 100 is achievable and the goal. Performance score of 90+ is a good baseline.

---

## 2. Free npm Libraries

| Library | Install | Purpose |
|---------|---------|---------|
| `react-helmet-async` | `npm i react-helmet-async` | Per-page `<head>` management (title, meta, OG, canonical) — the foundation of all title/meta fixes |
| `web-vitals` | `npm i web-vitals` | Measures LCP, CLS, INP in real user browsers using PerformanceObserver |
| `vite-plugin-sitemap` | `npm i -D vite-plugin-sitemap` | Generates `sitemap.xml` automatically from route list at build time |
| `react-router-sitemap-helper` | `npm i react-router-sitemap-helper` | Extracts routes from react-router config for sitemap generation |

---

## 3. Google Analytics 4 Setup Walkthrough

### Step 1: Create a GA4 Property

1. Go to https://analytics.google.com
2. Click **Admin** (gear icon, bottom left)
3. Under **Account**, click **Create Account** (or use an existing account)
4. Under **Property**, click **Create Property**
5. Enter property name (e.g., "Acme Cloud - Production"), timezone, currency
6. Click **Next** → choose "Web" as the platform
7. Enter your domain (e.g., `app.acmecloud.com`) → click **Create stream**
8. Copy the **Measurement ID** — it looks like `G-XXXXXXXXXX`

### Step 2: Store the Measurement ID as an Environment Variable

Never hardcode the GA4 Measurement ID in source code — it will be visible in the bundle but should still be environment-specific.

```bash
# .env.production
VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX

# .env.development
VITE_GA4_MEASUREMENT_ID=G-YYYYYYYYYY  # separate dev property, or omit to skip tracking
```

```
# .gitignore — do NOT commit .env files with real IDs
.env.production
.env.local
```

### Step 3: Install gtag via Script Tag in index.html

GA4's recommended approach for Vite/React SPAs is loading `gtag.js` directly in `index.html`. This avoids hydration issues and keeps the loading script out of the React bundle.

```html
<!-- index.html — inside <head>, before </head> -->
<!-- Google tag (gtag.js) — load async to avoid render blocking -->
<script async src="https://www.googletagmanager.com/gtag/js?id=%VITE_GA4_MEASUREMENT_ID%"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '%VITE_GA4_MEASUREMENT_ID%', {
    send_page_view: false  // We will send page views manually on route changes
  });
</script>
```

> **Important**: `send_page_view: false` prevents GA4 from firing a page view on the initial HTML load. React SPAs navigate without full page reloads, so we must fire page views manually on route changes (Step 5).

> **Vite note**: `%VITE_GA4_MEASUREMENT_ID%` is replaced at build time by Vite. For CRA, use `%REACT_APP_GA4_MEASUREMENT_ID%`.

### Step 4: Create a GA4 Utility Module

```tsx
// src/app/analytics.ts

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void;
  }
}

const GA4_ID = import.meta.env.VITE_GA4_MEASUREMENT_ID as string;

/** Send a page view. Call on every route change. */
export function trackPageView(path: string, title: string) {
  if (!window.gtag || !GA4_ID) return;
  window.gtag('event', 'page_view', {
    page_path: path,
    page_title: title,
    send_to: GA4_ID,
  });
}

/** Send a custom event. */
export function trackEvent(eventName: string, params?: Record<string, unknown>) {
  if (!window.gtag || !GA4_ID) return;
  window.gtag('event', eventName, { send_to: GA4_ID, ...params });
}
```

### Step 5: Track Route Changes (Critical for SPAs)

Without this, GA4 only records the first page load and misses all in-app navigation.

```tsx
// src/app/RouteTracker.tsx
import { useEffect } from 'react';
import { useLocation } from 'react-router';
import { trackPageView } from './analytics';

export function RouteTracker() {
  const location = useLocation();

  useEffect(() => {
    // document.title is set by react-helmet-async before this fires
    trackPageView(location.pathname + location.search, document.title);
  }, [location]);

  return null;
}
```

```tsx
// src/app/root-layout.tsx (or wherever your router's root component is)
import { Outlet } from 'react-router';
import { RouteTracker } from './RouteTracker';

export function RootLayout() {
  return (
    <>
      <RouteTracker />
      <Outlet />
    </>
  );
}
```

> **Why this works**: `useLocation` fires on every React Router navigation. The `document.title` at the time of the effect will be whatever `react-helmet-async` last set it to — which is the per-page title. This gives GA4 accurate page paths AND meaningful page titles.

### Step 6: Verify in GA4 Realtime

1. Open https://analytics.google.com → your property
2. Navigate to **Reports → Realtime**
3. Open your app in a browser tab and navigate between a few pages
4. GA4 Realtime should show:
   - **Page views** with correct `page_path` values (e.g., `/dashboard`, `/apps/abc123`)
   - **Page title** values matching your `<title>` tags
5. If page views show but page titles are all "(not set)" → `react-helmet-async` is not applied yet (fix Category 2 first)

### Step 7: Submit Site to Google Search Console

After GA4 is running:

1. Go to https://search.google.com/search-console
2. Click **Add property** → choose "URL prefix" (easier for SPAs)
3. Enter your production URL (e.g., `https://app.acmecloud.com`)
4. Verify ownership — easiest method: **HTML tag** (add `<meta name="google-site-verification" content="...">` inside `<SeoHead>` default output)
5. After verification, submit your sitemap under **Sitemaps** → enter `sitemap.xml`
6. Google Search Console will now show:
   - **Coverage**: which pages are indexed vs. excluded
   - **Core Web Vitals**: real-user LCP/CLS/INP data (shows after ~28 days of data)
   - **Search results**: impressions, clicks, average position per page

Google Search Console is the most authoritative free SEO tool available. Check it weekly once set up.

---

## 4. GEO-Specific Tools

These tools are specifically for the GEO categories (17–24). Use when a deployed URL is available.

| Tool | URL | What It Measures | GEO Category |
|------|-----|-----------------|--------------|
| **Bing Webmaster Tools** | webmaster.bing.com | Bing index coverage, crawl errors, IndexNow status | Cat 17, 22 |
| **PageSpeed Insights** | pagespeed.web.dev | INP (Interaction to Next Paint) field data | Cat 24 |
| **Schema.org Validator** | validator.schema.org | Full JSON-LD schema validation beyond rich results | Cat 23 |
| **Rich Results Test** | search.google.com/test/rich-results | Google rich result eligibility per schema | Cat 23 |
| **Perplexity AI** | perplexity.ai | Search for brand name to check if Perplexity cites the site | Cat 22 |
| **Bing site: search** | bing.com | `site:yourdomain.com` — verify Bing index coverage | Cat 22 |
| **Wikipedia Search API** | en.wikipedia.org/w/api.php | Brand presence check (use API, not web search) | Cat 21 |
| **Wikidata Search** | wikidata.org | Entity existence and property completeness | Cat 21, 23 |
| **llms.txt checker** | llmstxt.cloud | Validate llms.txt format and completeness | Cat 19 |

### GEO Scripts (run via Bash)

```bash
# Install script dependencies (one-time setup)
pip install -r requirements.txt

# Score a page's citability for AI models
python scripts/citability_scorer.py https://yourdomain.com/page

# Scan brand presence across AI-cited platforms
python scripts/brand_scanner.py "Your Brand Name" yourdomain.com

# Fetch and parse page HTML (detect SSR vs CSR, extract meta tags)
python scripts/fetch_page.py https://yourdomain.com

# Generate or validate llms.txt
python scripts/llmstxt_generator.py https://yourdomain.com
```

### Detecting CSR vs SSR (critical for Cat 24 and AI crawler visibility)

```bash
# If response body is just <div id="root"></div> → page is 100% client-side → AI crawlers see NOTHING
curl -s https://yourdomain.com | grep -E '(<h1|<h2|<p|<article|<main)' | wc -l
# 0 results = CSR only (CRITICAL GEO issue)
# 10+ results = content visible to AI crawlers (good)
```

---

## 5. Sending web-vitals to GA4

After completing the GA4 setup above, send Core Web Vitals as GA4 custom events:

```tsx
// src/app/vitals.ts
import { onCLS, onINP, onLCP, type Metric } from 'web-vitals';
import { trackEvent } from './analytics';

function sendToGA4(metric: Metric) {
  trackEvent('web_vitals', {
    metric_name: metric.name,          // 'LCP', 'CLS', 'INP'
    metric_value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
    metric_rating: metric.rating,      // 'good', 'needs-improvement', 'poor'
    metric_id: metric.id,              // unique ID for deduplication
    metric_delta: Math.round(metric.delta),
  });
}

export function reportWebVitals() {
  onCLS(sendToGA4);
  onINP(sendToGA4);
  onLCP(sendToGA4);
}
```

```tsx
// src/main.tsx
import { reportWebVitals } from './app/vitals';
// ... after ReactDOM.createRoot().render()
reportWebVitals();
```

In GA4, create a custom report:
- **Reports → Explore → Blank exploration**
- Dimension: `event_name` = `web_vitals`, then `metric_name`
- Metric: `event_count`, custom dimension `metric_value`
- This shows real-user CWV data segmented by LCP/CLS/INP across your actual user base
