"""Tests for accessiclock.audio.tts_engine module."""

from datetime import date, time
from unittest.mock import MagicMock, patch


# Helper to create a TTSEngine with mocked pyttsx3
def _make_tts_with_engine(mock_engine, rate=150):
    """Create a TTSEngine with a mocked pyttsx3 backend."""
    from accessiclock.audio.tts_engine import TTSEngine

    with (
        patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
        patch("accessiclock.audio.tts_engine.pyttsx3") as mock_pyttsx3,
    ):
        mock_pyttsx3.init.return_value = mock_engine
        return TTSEngine(rate=rate)


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

        engine = TTSEngine(rate=500)
        assert engine.rate <= 300

        engine2 = TTSEngine(rate=10)
        assert engine2.rate >= 50

    def test_init_pyttsx3_success(self):
        """Should initialize sapi5 engine when pyttsx3 is available."""
        mock_engine = MagicMock()
        tts = _make_tts_with_engine(mock_engine)
        assert tts.engine_type == "sapi5"

    def test_init_pyttsx3_failure_falls_back_to_dummy(self):
        """Should fall back to dummy if pyttsx3.init raises."""
        from accessiclock.audio.tts_engine import TTSEngine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3") as mock_pyttsx3,
        ):
            mock_pyttsx3.init.side_effect = RuntimeError("no audio")
            engine = TTSEngine(rate=150)
            assert engine.engine_type == "dummy"

    def test_force_dummy(self):
        """force_dummy should use dummy engine regardless."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        assert engine.engine_type == "dummy"

    def test_rate_setter_updates_engine(self):
        """Setting rate should update both internal and engine property."""
        mock_engine = MagicMock()
        tts = _make_tts_with_engine(mock_engine)
        mock_engine.reset_mock()

        tts.rate = 200
        assert tts.rate == 200
        mock_engine.setProperty.assert_called_with("rate", 200)

    def test_rate_setter_dummy_no_crash(self):
        """Setting rate on dummy engine should not crash."""
        from accessiclock.audio.tts_engine import TTSEngine

        tts = TTSEngine(force_dummy=True)
        tts.rate = 250
        assert tts.rate == 250


class TestTimeFormatting:
    """Test time-to-speech formatting."""

    def test_format_time_12h_simple(self):
        """Should format time in simple 12-hour format."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(15, 30), style="simple")
        assert "3" in result
        assert "30" in result
        assert "PM" in result.upper()

    def test_format_time_simple_on_the_hour(self):
        """Simple format on the hour should omit minutes."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(15, 0), style="simple")
        assert "3" in result
        assert "PM" in result.upper()

    def test_format_time_natural(self):
        """Should format time in natural speech style."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)

        result = engine.format_time(time(14, 15), style="natural")
        assert "quarter" in result.lower()

        result = engine.format_time(time(14, 30), style="natural")
        assert "half" in result.lower()

        result = engine.format_time(time(15, 0), style="natural")
        assert "o'clock" in result.lower()

    def test_format_time_natural_quarter_to(self):
        """Natural format for :45 should say 'quarter to'."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(14, 45), style="natural")
        assert "quarter to" in result.lower()

    def test_format_time_natural_other_minutes(self):
        """Natural format for non-special minutes should show time."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(14, 22), style="natural")
        assert "22" in result
        assert "PM" in result.upper()

    def test_format_time_precise(self):
        """Should format time with full precision."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(9, 5), style="precise")
        assert "9" in result
        assert "05" in result
        assert "AM" in result.upper()
        assert result.startswith("The time is")

    def test_format_time_with_date(self):
        """Should optionally include date."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(
            time(12, 0),
            include_date=True,
            date=date(2025, 1, 24),
        )
        assert "January" in result or "24" in result or "Friday" in result

    def test_format_time_midnight_hour(self):
        """Midnight (hour 0) should display as 12 AM."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(0, 0), style="simple")
        assert "12" in result
        assert "AM" in result.upper()

    def test_format_time_noon(self):
        """Noon (hour 12) should display as 12 PM."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(12, 0), style="simple")
        assert "12" in result
        assert "PM" in result.upper()


class TestSpeech:
    """Test speech synthesis."""

    def test_speak_dummy_does_not_crash(self):
        """speak() with dummy engine should not raise."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.speak("Hello world")

    def test_speak_uses_engine(self):
        """speak() should call engine.say and runAndWait."""
        mock_engine = MagicMock()
        tts = _make_tts_with_engine(mock_engine)
        tts.speak("Hello")
        mock_engine.say.assert_called_with("Hello")
        mock_engine.runAndWait.assert_called_once()

    def test_speak_error_handled(self):
        """speak() should not raise on engine error."""
        mock_engine = MagicMock()
        mock_engine.say.side_effect = RuntimeError("speak error")
        tts = _make_tts_with_engine(mock_engine)
        # Should not raise
        tts.speak("Hello")

    def test_speak_time_combines_format_and_speak(self):
        """speak_time() should format and speak the time."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.speak = MagicMock()

        engine.speak_time(time(15, 0))

        engine.speak.assert_called_once()
        call_arg = engine.speak.call_args[0][0]
        assert "3" in call_arg or "15" in call_arg

    def test_speak_time_with_style_and_date(self):
        """speak_time with all options should work."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.speak = MagicMock()

        engine.speak_time(
            time(9, 30),
            style="natural",
            include_date=True,
            current_date=date(2025, 6, 15),
        )

        engine.speak.assert_called_once()
        call_arg = engine.speak.call_args[0][0]
        assert "half past" in call_arg.lower() or "30" in call_arg


class TestVoiceSelection:
    """Test voice selection and listing."""

    def _make_mock_voice(self, voice_id="voice1", name="Test Voice"):
        mock_voice = MagicMock()
        mock_voice.id = voice_id
        mock_voice.name = name
        return mock_voice

    def test_list_voices_dummy_returns_empty(self):
        """Dummy engine should return empty voice list."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        assert engine.list_voices() == []

    def test_list_voices_with_engine(self):
        """Should list available voices from engine."""
        mock_engine = MagicMock()
        mock_voice = self._make_mock_voice()
        mock_engine.getProperty.return_value = [mock_voice]

        tts = _make_tts_with_engine(mock_engine)
        voices = tts.list_voices()
        assert len(voices) == 1
        assert voices[0]["id"] == "voice1"
        assert voices[0]["name"] == "Test Voice"

    def test_list_voices_exception_returns_empty(self):
        """list_voices should return [] on exception."""
        mock_engine = MagicMock()
        mock_engine.getProperty.side_effect = RuntimeError("voice error")

        tts = _make_tts_with_engine(mock_engine)
        assert tts.list_voices() == []

    def test_set_voice_dummy_returns_false(self):
        """Dummy engine should return False for set_voice."""
        from accessiclock.audio.tts_engine import TTSEngine

        tts = TTSEngine(force_dummy=True)
        assert tts.set_voice("Microsoft David") is False

    def test_set_voice_by_name(self):
        """Should set voice when matching by name."""
        mock_engine = MagicMock()
        mock_voice = self._make_mock_voice()
        mock_engine.getProperty.return_value = [mock_voice]

        tts = _make_tts_with_engine(mock_engine)
        assert tts.set_voice("Test Voice") is True
        mock_engine.setProperty.assert_called_with("voice", "voice1")

    def test_set_voice_by_id(self):
        """Should set voice when matching by ID."""
        mock_engine = MagicMock()
        mock_voice = self._make_mock_voice()
        mock_engine.getProperty.return_value = [mock_voice]

        tts = _make_tts_with_engine(mock_engine)
        assert tts.set_voice("voice1") is True
        mock_engine.setProperty.assert_called_with("voice", "voice1")

    def test_set_voice_not_found(self):
        """Should return False when voice not found."""
        mock_engine = MagicMock()
        mock_voice = self._make_mock_voice()
        mock_engine.getProperty.return_value = [mock_voice]

        tts = _make_tts_with_engine(mock_engine)
        assert tts.set_voice("Nonexistent Voice") is False

    def test_set_voice_exception(self):
        """Should return False on exception during voice setting."""
        mock_engine = MagicMock()
        mock_engine.getProperty.side_effect = RuntimeError("voice error")

        tts = _make_tts_with_engine(mock_engine)
        assert tts.set_voice("Any Voice") is False


class TestCleanup:
    """Test TTS engine cleanup."""

    def test_cleanup_dummy_no_crash(self):
        """Cleanup on dummy engine should not crash."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.cleanup()

    def test_cleanup_stops_engine(self):
        """Cleanup should call engine.stop()."""
        mock_engine = MagicMock()
        tts = _make_tts_with_engine(mock_engine)
        tts.cleanup()
        mock_engine.stop.assert_called_once()

    def test_cleanup_exception_suppressed(self):
        """Cleanup should suppress exceptions from engine.stop()."""
        mock_engine = MagicMock()
        mock_engine.stop.side_effect = RuntimeError("cleanup error")
        tts = _make_tts_with_engine(mock_engine)
        # Should not raise
        tts.cleanup()


class TestDummyEngine:
    """Test dummy/fallback engine for systems without TTS."""

    def test_dummy_engine_does_not_crash(self):
        """Dummy engine should not crash when TTS unavailable."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)

        engine.speak("Test")
        engine.speak_time(time(12, 0))
        voices = engine.list_voices()

        assert engine.engine_type == "dummy"
        assert voices == []
