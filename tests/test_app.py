"""Tests for accessiclock.app module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestAccessiClockAppConfig:
    """Test application configuration handling."""

    def test_default_config_values(self):
        """App should have sensible default config values."""
        with patch("accessiclock.app.wx"):
            with patch("accessiclock.app.Paths") as MockPaths:
                mock_paths = MagicMock()
                mock_paths.config_file = Path("/nonexistent/config.json")
                mock_paths.app_dir = Path("/app")
                MockPaths.return_value = mock_paths
                
                from accessiclock.app import AccessiClockApp
                
                # Create app without calling OnInit
                app = AccessiClockApp.__new__(AccessiClockApp)
                app._portable_mode = False
                app.paths = mock_paths
                app.main_window = None
                app.audio_player = None
                app.config = {}
                app.current_volume = 50
                app.selected_clock = "default"
                app.chime_hourly = True
                app.chime_half_hour = False
                app.chime_quarter_hour = False
                
                assert app.current_volume == 50
                assert app.selected_clock == "default"
                assert app.chime_hourly is True
                assert app.chime_half_hour is False

    def test_load_config_from_file(self):
        """App should load config from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = {
                "volume": 75,
                "clock": "westminster",
                "chime_hourly": True,
                "chime_half_hour": True,
                "chime_quarter_hour": False,
            }
            with open(config_path, "w") as f:
                json.dump(config_data, f)
            
            with patch("accessiclock.app.wx"):
                with patch("accessiclock.app.Paths") as MockPaths:
                    mock_paths = MagicMock()
                    mock_paths.config_file = config_path
                    mock_paths.app_dir = Path(tmpdir)
                    MockPaths.return_value = mock_paths
                    
                    from accessiclock.app import AccessiClockApp
                    
                    app = AccessiClockApp.__new__(AccessiClockApp)
                    app._portable_mode = False
                    app.paths = mock_paths
                    app.config = {}
                    app.current_volume = 50
                    app.selected_clock = "default"
                    app.chime_hourly = True
                    app.chime_half_hour = False
                    app.chime_quarter_hour = False
                    
                    app._load_config()
                    
                    assert app.current_volume == 75
                    assert app.selected_clock == "westminster"
                    assert app.chime_half_hour is True

    def test_save_config_to_file(self):
        """App should save config to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            with patch("accessiclock.app.wx"):
                with patch("accessiclock.app.Paths") as MockPaths:
                    mock_paths = MagicMock()
                    mock_paths.config_file = config_path
                    MockPaths.return_value = mock_paths
                    
                    from accessiclock.app import AccessiClockApp
                    
                    app = AccessiClockApp.__new__(AccessiClockApp)
                    app.paths = mock_paths
                    app.config = {}
                    app.current_volume = 80
                    app.selected_clock = "nature"
                    app.chime_hourly = False
                    app.chime_half_hour = True
                    app.chime_quarter_hour = True
                    
                    app.save_config()
                    
                    # Verify file was written
                    assert config_path.exists()
                    with open(config_path) as f:
                        saved = json.load(f)
                    
                    assert saved["volume"] == 80
                    assert saved["clock"] == "nature"
                    assert saved["chime_hourly"] is False
                    assert saved["chime_half_hour"] is True


class TestVolumeControl:
    """Test volume control methods."""

    def test_set_volume_updates_value(self):
        """set_volume should update current_volume."""
        with patch("accessiclock.app.wx"):
            with patch("accessiclock.app.Paths") as MockPaths:
                mock_paths = MagicMock()
                mock_paths.config_file = Path("/tmp/config.json")
                MockPaths.return_value = mock_paths
                
                from accessiclock.app import AccessiClockApp
                
                app = AccessiClockApp.__new__(AccessiClockApp)
                app.paths = mock_paths
                app.config = {}
                app.current_volume = 50
                app.selected_clock = "default"
                app.chime_hourly = True
                app.chime_half_hour = False
                app.chime_quarter_hour = False
                app.audio_player = None
                
                # Mock save_config to avoid file I/O
                app.save_config = MagicMock()
                
                app.set_volume(75)
                
                assert app.current_volume == 75
                app.save_config.assert_called_once()

    def test_set_volume_clamps_values(self):
        """set_volume should clamp to 0-100 range."""
        with patch("accessiclock.app.wx"):
            with patch("accessiclock.app.Paths") as MockPaths:
                mock_paths = MagicMock()
                mock_paths.config_file = Path("/tmp/config.json")
                MockPaths.return_value = mock_paths
                
                from accessiclock.app import AccessiClockApp
                
                app = AccessiClockApp.__new__(AccessiClockApp)
                app.paths = mock_paths
                app.config = {}
                app.current_volume = 50
                app.selected_clock = "default"
                app.chime_hourly = True
                app.chime_half_hour = False
                app.chime_quarter_hour = False
                app.audio_player = None
                app.save_config = MagicMock()
                
                app.set_volume(150)
                assert app.current_volume == 100
                
                app.set_volume(-50)
                assert app.current_volume == 0

    def test_set_volume_updates_audio_player(self):
        """set_volume should update audio player volume."""
        with patch("accessiclock.app.wx"):
            with patch("accessiclock.app.Paths") as MockPaths:
                mock_paths = MagicMock()
                mock_paths.config_file = Path("/tmp/config.json")
                MockPaths.return_value = mock_paths
                
                from accessiclock.app import AccessiClockApp
                
                app = AccessiClockApp.__new__(AccessiClockApp)
                app.paths = mock_paths
                app.config = {}
                app.current_volume = 50
                app.selected_clock = "default"
                app.chime_hourly = True
                app.chime_half_hour = False
                app.chime_quarter_hour = False
                app.audio_player = MagicMock()
                app.save_config = MagicMock()
                
                app.set_volume(75)
                
                app.audio_player.set_volume.assert_called_once_with(75)
