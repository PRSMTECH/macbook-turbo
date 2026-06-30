# Active Context

**Last Updated**: 2026-06-29

## Current Focus
- **v2.2.0 Intel i9 Optimization SHIPPED** (commit `32090d0`, pushed to `main`)
- Live thermal tuning applied to this machine + measured

## Machine context (this Mac)
- `MacBookPro15,1` · Intel i9-8950HK (6c/12t) · 32 GB · macOS 15.6 Sequoia · x86_64
- Throttle-prone; was throttling to ~35% under load

## Live machine state (applied this session — persists across reboots)
- `gpuswitch 0` → discrete Radeon 560X **parked** (integrated-only) ✅
- `lowpowermode 1` → Low Power Mode **ON** ✅
- Result: measured CPU speed limit recovered **39% → 100%** and held within ~1 min
- Undo anytime: `./scripts/optimize-intel.sh revert`

## OPEN LOOP — finish after next reboot
- Turbo Boost Switcher **Pro** installed (`/Applications/Turbo Boost Switcher.app`)
- Kext "Legacy Developer: Rugarciap" **APPROVED** in Privacy & Security, but
  **NOT loaded yet — requires a REBOOT** (user deferred the restart)
- After reboot: open Turbo Boost Switcher → **Disable Turbo Boost** (or set **Auto
  Mode ~80 °C**), then verify: `kextstat | grep -i turbo` loaded + optimizer shows
  `Turbo Boost: disabled 🧊`. Turbo-off is the insurance for heavy *sustained* load.

## Startup model (repaired this session)
- One LaunchAgent: `com.prsmtech.macbookturbo` (via `scripts/install-launch-agent.sh`),
  points at this repo's venv. Old `com.user.*` agents + duplicate Login Items removed.
- Backups: `~/.macbook-turbo-backups/<ts>/` (with `RESTORE-NOTES.txt`)

## Known Blockers
- None. Turbo-off pending a user reboot (not a blocker for normal use).

## Next Session Priorities
1. After reboot: load turbo kext + Disable Turbo Boost / Auto Mode, then verify
2. Tag a v2.2.0 release
3. Optional: Homebrew formula
