#!/bin/bash

# Protected Processes Configuration
# Shared list of processes that should NEVER be killed during cleanup
# Used by: cpu-cleanup-enhanced.sh, deploy-cpu-fix.sh, test-protection.sh

# Processes to NEVER kill
NEVER_KILL=(
    # System critical
    "kernel_task"
    "launchd"
    "SystemUIServer"
    "Finder"
    "Dock"
    "loginwindow"
    "WindowServer"
    "airportd"
    "bluetoothd"

    # Terminal emulators
    "Terminal"
    "iTerm"
    "Hyper"
    "Alacritty"
    "kitty"
    "WezTerm"

    # Shells
    "zsh"
    "bash"
    "sh"
    "fish"

    # IDEs and Editors
    "Code"
    "code"
    "Cursor"
    "cursor"
    "IntelliJ"
    "WebStorm"
    "PyCharm"
    "RubyMine"
    "GoLand"
    "DataGrip"
    "Rider"
    "Xcode"
    "Android Studio"
    "Sublime Text"
    "TextEdit"
    "Nova"
    "BBEdit"
    "vim"
    "nvim"
    "emacs"
    "nano"

    # Development tools
    "node"
    "npm"
    "yarn"
    "pnpm"
    "python"
    "python3"
    "ruby"
    "java"
    "go"
    "cargo"
    "rustc"
    "git"
    "docker"
    "kubectl"

    # Active sessions
    "ssh"
    "tmux"
    "screen"
    "mosh"

    # VS Code processes (all variants)
    "Code Helper"
    "Code - Insiders"
    "code-server"
    "electron"

    # Claude related
    "claude"

    # ========================================
    # USER APPLICATIONS (main processes only)
    # These are apps the user wants to keep running
    # Only their HELPER processes can be killed
    # ========================================

    # Browsers - MAIN processes (helpers can be killed)
    "Google Chrome"
    "Brave Browser"
    "Brave"
    "Safari"
    "Firefox"
    "Arc"
    "Microsoft Edge"
    "Opera"

    # Media players - MAIN processes
    "Spotify"
    "Music"
    "iTunes"
    "VLC"
    "IINA"
    "QuickTime Player"

    # Communication apps - MAIN processes
    "Slack"
    "Discord"
    "Zoom.us"
    "Microsoft Teams"
    "Messages"
    "FaceTime"
    "WhatsApp"
    "Telegram"
    "Signal"

    # Remote desktop applications
    "Splashtop Streamer"
    "Splashtop Business"
    "Splashtop Personal"
    "SRServer"
    "SRAgent"
    "SRUtility"
)

# Processes that CAN be killed when using excessive CPU
# NOTE: These are HELPER/WORKER processes only, NOT main applications
CAN_KILL_IF_HIGH_CPU=(
    # System background processes
    "mdworker"
    "mds_stores"
    "com.apple.WebKit"
    "quicklookd"
    "corespotlightd"

    # Browser HELPER processes (NOT main browser apps)
    "Safari Web Content"
    "Safari Networking"
    "Google Chrome Helper"
    "Brave Browser Helper"
    "Firefox Content"
    "Arc Helper"
    "Microsoft Edge Helper"

    # Communication HELPER processes
    "Slack Helper"
    "Discord Helper"
    "Teams Helper"
    "Zoom Helper"

    # Media HELPER processes
    "Spotify Helper"

    # Other helpers
    "plugin_host"
)

# Export for use in other scripts
export NEVER_KILL
export CAN_KILL_IF_HIGH_CPU
