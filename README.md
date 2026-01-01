# MacBook Turbo

<div align="center">

![macOS](https://img.shields.io/badge/macOS-Sonoma%20%7C%20Ventura%20%7C%20Monterey-blue?style=for-the-badge&logo=apple&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/PRSMTECH/macbook-turbo/ci.yml?style=for-the-badge&label=CI)

**Intelligent macOS System Optimizer & CPU Monitor**

*Keep your Mac running at peak performance with real-time monitoring and smart cleanup*

[Quick Start](#-quick-start) | [Features](#-features) | [Installation](#-installation) | [Usage](#-usage) | [Configuration](#%EF%B8%8F-configuration)

</div>

---

## Quick Start

**One-line install (recommended):**

```bash
curl -fsSL https://raw.githubusercontent.com/PRSMTECH/macbook-turbo/main/install.sh | bash
```

**Or manual install:**

```bash
git clone https://github.com/PRSMTECH/macbook-turbo.git ~/macbook-turbo
cd ~/macbook-turbo
pip3 install -r requirements.txt
python3 cpu-menubar-enhanced.py
```

After installation, look for the **CPU indicator** (🟢/🟡/🔴 with percentage) in your menu bar!

---

## Overview

MacBook Turbo is a comprehensive performance monitoring and optimization toolkit for macOS. It provides real-time CPU, memory, and thermal monitoring through an elegant menu bar app, combined with intelligent process management that protects your development workflow.

### Why MacBook Turbo?

- **Developer-Friendly**: Never kills your IDE, terminal, or dev tools
- **Smart Cleanup**: Multi-factor scoring algorithm prioritizes what to clean
- **Low Overhead**: Minimal resource usage while monitoring
- **Modular Design**: Use only what you need

---

## Features

### Menu Bar Monitor

Real-time system status with color-coded indicators:

| CPU Load | Color | Status |
|----------|-------|--------|
| < 50% | Green | Normal |
| 50-80% | Yellow | Moderate |
| > 80% | Red | High |

### Intelligent Process Management

- **Protected Categories**: IDEs, terminals, shells, and dev tools are whitelisted
- **Multi-Factor Scoring**: CPU (40%) + Memory (30%) + File Descriptors (10%) + Age (10%) + Category (10%)
- **Graceful Termination**: SIGTERM first, SIGKILL only if necessary

### Modular Monitors

| Module | Purpose |
|--------|---------|
| `thermal_monitor` | CPU/GPU temperature, throttle detection |
| `memory_monitor` | macOS-native memory pressure detection |
| `disk_cleaner` | Smart cache cleanup (30+ locations) |
| `process_scorer` | Intelligent process prioritization |

### Auto-Cleanup Modes

| Mode | CPU Threshold | Memory Threshold |
|------|---------------|------------------|
| OFF | Manual only | Manual only |
| CONSERVATIVE | > 90% | > 95% |
| BALANCED | > 70% | > 85% |
| AGGRESSIVE | > 50% | > 70% |

---

## Installation

### Prerequisites

Before installing, make sure you have:

- macOS 12.x (Monterey) or later
- Python 3.9 or higher (`python3 --version` to check)
- ~50 MB disk space

**Don't have Python?** Install via [Homebrew](https://brew.sh/):
```bash
brew install python@3.11
```

### One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/PRSMTECH/macbook-turbo/main/install.sh | bash
```

The installer will:
- Check prerequisites
- Clone the repository to `~/macbook-turbo`
- Create a virtual environment
- Install dependencies
- Set up launcher scripts
- Optionally configure auto-start

### Manual Install

```bash
# Clone the repository
git clone https://github.com/PRSMTECH/macbook-turbo.git ~/macbook-turbo
cd ~/macbook-turbo

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the menu bar app
python cpu-menubar-enhanced.py
```

### Uninstall

```bash
# Run the uninstall script
~/macbook-turbo/uninstall.sh

# Or manually:
pkill -f "cpu-menubar"
launchctl unload ~/Library/LaunchAgents/com.prsmtech.macbookturbo.plist 2>/dev/null
rm -rf ~/macbook-turbo
```

---

## Usage

### Double-Click Launchers

| File | Purpose |
|------|---------|
| `CPU-CONTROL-CENTER.command` | Interactive control panel |
| `START-CPU-MONITOR.command` | Launch menu bar app |
| `RUN-CPU-CLEANUP.command` | Manual cleanup |
| `CHECK-STATUS.command` | View protection status |

### Command Line

```bash
# System Optimizer CLI
python system-optimizer.py status    # Full system dashboard
python system-optimizer.py cleanup   # Run cache cleanup
python system-optimizer.py monitor   # Continuous monitoring
python system-optimizer.py analyze   # Deep analysis

# Individual Modules
python modules/disk_cleaner.py       # Scan cleanable space
python modules/thermal_monitor.py    # Check temperatures
python modules/memory_monitor.py     # Check memory pressure
python modules/process_scorer.py     # Score processes
```

### Shell Scripts

```bash
# Quick cleanup
./cpu-cleanup-enhanced.sh

# Check protection status
./check-protection-status.sh

# Verify startup configuration
./verify-startup.sh
```

---

## Configuration

### Protected Applications

The following are automatically protected from cleanup:

**IDEs & Editors**
- VS Code, Cursor, Xcode
- IntelliJ IDEA, PyCharm, WebStorm
- Sublime Text, vim, nvim, Emacs

**Terminals**
- Terminal.app, iTerm2
- Hyper, Alacritty, kitty, WezTerm

**Development Tools**
- node, npm, yarn, pnpm
- python, pip, conda
- docker, kubectl
- git, ssh, tmux

**Shells**
- zsh, bash, fish

### Customizing Protection

Edit `cpu-cleanup-enhanced.sh` to modify the whitelist:

```bash
PROTECTED_PROCESSES="CustomApp|AnotherApp"
```

---

## Architecture

```
macbook-turbo/
├── cpu-menubar-enhanced.py    # v2.0 Menu bar app
├── cpu-menubar.py             # v1.0 Basic menu bar
├── system-optimizer.py        # CLI optimizer tool
├── cpu-cleanup-enhanced.sh    # Smart cleanup script
├── modules/
│   ├── thermal_monitor.py     # Temperature monitoring
│   ├── memory_monitor.py      # Memory pressure detection
│   ├── disk_cleaner.py        # Cache cleanup (30+ locations)
│   └── process_scorer.py      # Multi-factor scoring
├── config/
│   └── com.user.cpumanager.plist  # LaunchAgent config
└── *.command                  # Double-click launchers
```

---

## Performance

- **Memory Usage**: ~15-25 MB
- **CPU Overhead**: < 1% during monitoring
- **Cleanup Speed**: ~2-5 seconds per run
- **Disk Space Recovery**: Typically 5-25 GB on first run

---

## Troubleshooting

### Menu Bar App Won't Start

```bash
# Check Python installation
python3 --version

# Verify dependencies
pip show rumps psutil

# Check for errors
python cpu-menubar-enhanced.py 2>&1
```

### LaunchAgent Not Working

```bash
# Check if loaded
launchctl list | grep cpumanager

# View logs
cat ~/Library/Logs/cpu-cleanup.log
```

### Process Not Being Protected

```bash
# Check protection status
./check-protection-status.sh

# Test specific process
./test-protection.sh "ProcessName"
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [rumps](https://github.com/jaredks/rumps) for macOS menu bar integration
- System metrics via [psutil](https://github.com/giampaolo/psutil)
- Inspired by the need for developer-friendly system optimization

---

<div align="center">

**Made with :heart: by [PRSMTECH](https://github.com/PRSMTECH)**

</div>
