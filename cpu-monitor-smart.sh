#!/bin/bash

# Smart CPU Monitor - Only kills processes when CPU is actually high
# Run this continuously or via cron/launchd

CPU_THRESHOLD=70  # Overall CPU usage threshold
PROCESS_THRESHOLD=50  # Individual process CPU threshold

while true; do
    # Get overall CPU usage
    cpu_usage=$(ps aux | awk 'NR>1{s+=$3} END {print s}')

    echo "[$(date)] Current CPU usage: ${cpu_usage}%"

    # Only act if CPU usage is above threshold
    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
        echo "[$(date)] High CPU detected! Running cleanup..."

        # Kill high CPU processes (excluding critical system processes)
        ps aux | awk -v threshold=$PROCESS_THRESHOLD '$3 > threshold {print $2, $3, $11}' | \
        while read pid cpu cmd; do
            # Skip critical processes
            case "$cmd" in
                */kernel_task|*/launchd|*/SystemUIServer|*/Finder|*/Dock)
                    echo "  Skipping critical: $cmd"
                    ;;
                *)
                    echo "  Killing $cmd (PID: $pid, CPU: ${cpu}%)"
                    kill -9 $pid 2>/dev/null
                    ;;
            esac
        done

        # Also run your original cleanup
        /Users/bigswizz/cpu-monitor/cpu-cleanup.sh
    else
        echo "[$(date)] CPU usage normal"
    fi

    # Wait 30 seconds before next check
    sleep 30
done