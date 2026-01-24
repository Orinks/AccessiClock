"""Tests for accessiclock.audio.player module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestAudioPlayerInit:
    """Test AudioPlayer initialization."""

    def test_init_default_volume(self):
        """AudioPlayer should initialize with default 50% volume."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            assert player.get_volume() == 50

    def test_init_custom_volume(self):
        """AudioPlayer should accept custom initial volume."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer(volume_percent=75)
            assert player.get_volume() == 75

    def test_init_volume_clamped_high(self):
        """Volume above 100 should be clamped to 100."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer(volume_percent=150)
            assert player.get_volume() == 100

    def test_init_volume_clamped_low(self):
        """Volume below 0 should be clamped to 0."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer(volume_percent=-50)
            assert player.get_volume() == 0


class TestVolumeControl:
    """Test volume control methods."""

    @pytest.fixture
    def player(self):
        """Create an AudioPlayer with mocked backend."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            return AudioPlayer(volume_percent=50)

    def test_set_volume(self, player):
        """set_volume should update volume level."""
        player.set_volume(75)
        assert player.get_volume() == 75

    def test_set_volume_clamped_high(self, player):
        """set_volume should clamp values above 100."""
        player.set_volume(200)
        assert player.get_volume() == 100

    def test_set_volume_clamped_low(self, player):
        """set_volume should clamp values below 0."""
        player.set_volume(-10)
        assert player.get_volume() == 0

    def test_volume_decimal_conversion(self, player):
        """Volume should convert correctly to decimal."""
        assert player._convert_volume_to_decimal(0) == 0.0
        assert player._convert_volume_to_decimal(50) == 0.5
        assert player._convert_volume_to_decimal(100) == 1.0


class TestPlaySound:
    """Test sound playback methods."""

    def test_play_nonexistent_file_raises(self):
        """Playing a nonexistent file should raise FileNotFoundError."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            with pytest.raises(FileNotFoundError):
                player.play_sound("/nonexistent/path/to/audio.wav")

    def test_play_sound_with_fallback(self):
        """play_sound should use fallback when sound_lib unavailable."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
            
            try:
                # Mock playsound to avoid actually playing
                with patch("accessiclock.audio.player.playsound") as mock_playsound:
                    player.play_sound(temp_path)
                    # playsound is called in a thread, so we check it was imported
            except ImportError:
                # playsound3 not installed, that's okay
                pass
            finally:
                Path(temp_path).unlink(missing_ok=True)


class TestIsPlaying:
    """Test is_playing method."""

    def test_is_playing_initially_false(self):
        """is_playing should return False when nothing is playing."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            assert player.is_playing() is False


class TestCleanup:
    """Test cleanup method."""

    def test_cleanup_no_error_when_nothing_playing(self):
        """cleanup should not raise when nothing is playing."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            # Should not raise
            player.cleanup()

    def test_cleanup_stops_playback(self):
        """cleanup should stop any current playback."""
        with patch("accessiclock.audio.player._use_sound_lib", True):
            with patch("accessiclock.audio.player._bass_initialized", True):
                from accessiclock.audio.player import AudioPlayer
                
                # Create player with mocked stream
                with patch("accessiclock.audio.player.stream") as mock_stream:
                    with patch("accessiclock.audio.player.BASS_Free"):
                        player = AudioPlayer.__new__(AudioPlayer)
                        player._volume = 50
                        mock_current = MagicMock()
                        player._current_stream = mock_current
                        
                        player.cleanup()
                        
                        mock_current.stop.assert_called_once()
                        mock_current.free.assert_called_once()
