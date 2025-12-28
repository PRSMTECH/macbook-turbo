#!/usr/bin/env python3
"""
Process Scoring System
Multi-factor scoring algorithm for intelligent process management
Inspired by: Mole, process-killer, port-killer patterns
"""

import psutil
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessCategory(Enum):
    """Process category classification"""
    SYSTEM_CRITICAL = "system_critical"
    DEVELOPMENT = "development"
    TERMINAL = "terminal"
    BROWSER = "browser"
    COMMUNICATION = "communication"
    CLOUD_SYNC = "cloud_sync"
    MEDIA = "media"
    BACKGROUND = "background"
    UNKNOWN = "unknown"


@dataclass
class ProcessInfo:
    """Detailed process information with scoring"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    num_threads: int
    num_fds: int
    create_time: float
    category: ProcessCategory
    is_protected: bool
    kill_score: float
    children_count: int
    has_open_files_in_home: bool
    cmdline: str = ""
    username: str = ""

    def __str__(self):
        status = "🛡️" if self.is_protected else "⚠️"
        return f"{status} {self.name} (PID:{self.pid}) CPU:{self.cpu_percent:.1f}% MEM:{self.memory_percent:.1f}% Score:{self.kill_score:.1f}"


class ProcessScorer:
    """
    Intelligent process scoring system for safe cleanup decisions

    Scoring factors (higher = more killable):
    - CPU usage (40% weight)
    - Memory usage (30% weight)
    - File descriptor count (10% weight)
    - Process age (10% weight)
    - Category penalty (10% weight)
    - Protection status (-100 if protected)
    """

    # Comprehensive protection whitelist
    PROTECTED_PATTERNS = {
        ProcessCategory.SYSTEM_CRITICAL: [
            r"kernel_task", r"launchd", r"SystemUIServer", r"Finder",
            r"Dock", r"loginwindow", r"WindowServer", r"airportd",
            r"bluetoothd", r"coreaudiod", r"cfprefsd", r"diskarbitrationd",
            r"mds$", r"notifyd", r"securityd", r"trustd", r"usbd",
            r"powerd", r"fseventsd", r"coreduetd", r"symptomsd",
            r"apsd", r"cloudd", r"nsurlsessiond", r"CommCenter",
            r"UserEventAgent", r"syslogd", r"configd", r"opendirectoryd",
        ],
        ProcessCategory.DEVELOPMENT: [
            # IDEs
            r"Code$", r"Code Helper", r"Code - Insiders", r"code-server",
            r"Cursor", r"cursor",
            r"IntelliJ", r"WebStorm", r"PyCharm", r"RubyMine", r"GoLand",
            r"DataGrip", r"Rider", r"CLion", r"PhpStorm", r"AppCode",
            r"Xcode", r"Android Studio", r"Sublime", r"TextEdit",
            r"Nova", r"BBEdit", r"Atom", r"Brackets",
            r"vim", r"nvim", r"emacs", r"nano", r"micro",
            # Dev tools
            r"node$", r"npm", r"yarn", r"pnpm", r"bun",
            r"python[23]?$", r"pip", r"ruby", r"gem", r"bundle",
            r"java$", r"javac", r"gradle", r"maven", r"mvn",
            r"go$", r"cargo", r"rustc", r"rustup",
            r"git$", r"git-", r"gh$",
            r"docker", r"kubectl", r"helm", r"terraform",
            r"aws$", r"gcloud", r"az$",
            r"postgres", r"mysql", r"redis", r"mongo",
            r"nginx", r"apache",
            r"electron",
            r"claude", r"copilot",
            # Language servers
            r"typescript-language", r"pylsp", r"gopls", r"rust-analyzer",
        ],
        ProcessCategory.TERMINAL: [
            r"Terminal$", r"iTerm", r"Hyper", r"Alacritty", r"kitty",
            r"WezTerm", r"Warp", r"Tabby", r"Terminus",
            r"zsh$", r"bash$", r"sh$", r"fish$", r"tcsh$", r"csh$",
            r"ssh$", r"sshd", r"tmux", r"screen", r"mosh",
        ],
    }

    # Processes safe to kill when using high resources
    KILLABLE_PATTERNS = {
        ProcessCategory.BROWSER: [
            r"Chrome Helper", r"Google Chrome Helper",
            r"Safari Web Content", r"Safari Networking",
            r"Firefox", r"firefox-bin",
            r"Brave Browser", r"Microsoft Edge",
            r"Arc Helper", r"Opera",
        ],
        ProcessCategory.COMMUNICATION: [
            r"Slack Helper", r"Discord Helper", r"Teams",
            r"WhatsApp", r"Telegram", r"Signal", r"Messages",
            r"Zoom", r"Skype", r"FaceTime",
        ],
        ProcessCategory.CLOUD_SYNC: [
            r"Dropbox", r"Google Drive", r"OneDrive",
            r"iCloud", r"Box Sync", r"Sync",
        ],
        ProcessCategory.MEDIA: [
            r"Spotify Helper", r"Music$", r"iTunes",
            r"Photos$", r"Preview$", r"QuickTime",
            r"VLC", r"IINA",
        ],
        ProcessCategory.BACKGROUND: [
            r"mds_stores", r"photoanalysisd", r"photolibraryd",
            r"suggestd", r"com\.apple\.photos", r"mediaanalysisd",
            r"bird$", r"commerce", r"ReportCrash",
            r"spindump", r"sysdiagnose", r"tailspind",
            r"analyticsd", r"diagnosticd",
        ],
    }

    # Scoring weights
    WEIGHTS = {
        'cpu': 0.40,
        'memory': 0.30,
        'fds': 0.10,
        'age': 0.10,
        'category': 0.10,
    }

    # Category penalties (lower = less likely to kill)
    CATEGORY_PENALTIES = {
        ProcessCategory.SYSTEM_CRITICAL: -1000,
        ProcessCategory.DEVELOPMENT: -500,
        ProcessCategory.TERMINAL: -500,
        ProcessCategory.BROWSER: 20,
        ProcessCategory.COMMUNICATION: 15,
        ProcessCategory.CLOUD_SYNC: 25,
        ProcessCategory.MEDIA: 10,
        ProcessCategory.BACKGROUND: 30,
        ProcessCategory.UNKNOWN: 0,
    }

    def __init__(self, home_dir: Optional[str] = None):
        self.home_dir = home_dir or os.path.expanduser("~")
        self.current_pid = os.getpid()
        self.parent_pids = self._get_parent_pids()
        self._compiled_patterns: Dict[ProcessCategory, List[re.Pattern]] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance"""
        for category, patterns in {**self.PROTECTED_PATTERNS, **self.KILLABLE_PATTERNS}.items():
            self._compiled_patterns[category] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def _get_parent_pids(self) -> Set[int]:
        """Get all parent PIDs of current process"""
        parents = set()
        try:
            proc = psutil.Process(self.current_pid)
            while proc:
                parents.add(proc.pid)
                proc = proc.parent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return parents

    def _categorize_process(self, name: str, cmdline: str) -> ProcessCategory:
        """Determine process category based on name and command line"""
        search_text = f"{name} {cmdline}"

        # Check protected patterns first
        for category in [ProcessCategory.SYSTEM_CRITICAL, ProcessCategory.DEVELOPMENT, ProcessCategory.TERMINAL]:
            if category in self._compiled_patterns:
                for pattern in self._compiled_patterns[category]:
                    if pattern.search(search_text):
                        return category

        # Check killable patterns
        for category in [ProcessCategory.BROWSER, ProcessCategory.COMMUNICATION,
                        ProcessCategory.CLOUD_SYNC, ProcessCategory.MEDIA, ProcessCategory.BACKGROUND]:
            if category in self._compiled_patterns:
                for pattern in self._compiled_patterns[category]:
                    if pattern.search(search_text):
                        return category

        return ProcessCategory.UNKNOWN

    def _is_protected(self, pid: int, category: ProcessCategory, children_count: int,
                      has_open_files: bool) -> bool:
        """Determine if process should be protected from killing"""
        # Always protect current process tree
        if pid in self.parent_pids:
            return True

        # Protect system-critical and development processes
        if category in [ProcessCategory.SYSTEM_CRITICAL, ProcessCategory.DEVELOPMENT, ProcessCategory.TERMINAL]:
            return True

        # Protect processes with children (likely doing work)
        if children_count > 0:
            return True

        # Protect processes with open files in home directory
        if has_open_files:
            return True

        return False

    def _check_open_files_in_home(self, proc: psutil.Process) -> bool:
        """Check if process has open files in home directory"""
        try:
            for f in proc.open_files():
                if f.path.startswith(self.home_dir):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            pass
        return False

    def _calculate_score(self, cpu: float, memory: float, num_fds: int,
                        age_seconds: float, category: ProcessCategory,
                        is_protected: bool) -> float:
        """
        Calculate kill score (higher = more killable)

        Score components:
        - CPU: 0-100 scaled by usage percentage
        - Memory: 0-100 scaled by usage percentage
        - FDs: 0-50 based on file descriptor count
        - Age: 0-50 based on process age (newer = higher score)
        - Category: penalty/bonus based on process type
        """
        if is_protected:
            return -1000.0

        # Normalize components to 0-100 scale
        cpu_score = min(cpu, 100)
        memory_score = min(memory * 10, 100)  # Scale up since memory % is usually lower
        fd_score = min(num_fds / 10, 50)  # Cap at 50

        # Age score: newer processes get higher scores (more killable)
        # Max age considered: 1 hour (3600 seconds)
        age_score = max(0, 50 - (age_seconds / 72))  # 0-50 range

        # Category penalty/bonus
        category_modifier = self.CATEGORY_PENALTIES.get(category, 0)

        # Calculate weighted score
        score = (
            cpu_score * self.WEIGHTS['cpu'] +
            memory_score * self.WEIGHTS['memory'] +
            fd_score * self.WEIGHTS['fds'] +
            age_score * self.WEIGHTS['age'] +
            category_modifier * self.WEIGHTS['category']
        )

        return round(score, 2)

    def analyze_process(self, proc: psutil.Process) -> Optional[ProcessInfo]:
        """Analyze a single process and return ProcessInfo"""
        try:
            with proc.oneshot():
                pid = proc.pid
                name = proc.name()

                try:
                    cmdline = " ".join(proc.cmdline())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    cmdline = ""

                cpu_percent = proc.cpu_percent()
                memory_percent = proc.memory_percent()
                num_threads = proc.num_threads()

                try:
                    num_fds = proc.num_fds()
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    num_fds = 0

                create_time = proc.create_time()
                age_seconds = psutil.time.time() - create_time

                try:
                    children_count = len(proc.children())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    children_count = 0

                try:
                    username = proc.username()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    username = ""

                has_open_files = self._check_open_files_in_home(proc)
                category = self._categorize_process(name, cmdline)
                is_protected = self._is_protected(pid, category, children_count, has_open_files)

                kill_score = self._calculate_score(
                    cpu_percent, memory_percent, num_fds,
                    age_seconds, category, is_protected
                )

                return ProcessInfo(
                    pid=pid,
                    name=name,
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    num_threads=num_threads,
                    num_fds=num_fds,
                    create_time=create_time,
                    category=category,
                    is_protected=is_protected,
                    kill_score=kill_score,
                    children_count=children_count,
                    has_open_files_in_home=has_open_files,
                    cmdline=cmdline[:200],  # Truncate long cmdlines
                    username=username,
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None

    def get_all_processes(self, min_cpu: float = 0.0) -> List[ProcessInfo]:
        """Get all processes with optional CPU filter"""
        processes = []

        for proc in psutil.process_iter():
            info = self.analyze_process(proc)
            if info and info.cpu_percent >= min_cpu:
                processes.append(info)

        return sorted(processes, key=lambda x: x.kill_score, reverse=True)

    def get_killable_processes(self, min_score: float = 30.0,
                               min_cpu: float = 20.0) -> List[ProcessInfo]:
        """Get processes that are safe to kill based on score and CPU usage"""
        all_procs = self.get_all_processes(min_cpu=min_cpu)
        return [p for p in all_procs if not p.is_protected and p.kill_score >= min_score]

    def get_top_resource_hogs(self, limit: int = 10) -> List[ProcessInfo]:
        """Get top resource-consuming processes"""
        all_procs = self.get_all_processes(min_cpu=1.0)
        return all_procs[:limit]

    def kill_process_gracefully(self, pid: int, timeout: float = 2.0) -> bool:
        """
        Kill process with grace period
        Pattern from port-killer: SIGTERM -> wait -> SIGKILL
        """
        try:
            proc = psutil.Process(pid)

            # Verify it's still killable
            info = self.analyze_process(proc)
            if info and info.is_protected:
                logger.warning(f"Refusing to kill protected process: {info.name} (PID:{pid})")
                return False

            # Step 1: SIGTERM (graceful shutdown)
            proc.terminate()

            try:
                # Step 2: Wait for process to exit
                proc.wait(timeout=timeout)
                logger.info(f"Process {pid} terminated gracefully")
                return True
            except psutil.TimeoutExpired:
                # Step 3: Force kill if not terminated
                proc.kill()
                proc.wait(timeout=1.0)
                logger.info(f"Process {pid} force killed")
                return True

        except psutil.NoSuchProcess:
            logger.info(f"Process {pid} already terminated")
            return True
        except psutil.AccessDenied:
            logger.error(f"Access denied killing process {pid}")
            return False
        except Exception as e:
            logger.error(f"Error killing process {pid}: {e}")
            return False

    def kill_process_tree(self, pid: int, timeout: float = 2.0) -> int:
        """
        Kill process and all its descendants
        Returns count of killed processes
        """
        killed = 0
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            # Kill children first (in reverse order)
            for child in reversed(children):
                if self.kill_process_gracefully(child.pid, timeout=timeout/2):
                    killed += 1

            # Kill parent
            if self.kill_process_gracefully(pid, timeout=timeout):
                killed += 1

        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            logger.error(f"Error killing process tree {pid}: {e}")

        return killed


def main():
    """Test the process scorer"""
    scorer = ProcessScorer()

    print("=" * 60)
    print("Process Scoring System Test")
    print("=" * 60)

    print("\n📊 Top 10 Resource Hogs:")
    print("-" * 60)
    for proc in scorer.get_top_resource_hogs(10):
        print(proc)

    print("\n⚠️ Killable Processes (score > 30, CPU > 20%):")
    print("-" * 60)
    killable = scorer.get_killable_processes(min_score=30, min_cpu=20)
    if killable:
        for proc in killable[:10]:
            print(proc)
    else:
        print("No killable processes found")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
