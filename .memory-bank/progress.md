# Progress Log

**Project**: MacBook Turbo
**Last Updated**: 2026-01-29

## Completed This Session

### 2026-06-29 - v2.2.0 Intel i9 Optimization + Startup Repair
- ✅ Diagnosed live system: 3 broken `com.user.*` LaunchAgents (exit 127/78, dead path), duplicate Login Items, rogue process from a 2nd repo clone (Xcode Python 3.9)
- ✅ Repaired startup: removed stale agents + login items, stopped rogue process, moved stray clone to `~/.macbook-turbo-backups/`, installed one correct venv-based LaunchAgent
- ✅ Created `modules/intel_optimizer.py` — throttle %, Turbo Boost, GPU switch, Low Power, model-aware advice
- ✅ Menu bar: "⚡ Performance (Intel)" submenu + live state + 🐢 throttle glyph in title
- ✅ `scripts/optimize-intel.sh` + `macos-speed-tweaks.sh` + `install-launch-agent.sh`
- ✅ `docs/INTEL-OPTIMIZATION.md`; README → v2.2.0 + readme-style refresh
- ✅ Archived 5 obsolete startup scripts; flake8/bandit clean
- ✅ Observed live CPU throttle as low as 35% speed (validates thermal-first approach)

### 2026-01-29 - v2.1.1 Cleanup & Organization
- ✅ Added protected apps: Antigravity, GitHub Desktop, Claude Desktop
- ✅ Fixed broken paths in bin/ (cpu-clean, cpu-status, cpu-test)
- ✅ Archived legacy cpu-menubar.py to archive/
- ✅ Fixed file permissions on all scripts
- ✅ Project cleanup and organization complete

### 2026-01-29 - v2.1.0 Protection System Rebuild
- ✅ Added USER_APPS ProcessCategory for main app protection
- ✅ Updated process_scorer.py with negative lookahead regex patterns
- ✅ Protected apps: Chrome, Brave, Safari, Firefox, Spotify, Slack, Discord, Splashtop
- ✅ Only helper processes are killable (Chrome Helper, Spotify Helper, etc.)
- ✅ Added thread safety with RLock and Lock
- ✅ Created settings.py for persistence (~/.../com.prsmtech.macbookturbo.json)
- ✅ Created apple_silicon_monitor.py (M1/M2/M3/M4 detection)
- ✅ Updated test-protection.sh with comprehensive test suite
- ✅ All 26 shell tests + 24 Python tests passing
- ✅ CPU monitor launched and running

### 2026-01-01 - /ship with PRSMTECH Styling
- ✅ Applied PRSMTECH visual styling to README
- ✅ Added animated typing SVG header ("Keep Your Mac Running Fast...")
- ✅ Added capsule-render gradient separators
- ✅ Used cyan theme color (#00D4FF) for badges
- ✅ Added version badge (v1.0.0)
- ✅ Created beginner-friendly "Super Easy Install" walkthrough
- ✅ Added "How to open Terminal" instructions for new users
- ✅ Added "What the Colors Mean" quick reference table
- ✅ Converted features to expandable `<details>` sections
- ✅ Added comprehensive FAQ with troubleshooting
- ✅ Committed and pushed (150bb48)

### 2026-01-01 - v1.0.0 Release Preparation
- ✅ Fixed hardcoded `/Users/bigswizz/` paths (CRITICAL)
- ✅ Created `install.sh` one-line installer
- ✅ Created GitHub Actions CI workflow (Python 3.9-3.12)
- ✅ Enhanced `uninstall.sh` with proper cleanup
- ✅ Updated README with Quick Start & prerequisites
- ✅ Added CHANGELOG.md
- ✅ Tagged and pushed v1.0.0 release

### 2025-12-27 - Initial GitHub Deployment
- ✅ Created PRSMTECH/macbook-turbo repository
- ✅ Created professional README.md with badges
- ✅ Added MIT LICENSE
- ✅ Added .gitignore for Python/macOS
- ✅ Initial commit: 32 files, 5,286 lines
- ✅ Pushed to GitHub successfully

## Repository Statistics
- **URL**: https://github.com/PRSMTECH/macbook-turbo
- **Latest Tag**: v1.0.0 (v2.1.0 pending)
- **Branch**: main
- **Visibility**: Public

## Current Status
✅ **v2.1.0 SHIPPED!** (f168e70) - Protection System Overhaul Complete!

### Deployment - 2026-01-29
- **URL**: https://github.com/PRSMTECH/macbook-turbo
- **Tag**: v2.1.0
- **Commit**: f168e70
- **Branch**: main
- **Changes**: Smart protection system, USER_APPS category, thread safety, settings persistence, Apple Silicon monitor

## New Files This Session
- `config/settings.py` - Settings persistence manager
- `modules/apple_silicon_monitor.py` - M-series chip monitoring

## Modified Files This Session
- `modules/process_scorer.py` - USER_APPS category, regex patterns
- `config/protected-processes.sh` - Added user apps to NEVER_KILL
- `src/cpu-menubar-enhanced.py` - Thread safety, settings integration
- `scripts/test-protection.sh` - Comprehensive test suite

## Install Command
```bash
curl -fsSL https://raw.githubusercontent.com/PRSMTECH/macbook-turbo/main/install.sh | bash
```

## Next Priorities
1. Test menu bar app stability under load
2. Integrate Apple Silicon monitor into UI
3. Update README for v2.1.0 features
4. Create v2.1.0 release tag
5. Optional: Homebrew formula

## Milestones
- [x] Menu bar app v1.0 (cpu-menubar.py)
- [x] Enhanced menu bar v2.0 (cpu-menubar-enhanced.py)
- [x] Modular architecture (modules/)
- [x] System optimizer CLI
- [x] GitHub deployment complete
- [x] v1.0.0 Released with one-line installer
- [x] PRSMTECH README styling applied
- [x] **v2.1.0 Protection system overhaul** ← LATEST
- [x] **Thread safety & settings persistence** ← LATEST
- [x] **Apple Silicon monitoring**
- [x] **v2.2.0 Intel i9 optimizer + startup repair** ← LATEST
