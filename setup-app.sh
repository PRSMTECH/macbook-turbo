#!/bin/bash
# MacBook Turbo App Setup
# Creates a desktop app and optionally adds to Login Items

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="MacBook Turbo"
APP_BUNDLE="$SCRIPT_DIR/MacBookTurbo.app"

echo "🚀 MacBook Turbo App Setup"
echo "=========================="
echo ""

# Make the app executable
chmod +x "$APP_BUNDLE/Contents/MacOS/MacBookTurbo"

# Remove empty icon file and use system icon
rm -f "$APP_BUNDLE/Contents/Resources/AppIcon.icns"

echo "✅ App bundle configured"

# Ask where to install
echo ""
echo "Where would you like to install MacBook Turbo?"
echo "  1) Desktop (recommended for easy access)"
echo "  2) Applications folder"
echo "  3) Both"
echo "  4) Keep in current location only"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        cp -R "$APP_BUNDLE" "$HOME/Desktop/"
        echo "✅ Installed to Desktop"
        INSTALLED_APP="$HOME/Desktop/MacBookTurbo.app"
        ;;
    2)
        cp -R "$APP_BUNDLE" "/Applications/"
        echo "✅ Installed to Applications"
        INSTALLED_APP="/Applications/MacBookTurbo.app"
        ;;
    3)
        cp -R "$APP_BUNDLE" "$HOME/Desktop/"
        cp -R "$APP_BUNDLE" "/Applications/"
        echo "✅ Installed to Desktop and Applications"
        INSTALLED_APP="/Applications/MacBookTurbo.app"
        ;;
    4)
        echo "✅ Keeping in current location"
        INSTALLED_APP="$APP_BUNDLE"
        ;;
    *)
        echo "Invalid choice, keeping in current location"
        INSTALLED_APP="$APP_BUNDLE"
        ;;
esac

# Set a nice icon using Finder
osascript <<EOF 2>/dev/null || true
tell application "Finder"
    set theFile to POSIX file "$INSTALLED_APP" as alias
    set label index of theFile to 4
end tell
EOF

echo ""
read -p "Would you like to start MacBook Turbo at login? [y/N]: " login_choice

if [[ "$login_choice" =~ ^[Yy]$ ]]; then
    osascript <<EOF
tell application "System Events"
    make login item at end with properties {path:"$INSTALLED_APP", hidden:false}
end tell
EOF
    echo "✅ Added to Login Items"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start MacBook Turbo:"
echo "  • Double-click the app icon"
echo "  • Or run: open \"$INSTALLED_APP\""
echo ""
echo "The CPU monitor will appear in your menu bar (top right)."
echo ""

read -p "Start MacBook Turbo now? [Y/n]: " start_choice

if [[ ! "$start_choice" =~ ^[Nn]$ ]]; then
    open "$INSTALLED_APP"
    echo "✅ MacBook Turbo started! Look for the CPU indicator in your menu bar."
fi
