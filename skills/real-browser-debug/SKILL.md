---
name: real-browser-debug
description: >
  Drive and debug a REAL, human-logged-in Chrome via Playwright over CDP — NOT the Playwright
  MCP's throwaway browser. Use whenever you need to see or operate the actual dashboard behind a
  login wall / Google OAuth (e.g. localhost:3000), perform real clicks/fills/navigation/screenshots
  in the user's own logged-in session, or capture real network responses (incl. failing 4xx/5xx
  bodies) and console from a logged-in page. The skill handles self-signed cert bypass (our own
  sites) and a "log in alongside the user" handshake: it drives the browser to the login screen,
  asks the user (via AskUserQuestion) to complete Google login, waits for confirmation, then
  continues. Trigger when a task needs a genuine authenticated browser window, not a fresh
  automation profile that Google OAuth rejects.
---

# real-browser-debug

Debug and operate a **real Chrome window the user is (or will be) logged into**, by attaching
Playwright to it over the Chrome DevTools Protocol (CDP). This is the ONLY reliable way to work
inside an authenticated dashboard, because:

- **The Playwright MCP launches its own throwaway browser** with a clean, isolated profile — it does
  NOT share the user's session, and Google OAuth rejects that automation profile
  ("This browser or app may not be secure"). Do **not** use the Playwright MCP for authenticated flows.
- **Attaching to a browser the human launched** (with a persistent profile + a remote-debugging port)
  reuses the user's real cookies/session. The human performs the OAuth login; automation only attaches
  afterward and drives the already-authenticated tab.

## When to use
- You need to *see* what the real dashboard renders behind auth (subscription state, an error toast,
  a stuck spinner) — not just reason about code.
- You need to *operate* it: click a button, fill a form, navigate, take a screenshot, capture the
  exact 4xx/5xx response body of a failing request.
- Any localhost app served over a **self-signed cert**.

## When NOT to use
- Unauthenticated, public pages where the MCP's fresh browser is fine.
- Pure code analysis with no need to observe the live UI.

---

## Golden rules

1. **Attach, never launch a fresh automation browser.** Use `connectOverCDP` and operate on the
   browser's **existing context** (`browser.contexts()[0]`) and **existing pages** — never
   `browser.newContext()` (that would be an isolated, logged-out session).
2. **Never close the user's browser.** `browser.close()` over CDP only *detaches*; it does not kill
   the user's Chrome. Do not call `context.close()` / `page.close()` on their tabs.
3. **SSL cert errors on our own sites are safe to bypass.** These are our localhost dev servers with
   self-signed certs — there is no security concern. Bypass via either:
   - launch flag `--ignore-certificate-errors` (preferred — no interstitial appears), or
   - runtime: on Chrome's "Your connection is not private" interstitial, type `thisisunsafe`
     (the scripts do this automatically in `bypassCertIfNeeded`).
4. **Log in alongside the user.** If a page redirects to the login screen, do NOT try to automate
   Google OAuth (it will be rejected). Instead drive to the login page, then use **AskUserQuestion**
   to ask the user to complete the login manually, wait for their confirmation, then continue.
5. **Every automated operation is real.** This skill is for doing things (click/fill/navigate/
   screenshot), not only reading the DOM.
6. **ONE action per call — always. This is how it MUST be done.** Debug interactively like a human
   (and like the Playwright MCP): make **one** `drive.js` call that performs **a single action**, read
   its output/screenshot, decide the next action, then make the **next single call**. Do NOT batch a
   multi-step script and run it blind. The browser persists between calls (it is the user's real
   Chrome; `drive.js` only reconnects each time), so state carries over exactly as if the connection
   were held open. Pass the action **inline** as one JSON object:
   `node .../drive.js '{"action":"click","selector":"..."}'`. A multi-step JSON file is allowed ONLY
   for a fully known, non-interactive sequence you are certain of end to end — never for exploration.

---

## Prerequisites (checked/handled by the skill)

- Google Chrome installed (`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` on macOS).
- `playwright-core` available (the npm package, NOT the Playwright MCP). Step 0 (`ensure-playwright.sh`)
  installs it into the skill's own `node_modules` if missing; the scripts auto-resolve it from there,
  from the host repo (`cloud_frontend/node_modules/playwright-core`), or from `PLAYWRIGHT_CORE`.
- A Chrome instance running with `--remote-debugging-port` (default `9222`). The skill launches it if
  absent.

---

## Workflow (orchestrator steps)

### 0. Ensure Playwright is installed (ALWAYS run first)
The scripts import `playwright-core` (used for `connectOverCDP`). This is a hard dependency and may
not be present on a fresh machine or in a repo without a frontend. Run the installer FIRST — it is
idempotent (no-ops if already resolvable) and installs `playwright-core` into the **skill's own**
`node_modules` (isolated; it does not touch the host repo, and it does NOT download browser binaries
— we attach to the user's real Chrome):

```bash
bash .claude/skills/real-browser-debug/scripts/ensure-playwright.sh
```

> Note: this needs only the `playwright-core` **npm package** — not the Playwright **MCP server**.
> Do NOT rely on the Playwright MCP for this skill (it launches its own throwaway browser and can't
> reuse the user's login).

### 1. Ensure a real, debuggable Chrome is running
Run the launcher (idempotent — no-ops if CDP is already live):

```bash
bash .claude/skills/real-browser-debug/scripts/launch-chrome.sh "https://localhost:3000"
```

Environment overrides: `CDP_PORT` (default 9222), `CHROME_DEBUG_PROFILE`
(default `$HOME/.smritea-chrome-debug`). The persistent profile means the user logs in **once** and
stays logged in across restarts.

Verify CDP is live:
```bash
curl -s http://localhost:9222/json/version | head -c 200
```

> If the user already started Chrome themselves with the debug port, skip the launch — just verify.

### 2. Probe the current state (read-only)
```bash
node .claude/skills/real-browser-debug/scripts/probe.js
```
Reports: open pages, the active URL, `navigator.serviceWorker.getRegistrations()` (settles any
service-worker question), and auth-token localStorage keys (a login signal).

### 3. If not logged in → log in alongside the user
If the probe shows the active URL is the login screen (e.g. `/auth/login`) or no auth token:

1. Make sure the login page is on screen (drive a `goto` to the app root if needed — the app will
   redirect to login itself).
2. Call **AskUserQuestion**:
   - question: "A Google login is required in the Chrome window I opened. Please complete the login
     there, then confirm. Have you finished logging in?"
   - header: "Browser login"
   - options: `["Yes, I'm logged in", "Not yet / it failed"]`
3. **STOP and wait** for the answer. Do not proceed on your own.
4. On "Yes", re-run `probe.js` to confirm the auth token is present and you're past the login screen.
   On "Not yet", surface any error and offer email/password login (`/auth/register` → `/auth/login`),
   which is NOT subject to Google's automation block.

### 4. Drive real operations — ONE ACTION PER CALL (primary mode)
Pass a **single** action inline as JSON and run the driver. Read the result, then decide the next
single action. This is deliberately interactive: you do **not** predict the whole workflow up front —
each real result (URL, screenshot, captured 500 body) informs the next single call.

```bash
# one action, then STOP and read the output before the next call
node .claude/skills/real-browser-debug/scripts/drive.js '{"action":"screenshot","path":"/tmp/now.png"}'
node .claude/skills/real-browser-debug/scripts/drive.js '{"action":"click","selector":"button:has-text(\"Authorize Card\")"}'
node .claude/skills/real-browser-debug/scripts/drive.js '{"action":"url"}'
```

`drive.js` operates on the existing logged-in tab, auto-bypasses self-signed certs, and **always
records failing (>=400) network responses with their bodies** — ideal for capturing a real 500 body.
The browser state persists between these separate calls (it's the user's real Chrome), so reconnecting
per call behaves exactly like a held-open session.

> A JSON **file** of multiple steps is supported too — but ONLY for a sequence you already know end to
> end and are not exploring. For debugging, use one inline action per call (Golden Rule 6).

Supported step actions:

| action | fields | effect |
|---|---|---|
| `goto` | `url`, `waitUntil?`, `timeout?` | navigate (cert auto-bypassed) |
| `click` | `selector`, `timeout?` | click element |
| `fill` | `selector`, `value` | type into input |
| `press` | `key`, `selector?` | keyboard press |
| `waitForSelector` | `selector`, `state?`, `timeout?` | wait for element |
| `waitForURL` | `url`, `timeout?` | wait for navigation |
| `waitForTimeout` | `ms` | sleep |
| `screenshot` | `path`, `fullPage?` | save PNG (put under the scratchpad dir) |
| `text` | `selector` | print element text |
| `evaluate` | `expr` (string) | run JS in the page, print JSON result |
| `url` | — | print current URL |

Example `steps.json` (screenshot the billing page and capture any failing request when clicking a button):
```json
[
  { "action": "goto", "url": "https://localhost:3000/dashboard/billing" },
  { "action": "waitForSelector", "selector": "text=Billing" },
  { "action": "screenshot", "path": "/tmp/billing-before.png" },
  { "action": "click", "selector": "button:has-text('Authorize Card')" },
  { "action": "waitForTimeout", "ms": 1500 },
  { "action": "screenshot", "path": "/tmp/billing-after.png" }
]
```
At the end, `drive.js` prints `HTTP_FAILURES` (method/url/status/body for every >=400 response seen),
plus `FINAL_URL`. Read the saved screenshots with the Read tool to *see* the result.

### 5. Report
Relay what actually happened — the screenshot(s), the captured failure bodies, the final URL — not
assumptions.

---

## Notes / caveats
- **Google OAuth + remote-debugging:** Google sometimes shows "browser may not be secure" for a
  remote-debug Chrome. A persistent (non-default) `--user-data-dir` reduces this; if it still blocks,
  the user can retry, or use email/password login (unaffected by Google's check).
- **One-off, no permanent config change:** this skill needs **zero** MCP-config edits. It does not
  touch `~/.claude.json`. (Adding `--cdp-endpoint` to the Playwright MCP would permanently force it to
  attach and break the default fresh-browser behavior — avoid that.)
- **Do not `newContext()`** — it creates a logged-out isolated session and defeats the purpose.
