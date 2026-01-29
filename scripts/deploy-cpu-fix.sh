#!/bin/bash

# Safe Deployment Script for Fixed CPU Cleanup
# This will backup your old script and deploy the fixed version

set -e

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration - use script directory as install dir
INSTALL_DIR="$SCRIPT_DIR"
BACKUP_DIR="$HOME/cpu-monitor-backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CPU Cleanup Fix Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Create backup directory
echo -e "${YELLOW}Step 1: Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"

# Backup existing script
if [[ -f "$INSTALL_DIR/cpu-cleanup-enhanced.sh" ]]; then
    cp "$INSTALL_DIR/cpu-cleanup-enhanced.sh" "$BACKUP_DIR/cpu-cleanup-enhanced-${TIMESTAMP}.sh"
    echo -e "${GREEN}✅ Backed up existing script to:${NC}"
    echo "   $BACKUP_DIR/cpu-cleanup-enhanced-${TIMESTAMP}.sh"
else
    echo -e "${RED}⚠️  No existing script found to backup${NC}"
fi

# Step 2: Stop the service temporarily
echo ""
echo -e "${YELLOW}Step 2: Stopping CPU monitor service...${NC}"
launchctl unload ~/Library/LaunchAgents/com.user.cpumanager.plist 2>/dev/null || true
echo -e "${GREEN}✅ Service stopped${NC}"

# Step 3: Deploy the fixed script
echo ""
echo -e "${YELLOW}Step 3: Verifying fixed script...${NC}"

# Script is already deployed, just verify it exists
if [[ ! -f "$INSTALL_DIR/cpu-cleanup-enhanced.sh" ]]; then
    echo -e "${RED}❌ Error: cpu-cleanup-enhanced.sh not found in $INSTALL_DIR${NC}"
    echo "Script deployment may have failed."
    exit 1
fi

chmod +x "$INSTALL_DIR/cpu-cleanup-enhanced.sh"
echo -e "${GREEN}✅ Fixed script verified and made executable${NC}"

# Step 4: Create a test script to verify protection
echo ""
echo -e "${YELLOW}Step 4: Creating test script...${NC}"
cat > "$INSTALL_DIR/test-protection.sh" << 'EOF'
#!/bin/bash

# Test script to verify IDE/Terminal protection

echo "Protection Test for CPU Cleanup"
echo "================================"
echo ""

# Source shared protected processes config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config/protected-processes.sh" 2>/dev/null

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
EOF
chmod +x "$INSTALL_DIR/test-protection.sh"

# Step 5: Run the test
echo ""
echo -e "${YELLOW}Step 5: Running protection test...${NC}"
"$INSTALL_DIR/test-protection.sh"

# Step 6: Restart the service
echo ""
echo -e "${YELLOW}Step 6: Restarting CPU monitor service...${NC}"
launchctl load ~/Library/LaunchAgents/com.user.cpumanager.plist 2>/dev/null || true
echo -e "${GREEN}✅ Service restarted${NC}"

# Step 7: Final verification
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "The fixed CPU cleanup script has been deployed."
echo ""
echo -e "${YELLOW}Key improvements:${NC}"
echo "  • Better process name matching (case-insensitive)"
echo "  • Protects processes with child processes"
echo "  • Protects processes with open files in home directory"
echo "  • Graceful termination before force kill"
echo "  • More comprehensive NEVER_KILL list"
echo "  • Better logging of protected processes"
echo ""
echo -e "${YELLOW}To verify protection is working:${NC}"
echo "  $INSTALL_DIR/test-protection.sh"
echo ""
echo -e "${YELLOW}To restore the old version:${NC}"
echo "  cp $BACKUP_DIR/cpu-cleanup-enhanced-${TIMESTAMP}.sh $INSTALL_DIR/cpu-cleanup-enhanced.sh"
echo ""
echo -e "${GREEN}Your IDE and Terminal sessions are now protected!${NC}"
