#!/usr/bin/env bash
set -euo pipefail

# Color definitions
BOLD=$(tput bold 2>/dev/null || echo "")
GREEN=$(tput setaf 2 2>/dev/null || echo "")
YELLOW=$(tput setaf 3 2>/dev/null || echo "")
RED=$(tput setaf 1 2>/dev/null || echo "")
NC=$(tput sgr0 2>/dev/null || echo "")

echo ""
echo "${BOLD}react-seo-geo-planner — Python Package Uninstaller${NC}"
echo "======================================================"
echo ""

echo "The following Python packages will be removed:"
echo "  beautifulsoup4  requests  lxml  playwright"
echo "  Pillow          urllib3   validators  reportlab"
echo ""
echo "${YELLOW}Note: These packages may be used by other tools. Removing them is system-wide.${NC}"
echo ""

# Confirmation prompt
read -r -p "Uninstall these Python packages? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted. No packages removed."
    exit 0
fi

# Uninstall packages
echo ""
echo "${BOLD}Removing packages...${NC}"
pip3 uninstall -y beautifulsoup4 requests lxml playwright Pillow urllib3 validators reportlab
echo "${GREEN}✓ Python packages removed${NC}"

# Optional Playwright browser removal
echo ""
read -r -p "Also remove Playwright Chromium browser? [y/N]: " remove_pw
if [[ "$remove_pw" =~ ^[Yy]$ ]]; then
    playwright uninstall chromium 2>/dev/null || echo "${YELLOW}Playwright Chromium not found or already removed.${NC}"
    echo "${GREEN}✓ Playwright Chromium removed${NC}"
fi

echo ""
echo "${GREEN}${BOLD}Done.${NC} Python packages have been removed."
echo "The skill files remain in place. To reinstall, run: ./install.sh"
echo ""
