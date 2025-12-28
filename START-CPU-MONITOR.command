#!/bin/bash
#
# DOUBLE-CLICK THIS FILE TO START CPU MONITOR
# Or run from Terminal: /Users/bigswizz/cpu-monitor/START-CPU-MONITOR.command
#

clear
echo "======================================"
echo "       CPU Monitor Launcher"
echo "======================================"
echo ""

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew install python3
fi

# Check if pip packages are installed
echo "📦 Checking required packages..."
python3 -m pip install --quiet --upgrade rumps psutil 2>/dev/null || {
    echo "Installing packages..."
    python3 -m pip install --user rumps psutil
}

echo "✅ All requirements satisfied"
echo ""
echo "🚀 Starting CPU Monitor Menu Bar App..."
echo ""
echo "Look for the CPU percentage in your menu bar (top-right)"
echo ""
echo "Features:"
echo "  • 🟢 Green = Low CPU (<50%)"
echo "  • 🟡 Yellow = Medium CPU (50-80%)"
echo "  • 🔴 Red = High CPU (>80%)"
echo ""
echo "Click the percentage to access:"
echo "  • Run cleanup manually"
echo "  • Check protection status"
echo "  • View top processes"
echo "  • Enable auto-cleanup"
echo ""
echo "Press Ctrl+C to stop the monitor"
echo "======================================"

# Start the menu bar app
cd /Users/bigswizz/cpu-monitor
python3 cpu-menubar.py