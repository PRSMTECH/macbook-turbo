#!/usr/bin/env python3
"""
Apple Silicon Monitor for MacBook Turbo.

Provides M-series chip specific monitoring:
- E-core vs P-core utilization
- Thermal pressure monitoring
- Power state detection
- Unified memory bandwidth
"""

import subprocess
import platform
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List


class ChipType(Enum):
    """Apple Silicon chip types."""
    INTEL = "intel"
    M1 = "m1"
    M1_PRO = "m1_pro"
    M1_MAX = "m1_max"
    M1_ULTRA = "m1_ultra"
    M2 = "m2"
    M2_PRO = "m2_pro"
    M2_MAX = "m2_max"
    M2_ULTRA = "m2_ultra"
    M3 = "m3"
    M3_PRO = "m3_pro"
    M3_MAX = "m3_max"
    M4 = "m4"
    M4_PRO = "m4_pro"
    M4_MAX = "m4_max"
    UNKNOWN = "unknown"


class ThermalPressure(Enum):
    """System thermal pressure levels (from pmset)."""
    NOMINAL = "nominal"
    MODERATE = "moderate"
    HEAVY = "heavy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class PowerMode(Enum):
    """System power mode."""
    LOW_POWER = "low_power"
    AUTOMATIC = "automatic"
    HIGH_PERFORMANCE = "high_performance"
    UNKNOWN = "unknown"


@dataclass
class CoreInfo:
    """Information about CPU cores."""
    efficiency_cores: int  # E-cores (low power)
    performance_cores: int  # P-cores (high performance)
    total_cores: int
    gpu_cores: int
    neural_cores: int


@dataclass
class AppleSiliconStatus:
    """Status information for Apple Silicon chip."""
    chip_type: ChipType
    core_info: CoreInfo
    thermal_pressure: ThermalPressure
    power_mode: PowerMode
    cpu_freq_efficiency: Optional[float]  # MHz
    cpu_freq_performance: Optional[float]  # MHz
    gpu_utilization: Optional[float]  # Percent
    memory_bandwidth: Optional[float]  # GB/s
    power_usage: Optional[float]  # Watts
    is_throttled: bool
    recommendations: List[str]


class AppleSiliconMonitor:
    """Monitor for Apple Silicon Macs."""

    # Chip configurations: (e-cores, p-cores, gpu-cores, neural-cores)
    CHIP_CONFIGS = {
        ChipType.M1: CoreInfo(4, 4, 8, 7, 16),
        ChipType.M1_PRO: CoreInfo(2, 8, 10, 16, 16),
        ChipType.M1_MAX: CoreInfo(2, 8, 10, 32, 16),
        ChipType.M1_ULTRA: CoreInfo(4, 16, 20, 64, 32),
        ChipType.M2: CoreInfo(4, 4, 8, 10, 16),
        ChipType.M2_PRO: CoreInfo(4, 8, 12, 19, 16),
        ChipType.M2_MAX: CoreInfo(4, 8, 12, 38, 16),
        ChipType.M2_ULTRA: CoreInfo(8, 16, 24, 76, 32),
        ChipType.M3: CoreInfo(4, 4, 8, 10, 16),
        ChipType.M3_PRO: CoreInfo(6, 6, 12, 18, 16),
        ChipType.M3_MAX: CoreInfo(4, 12, 16, 40, 16),
        ChipType.M4: CoreInfo(4, 6, 10, 10, 16),
        ChipType.M4_PRO: CoreInfo(4, 10, 14, 20, 16),
        ChipType.M4_MAX: CoreInfo(4, 12, 16, 40, 16),
    }

    def __init__(self):
        """Initialize the Apple Silicon monitor."""
        self._chip_type: Optional[ChipType] = None
        self._core_info: Optional[CoreInfo] = None
        self._is_apple_silicon: Optional[bool] = None

    @property
    def is_apple_silicon(self) -> bool:
        """Check if running on Apple Silicon."""
        if self._is_apple_silicon is None:
            self._is_apple_silicon = platform.machine() == "arm64"
        return self._is_apple_silicon

    def get_chip_type(self) -> ChipType:
        """Detect the Apple Silicon chip type."""
        if self._chip_type is not None:
            return self._chip_type

        if not self.is_apple_silicon:
            self._chip_type = ChipType.INTEL
            return self._chip_type

        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, timeout=5
            )
            brand = result.stdout.strip().lower()

            # Detect chip type from brand string
            if "m4 max" in brand:
                self._chip_type = ChipType.M4_MAX
            elif "m4 pro" in brand:
                self._chip_type = ChipType.M4_PRO
            elif "m4" in brand:
                self._chip_type = ChipType.M4
            elif "m3 max" in brand:
                self._chip_type = ChipType.M3_MAX
            elif "m3 pro" in brand:
                self._chip_type = ChipType.M3_PRO
            elif "m3" in brand:
                self._chip_type = ChipType.M3
            elif "m2 ultra" in brand:
                self._chip_type = ChipType.M2_ULTRA
            elif "m2 max" in brand:
                self._chip_type = ChipType.M2_MAX
            elif "m2 pro" in brand:
                self._chip_type = ChipType.M2_PRO
            elif "m2" in brand:
                self._chip_type = ChipType.M2
            elif "m1 ultra" in brand:
                self._chip_type = ChipType.M1_ULTRA
            elif "m1 max" in brand:
                self._chip_type = ChipType.M1_MAX
            elif "m1 pro" in brand:
                self._chip_type = ChipType.M1_PRO
            elif "m1" in brand:
                self._chip_type = ChipType.M1
            else:
                self._chip_type = ChipType.UNKNOWN

        except Exception:
            self._chip_type = ChipType.UNKNOWN

        return self._chip_type

    def get_core_info(self) -> CoreInfo:
        """Get information about CPU cores."""
        if self._core_info is not None:
            return self._core_info

        chip_type = self.get_chip_type()

        if chip_type in self.CHIP_CONFIGS:
            self._core_info = self.CHIP_CONFIGS[chip_type]
        else:
            # Fallback: get actual core count from system
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "hw.ncpu"],
                    capture_output=True, text=True, timeout=5
                )
                total_cores = int(result.stdout.strip())

                # Estimate E/P split (typically 50/50 for M1/M2 base)
                e_cores = total_cores // 2
                p_cores = total_cores - e_cores

                self._core_info = CoreInfo(
                    efficiency_cores=e_cores,
                    performance_cores=p_cores,
                    total_cores=total_cores,
                    gpu_cores=0,  # Unknown
                    neural_cores=0  # Unknown
                )
            except Exception:
                self._core_info = CoreInfo(0, 0, 0, 0, 0)

        return self._core_info

    def get_thermal_pressure(self) -> ThermalPressure:
        """Get current thermal pressure from the system."""
        try:
            result = subprocess.run(
                ["pmset", "-g", "therm"],
                capture_output=True, text=True, timeout=5
            )

            output = result.stdout.lower()

            if "critical" in output:
                return ThermalPressure.CRITICAL
            elif "heavy" in output:
                return ThermalPressure.HEAVY
            elif "moderate" in output:
                return ThermalPressure.MODERATE
            elif "nominal" in output:
                return ThermalPressure.NOMINAL

            # Parse numeric thermal state if available
            match = re.search(r"cpu_scheduler_limit\s*=\s*(\d+)", output)
            if match:
                limit = int(match.group(1))
                if limit >= 100:
                    return ThermalPressure.NOMINAL
                elif limit >= 80:
                    return ThermalPressure.MODERATE
                elif limit >= 50:
                    return ThermalPressure.HEAVY
                else:
                    return ThermalPressure.CRITICAL

            return ThermalPressure.UNKNOWN

        except Exception:
            return ThermalPressure.UNKNOWN

    def get_power_mode(self) -> PowerMode:
        """Get current power mode."""
        try:
            result = subprocess.run(
                ["pmset", "-g"],
                capture_output=True, text=True, timeout=5
            )

            output = result.stdout.lower()

            if "lowpowermode" in output and "1" in output:
                return PowerMode.LOW_POWER
            elif "highpowermode" in output and "1" in output:
                return PowerMode.HIGH_PERFORMANCE
            else:
                return PowerMode.AUTOMATIC

        except Exception:
            return PowerMode.UNKNOWN

    def get_status(self) -> AppleSiliconStatus:
        """Get comprehensive Apple Silicon status."""
        chip_type = self.get_chip_type()
        core_info = self.get_core_info()
        thermal_pressure = self.get_thermal_pressure()
        power_mode = self.get_power_mode()

        # Determine if throttled
        is_throttled = thermal_pressure in [
            ThermalPressure.HEAVY,
            ThermalPressure.CRITICAL
        ]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            thermal_pressure, power_mode, is_throttled
        )

        return AppleSiliconStatus(
            chip_type=chip_type,
            core_info=core_info,
            thermal_pressure=thermal_pressure,
            power_mode=power_mode,
            cpu_freq_efficiency=None,  # Requires sudo powermetrics
            cpu_freq_performance=None,
            gpu_utilization=None,
            memory_bandwidth=None,
            power_usage=None,
            is_throttled=is_throttled,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        thermal: ThermalPressure,
        power: PowerMode,
        throttled: bool
    ) -> List[str]:
        """Generate recommendations based on current state."""
        recs = []

        if thermal == ThermalPressure.CRITICAL:
            recs.append("Critical thermal state - close resource-intensive apps")
            recs.append("Consider improving ventilation or using a cooling pad")
        elif thermal == ThermalPressure.HEAVY:
            recs.append("Heavy thermal load - consider reducing workload")
        elif thermal == ThermalPressure.MODERATE:
            recs.append("Thermal pressure elevated - monitor closely")

        if throttled:
            recs.append("CPU is being throttled due to thermal limits")

        if power == PowerMode.LOW_POWER:
            recs.append("Low Power Mode active - performance is reduced")
        elif power == PowerMode.HIGH_PERFORMANCE:
            recs.append("High Performance Mode - expect higher power consumption")

        if not recs:
            recs.append("System operating normally")

        return recs

    def get_pressure_emoji(self, pressure: ThermalPressure) -> str:
        """Get emoji for thermal pressure level."""
        emoji_map = {
            ThermalPressure.NOMINAL: "🟢",
            ThermalPressure.MODERATE: "🟡",
            ThermalPressure.HEAVY: "🟠",
            ThermalPressure.CRITICAL: "🔴",
            ThermalPressure.UNKNOWN: "⚪",
        }
        return emoji_map.get(pressure, "⚪")

    def get_chip_display_name(self, chip_type: ChipType) -> str:
        """Get display-friendly chip name."""
        name_map = {
            ChipType.INTEL: "Intel",
            ChipType.M1: "Apple M1",
            ChipType.M1_PRO: "Apple M1 Pro",
            ChipType.M1_MAX: "Apple M1 Max",
            ChipType.M1_ULTRA: "Apple M1 Ultra",
            ChipType.M2: "Apple M2",
            ChipType.M2_PRO: "Apple M2 Pro",
            ChipType.M2_MAX: "Apple M2 Max",
            ChipType.M2_ULTRA: "Apple M2 Ultra",
            ChipType.M3: "Apple M3",
            ChipType.M3_PRO: "Apple M3 Pro",
            ChipType.M3_MAX: "Apple M3 Max",
            ChipType.M4: "Apple M4",
            ChipType.M4_PRO: "Apple M4 Pro",
            ChipType.M4_MAX: "Apple M4 Max",
            ChipType.UNKNOWN: "Unknown",
        }
        return name_map.get(chip_type, "Unknown")


# Convenience function
def get_apple_silicon_monitor() -> AppleSiliconMonitor:
    """Get an Apple Silicon monitor instance."""
    return AppleSiliconMonitor()


if __name__ == "__main__":
    # Test the monitor
    monitor = AppleSiliconMonitor()

    print("Apple Silicon Monitor Test")
    print("=" * 40)

    if monitor.is_apple_silicon:
        print(f"Running on Apple Silicon: Yes")

        status = monitor.get_status()

        print(f"\nChip: {monitor.get_chip_display_name(status.chip_type)}")
        print(f"Cores: {status.core_info.efficiency_cores} E-cores, "
              f"{status.core_info.performance_cores} P-cores")
        print(f"GPU Cores: {status.core_info.gpu_cores}")
        print(f"Neural Cores: {status.core_info.neural_cores}")
        print(f"\nThermal Pressure: {status.thermal_pressure.value} "
              f"{monitor.get_pressure_emoji(status.thermal_pressure)}")
        print(f"Power Mode: {status.power_mode.value}")
        print(f"Throttled: {status.is_throttled}")

        print(f"\nRecommendations:")
        for rec in status.recommendations:
            print(f"  - {rec}")
    else:
        print("Running on Intel Mac")
        print("Apple Silicon specific features not available")
