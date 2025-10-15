"""
Tests for TTS integration.
"""
import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from accessiclock.tts import TTSEngine


class TestTTSEngine(unittest.TestCase):
    """Test cases for TTSEngine class."""

    def test_tts_engine_creation(self):
        """Test that TTSEngine can be created."""
        engine = TTSEngine()
        self.assertIsNotNone(engine)

    def test_tts_can_speak(self):
        """Test that TTS engine has speak method."""
        engine = TTSEngine()
        # Should not raise an exception
        engine.speak("test", wait=False)


if __name__ == '__main__':
    unittest.main()
