#!/bin/bash
#
# DOUBLE-CLICK THIS FILE TO RUN CPU CLEANUP
#

# Get script directory (launchers/ folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get project root (parent of launchers/)
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

clear
echo "======================================"
echo "        CPU Cleanup Tool"
echo "======================================"
echo ""
echo "This will clean up high-CPU processes"
echo "while protecting your development tools"
echo ""
echo "Protected:"
echo "  IDEs (VS Code, Cursor, Xcode, etc.)"
echo "  Terminal sessions"
echo "  Development tools (node, python, docker)"
echo ""

# Run the cleanup
"$PROJECT_DIR/scripts/cpu-cleanup-enhanced.sh"

echo ""
echo "======================================"
echo "Press any key to close this window..."
read -n 1
