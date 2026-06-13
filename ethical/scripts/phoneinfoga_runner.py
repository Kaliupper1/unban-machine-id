"""PhoneInfoga scanner integration.

Invokes PhoneInfoga as an external CLI tool via subprocess, supporting
both Docker and native binary modes. Auto-detects which mode is available.
"""

import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from typing import Optional

from scripts.utils import error, info, warn


def _detect_mode() -> Optional[str]:
    """Detect whether PhoneInfoga is available as binary or Docker image.

    Returns 'binary', 'docker', or None.
    """
    if shutil.which("phoneinfoga"):
        return "binary"
    try:
        result = subprocess.run(
            ["docker", "images", "-q", "sundowndev/phoneinfoga"],
            capture_output=True, text=True, timeout=10,
        )
        if result.stdout.strip():
            return "docker"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _get_source_ip() -> str:
    """Best-effort retrieval of the local source IP for chain-of-custody."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_scan(
    normalized_number: str,
    scanners: list[str] | None = None,
) -> dict:
    """Run PhoneInfoga scan on *normalized_number*.

    Returns a dict with keys:
        success (bool), mode (str), stdout (str), stderr (str),
        scanners_run (list), scanners_skipped (list),
        scan_timestamp (str), tool_id (str), source_ip (str),
        rate_limited (bool), error_message (str|None)
    """
    if scanners is None:
        scanners = ["local", "googlesearch", "ovh"]

    mode = _detect_mode()
    if mode is None:
        return {
            "success": False,
            "mode": None,
            "stdout": "",
            "stderr": "PhoneInfoga not found. Install via binary or Docker.",
            "scanners_run": [],
            "scanners_skipped": scanners,
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_id": "phoneinfoga",
            "source_ip": _get_source_ip(),
            "rate_limited": False,
            "error_message": (
                "PhoneInfoga is not installed. "
                "Install the binary (curl -sSL https://raw.githubusercontent.com/"
                "sundowndev/phoneinfoga/master/install.sh | bash) "
                "or pull the Docker image (docker pull sundowndev/phoneinfoga)."
            ),
        }

    if mode == "binary":
        cmd = ["phoneinfoga", "scan", "-n", normalized_number]
    else:
        cmd = [
            "docker", "run", "--rm",
            "sundowndev/phoneinfoga",
            "scan", "-n", normalized_number,
        ]

    info(f"Running PhoneInfoga ({mode} mode): {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        warn("PhoneInfoga scan timed out after 120s")
        return {
            "success": False,
            "mode": mode,
            "stdout": "",
            "stderr": "Scan timed out after 120 seconds",
            "scanners_run": [],
            "scanners_skipped": scanners,
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_id": f"phoneinfoga:{mode}",
            "source_ip": _get_source_ip(),
            "rate_limited": False,
            "error_message": "Scan timed out after 120 seconds.",
        }

    rate_limited = "rate limit" in result.stdout.lower() or "rate limit" in result.stderr.lower()
    if rate_limited:
        warn("Rate limit detected — partial results may be saved")

    return {
        "success": result.returncode == 0,
        "mode": mode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "scanners_run": scanners if result.returncode == 0 else [],
        "scanners_skipped": [] if result.returncode == 0 else scanners,
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_id": f"phoneinfoga:{mode}",
        "source_ip": _get_source_ip(),
        "rate_limited": rate_limited,
        "error_message": result.stderr.strip() if result.returncode != 0 else None,
    }
