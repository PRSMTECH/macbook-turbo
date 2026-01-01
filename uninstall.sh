#!/bin/bash

#######################################
# MacBook Turbo - Uninstall Script
#######################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/macbook-turbo"
PLIST_FILE="$HOME/Library/LaunchAgents/com.prsmtech.macbookturbo.plist"
OLD_PLIST_FILE="$HOME/Library/LaunchAgents/com.user.cpumanager.plist"

echo ""
echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║           MacBook Turbo Uninstaller                       ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Confirm uninstall
read -p "Are you sure you want to uninstall MacBook Turbo? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Uninstall cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🧹 Uninstalling MacBook Turbo...${NC}"

# Stop LaunchAgents if running (both old and new)
echo -e "   ${BLUE}Stopping auto-start services...${NC}"
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl unload "$OLD_PLIST_FILE" 2>/dev/null || true
launchctl unload "$HOME/Library/LaunchAgents/com.user.cpumanager.startup.plist" 2>/dev/null || true
launchctl unload "$HOME/Library/LaunchAgents/com.user.cpucleanup.plist" 2>/dev/null || true
rm -f "$PLIST_FILE" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.user.cpumanager*.plist" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.user.cpucleanup.plist" 2>/dev/null || true
echo -e "   ${GREEN}✓${NC} LaunchAgents removed"

# Kill any running instances
echo -e "   ${BLUE}Stopping running processes...${NC}"
pkill -f "cpu-menubar" 2>/dev/null || true
pkill -f "system-optimizer" 2>/dev/null || true
echo -e "   ${GREEN}✓${NC} Processes stopped"

# Remove installation directory
if [[ -d "$INSTALL_DIR" ]]; then
    echo -e "   ${BLUE}Removing installation directory...${NC}"
    rm -rf "$INSTALL_DIR"
    echo -e "   ${GREEN}✓${NC} Installation directory removed"
else
    echo -e "   ${YELLOW}⚠️  Installation directory not found at $INSTALL_DIR${NC}"
fi

# Remove log files
echo -e "   ${BLUE}Removing log files...${NC}"
rm -f "$HOME/Library/Logs/macbook-turbo.log" 2>/dev/null || true
rm -f "$HOME/Library/Logs/macbook-turbo.err" 2>/dev/null || true
rm -f "$HOME/Library/Logs/cpu-cleanup.log" 2>/dev/null || true
echo -e "   ${GREEN}✓${NC} Log files removed"

# Note about PATH
echo ""
echo -e "${YELLOW}📝 Note:${NC}"
echo -e "   If you added MacBook Turbo to your PATH, you may want to remove"
echo -e "   the following line from your ~/.zshrc or ~/.bashrc:"
echo -e "   ${BLUE}export PATH=\"\$HOME/macbook-turbo:\$PATH\"${NC}"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ Uninstall Complete!                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Thank you for trying MacBook Turbo!${NC}"
echo -e "${YELLOW}Feedback welcome at: https://github.com/PRSMTECH/macbook-turbo/issues${NC}"
echo ""
