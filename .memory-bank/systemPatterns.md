# System Patterns

**Last Updated**: 2025-12-27

## Established Patterns

### Multi-Factor Process Scoring
```
Score = CPU(40%) + Memory(30%) + FDs(10%) + Age(10%) + Category(10%)
```
- Higher score = more eligible for cleanup
- Protected processes get score of 0

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
└── process_scorer.py
```

## Best Practices

### Developer Protection
Always whitelist:
- IDEs (VS Code, Cursor, Xcode, etc.)
- Terminals (Terminal, iTerm, etc.)
- Shells (zsh, bash, fish)
- Dev tools (node, python, docker, git)

### Logging
- Log to `~/Library/Logs/cpu-cleanup.log`
- Include timestamps
- Record actions taken

### macOS Integration
- Use `launchctl` for auto-start services
- Store plists in `~/Library/LaunchAgents/`
- Use `rumps` for menu bar apps
