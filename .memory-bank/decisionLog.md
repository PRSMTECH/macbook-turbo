# Decision Log

## 2026-01-29 - USER_APPS Protection Category

**Context**: Users reported Chrome, Brave, Spotify being killed during cleanup
**Decision**: Create separate USER_APPS category that protects main app processes while allowing helper processes to be killed
**Rationale**:
- Main browser processes (Google Chrome, Brave Browser) should NEVER be killed
- Helper processes (Chrome Helper, Brave Helper) are safe to kill - they respawn
- Distinction between "user intent" (main app) and "background work" (helpers)
- Research from GitHub repos (Stats, asitop, macmon) confirmed this pattern
**Alternatives**:
- Blanket protect all browser processes (would prevent any browser cleanup)
- Only protect by exact name match (too brittle)
**Implementation**: Negative lookahead regex `(?!.*Helper)` to exclude helpers
**Impact**: Critical apps never killed, cleanup still effective for runaway helpers

## 2026-01-29 - Thread Safety with RLock/Lock

**Context**: Menu bar app has multiple timers that can race on shared state
**Decision**: Add RLock for state, Lock for status updates and cleanup operations
**Rationale**:
- `auto_clean_mode` and `last_clean_time` accessed from multiple timer callbacks
- RLock allows same-thread re-entry (needed for property accessors)
- Lock prevents concurrent cleanups from triggering simultaneously
- `try/finally` ensures locks are always released
**Alternatives**:
- Single Lock for everything (could cause deadlocks)
- No locking (race conditions)
- Queue-based approach (over-engineering)
**Impact**: Menu bar app runs stably without race conditions

## 2026-01-29 - Settings Persistence Location

**Context**: User preferences (auto-clean mode, detailed view) should persist
**Decision**: Store in `~/Library/Preferences/com.prsmtech.macbookturbo.json`
**Rationale**:
- Standard macOS location for app preferences
- JSON format is human-readable and easy to edit
- Singleton pattern ensures one source of truth
- Loads on startup, saves on change
**Alternatives**:
- plist file (more macOS native but harder to debug)
- SQLite (overkill for simple settings)
- Config file in app directory (not standard location)
**Impact**: Settings persist between sessions automatically

## 2026-01-29 - Splashtop Protection

**Context**: User requested Splashtop remote desktop never be killed
**Decision**: Add Splashtop Streamer, Business, Personal, and SR* processes to USER_APPS
**Rationale**:
- Remote desktop is critical for remote work
- Killing it would disconnect user from their machine
- Multiple process names (SRServer, SRAgent, SRUtility)
**Impact**: Remote sessions protected during cleanup

## 2026-01-29 - Apple Silicon Monitor Module

**Context**: M-series Macs have different thermal/performance characteristics
**Decision**: Create dedicated apple_silicon_monitor.py module
**Rationale**:
- E-core vs P-core utilization matters for efficiency
- Thermal pressure from `pmset -g therm` is Apple Silicon specific
- Chip detection helps customize recommendations
- Research from asitop/macmon showed value of this data
**Alternatives**:
- Integrate into thermal_monitor.py (would bloat existing module)
- Skip Apple Silicon features (miss optimization opportunities)
**Impact**: Better monitoring for M1/M2/M3/M4 Macs

## 2026-01-01 - README Styling Approach

**Context**: Need to make README accessible for first-time macOS users who may not know how to use Terminal
**Decision**: Add explicit step-by-step walkthrough with expandable sections
**Rationale**:
- Many macOS users never open Terminal
- "How to open Terminal" removes friction for absolute beginners
- Expandable `<details>` keeps advanced info accessible but not overwhelming
- Color explanation table gives immediate understanding
**Alternatives**:
- Video tutorial (higher maintenance, not inline)
- Shorter README (would lose beginners)
**Impact**: Lower barrier to entry for non-technical users

## 2026-01-01 - PRSMTECH Visual Styling

**Context**: README needed brand consistency with other PRSMTECH projects
**Decision**: Apply standard PRSMTECH styling (typing SVG, capsule-render, cyan theme)
**Rationale**:
- Consistent brand identity across projects
- Animated header is eye-catching
- Cyan (#00D4FF) is distinctive and readable
**Alternatives**:
- Keep minimal styling (less memorable)
- Use different color scheme (inconsistent)
**Impact**: Better brand recognition, more professional appearance

## 2026-01-01 - Dynamic Path Resolution

**Context**: App had hardcoded `/Users/bigswizz/` paths that would break for other users
**Decision**: Use `os.path.dirname(os.path.abspath(__file__))` for dynamic path resolution
**Rationale**:
- Works regardless of install location
- Standard Python pattern for this use case
- No user configuration required
**Alternatives**:
- Environment variables (extra setup)
- Config file (extra complexity)
**Impact**: App now works for all users without modification (CRITICAL FIX)

## 2026-01-01 - One-Line Installer Pattern

**Context**: Needed easy installation for users unfamiliar with git/pip
**Decision**: Create curl-based one-line installer
**Rationale**:
- Industry standard (Homebrew, oh-my-zsh use same pattern)
- Single command to copy/paste
- Handles all setup automatically
**Alternatives**:
- Homebrew formula (requires separate tap)
- Manual instructions only (higher friction)
**Impact**: Dramatically reduced installation friction

## 2025-12-27 - GitHub Repository Naming

**Context**: Deploying cpu-monitor to fresh GitHub repository
**Decision**: Named repository "macbook-turbo" in PRSMTECH organization
**Rationale**:
- More marketable/memorable name than "cpu-monitor"
- Reflects the turbo/optimization focus
- Matches the product positioning as a performance toolkit
**Impact**: Better branding for potential open-source adoption
