# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MacBook Turbo is a macOS system optimizer with real-time CPU monitoring via a menu bar app, intelligent process cleanup, and disk cache cleaning. It uses a multi-factor scoring algorithm to safely identify killable processes while protecting developer tools.

**Requirements:** macOS (Sonoma/Ventura/Monterey), Python 3.9+

## Common Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run menu bar app
python src/cpu-menubar-enhanced.py

# CLI tool
python src/system-optimizer.py status          # System dashboard
python src/system-optimizer.py cleanup         # Run cleanup
python src/system-optimizer.py cleanup --dry-run   # Preview cleanup
python src/system-optimizer.py cleanup --aggressive
python src/system-optimizer.py monitor         # Continuous monitoring
python src/system-optimizer.py analyze         # Full analysis

# Run individual modules
python modules/process_scorer.py    # Test process scoring
python modules/thermal_monitor.py   # Check temperatures
python modules/memory_monitor.py    # Check memory pressure
python modules/disk_cleaner.py      # Scan cleanable files

# Linting (CI uses these)
pip install flake8 bandit
flake8 . --select=E9,F63,F7,F82 --show-source  # Critical errors only
bandit -r modules/ src/ -ll --skip B404,B603,B602

# Verify all modules import correctly
python -c "from modules import thermal_monitor, memory_monitor, disk_cleaner, process_scorer"
```

## Architecture

### Entry Points
- `src/cpu-menubar-enhanced.py` - Menu bar app using `rumps` library. Creates `EnhancedCPUMonitorApp` that orchestrates all monitoring
- `src/system-optimizer.py` - CLI tool with argparse. Wraps `SystemOptimizer` class for command-line access

### Module System (`modules/`)

All modules are independent and can run standalone for testing:

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `process_scorer.py` | Multi-factor scoring algorithm for process safety | `ProcessScorer`, `ProcessInfo`, `ProcessCategory` |
| `thermal_monitor.py` | CPU/GPU temperature via macOS APIs | `ThermalMonitor`, `ThermalState`, `ThrottleState` |
| `memory_monitor.py` | Memory pressure detection (macOS-specific) | `MemoryMonitor`, `MemoryPressure`, `SwapState` |
| `disk_cleaner.py` | Cache scanning and cleanup | `DiskCleaner`, `CleanupCategory` |

### Process Scoring Algorithm

The core intelligence is in `ProcessScorer` (`modules/process_scorer.py`):

```
Score = (CPU × 0.4) + (Memory × 0.3) + (FDs × 0.1) + (Age × 0.1) + (Category × 0.1)
```

Protected processes get score `-1000`. Categories like `SYSTEM_CRITICAL`, `DEVELOPMENT`, and `TERMINAL` are never killed.

### Protected Processes Configuration

Two parallel systems maintain protection lists:
1. **Python:** `ProcessScorer.PROTECTED_PATTERNS` in `modules/process_scorer.py` - regex patterns by category
2. **Shell:** `config/protected-processes.sh` - bash arrays sourced by cleanup scripts

When adding protected apps, update both locations.

### Auto-Cleanup Modes

The menu bar app supports four modes in `AutoCleanMode`:
- `OFF` - Manual only
- `CONSERVATIVE` - CPU >90% or Memory >95%
- `BALANCED` - CPU >70% or Memory >85%
- `AGGRESSIVE` - CPU >50% or Memory >70%

### Directory Structure

```
src/                  # Main applications
modules/              # Independent Python modules
scripts/              # Shell scripts for cleanup operations
config/               # Protected process lists
launchers/            # Double-click .command files for Finder
bin/                  # Quick CLI shortcuts
```

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR to main:
- Tests Python 3.9-3.12 on macOS
- Lints with flake8 (critical errors fail build)
- Security scan with bandit
- Checks for hardcoded paths
- Auto-creates releases on version tags

## Key Implementation Details

- Menu bar uses `rumps.Timer` with 2-second CPU updates and 10-second thermal updates
- Process killing uses SIGTERM → wait → SIGKILL pattern (see `ProcessScorer.kill_process_gracefully`)
- All cleanup operations support `dry_run=True` for preview
- Thermal monitoring detects Apple Silicon vs Intel and adapts sensor access accordingly
