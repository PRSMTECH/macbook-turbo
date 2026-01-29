# System Patterns

**Last Updated**: 2026-01-29

## Established Patterns

### Process Category Hierarchy (NEW)
```
PROTECTED CATEGORIES (never killed):
├── SYSTEM_CRITICAL  → kernel_task, launchd, WindowServer
├── DEVELOPMENT      → Code, Cursor, node, python, git, claude
├── TERMINAL         → Terminal, iTerm, zsh, bash, ssh
└── USER_APPS        → Chrome, Brave, Spotify, Slack, Splashtop (main processes only)

KILLABLE CATEGORIES (can be killed when high CPU):
├── BROWSER          → Chrome Helper, Brave Helper, Safari Web Content
├── MEDIA            → Spotify Helper
├── COMMUNICATION    → Slack Helper, Discord Helper
├── BACKGROUND       → mdworker, mds_stores
└── OTHER            → Unknown processes
```

### Main App vs Helper Process Distinction (NEW)
```python
# Main app (PROTECTED) - negative lookahead excludes helpers
r"^Google Chrome(?!.*Helper)"  # Matches "Google Chrome" but NOT "Google Chrome Helper"
r"^Brave(?!.*Helper)"          # Matches "Brave" but NOT "Brave Helper"
r"^Spotify(?!.*Helper)"        # Matches "Spotify" but NOT "Spotify Helper"

# Helper process (KILLABLE) - matches helpers specifically
r"Chrome Helper"               # Matches "Google Chrome Helper"
r"Spotify Helper"              # Matches "Spotify Helper"
```

### Multi-Factor Process Scoring
```
Score = CPU(40%) + Memory(30%) + FDs(10%) + Age(10%) + Category(10%)
```
- Higher score = more eligible for cleanup
- Protected categories get -100 penalty (effectively 0)
- USER_APPS category gets -400 penalty

### Thread Safety Pattern (NEW)
```python
# State protection with RLock (allows re-entry)
self._state_lock = RLock()

@property
def auto_clean_mode(self) -> AutoCleanMode:
    with self._state_lock:
        return self._auto_clean_mode

# Cleanup protection with Lock (prevents concurrent cleanup)
self._cleanup_lock = Lock()

def _run_auto_cleanup(self):
    if not self._cleanup_lock.acquire(blocking=False):
        return  # Skip if cleanup already running
    try:
        # ... cleanup code ...
    finally:
        self._cleanup_lock.release()  # Always release
```

### Settings Persistence Pattern (NEW)
```python
# Singleton settings manager
class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

# Location: ~/Library/Preferences/com.prsmtech.macbookturbo.json
```

### Color-Coded Status Indicators
| CPU Load | Color | Meaning |
|----------|-------|---------|
| < 50% | 🟢 Green | Normal |
| 50-80% | 🟡 Yellow | Moderate |
| > 80% | 🔴 Red | High |

### Graceful Process Termination
1. Send SIGTERM first
2. Wait 1 second
3. Send SIGKILL if still running

### Auto-Cleanup Mode Thresholds
| Mode | CPU | Memory |
|------|-----|--------|
| OFF | - | - |
| CONSERVATIVE | >90% | >95% |
| BALANCED | >70% | >85% |
| AGGRESSIVE | >50% | >70% |

## Conventions

### File Naming
- `.command` files: Double-click launchers
- `*.sh` files: Shell scripts
- `*-enhanced.*`: v2.0 versions with additional features

### Module Structure
```
modules/
├── __init__.py
├── thermal_monitor.py
├── memory_monitor.py
├── disk_cleaner.py
├── process_scorer.py
└── apple_silicon_monitor.py  ← NEW
config/
├── protected-processes.sh
└── settings.py               ← NEW
```

## Best Practices

### Developer Protection
Always whitelist:
- IDEs (VS Code, Cursor, Xcode, etc.)
- Terminals (Terminal, iTerm, etc.)
- Shells (zsh, bash, fish)
- Dev tools (node, python, docker, git, claude)

### User App Protection (NEW)
Protect main processes, allow helper cleanup:
- Browsers: Chrome, Brave, Safari, Firefox, Arc
- Media: Spotify, Music, VLC
- Communication: Slack, Discord, Zoom, Teams
- Remote Desktop: Splashtop Streamer, SRServer

### Logging
- Log to `~/Library/Logs/cpu-cleanup.log`
- Include timestamps
- Record actions taken

### macOS Integration
- Use `launchctl` for auto-start services
- Store plists in `~/Library/LaunchAgents/`
- Use `rumps` for menu bar apps
- Store settings in `~/Library/Preferences/`

### Apple Silicon Support (NEW)
- Detect chip type via `sysctl -n machdep.cpu.brand_string`
- Monitor thermal pressure via `pmset -g therm`
- Track E-core vs P-core configuration
- Support M1/M2/M3/M4 (including Pro/Max/Ultra variants)
