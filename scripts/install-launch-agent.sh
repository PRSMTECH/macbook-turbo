#!/bin/bash
#
# install-launch-agent.sh - run MacBook Turbo's menu bar app at login, correctly
#
# Generates a LaunchAgent that points at THIS repo's venv Python and the
# enhanced menu bar app, then loads it. Works regardless of where the repo
# lives (it resolves its own path), so it can't drift to a dead path the way
# the old com.user.* agents did.
#
# Usage:
#   ./install-launch-agent.sh            Install + load (run at login)
#   ./install-launch-agent.sh --uninstall  Bootout + remove the agent
#   ./install-launch-agent.sh --status     Show whether it's loaded

set -euo pipefail

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅${NC} $*"; }
info() { echo -e "${BLUE}ℹ️ ${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️ ${NC} $*"; }
err()  { echo -e "${RED}❌${NC} $*"; }

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.prsmtech.macbookturbo"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
APP="$REPO_DIR/src/cpu-menubar-enhanced.py"
VENV_PY="$REPO_DIR/venv/bin/python"
DOMAIN="gui/$(id -u)"

uninstall() {
    info "Removing LaunchAgent $LABEL..."
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    ok "Uninstalled. The menu bar app will no longer start at login."
}

status() {
    if launchctl list 2>/dev/null | grep -q "$LABEL"; then
        ok "$LABEL is loaded:"
        launchctl list | grep "$LABEL"
    else
        warn "$LABEL is not loaded."
    fi
    [ -f "$PLIST" ] && info "Plist: $PLIST" || warn "No plist installed."
}

install() {
    [ -f "$APP" ] || { err "Menu bar app not found at $APP"; exit 1; }

    if [ ! -x "$VENV_PY" ]; then
        info "No venv found - creating one and installing dependencies..."
        python3 -m venv "$REPO_DIR/venv"
        "$REPO_DIR/venv/bin/python" -m pip install --quiet --upgrade pip
        "$REPO_DIR/venv/bin/python" -m pip install --quiet -r "$REPO_DIR/requirements.txt"
        ok "venv ready."
    fi

    mkdir -p "$HOME/Library/LaunchAgents"

    cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PY</string>
        <string>$APP</string>
    </array>

    <!-- Start at login -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Restart if it crashes (but not if it exits cleanly, e.g. user Quit) -->
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>ThrottleInterval</key>
    <integer>10</integer>

    <key>WorkingDirectory</key>
    <string>$REPO_DIR</string>

    <!-- Low priority so the monitor never competes with real work -->
    <key>Nice</key>
    <integer>5</integer>
    <key>ProcessType</key>
    <string>Interactive</string>

    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/macbook-turbo.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/macbook-turbo.err</string>
</dict>
</plist>
EOF

    ok "Wrote $PLIST"
    info "Pointing at: $VENV_PY $APP"

    # Reload cleanly
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    launchctl bootstrap "$DOMAIN" "$PLIST"
    launchctl enable "$DOMAIN/$LABEL" 2>/dev/null || true
    ok "Loaded. The menu bar app starts now and at every login."
    info "Logs: ~/Library/Logs/macbook-turbo.log"
}

case "${1:-install}" in
    --uninstall|uninstall) uninstall ;;
    --status|status)       status ;;
    install|"")            install ;;
    *) echo "Usage: $0 [install|--uninstall|--status]"; exit 1 ;;
esac
