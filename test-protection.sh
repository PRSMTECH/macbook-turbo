#!/bin/bash

# Test script to verify IDE/Terminal protection

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Protection Test for CPU Cleanup"
echo "================================"
echo ""

# Source shared protected processes config directly
if [[ -f "$SCRIPT_DIR/config/protected-processes.sh" ]]; then
    source "$SCRIPT_DIR/config/protected-processes.sh"
else
    echo "⚠️  Warning: Could not load protected-processes.sh"
    exit 1
fi

# Test current terminal
echo "Testing current terminal protection..."
CURRENT_PID=$$
CURRENT_PPID=$PPID

echo "Current PID: $CURRENT_PID"
echo "Parent PID: $CURRENT_PPID"
echo ""

# Test various IDE process names
TEST_PROCESSES=(
    "Code"
    "Terminal"
    "python3"
    "node"
    "cursor"
    "IntelliJ IDEA"
)

echo "Testing process name protection:"
for proc in "${TEST_PROCESSES[@]}"; do
    protected=false
    for check in "${NEVER_KILL[@]}"; do
        if echo "$proc" | grep -qi "$check"; then
            protected=true
            break
        fi
    done
    
    if [[ "$protected" == true ]]; then
        echo "  ✅ $proc is PROTECTED"
    else
        echo "  ❌ $proc is NOT protected"
    fi
done

echo ""
echo "Test complete!"
