#!/usr/bin/env python3
"""
Intel Optimizer for MacBook Turbo.

Intel-Mac specific monitoring and optimization, with special handling for the
thermal-throttle-prone 2018 15" MacBook Pro (MacBookPro15,1 / Core i9-8950HK).

Provides:
- Intel chip + model detection (with known-throttler flagging)
- Turbo Boost state (via Turbo Boost Switcher kext detection)
- Discrete-GPU switching state (gpuswitch: integrated / discrete / automatic)
- Low Power Mode state
- CPU speed-limit / throttle detection (pmset -g therm)
- Model-aware optimization recommendations

This is the Intel counterpart to apple_silicon_monitor.py. Everything here is
read-only and needs no sudo; the privileged toggles (force-integrated GPU,
Low Power Mode, disabling Turbo Boost) live in scripts/optimize-intel.sh.
"""

import subprocess
import platform
import re
import shutil
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class TurboBoostState(Enum):
    """Intel Turbo Boost state."""
    ENABLED = "enabled"     # Default - turbo active (more heat on i9)
    DISABLED = "disabled"   # Turbo Boost Switcher kext loaded
    UNKNOWN = "unknown"


class GPUMode(Enum):
    """Discrete-vs-integrated graphics switching mode (pmset gpuswitch)."""
    INTEGRATED_ONLY = "integrated_only"   # gpuswitch 0 - coolest
    DISCRETE_ONLY = "discrete_only"       # gpuswitch 1 - hottest
    AUTOMATIC = "automatic"               # gpuswitch 2 - macOS default
    UNKNOWN = "unknown"


class PowerMode(Enum):
    """System power mode (pmset lowpowermode)."""
    LOW_POWER = "low_power"
    AUTOMATIC = "automatic"
    UNKNOWN = "unknown"


@dataclass
class IntelCpuInfo:
    """Information about an Intel CPU."""
    brand: str                       # Full brand string
    physical_cores: int
    logical_cores: int
    base_freq_ghz: Optional[float]
    max_turbo_ghz: Optional[float]


@dataclass
class IntelStatus:
    """Comprehensive status for an Intel Mac."""
    model_name: str
    model_identifier: str
    cpu: IntelCpuInfo
    turbo_state: TurboBoostState
    gpu_mode: GPUMode
    has_discrete_gpu: bool
    power_mode: PowerMode
    speed_limit_percent: int          # 100 = full speed, <100 = throttled
    is_throttled: bool
    is_throttle_prone_model: bool     # e.g. 2018 i9 MacBookPro15,1
    turbo_switcher_installed: bool
    recommendations: List[str] = field(default_factory=list)


class IntelOptimizer:
    """Monitor and advise optimizations for Intel Macs."""

    # Model identifiers with known severe thermal-throttling under sustained
    # load (the chassis can't dissipate the i9's heat -> VRM/thermal throttle).
    # For these, disabling Turbo Boost often RAISES sustained performance.
    THROTTLE_PRONE_MODELS = {
        "MacBookPro15,1": "2018 15\" MacBook Pro (Core i9-8950HK / i7-8850H)",
        "MacBookPro15,3": "2019 15\" MacBook Pro (Core i9-9980HK)",
        "MacBookPro16,1": "2019 16\" MacBook Pro (Core i9-9880H)",
        "MacBookPro11,3": "2014 15\" MacBook Pro (quad-core, aged paste)",
    }

    # Known max turbo clocks for common mobile i-series chips (GHz).
    KNOWN_TURBO_GHZ = {
        "i9-8950hk": 4.8,
        "i9-9980hk": 5.0,
        "i9-9880h": 4.8,
        "i7-8850h": 4.3,
        "i7-9750h": 4.5,
        "i7-8559u": 4.5,
        "i5-8259u": 3.8,
    }

    # Turbo Boost Switcher kext bundle id (rugarciap) used to detect disabled state.
    TURBO_KEXT_PATTERNS = ("rugarciap", "DisableTurboBoost", "TurboBoost")

    def __init__(self):
        self._is_intel: Optional[bool] = None
        self._cpu_info: Optional[IntelCpuInfo] = None
        self._model_identifier: Optional[str] = None
        self._model_name: Optional[str] = None

    @property
    def is_intel(self) -> bool:
        """Check if running on an Intel Mac."""
        if self._is_intel is None:
            self._is_intel = platform.machine() == "x86_64"
        return self._is_intel

    def _sysctl(self, key: str) -> str:
        """Read a sysctl value as a stripped string ('' on failure)."""
        try:
            result = subprocess.run(
                ["sysctl", "-n", key],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def get_model_identifier(self) -> str:
        """Get the hardware model identifier (e.g. MacBookPro15,1)."""
        if self._model_identifier is None:
            self._model_identifier = self._sysctl("hw.model") or "Unknown"
        return self._model_identifier

    def get_model_name(self) -> str:
        """Get a friendly model name (falls back to the identifier)."""
        if self._model_name is not None:
            return self._model_name

        identifier = self.get_model_identifier()
        # Prefer the human description we know for throttle-prone models.
        self._model_name = self.THROTTLE_PRONE_MODELS.get(identifier, identifier)
        return self._model_name

    def get_cpu_info(self) -> IntelCpuInfo:
        """Get Intel CPU details."""
        if self._cpu_info is not None:
            return self._cpu_info

        brand = self._sysctl("machdep.cpu.brand_string") or "Unknown Intel CPU"

        try:
            physical = int(self._sysctl("hw.physicalcpu") or 0)
        except ValueError:
            physical = 0
        try:
            logical = int(self._sysctl("hw.logicalcpu") or 0)
        except ValueError:
            logical = 0

        # Base frequency: hw.cpufrequency is in Hz on Intel Macs.
        base_ghz: Optional[float] = None
        freq_hz = self._sysctl("hw.cpufrequency")
        if freq_hz.isdigit():
            base_ghz = round(int(freq_hz) / 1_000_000_000, 1)
        else:
            # Fall back to parsing "@ 2.90GHz" from the brand string.
            m = re.search(r"@\s*([\d.]+)\s*GHz", brand)
            if m:
                base_ghz = float(m.group(1))

        # Max turbo: look up by chip model token in the brand string.
        max_turbo: Optional[float] = None
        brand_lower = brand.lower()
        for token, ghz in self.KNOWN_TURBO_GHZ.items():
            if token in brand_lower:
                max_turbo = ghz
                break

        self._cpu_info = IntelCpuInfo(
            brand=brand,
            physical_cores=physical,
            logical_cores=logical,
            base_freq_ghz=base_ghz,
            max_turbo_ghz=max_turbo,
        )
        return self._cpu_info

    def get_turbo_state(self) -> TurboBoostState:
        """
        Detect Turbo Boost state.

        There is no public sysctl for turbo state without sudo, so we detect
        the Turbo Boost Switcher kernel extension. If its kext is loaded,
        Turbo Boost is disabled; otherwise it is at its (enabled) default.
        """
        try:
            result = subprocess.run(
                ["kextstat", "-l"],
                capture_output=True, text=True, timeout=5
            )
            out = result.stdout.lower()
            if any(p.lower() in out for p in self.TURBO_KEXT_PATTERNS):
                return TurboBoostState.DISABLED
            return TurboBoostState.ENABLED
        except Exception:
            return TurboBoostState.UNKNOWN

    def turbo_switcher_installed(self) -> bool:
        """Check whether Turbo Boost Switcher (app or CLI) is available."""
        if shutil.which("turbo-boost") or shutil.which("tbswitcher"):
            return True
        import os
        return os.path.exists("/Applications/Turbo Boost Switcher.app")

    def get_gpu_mode(self) -> GPUMode:
        """Get the discrete/integrated GPU switching mode from pmset."""
        try:
            result = subprocess.run(
                ["pmset", "-g"],
                capture_output=True, text=True, timeout=5
            )
            m = re.search(r"gpuswitch\s+(\d+)", result.stdout)
            if m:
                val = int(m.group(1))
                return {
                    0: GPUMode.INTEGRATED_ONLY,
                    1: GPUMode.DISCRETE_ONLY,
                    2: GPUMode.AUTOMATIC,
                }.get(val, GPUMode.UNKNOWN)
        except Exception:
            pass
        return GPUMode.UNKNOWN

    def has_discrete_gpu(self) -> bool:
        """Check whether the Mac has a discrete (switchable) GPU."""
        # gpuswitch only appears in pmset output when a dGPU is present.
        return self.get_gpu_mode() != GPUMode.UNKNOWN

    def get_power_mode(self) -> PowerMode:
        """Get Low Power Mode state from pmset."""
        try:
            result = subprocess.run(
                ["pmset", "-g"],
                capture_output=True, text=True, timeout=5
            )
            m = re.search(r"lowpowermode\s+(\d+)", result.stdout)
            if m:
                return PowerMode.LOW_POWER if int(m.group(1)) == 1 else PowerMode.AUTOMATIC
        except Exception:
            pass
        return PowerMode.UNKNOWN

    def get_speed_limit(self) -> int:
        """
        Get the current CPU speed limit percent from pmset -g therm.
        100 = full speed; lower values mean the CPU is being throttled.
        """
        try:
            result = subprocess.run(
                ["pmset", "-g", "therm"],
                capture_output=True, text=True, timeout=5
            )
            m = re.search(r"CPU_Speed_Limit\s*=\s*(\d+)", result.stdout)
            if m:
                return int(m.group(1))
        except Exception:
            pass
        return 100  # Assume full speed if not reported.

    def is_throttle_prone(self) -> bool:
        """Whether this exact model is a known severe thermal throttler."""
        return self.get_model_identifier() in self.THROTTLE_PRONE_MODELS

    def get_status(self) -> IntelStatus:
        """Get a comprehensive Intel optimization status snapshot."""
        cpu = self.get_cpu_info()
        turbo = self.get_turbo_state()
        gpu_mode = self.get_gpu_mode()
        has_dgpu = gpu_mode != GPUMode.UNKNOWN
        power = self.get_power_mode()
        speed_limit = self.get_speed_limit()
        throttle_prone = self.is_throttle_prone()

        status = IntelStatus(
            model_name=self.get_model_name(),
            model_identifier=self.get_model_identifier(),
            cpu=cpu,
            turbo_state=turbo,
            gpu_mode=gpu_mode,
            has_discrete_gpu=has_dgpu,
            power_mode=power,
            speed_limit_percent=speed_limit,
            is_throttled=speed_limit < 100,
            is_throttle_prone_model=throttle_prone,
            turbo_switcher_installed=self.turbo_switcher_installed(),
        )
        status.recommendations = self._generate_recommendations(status)
        return status

    def _generate_recommendations(self, s: IntelStatus) -> List[str]:
        """Generate model-aware optimization recommendations."""
        recs: List[str] = []

        if s.is_throttled:
            recs.append(
                f"CPU throttled to {s.speed_limit_percent}% - thermal limit reached"
            )

        if s.is_throttle_prone_model:
            recs.append(
                "This model throttles hard under sustained load; "
                "disabling Turbo Boost usually RAISES sustained performance"
            )
            if s.turbo_state == TurboBoostState.ENABLED:
                if s.turbo_switcher_installed:
                    recs.append("Run 'optimize-intel.sh turbo-off' to disable Turbo Boost")
                else:
                    recs.append("Install Turbo Boost Switcher to cap heat (see INTEL-OPTIMIZATION.md)")

        if s.has_discrete_gpu and s.gpu_mode in (GPUMode.AUTOMATIC, GPUMode.DISCRETE_ONLY):
            recs.append(
                "Discrete GPU can engage and add heat; "
                "'optimize-intel.sh gpu-integrated' forces the cooler integrated GPU"
            )

        if s.power_mode == PowerMode.AUTOMATIC:
            recs.append("Enable Low Power Mode for a cooler, quieter machine on battery")
        elif s.power_mode == PowerMode.LOW_POWER:
            recs.append("Low Power Mode active - performance is intentionally reduced")

        if not recs:
            recs.append("Intel system operating normally")
        return recs

    # -- display helpers -----------------------------------------------------

    def get_turbo_emoji(self, state: TurboBoostState) -> str:
        return {
            TurboBoostState.ENABLED: "🚀",
            TurboBoostState.DISABLED: "🧊",
            TurboBoostState.UNKNOWN: "⚪",
        }.get(state, "⚪")

    def get_gpu_emoji(self, mode: GPUMode) -> str:
        return {
            GPUMode.INTEGRATED_ONLY: "🧊",
            GPUMode.DISCRETE_ONLY: "🔥",
            GPUMode.AUTOMATIC: "🔀",
            GPUMode.UNKNOWN: "⚪",
        }.get(mode, "⚪")

    def get_speed_limit_emoji(self, percent: int) -> str:
        if percent >= 100:
            return "🟢"
        elif percent >= 80:
            return "🟡"
        elif percent >= 50:
            return "🟠"
        return "🔴"


# Convenience function
def get_intel_optimizer() -> IntelOptimizer:
    """Get an Intel optimizer instance."""
    return IntelOptimizer()


if __name__ == "__main__":
    opt = IntelOptimizer()

    print("Intel Optimizer Test")
    print("=" * 44)

    if not opt.is_intel:
        print("Running on Apple Silicon - Intel features not applicable")
        raise SystemExit(0)

    status = opt.get_status()
    cpu = status.cpu

    print(f"\nModel:   {status.model_name}")
    print(f"         ({status.model_identifier})")
    print(f"CPU:     {cpu.brand}")
    print(f"Cores:   {cpu.physical_cores} physical / {cpu.logical_cores} logical")
    if cpu.base_freq_ghz:
        turbo = f" (turbo {cpu.max_turbo_ghz} GHz)" if cpu.max_turbo_ghz else ""
        print(f"Clocks:  {cpu.base_freq_ghz} GHz base{turbo}")

    print(f"\nTurbo Boost:  {status.turbo_state.value} {opt.get_turbo_emoji(status.turbo_state)}")
    if status.has_discrete_gpu:
        print(f"GPU mode:     {status.gpu_mode.value} {opt.get_gpu_emoji(status.gpu_mode)}")
    print(f"Power mode:   {status.power_mode.value}")
    print(f"Speed limit:  {status.speed_limit_percent}% "
          f"{opt.get_speed_limit_emoji(status.speed_limit_percent)}"
          f"{'  (THROTTLED)' if status.is_throttled else ''}")
    print(f"Throttle-prone model: {status.is_throttle_prone_model}")
    print(f"Turbo Boost Switcher installed: {status.turbo_switcher_installed}")

    print("\nRecommendations:")
    for rec in status.recommendations:
        print(f"  - {rec}")
