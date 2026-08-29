#!/usr/bin/env bash
# Launch a REAL Chrome with remote debugging + a persistent profile so:
#   - Google OAuth works (human logs in once; automation attaches after),
#   - Playwright can attach over CDP,
#   - self-signed certs on our own localhost sites are ignored (no security concern).
# Idempotent: no-ops if a CDP endpoint is already live on the port.
#
# Usage: launch-chrome.sh [URL]
# Env:   CDP_PORT (default 9222), CHROME_DEBUG_PROFILE (default $HOME/.smritea-chrome-debug)
set -euo pipefail

PORT="${CDP_PORT:-9222}"
PROFILE="${CHROME_DEBUG_PROFILE:-$HOME/.smritea-chrome-debug}"
URL="${1:-}"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ ! -x "$CHROME" ]; then
  echo "ERROR: Chrome not found at: $CHROME" >&2
  echo "Set the correct path or install Google Chrome." >&2
  exit 1
fi

if curl -s "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
  echo "CDP already live on port ${PORT} — reusing it."
  exit 0
fi

# --ignore-certificate-errors: our own localhost dev certs are self-signed and safe.
# --user-data-dir: persistent profile keeps the login across restarts.
"$CHROME" \
  --remote-debugging-port="${PORT}" \
  --user-data-dir="${PROFILE}" \
  --ignore-certificate-errors \
  --no-first-run \
  --no-default-browser-check \
  ${URL:+"$URL"} >/dev/null 2>&1 &

PID=$!
echo "Launched Chrome (pid ${PID}) — CDP on port ${PORT}, profile ${PROFILE}"

# Wait until the CDP endpoint answers (up to ~10s).
for _ in $(seq 1 20); do
  if curl -s "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
    echo "CDP endpoint is ready on port ${PORT}."
    exit 0
  fi
  sleep 0.5
done
echo "WARNING: Chrome started but CDP endpoint did not respond within 10s." >&2
exit 0
