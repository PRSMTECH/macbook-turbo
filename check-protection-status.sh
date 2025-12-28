#!/bin/bash

# CPU Monitor Protection Checker
# Shows which processes are currently protected from cleanup

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CPU Cleanup Protection Status Monitor${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get current shell info
echo -e "${CYAN}Current Session Info:${NC}"
echo "  Shell PID: $$"
echo "  Parent PID: $PPID"
echo "  Terminal: $TERM_PROGRAM"
echo "  User: $USER"
echo ""

# Show currently running protected processes
echo -e "${CYAN}Currently Running Protected Processes:${NC}"
echo ""

# Define the protected processes list (same as in the cleanup script)
PROTECTED_PROCESSES=(
    "Terminal"
    "iTerm"
    "Code"
    "Cursor"
    "IntelliJ"
    "WebStorm"
    "PyCharm"
    "Xcode"
    "Android Studio"
    "Sublime Text"
    "vim"
    "nvim"
    "emacs"
    "node"
    "python"
    "ruby"
    "java"
    "docker"
    "ssh"
    "tmux"
    "screen"
)

# Check which protected processes are currently running
found_count=0
for proc in "${PROTECTED_PROCESSES[@]}"; do
    # Check if process is running
    if pgrep -i "$proc" > /dev/null 2>&1; then
        pids=$(pgrep -i "$proc" | tr '\n' ' ')
        cpu_usage=$(ps aux | grep -i "$proc" | grep -v grep | awk '{sum+=$3} END {printf "%.1f", sum}')
        echo -e "  ${GREEN}✅ $proc${NC}"
        echo "     PIDs: $pids"
        echo "     Total CPU: ${cpu_usage}%"
        echo ""
        ((found_count++))
    fi
done

if [[ $found_count -eq 0 ]]; then
    echo -e "  ${YELLOW}No protected processes currently running${NC}"
fi

# Show high CPU processes that would be targeted
echo ""
echo -e "${CYAN}High CPU Processes (>40%):${NC}"
echo ""

high_cpu_found=false
ps aux | awk '$3 > 40 {print $2, $3, $11}' | while read pid cpu cmd; do
    if [[ -n "$pid" ]]; then
        high_cpu_found=true
        cmd_clean=$(basename "$cmd")
        
        # Check if it would be protected
        protected=false
        for proc in "${PROTECTED_PROCESSES[@]}"; do
            if echo "$cmd" | grep -qi "$proc"; then
                protected=true
                break
            fi
        done
        
        if [[ "$protected" == true ]]; then
            echo -e "  ${GREEN}PROTECTED:${NC} $cmd_clean (PID: $pid, CPU: ${cpu}%)"
        else
            echo -e "  ${RED}WOULD BE KILLED:${NC} $cmd_clean (PID: $pid, CPU: ${cpu}%)"
        fi
    fi
done

# If no high CPU processes
if ! ps aux | awk '$3 > 40' | grep -v "COMMAND" | head -1 > /dev/null; then
    echo -e "  ${GREEN}No high CPU processes detected${NC}"
fi

# Show cleanup schedule
echo ""
echo -e "${CYAN}Cleanup Schedule:${NC}"
if launchctl list | grep -q "com.user.cpumanager"; then
    echo -e "  ${GREEN}✅ CPU Manager is active${NC}"
    echo "  Next cleanup: Within 3 minutes"
    
    # Check last cleanup time from log
    if [[ -f "$HOME/Library/Logs/cpu-cleanup.log" ]]; then
        last_cleanup=$(tail -1 "$HOME/Library/Logs/cpu-cleanup.log" 2>/dev/null | cut -d']' -f1 | sed 's/\[//')
        if [[ -n "$last_cleanup" ]]; then
            echo "  Last cleanup: $last_cleanup"
        fi
    fi
else
    echo -e "  ${RED}❌ CPU Manager is not active${NC}"
fi

# Recommendations
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${CYAN}Protection Recommendations:${NC}"
echo ""

# Check if any dev tools are running without protection
unprotected_dev_tools=false
for tool in "WebStorm" "PhpStorm" "CLion" "DataGrip" "Fleet"; do
    if pgrep -i "$tool" > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠️  Found $tool running - consider adding to protection list${NC}"
        unprotected_dev_tools=true
    fi
done

if [[ "$unprotected_dev_tools" == false ]]; then
    echo -e "  ${GREEN}✅ All detected development tools are protected${NC}"
fi

# Final status
echo ""
echo -e "${BLUE}========================================${NC}"
if [[ $found_count -gt 0 ]]; then
    echo -e "${GREEN}Status: $found_count protected processes are running${NC}"
else
    echo -e "${YELLOW}Status: No protected processes detected${NC}"
fi
echo -e "${BLUE}========================================${NC}"
