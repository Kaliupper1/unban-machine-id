"""Tests for setup_env — tool detection, distro detection, environment validation."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.utils import (
    check_dependencies,
    check_disk_space,
    detect_distro,
    format_bytes,
    get_package_manager,
)


class TestDistroDetection:
    def test_detect_distro_returns_dict(self):
        result = detect_distro()
        assert isinstance(result, dict)
        assert "ID" in result or "NAME" in result

    @patch("scripts.utils.Path")
    def test_fallback_to_platform(self, mock_path):
        mock_path.return_value.exists.return_value = False
        result = detect_distro()
        assert isinstance(result, dict)


class TestPackageManager:
    def test_arch(self):
        assert get_package_manager("arch") == "pacman -S"

    def test_ubuntu(self):
        assert get_package_manager("ubuntu") == "apt install"

    def test_kali(self):
        assert get_package_manager("kali") == "apt install"

    def test_unknown(self):
        assert get_package_manager("unknown_distro") is None


class TestDiskSpace:
    def test_returns_tuple(self):
        has_space, free = check_disk_space(".")
        assert isinstance(has_space, bool)
        assert isinstance(free, int)
        assert free > 0

    def test_format_bytes(self):
        assert "KB" in format_bytes(2048)
        assert "MB" in format_bytes(2 * 1024 * 1024)
        assert "GB" in format_bytes(3 * 1024 * 1024 * 1024)


class TestDependencyChecker:
    def test_returns_dict(self):
        deps = check_dependencies()
        assert isinstance(deps, dict)
        assert "python3" in deps

    def test_python3_available(self):
        deps = check_dependencies()
        assert deps["python3"]["available"] is True
        assert deps["python3"]["method"] == "binary"

    def test_each_dep_has_required_keys(self):
        deps = check_dependencies()
        for name, dep in deps.items():
            assert "available" in dep
            assert "required" in dep
            assert "method" in dep


class TestSetupEnvCLI:
    def test_check_only_mode(self):
        from scripts.setup_env import main
        result = main(["--check-only"])
        assert result in (0, 1)

    def test_json_output(self, capsys):
        from scripts.setup_env import main
        result = main(["--check-only", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "dependencies" in data
        assert "distro" in data
        assert "disk" in data
