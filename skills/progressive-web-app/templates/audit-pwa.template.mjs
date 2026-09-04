// scripts/verify-pwa/audit-pwa.mjs — PWA installability/offline audit (Playwright + CDP)
// Tests: manifest fields, icons, SW scope, installability (L2 PWA)
// Usage: node audit-pwa.mjs http://localhost:4173

import { chromium } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { resolveReportsDir } from './create-reports-directory.mjs';

const reportsDir = resolveReportsDir(); // reports location from ai_skill_anchors/pwa.json
const url = process.argv[2] || 'http://localhost:4173';
const results = [];

const tests = {
  'L2-A4 installable (no CDP errors)': { name: 'Installable', desc: 'Web app manifest loads without CDP errors' },
  'L2-A1 manifest fields': { name: 'Manifest fields', desc: 'All required fields present: name, short_name, start_url, scope, display, theme_color, background_color, icons' },
  'L2-A2 icon-192': { name: 'Icon 192x192', desc: 'App icon at 192x192px with purpose=any' },
  'L2-A2 icon-512': { name: 'Icon 512x512', desc: 'App icon at 512x512px with purpose=any' },
  'L2-A2 icon-512-maskable': { name: 'Icon 512x512 maskable', desc: 'Maskable icon at 512x512px for adaptive display' },
  'L2-D1 apple-touch-icon <link>': { name: 'Apple Touch Icon', desc: 'iOS home screen icon via <link rel="apple-touch-icon">' },
  'L2-A3 <meta theme-color> present': { name: 'Theme color meta', desc: 'HTML <meta name="theme-color"> tag present' },
  'L2-A3 theme-color matches manifest': { name: 'Theme color match', desc: 'Meta theme-color value matches manifest.theme_color' },
  'L2-B1 SW controls page': { name: 'Service Worker active', desc: 'SW controls page and is actively registered' },
  'L2-B1 SW scope covers start_url': { name: 'SW scope correct', desc: 'Service worker scope covers the start_url' },
};

const rec = (testId, ok, detail = {}) => {
  const test = tests[testId];
  results.push({ id: testId, name: test.name, description: test.desc, ok, detail });
  const status = ok ? '✓' : '✗';
  console.log(`  ${status} ${test.name}`);
};

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(url, { waitUntil: 'load', timeout: 45000 });
// A cold first visit registers the SW asynchronously; wait for it to activate before reloading
// (a single reload is not enough over real network latency — e.g. a remote/production origin).
await page.evaluate(async () => {
  if (!('serviceWorker' in navigator)) return;
  await Promise.race([navigator.serviceWorker.ready, new Promise((r) => setTimeout(r, 12000))]);
}).catch(() => {});
await page.reload({ waitUntil: 'load', timeout: 45000 }); // 2nd load so the active SW controls the page

const cdp = await page.context().newCDPSession(page);
const app = await cdp.send('Page.getAppManifest');
let manifest = {};
try { manifest = JSON.parse(app.data || '{}'); } catch {}
rec('L2-A4 installable (no CDP errors)', (app.errors ?? []).length === 0, { errors: app.errors });

const need = ['name','short_name','start_url','scope','display','theme_color','background_color','icons'];
rec('L2-A1 manifest fields', need.every((k) => k in manifest), { missing: need.filter((k) => !(k in manifest)) });

const icons = manifest.icons ?? [];
const hasIcon = (sz, purpose) => icons.some((i) => (i.sizes||'').includes(sz) && (!purpose || (i.purpose||'').includes(purpose)));
rec('L2-A2 icon-192', hasIcon('192x192'));
rec('L2-A2 icon-512', hasIcon('512x512'));
rec('L2-A2 icon-512-maskable', hasIcon('512x512','maskable'));
rec('L2-D1 apple-touch-icon <link>', (await page.locator('link[rel="apple-touch-icon"]').count()) > 0);

const metaTheme = await page.locator('meta[name="theme-color"]').first().getAttribute('content').catch(() => null);
rec('L2-A3 <meta theme-color> present', !!metaTheme, { metaTheme });
rec('L2-A3 theme-color matches manifest', !!metaTheme && metaTheme.toLowerCase() === String(manifest.theme_color||'').toLowerCase(), { metaTheme, manifest: manifest.theme_color });

const sw = await page.evaluate(async () => {
  // Poll briefly: after the reload the SW may take a moment to activate and claim the page.
  const end = Date.now() + 8000;
  let reg = await navigator.serviceWorker.getRegistration();
  while (Date.now() < end && !(navigator.serviceWorker.controller && reg && reg.active)) {
    await new Promise((r) => setTimeout(r, 300));
    reg = await navigator.serviceWorker.getRegistration();
  }
  return { controller: !!navigator.serviceWorker.controller, active: !!(reg && reg.active), scope: (reg && reg.scope) || null };
});
const startUrl = new URL(manifest.start_url || '/', url).href;
rec('L2-B1 SW controls page', sw.controller && sw.active, sw);
rec('L2-B1 SW scope covers start_url', !!sw.scope && startUrl.startsWith(sw.scope), { scope: sw.scope, startUrl });

await browser.close();
fs.mkdirSync(reportsDir, { recursive: true });
fs.writeFileSync(path.join(reportsDir, 'pwa-checks.json'), JSON.stringify({ url, results }, null, 2));
const fail = results.filter((r) => !r.ok);
console.log(JSON.stringify({ pass: results.length - fail.length, fail: fail.length, results }, null, 2));
process.exit(fail.length ? 1 : 0);
