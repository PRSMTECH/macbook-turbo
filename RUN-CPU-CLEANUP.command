#!/bin/bash
#
# DOUBLE-CLICK THIS FILE TO RUN CPU CLEANUP
# Or run from Terminal: /Users/bigswizz/cpu-monitor/RUN-CPU-CLEANUP.command
#

clear
echo "======================================"
echo "        CPU Cleanup Tool"
echo "======================================"
echo ""
echo "This will clean up high-CPU processes"
echo "while protecting your development tools"
echo ""
echo "Protected:"
echo "  • IDEs (VS Code, Cursor, Xcode, etc.)"
echo "  • Terminal sessions"
echo "  • Development tools (node, python, docker)"
echo ""

# Run the cleanup
/Users/bigswizz/cpu-monitor/cpu-cleanup-enhanced.sh

echo ""
echo "======================================"
echo "Press any key to close this window..."
read -n 1