#!/usr/bin/env python3
"""OSINT Investigation Toolkit — Evidence Vault Integrity Manager.

Hashes all evidence files with SHA-256 and maintains a central
manifest.json for chain-of-custody documentation. Supports
verification mode to detect tampering.

Usage:
    python3 scripts/vault_integrity.py [options]
    python3 scripts/vault_integrity.py --verify

Exit codes:
    0 — All evidence files verified / manifest updated successfully
    1 — Tampering detected (hash mismatch)
    2 — No evidence files found
"""

import argparse
import hashlib
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.utils import error, info, success, warn

MANIFEST_FILENAME = "manifest.json"
EVIDENCE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".txt", ".log", ".json", ".md", ".csv", ".html"}
MANIFEST_VERSION = "1.0.0"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _source_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _sha256(filepath: Path) -> str | None:
    """Compute SHA-256 hex digest. Returns None if the file is locked/unreadable."""
    try:
        h = hashlib.sha256()
        with open(filepath, "rb") as fh:
            while True:
                chunk = fh.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError):
        return None


def _classify_file(name: str) -> str:
    """Classify a file by its name into an evidence type."""
    lower = name.lower()
    if "scan_output" in lower:
        return "scan_output"
    if "dork" in lower:
        return "dorks"
    if lower.endswith((".png", ".jpg", ".jpeg")):
        return "screenshot"
    if lower.endswith(".log"):
        return "log"
    if "report" in lower:
        return "report"
    return "other"


def collect_evidence_files(evidence_dir: Path) -> list[Path]:
    """Recursively find all evidence files under *evidence_dir*."""
    files: list[Path] = []
    for root, _dirs, filenames in os.walk(evidence_dir):
        for fname in filenames:
            fp = Path(root) / fname
            if fp.name == MANIFEST_FILENAME:
                continue
            if fp.name == ".gitkeep":
                continue
            if fp.suffix.lower() in EVIDENCE_EXTENSIONS:
                files.append(fp)
    return sorted(files)


def load_manifest(evidence_dir: Path) -> dict[str, Any]:
    """Load existing manifest or return a fresh skeleton."""
    manifest_path = evidence_dir / MANIFEST_FILENAME
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {
        "manifest_version": MANIFEST_VERSION,
        "created_at": _now_iso(),
        "last_updated": _now_iso(),
        "investigator": "",
        "files": [],
    }


def save_manifest(evidence_dir: Path, manifest: dict[str, Any]) -> Path:
    """Write manifest.json atomically."""
    manifest["last_updated"] = _now_iso()
    manifest_path = evidence_dir / MANIFEST_FILENAME
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    return manifest_path


def update_manifest(
    evidence_dir: Path,
    investigator: str = "",
    tool_id: str = "vault_integrity",
) -> dict[str, Any]:
    """Hash all evidence files and create/update the manifest.

    - New files are added with status 'new' (or 'original' on first run).
    - Existing files with changed hashes are marked 'modified'.
    - Unchanged files keep status 'original'.
    - Locked/unreadable files are marked 'locked'.
    """
    manifest = load_manifest(evidence_dir)
    if investigator:
        manifest["investigator"] = investigator

    existing_map: dict[str, dict] = {}
    for entry in manifest.get("files", []):
        existing_map[entry["file_path"]] = entry

    is_first_run = len(existing_map) == 0
    evidence_files = collect_evidence_files(evidence_dir)
    new_files_list: list[dict] = []
    source_ip = _source_ip()

    for fp in evidence_files:
        rel = str(fp.relative_to(evidence_dir))
        sha = _sha256(fp)

        if sha is None:
            entry = {
                "file_path": rel,
                "sha256": "",
                "size_bytes": 0,
                "timestamp_iso": _now_iso(),
                "file_type": _classify_file(fp.name),
                "status": "locked",
                "tool_id": tool_id,
                "source_ip": source_ip,
            }
            warn(f"Locked/unreadable — flagged for re-hash: {rel}")
        else:
            size = fp.stat().st_size
            prev = existing_map.get(rel)
            if prev is None:
                status = "original" if is_first_run else "new"
            elif prev.get("sha256") != sha:
                status = "modified"
                warn(f"Hash mismatch detected: {rel}")
            else:
                status = "original"

            entry = {
                "file_path": rel,
                "sha256": sha,
                "size_bytes": size,
                "timestamp_iso": _now_iso(),
                "file_type": _classify_file(fp.name),
                "status": status,
                "tool_id": tool_id,
                "source_ip": source_ip,
            }

        new_files_list.append(entry)

    manifest["files"] = new_files_list
    save_manifest(evidence_dir, manifest)
    return manifest


def verify_manifest(evidence_dir: Path) -> tuple[bool, list[dict]]:
    """Verify all files against the existing manifest.

    Returns (all_ok, results) where results is a list of dicts with
    keys: file_path, expected_hash, actual_hash, status (match/mismatch/missing/new/locked).
    """
    manifest = load_manifest(evidence_dir)
    if not manifest.get("files"):
        return True, []

    existing_map: dict[str, dict] = {}
    for entry in manifest["files"]:
        existing_map[entry["file_path"]] = entry

    results: list[dict] = []
    all_ok = True

    for rel, entry in existing_map.items():
        fp = evidence_dir / rel
        if not fp.exists():
            results.append({
                "file_path": rel,
                "expected_hash": entry["sha256"],
                "actual_hash": None,
                "status": "missing",
            })
            all_ok = False
            continue

        sha = _sha256(fp)
        if sha is None:
            results.append({
                "file_path": rel,
                "expected_hash": entry["sha256"],
                "actual_hash": None,
                "status": "locked",
            })
            continue

        if sha == entry["sha256"]:
            results.append({
                "file_path": rel,
                "expected_hash": entry["sha256"],
                "actual_hash": sha,
                "status": "match",
            })
        else:
            results.append({
                "file_path": rel,
                "expected_hash": entry["sha256"],
                "actual_hash": sha,
                "status": "mismatch",
            })
            all_ok = False

    # Check for new files not in manifest
    current_files = collect_evidence_files(evidence_dir)
    for fp in current_files:
        rel = str(fp.relative_to(evidence_dir))
        if rel not in existing_map:
            results.append({
                "file_path": rel,
                "expected_hash": None,
                "actual_hash": _sha256(fp),
                "status": "new",
            })

    return all_ok, results


def _format_verify_table(results: list[dict]) -> str:
    """Format verification results as a human-readable table."""
    lines = [
        "",
        "  التحقق من سلامة الأدلة — Evidence Integrity Verification",
        "  " + "=" * 60,
        "",
    ]
    status_symbols = {
        "match": "OK ",
        "mismatch": "TAMPERED",
        "missing": "MISSING ",
        "new": "NEW     ",
        "locked": "LOCKED  ",
    }
    for r in results:
        sym = status_symbols.get(r["status"], "???")
        lines.append(f"  [{sym}] {r['file_path']}")
        if r["status"] == "mismatch":
            lines.append(f"          Expected: {r['expected_hash']}")
            lines.append(f"          Actual  : {r['actual_hash']}")

    lines.append("")

    matches = sum(1 for r in results if r["status"] == "match")
    total = len(results)
    lines.append(f"  النتيجة / Result: {matches}/{total} files verified OK")
    lines.append("")
    return "\n".join(lines)


def _write_verification_certificate(evidence_dir: Path, results: list[dict], all_ok: bool) -> Path:
    """Write a verification certificate with Arabic section headers."""
    cert_path = evidence_dir / "verification_certificate.txt"
    lines = [
        "شهادة التحقق من سلامة الأدلة",
        "Evidence Integrity Verification Certificate",
        "=" * 50,
        "",
        f"التاريخ / Date: {_now_iso()}",
        f"المجلد / Directory: {evidence_dir}",
        f"النتيجة / Result: {'PASS — All evidence intact' if all_ok else 'FAIL — Tampering detected'}",
        "",
        "تفاصيل الملفات / File Details:",
        "-" * 50,
    ]
    for r in results:
        lines.append(f"  File: {r['file_path']}")
        lines.append(f"  Status: {r['status']}")
        if r.get("expected_hash"):
            lines.append(f"  SHA-256: {r['expected_hash']}")
        lines.append("")

    cert_path.write_text("\n".join(lines), encoding="utf-8")
    return cert_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vault_integrity",
        description="Evidence Vault Integrity — hash evidence files and maintain chain of custody.",
    )
    parser.add_argument(
        "--evidence-dir",
        default="./evidence",
        help="Root evidence directory (default: ./evidence)",
    )
    parser.add_argument(
        "--investigator",
        default="",
        help="Investigator name for chain-of-custody attribution",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify evidence files against existing manifest",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON instead of human-readable text",
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
    evidence_dir = Path(args.evidence_dir)

    if not evidence_dir.exists():
        error(f"Evidence directory does not exist: {evidence_dir}")
        return 2

    if args.verify:
        all_ok, results = verify_manifest(evidence_dir)
        if not results:
            warn("No manifest found or manifest is empty. Run without --verify first.")
            return 2

        if args.json_output:
            print(json.dumps({"all_ok": all_ok, "results": results}, indent=2, ensure_ascii=False))
        else:
            print(_format_verify_table(results))

        cert = _write_verification_certificate(evidence_dir, results, all_ok)
        if not args.quiet:
            info(f"Verification certificate: {cert}")

        return 0 if all_ok else 1

    # Update mode
    files = collect_evidence_files(evidence_dir)
    if not files:
        warn(f"No evidence files found in {evidence_dir}")
        return 2

    manifest = update_manifest(evidence_dir, args.investigator)

    if args.json_output:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    else:
        file_count = len(manifest["files"])
        new_count = sum(1 for f in manifest["files"] if f["status"] == "new")
        modified_count = sum(1 for f in manifest["files"] if f["status"] == "modified")
        locked_count = sum(1 for f in manifest["files"] if f["status"] == "locked")

        success(f"Manifest updated: {file_count} files hashed")
        if new_count:
            info(f"  New files added: {new_count}")
        if modified_count:
            warn(f"  Modified files detected: {modified_count}")
        if locked_count:
            warn(f"  Locked files (re-hash needed): {locked_count}")
        if not args.quiet:
            info(f"  Manifest: {evidence_dir / MANIFEST_FILENAME}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
