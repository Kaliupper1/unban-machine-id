"""Evidence directory management.

Creates and manages the per-number evidence directory structure,
writing scan outputs, dork files, and reports.
"""

from pathlib import Path

from scripts.utils import check_disk_space, error, format_bytes, info, warn


def create_evidence_dir(normalized_number: str, output_root: str = "./evidence") -> Path:
    """Create the evidence directory for a phone number.

    Creates ``<output_root>/<normalized_number>/`` and returns the Path.
    Checks disk space before proceeding (FR-006a).

    Raises RuntimeError if disk space is insufficient.
    """
    has_space, free = check_disk_space(output_root if Path(output_root).exists() else ".")
    if not has_space:
        raise RuntimeError(
            f"Insufficient disk space: {format_bytes(free)} free. "
            f"At least 2 GB required (FR-006a)."
        )

    evidence_dir = Path(output_root) / normalized_number
    evidence_dir.mkdir(parents=True, exist_ok=True)
    info(f"Evidence directory ready: {evidence_dir}")
    return evidence_dir


def write_scan_output(evidence_dir: Path, stdout: str, stderr: str = "") -> Path:
    """Write raw PhoneInfoga output to scan_output.txt."""
    out_path = evidence_dir / "scan_output.txt"
    content = stdout
    if stderr:
        content += f"\n\n--- STDERR ---\n{stderr}"
    out_path.write_text(content, encoding="utf-8")
    info(f"Scan output saved: {out_path}")
    return out_path


def write_dorks_file(evidence_dir: Path, dorks_text: str) -> Path:
    """Write formatted dorking URLs to dorks.txt."""
    out_path = evidence_dir / "dorks.txt"
    out_path.write_text(dorks_text, encoding="utf-8")
    info(f"Dorks file saved: {out_path}")
    return out_path
