"""
Tests for audio playback functionality.
"""
import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from accessiclock.audio import AudioPlayer


class TestAudioPlayer(unittest.TestCase):
    """Test cases for AudioPlayer class."""

    def test_audio_player_creation(self):
        """Test that AudioPlayer can be created."""
        player = AudioPlayer()
        self.assertIsNotNone(player)

    def test_audio_player_play_nonexistent_file(self):
        """Test that playing a nonexistent file doesn't crash."""
        player = AudioPlayer()
        # Should not raise an exception
        player.play_sound("/nonexistent/file.wav")

    def test_audio_player_play_async(self):
        """Test that async playback method exists and can be called."""
        player = AudioPlayer()
        # Should not raise an exception
        player.play_sound_async("/nonexistent/file.wav")


if __name__ == '__main__':
    unittest.main()
