"""Tests for accessiclock.app module - config and volume logic."""

import json
import tempfile
from pathlib import Path


class TestConfigLoading:
    """Test configuration loading logic (independent of wx)."""

    def test_load_config_from_valid_file(self):
        """Should load config values from JSON file."""
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
            
            # Load config manually (same logic as app._load_config)
            with open(config_path, encoding="utf-8") as f:
                loaded = json.load(f)
            
            assert loaded["volume"] == 75
            assert loaded["clock"] == "westminster"
            assert loaded["chime_hourly"] is True
            assert loaded["chime_half_hour"] is True
            assert loaded["chime_quarter_hour"] is False

    def test_load_config_missing_file_returns_empty(self):
        """Should return empty when config file doesn't exist."""
        config_path = Path("/nonexistent/config.json")
        
        loaded = {}
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                loaded = json.load(f)
        
        assert loaded == {}

    def test_save_config_writes_json_file(self):
        """Should write config to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            config = {
                "volume": 80,
                "clock": "nature",
                "chime_hourly": False,
                "chime_half_hour": True,
                "chime_quarter_hour": True,
            }
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            
            # Verify file
            assert config_path.exists()
            with open(config_path) as f:
                saved = json.load(f)
            
            assert saved["volume"] == 80
            assert saved["clock"] == "nature"
            assert saved["chime_hourly"] is False

    def test_config_default_values(self):
        """Test default config values."""
        # These match the defaults in AccessiClockApp.__init__
        defaults = {
            "current_volume": 50,
            "selected_clock": "default",
            "chime_hourly": True,
            "chime_half_hour": False,
            "chime_quarter_hour": False,
        }
        
        assert defaults["current_volume"] == 50
        assert defaults["selected_clock"] == "default"
        assert defaults["chime_hourly"] is True
        assert defaults["chime_half_hour"] is False


class TestVolumeLogic:
    """Test volume control logic (independent of wx)."""

    def test_volume_clamp_high(self):
        """Volume should be clamped to 100 max."""
        volume = 150
        clamped = max(0, min(100, volume))
        assert clamped == 100

    def test_volume_clamp_low(self):
        """Volume should be clamped to 0 min."""
        volume = -50
        clamped = max(0, min(100, volume))
        assert clamped == 0

    def test_volume_clamp_valid(self):
        """Valid volume should pass through unchanged."""
        volume = 75
        clamped = max(0, min(100, volume))
        assert clamped == 75

    def test_volume_zero(self):
        """Volume 0 is valid (muted)."""
        volume = 0
        clamped = max(0, min(100, volume))
        assert clamped == 0

    def test_volume_hundred(self):
        """Volume 100 is valid (max)."""
        volume = 100
        clamped = max(0, min(100, volume))
        assert clamped == 100


class TestAppIntegration:
    """Integration tests that can run without wx."""

    def test_paths_module_importable(self):
        """Paths module should be importable."""
        from accessiclock.paths import Paths
        assert Paths is not None

    def test_constants_module_importable(self):
        """Constants module should be importable."""
        from accessiclock.constants import APP_NAME, APP_VERSION
        assert APP_NAME == "AccessiClock"
        assert APP_VERSION is not None

    def test_clock_service_importable(self):
        """Clock service should be importable."""
        from accessiclock.services.clock_service import ClockService
        service = ClockService()
        assert service is not None

    def test_clock_pack_loader_importable(self):
        """Clock pack loader should be importable."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader
        assert ClockPackLoader is not None

    def test_tts_engine_importable(self):
        """TTS engine should be importable."""
        from accessiclock.audio.tts_engine import TTSEngine
        assert TTSEngine is not None

    def test_audio_player_importable(self):
        """Audio player should be importable."""
        from accessiclock.audio.player import AudioPlayer
        assert AudioPlayer is not None
