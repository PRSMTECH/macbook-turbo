# Active Context

**Last Updated**: 2026-06-29

## Current Focus
- **v2.2.0 Intel i9 Optimization + Startup Repair** — machine-specific tuning for
  the 2018 15" MacBook Pro (`MacBookPro15,1`, Core i9-8950HK)

## Machine context (this Mac)
- `MacBookPro15,1` · Intel i9-8950HK (6c/12t) · 32 GB · macOS 15.6 Sequoia · x86_64
- Severe thermal throttling — observed CPU speed limit as low as **35%** under load
- Discrete Radeon Pro 560X (heat source) + Intel UHD 630 (cool); auto GPU switching on

## Completed This Session (2026-06-29)

### Live system repair
- Removed 3 broken `com.user.*` LaunchAgents (dead `/Users/bigswizz/cpu-monitor`
  path, exit codes 127/78)
- Removed duplicate `MacBookTurbo` / `cpu-menubar.py` Login Items (kept Google
  Drive, Claude)
- Stopped rogue menu bar process (ran from a 2nd repo clone via Xcode Python 3.9)
- Moved stray duplicate clone `/Users/bigswizz/PRSMTECH/macbook-turbo` →
  `~/.macbook-turbo-backups/<ts>/`
- Installed ONE correct LaunchAgent (`com.prsmtech.macbookturbo`) via
  `scripts/install-launch-agent.sh`, pointing at this repo's venv. Loaded + runs at login.

### New Intel features
- `modules/intel_optimizer.py` — throttle %, Turbo Boost, GPU switch, Low Power, advice
- Menu bar: "⚡ Performance (Intel)" submenu + live state + 🐢 throttle glyph in title
- `scripts/optimize-intel.sh` — Turbo/GPU/Low-Power levers + `cool-now` + `revert`
- `scripts/macos-speed-tweaks.sh` — per-user UI speedups (applied) + `revert`
- `scripts/install-launch-agent.sh` — location-independent run-at-login installer
- `docs/INTEL-OPTIMIZATION.md`

### Cleanup
- Archived 5 obsolete old-startup scripts → `archive/deprecated-scripts/`
- Removed `.DS_Store` + `__pycache__`; bandit clean (`# nosec B108` on `/tmp` cleanup target)

## Backups (fully reversible)
- `~/.macbook-turbo-backups/<timestamp>/` — 4 old plists, stray clone, `RESTORE-NOTES.txt`

## Known Blockers
- None. Turbo Boost Switcher not installed (needed for the `turbo-off` lever).

## Next Session Priorities
1. Install Turbo Boost Switcher to enable the Turbo Boost lever
2. Tag a v2.2.0 release
3. Optional: Homebrew formula
