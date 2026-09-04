// Read-only probe of the real, attached browser: pages, active URL, service workers, auth signal.
// Usage: node probe.js
// Env: CDP_ENDPOINT (default http://localhost:9222), TARGET_URL_CONTAINS (default localhost:3000)
const { connect, pickPage } = require('./_pw');

(async () => {
  const browser = await connect();
  const ctx = browser.contexts()[0];
  const pages = ctx ? ctx.pages() : [];
  console.log('contexts:', browser.contexts().length, 'pages:', pages.length);
  pages.forEach((p, i) => console.log(`  [${i}] ${p.url()}`));

  const page = pickPage(browser);
  if (!page) { console.log('NO_PAGE'); await browser.close(); return; }
  console.log('ACTIVE_URL:', page.url());

  const sw = await page.evaluate(async () => {
    if (!('serviceWorker' in navigator)) return 'no-SW-api';
    const regs = await navigator.serviceWorker.getRegistrations();
    return regs.map((r) => ({ scope: r.scope, active: !!r.active, waiting: !!r.waiting, installing: !!r.installing }));
  }).catch((e) => `eval-error: ${e.message}`);
  console.log('SERVICE_WORKERS:', JSON.stringify(sw));

  const auth = await page.evaluate(() => {
    try { return Object.keys(localStorage).filter((k) => /token|auth|jwt|session/i.test(k)); }
    catch (_) { return 'localStorage-blocked'; }
  }).catch(() => 'eval-error');
  console.log('AUTH_LOCALSTORAGE_KEYS:', JSON.stringify(auth));

  await browser.close(); // detach only; does NOT close the user's Chrome
})().catch((e) => { console.error('FATAL', e.message); process.exit(1); });
