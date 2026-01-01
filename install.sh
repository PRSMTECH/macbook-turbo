#!/bin/bash

#######################################
# MacBook Turbo - Installation Script
# One-line install: curl -fsSL https://raw.githubusercontent.com/PRSMTECH/macbook-turbo/main/install.sh | bash
#######################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/macbook-turbo"
REPO_URL="https://github.com/PRSMTECH/macbook-turbo.git"
MIN_PYTHON_VERSION="3.9"

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           ${GREEN}MacBook Turbo Installer v1.0.0${BLUE}                 ║${NC}"
echo -e "${BLUE}║     macOS System Optimization with Developer Protection   ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

#######################################
# Pre-flight Checks
#######################################

echo -e "${YELLOW}🔍 Running pre-flight checks...${NC}"

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}❌ Error: MacBook Turbo is designed for macOS only.${NC}"
    exit 1
fi
echo -e "   ${GREEN}✓${NC} macOS detected: $(sw_vers -productVersion)"

# Check for Python 3.9+
check_python_version() {
    local python_cmd=$1
    if command -v "$python_cmd" &> /dev/null; then
        local version=$($python_cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        local major=$(echo "$version" | cut -d. -f1)
        local minor=$(echo "$version" | cut -d. -f2)
        if [[ $major -ge 3 && $minor -ge 9 ]]; then
            echo "$python_cmd"
            return 0
        fi
    fi
    return 1
}

PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3.9 python3 python; do
    if result=$(check_python_version "$cmd"); then
        PYTHON_CMD="$result"
        break
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo -e "${RED}❌ Error: Python 3.9 or higher is required.${NC}"
    echo -e "${YELLOW}   Install Python using Homebrew:${NC}"
    echo -e "   ${BLUE}brew install python@3.11${NC}"
    echo -e ""
    echo -e "${YELLOW}   Or download from:${NC}"
    echo -e "   ${BLUE}https://www.python.org/downloads/${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "   ${GREEN}✓${NC} Python $PYTHON_VERSION found ($PYTHON_CMD)"

# Check for pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}❌ Error: pip is not installed.${NC}"
    echo -e "${YELLOW}   Install pip:${NC}"
    echo -e "   ${BLUE}$PYTHON_CMD -m ensurepip --upgrade${NC}"
    exit 1
fi
echo -e "   ${GREEN}✓${NC} pip available"

# Check for git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Error: git is not installed.${NC}"
    echo -e "${YELLOW}   Install git:${NC}"
    echo -e "   ${BLUE}xcode-select --install${NC}"
    exit 1
fi
echo -e "   ${GREEN}✓${NC} git available"

echo ""

#######################################
# Installation
#######################################

echo -e "${YELLOW}📦 Installing MacBook Turbo...${NC}"

# Check if already installed
if [[ -d "$INSTALL_DIR" ]]; then
    echo -e "${YELLOW}   ⚠️  Existing installation found at $INSTALL_DIR${NC}"
    read -p "   Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "   ${BLUE}Updating existing installation...${NC}"
        cd "$INSTALL_DIR"
        git pull origin main
    else
        echo -e "${YELLOW}   Installation cancelled.${NC}"
        exit 0
    fi
else
    # Clone repository
    echo -e "   ${BLUE}Cloning repository...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo -e "   ${GREEN}✓${NC} Repository ready"

# Create virtual environment
echo -e "   ${BLUE}Creating virtual environment...${NC}"
if [[ ! -d "$INSTALL_DIR/venv" ]]; then
    $PYTHON_CMD -m venv "$INSTALL_DIR/venv"
fi
echo -e "   ${GREEN}✓${NC} Virtual environment created"

# Install dependencies
echo -e "   ${BLUE}Installing dependencies...${NC}"
"$INSTALL_DIR/venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"
echo -e "   ${GREEN}✓${NC} Dependencies installed"

# Make scripts executable
echo -e "   ${BLUE}Making scripts executable...${NC}"
chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true
chmod +x "$INSTALL_DIR"/*.command 2>/dev/null || true
chmod +x "$INSTALL_DIR"/cpu-status 2>/dev/null || true
chmod +x "$INSTALL_DIR"/cpu-clean 2>/dev/null || true
chmod +x "$INSTALL_DIR"/cpu-test 2>/dev/null || true
echo -e "   ${GREEN}✓${NC} Scripts are executable"

echo ""

#######################################
# Create launcher scripts
#######################################

echo -e "${YELLOW}🚀 Creating launcher scripts...${NC}"

# Create a global launcher script
LAUNCHER_SCRIPT="$INSTALL_DIR/launch-macbook-turbo.sh"
cat > "$LAUNCHER_SCRIPT" << 'LAUNCHER'
#!/bin/bash
# MacBook Turbo Launcher
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/cpu-menubar-enhanced.py"
LAUNCHER
chmod +x "$LAUNCHER_SCRIPT"

# Create CLI launcher
CLI_SCRIPT="$INSTALL_DIR/macbook-turbo-cli"
cat > "$CLI_SCRIPT" << 'CLILAUNCHER'
#!/bin/bash
# MacBook Turbo CLI
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/system-optimizer.py" "$@"
CLILAUNCHER
chmod +x "$CLI_SCRIPT"

echo -e "   ${GREEN}✓${NC} Launcher scripts created"

#######################################
# Optional: Add to PATH
#######################################

echo ""
echo -e "${YELLOW}🔧 Optional Setup${NC}"

# Ask about adding to PATH
read -p "   Add macbook-turbo to PATH for easy CLI access? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Detect shell
    if [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.zshrc"
    fi

    # Add to PATH if not already there
    if ! grep -q "macbook-turbo" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# MacBook Turbo" >> "$SHELL_RC"
        echo "export PATH=\"\$HOME/macbook-turbo:\$PATH\"" >> "$SHELL_RC"
        echo -e "   ${GREEN}✓${NC} Added to PATH in $SHELL_RC"
        echo -e "   ${YELLOW}   Run 'source $SHELL_RC' or restart terminal to use 'macbook-turbo-cli'${NC}"
    else
        echo -e "   ${GREEN}✓${NC} Already in PATH"
    fi
fi

# Ask about LaunchAgent (auto-start)
echo ""
read -p "   Set up auto-start on login? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PLIST_DIR="$HOME/Library/LaunchAgents"
    PLIST_FILE="$PLIST_DIR/com.prsmtech.macbookturbo.plist"

    mkdir -p "$PLIST_DIR"

    cat > "$PLIST_FILE" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.prsmtech.macbookturbo</string>
    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/venv/bin/python</string>
        <string>$INSTALL_DIR/cpu-menubar-enhanced.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/macbook-turbo.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/macbook-turbo.err</string>
</dict>
</plist>
PLIST

    # Load the LaunchAgent
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    launchctl load "$PLIST_FILE"

    echo -e "   ${GREEN}✓${NC} Auto-start configured"
    echo -e "   ${YELLOW}   MacBook Turbo will start automatically on login${NC}"
fi

echo ""

#######################################
# Success!
#######################################

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ Installation Complete!                    ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Installed to:${NC} $INSTALL_DIR"
echo ""
echo -e "${YELLOW}🚀 Quick Start:${NC}"
echo ""
echo -e "   ${GREEN}Launch Menu Bar App:${NC}"
echo -e "   ${BLUE}$INSTALL_DIR/launch-macbook-turbo.sh${NC}"
echo ""
echo -e "   ${GREEN}Or double-click in Finder:${NC}"
echo -e "   ${BLUE}$INSTALL_DIR/START-CPU-MONITOR.command${NC}"
echo ""
echo -e "   ${GREEN}CLI Usage:${NC}"
echo -e "   ${BLUE}$INSTALL_DIR/macbook-turbo-cli status${NC}    # Show system status"
echo -e "   ${BLUE}$INSTALL_DIR/macbook-turbo-cli cleanup${NC}   # Run cleanup"
echo -e "   ${BLUE}$INSTALL_DIR/macbook-turbo-cli monitor${NC}   # Live monitoring"
echo ""
echo -e "${YELLOW}📖 Documentation:${NC} https://github.com/PRSMTECH/macbook-turbo"
echo ""
echo -e "${GREEN}Enjoy your turbocharged Mac! 🚀${NC}"
echo ""
