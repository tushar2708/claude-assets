#!/usr/bin/env bash
set -euo pipefail

# Color definitions
BOLD=$(tput bold 2>/dev/null || echo "")
GREEN=$(tput setaf 2 2>/dev/null || echo "")
YELLOW=$(tput setaf 3 2>/dev/null || echo "")
RED=$(tput setaf 1 2>/dev/null || echo "")
NC=$(tput sgr0 2>/dev/null || echo "")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "${BOLD}react-seo-geo-planner — Python Dependency Installer${NC}"
echo "======================================================"
echo ""

# Step 1: Check Python version
echo "${BOLD}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "${RED}ERROR: Python not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PY_VERSION=$("$PY_CMD" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$("$PY_CMD" -c "import sys; print(sys.version_info.major)")
PY_MINOR=$("$PY_CMD" -c "import sys; print(sys.version_info.minor)")

if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 8 ]]; then
    echo "${RED}ERROR: Python 3.8 or higher required. Found Python ${PY_VERSION}.${NC}"
    exit 1
fi
echo "${GREEN}✓ Python ${PY_VERSION} found${NC}"

# Step 2: Install pip dependencies
echo ""
echo "${BOLD}Installing Python dependencies from requirements.txt...${NC}"
if ! pip3 install -r "${SCRIPT_DIR}/requirements.txt"; then
    echo "${RED}ERROR: pip install failed. Check your Python/pip setup.${NC}"
    exit 1
fi
echo "${GREEN}✓ All packages installed${NC}"

# Step 3: Optional Playwright Chromium installation
echo ""
read -r -p "${YELLOW}Install Playwright Chromium browser? (needed for PDF reports with screenshots) [y/N]: ${NC}" install_pw
if [[ "$install_pw" =~ ^[Yy]$ ]]; then
    echo "Installing Playwright Chromium..."
    playwright install chromium
    echo "${GREEN}✓ Playwright Chromium installed${NC}"
else
    echo "Skipping Playwright Chromium. You can run 'playwright install chromium' later if needed."
fi

# Step 4: Verify imports
echo ""
echo "${BOLD}Verifying package imports...${NC}"
if "$PY_CMD" -c "import bs4, requests, lxml, validators, reportlab; print('Core packages OK')" 2>/dev/null; then
    echo "${GREEN}✓ All core packages import successfully${NC}"
else
    echo "${YELLOW}WARNING: One or more packages failed to import. Try re-running pip install.${NC}"
fi

# Step 5: Success message
echo ""
echo "${GREEN}${BOLD}Installation complete!${NC}"
echo ""
echo "Usage examples:"
echo "  python scripts/citability_scorer.py https://yourdomain.com/page"
echo "  python scripts/brand_scanner.py \"Your Brand\" yourdomain.com"
echo "  python scripts/fetch_page.py https://yourdomain.com"
echo "  python scripts/llmstxt_generator.py https://yourdomain.com"
echo ""
echo "${YELLOW}Note: Make this script executable with: chmod +x install.sh${NC}"
echo ""
