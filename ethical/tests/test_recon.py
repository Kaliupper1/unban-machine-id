"""Tests for recon_engine — dork generation, evidence management, CLI integration."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.dork_generator import format_dorks_text, generate_dorks
from scripts.evidence_manager import create_evidence_dir, write_dorks_file, write_scan_output


class TestDorkGenerator:
    def test_generates_dorks(self):
        dorks = generate_dorks("+201201796383")
        assert len(dorks) > 0

    def test_all_dorks_have_required_keys(self):
        dorks = generate_dorks("+201201796383")
        for dork in dorks:
            assert "platform" in dork
            assert "dork_type" in dork
            assert "url" in dork
            assert "phone_number" in dork

    def test_platform_coverage(self):
        dorks = generate_dorks("+201201796383")
        platforms = {d["platform"] for d in dorks}
        expected = {"facebook", "linkedin", "instagram", "twitter", "tiktok", "pastebin"}
        assert expected.issubset(platforms)

    def test_dork_contains_number(self):
        dorks = generate_dorks("+201201796383")
        site_dorks = [d for d in dorks if d["dork_type"] == "site_specific"]
        for dork in site_dorks:
            assert "+201201796383" in dork["url"] or "201201796383" in dork["url"]

    def test_format_dorks_text(self):
        dorks = generate_dorks("+201201796383")
        text = format_dorks_text(dorks)
        assert "Google Dorking URLs" in text
        assert "+201201796383" in text
        assert "FACEBOOK" in text


class TestEvidenceManager:
    def test_create_evidence_dir(self, tmp_path):
        edir = create_evidence_dir("+201201796383", str(tmp_path))
        assert edir.exists()
        assert edir.name == "+201201796383"

    def test_create_evidence_dir_idempotent(self, tmp_path):
        edir1 = create_evidence_dir("+201201796383", str(tmp_path))
        edir2 = create_evidence_dir("+201201796383", str(tmp_path))
        assert edir1 == edir2
        assert edir1.exists()

    def test_write_scan_output(self, tmp_path):
        edir = tmp_path / "+201201796383"
        edir.mkdir()
        path = write_scan_output(edir, "scan results here", "some warnings")
        assert path.exists()
        content = path.read_text()
        assert "scan results here" in content
        assert "STDERR" in content

    def test_write_dorks_file(self, tmp_path):
        edir = tmp_path / "+201201796383"
        edir.mkdir()
        path = write_dorks_file(edir, "# Dorks\nhttps://google.com")
        assert path.exists()
        assert "Dorks" in path.read_text()


class TestReconEngineCLI:
    def test_invalid_number_exits_1(self):
        from scripts.recon_engine import main
        result = main(["invalid_number"])
        assert result == 1

    def test_skip_scan_mode(self, tmp_path):
        from scripts.recon_engine import main
        result = main([
            "+201201796383",
            "--skip-scan",
            "--output-dir", str(tmp_path),
            "--quiet",
        ])
        assert result == 0
        evidence_dir = tmp_path / "+201201796383"
        assert evidence_dir.exists()
        assert (evidence_dir / "dorks.txt").exists()
        assert (evidence_dir / "report.json").exists()
        assert (evidence_dir / "report.md").exists()

    def test_json_output_mode(self, tmp_path, capsys):
        from scripts.recon_engine import main
        result = main([
            "+201201796383",
            "--skip-scan",
            "--output-dir", str(tmp_path),
            "--json",
        ])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["phone_number"] == "+201201796383"
        assert data["dorks_generated"] > 0
