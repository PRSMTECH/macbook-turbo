# Changelog

All notable changes to MacBook Turbo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-01

### Added
- **One-line installer** - Install with a single curl command
- **GitHub Actions CI** - Automated testing for Python 3.9-3.12
- **Improved uninstall script** - Clean removal with proper cleanup
- **Dynamic path resolution** - No more hardcoded paths

### Features
- **Menu Bar App (v2.0)** - Real-time CPU/Memory/Thermal monitoring
- **System Optimizer CLI** - Command-line interface for power users
- **Intelligent Process Management** - Multi-factor scoring algorithm
- **Developer Protection** - 30+ whitelisted dev tools
- **Disk Cleanup** - 30+ cache locations supported
- **Auto-Cleanup Modes** - Off, Conservative, Balanced, Aggressive

### Modules
- `thermal_monitor.py` - CPU/GPU temperature and throttle detection
- `memory_monitor.py` - macOS-native memory pressure monitoring
- `disk_cleaner.py` - Smart cache cleanup with dry-run support
- `process_scorer.py` - Protected process identification

### Documentation
- Comprehensive README with installation guide
- HOW-TO-USE.txt for quick reference
- Inline code documentation

---

## [Unreleased]

### Planned
- Homebrew formula for easier installation
- Configuration file support
- Additional thermal sensors for Apple Silicon
- Notification center integration
