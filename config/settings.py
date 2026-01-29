#!/usr/bin/env python3
"""
Settings persistence for MacBook Turbo CPU Monitor.

Saves user preferences to ~/Library/Preferences/com.prsmtech.macbookturbo.json
"""

import json
import os
from pathlib import Path
from typing import Any, Optional
from enum import Enum


# Default settings
DEFAULTS = {
    "auto_clean_mode": "off",  # off, conservative, balanced, aggressive
    "show_detailed": False,
    "cooldown_seconds": 30,
    "cpu_threshold_conservative": 90,
    "cpu_threshold_balanced": 80,
    "cpu_threshold_aggressive": 70,
    "update_interval_seconds": 2,
    "enable_notifications": True,
    "enable_sound": False,
}

SETTINGS_PATH = Path.home() / "Library" / "Preferences" / "com.prsmtech.macbookturbo.json"


class Settings:
    """Thread-safe settings manager with file persistence."""

    _instance: Optional["Settings"] = None
    _settings: dict[str, Any]

    def __new__(cls) -> "Settings":
        """Singleton pattern to ensure one settings instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = {}
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        """Load settings from file, using defaults for missing values."""
        self._settings = DEFAULTS.copy()

        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, "r") as f:
                    saved = json.load(f)
                    # Merge saved settings with defaults
                    for key, value in saved.items():
                        if key in DEFAULTS:
                            self._settings[key] = value
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings: {e}")
                # Keep defaults on error

    def _save(self) -> None:
        """Save current settings to file."""
        try:
            # Ensure directory exists
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

            with open(SETTINGS_PATH, "w") as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default if default is not None else DEFAULTS.get(key))

    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a setting value and optionally save to disk."""
        self._settings[key] = value
        if save:
            self._save()

    def reset(self, key: Optional[str] = None) -> None:
        """Reset one or all settings to defaults."""
        if key is None:
            self._settings = DEFAULTS.copy()
        elif key in DEFAULTS:
            self._settings[key] = DEFAULTS[key]
        self._save()

    # Convenience properties for common settings

    @property
    def auto_clean_mode(self) -> str:
        """Get the auto-clean mode (off, conservative, balanced, aggressive)."""
        return self.get("auto_clean_mode")

    @auto_clean_mode.setter
    def auto_clean_mode(self, value: str) -> None:
        """Set the auto-clean mode."""
        valid_modes = ["off", "conservative", "balanced", "aggressive"]
        if value.lower() in valid_modes:
            self.set("auto_clean_mode", value.lower())

    @property
    def show_detailed(self) -> bool:
        """Get whether to show detailed view."""
        return self.get("show_detailed")

    @show_detailed.setter
    def show_detailed(self, value: bool) -> None:
        """Set whether to show detailed view."""
        self.set("show_detailed", bool(value))

    @property
    def cooldown_seconds(self) -> int:
        """Get the cooldown period between cleanups."""
        return self.get("cooldown_seconds")

    @cooldown_seconds.setter
    def cooldown_seconds(self, value: int) -> None:
        """Set the cooldown period (minimum 10 seconds)."""
        self.set("cooldown_seconds", max(10, int(value)))

    @property
    def update_interval(self) -> int:
        """Get the update interval in seconds."""
        return self.get("update_interval_seconds")

    @update_interval.setter
    def update_interval(self, value: int) -> None:
        """Set the update interval (minimum 1 second)."""
        self.set("update_interval_seconds", max(1, int(value)))

    @property
    def enable_notifications(self) -> bool:
        """Get whether notifications are enabled."""
        return self.get("enable_notifications")

    @enable_notifications.setter
    def enable_notifications(self, value: bool) -> None:
        """Set whether notifications are enabled."""
        self.set("enable_notifications", bool(value))

    def get_cpu_threshold(self, mode: Optional[str] = None) -> int:
        """Get CPU threshold for the specified or current mode."""
        mode = mode or self.auto_clean_mode
        if mode == "conservative":
            return self.get("cpu_threshold_conservative")
        elif mode == "balanced":
            return self.get("cpu_threshold_balanced")
        elif mode == "aggressive":
            return self.get("cpu_threshold_aggressive")
        return 100  # Off mode - never trigger

    def to_dict(self) -> dict[str, Any]:
        """Return all settings as a dictionary."""
        return self._settings.copy()


# Convenience function for quick access
def get_settings() -> Settings:
    """Get the singleton Settings instance."""
    return Settings()


if __name__ == "__main__":
    # Test settings module
    settings = get_settings()
    print("Current settings:")
    for key, value in settings.to_dict().items():
        print(f"  {key}: {value}")

    print(f"\nSettings file: {SETTINGS_PATH}")
    print(f"File exists: {SETTINGS_PATH.exists()}")
