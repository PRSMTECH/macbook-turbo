#!/bin/bash

# LAUNCH-ENHANCED-MONITOR.command
# Double-click to launch the Enhanced CPU Monitor Menu Bar App v2.0
# Features: Thermal monitoring, Memory pressure, Disk cleanup, Auto-cleanup modes

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Enhanced CPU Monitor v2.0 Launcher   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if already running
if pgrep -f "cpu-menubar-enhanced.py" > /dev/null; then
    echo -e "${YELLOW}Enhanced Monitor is already running!${NC}"
    echo ""
    echo "Options:"
    echo "  1) Restart the monitor"
    echo "  2) Stop the monitor"
    echo "  3) Keep running and exit"
    echo ""
    read -p "Choose an option (1-3): " choice

    case $choice in
        1)
            echo -e "${YELLOW}Stopping existing monitor...${NC}"
            pkill -f "cpu-menubar-enhanced.py" 2>/dev/null
            sleep 1
            ;;
        2)
            echo -e "${YELLOW}Stopping monitor...${NC}"
            pkill -f "cpu-menubar-enhanced.py" 2>/dev/null
            echo -e "${GREEN}Monitor stopped.${NC}"
            sleep 2
            exit 0
            ;;
        3)
            echo -e "${GREEN}Monitor continues running.${NC}"
            sleep 1
            exit 0
            ;;
        *)
            echo "Invalid option. Keeping current instance running."
            exit 0
            ;;
    esac
fi

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

python3 -c "import rumps" 2>/dev/null
if [[ $? -ne 0 ]]; then
    echo -e "${RED}rumps not found. Installing...${NC}"
    pip3 install rumps
fi

python3 -c "import psutil" 2>/dev/null
if [[ $? -ne 0 ]]; then
    echo -e "${RED}psutil not found. Installing...${NC}"
    pip3 install psutil
fi

echo -e "${GREEN}Dependencies OK${NC}"
echo ""

# Launch the enhanced monitor
echo -e "${GREEN}Launching Enhanced CPU Monitor v2.0...${NC}"
echo ""
echo "Features enabled:"
echo "  - CPU monitoring with color indicators"
echo "  - Thermal state detection (Cool/Warm/Hot/Critical)"
echo "  - Memory pressure monitoring (Normal/Warn/Critical)"
echo "  - Disk usage and cleanable space detection"
echo "  - Multi-factor process scoring for safe cleanup"
echo "  - Auto-cleanup modes (Off/Conservative/Balanced/Aggressive)"
echo ""

cd "$SCRIPT_DIR"
nohup python3 "$SCRIPT_DIR/cpu-menubar-enhanced.py" > ~/Library/Logs/cpu-menubar-enhanced.log 2>&1 &

# Verify launch
sleep 2
if pgrep -f "cpu-menubar-enhanced.py" > /dev/null; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Monitor launched successfully!       ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Look for the CPU icon in your menu bar."
    echo "Log file: ~/Library/Logs/cpu-menubar-enhanced.log"
else
    echo -e "${RED}Failed to launch monitor!${NC}"
    echo "Check the log: tail -f ~/Library/Logs/cpu-menubar-enhanced.log"
fi

echo ""
echo "Press any key to close this window..."
read -n 1 -s
