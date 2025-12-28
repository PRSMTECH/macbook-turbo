#!/bin/bash

echo "Uninstalling CPU Monitor System..."

# Stop and unload LaunchAgents
launchctl unload ~/Library/LaunchAgents/com.user.cpumanager.plist 2>/dev/null
launchctl unload ~/Library/LaunchAgents/com.user.cpumanager.startup.plist 2>/dev/null
launchctl unload ~/Library/LaunchAgents/com.user.cpucleanup.plist 2>/dev/null

# Kill menu bar app
pkill -f "cpu-menubar.py"

# Remove LaunchAgent files
rm -f ~/Library/LaunchAgents/com.user.cpumanager*.plist
rm -f ~/Library/LaunchAgents/com.user.cpucleanup.plist

# Remove install directory
rm -rf /Users/bigswizz/cpu-monitor

echo "CPU Monitor System uninstalled successfully!"
echo "Log files are preserved in ~/Library/Logs/"
