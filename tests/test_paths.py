"""Tests for accessiclock.paths module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from accessiclock.paths import Paths


class TestPathsBasic:
    """Test basic Paths functionality."""

    def test_init_default_mode(self):
        """Paths should initialize in non-portable mode by default."""
        paths = Paths()
        assert paths._portable_mode is False

    def test_init_portable_mode(self):
        """Paths should accept portable mode flag."""
        paths = Paths(portable_mode=True)
        assert paths._portable_mode is True

    def test_app_dir_is_path(self):
        """app_dir should return a Path object."""
        paths = Paths()
        assert isinstance(paths.app_dir, Path)

    def test_app_dir_exists(self):
        """app_dir should point to existing directory."""
        paths = Paths()
        assert paths.app_dir.exists()


class TestDataDirectory:
    """Test data directory resolution."""

    def test_data_dir_is_path(self):
        """data_dir should return a Path object."""
        paths = Paths()
        assert isinstance(paths.data_dir, Path)

    def test_data_dir_created_if_missing(self):
        """data_dir should create directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict("os.environ", {"APPDATA": tmpdir}):
            paths = Paths()
            data_dir = paths.data_dir
            assert data_dir.exists()

    def test_portable_mode_uses_app_dir(self):
        """In portable mode, data_dir should be under app_dir."""
        paths = Paths(portable_mode=True)
        # In portable mode, data is stored alongside app
        assert "data" in str(paths.data_dir) or paths.data_dir.parent == paths.app_dir


class TestConfigFile:
    """Test config file path resolution."""

    def test_config_file_is_path(self):
        """config_file should return a Path object."""
        paths = Paths()
        assert isinstance(paths.config_file, Path)

    def test_config_file_is_json(self):
        """config_file should have .json extension."""
        paths = Paths()
        assert paths.config_file.suffix == ".json"

    def test_config_file_under_data_dir(self):
        """config_file should be under data_dir."""
        paths = Paths()
        assert paths.config_file.parent == paths.data_dir


class TestClocksDirectory:
    """Test clocks directory resolution."""

    def test_clocks_dir_is_path(self):
        """clocks_dir should return a Path object."""
        paths = Paths()
        assert isinstance(paths.clocks_dir, Path)

    def test_user_clocks_dir_is_path(self):
        """user_clocks_dir should return a Path object."""
        paths = Paths()
        assert isinstance(paths.user_clocks_dir, Path)

    def test_user_clocks_dir_created(self):
        """user_clocks_dir should create directory."""
        paths = Paths()
        user_clocks = paths.user_clocks_dir
        assert user_clocks.exists()


class TestLogsDirectory:
    """Test logs directory resolution."""

    def test_logs_dir_is_path(self):
        """logs_dir should return a Path object."""
        paths = Paths()
        assert isinstance(paths.logs_dir, Path)

    def test_logs_dir_created(self):
        """logs_dir should create directory."""
        paths = Paths()
        logs = paths.logs_dir
        assert logs.exists()
