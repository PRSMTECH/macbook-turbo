#!/bin/bash

# CPU Manager Startup Script
# Add this to your login items for automatic startup

echo "Starting CPU Management System..."

# Start the menu bar app
nohup python3 /Users/bigswizz/cpu-monitor/cpu-menubar.py > /Users/bigswizz/Library/Logs/cpu-menubar.log 2>&1 &

# Ensure LaunchAgent is loaded
launchctl load ~/Library/LaunchAgents/com.user.cpumanager.plist 2>/dev/null

# Run initial cleanup
/Users/bigswizz/cpu-monitor/cpu-cleanup-enhanced.sh

echo "CPU Management System Started!"
echo "Menu bar app PID: $!"