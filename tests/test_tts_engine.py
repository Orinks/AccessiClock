"""Tests for accessiclock.audio.tts_engine module."""

from datetime import date, time
from unittest.mock import MagicMock, patch


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

    def test_init_force_dummy(self):
        """force_dummy should override pyttsx3 availability."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        assert engine.engine_type == "dummy"
        assert engine._engine is None

    def test_init_pyttsx3_available(self):
        """Should use sapi5 engine when pyttsx3 is available."""
        mock_engine = MagicMock()
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            assert engine.engine_type == "sapi5"
            assert engine._engine is mock_engine
            mock_pyttsx3.init.assert_called_once()
            mock_engine.setProperty.assert_called_once_with("rate", 150)

    def test_init_pyttsx3_init_failure(self):
        """Should fall back to dummy if pyttsx3.init fails."""
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.side_effect = RuntimeError("init failed")

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            assert engine.engine_type == "dummy"


class TestRateProperty:
    """Test rate getter/setter."""

    def test_rate_getter(self):
        """rate property should return current rate."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True, rate=175)
        assert engine.rate == 175

    def test_rate_setter_dummy(self):
        """rate setter on dummy should update value without engine."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.rate = 250
        assert engine.rate == 250

    def test_rate_setter_clamps(self):
        """rate setter should clamp values."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.rate = 999
        assert engine.rate == 300
        engine.rate = 1
        assert engine.rate == 50

    def test_rate_setter_with_engine(self):
        """rate setter should update pyttsx3 engine."""
        mock_engine = MagicMock()
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            mock_engine.reset_mock()

            engine.rate = 200
            assert engine.rate == 200
            mock_engine.setProperty.assert_called_once_with("rate", 200)


class TestTimeFormatting:
    """Test time-to-speech formatting."""

    def test_format_time_12h_simple(self):
        """Should format time in simple 12-hour format."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)

        result = engine.format_time(time(15, 30), style="simple")
        assert "3" in result
        assert "30" in result
        assert "PM" in result

    def test_format_time_simple_on_hour(self):
        """Simple style on the hour should omit minutes."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(15, 0), style="simple")
        assert result == "3 PM"

    def test_format_time_simple_midnight(self):
        """Midnight should be 12 AM."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(0, 0), style="simple")
        assert "12" in result
        assert "AM" in result

    def test_format_time_simple_noon(self):
        """Noon should be 12 PM."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(12, 0), style="simple")
        assert "12" in result
        assert "PM" in result

    def test_format_time_natural(self):
        """Should format time in natural speech style."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)

        # Quarter past
        result = engine.format_time(time(14, 15), style="natural")
        assert "quarter past" in result.lower()

        # Half past
        result = engine.format_time(time(14, 30), style="natural")
        assert "half past" in result.lower()

        # On the hour
        result = engine.format_time(time(15, 0), style="natural")
        assert "o'clock" in result.lower()

    def test_format_time_natural_quarter_to(self):
        """Natural style at :45 should say 'quarter to'."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(14, 45), style="natural")
        assert "quarter to" in result.lower()

    def test_format_time_natural_quarter_to_noon_boundary(self):
        """At 11:45 AM, 'quarter to' should say 'quarter to 12 PM' not 'AM'."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(11, 45), style="natural")
        assert "quarter to" in result.lower()
        assert "12" in result
        assert "PM" in result

    def test_format_time_natural_quarter_to_midnight_boundary(self):
        """At 11:45 PM, 'quarter to' should say 'quarter to 12 AM' not 'PM'."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(23, 45), style="natural")
        assert "quarter to" in result.lower()
        assert "12" in result
        assert "AM" in result

    def test_format_time_natural_quarter_to_no_boundary(self):
        """At 2:45 PM, 'quarter to' should keep PM."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(14, 45), style="natural")
        assert "quarter to" in result.lower()
        assert "3" in result
        assert "PM" in result

    def test_format_time_natural_irregular_minute(self):
        """Natural style with irregular minutes should show time normally."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(14, 22), style="natural")
        assert "2:22" in result
        assert "PM" in result

    def test_format_time_precise(self):
        """Should format time with full precision."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)

        result = engine.format_time(time(9, 5), style="precise")
        assert "The time is" in result
        assert "9:05" in result
        assert "AM" in result

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

    def test_format_time_without_date_flag(self):
        """include_date=False should not include date."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(12, 0), include_date=False)
        assert "January" not in result
        assert "Monday" not in result

    def test_format_time_include_date_no_date_provided(self):
        """include_date=True but no date should not include date."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.format_time(time(12, 0), include_date=True, date=None)
        # Should still work, just no date prefix
        assert "12" in result


class TestSpeech:
    """Test speech synthesis."""

    def test_speak_dummy_no_crash(self):
        """speak() with dummy engine should not crash."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.speak("Hello world")  # Should not raise

    def test_speak_with_engine(self):
        """speak() should use pyttsx3 engine."""
        mock_engine = MagicMock()
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            engine.speak("Hello world")

            mock_engine.say.assert_called_once_with("Hello world")
            mock_engine.runAndWait.assert_called_once()

    def test_speak_engine_error_handled(self):
        """speak() should handle engine errors gracefully."""
        mock_engine = MagicMock()
        mock_engine.say.side_effect = RuntimeError("speech error")
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            # Should not raise
            engine.speak("Hello world")

    def test_speak_time_combines_format_and_speak(self):
        """speak_time() should format and speak the time."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.speak = MagicMock()

        engine.speak_time(time(15, 0))

        engine.speak.assert_called_once()
        call_arg = engine.speak.call_args[0][0]
        assert "3" in call_arg

    def test_speak_time_with_style(self):
        """speak_time() should pass style to format_time."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.speak = MagicMock()

        engine.speak_time(time(14, 30), style="natural")

        call_arg = engine.speak.call_args[0][0]
        assert "half past" in call_arg.lower()

    def test_speak_time_with_date(self):
        """speak_time() should support include_date."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.speak = MagicMock()

        engine.speak_time(
            time(12, 0),
            include_date=True,
            current_date=date(2025, 6, 15),
        )

        call_arg = engine.speak.call_args[0][0]
        assert "June" in call_arg or "15" in call_arg


class TestVoiceSelection:
    """Test voice selection and listing."""

    def test_list_voices_dummy(self):
        """Dummy engine should return empty list."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        voices = engine.list_voices()
        assert voices == []

    def test_list_voices_with_engine(self):
        """list_voices should return voice info from pyttsx3."""
        mock_engine = MagicMock()
        mock_voice1 = MagicMock()
        mock_voice1.id = "voice1_id"
        mock_voice1.name = "Voice One"
        mock_voice2 = MagicMock()
        mock_voice2.id = "voice2_id"
        mock_voice2.name = "Voice Two"
        mock_engine.getProperty.return_value = [mock_voice1, mock_voice2]

        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            voices = engine.list_voices()

            assert len(voices) == 2
            assert voices[0] == {"id": "voice1_id", "name": "Voice One"}
            assert voices[1] == {"id": "voice2_id", "name": "Voice Two"}
            mock_engine.getProperty.assert_called_with("voices")

    def test_list_voices_error_returns_empty(self):
        """list_voices should return empty list on error."""
        mock_engine = MagicMock()
        mock_engine.getProperty.side_effect = RuntimeError("voices error")
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            voices = engine.list_voices()
            assert voices == []

    def test_set_voice_dummy_returns_false(self):
        """set_voice on dummy engine should return False."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        result = engine.set_voice("Some Voice")
        assert result is False

    def test_set_voice_by_name(self):
        """set_voice should match by name."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.id = "voice_id_1"
        mock_voice.name = "Microsoft David"
        mock_engine.getProperty.return_value = [mock_voice]
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            result = engine.set_voice("Microsoft David")
            assert result is True
            mock_engine.setProperty.assert_called_with("voice", "voice_id_1")

    def test_set_voice_by_id(self):
        """set_voice should match by id."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.id = "HKEY_VOICE_1"
        mock_voice.name = "Microsoft David"
        mock_engine.getProperty.return_value = [mock_voice]
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            result = engine.set_voice("HKEY_VOICE_1")
            assert result is True
            mock_engine.setProperty.assert_called_with("voice", "HKEY_VOICE_1")

    def test_set_voice_not_found(self):
        """set_voice should return False if voice not found."""
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.id = "voice_id_1"
        mock_voice.name = "Microsoft David"
        mock_engine.getProperty.return_value = [mock_voice]
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            result = engine.set_voice("Nonexistent Voice")
            assert result is False

    def test_set_voice_error_returns_false(self):
        """set_voice should return False on error."""
        mock_engine = MagicMock()
        mock_engine.getProperty.side_effect = RuntimeError("voice error")
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            result = engine.set_voice("Some Voice")
            assert result is False


class TestCleanup:
    """Test cleanup method."""

    def test_cleanup_dummy_no_crash(self):
        """Cleanup on dummy engine should not crash."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        engine.cleanup()  # Should not raise

    def test_cleanup_with_engine(self):
        """Cleanup should stop pyttsx3 engine."""
        mock_engine = MagicMock()
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            engine.cleanup()
            mock_engine.stop.assert_called_once()

    def test_cleanup_engine_error_suppressed(self):
        """Cleanup should suppress engine stop errors."""
        mock_engine = MagicMock()
        mock_engine.stop.side_effect = RuntimeError("stop error")
        mock_pyttsx3 = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        with (
            patch("accessiclock.audio.tts_engine._PYTTSX3_AVAILABLE", True),
            patch("accessiclock.audio.tts_engine.pyttsx3", mock_pyttsx3, create=True),
        ):
            from accessiclock.audio.tts_engine import TTSEngine

            engine = TTSEngine()
            # Should not raise
            engine.cleanup()


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

    def test_dummy_set_voice_returns_false(self):
        """Dummy engine set_voice should always return False."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        assert engine.set_voice("any") is False

    def test_dummy_list_voices_empty(self):
        """Dummy engine list_voices should return empty list."""
        from accessiclock.audio.tts_engine import TTSEngine

        engine = TTSEngine(force_dummy=True)
        assert engine.list_voices() == []
