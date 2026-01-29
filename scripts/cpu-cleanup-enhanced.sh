#!/bin/bash

# Enhanced CPU Cleanup Script with PROPER Protection
# FIXED: Will NOT kill IDE or Terminal sessions

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source shared protected processes config
if [[ -f "$SCRIPT_DIR/config/protected-processes.sh" ]]; then
    source "$SCRIPT_DIR/config/protected-processes.sh"
else
    echo "⚠️  Warning: Could not load protected-processes.sh, using fallback list"
    NEVER_KILL=("kernel_task" "launchd" "Finder" "Dock" "Terminal" "iTerm" "zsh" "bash" "Code" "Cursor" "node" "python" "git" "ssh" "tmux")
fi

echo "🔧 Enhanced CPU Cleanup - $(date)"
echo "=============================="

# Define thresholds
HIGH_CPU_THRESHOLD=40
CRITICAL_CPU_THRESHOLD=60

# Get current terminal PID and all parent PIDs to protect
CURRENT_PPID=$PPID
CURRENT_PID=$$
TERM_PIDS=$(pgrep -P $PPID 2>/dev/null)

# Processes that can be killed ONLY if using excessive CPU
KILLABLE_HIGH_CPU=(
    "Chrome Helper"
    "Safari Web Content"
    "Firefox"
    "Spotify Helper"
    "Discord Helper"
    "Slack Helper"
    "Teams"
    "WhatsApp"
    "Telegram"
    "Signal"
    "Dropbox"
    "Google Drive"
    "OneDrive"
    "Creative Cloud"
)

# Function to check if process should be protected
is_protected() {
    local cmd=$1
    local pid=$2
    
    # Always protect current shell and parents
    if [[ "$pid" == "$CURRENT_PID" ]] || [[ "$pid" == "$CURRENT_PPID" ]]; then
        echo "  ⚠️  Protected (current shell): PID $pid"
        return 0
    fi
    
    # Check if it's a parent of current process
    local parent_check=$(pstree -p $$ 2>/dev/null | grep -o "([0-9]*)" | tr -d "()")
    for parent_pid in $parent_check; do
        if [[ "$pid" == "$parent_pid" ]]; then
            echo "  ⚠️  Protected (parent process): PID $pid"
            return 0
        fi
    done
    
    # Check against NEVER_KILL list (improved matching)
    for protected in "${NEVER_KILL[@]}"; do
        # Case-insensitive partial match
        if echo "$cmd" | grep -qi "$protected"; then
            echo "  ⚠️  Protected ($protected): $cmd"
            return 0
        fi
    done
    
    # Check if process has any child processes (likely active work)
    local children=$(pgrep -P $pid 2>/dev/null | wc -l)
    if [[ $children -gt 0 ]]; then
        echo "  ⚠️  Protected (has $children child processes): $cmd"
        return 0
    fi
    
    # Check if process owns any open files in home directory (active work)
    if lsof -p $pid 2>/dev/null | grep -q "$HOME"; then
        echo "  ⚠️  Protected (has open files in home): $cmd"
        return 0
    fi
    
    return 1
}

# Function to safely kill a process
safe_kill() {
    local pid=$1
    local name=$2
    local cpu=$3
    
    echo "  🎯 Attempting to kill: $name (PID: $pid, CPU: ${cpu}%)"
    
    # Try graceful termination first
    kill -TERM $pid 2>/dev/null
    sleep 1
    
    # Check if still running
    if kill -0 $pid 2>/dev/null; then
        echo "     Force killing..."
        kill -9 $pid 2>/dev/null
    fi
}

# Main cleanup process
echo ""
echo "Step 1: Analyzing processes..."
echo "Current thresholds: HIGH=${HIGH_CPU_THRESHOLD}%, CRITICAL=${CRITICAL_CPU_THRESHOLD}%"
echo ""

# Get list of high CPU processes
HIGH_CPU_PROCS=$(ps aux | awk -v threshold=$HIGH_CPU_THRESHOLD 'NR>1 && $3 > threshold {print $2 "|" $3 "|" $11}')

if [[ -z "$HIGH_CPU_PROCS" ]]; then
    echo "✅ No high CPU processes found!"
else
    echo "Found high CPU processes:"
    echo "$HIGH_CPU_PROCS" | while IFS='|' read pid cpu cmd; do
        # Clean up the command name
        cmd_clean=$(echo "$cmd" | sed 's/^.*\///')
        
        # Check if protected
        if is_protected "$cmd" "$pid"; then
            continue
        fi
        
        # Check if it's a killable process
        killable=false
        for proc in "${KILLABLE_HIGH_CPU[@]}"; do
            if echo "$cmd" | grep -q "$proc"; then
                killable=true
                break
            fi
        done
        
        # Decision logic
        if [[ "$killable" == true ]] && (( $(echo "$cpu > $HIGH_CPU_THRESHOLD" | bc -l) )); then
            safe_kill "$pid" "$cmd_clean" "$cpu"
        elif (( $(echo "$cpu > $CRITICAL_CPU_THRESHOLD" | bc -l) )); then
            echo "  ⚠️  Critical CPU but unknown process: $cmd_clean (${cpu}%)"
            echo "     Skipping for safety..."
        else
            echo "  👀 Monitoring: $cmd_clean (${cpu}%)"
        fi
    done
fi

# Kill specific known problematic processes that are always safe to kill
echo ""
echo "Step 2: Cleaning known resource hogs..."
ALWAYS_KILL_SAFE=(
    "mds_stores"
    "photoanalysisd"
    "photolibraryd"
    "suggestd"
    "com.apple.photos"
    "cloudd"
    "bird"
    "commerce"
    "trustd"
)

for proc in "${ALWAYS_KILL_SAFE[@]}"; do
    if pgrep -x "$proc" > /dev/null; then
        pkill -9 "$proc" 2>/dev/null && echo "  ✅ Killed: $proc"
    fi
done

# Clear caches (safe operations)
echo ""
echo "Step 3: Optimizing system..."
dscacheutil -flushcache 2>/dev/null && echo "  ✅ DNS cache cleared"

# Report status
echo ""
echo "=============================="
echo "✅ Cleanup Complete!"
echo ""
echo "Top 5 CPU users now:"
ps aux | sort -nrk 3,3 | head -6 | tail -5 | awk '{printf "  %-30s %6.1f%%\n", substr($11,1,30), $3}'

# Log the action
echo "[$(date)] Cleanup completed" >> ~/Library/Logs/cpu-cleanup.log
