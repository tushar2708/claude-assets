#!/usr/bin/env bash
# docsmith test runner. Runs the pytest suite with all runtime deps provided
# by uv (no venv or install step needed).
# NOTE: this file is created by the Write tool (which cannot set the
# executable bit); `chmod +x` is applied separately.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --with pytest --with pyyaml --with jinja2 python -m pytest tests/ "$@"
