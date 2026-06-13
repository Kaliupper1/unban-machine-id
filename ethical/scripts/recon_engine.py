#!/usr/bin/env python3
"""OSINT Investigation Toolkit — Phone Reconnaissance Engine.

Single-command phone number OSINT: validates the number, runs PhoneInfoga,
generates Google Dorking URLs, and saves all output into an organized
evidence directory.

Usage:
    python3 scripts/recon_engine.py <phone_number> [options]

Shell alias (add to .zshrc / .bashrc):
    alias recon="python3 $(pwd)/scripts/recon_engine.py"

Exit codes:
    0 — Success
    1 — Invalid phone number format
    2 — Missing dependency (PhoneInfoga / Docker not found)
    3 — PhoneInfoga scan failed (runtime error)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure the project root is on sys.path so `scripts.*` imports work
# when invoked as `python3 scripts/recon_engine.py` from ethical/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.dork_generator import format_dorks_text, generate_dorks
from scripts.evidence_manager import create_evidence_dir, write_dorks_file, write_scan_output
from scripts.phoneinfoga_runner import run_scan
from scripts.report_writer import write_dual_report
from scripts.utils import check_dependencies, error, info, success, warn
from scripts.validators import get_phone_metadata, normalize_phone


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recon_engine",
        description="OSINT Phone Reconnaissance Engine — scan a phone number and collect evidence.",
    )
    parser.add_argument(
        "phone_number",
        help="Phone number to investigate (e.g. 01201796383 or +201201796383)",
    )
    parser.add_argument(
        "--output-dir",
        default="./evidence",
        help="Root evidence directory (default: ./evidence)",
    )
    parser.add_argument(
        "--scanners",
        default="local,googlesearch,ovh",
        help="Comma-separated PhoneInfoga scanners (default: local,googlesearch,ovh)",
    )
    parser.add_argument(
        "--skip-scan",
        action="store_true",
        help="Skip PhoneInfoga execution (generate dorks only)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON report to stdout",
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

    # --- Step 1: Validate phone number ---
    try:
        normalized = normalize_phone(args.phone_number)
    except ValueError as exc:
        error(str(exc))
        return 1

    metadata = get_phone_metadata(args.phone_number)
    if not args.quiet:
        info(f"Target: {normalized} ({metadata['line_type']}, {metadata['carrier'] or 'carrier unknown'})")
        if metadata["is_voip"]:
            warn("HIGH-ANONYMITY INDICATOR: Number classified as VoIP")

    # --- Step 2: Check dependencies (unless --skip-scan) ---
    scanners_list = [s.strip() for s in args.scanners.split(",")]
    scan_result = None

    if not args.skip_scan:
        deps = check_dependencies()
        pi_dep = deps.get("phoneinfoga", {})
        if not pi_dep.get("available"):
            error(
                "PhoneInfoga is not available. "
                "Install the binary or pull the Docker image: "
                "docker pull sundowndev/phoneinfoga"
            )
            return 2

        # --- Step 3: Run PhoneInfoga scan ---
        scan_result = run_scan(normalized, scanners_list)
        if not scan_result["success"] and not scan_result["rate_limited"]:
            error(f"PhoneInfoga scan failed: {scan_result.get('error_message', 'Unknown error')}")
            if scan_result["stdout"]:
                warn("Partial output may have been captured")
            else:
                return 3

        if scan_result["rate_limited"]:
            warn("Rate limit hit — saving partial results")

    # --- Step 4: Create evidence directory ---
    try:
        evidence_dir = create_evidence_dir(normalized, args.output_dir)
    except RuntimeError as exc:
        error(str(exc))
        return 3

    # --- Step 5: Save scan output ---
    if scan_result is not None:
        write_scan_output(evidence_dir, scan_result["stdout"], scan_result["stderr"])

    # --- Step 6: Generate and save dorking URLs ---
    dorks = generate_dorks(normalized)
    dorks_text = format_dorks_text(dorks)
    write_dorks_file(evidence_dir, dorks_text)

    # --- Step 7: Write dual report ---
    report_data = {
        "phone_number": normalized,
        "scan_timestamp": scan_result["scan_timestamp"] if scan_result else datetime.now(timezone.utc).isoformat(),
        "line_type": metadata["line_type"],
        "carrier": metadata["carrier"] or "Unknown",
        "country": metadata["country_code"],
        "is_voip": metadata["is_voip"],
        "scanners_run": scan_result["scanners_run"] if scan_result else [],
        "scanners_skipped": scan_result["scanners_skipped"] if scan_result else scanners_list,
        "dorks_generated": len(dorks),
        "evidence_dir": str(evidence_dir),
        "tool_id": scan_result["tool_id"] if scan_result else "recon_engine:dorks_only",
        "source_ip": scan_result["source_ip"] if scan_result else "N/A",
    }

    json_path, md_path = write_dual_report(report_data, evidence_dir)

    # --- Step 8: Output ---
    if args.json_output:
        print(json.dumps(report_data, indent=2, ensure_ascii=False))
    else:
        success(f"Reconnaissance complete for {normalized}")
        if not args.quiet:
            info(f"  Evidence dir : {evidence_dir}")
            info(f"  Scan output  : {evidence_dir / 'scan_output.txt'}")
            info(f"  Dorking URLs : {evidence_dir / 'dorks.txt'} ({len(dorks)} URLs)")
            info(f"  JSON report  : {json_path}")
            info(f"  MD report    : {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
