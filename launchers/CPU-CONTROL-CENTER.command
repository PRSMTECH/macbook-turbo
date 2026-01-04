#!/bin/bash
#
# CPU MONITOR CONTROL CENTER
# DOUBLE-CLICK TO OPEN CONTROL CENTER
#

# Get script directory (launchers/ folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get project root (parent of launchers/)
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

clear

while true; do
    echo "======================================"
    echo "    CPU MONITOR CONTROL CENTER"
    echo "======================================"
    echo ""
    echo "Current Status:"

    # Check if menu bar app is running
    if pgrep -f "cpu-menubar.py" > /dev/null; then
        echo "  Menu Bar Monitor: RUNNING"
    else
        echo "  Menu Bar Monitor: NOT RUNNING"
    fi

    # Check if auto-cleanup is active
    if launchctl list | grep -q "com.user.cpumanager"; then
        echo "  Auto-Cleanup Service: ACTIVE"
    else
        echo "  Auto-Cleanup Service: INACTIVE"
    fi

    # Show current CPU usage
    cpu_usage=$(ps -A -o %cpu | awk '{sum+=$1} END {printf "%.1f", sum}')
    echo "  Current CPU Usage: ${cpu_usage}%"

    echo ""
    echo "======================================"
    echo "Choose an option:"
    echo ""
    echo "  1) Start Menu Bar Monitor"
    echo "  2) Stop Menu Bar Monitor"
    echo "  3) Run CPU Cleanup Now"
    echo "  4) Check Protection Status"
    echo "  5) Show Top CPU Processes"
    echo "  6) Enable Auto-Cleanup Service"
    echo "  7) Disable Auto-Cleanup Service"
    echo "  8) Open Project Folder"
    echo "  9) Refresh Status"
    echo "  0) Exit"
    echo ""
    echo -n "Enter choice [0-9]: "

    read choice

    case $choice in
        1)
            echo ""
            echo "Starting Menu Bar Monitor..."
            # Kill existing if running
            pkill -f "cpu-menubar.py" 2>/dev/null
            # Start in background
            cd "$PROJECT_DIR"
            nohup python3 "$PROJECT_DIR/src/cpu-menubar.py" > /dev/null 2>&1 &
            echo "Menu Bar Monitor started!"
            echo "Look for CPU percentage in your menu bar"
            sleep 2
            ;;

        2)
            echo ""
            echo "Stopping Menu Bar Monitor..."
            pkill -f "cpu-menubar.py"
            echo "Menu Bar Monitor stopped"
            sleep 2
            ;;

        3)
            echo ""
            echo "Running CPU Cleanup..."
            "$PROJECT_DIR/scripts/cpu-cleanup-enhanced.sh"
            echo ""
            echo "Press any key to continue..."
            read -n 1
            ;;

        4)
            echo ""
            "$PROJECT_DIR/scripts/check-protection-status.sh"
            echo ""
            echo "Press any key to continue..."
            read -n 1
            ;;

        5)
            echo ""
            echo "Top CPU Processes:"
            echo "=================="
            ps aux | sort -nrk 3,3 | head -10 | awk '{printf "%-20s %6.1f%%  %s\n", substr($11,1,20), $3, $2}'
            echo ""
            echo "Press any key to continue..."
            read -n 1
            ;;

        6)
            echo ""
            echo "Enabling Auto-Cleanup Service..."
            launchctl load ~/Library/LaunchAgents/com.user.cpumanager.plist 2>/dev/null && \
                echo "Auto-cleanup service enabled" || \
                echo "Service may already be enabled"
            sleep 2
            ;;

        7)
            echo ""
            echo "Disabling Auto-Cleanup Service..."
            launchctl unload ~/Library/LaunchAgents/com.user.cpumanager.plist 2>/dev/null && \
                echo "Auto-cleanup service disabled" || \
                echo "Service may already be disabled"
            sleep 2
            ;;

        8)
            echo ""
            echo "Opening project folder..."
            open "$PROJECT_DIR"
            ;;

        9)
            echo "Refreshing..."
            ;;

        0)
            echo ""
            echo "Goodbye!"
            exit 0
            ;;

        *)
            echo ""
            echo "Invalid choice. Please try again."
            sleep 1
            ;;
    esac

    clear
done
