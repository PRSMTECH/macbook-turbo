#!/usr/bin/env python3

"""
Enhanced CPU Monitor Menu Bar App
Shows CPU percentage with color indicators and quick actions
"""

import subprocess
import os
import sys
import time

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Try to install dependencies if needed
try:
    import rumps
    import psutil
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rumps", "psutil"])
    import rumps
    import psutil

class CPUMonitorApp(rumps.App):
    def __init__(self):
        super(CPUMonitorApp, self).__init__("CPU", quit_button=None)
        self.icon = None
        self.timer = rumps.Timer(self.update_cpu, 2)
        self.timer.start()

        # Store menu item references for reliable updates
        self.cpu_item = rumps.MenuItem("CPU: Loading...", callback=None)
        self.mem_item = rumps.MenuItem("Memory: Loading...", callback=None)

        # Build menu using stored references
        self.menu = [
            self.cpu_item,
            self.mem_item,
            rumps.separator,
            rumps.MenuItem("🧹 Run Cleanup Now", callback=self.run_cleanup),
            rumps.MenuItem("📊 Check Protection Status", callback=self.check_status),
            rumps.MenuItem("🔍 Show Top Processes", callback=self.show_top),
            rumps.separator,
            rumps.MenuItem("⚙️ Auto-Clean (>70%)", callback=self.toggle_auto),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

        self.auto_clean = False
        self.last_clean_time = 0

    def update_cpu(self, _):
        """Update CPU and memory stats"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()

            # Color code the CPU percentage
            if cpu_percent > 80:
                emoji = "🔴"
            elif cpu_percent > 50:
                emoji = "🟡"
            else:
                emoji = "🟢"

            # Update menu bar title
            self.title = f"{emoji} {cpu_percent:.0f}%"

            # Update menu items using stored references
            self.cpu_item.title = f"CPU: {cpu_percent:.1f}%"
            self.mem_item.title = f"Memory: {mem.percent:.1f}% ({mem.used / (1024**3):.1f}GB used)"

            # Auto-clean if enabled and CPU is high
            if self.auto_clean and cpu_percent > 70:
                current_time = time.time()
                if current_time - self.last_clean_time > 180:  # 3 min cooldown
                    self.run_cleanup(None)
                    self.last_clean_time = current_time

        except Exception as e:
            self.title = "CPU: Error"

    def run_cleanup(self, _):
        """Run the CPU cleanup script"""
        rumps.notification("CPU Cleanup", "Running...", "Cleaning up high CPU processes")

        try:
            cleanup_script = os.path.join(SCRIPT_DIR, "cpu-cleanup-enhanced.sh")
            result = subprocess.run(
                ["/bin/bash", cleanup_script],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Count processes killed from output
                killed_count = result.stdout.count("✅ Killed:")
                if killed_count > 0:
                    rumps.notification("CPU Cleanup", "Complete", f"Terminated {killed_count} processes")
                else:
                    rumps.notification("CPU Cleanup", "Complete", "No high CPU processes found")
            else:
                rumps.notification("CPU Cleanup", "Warning", "Some processes could not be cleaned")

        except subprocess.TimeoutExpired:
            rumps.notification("CPU Cleanup", "Timeout", "Cleanup took too long")
        except Exception as e:
            rumps.notification("CPU Cleanup", "Error", str(e))

    def check_status(self, _):
        """Check protection status"""
        try:
            status_script = os.path.join(SCRIPT_DIR, "check-protection-status.sh")
            result = subprocess.run(
                ["/bin/bash", status_script],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse output for protected process count
            protected_count = 0
            for line in result.stdout.split('\n'):
                if "protected processes are running" in line.lower():
                    words = line.split()
                    for word in words:
                        if word.isdigit():
                            protected_count = int(word)
                            break

            rumps.notification(
                "Protection Status",
                f"{protected_count} Protected Processes",
                "Your development tools are safe from cleanup"
            )

        except Exception as e:
            rumps.notification("Protection Status", "Error", str(e))

    def show_top(self, _):
        """Show top CPU processes in an alert"""
        try:
            # Get top processes
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] > 1:  # Only show processes using >1% CPU
                        processes.append((info['name'][:30], info['cpu_percent']))
                except:
                    pass

            # Sort and get top 10
            processes.sort(key=lambda x: x[1], reverse=True)
            top_procs = processes[:10]

            # Format message
            msg = "Top CPU Processes:\n\n"
            for name, cpu in top_procs:
                msg += f"{name}: {cpu:.1f}%\n"

            rumps.alert("Top Processes", msg)

        except Exception as e:
            rumps.alert("Error", f"Could not get processes: {e}")

    def toggle_auto(self, sender):
        """Toggle auto-cleanup"""
        self.auto_clean = not self.auto_clean
        sender.state = self.auto_clean

        if self.auto_clean:
            rumps.notification(
                "Auto-Clean Enabled",
                "Monitoring CPU Usage",
                "Will clean when CPU exceeds 70%"
            )
        else:
            rumps.notification(
                "Auto-Clean Disabled",
                "Manual Mode",
                "Use menu to run cleanup"
            )

if __name__ == "__main__":
    app = CPUMonitorApp()
    app.run()