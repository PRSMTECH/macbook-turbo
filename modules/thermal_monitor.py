#!/usr/bin/env python3
"""
Thermal Monitoring Module
Detect thermal throttling and temperature issues on macOS
Inspired by: stats, macoh, VoltageShift patterns
"""

import subprocess
import re
import platform
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThermalState(Enum):
    """Thermal state classification"""
    COOL = "cool"           # < 50°C - Normal operation
    WARM = "warm"           # 50-70°C - Light load
    HOT = "hot"             # 70-85°C - Heavy load
    CRITICAL = "critical"   # 85-95°C - Throttling likely
    DANGER = "danger"       # > 95°C - Thermal emergency


class ThrottleState(Enum):
    """CPU throttle state"""
    NONE = "none"           # No throttling
    LIGHT = "light"         # Minor throttling
    MODERATE = "moderate"   # Significant throttling
    HEAVY = "heavy"         # Severe throttling
    EMERGENCY = "emergency" # Emergency throttle


@dataclass
class ThermalReading:
    """A single thermal sensor reading"""
    name: str
    temperature: float
    state: ThermalState
    location: str = ""


@dataclass
class ThermalStatus:
    """Complete thermal status of the system"""
    cpu_temp: float
    gpu_temp: float
    battery_temp: float
    ambient_temp: float
    cpu_state: ThermalState
    throttle_state: ThrottleState
    fan_speeds: Dict[str, int]  # RPM
    sensors: List[ThermalReading]
    is_apple_silicon: bool
    timestamp: float
    recommendations: List[str] = field(default_factory=list)


class ThermalMonitor:
    """
    macOS Thermal Monitoring System

    Features:
    - CPU/GPU/Battery temperature monitoring
    - Throttle detection
    - Fan speed monitoring
    - Apple Silicon and Intel support
    - Thermal state classification
    - Recommendations for thermal management
    """

    # Temperature thresholds (Celsius)
    THRESHOLDS = {
        ThermalState.COOL: 50,
        ThermalState.WARM: 70,
        ThermalState.HOT: 85,
        ThermalState.CRITICAL: 95,
        ThermalState.DANGER: 100,
    }

    # Intel-specific sensor names
    INTEL_SENSORS = {
        'cpu': ['TC0P', 'TC0H', 'TC0D', 'TC0E', 'TC0F', 'CPU Core'],
        'gpu': ['TG0P', 'TG0H', 'TG0D', 'GPU'],
        'battery': ['TB0T', 'TB1T', 'TB2T', 'Battery'],
        'ambient': ['TA0P', 'TA0S', 'Ambient'],
    }

    # Apple Silicon sensor patterns
    APPLE_SILICON_SENSORS = {
        'cpu': ['CPU', 'Pcore', 'Ecore', 'SOC'],
        'gpu': ['GPU'],
        'battery': ['Battery', 'PMU'],
        'ambient': ['Ambient', 'Air'],
    }

    def __init__(self):
        self.is_apple_silicon = self._detect_apple_silicon()
        self._powermetrics_available = self._check_powermetrics()
        self._last_status: Optional[ThermalStatus] = None
        self._history: List[ThermalStatus] = []
        self._max_history = 60  # Keep 60 readings for trend analysis

    def _detect_apple_silicon(self) -> bool:
        """Detect if running on Apple Silicon"""
        return platform.processor() == 'arm' or 'Apple' in platform.processor()

    def _check_powermetrics(self) -> bool:
        """Check if powermetrics is available (requires sudo)"""
        try:
            result = subprocess.run(
                ['which', 'powermetrics'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _get_temperature_state(self, temp: float) -> ThermalState:
        """Classify temperature into thermal state"""
        if temp < self.THRESHOLDS[ThermalState.COOL]:
            return ThermalState.COOL
        elif temp < self.THRESHOLDS[ThermalState.WARM]:
            return ThermalState.WARM
        elif temp < self.THRESHOLDS[ThermalState.HOT]:
            return ThermalState.HOT
        elif temp < self.THRESHOLDS[ThermalState.CRITICAL]:
            return ThermalState.CRITICAL
        else:
            return ThermalState.DANGER

    def _parse_ioreg_thermal(self) -> Dict[str, float]:
        """
        Parse thermal data from ioreg (works without sudo)
        This is the most reliable method for basic temperature data
        """
        temps = {}

        try:
            # Get AppleSMC data
            result = subprocess.run(
                ['ioreg', '-r', '-n', 'AppleSMC', '-d', '1'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse for temperature values
            # Look for patterns like "TC0P" = 45.5
            for line in result.stdout.split('\n'):
                # Temperature keys typically start with 'T'
                match = re.search(r'"(T[A-Z0-9]{3})"\s*=\s*(\d+\.?\d*)', line)
                if match:
                    key = match.group(1)
                    value = float(match.group(2))
                    # SMC reports in different scales, normalize to Celsius
                    if value > 200:  # Likely in centi-degrees
                        value = value / 100
                    elif value > 120:  # Likely in deci-degrees
                        value = value / 10
                    temps[key] = value

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.warning(f"Failed to get ioreg thermal data: {e}")

        return temps

    def _parse_osx_cpu_temp(self) -> Optional[float]:
        """
        Try to get CPU temperature using osx-cpu-temp if available
        Install with: brew install osx-cpu-temp
        """
        try:
            result = subprocess.run(
                ['osx-cpu-temp'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Output like: "65.0°C"
                match = re.search(r'([\d.]+)', result.stdout)
                if match:
                    return float(match.group(1))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

    def _parse_istats(self) -> Dict[str, float]:
        """
        Parse thermal data from iStats if available
        Install with: gem install iStats
        """
        temps = {}

        try:
            result = subprocess.run(
                ['istats', '--no-graphs'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    # Parse lines like "CPU temp: 65.0°C"
                    if 'CPU temp' in line:
                        match = re.search(r'([\d.]+)', line)
                        if match:
                            temps['cpu'] = float(match.group(1))
                    elif 'GPU temp' in line:
                        match = re.search(r'([\d.]+)', line)
                        if match:
                            temps['gpu'] = float(match.group(1))
                    elif 'Battery temp' in line:
                        match = re.search(r'([\d.]+)', line)
                        if match:
                            temps['battery'] = float(match.group(1))
                    elif 'Fan' in line and 'rpm' in line.lower():
                        match = re.search(r'Fan\s*(\d+)[^:]*:\s*(\d+)', line)
                        if match:
                            fan_num = match.group(1)
                            rpm = int(match.group(2))
                            temps[f'fan_{fan_num}'] = rpm

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return temps

    def _get_fan_speeds(self) -> Dict[str, int]:
        """Get fan speeds from SMC"""
        fans = {}

        try:
            result = subprocess.run(
                ['ioreg', '-r', '-n', 'AppleSMC', '-d', '1'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Look for fan speed patterns (F0Ac, F1Ac, etc.)
            for line in result.stdout.split('\n'):
                match = re.search(r'"(F\dAc)"\s*=\s*(\d+)', line)
                if match:
                    fan_id = match.group(1)
                    rpm = int(match.group(2))
                    fans[fan_id] = rpm

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass

        return fans

    def _detect_throttle(self, cpu_temp: float, cpu_percent: Optional[float] = None) -> ThrottleState:
        """
        Detect CPU throttling based on temperature and CPU usage patterns

        Throttling indicators:
        - High temperature (>85°C) + lower than expected CPU usage
        - Sudden CPU frequency drops
        - kernel_task high CPU (macOS thermal protection)
        """
        # Check kernel_task CPU usage (macOS thermal throttle indicator)
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                if proc.info['name'] == 'kernel_task':
                    kernel_cpu = proc.info['cpu_percent']
                    if kernel_cpu > 100:  # kernel_task using >100% CPU
                        if cpu_temp > self.THRESHOLDS[ThermalState.CRITICAL]:
                            return ThrottleState.EMERGENCY
                        elif cpu_temp > self.THRESHOLDS[ThermalState.HOT]:
                            return ThrottleState.HEAVY
                        else:
                            return ThrottleState.MODERATE
                    elif kernel_cpu > 50:
                        return ThrottleState.LIGHT
        except Exception:
            pass

        # Temperature-based throttle estimation
        if cpu_temp >= self.THRESHOLDS[ThermalState.DANGER]:
            return ThrottleState.EMERGENCY
        elif cpu_temp >= self.THRESHOLDS[ThermalState.CRITICAL]:
            return ThrottleState.HEAVY
        elif cpu_temp >= self.THRESHOLDS[ThermalState.HOT]:
            return ThrottleState.MODERATE
        elif cpu_temp >= self.THRESHOLDS[ThermalState.WARM] + 5:  # 75°C
            return ThrottleState.LIGHT

        return ThrottleState.NONE

    def _generate_recommendations(self, status: 'ThermalStatus') -> List[str]:
        """Generate recommendations based on thermal status"""
        recommendations = []

        if status.throttle_state != ThrottleState.NONE:
            recommendations.append("⚠️ CPU is being throttled - performance reduced")

        if status.cpu_state == ThermalState.DANGER:
            recommendations.append("🚨 CRITICAL: CPU temperature dangerously high!")
            recommendations.append("   - Immediately reduce workload")
            recommendations.append("   - Check for blocked ventilation")
            recommendations.append("   - Consider shutting down to prevent damage")
        elif status.cpu_state == ThermalState.CRITICAL:
            recommendations.append("🔴 HIGH: CPU temperature in critical range")
            recommendations.append("   - Close resource-intensive applications")
            recommendations.append("   - Ensure good airflow around device")
            recommendations.append("   - Consider using a cooling pad")
        elif status.cpu_state == ThermalState.HOT:
            recommendations.append("🟡 WARM: CPU under heavy load")
            recommendations.append("   - Monitor for continued temperature rise")
            recommendations.append("   - Close unnecessary background apps")

        # Fan recommendations
        max_fan = max(status.fan_speeds.values()) if status.fan_speeds else 0
        if max_fan == 0 and status.cpu_temp > 60:
            recommendations.append("ℹ️ Fans not detected or not running - may be passive cooling")
        elif max_fan > 5000:
            recommendations.append("🌀 Fans running at high speed")

        # Battery thermal
        if status.battery_temp > 40:
            recommendations.append("🔋 Battery temperature elevated - avoid charging during heavy use")

        # Trend analysis
        if len(self._history) >= 5:
            recent_temps = [h.cpu_temp for h in self._history[-5:]]
            if all(recent_temps[i] < recent_temps[i+1] for i in range(len(recent_temps)-1)):
                recommendations.append("📈 Temperature rising consistently - consider reducing load")

        return recommendations

    def get_status(self, include_sensors: bool = True) -> ThermalStatus:
        """
        Get comprehensive thermal status

        Args:
            include_sensors: Include detailed sensor readings

        Returns:
            ThermalStatus object with all thermal data
        """
        sensors = []
        temps = {}

        # Try multiple sources for temperature data
        # 1. Try osx-cpu-temp first (most accurate)
        cpu_temp = self._parse_osx_cpu_temp()
        if cpu_temp:
            temps['cpu'] = cpu_temp

        # 2. Try iStats
        istats_data = self._parse_istats()
        if istats_data:
            if 'cpu' not in temps and 'cpu' in istats_data:
                temps['cpu'] = istats_data['cpu']
            if 'gpu' in istats_data:
                temps['gpu'] = istats_data['gpu']
            if 'battery' in istats_data:
                temps['battery'] = istats_data['battery']

        # 3. Parse ioreg for additional sensors
        ioreg_temps = self._parse_ioreg_thermal()
        for key, value in ioreg_temps.items():
            if 30 < value < 120:  # Sanity check for valid temps
                if include_sensors:
                    state = self._get_temperature_state(value)
                    sensors.append(ThermalReading(
                        name=key,
                        temperature=value,
                        state=state,
                        location=self._classify_sensor_location(key)
                    ))

                # Map to main categories if not already set
                if key.startswith('TC') and 'cpu' not in temps:
                    temps['cpu'] = value
                elif key.startswith('TG') and 'gpu' not in temps:
                    temps['gpu'] = value
                elif key.startswith('TB') and 'battery' not in temps:
                    temps['battery'] = value
                elif key.startswith('TA') and 'ambient' not in temps:
                    temps['ambient'] = value

        # Default values if sensors not available
        cpu_temp = temps.get('cpu', 0)
        gpu_temp = temps.get('gpu', 0)
        battery_temp = temps.get('battery', 0)
        ambient_temp = temps.get('ambient', 0)

        # Get fan speeds
        fan_speeds = self._get_fan_speeds()
        # Also check iStats fans
        for key, value in istats_data.items():
            if key.startswith('fan_'):
                fan_speeds[key] = int(value)

        # Determine states
        cpu_state = self._get_temperature_state(cpu_temp) if cpu_temp else ThermalState.COOL
        throttle_state = self._detect_throttle(cpu_temp)

        # Create status object
        status = ThermalStatus(
            cpu_temp=cpu_temp,
            gpu_temp=gpu_temp,
            battery_temp=battery_temp,
            ambient_temp=ambient_temp,
            cpu_state=cpu_state,
            throttle_state=throttle_state,
            fan_speeds=fan_speeds,
            sensors=sensors,
            is_apple_silicon=self.is_apple_silicon,
            timestamp=time.time()
        )

        # Generate recommendations
        status.recommendations = self._generate_recommendations(status)

        # Update history
        self._last_status = status
        self._history.append(status)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        return status

    def _classify_sensor_location(self, sensor_key: str) -> str:
        """Classify sensor location based on key"""
        if sensor_key.startswith('TC'):
            return 'CPU'
        elif sensor_key.startswith('TG'):
            return 'GPU'
        elif sensor_key.startswith('TB'):
            return 'Battery'
        elif sensor_key.startswith('TA'):
            return 'Ambient'
        elif sensor_key.startswith('TH'):
            return 'Heatsink'
        elif sensor_key.startswith('TM'):
            return 'Memory'
        elif sensor_key.startswith('Tp'):
            return 'Power Supply'
        elif sensor_key.startswith('TW'):
            return 'Wireless'
        else:
            return 'Unknown'

    def get_temperature_emoji(self, state: ThermalState) -> str:
        """Get emoji for thermal state"""
        emojis = {
            ThermalState.COOL: "❄️",
            ThermalState.WARM: "🟢",
            ThermalState.HOT: "🟡",
            ThermalState.CRITICAL: "🔴",
            ThermalState.DANGER: "🔥",
        }
        return emojis.get(state, "❓")

    def get_throttle_emoji(self, state: ThrottleState) -> str:
        """Get emoji for throttle state"""
        emojis = {
            ThrottleState.NONE: "✅",
            ThrottleState.LIGHT: "⚡",
            ThrottleState.MODERATE: "⚠️",
            ThrottleState.HEAVY: "🐢",
            ThrottleState.EMERGENCY: "🚨",
        }
        return emojis.get(state, "❓")

    def is_throttling(self) -> bool:
        """Quick check if CPU is currently throttling"""
        if self._last_status:
            return self._last_status.throttle_state != ThrottleState.NONE
        status = self.get_status(include_sensors=False)
        return status.throttle_state != ThrottleState.NONE

    def get_trend(self) -> str:
        """Get temperature trend from history"""
        if len(self._history) < 3:
            return "stable"

        recent = [h.cpu_temp for h in self._history[-3:]]
        avg_change = (recent[-1] - recent[0]) / len(recent)

        if avg_change > 2:
            return "rising_fast"
        elif avg_change > 0.5:
            return "rising"
        elif avg_change < -2:
            return "cooling_fast"
        elif avg_change < -0.5:
            return "cooling"
        else:
            return "stable"


def main():
    """Test the thermal monitor"""
    monitor = ThermalMonitor()

    print("=" * 60)
    print("Thermal Monitor Test")
    print("=" * 60)

    print(f"\n🖥️  Platform: {'Apple Silicon' if monitor.is_apple_silicon else 'Intel'}")

    status = monitor.get_status()

    print(f"\n🌡️  Temperatures:")
    print(f"   CPU:     {status.cpu_temp:.1f}°C {monitor.get_temperature_emoji(status.cpu_state)}")
    if status.gpu_temp:
        print(f"   GPU:     {status.gpu_temp:.1f}°C")
    if status.battery_temp:
        print(f"   Battery: {status.battery_temp:.1f}°C")
    if status.ambient_temp:
        print(f"   Ambient: {status.ambient_temp:.1f}°C")

    print(f"\n🎚️  States:")
    print(f"   Thermal:  {status.cpu_state.value} {monitor.get_temperature_emoji(status.cpu_state)}")
    print(f"   Throttle: {status.throttle_state.value} {monitor.get_throttle_emoji(status.throttle_state)}")

    if status.fan_speeds:
        print(f"\n🌀 Fan Speeds:")
        for fan, rpm in status.fan_speeds.items():
            print(f"   {fan}: {rpm} RPM")

    if status.sensors:
        print(f"\n📊 All Sensors ({len(status.sensors)} detected):")
        for sensor in sorted(status.sensors, key=lambda x: x.temperature, reverse=True)[:10]:
            print(f"   {sensor.name:8s} ({sensor.location:10s}): {sensor.temperature:.1f}°C")

    if status.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in status.recommendations:
            print(f"   {rec}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
