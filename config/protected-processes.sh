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
)

# Processes that CAN be killed when using excessive CPU
CAN_KILL_IF_HIGH_CPU=(
    "mdworker"
    "mds_stores"
    "com.apple.WebKit"
    "Safari Web Content"
    "Google Chrome Helper"
    "firefox"
    "plugin_host"
    "quicklookd"
    "corespotlightd"
)

# Export for use in other scripts
export NEVER_KILL
export CAN_KILL_IF_HIGH_CPU
