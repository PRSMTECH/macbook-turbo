#!/bin/bash

# Test script to verify process protection
# Tests both shell-level (protected-processes.sh) and Python-level (process_scorer.py) protection

echo "====================================="
echo "MacBook Turbo Protection Test Suite"
echo "====================================="
echo ""

# Source shared protected processes config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/config"
source "$CONFIG_DIR/protected-processes.sh" 2>/dev/null

# Test current terminal
echo "Current Session Info:"
echo "  PID: $$"
echo "  Parent PID: $PPID"
echo "  Shell: $SHELL"
echo ""

# ========================================
# Test 1: Shell-level protection (NEVER_KILL)
# ========================================
echo "Test 1: Shell-Level Protection (NEVER_KILL array)"
echo "--------------------------------------------------"

# Critical processes that MUST be protected
TEST_PROTECTED=(
    # System critical
    "kernel_task"
    "launchd"
    "Finder"
    "WindowServer"
    # Terminals
    "Terminal"
    "iTerm"
    "zsh"
    "bash"
    # IDEs
    "Code"
    "Cursor"
    "Xcode"
    # Development tools
    "node"
    "python3"
    "git"
    "claude"
    # User applications (NEW - should be protected)
    "Google Chrome"
    "Brave Browser"
    "Brave"
    "Spotify"
    "Safari"
    "Firefox"
    "Slack"
    "Discord"
    # Remote desktop
    "Splashtop Streamer"
    "Splashtop Business"
    "SRServer"
)

passed=0
failed=0

for proc in "${TEST_PROTECTED[@]}"; do
    protected=false
    for check in "${NEVER_KILL[@]}"; do
        if [[ "$proc" == "$check" ]]; then
            protected=true
            break
        fi
    done

    if [[ "$protected" == true ]]; then
        echo "  ✅ $proc → PROTECTED"
        ((passed++))
    else
        echo "  ❌ $proc → NOT protected (FAIL)"
        ((failed++))
    fi
done

echo ""
echo "Shell-level results: $passed passed, $failed failed"
echo ""

# ========================================
# Test 2: Helper processes (CAN_KILL_IF_HIGH_CPU)
# ========================================
echo "Test 2: Helper Processes (CAN_KILL_IF_HIGH_CPU array)"
echo "------------------------------------------------------"

# These SHOULD be in the killable list
TEST_KILLABLE=(
    "mdworker"
    "mds_stores"
    "Google Chrome Helper"
    "Brave Browser Helper"
    "Safari Web Content"
    "Slack Helper"
    "Spotify Helper"
)

killable_passed=0
killable_failed=0

for proc in "${TEST_KILLABLE[@]}"; do
    found=false
    for check in "${CAN_KILL_IF_HIGH_CPU[@]}"; do
        if [[ "$proc" == "$check" ]]; then
            found=true
            break
        fi
    done

    if [[ "$found" == true ]]; then
        echo "  ✅ $proc → Can be killed (correct)"
        ((killable_passed++))
    else
        echo "  ⚠️  $proc → Not in killable list"
        ((killable_failed++))
    fi
done

echo ""
echo "Killable list results: $killable_passed confirmed, $killable_failed not found"
echo ""

# ========================================
# Test 3: Python process_scorer.py
# ========================================
echo "Test 3: Python Process Scorer Module"
echo "--------------------------------------"

MODULES_DIR="$(dirname "$SCRIPT_DIR")/modules"

if [[ -f "$MODULES_DIR/process_scorer.py" ]]; then
    echo "Running Python protection tests..."
    echo ""

    # Run Python test script
    python3 -c "
import sys
sys.path.insert(0, '$MODULES_DIR')

from process_scorer import ProcessScorer, ProcessCategory

scorer = ProcessScorer()

def is_name_protected(name):
    '''Check if a process name would be protected based on category'''
    # Pass empty cmdline - name matching is sufficient for tests
    category = scorer._categorize_process(name, '')
    # Protected categories
    protected_categories = [
        ProcessCategory.SYSTEM_CRITICAL,
        ProcessCategory.DEVELOPMENT,
        ProcessCategory.TERMINAL,
        ProcessCategory.USER_APPS,
    ]
    return category in protected_categories

def is_name_killable(name):
    '''Check if a process name would be killable based on category'''
    # Pass empty cmdline - name matching is sufficient for tests
    category = scorer._categorize_process(name, '')
    # Killable categories (helper processes)
    killable_categories = [
        ProcessCategory.BROWSER,
        ProcessCategory.MEDIA,
        ProcessCategory.COMMUNICATION,
        ProcessCategory.SYSTEM_SERVICES,
        ProcessCategory.BACKGROUND,
        ProcessCategory.OTHER,
    ]
    return category in killable_categories

# Test cases: (name, expected_protected, expected_category)
test_cases = [
    # User apps - MUST be protected
    ('Google Chrome', True, ProcessCategory.USER_APPS),
    ('Brave Browser', True, ProcessCategory.USER_APPS),
    ('Brave', True, ProcessCategory.USER_APPS),
    ('Spotify', True, ProcessCategory.USER_APPS),
    ('Safari', True, ProcessCategory.USER_APPS),
    ('Firefox', True, ProcessCategory.USER_APPS),
    ('Slack', True, ProcessCategory.USER_APPS),
    ('Discord', True, ProcessCategory.USER_APPS),
    ('Splashtop Streamer', True, ProcessCategory.USER_APPS),
    # System critical - protected
    ('kernel_task', True, ProcessCategory.SYSTEM_CRITICAL),
    ('launchd', True, ProcessCategory.SYSTEM_CRITICAL),
    # Development - protected
    ('Code', True, ProcessCategory.DEVELOPMENT),
    ('Cursor', True, ProcessCategory.DEVELOPMENT),
    ('node', True, ProcessCategory.DEVELOPMENT),
    ('python3', True, ProcessCategory.DEVELOPMENT),
    ('claude', True, ProcessCategory.DEVELOPMENT),
    # Terminal - protected
    ('Terminal', True, ProcessCategory.TERMINAL),
    ('zsh', True, ProcessCategory.TERMINAL),
    # Helper processes - NOT protected (killable)
    ('Google Chrome Helper', False, ProcessCategory.BROWSER),
    ('Chrome Helper', False, ProcessCategory.BROWSER),
    ('Brave Browser Helper', False, ProcessCategory.BROWSER),
    ('Safari Web Content', False, ProcessCategory.BROWSER),
    ('Spotify Helper', False, ProcessCategory.MEDIA),
    ('Slack Helper', False, ProcessCategory.COMMUNICATION),
]

passed = 0
failed = 0

for name, expected_protected, expected_category in test_cases:
    is_protected = is_name_protected(name)
    category = scorer._categorize_process(name, '')

    # Check protection status
    if is_protected == expected_protected:
        status = '✅'
        passed += 1
    else:
        status = '❌'
        failed += 1

    # Show result
    protected_str = 'PROTECTED' if is_protected else 'KILLABLE'
    print(f'  {status} {name[:25]:<25} → {protected_str:<10} ({category.value})')

print()
print(f'Python tests: {passed} passed, {failed} failed')

# Summary
if failed == 0:
    print()
    print('🎉 All protection tests passed!')
    sys.exit(0)
else:
    print()
    print('⚠️  Some tests failed - check protection configuration')
    sys.exit(1)
"
    PYTHON_EXIT=$?
else
    echo "  ⚠️  process_scorer.py not found at $MODULES_DIR"
    PYTHON_EXIT=1
fi

echo ""
echo "====================================="
echo "Test Summary"
echo "====================================="
echo "Shell-level protection: $passed passed, $failed failed"
echo "Python protection: $([ $PYTHON_EXIT -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
echo ""

# Final status
if [[ $failed -eq 0 ]] && [[ $PYTHON_EXIT -eq 0 ]]; then
    echo "✅ All tests passed - protection system working correctly!"
    exit 0
else
    echo "❌ Some tests failed - review protection configuration"
    exit 1
fi
