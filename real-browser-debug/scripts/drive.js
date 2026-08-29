// Drive REAL operations on the attached, logged-in browser tab from a JSON steps file.
// Always records failing (>=400) network responses + bodies. Never opens a new context.
// Usage: node drive.js /path/to/steps.json
// Env: CDP_ENDPOINT (default http://localhost:9222), TARGET_URL_CONTAINS (default localhost:3000)
const fs = require('fs');
const { connect, pickPage, bypassCertIfNeeded } = require('./_pw');

async function runStep(page, s, i) {
  const tag = `[step ${i} ${s.action}]`;
  switch (s.action) {
    case 'goto':
      await page.goto(s.url, { waitUntil: s.waitUntil || 'domcontentloaded', timeout: s.timeout || 30000 });
      await bypassCertIfNeeded(page);
      return `${tag} -> ${page.url()}`;
    case 'click':
      await page.click(s.selector, { timeout: s.timeout || 10000 });
      return `${tag} clicked ${s.selector}`;
    case 'fill':
      await page.fill(s.selector, s.value, { timeout: s.timeout || 10000 });
      return `${tag} filled ${s.selector}`;
    case 'press':
      await page.press(s.selector || 'body', s.key);
      return `${tag} pressed ${s.key}`;
    case 'waitForSelector':
      await page.waitForSelector(s.selector, { state: s.state || 'visible', timeout: s.timeout || 15000 });
      return `${tag} saw ${s.selector}`;
    case 'waitForURL':
      await page.waitForURL(s.url, { timeout: s.timeout || 15000 });
      return `${tag} url=${page.url()}`;
    case 'waitForTimeout':
      await page.waitForTimeout(s.ms || 1000);
      return `${tag} waited ${s.ms || 1000}ms`;
    case 'screenshot':
      await page.screenshot({ path: s.path, fullPage: !!s.fullPage });
      return `${tag} saved ${s.path}`;
    case 'text': {
      const t = await page.textContent(s.selector).catch(() => null);
      return `${tag} ${JSON.stringify(t)}`;
    }
    case 'evaluate': {
      const r = await page.evaluate(s.expr);
      return `${tag} ${JSON.stringify(r)}`;
    }
    case 'url':
      return `${tag} ${page.url()}`;
    default:
      return `${tag} UNKNOWN_ACTION`;
  }
}

// Accept EITHER a path to a JSON steps file, OR inline JSON (a single {action...} object or an
// array). Inline single-object form is meant for ONE-STEP-AT-A-TIME driving:
//   node drive.js '{"action":"click","selector":"button:has-text(\"Sign In\")"}'
// The browser persists between calls (it's the user's real Chrome); this script only reconnects.
function parseSteps(arg) {
  if (!arg) return [];
  const t = arg.trim();
  if (t.startsWith('[') || t.startsWith('{')) {
    const parsed = JSON.parse(t);
    return Array.isArray(parsed) ? parsed : [parsed];
  }
  return JSON.parse(fs.readFileSync(arg, 'utf8'));
}

(async () => {
  const steps = parseSteps(process.argv[2]);
  const browser = await connect();
  const page = pickPage(browser);
  if (!page) { console.log('NO_PAGE'); await browser.close(); return; }
  await page.bringToFront();

  // Capture failing network responses (great for grabbing a real 500 body).
  const failures = [];
  page.on('response', async (resp) => {
    const st = resp.status();
    if (st >= 400) {
      let body = '';
      try { body = (await resp.text()).slice(0, 800); } catch (_) { /* opaque */ }
      failures.push({ method: resp.request().method(), url: resp.url(), status: st, body });
    }
  });

  for (let i = 0; i < steps.length; i++) {
    try {
      console.log(await runStep(page, steps[i], i));
    } catch (e) {
      console.log(`[step ${i} ${steps[i].action}] ERROR ${e.message}`);
      if (steps[i].critical) break;
    }
  }

  await page.waitForTimeout(500); // let late responses land
  console.log('FINAL_URL', page.url());
  console.log('HTTP_FAILURES', JSON.stringify(failures, null, 2));
  await browser.close(); // detach only
})().catch((e) => { console.error('FATAL', e.message); process.exit(1); });
