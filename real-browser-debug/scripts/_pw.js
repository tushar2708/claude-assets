// Shared helpers: resolve playwright-core, connect over CDP, pick the real logged-in page.
const path = require('path');

function loadChromium() {
  const candidates = [
    process.env.PLAYWRIGHT_CORE,
    // Skill-local install (created by ensure-playwright.sh) — checked first so the skill is
    // self-contained and does not depend on any host project having playwright installed.
    path.join(__dirname, '..', 'node_modules', 'playwright-core'),
    path.join(__dirname, 'node_modules', 'playwright-core'),
    // Host-project fallbacks.
    path.join(process.cwd(), 'cloud_frontend/node_modules/playwright-core'),
    path.join(process.cwd(), 'node_modules/playwright-core'),
    path.join(process.cwd(), 'node_modules/playwright'),
    'playwright-core',
    'playwright',
  ].filter(Boolean);
  for (const c of candidates) {
    try { return require(c).chromium; } catch (_) { /* try next */ }
  }
  throw new Error('playwright-core not found. Set PLAYWRIGHT_CORE to its absolute path.');
}

async function connect() {
  const chromium = loadChromium();
  const endpoint = process.env.CDP_ENDPOINT || 'http://localhost:9222';
  const browser = await chromium.connectOverCDP(endpoint);
  return browser;
}

// Pick the existing, non-devtools page (prefer one matching TARGET_URL_CONTAINS).
function pickPage(browser) {
  const target = process.env.TARGET_URL_CONTAINS || 'localhost:3000';
  const ctx = browser.contexts()[0];
  if (!ctx) return null;
  const pages = ctx.pages().filter((p) => !p.url().startsWith('devtools://'));
  return pages.find((p) => p.url().includes(target)) || pages[0] || null;
}

// Our own localhost sites use self-signed certs — bypassing the interstitial is safe.
async function bypassCertIfNeeded(page) {
  const title = await page.title().catch(() => '');
  const body = await page.evaluate(() => (document.body ? document.body.innerText : '')).catch(() => '');
  if (/Your connection is not private|NET::ERR_CERT|Privacy error|is not secure/i.test(`${title} ${body}`)) {
    // Chrome accepts the literal string "thisisunsafe" typed anywhere on the interstitial.
    await page.keyboard.type('thisisunsafe');
    await page.waitForTimeout(700);
  }
}

module.exports = { connect, pickPage, bypassCertIfNeeded };
