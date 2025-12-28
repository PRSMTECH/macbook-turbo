#!/bin/bash

# Enhanced monitoring for multi-display setup

while true; do
    clear
    echo "=== Multi-Display Performance Monitor ==="
    echo "Time: $(date '+%H:%M:%S')"
    echo ""

    # Display metrics
    DISPLAYS=$(ioreg -lw0 | grep EDID | wc -l)
    WS_CPU=$(ps aux | grep WindowServer | grep -v grep | awk '{print $3}')
    echo "🖥️ Displays: $DISPLAYS | WindowServer: ${WS_CPU}%"

    # Memory
    MEM=$(memory_pressure | grep "System-wide" | cut -d: -f2 | tr -d ' ')
    echo "💾 Memory Pressure: $MEM"

    # Top processes
    echo ""
    echo "🔥 Top CPU Consumers:"
    ps aux | sort -nrk 3,3 | head -5 | awk '{printf "  %-30s %6.1f%%\n", substr($11,1,30), $3}'

    # Claude/Terminal specific
    echo ""
    echo "💻 Development Processes:"
    ps aux | grep -E "claude|Terminal|Code" | grep -v grep | awk '{printf "  %-30s %6.1f%%\n", substr($11,1,30), $3}'

    sleep 3
done
