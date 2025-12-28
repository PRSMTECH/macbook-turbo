#!/usr/bin/env python3
"""
Disk Cleaner Module
Intelligent cache and temporary file cleanup for macOS
Inspired by: Mole, mac-cleanup-py, MacCleaner patterns
"""

import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from pathlib import Path
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CleanupCategory(Enum):
    """Categories of cleanable items"""
    SYSTEM_CACHE = "system_cache"
    USER_CACHE = "user_cache"
    BROWSER_CACHE = "browser_cache"
    DEV_CACHE = "dev_cache"
    LOGS = "logs"
    TEMP_FILES = "temp_files"
    TRASH = "trash"
    DOWNLOADS = "downloads"
    XCODE = "xcode"
    IOS_DEVICE = "ios_device"


@dataclass
class CleanupTarget:
    """Definition of a cleanup target"""
    path: str
    category: CleanupCategory
    description: str
    safe_to_delete: bool = True
    requires_sudo: bool = False
    min_age_days: int = 0  # Only delete files older than this
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class CleanupResult:
    """Result of a cleanup operation"""
    target: str
    category: CleanupCategory
    bytes_freed: int
    files_deleted: int
    errors: List[str] = field(default_factory=list)
    skipped: bool = False
    dry_run: bool = False


class DiskCleaner:
    """
    Intelligent disk cleanup system for macOS

    Features:
    - Multi-category cleanup (caches, logs, temp files, etc.)
    - Developer-aware: protects active project files
    - Dry-run mode for preview
    - Age-based filtering
    - Size reporting
    """

    def __init__(self, home_dir: Optional[str] = None):
        self.home_dir = Path(home_dir or os.path.expanduser("~"))
        self.cleanup_targets = self._initialize_targets()
        self._total_freed = 0
        self._total_files = 0

    def _initialize_targets(self) -> List[CleanupTarget]:
        """Initialize all cleanup targets"""
        home = str(self.home_dir)

        return [
            # System caches
            CleanupTarget(
                path=f"{home}/Library/Caches",
                category=CleanupCategory.USER_CACHE,
                description="User application caches",
                exclude_patterns=["com.apple.*", "CloudKit", "com.spotify.*"]
            ),

            # Browser caches
            CleanupTarget(
                path=f"{home}/Library/Caches/Google/Chrome",
                category=CleanupCategory.BROWSER_CACHE,
                description="Chrome browser cache"
            ),
            CleanupTarget(
                path=f"{home}/Library/Caches/com.google.Chrome",
                category=CleanupCategory.BROWSER_CACHE,
                description="Chrome app cache"
            ),
            CleanupTarget(
                path=f"{home}/Library/Caches/Firefox",
                category=CleanupCategory.BROWSER_CACHE,
                description="Firefox browser cache"
            ),
            CleanupTarget(
                path=f"{home}/Library/Caches/com.apple.Safari",
                category=CleanupCategory.BROWSER_CACHE,
                description="Safari browser cache"
            ),
            CleanupTarget(
                path=f"{home}/Library/Safari/LocalStorage",
                category=CleanupCategory.BROWSER_CACHE,
                description="Safari local storage",
                min_age_days=7
            ),

            # Development caches
            CleanupTarget(
                path=f"{home}/.npm/_cacache",
                category=CleanupCategory.DEV_CACHE,
                description="NPM cache"
            ),
            CleanupTarget(
                path=f"{home}/.yarn/cache",
                category=CleanupCategory.DEV_CACHE,
                description="Yarn cache"
            ),
            CleanupTarget(
                path=f"{home}/.pnpm-store",
                category=CleanupCategory.DEV_CACHE,
                description="PNPM store",
                min_age_days=30  # Only old packages
            ),
            CleanupTarget(
                path=f"{home}/.cache/pip",
                category=CleanupCategory.DEV_CACHE,
                description="Pip cache"
            ),
            CleanupTarget(
                path=f"{home}/.cargo/registry/cache",
                category=CleanupCategory.DEV_CACHE,
                description="Cargo registry cache"
            ),
            CleanupTarget(
                path=f"{home}/.gradle/caches",
                category=CleanupCategory.DEV_CACHE,
                description="Gradle caches"
            ),
            CleanupTarget(
                path=f"{home}/.m2/repository",
                category=CleanupCategory.DEV_CACHE,
                description="Maven repository cache",
                min_age_days=60
            ),
            CleanupTarget(
                path=f"{home}/go/pkg/mod/cache",
                category=CleanupCategory.DEV_CACHE,
                description="Go module cache"
            ),
            CleanupTarget(
                path=f"{home}/.cache/homebrew",
                category=CleanupCategory.DEV_CACHE,
                description="Homebrew cache"
            ),
            CleanupTarget(
                path="/usr/local/Homebrew/Library/Taps",
                category=CleanupCategory.DEV_CACHE,
                description="Homebrew taps cache",
                safe_to_delete=False  # Keep taps
            ),

            # Logs
            CleanupTarget(
                path=f"{home}/Library/Logs",
                category=CleanupCategory.LOGS,
                description="User application logs",
                min_age_days=7,
                exclude_patterns=["DiagnosticReports"]
            ),
            CleanupTarget(
                path="/var/log",
                category=CleanupCategory.LOGS,
                description="System logs",
                requires_sudo=True,
                min_age_days=14
            ),
            CleanupTarget(
                path=f"{home}/Library/Logs/DiagnosticReports",
                category=CleanupCategory.LOGS,
                description="Crash reports",
                min_age_days=30
            ),

            # Temporary files
            CleanupTarget(
                path="/tmp",
                category=CleanupCategory.TEMP_FILES,
                description="System temp files",
                min_age_days=1
            ),
            CleanupTarget(
                path="/private/var/folders",
                category=CleanupCategory.TEMP_FILES,
                description="Private temp folders",
                requires_sudo=True,
                min_age_days=3
            ),
            CleanupTarget(
                path=f"{home}/Library/Application Support/CrashReporter",
                category=CleanupCategory.TEMP_FILES,
                description="Crash reporter data",
                min_age_days=7
            ),

            # Xcode
            CleanupTarget(
                path=f"{home}/Library/Developer/Xcode/DerivedData",
                category=CleanupCategory.XCODE,
                description="Xcode derived data"
            ),
            CleanupTarget(
                path=f"{home}/Library/Developer/Xcode/Archives",
                category=CleanupCategory.XCODE,
                description="Xcode archives",
                min_age_days=30
            ),
            CleanupTarget(
                path=f"{home}/Library/Developer/Xcode/iOS DeviceSupport",
                category=CleanupCategory.IOS_DEVICE,
                description="iOS device support files",
                min_age_days=60
            ),
            CleanupTarget(
                path=f"{home}/Library/Developer/CoreSimulator/Caches",
                category=CleanupCategory.XCODE,
                description="iOS Simulator caches"
            ),

            # Trash
            CleanupTarget(
                path=f"{home}/.Trash",
                category=CleanupCategory.TRASH,
                description="User trash",
                min_age_days=7
            ),

            # Downloads (optional, conservative)
            CleanupTarget(
                path=f"{home}/Downloads",
                category=CleanupCategory.DOWNLOADS,
                description="Downloads folder",
                safe_to_delete=False,  # Requires explicit opt-in
                min_age_days=30
            ),

            # Docker
            CleanupTarget(
                path=f"{home}/Library/Containers/com.docker.docker/Data/vms",
                category=CleanupCategory.DEV_CACHE,
                description="Docker VM data",
                safe_to_delete=False  # Can break Docker
            ),

            # VS Code / Cursor
            CleanupTarget(
                path=f"{home}/Library/Application Support/Code/Cache",
                category=CleanupCategory.DEV_CACHE,
                description="VS Code cache"
            ),
            CleanupTarget(
                path=f"{home}/Library/Application Support/Code/CachedExtensions",
                category=CleanupCategory.DEV_CACHE,
                description="VS Code extension cache"
            ),
            CleanupTarget(
                path=f"{home}/Library/Application Support/Cursor/Cache",
                category=CleanupCategory.DEV_CACHE,
                description="Cursor IDE cache"
            ),

            # Spotify
            CleanupTarget(
                path=f"{home}/Library/Application Support/Spotify/PersistentCache",
                category=CleanupCategory.USER_CACHE,
                description="Spotify cache"
            ),

            # Slack
            CleanupTarget(
                path=f"{home}/Library/Application Support/Slack/Cache",
                category=CleanupCategory.USER_CACHE,
                description="Slack cache"
            ),
            CleanupTarget(
                path=f"{home}/Library/Application Support/Slack/Service Worker/CacheStorage",
                category=CleanupCategory.USER_CACHE,
                description="Slack service worker cache"
            ),

            # Discord
            CleanupTarget(
                path=f"{home}/Library/Application Support/discord/Cache",
                category=CleanupCategory.USER_CACHE,
                description="Discord cache"
            ),
        ]

    def get_size(self, path: str) -> int:
        """Get total size of a path in bytes"""
        total = 0
        path_obj = Path(path)

        if not path_obj.exists():
            return 0

        try:
            if path_obj.is_file():
                return path_obj.stat().st_size

            for entry in path_obj.rglob('*'):
                try:
                    if entry.is_file() and not entry.is_symlink():
                        total += entry.stat().st_size
                except (OSError, PermissionError):
                    pass
        except (OSError, PermissionError):
            pass

        return total

    def format_size(self, bytes_size: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} PB"

    def _should_delete(self, path: Path, min_age_days: int,
                       exclude_patterns: List[str]) -> bool:
        """Check if a file/folder should be deleted"""
        # Check exclusion patterns
        for pattern in exclude_patterns:
            if pattern in str(path):
                return False

        # Check age
        if min_age_days > 0:
            try:
                mtime = path.stat().st_mtime
                age_days = (time.time() - mtime) / (24 * 3600)
                if age_days < min_age_days:
                    return False
            except (OSError, PermissionError):
                return False

        return True

    def _delete_path(self, path: Path, min_age_days: int = 0,
                     exclude_patterns: List[str] = None) -> Tuple[int, int, List[str]]:
        """
        Delete a path (file or directory)
        Returns: (bytes_freed, files_deleted, errors)
        """
        exclude_patterns = exclude_patterns or []
        bytes_freed = 0
        files_deleted = 0
        errors = []

        if not path.exists():
            return 0, 0, []

        try:
            if path.is_file():
                if self._should_delete(path, min_age_days, exclude_patterns):
                    size = path.stat().st_size
                    path.unlink()
                    return size, 1, []
                return 0, 0, []

            # Directory: iterate and delete eligible items
            for item in list(path.rglob('*')):
                try:
                    if item.is_file() and not item.is_symlink():
                        if self._should_delete(item, min_age_days, exclude_patterns):
                            size = item.stat().st_size
                            item.unlink()
                            bytes_freed += size
                            files_deleted += 1
                except PermissionError:
                    errors.append(f"Permission denied: {item}")
                except OSError as e:
                    errors.append(f"Error deleting {item}: {e}")

            # Clean up empty directories
            for item in sorted(path.rglob('*'), key=lambda x: len(str(x)), reverse=True):
                try:
                    if item.is_dir() and not any(item.iterdir()):
                        item.rmdir()
                except (OSError, PermissionError):
                    pass

        except PermissionError:
            errors.append(f"Permission denied: {path}")
        except OSError as e:
            errors.append(f"Error processing {path}: {e}")

        return bytes_freed, files_deleted, errors

    def analyze(self, categories: Optional[List[CleanupCategory]] = None) -> Dict[CleanupCategory, int]:
        """
        Analyze disk usage by category
        Returns dict of category -> bytes
        """
        results = {}

        for target in self.cleanup_targets:
            if categories and target.category not in categories:
                continue

            if not target.safe_to_delete:
                continue

            size = self.get_size(target.path)
            if target.category not in results:
                results[target.category] = 0
            results[target.category] += size

        return results

    def clean(self, categories: Optional[List[CleanupCategory]] = None,
              dry_run: bool = False,
              include_unsafe: bool = False,
              progress_callback: Optional[Callable[[str, int, int], None]] = None) -> List[CleanupResult]:
        """
        Perform cleanup operation

        Args:
            categories: List of categories to clean (None = all safe)
            dry_run: If True, only report what would be deleted
            include_unsafe: If True, include targets marked as unsafe
            progress_callback: Function(target_name, current, total) for progress updates

        Returns:
            List of CleanupResult objects
        """
        results = []
        targets = [t for t in self.cleanup_targets
                   if (categories is None or t.category in categories)
                   and (include_unsafe or t.safe_to_delete)
                   and not t.requires_sudo]

        total = len(targets)

        for i, target in enumerate(targets):
            if progress_callback:
                progress_callback(target.description, i + 1, total)

            path = Path(target.path)

            if not path.exists():
                results.append(CleanupResult(
                    target=target.path,
                    category=target.category,
                    bytes_freed=0,
                    files_deleted=0,
                    skipped=True,
                    dry_run=dry_run
                ))
                continue

            if dry_run:
                size = self.get_size(target.path)
                results.append(CleanupResult(
                    target=target.path,
                    category=target.category,
                    bytes_freed=size,
                    files_deleted=0,
                    dry_run=True
                ))
            else:
                bytes_freed, files_deleted, errors = self._delete_path(
                    path,
                    target.min_age_days,
                    target.exclude_patterns
                )
                results.append(CleanupResult(
                    target=target.path,
                    category=target.category,
                    bytes_freed=bytes_freed,
                    files_deleted=files_deleted,
                    errors=errors,
                    dry_run=False
                ))
                self._total_freed += bytes_freed
                self._total_files += files_deleted

        return results

    def clean_dns_cache(self) -> bool:
        """Flush DNS cache"""
        try:
            subprocess.run(
                ["dscacheutil", "-flushcache"],
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["sudo", "killall", "-HUP", "mDNSResponder"],
                capture_output=True,
                check=False  # May fail without sudo
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def clean_homebrew(self) -> Tuple[int, str]:
        """
        Clean Homebrew caches and old versions
        Returns: (bytes_freed, output)
        """
        try:
            # Get initial size
            brew_cache = Path("/usr/local/Homebrew/Library/Homebrew/vendor")
            initial_size = self.get_size(str(brew_cache))

            # Run cleanup
            result = subprocess.run(
                ["brew", "cleanup", "-s"],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Get final size
            final_size = self.get_size(str(brew_cache))
            freed = max(0, initial_size - final_size)

            return freed, result.stdout + result.stderr
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            return 0, str(e)

    def clean_docker(self) -> Tuple[int, str]:
        """
        Clean Docker unused resources
        Returns: (bytes_freed, output)
        """
        try:
            result = subprocess.run(
                ["docker", "system", "prune", "-f"],
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse output for reclaimed space
            output = result.stdout + result.stderr
            freed = 0

            # Docker reports like "Total reclaimed space: 1.5GB"
            import re
            match = re.search(r'reclaimed space:\s*([\d.]+)\s*([KMGT]?B)', output, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2).upper()
                multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
                freed = int(value * multipliers.get(unit, 1))

            return freed, output
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            return 0, str(e)

    def get_total_freed(self) -> int:
        """Get total bytes freed in this session"""
        return self._total_freed

    def get_total_files(self) -> int:
        """Get total files deleted in this session"""
        return self._total_files

    def get_disk_usage(self) -> Dict[str, any]:
        """Get current disk usage statistics"""
        usage = shutil.disk_usage(str(self.home_dir))
        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent_used': (usage.used / usage.total) * 100,
            'total_formatted': self.format_size(usage.total),
            'used_formatted': self.format_size(usage.used),
            'free_formatted': self.format_size(usage.free),
        }


def main():
    """Test the disk cleaner"""
    cleaner = DiskCleaner()

    print("=" * 60)
    print("Disk Cleaner Analysis")
    print("=" * 60)

    # Show disk usage
    usage = cleaner.get_disk_usage()
    print(f"\n💾 Disk Usage: {usage['used_formatted']} / {usage['total_formatted']} ({usage['percent_used']:.1f}%)")
    print(f"   Free: {usage['free_formatted']}")

    # Analyze by category
    print("\n📊 Cleanable Space by Category:")
    print("-" * 60)

    analysis = cleaner.analyze()
    total_cleanable = 0

    for category, size in sorted(analysis.items(), key=lambda x: x[1], reverse=True):
        if size > 0:
            print(f"   {category.value:20s}: {cleaner.format_size(size):>12s}")
            total_cleanable += size

    print("-" * 60)
    print(f"   {'TOTAL':20s}: {cleaner.format_size(total_cleanable):>12s}")

    # Dry run
    print("\n🔍 Dry Run (preview):")
    print("-" * 60)

    results = cleaner.clean(
        categories=[CleanupCategory.USER_CACHE, CleanupCategory.BROWSER_CACHE],
        dry_run=True
    )

    for result in results:
        if result.bytes_freed > 0:
            print(f"   Would free: {cleaner.format_size(result.bytes_freed):>10s} from {result.target}")

    print("\n" + "=" * 60)
    print("Run with dry_run=False to actually clean")


if __name__ == "__main__":
    main()
