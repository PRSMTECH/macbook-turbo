#!/bin/bash
#
# DOUBLE-CLICK THIS FILE TO CHECK PROTECTION STATUS
#

# Get script directory (launchers/ folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get project root (parent of launchers/)
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

clear

# Run the status check
"$PROJECT_DIR/scripts/check-protection-status.sh"

echo ""
echo "Press any key to close this window..."
read -n 1
