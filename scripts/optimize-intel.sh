#!/bin/bash
#
# optimize-intel.sh - Intel-Mac thermal & performance levers
#
# Tuned for the thermal-throttle-prone 2018 15" MacBook Pro (MacBookPro15,1,
# Core i9-8950HK). On that chassis the CPU throttles HARD under sustained load,
# so capping heat (disable Turbo Boost, force the integrated GPU, Low Power
# Mode) typically RAISES sustained performance and quiets the fans.
#
# Everything here is reversible:  ./optimize-intel.sh revert
#
# Commands that change system power settings need sudo (you will be prompted).
# Nothing is applied just by sourcing this file - you must pass a command.

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}ℹ️ ${NC} $*"; }
ok()    { echo -e "${GREEN}✅${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠️ ${NC} $*"; }
err()   { echo -e "${RED}❌${NC} $*"; }

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$REPO_DIR/venv/bin/python"
[ -x "$PYTHON" ] || PYTHON="$(command -v python3)"

require_intel() {
    if [ "$(uname -m)" != "x86_64" ]; then
        err "This machine is Apple Silicon. Intel levers do not apply."
        exit 1
    fi
}

# --- Turbo Boost (via Turbo Boost Switcher CLI / app) ----------------------
turbo_cli() {
    if command -v turbo-boost >/dev/null 2>&1; then echo "turbo-boost"; return 0; fi
    if command -v tbswitcher >/dev/null 2>&1; then echo "tbswitcher"; return 0; fi
    return 1
}

turbo_off() {
    info "Disabling Turbo Boost (caps heat → less throttling on the i9)..."
    if cli=$(turbo_cli); then
        sudo "$cli" disable && ok "Turbo Boost disabled."
    elif [ -d "/Applications/Turbo Boost Switcher.app" ]; then
        warn "Turbo Boost Switcher app is installed but has no CLI."
        warn "Open it from the menu bar and choose 'Disable Turbo Boost'."
    else
        warn "Turbo Boost Switcher is not installed."
        echo "   Install it (free):  https://tbswitcher.rugarciap.com/"
        echo "   It needs a one-time kernel-extension approval in System Settings → Privacy & Security."
    fi
}

turbo_on() {
    info "Re-enabling Turbo Boost..."
    if cli=$(turbo_cli); then
        sudo "$cli" enable && ok "Turbo Boost enabled."
    else
        warn "No Turbo Boost Switcher CLI found; toggle it from the app's menu bar item."
    fi
}

# --- Discrete GPU switching (pmset gpuswitch) ------------------------------
# 0 = integrated only (coolest)   1 = discrete only (hottest)   2 = automatic
gpu_integrated() {
    require_intel
    info "Forcing the integrated Intel UHD 630 GPU (Radeon stays parked → cooler)..."
    sudo pmset -a gpuswitch 0 && ok "GPU set to integrated-only. (Some apps may need a relaunch.)"
}
gpu_auto() {
    require_intel
    info "Restoring automatic graphics switching..."
    sudo pmset -a gpuswitch 2 && ok "GPU switching set to automatic (macOS default)."
}

# --- Low Power Mode (pmset lowpowermode) -----------------------------------
lowpower_on() {
    info "Enabling Low Power Mode (lower clocks, cooler, quieter, longer battery)..."
    sudo pmset -a lowpowermode 1 && ok "Low Power Mode ON."
}
lowpower_off() {
    info "Disabling Low Power Mode..."
    sudo pmset -a lowpowermode 0 && ok "Low Power Mode OFF."
}

status() {
    require_intel
    "$PYTHON" "$REPO_DIR/modules/intel_optimizer.py"
}

cool_now() {
    # One-shot "cool this machine down" combo for the throttle-prone i9.
    require_intel
    warn "Applying the full cool-down combo (needs sudo)..."
    gpu_integrated
    lowpower_on
    turbo_off
    echo
    ok "Cool-down combo applied. Run './optimize-intel.sh status' to confirm."
    info "To undo everything:  ./optimize-intel.sh revert"
}

revert() {
    require_intel
    warn "Reverting Intel optimizations to macOS defaults..."
    sudo pmset -a gpuswitch 2 || true
    sudo pmset -a lowpowermode 0 || true
    turbo_on || true
    ok "Reverted: automatic GPU, Low Power Mode off, Turbo Boost on."
}

usage() {
    cat <<EOF
Intel-Mac optimization levers (2018 i9 MacBook Pro tuned)

Usage: ./optimize-intel.sh <command>

  status           Show CPU model, throttle %, turbo/GPU/power state + advice
  cool-now         Apply the full cool-down combo (GPU→integrated, Low Power on,
                   Turbo off) — best single command for a throttling i9
  turbo-off        Disable Turbo Boost (needs Turbo Boost Switcher)
  turbo-on         Re-enable Turbo Boost
  gpu-integrated   Force the cooler integrated GPU (sudo)
  gpu-auto         Restore automatic graphics switching (sudo)
  lowpower-on      Enable Low Power Mode (sudo)
  lowpower-off     Disable Low Power Mode (sudo)
  revert           Undo all of the above (back to macOS defaults)

Tip: 'status' is read-only and safe. The sudo commands change system power
settings and are fully reversible with 'revert'.
EOF
}

case "${1:-status}" in
    status)          status ;;
    cool-now)        cool_now ;;
    turbo-off)       turbo_off ;;
    turbo-on)        turbo_on ;;
    gpu-integrated)  gpu_integrated ;;
    gpu-auto)        gpu_auto ;;
    lowpower-on)     lowpower_on ;;
    lowpower-off)    lowpower_off ;;
    revert|reset)    revert ;;
    -h|--help|help)  usage ;;
    *)               err "Unknown command: $1"; echo; usage; exit 1 ;;
esac
