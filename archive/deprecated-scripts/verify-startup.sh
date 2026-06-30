#!/bin/bash

# Verify all startup components are configured
INSTALL_DIR="/Users/bigswizz/cpu-monitor"

echo "CPU Monitor Startup Configuration Status:"
echo "========================================="

# Check LaunchAgents
echo ""
echo "LaunchAgents:"
for agent in com.user.cpumanager com.user.cpumanager.startup com.user.cpumonitor.master; do
    if launchctl list | grep -q "$agent"; then
        echo "  ✅ $agent is loaded"
    else
        echo "  ❌ $agent is not loaded"
    fi
done

# Check if set to run at boot
echo ""
echo "Boot Configuration:"
for plist in ~/Library/LaunchAgents/com.user.cpu*.plist; do
    if [[ -f "$plist" ]]; then
        if grep -q "<key>RunAtLoad</key>" "$plist" && grep -A1 "<key>RunAtLoad</key>" "$plist" | grep -q "<true/>"; then
            echo "  ✅ $(basename $plist) will run at boot"
        else
            echo "  ❌ $(basename $plist) will NOT run at boot"
        fi
    fi
done

# Check current status
echo ""
echo "Current Status:"
if pgrep -f "cpu-menubar.py" > /dev/null; then
    echo "  ✅ Menu bar app is running"
else
    echo "  ❌ Menu bar app is not running"
fi

echo ""
echo "To manually start all components:"
echo "  $INSTALL_DIR/cpu-manager-startup.sh"
