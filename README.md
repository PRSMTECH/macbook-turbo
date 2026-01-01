<div align="center">

# 🚀 MacBook Turbo

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=4000&pause=1000&color=00D4FF&center=true&vCenter=true&width=600&lines=Keep+Your+Mac+Running+Fast;Real-Time+CPU+%26+Memory+Monitoring;Smart+Process+Management;Developer-Friendly+Optimization" alt="Typing SVG" />

<br/>

![macOS](https://img.shields.io/badge/macOS-Sonoma%20%7C%20Ventura%20%7C%20Monterey-000000?style=for-the-badge&logo=apple&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00D4FF?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/PRSMTECH/macbook-turbo/ci.yml?style=for-the-badge&label=CI&color=00D4FF)
![Version](https://img.shields.io/badge/Version-1.0.0-FF6B6B?style=for-the-badge)

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=24&height=2&section=header" width="100%"/>

**Intelligent macOS System Optimizer & CPU Monitor**

*Your Mac's performance guardian — monitors, protects, and optimizes automatically*

[🚀 Quick Start](#-super-easy-install-just-copy--paste) • [📖 How It Works](#-how-it-works) • [✨ Features](#-features) • [❓ FAQ](#-frequently-asked-questions)

</div>

---

## 🎯 What Does MacBook Turbo Do?

**MacBook Turbo** is like having a smart assistant that:

| It Does This | So You Get This |
|-------------|-----------------|
| 👀 **Watches your CPU usage** | Know when your Mac is working hard |
| 🧹 **Cleans up junk files** | Free up disk space automatically |
| 🛡️ **Protects your work apps** | Never kills VS Code, Terminal, etc. |
| 🌡️ **Monitors temperature** | Prevents overheating issues |
| 📊 **Shows status in menu bar** | Always know your Mac's health |

---

## 🚀 Super Easy Install (Just Copy & Paste!)

### Step 1: Open Terminal

**Don't know how to open Terminal?** Here's how:

1. Press `Cmd + Space` (opens Spotlight)
2. Type `Terminal`
3. Press `Enter`

You'll see a window with a blinking cursor — that's Terminal!

### Step 2: Copy and Paste This Command

```bash
curl -fsSL https://raw.githubusercontent.com/PRSMTECH/macbook-turbo/main/install.sh | bash
```

**How to paste:**
- Click in the Terminal window
- Press `Cmd + V` to paste
- Press `Enter` to run

### Step 3: Watch the Magic! ✨

The installer will:
```
✅ Check your Mac is compatible
✅ Download MacBook Turbo
✅ Install everything automatically
✅ Ask if you want it to start automatically
```

### Step 4: Look at Your Menu Bar!

After installation, look at the **top right of your screen** (the menu bar).

You'll see something like: **🟢 25%** or **🟡 65%** or **🔴 85%**

That's MacBook Turbo showing your CPU usage!

---

## 🎨 What the Colors Mean

| What You See | What It Means | Should You Worry? |
|-------------|---------------|-------------------|
| 🟢 **Green (0-50%)** | Your Mac is running great | Nope! All good |
| 🟡 **Yellow (50-80%)** | Working a bit hard | Keep an eye on it |
| 🔴 **Red (80-100%)** | Working very hard | Maybe close some apps |

---

## 📖 How It Works

<details>
<summary><strong>🖱️ Click here to see the step-by-step explanation</strong></summary>

### The Menu Bar App

1. **Always Running** — Sits quietly in your menu bar
2. **Updates Every 3 Seconds** — Shows real-time CPU percentage
3. **Click for Options** — Click the icon for a menu of actions

### What Happens When You Click It?

```
┌─────────────────────────────┐
│  🔄 Refresh Status          │  ← Update the display
│  🧹 Run Cleanup             │  ← Clean junk files
│  📊 System Status           │  ← See detailed info
│  ⚙️  Auto-Cleanup Mode      │  ← Set automatic cleanup
│  ℹ️  About                   │  ← Version info
│  ❌ Quit                     │  ← Close the app
└─────────────────────────────┘
```

### The Smart Cleanup

When you run cleanup, MacBook Turbo:

1. **Finds junk files** in 30+ locations (caches, logs, temp files)
2. **Calculates what's safe to delete**
3. **Shows you how much space you'll free up**
4. **Deletes only what's safe**

### Developer Protection (The Cool Part!)

MacBook Turbo **never** messes with your work:

```
✅ Protected Apps:
   • VS Code, Cursor, Xcode
   • Terminal, iTerm2
   • Node.js, Python, Docker
   • Git, npm, yarn
   • And 30+ more developer tools!
```

</details>

---

## ✨ Features

<details>
<summary><strong>🖥️ Menu Bar Monitor</strong></summary>

Real-time system status right in your menu bar:

- CPU percentage with color indicator
- Click to access all features
- Minimal resource usage (~15-25 MB)
- Updates every 3 seconds

</details>

<details>
<summary><strong>🧹 Smart Disk Cleanup</strong></summary>

Automatically finds and cleans:

| Location | What It Cleans |
|----------|---------------|
| `~/Library/Caches` | App caches |
| `/tmp` | Temporary files |
| `~/.Trash` | Emptied trash |
| Browser caches | Chrome, Safari, Firefox |
| Xcode derived data | Build files |
| npm/pip caches | Package caches |

**First run typically frees 5-25 GB!**

</details>

<details>
<summary><strong>🛡️ Developer Protection</strong></summary>

Uses a **multi-factor scoring algorithm**:

```
Score = (CPU × 0.4) + (Memory × 0.3) + (FDs × 0.1) + (Age × 0.1) + (Category × 0.1)
```

Protected categories:
- **IDEs**: VS Code, Cursor, Xcode, IntelliJ, PyCharm
- **Terminals**: Terminal.app, iTerm2, Hyper, Alacritty
- **Dev Tools**: Node, Python, Docker, Git
- **Shells**: zsh, bash, fish

</details>

<details>
<summary><strong>🌡️ Thermal Monitoring</strong></summary>

Monitors your Mac's temperature to:
- Detect throttling
- Warn before overheating
- Track CPU/GPU temps

</details>

<details>
<summary><strong>⚡ Auto-Cleanup Modes</strong></summary>

| Mode | When It Cleans |
|------|---------------|
| **OFF** | Only when you ask |
| **CONSERVATIVE** | CPU > 90% or Memory > 95% |
| **BALANCED** | CPU > 70% or Memory > 85% |
| **AGGRESSIVE** | CPU > 50% or Memory > 70% |

</details>

---

## 🛠️ Manual Installation

<details>
<summary><strong>Click if you prefer to install manually</strong></summary>

### Prerequisites

First, check you have Python:
```bash
python3 --version
```

**Don't have Python?** Install with Homebrew:
```bash
# Install Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/PRSMTECH/macbook-turbo.git ~/macbook-turbo

# 2. Go to the folder
cd ~/macbook-turbo

# 3. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app!
python cpu-menubar-enhanced.py
```

### Make It Start Automatically

```bash
# Copy the LaunchAgent
cp config/com.user.cpumanager.plist ~/Library/LaunchAgents/com.prsmtech.macbookturbo.plist

# Load it
launchctl load ~/Library/LaunchAgents/com.prsmtech.macbookturbo.plist
```

</details>

---

## 🗑️ Uninstall

If you ever want to remove MacBook Turbo:

```bash
~/macbook-turbo/uninstall.sh
```

Or manually:
```bash
pkill -f "cpu-menubar"
launchctl unload ~/Library/LaunchAgents/com.prsmtech.macbookturbo.plist 2>/dev/null
rm -rf ~/macbook-turbo
```

---

## ❓ Frequently Asked Questions

<details>
<summary><strong>Is this safe to use?</strong></summary>

**Yes!** MacBook Turbo:
- Only deletes cache/temp files that are safe to remove
- Never touches your documents, photos, or important files
- Protects all developer tools automatically
- Is open source — you can read all the code

</details>

<details>
<summary><strong>Will this slow down my Mac?</strong></summary>

**No!** MacBook Turbo uses:
- Less than 1% CPU when monitoring
- Only 15-25 MB of memory
- No background processes except the menu bar app

</details>

<details>
<summary><strong>How do I stop it?</strong></summary>

Click the menu bar icon → Click **Quit**

Or in Terminal:
```bash
pkill -f "cpu-menubar"
```

</details>

<details>
<summary><strong>How do I restart it?</strong></summary>

```bash
cd ~/macbook-turbo
python cpu-menubar-enhanced.py &
```

Or double-click `START-CPU-MONITOR.command` in the folder.

</details>

<details>
<summary><strong>The menu bar icon isn't showing up</strong></summary>

Try these steps:

1. **Check if it's running:**
   ```bash
   ps aux | grep cpu-menubar
   ```

2. **Restart it:**
   ```bash
   pkill -f "cpu-menubar"
   cd ~/macbook-turbo
   source venv/bin/activate
   python cpu-menubar-enhanced.py &
   ```

3. **Check for errors:**
   ```bash
   python cpu-menubar-enhanced.py
   ```

</details>

<details>
<summary><strong>Can I add my own protected apps?</strong></summary>

Yes! Edit `cpu-cleanup-enhanced.sh` and add your apps:

```bash
PROTECTED_PROCESSES="YourApp|AnotherApp"
```

</details>

---

## 📊 Command Line Tools

For power users who want more control:

```bash
# Full system status dashboard
python system-optimizer.py status

# Run disk cleanup
python system-optimizer.py cleanup

# Continuous monitoring mode
python system-optimizer.py monitor

# Deep system analysis
python system-optimizer.py analyze
```

Individual modules:
```bash
python modules/disk_cleaner.py      # Just scan for cleanable files
python modules/thermal_monitor.py   # Just check temperatures
python modules/memory_monitor.py    # Just check memory pressure
python modules/process_scorer.py    # Just score running processes
```

---

## 📁 What's in the Folder

```
macbook-turbo/
├── cpu-menubar-enhanced.py    # 🖥️  The main menu bar app
├── system-optimizer.py        # 🛠️  Command line tool
├── cpu-cleanup-enhanced.sh    # 🧹  The cleanup script
├── install.sh                 # 📦  The installer
├── uninstall.sh              # 🗑️  The uninstaller
├── modules/
│   ├── thermal_monitor.py    # 🌡️  Temperature monitoring
│   ├── memory_monitor.py     # 💾  Memory tracking
│   ├── disk_cleaner.py       # 💿  Disk cleanup
│   └── process_scorer.py     # 📊  Process scoring
└── *.command                  # 🖱️  Double-click launchers
```

---

## 🤝 Contributing

Found a bug? Have an idea? We'd love your help!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/cool-feature`)
3. Commit your changes (`git commit -m 'Add cool feature'`)
4. Push to the branch (`git push origin feature/cool-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — use it however you want!

See the [LICENSE](LICENSE) file for details.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=24&height=2&section=header" width="100%"/>

<br/>

**Built with ❤️ by [PRSMTECH](https://github.com/PRSMTECH)**

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-PRSMTECH-181717?style=for-the-badge&logo=github)](https://github.com/PRSMTECH)

<br/>

*If MacBook Turbo helped you, consider giving it a ⭐ on GitHub!*

</div>
