#!/usr/bin/env python3
"""
Enhanced CPU Monitor Menu Bar App v2.0
Complete system monitoring with intelligent cleanup

Features:
- CPU monitoring with color-coded indicators
- Memory pressure monitoring (macOS specific)
- Thermal throttle detection
- Intelligent process scoring and cleanup
- Disk cache cleanup
- Dry-run mode for preview
- Auto-cleanup with configurable thresholds
- Process protection for development workflows
"""

import subprocess
import os
import sys
import time
import threading
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

# Try to install dependencies if needed
try:
    import rumps
    import psutil
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rumps", "psutil"])
    import rumps
    import psutil

# Add modules directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(SCRIPT_DIR, 'modules')
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

# Import custom modules
try:
    from process_scorer import ProcessScorer, ProcessInfo
    from thermal_monitor import ThermalMonitor, ThermalState, ThrottleState
    from memory_monitor import MemoryMonitor, MemoryPressure, SwapState
    from disk_cleaner import DiskCleaner, CleanupCategory
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    print("Some features may be unavailable")
    ProcessScorer = None
    ThermalMonitor = None
    MemoryMonitor = None
    DiskCleaner = None


class AutoCleanMode(Enum):
    """Auto-cleanup mode settings"""
    OFF = "off"
    CONSERVATIVE = "conservative"  # Only when critical
    BALANCED = "balanced"          # Default behavior
    AGGRESSIVE = "aggressive"      # Proactive cleanup


@dataclass
class SystemStatus:
    """Combined system status"""
    cpu_percent: float
    memory_percent: float
    memory_pressure: str
    thermal_state: str
    throttle_state: str
    swap_used_gb: float
    disk_free_gb: float
    cleanable_gb: float


class EnhancedCPUMonitorApp(rumps.App):
    """
    Enhanced CPU Monitor with intelligent system optimization

    Features:
    - Multi-metric monitoring (CPU, Memory, Thermal, Disk)
    - Smart process cleanup with protection
    - Thermal throttle detection
    - Memory pressure awareness
    - Disk cache cleanup
    - Configurable auto-cleanup modes
    """

    # Thresholds for auto-cleanup
    THRESHOLDS = {
        AutoCleanMode.CONSERVATIVE: {
            'cpu': 90, 'memory': 95, 'thermal': ThermalState.CRITICAL
        },
        AutoCleanMode.BALANCED: {
            'cpu': 70, 'memory': 85, 'thermal': ThermalState.HOT
        },
        AutoCleanMode.AGGRESSIVE: {
            'cpu': 50, 'memory': 70, 'thermal': ThermalState.WARM
        },
    }

    def __init__(self):
        super(EnhancedCPUMonitorApp, self).__init__("CPU", quit_button=None)
        self.icon = None

        # Initialize monitors
        self.process_scorer = ProcessScorer() if ProcessScorer else None
        self.thermal_monitor = ThermalMonitor() if ThermalMonitor else None
        self.memory_monitor = MemoryMonitor() if MemoryMonitor else None
        self.disk_cleaner = DiskCleaner() if DiskCleaner else None

        # State
        self.auto_clean_mode = AutoCleanMode.OFF
        self.last_clean_time = 0
        self.cooldown_seconds = 180  # 3 minute cooldown
        self.show_detailed = False
        self.last_status: Optional[SystemStatus] = None

        # Build menu
        self._build_menu()

        # Start update timer (2 second interval)
        self.timer = rumps.Timer(self.update_status, 2)
        self.timer.start()

        # Start thermal monitoring in background (less frequent)
        self.thermal_timer = rumps.Timer(self.update_thermal, 10)
        self.thermal_timer.start()

    def _build_menu(self):
        """Build the menu structure"""
        # Store references for items that need updating
        self.cpu_item = rumps.MenuItem("CPU: Loading...", callback=None)
        self.mem_item = rumps.MenuItem("Memory: Loading...", callback=None)
        self.thermal_item = rumps.MenuItem("Thermal: Loading...", callback=None)
        self.disk_item = rumps.MenuItem("Disk: Loading...", callback=None)

        # Build cleanup submenu
        cleanup_menu = rumps.MenuItem("🧹 Cleanup")
        cleanup_menu.add(rumps.MenuItem("🚀 Quick Cleanup (Processes)", callback=self.run_process_cleanup))
        cleanup_menu.add(rumps.MenuItem("🗑️ Clean Caches", callback=self.run_cache_cleanup))
        cleanup_menu.add(rumps.MenuItem("🧼 Deep Clean (All)", callback=self.run_deep_cleanup))
        cleanup_menu.add(rumps.MenuItem("👁️ Preview Cleanup (Dry Run)", callback=self.preview_cleanup))

        # Build analysis submenu
        analysis_menu = rumps.MenuItem("🔍 Analysis")
        analysis_menu.add(rumps.MenuItem("📈 Top Processes", callback=self.show_top_processes))
        analysis_menu.add(rumps.MenuItem("🛡️ Protected Processes", callback=self.show_protected))
        analysis_menu.add(rumps.MenuItem("⚠️ Killable Processes", callback=self.show_killable))
        analysis_menu.add(rumps.MenuItem("🔥 Thermal Status", callback=self.show_thermal_details))
        analysis_menu.add(rumps.MenuItem("💾 Memory Details", callback=self.show_memory_details))
        analysis_menu.add(rumps.MenuItem("📊 Disk Analysis", callback=self.show_disk_analysis))

        # Build auto-clean submenu
        automode_menu = rumps.MenuItem("⚙️ Auto-Clean Mode")
        self.mode_off = rumps.MenuItem("Off", callback=lambda _: self.set_auto_mode(AutoCleanMode.OFF))
        self.mode_conservative = rumps.MenuItem("Conservative", callback=lambda _: self.set_auto_mode(AutoCleanMode.CONSERVATIVE))
        self.mode_balanced = rumps.MenuItem("Balanced", callback=lambda _: self.set_auto_mode(AutoCleanMode.BALANCED))
        self.mode_aggressive = rumps.MenuItem("Aggressive", callback=lambda _: self.set_auto_mode(AutoCleanMode.AGGRESSIVE))
        automode_menu.add(self.mode_off)
        automode_menu.add(self.mode_conservative)
        automode_menu.add(self.mode_balanced)
        automode_menu.add(self.mode_aggressive)
        # Mark current mode
        self.mode_off.state = 1  # Default is OFF

        # Build main menu
        self.menu = [
            rumps.MenuItem("📊 System Status", callback=None),
            self.cpu_item,
            self.mem_item,
            self.thermal_item,
            self.disk_item,
            None,  # Separator
            cleanup_menu,
            analysis_menu,
            automode_menu,
            None,  # Separator
            rumps.MenuItem("👁️ Toggle Detailed View", callback=self.toggle_detailed),
            None,  # Separator
            rumps.MenuItem("Quit", callback=rumps.quit_application),
        ]

    def update_status(self, _):
        """Update CPU and memory stats"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memory
            mem = psutil.virtual_memory()
            memory_percent = mem.percent

            # Memory pressure (if available)
            memory_pressure = "unknown"
            if self.memory_monitor:
                try:
                    mem_stats = self.memory_monitor.get_stats()
                    memory_pressure = mem_stats.pressure.value
                except:
                    pass

            # Disk
            disk_free_gb = 0
            cleanable_gb = 0
            if self.disk_cleaner:
                try:
                    disk_usage = self.disk_cleaner.get_disk_usage()
                    disk_free_gb = disk_usage['free'] / (1024**3)
                except:
                    pass

            # Color code the CPU percentage
            if cpu_percent > 80:
                cpu_emoji = "🔴"
            elif cpu_percent > 50:
                cpu_emoji = "🟡"
            else:
                cpu_emoji = "🟢"

            # Memory pressure indicator
            if memory_pressure == "critical":
                mem_emoji = "🔴"
            elif memory_pressure == "warn":
                mem_emoji = "🟡"
            else:
                mem_emoji = "🟢"

            # Update menu bar title
            if self.show_detailed:
                self.title = f"{cpu_emoji}{cpu_percent:.0f}% {mem_emoji}{memory_percent:.0f}%"
            else:
                self.title = f"{cpu_emoji} {cpu_percent:.0f}%"

            # Update menu items using stored references
            self.cpu_item.title = f"CPU: {cpu_percent:.1f}% {cpu_emoji}"
            self.mem_item.title = f"Memory: {memory_percent:.1f}% ({mem.used / (1024**3):.1f}GB) {mem_emoji}"
            self.disk_item.title = f"Disk Free: {disk_free_gb:.1f}GB"

            # Store status
            self.last_status = SystemStatus(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_pressure=memory_pressure,
                thermal_state="unknown",
                throttle_state="unknown",
                swap_used_gb=psutil.swap_memory().used / (1024**3),
                disk_free_gb=disk_free_gb,
                cleanable_gb=cleanable_gb
            )

            # Check auto-cleanup triggers
            self._check_auto_cleanup(cpu_percent, memory_percent, memory_pressure)

        except Exception as e:
            self.title = "CPU: Error"
            print(f"Update error: {e}")

    def update_thermal(self, _):
        """Update thermal status (less frequent)"""
        if not self.thermal_monitor:
            self.thermal_item.title = "Thermal: N/A"
            return

        try:
            status = self.thermal_monitor.get_status(include_sensors=False)

            thermal_emoji = self.thermal_monitor.get_temperature_emoji(status.cpu_state)
            throttle_emoji = self.thermal_monitor.get_throttle_emoji(status.throttle_state)

            if status.cpu_temp > 0:
                thermal_text = f"Thermal: {status.cpu_temp:.0f}°C {thermal_emoji}"
                if status.throttle_state != ThrottleState.NONE:
                    thermal_text += f" {throttle_emoji}"
            else:
                thermal_text = f"Thermal: {status.cpu_state.value} {thermal_emoji}"

            self.thermal_item.title = thermal_text

            if self.last_status:
                self.last_status.thermal_state = status.cpu_state.value
                self.last_status.throttle_state = status.throttle_state.value

        except Exception as e:
            print(f"Thermal update error: {e}")

    def _check_auto_cleanup(self, cpu: float, memory: float, pressure: str):
        """Check if auto-cleanup should trigger"""
        if self.auto_clean_mode == AutoCleanMode.OFF:
            return

        # Check cooldown
        if time.time() - self.last_clean_time < self.cooldown_seconds:
            return

        thresholds = self.THRESHOLDS[self.auto_clean_mode]
        should_clean = False
        reason = ""

        # Check CPU
        if cpu > thresholds['cpu']:
            should_clean = True
            reason = f"CPU at {cpu:.0f}%"

        # Check memory
        if memory > thresholds['memory']:
            should_clean = True
            reason = f"Memory at {memory:.0f}%"

        # Check memory pressure
        if pressure == "critical":
            should_clean = True
            reason = "Critical memory pressure"
        elif pressure == "warn" and self.auto_clean_mode == AutoCleanMode.AGGRESSIVE:
            should_clean = True
            reason = "Memory pressure warning"

        if should_clean:
            self._run_auto_cleanup(reason)

    def _run_auto_cleanup(self, reason: str):
        """Run automatic cleanup"""
        self.last_clean_time = time.time()

        rumps.notification(
            "Auto-Cleanup",
            f"Triggered: {reason}",
            f"Mode: {self.auto_clean_mode.value}"
        )

        # Run in background thread
        thread = threading.Thread(target=self._background_cleanup, args=(reason,))
        thread.daemon = True
        thread.start()

    def _background_cleanup(self, reason: str):
        """Background cleanup worker"""
        try:
            killed = 0

            if self.process_scorer:
                # Get killable processes
                killable = self.process_scorer.get_killable_processes(
                    min_score=30 if self.auto_clean_mode == AutoCleanMode.AGGRESSIVE else 50,
                    min_cpu=20 if self.auto_clean_mode == AutoCleanMode.AGGRESSIVE else 30
                )

                # Kill top offenders
                for proc in killable[:5]:  # Limit to 5 processes
                    if self.process_scorer.kill_process_gracefully(proc.pid):
                        killed += 1

            # Notify result
            if killed > 0:
                rumps.notification(
                    "Auto-Cleanup Complete",
                    f"Cleaned {killed} processes",
                    f"Reason: {reason}"
                )

        except Exception as e:
            print(f"Background cleanup error: {e}")

    def run_process_cleanup(self, _):
        """Manual process cleanup"""
        rumps.notification("Process Cleanup", "Starting...", "Analyzing processes")

        try:
            killed = 0
            protected = 0

            if self.process_scorer:
                killable = self.process_scorer.get_killable_processes(min_score=30, min_cpu=20)

                for proc in killable[:10]:
                    if self.process_scorer.kill_process_gracefully(proc.pid):
                        killed += 1
                    else:
                        protected += 1

            if killed > 0:
                rumps.notification(
                    "Process Cleanup",
                    "Complete",
                    f"Terminated {killed} processes, {protected} protected"
                )
            else:
                rumps.notification(
                    "Process Cleanup",
                    "Complete",
                    "No killable processes found"
                )

        except Exception as e:
            rumps.notification("Process Cleanup", "Error", str(e))

    def run_cache_cleanup(self, _):
        """Clean caches and temporary files"""
        if not self.disk_cleaner:
            rumps.notification("Cache Cleanup", "Error", "Disk cleaner not available")
            return

        rumps.notification("Cache Cleanup", "Starting...", "This may take a moment")

        try:
            # Run cleanup in background
            thread = threading.Thread(target=self._background_cache_cleanup)
            thread.daemon = True
            thread.start()

        except Exception as e:
            rumps.notification("Cache Cleanup", "Error", str(e))

    def _background_cache_cleanup(self):
        """Background cache cleanup worker"""
        try:
            results = self.disk_cleaner.clean(
                categories=[
                    CleanupCategory.USER_CACHE,
                    CleanupCategory.BROWSER_CACHE,
                    CleanupCategory.DEV_CACHE,
                    CleanupCategory.TEMP_FILES,
                ],
                dry_run=False
            )

            total_freed = sum(r.bytes_freed for r in results)
            total_files = sum(r.files_deleted for r in results)

            # Also clean DNS cache
            self.disk_cleaner.clean_dns_cache()

            rumps.notification(
                "Cache Cleanup",
                "Complete",
                f"Freed {self.disk_cleaner.format_size(total_freed)}, {total_files} files"
            )

        except Exception as e:
            rumps.notification("Cache Cleanup", "Error", str(e))

    def run_deep_cleanup(self, _):
        """Run comprehensive cleanup"""
        rumps.notification("Deep Clean", "Starting...", "Cleaning processes and caches")

        try:
            thread = threading.Thread(target=self._background_deep_cleanup)
            thread.daemon = True
            thread.start()

        except Exception as e:
            rumps.notification("Deep Clean", "Error", str(e))

    def _background_deep_cleanup(self):
        """Background deep cleanup worker"""
        results = []

        # Process cleanup
        killed = 0
        if self.process_scorer:
            killable = self.process_scorer.get_killable_processes(min_score=25, min_cpu=15)
            for proc in killable[:10]:
                if self.process_scorer.kill_process_gracefully(proc.pid):
                    killed += 1
        results.append(f"Processes: {killed}")

        # Cache cleanup
        if self.disk_cleaner:
            cache_results = self.disk_cleaner.clean(dry_run=False)
            total_freed = sum(r.bytes_freed for r in cache_results)
            results.append(f"Disk: {self.disk_cleaner.format_size(total_freed)}")

            # DNS cache
            self.disk_cleaner.clean_dns_cache()
            results.append("DNS: flushed")

        rumps.notification(
            "Deep Clean",
            "Complete",
            " | ".join(results)
        )

    def preview_cleanup(self, _):
        """Preview what would be cleaned (dry run)"""
        if not self.disk_cleaner and not self.process_scorer:
            rumps.alert("Preview", "Monitoring modules not available")
            return

        msg = "🔍 CLEANUP PREVIEW (Dry Run)\n"
        msg += "=" * 40 + "\n\n"

        # Process preview
        if self.process_scorer:
            killable = self.process_scorer.get_killable_processes(min_score=30, min_cpu=20)
            if killable:
                msg += "⚠️ KILLABLE PROCESSES:\n"
                for proc in killable[:5]:
                    msg += f"   {proc.name}: {proc.cpu_percent:.1f}% CPU (score: {proc.kill_score:.0f})\n"
            else:
                msg += "✅ No killable processes\n"
            msg += "\n"

        # Cache preview
        if self.disk_cleaner:
            results = self.disk_cleaner.clean(
                categories=[
                    CleanupCategory.USER_CACHE,
                    CleanupCategory.BROWSER_CACHE,
                    CleanupCategory.DEV_CACHE,
                ],
                dry_run=True
            )
            total = sum(r.bytes_freed for r in results if not r.skipped)
            msg += f"🗑️ CLEANABLE CACHES:\n"
            msg += f"   Total: {self.disk_cleaner.format_size(total)}\n"

            # Show by category
            by_category = {}
            for r in results:
                if r.bytes_freed > 0:
                    cat = r.category.value
                    by_category[cat] = by_category.get(cat, 0) + r.bytes_freed

            for cat, size in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                msg += f"   {cat}: {self.disk_cleaner.format_size(size)}\n"

        rumps.alert("Cleanup Preview", msg)

    def show_top_processes(self, _):
        """Show top CPU processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] > 1:
                        processes.append(info)
                except:
                    pass

            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            top = processes[:10]

            msg = "🔝 TOP CPU PROCESSES\n"
            msg += "=" * 40 + "\n\n"

            for p in top:
                name = p['name'][:25]
                msg += f"{name:25s}  CPU: {p['cpu_percent']:5.1f}%  MEM: {p['memory_percent']:5.1f}%\n"

            rumps.alert("Top Processes", msg)

        except Exception as e:
            rumps.alert("Error", f"Could not get processes: {e}")

    def show_protected(self, _):
        """Show protected processes"""
        if not self.process_scorer:
            rumps.alert("Protected Processes", "Process scorer not available")
            return

        try:
            all_procs = self.process_scorer.get_all_processes(min_cpu=1)
            protected = [p for p in all_procs if p.is_protected][:15]

            msg = "🛡️ PROTECTED PROCESSES\n"
            msg += "(Will NOT be killed)\n"
            msg += "=" * 40 + "\n\n"

            for p in protected:
                msg += f"{p.name[:25]:25s}  {p.category.value}\n"

            msg += f"\n Total protected: {len([p for p in all_procs if p.is_protected])}"

            rumps.alert("Protected Processes", msg)

        except Exception as e:
            rumps.alert("Error", str(e))

    def show_killable(self, _):
        """Show killable processes"""
        if not self.process_scorer:
            rumps.alert("Killable Processes", "Process scorer not available")
            return

        try:
            killable = self.process_scorer.get_killable_processes(min_score=20, min_cpu=10)

            msg = "⚠️ KILLABLE PROCESSES\n"
            msg += "(Can be safely terminated)\n"
            msg += "=" * 40 + "\n\n"

            if killable:
                for p in killable[:10]:
                    msg += f"{p.name[:20]:20s}  CPU:{p.cpu_percent:5.1f}%  Score:{p.kill_score:5.1f}\n"
            else:
                msg += "No killable processes found\n"

            rumps.alert("Killable Processes", msg)

        except Exception as e:
            rumps.alert("Error", str(e))

    def show_thermal_details(self, _):
        """Show detailed thermal information"""
        if not self.thermal_monitor:
            rumps.alert("Thermal Status", "Thermal monitor not available")
            return

        try:
            status = self.thermal_monitor.get_status(include_sensors=True)

            msg = "🌡️ THERMAL STATUS\n"
            msg += "=" * 40 + "\n\n"

            msg += f"CPU Temperature: {status.cpu_temp:.1f}°C {self.thermal_monitor.get_temperature_emoji(status.cpu_state)}\n"
            if status.gpu_temp:
                msg += f"GPU Temperature: {status.gpu_temp:.1f}°C\n"
            if status.battery_temp:
                msg += f"Battery Temp:    {status.battery_temp:.1f}°C\n"

            msg += f"\nThermal State:   {status.cpu_state.value}\n"
            msg += f"Throttle State:  {status.throttle_state.value} {self.thermal_monitor.get_throttle_emoji(status.throttle_state)}\n"

            if status.fan_speeds:
                msg += f"\n🌀 Fan Speeds:\n"
                for fan, rpm in status.fan_speeds.items():
                    msg += f"   {fan}: {rpm} RPM\n"

            if status.recommendations:
                msg += f"\n💡 Recommendations:\n"
                for rec in status.recommendations[:3]:
                    msg += f"   {rec}\n"

            rumps.alert("Thermal Status", msg)

        except Exception as e:
            rumps.alert("Error", str(e))

    def show_memory_details(self, _):
        """Show detailed memory information"""
        if not self.memory_monitor:
            rumps.alert("Memory Details", "Memory monitor not available")
            return

        try:
            stats = self.memory_monitor.get_stats()

            msg = "💾 MEMORY STATUS\n"
            msg += "=" * 40 + "\n\n"

            msg += f"Total:       {self.memory_monitor.format_bytes(stats.total)}\n"
            msg += f"Used:        {self.memory_monitor.format_bytes(stats.used)} ({stats.percent_used:.1f}%)\n"
            msg += f"Available:   {self.memory_monitor.format_bytes(stats.available)}\n"
            msg += f"\n"
            msg += f"App Memory:  {self.memory_monitor.format_bytes(stats.app_memory)}\n"
            msg += f"Wired:       {self.memory_monitor.format_bytes(stats.wired)}\n"
            msg += f"Compressed:  {self.memory_monitor.format_bytes(stats.compressed)}\n"
            msg += f"\n"
            msg += f"Pressure:    {stats.pressure.value} {self.memory_monitor.get_pressure_emoji(stats.pressure)}\n"
            msg += f"Swap Used:   {self.memory_monitor.format_bytes(stats.swap_used)} {self.memory_monitor.get_swap_emoji(stats.swap_state)}\n"

            # Top memory processes
            msg += f"\n🔝 Top Memory Users:\n"
            for proc in self.memory_monitor.get_top_memory_processes(5):
                msg += f"   {proc.name[:18]:18s} {self.memory_monitor.format_bytes(proc.rss):>8s}\n"

            rumps.alert("Memory Details", msg)

        except Exception as e:
            rumps.alert("Error", str(e))

    def show_disk_analysis(self, _):
        """Show disk usage analysis"""
        if not self.disk_cleaner:
            rumps.alert("Disk Analysis", "Disk cleaner not available")
            return

        try:
            usage = self.disk_cleaner.get_disk_usage()
            analysis = self.disk_cleaner.analyze()

            msg = "💿 DISK ANALYSIS\n"
            msg += "=" * 40 + "\n\n"

            msg += f"Total:  {usage['total_formatted']}\n"
            msg += f"Used:   {usage['used_formatted']} ({usage['percent_used']:.1f}%)\n"
            msg += f"Free:   {usage['free_formatted']}\n"
            msg += f"\n"

            msg += "🗑️ CLEANABLE BY CATEGORY:\n"
            total_cleanable = 0
            for category, size in sorted(analysis.items(), key=lambda x: x[1], reverse=True):
                if size > 0:
                    msg += f"   {category.value:15s}: {self.disk_cleaner.format_size(size)}\n"
                    total_cleanable += size

            msg += f"\n   {'TOTAL':15s}: {self.disk_cleaner.format_size(total_cleanable)}\n"

            rumps.alert("Disk Analysis", msg)

        except Exception as e:
            rumps.alert("Error", str(e))

    def set_auto_mode(self, mode: AutoCleanMode):
        """Set auto-cleanup mode"""
        self.auto_clean_mode = mode

        # Update menu checkmarks using stored references
        self.mode_off.state = False
        self.mode_conservative.state = False
        self.mode_balanced.state = False
        self.mode_aggressive.state = False

        if mode == AutoCleanMode.OFF:
            self.mode_off.state = True
        elif mode == AutoCleanMode.CONSERVATIVE:
            self.mode_conservative.state = True
        elif mode == AutoCleanMode.BALANCED:
            self.mode_balanced.state = True
        elif mode == AutoCleanMode.AGGRESSIVE:
            self.mode_aggressive.state = True

        rumps.notification(
            "Auto-Clean Mode",
            f"Set to: {mode.value}",
            f"Thresholds: CPU>{self.THRESHOLDS.get(mode, {}).get('cpu', 'N/A')}%, Memory>{self.THRESHOLDS.get(mode, {}).get('memory', 'N/A')}%"
            if mode != AutoCleanMode.OFF else "Auto-cleanup disabled"
        )

    def toggle_detailed(self, _):
        """Toggle detailed view in menu bar"""
        self.show_detailed = not self.show_detailed
        rumps.notification(
            "Display Mode",
            "Detailed view" if self.show_detailed else "Simple view",
            "Menu bar display updated"
        )


def main():
    """Main entry point"""
    print("=" * 50)
    print("Enhanced CPU Monitor v2.0")
    print("=" * 50)
    print("\nInitializing monitors...")

    app = EnhancedCPUMonitorApp()

    print("Starting menu bar app...")
    print("Check your menu bar for the CPU indicator")
    print("\nFeatures:")
    print("  - CPU/Memory/Thermal monitoring")
    print("  - Intelligent process cleanup")
    print("  - Cache cleanup")
    print("  - Auto-cleanup modes")
    print("  - Dry-run preview")
    print("\nPress Ctrl+C to stop\n")

    app.run()


if __name__ == "__main__":
    main()
