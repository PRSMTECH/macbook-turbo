# Active Context

**Last Updated**: 2026-01-29

## Current Focus
- **v2.1.0 Protection System Overhaul** - Complete rebuild of process protection
- CPU monitor running with enhanced thread safety
- Settings persistence implemented
- Apple Silicon monitoring added

## Active Features
- CPU/Memory/Thermal menu bar monitor (v2.0)
- **NEW: USER_APPS protection category** - Main apps protected, only helpers killed
- **NEW: Thread-safe state management** - RLock/Lock for concurrent access
- **NEW: Settings persistence** - `~/Library/Preferences/com.prsmtech.macbookturbo.json`
- **NEW: Apple Silicon monitor** - M1/M2/M3/M4 chip detection & thermal pressure
- **NEW: Splashtop protection** - Remote desktop apps never killed
- Intelligent process management with developer protection
- Modular architecture with 5 specialized monitors
- Auto-cleanup modes (Off/Conservative/Balanced/Aggressive)

## Completed This Session (2026-01-29)

### Phase 1: Protection System Overhaul
- Added `USER_APPS` ProcessCategory for main application protection
- Updated regex patterns with negative lookahead to exclude helper processes
- Protected: Google Chrome, Brave, Safari, Firefox, Spotify, Slack, Discord, Splashtop
- Killable helpers: Chrome Helper, Brave Helper, Safari Web Content, Spotify Helper, etc.

### Phase 2: Thread Safety
- Added `RLock` for state protection (`auto_clean_mode`, `last_clean_time`)
- Added `Lock` for status updates and cleanup operations
- Fixed background cleanup with proper `try/finally` lock release
- Created thread-safe property accessors

### Phase 3: Settings Persistence
- Created `config/settings.py` - Singleton pattern settings manager
- Saves to `~/Library/Preferences/com.prsmtech.macbookturbo.json`
- Persists: auto_clean_mode, show_detailed, cooldown_seconds
- Loads on startup, saves on mode change

### Phase 4: Apple Silicon Support
- Created `modules/apple_silicon_monitor.py`
- Detects M1/M2/M3/M4 chip types (including Pro/Max/Ultra variants)
- Monitors thermal pressure via `pmset -g therm`
- Tracks E-core vs P-core configuration

### Phase 5: Test Suite Update
- Comprehensive test script `scripts/test-protection.sh`
- Tests shell-level (NEVER_KILL array) and Python-level protection
- All 26 shell tests + 24 Python tests passing

## Known Blockers
- None - All features working!

## Next Session Priorities
1. Test menu bar app thoroughly with various workloads
2. Consider integrating Apple Silicon monitor into menu bar UI
3. Add thermal pressure display in menu bar
4. Optional: Homebrew formula for easier distribution
5. Update README with new v2.1.0 features
