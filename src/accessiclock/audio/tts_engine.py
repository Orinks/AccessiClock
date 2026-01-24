"""
Text-to-Speech engine for AccessiClock.

Supports SAPI5 (Windows) via pyttsx3, with fallback to dummy engine.
"""

from __future__ import annotations

import logging
from datetime import date, time
from typing import Literal

from ..constants import TTS_RATE_DEFAULT, TTS_RATE_MAX, TTS_RATE_MIN

logger = logging.getLogger(__name__)

# Try to import pyttsx3
try:
    import pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False
    logger.debug("pyttsx3 not available")


TimeStyle = Literal["simple", "natural", "precise"]


class TTSEngine:
    """
    Text-to-Speech engine with time formatting.
    
    Uses pyttsx3 (SAPI5 on Windows) for speech synthesis.
    Falls back to a dummy engine if TTS is not available.
    """

    def __init__(
        self,
        rate: int = TTS_RATE_DEFAULT,
        force_dummy: bool = False,
    ):
        """
        Initialize the TTS engine.
        
        Args:
            rate: Speech rate in words per minute (50-300).
            force_dummy: Force use of dummy engine (for testing).
        """
        self._rate = self._clamp_rate(rate)
        self._engine = None
        self._voice_id: str | None = None
        
        if force_dummy or not _PYTTSX3_AVAILABLE:
            self.engine_type = "dummy"
            logger.info("Using dummy TTS engine")
        else:
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", self._rate)
                self.engine_type = "sapi5"
                logger.info("Using SAPI5 TTS engine")
            except Exception as e:
                logger.warning(f"Failed to initialize pyttsx3: {e}")
                self.engine_type = "dummy"

    def _clamp_rate(self, rate: int) -> int:
        """Clamp speech rate to valid range."""
        return max(TTS_RATE_MIN, min(TTS_RATE_MAX, rate))

    @property
    def rate(self) -> int:
        """Get the speech rate."""
        return self._rate

    @rate.setter
    def rate(self, value: int) -> None:
        """Set the speech rate."""
        self._rate = self._clamp_rate(value)
        if self._engine:
            self._engine.setProperty("rate", self._rate)

    def speak(self, text: str) -> None:
        """
        Speak the given text.
        
        Args:
            text: Text to speak.
        """
        if self.engine_type == "dummy":
            logger.debug(f"Dummy TTS: {text}")
            return

        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS speak error: {e}")

    def speak_time(
        self,
        current_time: time,
        style: TimeStyle = "simple",
        include_date: bool = False,
        current_date: date | None = None,
    ) -> None:
        """
        Speak the current time.
        
        Args:
            current_time: Time to announce.
            style: Formatting style ("simple", "natural", "precise").
            include_date: Whether to include the date.
            current_date: Date to include (if include_date is True).
        """
        text = self.format_time(
            current_time,
            style=style,
            include_date=include_date,
            date=current_date,
        )
        self.speak(text)

    def format_time(
        self,
        current_time: time,
        style: TimeStyle = "simple",
        include_date: bool = False,
        date: date | None = None,
    ) -> str:
        """
        Format time for speech.
        
        Args:
            current_time: Time to format.
            style: Formatting style.
            include_date: Whether to include the date.
            date: Date to include.
            
        Returns:
            Formatted time string for speech.
        """
        hour = current_time.hour
        minute = current_time.minute
        
        # Convert to 12-hour format
        am_pm = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12

        if style == "natural":
            text = self._format_natural(hour_12, minute, am_pm)
        elif style == "precise":
            text = self._format_precise(hour_12, minute, am_pm)
        else:  # simple
            text = self._format_simple(hour_12, minute, am_pm)

        if include_date and date:
            date_str = self._format_date(date)
            text = f"{date_str}, {text}"

        return text

    def _format_simple(self, hour: int, minute: int, am_pm: str) -> str:
        """Format time in simple style: '3:30 PM'."""
        if minute == 0:
            return f"{hour} {am_pm}"
        return f"{hour}:{minute:02d} {am_pm}"

    def _format_natural(self, hour: int, minute: int, am_pm: str) -> str:
        """Format time in natural speech style."""
        if minute == 0:
            return f"{hour} o'clock {am_pm}"
        elif minute == 15:
            return f"quarter past {hour} {am_pm}"
        elif minute == 30:
            return f"half past {hour} {am_pm}"
        elif minute == 45:
            next_hour = hour % 12 + 1
            if next_hour == 0:
                next_hour = 12
            return f"quarter to {next_hour} {am_pm}"
        else:
            return f"{hour}:{minute:02d} {am_pm}"

    def _format_precise(self, hour: int, minute: int, am_pm: str) -> str:
        """Format time with full precision: 'The time is 9:05 AM'."""
        return f"The time is {hour}:{minute:02d} {am_pm}"

    def _format_date(self, d: date) -> str:
        """Format date for speech."""
        return d.strftime("%A, %B %d")

    def list_voices(self) -> list[dict]:
        """
        List available voices.
        
        Returns:
            List of voice info dicts with 'id' and 'name'.
        """
        if self.engine_type == "dummy" or not self._engine:
            return []

        try:
            voices = self._engine.getProperty("voices")
            return [{"id": v.id, "name": v.name} for v in voices]
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return []

    def set_voice(self, name_or_id: str) -> bool:
        """
        Set the voice by name or ID.
        
        Args:
            name_or_id: Voice name or ID.
            
        Returns:
            True if voice was set, False otherwise.
        """
        if self.engine_type == "dummy" or not self._engine:
            return False

        try:
            voices = self._engine.getProperty("voices")
            for voice in voices:
                if voice.name == name_or_id or voice.id == name_or_id:
                    self._engine.setProperty("voice", voice.id)
                    self._voice_id = voice.id
                    logger.info(f"Voice set to: {voice.name}")
                    return True
            
            logger.warning(f"Voice not found: {name_or_id}")
            return False
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False

    def cleanup(self) -> None:
        """Clean up TTS resources."""
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
