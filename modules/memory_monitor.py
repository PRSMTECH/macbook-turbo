#!/usr/bin/env python3
"""
Memory Monitor Module
macOS-specific memory pressure monitoring and management
Inspired by: stats, Activity Monitor patterns
"""

import subprocess
import re
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryPressure(Enum):
    """macOS memory pressure levels"""
    NORMAL = "normal"       # Green in Activity Monitor
    WARN = "warn"           # Yellow - system starting to compress
    CRITICAL = "critical"   # Red - heavy swapping/compression


class SwapState(Enum):
    """Swap usage state"""
    NONE = "none"           # No swap used
    LIGHT = "light"         # < 1GB swap
    MODERATE = "moderate"   # 1-4GB swap
    HEAVY = "heavy"         # > 4GB swap


@dataclass
class MemoryStats:
    """Detailed memory statistics"""
    total: int              # Total physical RAM
    available: int          # Available memory
    used: int               # Used memory
    free: int               # Free memory (unused)
    active: int             # Active memory
    inactive: int           # Inactive memory
    wired: int              # Wired/kernel memory
    compressed: int         # Compressed memory
    swap_total: int         # Total swap
    swap_used: int          # Used swap
    swap_free: int          # Free swap
    cached: int             # File cache
    app_memory: int         # Application memory
    pressure: MemoryPressure
    swap_state: SwapState
    percent_used: float
    pressure_percent: float  # 0-100 memory pressure
    timestamp: float


@dataclass
class ProcessMemory:
    """Memory info for a process"""
    pid: int
    name: str
    rss: int                # Resident Set Size (actual RAM)
    vms: int                # Virtual Memory Size
    percent: float          # Percentage of total RAM
    compressed: int         # Compressed memory (macOS specific)
    is_compressible: bool   # Can be compressed


class MemoryMonitor:
    """
    macOS Memory Monitoring System

    Features:
    - Memory pressure detection (macOS specific)
    - Swap usage monitoring
    - Compressed memory tracking
    - Process memory analysis
    - Memory leak detection
    - Recommendations for memory management
    """

    # Pressure thresholds
    PRESSURE_THRESHOLDS = {
        MemoryPressure.NORMAL: 50,
        MemoryPressure.WARN: 75,
        MemoryPressure.CRITICAL: 90,
    }

    def __init__(self):
        self._history: List[MemoryStats] = []
        self._max_history = 60
        self._last_stats: Optional[MemoryStats] = None
        self._process_memory_history: Dict[int, List[int]] = {}  # pid -> [rss values]

    def _run_vm_stat(self) -> Dict[str, int]:
        """
        Parse vm_stat output for detailed memory info
        vm_stat is macOS-specific and provides detailed VM statistics
        """
        stats = {}

        try:
            result = subprocess.run(
                ['vm_stat'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse page size
                page_size = 4096  # Default macOS page size
                for line in result.stdout.split('\n'):
                    if 'page size of' in line:
                        match = re.search(r'(\d+) bytes', line)
                        if match:
                            page_size = int(match.group(1))
                        break

                # Parse memory categories
                patterns = {
                    'free': r'Pages free:\s+(\d+)',
                    'active': r'Pages active:\s+(\d+)',
                    'inactive': r'Pages inactive:\s+(\d+)',
                    'speculative': r'Pages speculative:\s+(\d+)',
                    'wired': r'Pages wired down:\s+(\d+)',
                    'compressed': r'Pages occupied by compressor:\s+(\d+)',
                    'cached': r'File-backed pages:\s+(\d+)',
                    'purgeable': r'Pages purgeable:\s+(\d+)',
                    'swapins': r'Swapins:\s+(\d+)',
                    'swapouts': r'Swapouts:\s+(\d+)',
                    'compressions': r'Compressions:\s+(\d+)',
                    'decompressions': r'Decompressions:\s+(\d+)',
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, result.stdout)
                    if match:
                        # Convert pages to bytes
                        stats[key] = int(match.group(1)) * page_size

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.warning(f"Failed to get vm_stat: {e}")

        return stats

    def _get_memory_pressure(self) -> Tuple[MemoryPressure, float]:
        """
        Get macOS memory pressure level
        Uses the memory_pressure command for accurate pressure reading
        """
        pressure = MemoryPressure.NORMAL
        pressure_percent = 0.0

        try:
            result = subprocess.run(
                ['memory_pressure'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                output = result.stdout.lower()

                # Parse pressure level
                if 'critical' in output:
                    pressure = MemoryPressure.CRITICAL
                elif 'warn' in output:
                    pressure = MemoryPressure.WARN
                else:
                    pressure = MemoryPressure.NORMAL

                # Try to get percentage
                match = re.search(r'(\d+(?:\.\d+)?)\s*%', result.stdout)
                if match:
                    pressure_percent = float(match.group(1))
                else:
                    # Estimate from level
                    if pressure == MemoryPressure.CRITICAL:
                        pressure_percent = 90
                    elif pressure == MemoryPressure.WARN:
                        pressure_percent = 70
                    else:
                        pressure_percent = 30

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.warning(f"Failed to get memory pressure: {e}")
            # Fall back to psutil-based estimation
            mem = psutil.virtual_memory()
            pressure_percent = mem.percent
            if pressure_percent > 90:
                pressure = MemoryPressure.CRITICAL
            elif pressure_percent > 75:
                pressure = MemoryPressure.WARN

        return pressure, pressure_percent

    def _get_swap_state(self, swap_used: int) -> SwapState:
        """Classify swap usage state"""
        gb = 1024 ** 3
        if swap_used < 100 * 1024 * 1024:  # < 100MB
            return SwapState.NONE
        elif swap_used < gb:
            return SwapState.LIGHT
        elif swap_used < 4 * gb:
            return SwapState.MODERATE
        else:
            return SwapState.HEAVY

    def get_stats(self) -> MemoryStats:
        """Get comprehensive memory statistics"""
        # Get basic stats from psutil
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Get detailed macOS stats
        vm_stats = self._run_vm_stat()

        # Get memory pressure
        pressure, pressure_percent = self._get_memory_pressure()

        # Calculate app memory (used - wired - compressed)
        wired = vm_stats.get('wired', 0)
        compressed = vm_stats.get('compressed', 0)
        app_memory = mem.used - wired - compressed
        app_memory = max(0, app_memory)  # Ensure non-negative

        stats = MemoryStats(
            total=mem.total,
            available=mem.available,
            used=mem.used,
            free=mem.free,
            active=vm_stats.get('active', 0),
            inactive=vm_stats.get('inactive', 0),
            wired=wired,
            compressed=compressed,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_free=swap.free,
            cached=vm_stats.get('cached', 0),
            app_memory=app_memory,
            pressure=pressure,
            swap_state=self._get_swap_state(swap.used),
            percent_used=mem.percent,
            pressure_percent=pressure_percent,
            timestamp=time.time()
        )

        # Update history
        self._last_stats = stats
        self._history.append(stats)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        return stats

    def get_top_memory_processes(self, limit: int = 10) -> List[ProcessMemory]:
        """Get processes using the most memory"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
            try:
                info = proc.info
                mem_info = info['memory_info']

                processes.append(ProcessMemory(
                    pid=info['pid'],
                    name=info['name'],
                    rss=mem_info.rss,
                    vms=mem_info.vms,
                    percent=info['memory_percent'] or 0,
                    compressed=0,  # Would need additional API access
                    is_compressible=True
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort by RSS and return top N
        processes.sort(key=lambda x: x.rss, reverse=True)
        return processes[:limit]

    def detect_memory_leaks(self, threshold_mb: int = 100) -> List[Tuple[int, str, int]]:
        """
        Detect potential memory leaks by tracking memory growth

        Returns: List of (pid, name, growth_mb) for processes with significant growth
        """
        leaks = []

        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                rss = proc.info['memory_info'].rss

                if pid not in self._process_memory_history:
                    self._process_memory_history[pid] = []

                history = self._process_memory_history[pid]
                history.append(rss)

                # Keep only last 10 readings
                if len(history) > 10:
                    history.pop(0)

                # Check for consistent growth
                if len(history) >= 5:
                    growth = history[-1] - history[0]
                    growth_mb = growth / (1024 * 1024)

                    # Check if growth is consistent (always increasing)
                    is_growing = all(history[i] <= history[i+1] for i in range(len(history)-1))

                    if is_growing and growth_mb > threshold_mb:
                        leaks.append((pid, name, int(growth_mb)))

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Clean up history for dead processes
                if pid in self._process_memory_history:
                    del self._process_memory_history[pid]

        return sorted(leaks, key=lambda x: x[2], reverse=True)

    def format_bytes(self, bytes_size: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} PB"

    def get_pressure_emoji(self, pressure: MemoryPressure) -> str:
        """Get emoji for memory pressure level"""
        emojis = {
            MemoryPressure.NORMAL: "🟢",
            MemoryPressure.WARN: "🟡",
            MemoryPressure.CRITICAL: "🔴",
        }
        return emojis.get(pressure, "❓")

    def get_swap_emoji(self, state: SwapState) -> str:
        """Get emoji for swap state"""
        emojis = {
            SwapState.NONE: "✅",
            SwapState.LIGHT: "💧",
            SwapState.MODERATE: "💦",
            SwapState.HEAVY: "🌊",
        }
        return emojis.get(state, "❓")

    def get_recommendations(self, stats: Optional[MemoryStats] = None) -> List[str]:
        """Generate recommendations based on memory status"""
        if stats is None:
            stats = self.get_stats()

        recommendations = []

        # Pressure-based recommendations
        if stats.pressure == MemoryPressure.CRITICAL:
            recommendations.append("🚨 CRITICAL: System under severe memory pressure!")
            recommendations.append("   - Close unused applications immediately")
            recommendations.append("   - Restart memory-heavy applications")
            recommendations.append("   - Consider adding more RAM")
        elif stats.pressure == MemoryPressure.WARN:
            recommendations.append("⚠️ WARNING: Memory pressure elevated")
            recommendations.append("   - Close browser tabs and unused apps")
            recommendations.append("   - Monitor for further degradation")

        # Swap recommendations
        if stats.swap_state == SwapState.HEAVY:
            recommendations.append("🌊 Heavy swap usage detected")
            recommendations.append(f"   - {self.format_bytes(stats.swap_used)} in swap")
            recommendations.append("   - System performance significantly impacted")
            recommendations.append("   - Reduce application memory usage")
        elif stats.swap_state == SwapState.MODERATE:
            recommendations.append(f"💦 Moderate swap usage: {self.format_bytes(stats.swap_used)}")

        # Compressed memory recommendations
        if stats.compressed > 4 * 1024 ** 3:  # > 4GB compressed
            recommendations.append(f"📦 High memory compression: {self.format_bytes(stats.compressed)}")
            recommendations.append("   - System actively compressing memory")

        # Check for memory leaks
        leaks = self.detect_memory_leaks()
        if leaks:
            recommendations.append("🔍 Potential memory leaks detected:")
            for pid, name, growth in leaks[:3]:
                recommendations.append(f"   - {name} (PID:{pid}): +{growth}MB")

        return recommendations

    def purge_memory(self) -> bool:
        """
        Attempt to purge inactive memory (requires sudo)
        Uses the 'purge' command
        """
        try:
            result = subprocess.run(
                ['sudo', 'purge'],
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False

    def get_trend(self) -> str:
        """Get memory usage trend from history"""
        if len(self._history) < 3:
            return "stable"

        recent = [h.percent_used for h in self._history[-3:]]
        avg_change = (recent[-1] - recent[0]) / len(recent)

        if avg_change > 3:
            return "rising_fast"
        elif avg_change > 1:
            return "rising"
        elif avg_change < -3:
            return "freeing_fast"
        elif avg_change < -1:
            return "freeing"
        else:
            return "stable"


def main():
    """Test the memory monitor"""
    monitor = MemoryMonitor()

    print("=" * 60)
    print("Memory Monitor Test")
    print("=" * 60)

    stats = monitor.get_stats()

    print(f"\n📊 Memory Overview:")
    print(f"   Total:      {monitor.format_bytes(stats.total)}")
    print(f"   Used:       {monitor.format_bytes(stats.used)} ({stats.percent_used:.1f}%)")
    print(f"   Available:  {monitor.format_bytes(stats.available)}")
    print(f"   Free:       {monitor.format_bytes(stats.free)}")

    print(f"\n📦 Memory Breakdown:")
    print(f"   App Memory: {monitor.format_bytes(stats.app_memory)}")
    print(f"   Wired:      {monitor.format_bytes(stats.wired)}")
    print(f"   Compressed: {monitor.format_bytes(stats.compressed)}")
    print(f"   Cached:     {monitor.format_bytes(stats.cached)}")
    print(f"   Active:     {monitor.format_bytes(stats.active)}")
    print(f"   Inactive:   {monitor.format_bytes(stats.inactive)}")

    print(f"\n💾 Swap:")
    print(f"   Total:      {monitor.format_bytes(stats.swap_total)}")
    print(f"   Used:       {monitor.format_bytes(stats.swap_used)} {monitor.get_swap_emoji(stats.swap_state)}")
    print(f"   State:      {stats.swap_state.value}")

    print(f"\n🎚️ Status:")
    print(f"   Pressure:   {stats.pressure.value} {monitor.get_pressure_emoji(stats.pressure)}")
    print(f"   Pressure %: {stats.pressure_percent:.1f}%")

    print(f"\n🔝 Top Memory Processes:")
    for proc in monitor.get_top_memory_processes(5):
        print(f"   {proc.name:25s}: {monitor.format_bytes(proc.rss):>10s} ({proc.percent:.1f}%)")

    recommendations = monitor.get_recommendations(stats)
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
