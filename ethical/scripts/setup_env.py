#!/usr/bin/env python3
"""OSINT Investigation Toolkit — Environment Setup & Validation.

Checks for required dependencies, detects the Linux distribution,
and provides distro-specific installation instructions. Supports
interactive mode for choosing native install vs Docker pull.

Usage:
    python3 scripts/setup_env.py [options]

Exit codes:
    0 — All required dependencies available
    1 — One or more required dependencies missing
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.utils import (
    REQUIRED_TOOLS,
    check_dependencies,
    check_disk_space,
    detect_distro,
    error,
    format_bytes,
    get_package_manager,
    info,
    success,
    warn,
)

PREFIX = "[SETUP]"


def _get_version(cmd: str) -> str:
    """Try to get version string for a command."""
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True, text=True, timeout=5,
        )
        first_line = result.stdout.strip().split("\n")[0]
        return first_line if first_line else "installed"
    except Exception:
        return "installed"


def _get_install_command(tool_name: str, distro_id: str) -> str:
    """Get the appropriate install command for a tool on this distro."""
    spec = REQUIRED_TOOLS.get(tool_name, {})
    install_map = spec.get("install", {})

    if distro_id.lower() in install_map:
        return install_map[distro_id.lower()]
    if "_docker" in install_map:
        return install_map["_docker"]

    pkg_mgr = get_package_manager(distro_id)
    if pkg_mgr:
        return f"{pkg_mgr} {tool_name}"

    return f"# See {tool_name} documentation for installation"


def _format_table(deps: dict, distro: dict) -> str:
    """Format a table of dependency status."""
    distro_id = distro.get("ID", "unknown")
    distro_name = distro.get("NAME", distro.get("PRETTY_NAME", "Unknown"))

    lines = [
        f"{PREFIX} OSINT Investigation Toolkit — Environment Check",
        f"{PREFIX} ",
        f"{PREFIX} ┌────────────────┬──────────┬─────────────────────────────────────────────┐",
        f"{PREFIX} │ Dependency      │ Status   │ Install Command                             │",
        f"{PREFIX} ├────────────────┼──────────┼─────────────────────────────────────────────┤",
    ]

    for name, dep in deps.items():
        label = name.ljust(15)
        if dep["available"]:
            ver = dep.get("version", "")
            if ver and len(ver) > 6:
                ver = ver[:20]
            status = f"OK {ver}".ljust(8)
            install = "—"
        elif dep["required"]:
            status = "MISSING ".ljust(8)
            install = _get_install_command(name, distro_id)
        else:
            status = "OPT    ".ljust(8)
            install = _get_install_command(name, distro_id)

        lines.append(f"{PREFIX} │ {label} │ {status} │ {install.ljust(43)} │")

    lines.append(f"{PREFIX} └────────────────┴──────────┴─────────────────────────────────────────────┘")
    lines.append(f"{PREFIX} ")
    lines.append(f"{PREFIX} Detected distro: {distro_name}")

    required_count = sum(1 for d in deps.values() if d["required"])
    available_count = sum(1 for d in deps.values() if d["required"] and d["available"])
    lines.append(f"{PREFIX} Result: {available_count}/{required_count} required deps available.")

    return "\n".join(lines)


def _interactive_install(deps: dict, distro: dict) -> None:
    """Interactively prompt user to install missing tools."""
    distro_id = distro.get("ID", "unknown")

    for name, dep in deps.items():
        if dep["available"]:
            continue

        label = "REQUIRED" if dep["required"] else "OPTIONAL"
        spec = REQUIRED_TOOLS.get(name, {})

        print(f"\n{PREFIX} {name} [{label}] — not found")

        options = []
        native_cmd = _get_install_command(name, distro_id)
        if not native_cmd.startswith("#"):
            options.append(("Native install", native_cmd))

        if "docker_image" in spec:
            docker_cmd = f"docker pull {spec['docker_image']}"
            options.append(("Docker pull", docker_cmd))

        options.append(("Skip", None))

        for i, (desc, cmd) in enumerate(options, 1):
            if cmd:
                print(f"  {i}) {desc}: {cmd}")
            else:
                print(f"  {i}) {desc}")

        has_space, free = check_disk_space(".")
        if not has_space:
            warn(f"Low disk space: {format_bytes(free)} free. Installation may fail.")

        try:
            choice = input(f"{PREFIX} Choose [1-{len(options)}]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                _, cmd = options[idx]
                if cmd:
                    info(f"Running: {cmd}")
                    os.system(cmd)
                else:
                    info(f"Skipping {name}")
            else:
                info(f"Skipping {name}")
        except (ValueError, EOFError, KeyboardInterrupt):
            info(f"Skipping {name}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="setup_env",
        description="OSINT Investigation Toolkit — Environment Setup & Validation",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check dependencies, don't offer installation",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output JSON status report",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-essential output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    distro = detect_distro()
    deps = check_dependencies()

    has_space, free = check_disk_space(".")

    if args.json_output:
        output = {
            "distro": distro,
            "dependencies": deps,
            "disk": {"free_bytes": free, "sufficient": has_space},
        }
        print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    else:
        print(_format_table(deps, distro))
        if not has_space:
            warn(f"Disk space warning: {format_bytes(free)} free (< 2 GB)")
        print()

    all_required_available = all(
        dep["available"] for dep in deps.values() if dep["required"]
    )

    if all_required_available:
        if not args.json_output:
            success("All required dependencies are available.")
        return 0

    if not args.check_only and not args.json_output:
        _interactive_install(deps, distro)
        # Re-check after install
        deps = check_dependencies()
        all_required_available = all(
            dep["available"] for dep in deps.values() if dep["required"]
        )
        if all_required_available:
            success("All required dependencies are now available.")
            return 0

    if not args.json_output:
        error("Some required dependencies are still missing. See install commands above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
