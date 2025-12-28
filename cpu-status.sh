#!/bin/bash

# CPU Management System Status Check

echo "================================"
echo "CPU Management System Status"
echo "================================"
echo ""

# Check if LaunchAgent is running
echo "🎯 LaunchAgent Status:"
if launchctl list | grep -q cpumanager; then
    echo "  ✅ CPU Manager daemon is RUNNING"
    echo "     (Runs cleanup every 3 minutes)"
else
    echo "  ❌ CPU Manager daemon is NOT running"
fi
echo ""

# Check if menu bar app is running
echo "📊 Menu Bar Monitor:"
if pgrep -f "cpu-menubar.py" > /dev/null; then
    echo "  ✅ Menu bar app is RUNNING"
    pid=$(pgrep -f "cpu-menubar.py")
    echo "     PID: $pid"
else
    echo "  ❌ Menu bar app is NOT running"
fi
echo ""

# Show current CPU usage
echo "💻 Current System Status:"
cpu_usage=$(ps aux | awk 'NR>1{s+=$3} END {print s}')
echo "  Total CPU Usage: ${cpu_usage}%"
echo ""

# Show top 5 CPU users
echo "🔥 Top 5 CPU Users:"
ps aux | head -1
ps aux | sort -nrk 3,3 | head -5 | awk '{printf "  %-10s %5s %5.1f%% %s\n", $1, $2, $3, $11}'
echo ""

# Show recent cleanup logs
echo "📝 Recent Cleanup Activity:"
if [[ -f /Users/bigswizz/Library/Logs/cpu-cleanup.log ]]; then
    tail -5 /Users/bigswizz/Library/Logs/cpu-cleanup.log | sed 's/^/  /'
else
    echo "  No logs available yet"
fi
echo ""

echo "================================"
echo "Management Commands:"
echo "  Stop daemon:  launchctl unload ~/Library/LaunchAgents/com.user.cpumanager.plist"
echo "  Start daemon: launchctl load ~/Library/LaunchAgents/com.user.cpumanager.plist"
echo "  Manual cleanup: /Users/bigswizz/cpu-monitor/cpu-cleanup-enhanced.sh"
echo "  Check status: /Users/bigswizz/cpu-monitor/cpu-status.sh"
echo "================================"