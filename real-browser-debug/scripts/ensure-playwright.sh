#!/usr/bin/env bash
# STEP 0 of the skill: guarantee `playwright-core` is importable by the skill scripts.
# We only need playwright-core (for connectOverCDP) — NOT full `playwright` and NOT any
# downloaded browser binaries (we attach to the user's already-running Chrome).
# Resolution order: env override -> skill-local install -> host project -> global.
# If nothing is found, install playwright-core INTO THE SKILL's own node_modules (isolated;
# does not pollute the host repo).
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

resolvable() {
  # True if node can require playwright-core from any of the candidate locations.
  node -e '
    const path = require("path");
    const skill = process.argv[1];
    const cands = [
      process.env.PLAYWRIGHT_CORE,
      path.join(skill, "node_modules", "playwright-core"),
      path.join(process.cwd(), "cloud_frontend/node_modules/playwright-core"),
      path.join(process.cwd(), "node_modules/playwright-core"),
      "playwright-core",
    ].filter(Boolean);
    for (const c of cands) { try { require.resolve(c); console.log(c); process.exit(0); } catch (_) {} }
    process.exit(1);
  ' "$SKILL_DIR" 2>/dev/null
}

if FOUND="$(resolvable)"; then
  echo "playwright-core OK: ${FOUND}"
  exit 0
fi

echo "playwright-core not found — installing into skill dir: ${SKILL_DIR}"
if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm not on PATH; cannot auto-install playwright-core." >&2
  echo "Install manually: (cd '${SKILL_DIR}' && npm install playwright-core)" >&2
  exit 1
fi

( cd "$SKILL_DIR" \
  && [ -f package.json ] || npm init -y >/dev/null 2>&1 \
  ; PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install playwright-core >/tmp/ensure-playwright.log 2>&1 )

if FOUND="$(resolvable)"; then
  echo "installed playwright-core: ${FOUND}"
  exit 0
fi
echo "ERROR: install completed but playwright-core still not resolvable. See /tmp/ensure-playwright.log" >&2
exit 1
