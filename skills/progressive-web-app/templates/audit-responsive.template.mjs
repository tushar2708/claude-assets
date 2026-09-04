// scripts/verify-pwa/audit-responsive.mjs
// Level-1 responsive checker — the SINGLE source of truth for responsive verification (merged from the
// former Playwright viewport suite). Per public route it asserts (a) no horizontal overflow across
// 320→1280 viewports and (b) — on the home route at mobile widths — that the marketing hamburger OPENS
// and reveals the nav links. Robust by construction: it reuses (or auto-starts, like Playwright's
// webServer) the dev server, and retries the first cold-compile load so a slow on-demand Vite transform
// is never mistaken for a layout defect. Emits responsive-audit.json (naming the offending element on
// overflow) for the PWA report.

import { chromium } from '@playwright/test';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { resolveReportsDir, readAnchor } from './create-reports-directory.mjs';

const anchor = readAnchor();
const appDir = path.resolve(anchor._projectRoot, anchor.app_dir);

// When an external target (e.g. production) is passed we audit it verbatim and NEVER manage a local
// server. With no arg we default to the local HTTPS dev server on :3000 and manage it (reuse if already
// serving, else auto-start); the self-signed cert is tolerated via ignoreHTTPSErrors everywhere.
const externalUrl = process.argv[2];
const baseUrl = externalUrl || 'https://localhost:3000';
const manageServer = !externalUrl;
const results = [];
const rec = (route, viewport, ok, detail = {}) => {
  const vp = `${viewport.width}px`;
  const status = ok ? '✓' : '✗';
  // Make each line self-explanatory so a failure needs no JSON lookup: state WHAT was checked and the
  // actual measurement. The assertion is: documentElement.scrollWidth must be ≤ clientWidth (no
  // horizontal overflow). Navigation reachability is recorded but does not fail the test.
  let reason;
  if (detail.error) {
    reason = `page failed to load — ${String(detail.error).split('\n')[0]}`;
  } else if (detail.overflow) {
    const widest = detail.offenders?.widest ?? [];
    const culprits = widest
      .map((o) => `<${o.tag}${o.id ? '#' + o.id : ''}${o.cls ? ' class="' + o.cls + '"' : ''}> ${o.width}px${o.text ? ` ("${o.text}")` : ''}`)
      .join('; ');
    const more = detail.offenders && detail.offenders.total > widest.length ? ` [+${detail.offenders.total - widest.length} more]` : '';
    reason = `HORIZONTAL OVERFLOW: content is ${detail.scrollWidth}px wide but viewport is ${detail.clientWidth}px (+${detail.scrollWidth - detail.clientWidth}px past the edge)` +
      (culprits ? `\n        offending element(s): ${culprits}${more}` : '');
  } else {
    reason = `no horizontal overflow (content ${detail.scrollWidth}px ≤ viewport ${detail.clientWidth}px); nav ${detail.navigationReachable ? 'reachable' : 'not shown'}`;
  }
  console.log(`  ${status} ${route} @ ${vp} — ${reason}`);
  results.push({
    id: `L1-${route}@${vp}`,
    name: `${route} at ${vp}`,
    description: `Asserts no horizontal overflow (documentElement.scrollWidth ≤ clientWidth) at a ${vp}-wide viewport; also records whether primary navigation is reachable (informational).`,
    ok,
    detail: { ...detail, viewport: vp }
  });
};

// Records the mobile marketing-nav BEHAVIOR check (home route, mobile widths): the hamburger must OPEN
// and reveal the nav links — a stronger assertion than "the trigger is visible".
const recNav = (route, viewport, ok, detail = {}) => {
  const vp = `${viewport.width}px`;
  const status = ok ? '✓' : '✗';
  const reason = ok
    ? 'marketing hamburger opens and reveals the nav links'
    : `marketing hamburger did NOT reveal the nav links${detail.error ? ` — ${String(detail.error).split('\n')[0]}` : ''}`;
  console.log(`  ${status} nav ${route} @ ${vp} — ${reason}`);
  results.push({
    id: `L1-nav-${route}@${vp}`,
    name: `marketing hamburger at ${vp}`,
    description: `Asserts that below md the marketing hamburger opens and reveals the primary nav links (they must not simply disappear on mobile).`,
    ok,
    detail: { ...detail, viewport: vp }
  });
};

const viewports = [
  { name: 'w320', width: 320, height: 720 },
  { name: 'w375', width: 375, height: 812 },
  { name: 'w768', width: 768, height: 1024 },
  { name: 'w1024', width: 1024, height: 768 },
  { name: 'w1280', width: 1280, height: 800 },
];
const MOBILE_WIDTHS = new Set([320, 375]); // widths where the hamburger-opens check applies

const routes = anchor.routes; // public routes from ai_skill_anchors/pwa.json
// Optional mobile-nav behavior check, from the anchor: { route, trigger_label, reveal_link }. When set,
// at mobile widths on that route the hamburger (a button whose accessible name matches trigger_label)
// must OPEN and reveal a link whose name matches reveal_link. Omit it for apps with no mobile hamburger.
const navCheck = anchor.mobile_nav_check ?? null;

// Auto-started dev server (only when we start one; a reused server is left running).
let devProc = null;
const stopDevServer = () => {
  if (devProc && !devProc.killed) {
    devProc.kill('SIGTERM');
    devProc = null;
  }
};
process.on('exit', stopDevServer);
process.on('SIGINT', () => { stopDevServer(); process.exit(1); });

// Probe readiness with a real, cert-tolerant browser navigation. Node's fetch rejects the dev server's
// self-signed HTTPS cert, so it can't be used for readiness; a Playwright page with ignoreHTTPSErrors can.
const probe = async (browser, url, timeout) => {
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await ctx.newPage();
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout });
    return true;
  } catch {
    return false;
  } finally {
    await ctx.close();
  }
};

const waitForServer = async (browser, url, timeout = 120000) => {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (await probe(browser, url, 3000)) return true;
    await new Promise((r) => setTimeout(r, 1000));
  }
  return false;
};

// Navigate with ONE retry. The first hit on a route triggers Vite's on-demand compile, whose latency can
// exceed a single navigation budget; the retry lands on the now-warm route. We wait for 'load' (not
// 'networkidle', which never settles while the dev HMR socket is open) — the overflow assertion needs a
// laid-out document, not network silence. Returns null on success, or the last error on repeated failure.
const gotoResilient = async (page, url) => {
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      await page.goto(url, { waitUntil: 'load', timeout: 30000 });
      return null;
    } catch (err) {
      if (attempt === 2) return err;
    }
  }
  return null;
};

try {
  const browser = await chromium.launch();

  // Reuse a server already serving baseUrl, else auto-start the dev server (mirrors Playwright's
  // webServer). Skipped entirely for external targets.
  if (manageServer) {
    if (await probe(browser, baseUrl, 3000)) {
      console.log(`Reusing server already serving ${baseUrl}`);
    } else {
      console.log(`No server on ${baseUrl} — starting "npm run dev"...`);
      devProc = spawn('npm', ['--prefix', appDir, 'run', 'dev'], { stdio: 'ignore' });
      const ready = await waitForServer(browser, baseUrl, 120000);
      if (!ready) {
        console.error(`Dev server did not become ready at ${baseUrl} within 120s`);
        await browser.close();
        stopDevServer();
        process.exit(1);
      }
      console.log('Dev server ready');
    }
  }

  for (const route of routes) {
    const url = `${baseUrl}${route}`;
    console.log(`Testing ${url}...`);

    // Warm the route once (pays the cold-compile cost up front via the same resilient navigation) so the
    // measured viewport loop is fast and consistent. Warm-up failures are ignored — the loop measures.
    const warmCtx = await browser.newContext({ ignoreHTTPSErrors: true });
    const warmPage = await warmCtx.newPage();
    await gotoResilient(warmPage, url);
    await warmCtx.close();

    for (const viewport of viewports) {
      const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, ignoreHTTPSErrors: true });
      const page = await context.newPage();

      try {
        const navErr = await gotoResilient(page, url);
        if (navErr) {
          rec(route, viewport, false, { error: navErr.message });
          continue;
        }

        // Check for horizontal overflow (L1 hard gate)
        const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
        const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
        const hasOverflow = scrollWidth > clientWidth;

        // When overflow is detected, identify the actual offending element(s) in the page so the failure
        // NAMES the culprit component (tag + classes + width + text) — not just the total overflow amount.
        let offenders = null;
        if (hasOverflow) {
          offenders = await page.evaluate(() => {
            const docW = document.documentElement.clientWidth;
            // A wide element only stretches the PAGE if no ancestor clips/scrolls it. Elements inside an
            // overflow-x auto/scroll/hidden/clip container scroll internally and are NOT the culprit.
            const isClipped = (el) => {
              let p = el.parentElement;
              while (p && p !== document.documentElement) {
                const ox = getComputedStyle(p).overflowX;
                if (ox === 'hidden' || ox === 'auto' || ox === 'scroll' || ox === 'clip') return true;
                p = p.parentElement;
              }
              return false;
            };
            const list = [];
            for (const el of document.querySelectorAll('*')) {
              const r = el.getBoundingClientRect();
              if (r.right > docW + 1 && !isClipped(el)) {
                list.push({
                  width: Math.round(r.width),
                  right: Math.round(r.right),
                  tag: el.tagName.toLowerCase(),
                  cls: (el.className && el.className.toString ? el.className.toString() : '').trim().slice(0, 70),
                  id: el.id || undefined,
                  text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40),
                });
              }
            }
            // Sort by how far the RIGHT edge extends past the viewport — the page-wideners come first.
            list.sort((a, b) => b.right - a.right);
            return { total: list.length, widest: list.slice(0, 3) };
          });
        }

        // Check if navigation is reachable
        const hamburger = await page.locator('button[aria-label*="menu" i], button[aria-label*="navigation" i]').first();
        const navVisible = await hamburger.isVisible().catch(() => false);

        rec(route, viewport, !hasOverflow, {
          scrollWidth,
          clientWidth,
          overflow: hasOverflow,
          navigationReachable: navVisible,
          offenders,
        });

        // Mobile marketing-nav behavior: at mobile widths on the configured route, the hamburger must OPEN
        // and reveal the nav links (ported from the Playwright suite — a real behavior gate, not just
        // "visible"). Selectors come from the anchor so this file stays project-agnostic.
        if (navCheck && route === navCheck.route && MOBILE_WIDTHS.has(viewport.width)) {
          let navOk = false;
          let navBehaviorErr = null;
          try {
            await page.getByRole('button', { name: new RegExp(navCheck.trigger_label, 'i') }).click({ timeout: 5000 });
            navOk = await page.getByRole('link', { name: new RegExp(navCheck.reveal_link, 'i') }).isVisible();
          } catch (e) {
            navBehaviorErr = e.message;
          }
          recNav(route, viewport, navOk, { error: navBehaviorErr });
        }
      } catch (err) {
        rec(route, viewport, false, { error: err.message });
      } finally {
        await context.close();
      }
    }
  }

  await browser.close();
  stopDevServer();

  // Write results
  const fs = await import('node:fs');
  const reportsDir = resolveReportsDir(); // reports location from ai_skill_anchors/pwa.json
  fs.mkdirSync(reportsDir, { recursive: true });
  fs.writeFileSync(
    path.join(reportsDir, 'responsive-audit.json'),
    JSON.stringify({ baseUrl, results }, null, 2)
  );

  const fail = results.filter((r) => !r.ok);
  console.log(JSON.stringify({ pass: results.length - fail.length, fail: fail.length, results }, null, 2));
  process.exit(fail.length ? 1 : 0);
} catch (err) {
  console.error('Responsive audit failed:', err);
  stopDevServer();
  process.exit(1);
}
