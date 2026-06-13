"""Shared utilities for the OSINT Investigation Toolkit.

Provides phone validation helpers, disk space checking, colored output,
distro detection, and dependency checking used across all scripts.
"""

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

PREFIX = "[OSINT]"


def _color(text: str, color: str) -> str:
    if not HAS_COLORAMA:
        return text
    colors = {
        "green": Fore.GREEN,
        "red": Fore.RED,
        "yellow": Fore.YELLOW,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "magenta": Fore.MAGENTA,
    }
    c = colors.get(color, "")
    reset = Style.RESET_ALL if c else ""
    return f"{c}{text}{reset}"


def info(msg: str) -> None:
    print(f"{PREFIX} {_color(msg, 'cyan')}", file=sys.stderr)


def success(msg: str) -> None:
    print(f"{PREFIX} {_color(msg, 'green')}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"{PREFIX} {_color(msg, 'yellow')}", file=sys.stderr)


def error(msg: str) -> None:
    print(f"{PREFIX} {_color(msg, 'red')}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Disk space
# ---------------------------------------------------------------------------

MIN_FREE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB


def check_disk_space(path: str = ".") -> tuple[bool, int]:
    """Return (has_enough, free_bytes) for the partition containing *path*.

    Considers space sufficient when >= 2 GB free (FR-006a).
    """
    usage = shutil.disk_usage(os.path.abspath(path))
    return usage.free >= MIN_FREE_BYTES, usage.free


def format_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024  # type: ignore[assignment]
    return f"{n:.1f} PB"


# ---------------------------------------------------------------------------
# Distro detection
# ---------------------------------------------------------------------------

def detect_distro() -> dict[str, str]:
    """Parse /etc/os-release and return a dict with ID, NAME, etc."""
    result: dict[str, str] = {}
    os_release = Path("/etc/os-release")
    if os_release.exists():
        for line in os_release.read_text().splitlines():
            if "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip().strip('"')
    if not result:
        result["ID"] = platform.system().lower()
        result["NAME"] = platform.system()
    return result


def get_package_manager(distro_id: str) -> Optional[str]:
    """Map distro ID to its primary package manager command."""
    mapping = {
        "arch": "pacman -S",
        "manjaro": "pacman -S",
        "ubuntu": "apt install",
        "debian": "apt install",
        "kali": "apt install",
        "fedora": "dnf install",
        "centos": "yum install",
        "rhel": "yum install",
    }
    return mapping.get(distro_id.lower())


# ---------------------------------------------------------------------------
# Dependency checking
# ---------------------------------------------------------------------------

def _which(cmd: str) -> Optional[str]:
    """Find executable on PATH."""
    return shutil.which(cmd)


def _docker_image_exists(image: str) -> bool:
    """Check whether a Docker image is already pulled locally."""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", image],
            capture_output=True, text=True, timeout=10,
        )
        return bool(result.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


REQUIRED_TOOLS = {
    "python3": {
        "check_cmd": "python3",
        "install": {"arch": "pacman -S python", "ubuntu": "apt install python3", "kali": "apt install python3"},
        "required": True,
    },
    "docker": {
        "check_cmd": "docker",
        "install": {"arch": "pacman -S docker", "ubuntu": "apt install docker.io", "kali": "apt install docker.io"},
        "required": True,
    },
    "phoneinfoga": {
        "check_cmd": "phoneinfoga",
        "docker_image": "sundowndev/phoneinfoga",
        "install": {"_docker": "docker pull sundowndev/phoneinfoga"},
        "required": True,
    },
    "chromedriver": {
        "check_cmd": "chromedriver",
        "install": {"arch": "pacman -S chromedriver", "ubuntu": "apt install chromium-chromedriver"},
        "required": False,
    },
}


def check_dependencies() -> dict[str, dict]:
    """Check each tool's availability via PATH and Docker images.

    Returns a dict keyed by tool name with fields:
        available (bool), method (str|None), version (str|None), required (bool)
    """
    results: dict[str, dict] = {}
    for name, spec in REQUIRED_TOOLS.items():
        entry: dict = {"required": spec["required"], "available": False, "method": None, "version": None}
        path = _which(spec["check_cmd"])
        if path:
            entry["available"] = True
            entry["method"] = "binary"
            try:
                ver = subprocess.run(
                    [spec["check_cmd"], "--version"],
                    capture_output=True, text=True, timeout=5,
                )
                entry["version"] = ver.stdout.strip().split("\n")[0]
            except Exception:
                entry["version"] = "unknown"
        elif "docker_image" in spec and _docker_image_exists(spec["docker_image"]):
            entry["available"] = True
            entry["method"] = "docker"
            entry["version"] = f"docker:{spec['docker_image']}"
        results[name] = entry
    return results
