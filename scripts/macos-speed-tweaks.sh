#!/bin/bash
#
# macos-speed-tweaks.sh - per-user UI/animation speedups (no sudo, reversible)
#
# These don't make the hardware faster, but they make macOS *feel* dramatically
# snappier by cutting animation time — especially valuable on an older Intel Mac
# where every saved GPU cycle helps. All changes are per-user `defaults` writes
# and are fully reversible:  ./macos-speed-tweaks.sh revert
#
# Usage:
#   ./macos-speed-tweaks.sh apply     Apply the speedups (default)
#   ./macos-speed-tweaks.sh revert    Restore macOS defaults
#   ./macos-speed-tweaks.sh show      Print current values

set -uo pipefail

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅${NC} $*"; }
info() { echo -e "${BLUE}ℹ️ ${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️ ${NC} $*"; }

apply() {
    info "Applying per-user UI speedups..."

    # Window + sheet animations
    defaults write -g NSWindowResizeTime -float 0.001
    defaults write -g NSAutomaticWindowAnimationsEnabled -bool false
    defaults write -g NSScrollAnimationEnabled -bool true   # keep smooth scroll

    # Dock: instant autohide, no launch bounce, faster Mission Control
    defaults write com.apple.dock autohide-time-modifier -float 0
    defaults write com.apple.dock autohide-delay -float 0
    defaults write com.apple.dock launchanim -bool false
    defaults write com.apple.dock expose-animation-duration -float 0.1
    defaults write com.apple.dock mineffect -string scale

    # Finder: disable window animations, faster info/copy sheets
    defaults write com.apple.finder DisableAllAnimations -bool true

    # Faster keyboard repeat (developer workflow win)
    defaults write -g KeyRepeat -int 2
    defaults write -g InitialKeyRepeat -int 15

    # Quick Look / Save panel animations off
    defaults write -g NSUseAnimatedFocusRing -bool false

    killall Dock 2>/dev/null || true
    killall Finder 2>/dev/null || true

    ok "Speed tweaks applied."
    warn "Key repeat & some effects fully apply after log out / log back in."
}

revert() {
    info "Reverting to macOS defaults..."
    for kv in \
        "-g NSWindowResizeTime" \
        "-g NSAutomaticWindowAnimationsEnabled" \
        "-g NSScrollAnimationEnabled" \
        "-g KeyRepeat" \
        "-g InitialKeyRepeat" \
        "-g NSUseAnimatedFocusRing" \
        "com.apple.dock autohide-time-modifier" \
        "com.apple.dock autohide-delay" \
        "com.apple.dock launchanim" \
        "com.apple.dock expose-animation-duration" \
        "com.apple.dock mineffect" \
        "com.apple.finder DisableAllAnimations"; do
        # shellcheck disable=SC2086
        defaults delete $kv 2>/dev/null || true
    done
    killall Dock 2>/dev/null || true
    killall Finder 2>/dev/null || true
    ok "Reverted. (Defaults restored; log out/in to fully reset key repeat.)"
}

show() {
    echo "Current values (blank = macOS default):"
    for kv in \
        "-g NSWindowResizeTime" \
        "-g NSAutomaticWindowAnimationsEnabled" \
        "-g KeyRepeat" \
        "-g InitialKeyRepeat" \
        "com.apple.dock autohide-time-modifier" \
        "com.apple.dock launchanim" \
        "com.apple.dock mineffect" \
        "com.apple.finder DisableAllAnimations"; do
        # shellcheck disable=SC2086
        printf "  %-45s = %s\n" "$kv" "$(defaults read $kv 2>/dev/null || echo '(default)')"
    done
}

case "${1:-apply}" in
    apply)        apply ;;
    revert|reset) revert ;;
    show|status)  show ;;
    *) echo "Usage: $0 [apply|revert|show]"; exit 1 ;;
esac
