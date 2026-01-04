#!/usr/bin/env python3
"""
System Optimizer - Unified CLI for macOS Performance Optimization
Combines all monitoring and cleanup modules into a single command-line tool

Usage:
    python system-optimizer.py status          # Show system status
    python system-optimizer.py cleanup         # Run smart cleanup
    python system-optimizer.py cleanup --dry-run  # Preview cleanup
    python system-optimizer.py cleanup --aggressive  # Aggressive cleanup
    python system-optimizer.py monitor         # Continuous monitoring
    python system-optimizer.py analyze         # Full system analysis
"""

import argparse
import sys
import os
import time
import signal
from typing import Optional

# Add modules directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(SCRIPT_DIR, 'modules')
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

try:
    import psutil
except ImportError:
    print("Installing psutil...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

# Import modules
try:
    from process_scorer import ProcessScorer
    from thermal_monitor import ThermalMonitor, ThermalState, ThrottleState
    from memory_monitor import MemoryMonitor, MemoryPressure
    from disk_cleaner import DiskCleaner, CleanupCategory
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure modules directory exists with all required files")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


class SystemOptimizer:
    """
    Unified system optimizer combining all monitoring and cleanup capabilities
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.process_scorer = ProcessScorer()
        self.thermal_monitor = ThermalMonitor()
        self.memory_monitor = MemoryMonitor()
        self.disk_cleaner = DiskCleaner()

    def _print(self, msg: str, color: str = ""):
        """Print with optional color"""
        if color:
            print(f"{color}{msg}{Colors.RESET}")
        else:
            print(msg)

    def _print_header(self, title: str):
        """Print a section header"""
        width = 60
        print()
        self._print("=" * width, Colors.CYAN)
        self._print(f" {title}", Colors.BOLD + Colors.CYAN)
        self._print("=" * width, Colors.CYAN)

    def _print_subheader(self, title: str):
        """Print a subsection header"""
        self._print(f"\n{title}", Colors.BOLD)
        self._print("-" * 40, Colors.DIM)

    def _get_cpu_color(self, percent: float) -> str:
        """Get color based on CPU percentage"""
        if percent > 80:
            return Colors.RED
        elif percent > 50:
            return Colors.YELLOW
        return Colors.GREEN

    def _get_memory_color(self, percent: float) -> str:
        """Get color based on memory percentage"""
        if percent > 85:
            return Colors.RED
        elif percent > 70:
            return Colors.YELLOW
        return Colors.GREEN

    def _get_thermal_color(self, state: ThermalState) -> str:
        """Get color based on thermal state"""
        colors = {
            ThermalState.COOL: Colors.CYAN,
            ThermalState.WARM: Colors.GREEN,
            ThermalState.HOT: Colors.YELLOW,
            ThermalState.CRITICAL: Colors.RED,
            ThermalState.DANGER: Colors.RED + Colors.BOLD,
        }
        return colors.get(state, Colors.WHITE)

    def show_status(self):
        """Display comprehensive system status"""
        self._print_header("SYSTEM STATUS")

        # CPU
        self._print_subheader("🖥️  CPU")
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        color = self._get_cpu_color(cpu_percent)
        self._print(f"   Usage:      {cpu_percent:.1f}%", color)
        self._print(f"   Cores:      {cpu_count}")
        if cpu_freq:
            self._print(f"   Frequency:  {cpu_freq.current:.0f} MHz")

        # Memory
        self._print_subheader("💾 Memory")
        mem_stats = self.memory_monitor.get_stats()

        color = self._get_memory_color(mem_stats.percent_used)
        self._print(f"   Used:       {self.memory_monitor.format_bytes(mem_stats.used)} / {self.memory_monitor.format_bytes(mem_stats.total)} ({mem_stats.percent_used:.1f}%)", color)
        self._print(f"   Available:  {self.memory_monitor.format_bytes(mem_stats.available)}")
        self._print(f"   Compressed: {self.memory_monitor.format_bytes(mem_stats.compressed)}")

        pressure_color = Colors.GREEN if mem_stats.pressure == MemoryPressure.NORMAL else (
            Colors.YELLOW if mem_stats.pressure == MemoryPressure.WARN else Colors.RED
        )
        self._print(f"   Pressure:   {mem_stats.pressure.value}", pressure_color)

        if mem_stats.swap_used > 0:
            self._print(f"   Swap Used:  {self.memory_monitor.format_bytes(mem_stats.swap_used)}", Colors.YELLOW)

        # Thermal
        self._print_subheader("🌡️  Thermal")
        thermal = self.thermal_monitor.get_status(include_sensors=False)

        color = self._get_thermal_color(thermal.cpu_state)
        if thermal.cpu_temp > 0:
            self._print(f"   CPU Temp:   {thermal.cpu_temp:.1f}°C", color)
        self._print(f"   State:      {thermal.cpu_state.value}", color)

        if thermal.throttle_state != ThrottleState.NONE:
            self._print(f"   Throttling: {thermal.throttle_state.value}", Colors.RED)

        if thermal.fan_speeds:
            fans = ", ".join([f"{k}:{v}rpm" for k, v in thermal.fan_speeds.items()])
            self._print(f"   Fans:       {fans}")

        # Disk
        self._print_subheader("💿 Disk")
        disk = self.disk_cleaner.get_disk_usage()
        self._print(f"   Used:       {disk['used_formatted']} / {disk['total_formatted']} ({disk['percent_used']:.1f}%)")
        self._print(f"   Free:       {disk['free_formatted']}")

        # Cleanable space preview
        analysis = self.disk_cleaner.analyze()
        total_cleanable = sum(analysis.values())
        if total_cleanable > 100 * 1024 * 1024:  # > 100MB
            self._print(f"   Cleanable:  {self.disk_cleaner.format_size(total_cleanable)}", Colors.YELLOW)

        # Top processes
        self._print_subheader("📊 Top Processes")
        top = self.process_scorer.get_top_resource_hogs(5)
        for proc in top:
            protected = "🛡️" if proc.is_protected else "  "
            color = self._get_cpu_color(proc.cpu_percent)
            self._print(f"   {protected} {proc.name[:20]:20s} CPU:{proc.cpu_percent:5.1f}% MEM:{proc.memory_percent:5.1f}%", color)

        print()

    def run_cleanup(self, dry_run: bool = False, aggressive: bool = False,
                    processes: bool = True, caches: bool = True,
                    categories: Optional[list] = None):
        """
        Run system cleanup

        Args:
            dry_run: Preview only, don't actually clean
            aggressive: Use lower thresholds for cleanup
            processes: Clean up processes
            caches: Clean up disk caches
            categories: Specific cleanup categories to target
        """
        mode = "PREVIEW" if dry_run else "CLEANUP"
        self._print_header(f"SYSTEM {mode}")

        total_processes_killed = 0
        total_bytes_freed = 0
        total_files_deleted = 0

        # Process cleanup
        if processes:
            self._print_subheader("🧹 Process Cleanup")

            min_score = 25 if aggressive else 40
            min_cpu = 15 if aggressive else 25

            killable = self.process_scorer.get_killable_processes(
                min_score=min_score,
                min_cpu=min_cpu
            )

            if not killable:
                self._print("   No killable processes found", Colors.GREEN)
            else:
                for proc in killable[:10]:
                    if dry_run:
                        self._print(f"   Would kill: {proc.name} (CPU:{proc.cpu_percent:.1f}%, Score:{proc.kill_score:.0f})", Colors.YELLOW)
                    else:
                        if self.process_scorer.kill_process_gracefully(proc.pid):
                            self._print(f"   ✅ Killed: {proc.name} (CPU:{proc.cpu_percent:.1f}%)", Colors.GREEN)
                            total_processes_killed += 1
                        else:
                            self._print(f"   ❌ Failed: {proc.name}", Colors.RED)

        # Cache cleanup
        if caches:
            self._print_subheader("🗑️  Cache Cleanup")

            # Default categories
            if categories is None:
                categories = [
                    CleanupCategory.USER_CACHE,
                    CleanupCategory.BROWSER_CACHE,
                    CleanupCategory.DEV_CACHE,
                    CleanupCategory.TEMP_FILES,
                ]
                if aggressive:
                    categories.extend([
                        CleanupCategory.LOGS,
                        CleanupCategory.XCODE,
                    ])

            def progress_callback(name, current, total):
                if self.verbose:
                    print(f"   [{current}/{total}] {name}...")

            results = self.disk_cleaner.clean(
                categories=categories,
                dry_run=dry_run,
                progress_callback=progress_callback if self.verbose else None
            )

            # Summarize by category
            by_category = {}
            for r in results:
                if r.bytes_freed > 0:
                    cat = r.category.value
                    if cat not in by_category:
                        by_category[cat] = {'bytes': 0, 'files': 0}
                    by_category[cat]['bytes'] += r.bytes_freed
                    by_category[cat]['files'] += r.files_deleted

            if not by_category:
                self._print("   No cleanable caches found", Colors.GREEN)
            else:
                for cat, data in sorted(by_category.items(), key=lambda x: x[1]['bytes'], reverse=True):
                    action = "Would free" if dry_run else "Freed"
                    self._print(f"   {action}: {self.disk_cleaner.format_size(data['bytes']):>10s} from {cat}", Colors.YELLOW if dry_run else Colors.GREEN)
                    total_bytes_freed += data['bytes']
                    total_files_deleted += data['files']

            # DNS cache
            if not dry_run:
                self._print_subheader("🌐 DNS Cache")
                if self.disk_cleaner.clean_dns_cache():
                    self._print("   ✅ DNS cache flushed", Colors.GREEN)
                else:
                    self._print("   ⚠️  DNS cache flush may require sudo", Colors.YELLOW)

        # Summary
        self._print_subheader("📊 Summary")
        if dry_run:
            self._print(f"   Would kill {total_processes_killed} processes")
            self._print(f"   Would free {self.disk_cleaner.format_size(total_bytes_freed)}")
            self._print(f"   Would delete {total_files_deleted} files")
            self._print("\n   Run without --dry-run to execute cleanup", Colors.CYAN)
        else:
            self._print(f"   Killed {total_processes_killed} processes", Colors.GREEN)
            self._print(f"   Freed {self.disk_cleaner.format_size(total_bytes_freed)}", Colors.GREEN)
            self._print(f"   Deleted {total_files_deleted} files", Colors.GREEN)

        print()

    def run_analyze(self):
        """Run comprehensive system analysis"""
        self._print_header("SYSTEM ANALYSIS")

        # Process analysis
        self._print_subheader("🔍 Process Analysis")

        all_procs = self.process_scorer.get_all_processes(min_cpu=0)
        protected = [p for p in all_procs if p.is_protected]
        killable = [p for p in all_procs if not p.is_protected and p.kill_score > 20]

        self._print(f"   Total processes:     {len(all_procs)}")
        self._print(f"   Protected processes: {len(protected)}", Colors.GREEN)
        self._print(f"   Killable processes:  {len(killable)}", Colors.YELLOW if killable else Colors.GREEN)

        # Category breakdown
        categories = {}
        for p in all_procs:
            cat = p.category.value
            categories[cat] = categories.get(cat, 0) + 1

        self._print("\n   By category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            self._print(f"      {cat:20s}: {count}")

        # Memory analysis
        self._print_subheader("💾 Memory Analysis")

        mem_stats = self.memory_monitor.get_stats()
        self._print(f"   Memory pressure:  {mem_stats.pressure.value}")
        self._print(f"   Pressure level:   {mem_stats.pressure_percent:.1f}%")

        # Check for memory leaks
        leaks = self.memory_monitor.detect_memory_leaks(threshold_mb=50)
        if leaks:
            self._print(f"\n   ⚠️  Potential memory leaks:", Colors.YELLOW)
            for pid, name, growth in leaks[:5]:
                self._print(f"      {name} (PID:{pid}): +{growth}MB", Colors.YELLOW)

        # Top memory users
        self._print("\n   Top memory users:")
        for proc in self.memory_monitor.get_top_memory_processes(5):
            self._print(f"      {proc.name[:20]:20s}: {self.memory_monitor.format_bytes(proc.rss)}")

        # Thermal analysis
        self._print_subheader("🌡️  Thermal Analysis")

        thermal = self.thermal_monitor.get_status(include_sensors=True)
        self._print(f"   Platform:     {'Apple Silicon' if thermal.is_apple_silicon else 'Intel'}")
        self._print(f"   CPU temp:     {thermal.cpu_temp:.1f}°C" if thermal.cpu_temp else "   CPU temp:     N/A")
        self._print(f"   Thermal state: {thermal.cpu_state.value}")
        self._print(f"   Throttle:     {thermal.throttle_state.value}")

        if thermal.sensors:
            self._print("\n   Detected sensors:")
            for sensor in sorted(thermal.sensors, key=lambda x: x.temperature, reverse=True)[:8]:
                self._print(f"      {sensor.name:8s} ({sensor.location:10s}): {sensor.temperature:.1f}°C")

        # Disk analysis
        self._print_subheader("💿 Disk Analysis")

        disk = self.disk_cleaner.get_disk_usage()
        self._print(f"   Total space:  {disk['total_formatted']}")
        self._print(f"   Used:         {disk['used_formatted']} ({disk['percent_used']:.1f}%)")
        self._print(f"   Free:         {disk['free_formatted']}")

        analysis = self.disk_cleaner.analyze()
        total_cleanable = sum(analysis.values())

        self._print(f"\n   Cleanable space by category:")
        for category, size in sorted(analysis.items(), key=lambda x: x[1], reverse=True):
            if size > 10 * 1024 * 1024:  # > 10MB
                self._print(f"      {category.value:20s}: {self.disk_cleaner.format_size(size)}")

        self._print(f"\n   Total cleanable: {self.disk_cleaner.format_size(total_cleanable)}", Colors.CYAN)

        # Recommendations
        self._print_subheader("💡 Recommendations")

        recommendations = []

        # CPU recommendations
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 80:
            recommendations.append("High CPU usage - consider closing resource-intensive apps")
        elif cpu_percent > 50:
            recommendations.append("Moderate CPU usage - monitor for sustained high load")

        # Memory recommendations
        recommendations.extend(self.memory_monitor.get_recommendations(mem_stats))

        # Thermal recommendations
        recommendations.extend(thermal.recommendations)

        # Disk recommendations
        if disk['percent_used'] > 90:
            recommendations.append(f"Disk nearly full ({disk['percent_used']:.0f}%) - run cleanup immediately")
        elif disk['percent_used'] > 80:
            recommendations.append(f"Disk usage high ({disk['percent_used']:.0f}%) - consider running cleanup")

        if total_cleanable > 1024 ** 3:  # > 1GB
            recommendations.append(f"Over {self.disk_cleaner.format_size(total_cleanable)} of cleanable data found")

        if not recommendations:
            self._print("   ✅ System is running optimally", Colors.GREEN)
        else:
            for rec in recommendations:
                if "critical" in rec.lower() or "danger" in rec.lower():
                    color = Colors.RED
                elif "warning" in rec.lower() or "high" in rec.lower():
                    color = Colors.YELLOW
                else:
                    color = Colors.WHITE
                self._print(f"   • {rec}", color)

        print()

    def run_monitor(self, interval: float = 2.0):
        """
        Run continuous monitoring

        Args:
            interval: Update interval in seconds
        """
        self._print_header("CONTINUOUS MONITORING")
        self._print("Press Ctrl+C to stop\n", Colors.DIM)

        # Handle Ctrl+C gracefully
        def signal_handler(sig, frame):
            print("\n\nMonitoring stopped.")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        iteration = 0
        while True:
            iteration += 1

            # Clear previous output (move cursor up)
            if iteration > 1:
                print("\033[10A\033[J", end="")  # Move up 10 lines and clear

            # Get metrics
            cpu = psutil.cpu_percent(interval=0.1)
            mem = self.memory_monitor.get_stats()
            thermal = self.thermal_monitor.get_status(include_sensors=False)

            # Build status line
            cpu_color = self._get_cpu_color(cpu)
            mem_color = self._get_memory_color(mem.percent_used)
            thermal_color = self._get_thermal_color(thermal.cpu_state)

            timestamp = time.strftime("%H:%M:%S")

            print(f"[{timestamp}] Update #{iteration}")
            print("-" * 50)
            print(f"{cpu_color}CPU:     {cpu:5.1f}%{Colors.RESET}")
            print(f"{mem_color}Memory:  {mem.percent_used:5.1f}% ({self.memory_monitor.format_bytes(mem.used)}){Colors.RESET}")
            print(f"         Pressure: {mem.pressure.value}")
            print(f"{thermal_color}Thermal: {thermal.cpu_temp:.0f}°C ({thermal.cpu_state.value}){Colors.RESET}" if thermal.cpu_temp else f"{thermal_color}Thermal: {thermal.cpu_state.value}{Colors.RESET}")

            if thermal.throttle_state != ThrottleState.NONE:
                print(f"{Colors.RED}⚠️  THROTTLING: {thermal.throttle_state.value}{Colors.RESET}")

            # Alerts
            alerts = []
            if cpu > 80:
                alerts.append("High CPU")
            if mem.pressure == MemoryPressure.CRITICAL:
                alerts.append("Critical Memory")
            if thermal.cpu_state in [ThermalState.CRITICAL, ThermalState.DANGER]:
                alerts.append("High Temperature")

            if alerts:
                print(f"\n{Colors.RED}ALERTS: {', '.join(alerts)}{Colors.RESET}")
            else:
                print()

            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description="System Optimizer - macOS Performance Optimization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status              Show system status
  %(prog)s cleanup             Run smart cleanup
  %(prog)s cleanup --dry-run   Preview cleanup without executing
  %(prog)s cleanup --aggressive  Aggressive cleanup
  %(prog)s monitor             Continuous monitoring
  %(prog)s analyze             Full system analysis
        """
    )

    parser.add_argument('command', choices=['status', 'cleanup', 'monitor', 'analyze'],
                       help='Command to run')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview cleanup without executing')
    parser.add_argument('--aggressive', action='store_true',
                       help='Use aggressive cleanup thresholds')
    parser.add_argument('--no-processes', action='store_true',
                       help='Skip process cleanup')
    parser.add_argument('--no-caches', action='store_true',
                       help='Skip cache cleanup')
    parser.add_argument('--interval', type=float, default=2.0,
                       help='Monitor update interval (default: 2.0)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    optimizer = SystemOptimizer(verbose=args.verbose)

    if args.command == 'status':
        optimizer.show_status()
    elif args.command == 'cleanup':
        optimizer.run_cleanup(
            dry_run=args.dry_run,
            aggressive=args.aggressive,
            processes=not args.no_processes,
            caches=not args.no_caches
        )
    elif args.command == 'monitor':
        optimizer.run_monitor(interval=args.interval)
    elif args.command == 'analyze':
        optimizer.run_analyze()


if __name__ == "__main__":
    main()
