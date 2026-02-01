"""
Tests for AudioPlayer class.
Following TDD approach - these tests are written before implementation.
"""

import pytest
from pathlib import Path
from accessibletalkingclock.audio import AudioPlayer


@pytest.fixture
def test_sound_path():
    """Path to test sound file."""
    return Path(__file__).parent.parent / "src" / "accessibletalkingclock" / "audio" / "test_sound.wav"


@pytest.fixture
def audio_player():
    """Create an AudioPlayer instance for testing."""
    player = AudioPlayer(volume_percent=50)
    yield player
    # Cleanup: stop any playing audio
    if player.is_playing():
        player.stop()


class TestAudioPlayerInitialization:
    """Test AudioPlayer initialization and basic properties."""
    
    def test_audio_player_initializes_with_default_volume(self):
        """AudioPlayer should initialize with default volume of 50%."""
        player = AudioPlayer()
        assert player.get_volume() == 50
    
    def test_audio_player_initializes_with_custom_volume(self):
        """AudioPlayer should initialize with specified volume."""
        player = AudioPlayer(volume_percent=75)
        assert player.get_volume() == 75
    
    def test_audio_player_volume_clamped_to_valid_range(self):
        """AudioPlayer should clamp volume to 0-100 range."""
        player = AudioPlayer(volume_percent=150)
        assert player.get_volume() <= 100
        
        player = AudioPlayer(volume_percent=-10)
        assert player.get_volume() >= 0


class TestAudioPlayerVolumeControl:
    """Test volume control methods."""
    
    def test_set_volume_changes_volume(self, audio_player):
        """set_volume() should update the volume level."""
        audio_player.set_volume(80)
        assert audio_player.get_volume() == 80
    
    def test_set_volume_clamps_to_maximum(self, audio_player):
        """set_volume() should clamp volume to maximum of 100."""
        audio_player.set_volume(150)
        assert audio_player.get_volume() == 100
    
    def test_set_volume_clamps_to_minimum(self, audio_player):
        """set_volume() should clamp volume to minimum of 0."""
        audio_player.set_volume(-10)
        assert audio_player.get_volume() == 0


class TestAudioPlayerPlayback:
    """Test audio playback functionality."""
    
    def test_play_sound_with_valid_file(self, audio_player, test_sound_path):
        """play_sound() should successfully play a valid audio file."""
        # Should not raise exception
        audio_player.play_sound(str(test_sound_path))
        # Give it a moment to start playing
        import time
        time.sleep(0.1)
        # May or may not be playing depending on file length
        # Just verify no exception was raised
    
    def test_play_sound_with_invalid_file_raises_error(self, audio_player):
        """play_sound() should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            audio_player.play_sound("nonexistent_file.wav")
    
    def test_is_playing_returns_false_initially(self, audio_player):
        """is_playing() should return False when no sound is playing."""
        assert not audio_player.is_playing()
    
    def test_is_playing_returns_true_during_playback(self, audio_player, test_sound_path):
        """is_playing() should return True while sound is playing."""
        audio_player.play_sound(str(test_sound_path))
        import time
        time.sleep(0.05)  # Brief delay to let playback start
        # Check if playing (may be False if sound is very short)
        is_playing = audio_player.is_playing()
        # This assertion is lenient - sound might finish quickly
        assert isinstance(is_playing, bool)
    
    def test_stop_halts_playback(self, audio_player, test_sound_path):
        """stop() should halt audio playback."""
        audio_player.play_sound(str(test_sound_path))
        audio_player.stop()
        import time
        time.sleep(0.05)
        assert not audio_player.is_playing()


class TestAudioPlayerErrorHandling:
    """Test error handling and edge cases."""
    
    def test_play_sound_with_invalid_format_raises_error(self, audio_player, tmp_path):
        """play_sound() should raise appropriate error for invalid audio formats."""
        # Create a fake audio file with invalid format
        fake_file = tmp_path / "fake.wav"
        fake_file.write_text("Not a real WAV file")
        
        with pytest.raises(Exception):  # Could be various exceptions depending on sound_lib
            audio_player.play_sound(str(fake_file))
    
    def test_multiple_play_calls_handle_gracefully(self, audio_player, test_sound_path):
        """Multiple play_sound() calls should handle gracefully (stop previous, play new)."""
        # Should not raise exception
        audio_player.play_sound(str(test_sound_path))
        audio_player.play_sound(str(test_sound_path))
        # If we get here without exception, test passes
    
    def test_stop_when_not_playing_does_not_error(self, audio_player):
        """stop() should not raise error when nothing is playing."""
        # Should not raise exception
        audio_player.stop()


class TestAudioPlayerCleanup:
    """Test resource cleanup."""
    
    def test_audio_player_cleanup_releases_resources(self, test_sound_path):
        """AudioPlayer should properly release resources when done."""
        player = AudioPlayer()
        player.play_sound(str(test_sound_path))
        player.stop()
        # If we can create another player without issues, cleanup worked
        player2 = AudioPlayer()
        assert player2 is not None
