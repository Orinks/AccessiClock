"""Tests for accessiclock.audio.tts_engine module.

TDD: These tests are written before the implementation.
"""

from datetime import time
from unittest.mock import MagicMock, patch

import pytest


class TestTTSEngine:
    """Test TTS engine initialization and configuration."""

    def test_init_default_engine(self):
        """Should initialize with SAPI5 as default engine on Windows."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine()
        assert engine.engine_type in ("sapi5", "dummy")

    def test_init_with_custom_rate(self):
        """Should accept custom speech rate."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine(rate=200)
        assert engine.rate == 200

    def test_rate_clamped_to_valid_range(self):
        """Rate should be clamped to valid range."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine(rate=500)  # Too high
        assert engine.rate <= 300
        
        engine2 = TTSEngine(rate=10)  # Too low
        assert engine2.rate >= 50


class TestTimeFormatting:
    """Test time-to-speech formatting."""

    def test_format_time_12h_simple(self):
        """Should format time in simple 12-hour format."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine()
        
        result = engine.format_time(time(15, 30), style="simple")
        assert "3" in result
        assert "30" in result
        assert "PM" in result.upper() or "P.M." in result.upper()

    def test_format_time_natural(self):
        """Should format time in natural speech style."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine()
        
        # Quarter past
        result = engine.format_time(time(14, 15), style="natural")
        assert "quarter" in result.lower() or "15" in result
        
        # Half past
        result = engine.format_time(time(14, 30), style="natural")
        assert "half" in result.lower() or "30" in result
        
        # On the hour
        result = engine.format_time(time(15, 0), style="natural")
        assert "o'clock" in result.lower() or "00" in result or "3" in result

    def test_format_time_precise(self):
        """Should format time with full precision."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine()
        
        result = engine.format_time(time(9, 5), style="precise")
        assert "9" in result
        assert "05" in result or "5" in result
        assert "AM" in result.upper() or "A.M." in result.upper()

    def test_format_time_with_date(self):
        """Should optionally include date."""
        from datetime import datetime
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine()
        
        result = engine.format_time(
            time(12, 0),
            include_date=True,
            date=datetime(2025, 1, 24).date()
        )
        assert "January" in result or "24" in result or "Friday" in result


class TestSpeech:
    """Test speech synthesis."""

    def test_speak_uses_engine(self):
        """speak() should use the TTS engine when pyttsx3 available."""
        from accessiclock.audio.tts_engine import TTSEngine, _PYTTSX3_AVAILABLE
        
        if not _PYTTSX3_AVAILABLE:
            # Can't test real engine without pyttsx3
            pytest.skip("pyttsx3 not available")
        
        # Test with real engine (mocked)
        engine = TTSEngine()
        if engine._engine:
            engine._engine.say = MagicMock()
            engine._engine.runAndWait = MagicMock()
            
            engine.speak("Hello world")
            
            engine._engine.say.assert_called()
            engine._engine.runAndWait.assert_called()

    def test_speak_time_combines_format_and_speak(self):
        """speak_time() should format and speak the time."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine(force_dummy=True)  # Use dummy to avoid pyttsx3
        engine.speak = MagicMock()  # Mock the speak method
        
        engine.speak_time(time(15, 0))
        
        engine.speak.assert_called_once()
        call_arg = engine.speak.call_args[0][0]
        assert "3" in call_arg or "15" in call_arg


class TestVoiceSelection:
    """Test voice selection and listing."""

    def test_list_voices(self):
        """Should list available voices."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        engine = TTSEngine()
        voices = engine.list_voices()
        
        assert isinstance(voices, list)
        # May be empty on systems without TTS

    def test_set_voice_by_name(self):
        """Should set voice by name when pyttsx3 available."""
        from accessiclock.audio.tts_engine import TTSEngine, _PYTTSX3_AVAILABLE
        
        if not _PYTTSX3_AVAILABLE:
            # Test that dummy engine returns False
            tts = TTSEngine(force_dummy=True)
            result = tts.set_voice("Microsoft David")
            assert result is False
            return
        
        # Test with real engine
        tts = TTSEngine()
        voices = tts.list_voices()
        if voices:
            # Try to set the first available voice
            result = tts.set_voice(voices[0]["name"])
            assert result is True


class TestDummyEngine:
    """Test dummy/fallback engine for systems without TTS."""

    def test_dummy_engine_does_not_crash(self):
        """Dummy engine should not crash when TTS unavailable."""
        from accessiclock.audio.tts_engine import TTSEngine
        
        # Force dummy mode
        engine = TTSEngine(force_dummy=True)
        
        # These should not raise
        engine.speak("Test")
        engine.speak_time(time(12, 0))
        voices = engine.list_voices()
        
        assert engine.engine_type == "dummy"
        assert voices == []
