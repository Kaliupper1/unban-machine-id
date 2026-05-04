"""Tests for vault_integrity — SHA-256 hashing, manifest management, tamper detection."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.vault_integrity import (
    collect_evidence_files,
    load_manifest,
    save_manifest,
    update_manifest,
    verify_manifest,
)


@pytest.fixture
def evidence_dir(tmp_path):
    """Create a temporary evidence directory with sample files."""
    edir = tmp_path / "evidence"
    edir.mkdir()
    number_dir = edir / "+201201796383"
    number_dir.mkdir()

    (number_dir / "scan_output.txt").write_text("PhoneInfoga scan results here")
    (number_dir / "dorks.txt").write_text("# Dorking URLs\nhttps://google.com/search?q=test")
    (number_dir / "report.json").write_text('{"phone": "+201201796383"}')
    return edir


class TestCollectEvidenceFiles:
    def test_finds_evidence_files(self, evidence_dir):
        files = collect_evidence_files(evidence_dir)
        assert len(files) == 3

    def test_ignores_manifest(self, evidence_dir):
        (evidence_dir / "manifest.json").write_text("{}")
        files = collect_evidence_files(evidence_dir)
        names = [f.name for f in files]
        assert "manifest.json" not in names

    def test_ignores_gitkeep(self, evidence_dir):
        (evidence_dir / ".gitkeep").write_text("")
        files = collect_evidence_files(evidence_dir)
        names = [f.name for f in files]
        assert ".gitkeep" not in names

    def test_empty_directory(self, tmp_path):
        edir = tmp_path / "empty"
        edir.mkdir()
        files = collect_evidence_files(edir)
        assert len(files) == 0


class TestManifest:
    def test_load_missing_manifest_returns_skeleton(self, evidence_dir):
        manifest = load_manifest(evidence_dir)
        assert manifest["manifest_version"] == "1.0.0"
        assert manifest["files"] == []

    def test_save_and_load(self, evidence_dir):
        manifest = {
            "manifest_version": "1.0.0",
            "created_at": "2026-01-01T00:00:00Z",
            "last_updated": "2026-01-01T00:00:00Z",
            "investigator": "Test",
            "files": [{"file_path": "test.txt", "sha256": "abc123"}],
        }
        save_manifest(evidence_dir, manifest)
        loaded = load_manifest(evidence_dir)
        assert loaded["investigator"] == "Test"
        assert len(loaded["files"]) == 1

    def test_save_updates_timestamp(self, evidence_dir):
        manifest = load_manifest(evidence_dir)
        old_ts = manifest["last_updated"]
        save_manifest(evidence_dir, manifest)
        loaded = load_manifest(evidence_dir)
        assert loaded["last_updated"] >= old_ts


class TestUpdateManifest:
    def test_first_run_marks_original(self, evidence_dir):
        manifest = update_manifest(evidence_dir, investigator="Tester")
        assert manifest["investigator"] == "Tester"
        assert len(manifest["files"]) == 3
        for f in manifest["files"]:
            assert f["status"] == "original"
            assert len(f["sha256"]) == 64

    def test_unchanged_files_stay_original(self, evidence_dir):
        update_manifest(evidence_dir)
        manifest = update_manifest(evidence_dir)
        for f in manifest["files"]:
            assert f["status"] == "original"

    def test_modified_file_detected(self, evidence_dir):
        update_manifest(evidence_dir)
        scan_file = evidence_dir / "+201201796383" / "scan_output.txt"
        scan_file.write_text("MODIFIED CONTENT")
        manifest = update_manifest(evidence_dir)
        modified = [f for f in manifest["files"] if f["status"] == "modified"]
        assert len(modified) == 1
        assert "scan_output.txt" in modified[0]["file_path"]

    def test_new_file_detected(self, evidence_dir):
        update_manifest(evidence_dir)
        new_file = evidence_dir / "+201201796383" / "screenshot.png"
        new_file.write_bytes(b"\x89PNG fake image data")
        manifest = update_manifest(evidence_dir)
        new_entries = [f for f in manifest["files"] if f["status"] == "new"]
        assert len(new_entries) == 1


class TestVerifyManifest:
    def test_verify_intact(self, evidence_dir):
        update_manifest(evidence_dir)
        all_ok, results = verify_manifest(evidence_dir)
        assert all_ok is True
        assert all(r["status"] == "match" for r in results)

    def test_verify_tampered(self, evidence_dir):
        update_manifest(evidence_dir)
        scan_file = evidence_dir / "+201201796383" / "scan_output.txt"
        scan_file.write_text("TAMPERED!")
        all_ok, results = verify_manifest(evidence_dir)
        assert all_ok is False
        mismatches = [r for r in results if r["status"] == "mismatch"]
        assert len(mismatches) == 1

    def test_verify_missing_file(self, evidence_dir):
        update_manifest(evidence_dir)
        scan_file = evidence_dir / "+201201796383" / "scan_output.txt"
        scan_file.unlink()
        all_ok, results = verify_manifest(evidence_dir)
        assert all_ok is False
        missing = [r for r in results if r["status"] == "missing"]
        assert len(missing) == 1

    def test_verify_new_file(self, evidence_dir):
        update_manifest(evidence_dir)
        new_file = evidence_dir / "+201201796383" / "notes.txt"
        new_file.write_text("investigator notes")
        all_ok, results = verify_manifest(evidence_dir)
        assert all_ok is True  # New files don't fail verification
        new_entries = [r for r in results if r["status"] == "new"]
        assert len(new_entries) == 1

    def test_verify_empty_manifest(self, evidence_dir):
        all_ok, results = verify_manifest(evidence_dir)
        assert all_ok is True
        assert results == []
