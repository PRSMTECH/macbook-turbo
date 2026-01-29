#!/bin/bash
# One-Click Desktop App Installer
# Double-click this file to install MacBook Turbo to your Desktop

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_BUNDLE="$SCRIPT_DIR/MacBookTurbo.app"

echo "🚀 Installing MacBook Turbo..."
echo ""

# Make executable
chmod +x "$APP_BUNDLE/Contents/MacOS/MacBookTurbo"

# Remove empty icon placeholder
rm -f "$APP_BUNDLE/Contents/Resources/AppIcon.icns"

# Copy to Desktop
cp -R "$APP_BUNDLE" "$HOME/Desktop/"

echo "✅ Installed to Desktop!"
echo ""

# Also add to Dock (optional via AppleScript)
osascript -e 'display notification "MacBook Turbo installed to Desktop!" with title "Installation Complete" sound name "Glass"' 2>/dev/null || true

echo "Starting MacBook Turbo..."
open "$HOME/Desktop/MacBookTurbo.app"

echo ""
echo "🎉 Done! Look for the CPU indicator in your menu bar (top right)."
echo ""
echo "Press any key to close this window..."
read -n 1
