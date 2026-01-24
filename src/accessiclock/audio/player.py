"""
AudioPlayer class for playing sound files with volume control.

Uses sound_lib library for thread-safe audio playback on Windows.
Falls back to playsound3 on other platforms.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Global flag to track if BASS has been initialized
_bass_initialized = False
_use_sound_lib = False

# Try to import sound_lib (cross-platform: Windows, macOS, Linux)
try:
    from sound_lib import stream
    from sound_lib.main import BASS_Free

    _use_sound_lib = True
    logger.debug("sound_lib available")
except ImportError:
    logger.debug("sound_lib not available, will use fallback")
except Exception as e:
    logger.debug(f"sound_lib initialization failed: {e}")


class AudioPlayer:
    """
    Audio player for playing sound files with volume control.

    Uses sound_lib library which provides thread-safe audio playback
    without blocking the UI thread. Falls back to playsound3 on non-Windows.
    """

    def __init__(self, volume_percent: int = 50):
        """
        Initialize AudioPlayer.

        Args:
            volume_percent: Initial volume level (0-100). Defaults to 50.
        """
        global _bass_initialized

        self._current_stream = None
        self._volume = self._clamp_volume(volume_percent)

        # Initialize BASS audio library if using sound_lib
        if _use_sound_lib and not _bass_initialized:
            try:
                from sound_lib import output

                output.Output()  # Initialize default output device
                _bass_initialized = True
                logger.info("BASS audio system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize BASS audio system: {e}")
                raise

        logger.info(f"AudioPlayer initialized with volume {self._volume}%")

    def _clamp_volume(self, volume_percent: int) -> int:
        """Clamp volume to valid range (0-100)."""
        return max(0, min(100, volume_percent))

    def _convert_volume_to_decimal(self, volume_percent: int) -> float:
        """Convert volume percentage to decimal (0.0-1.0) for sound_lib."""
        return volume_percent / 100.0

    def get_volume(self) -> int:
        """Get current volume level (0-100)."""
        return self._volume

    def set_volume(self, volume_percent: int) -> None:
        """Set volume level (0-100)."""
        self._volume = self._clamp_volume(volume_percent)
        logger.info(f"Volume set to {self._volume}%")

        # Update volume of currently playing stream if any (sound_lib only)
        if _use_sound_lib and self._current_stream and self.is_playing():
            self._current_stream.volume = self._convert_volume_to_decimal(self._volume)

    def play_sound(self, file_path: str) -> None:
        """
        Play an audio file.

        Args:
            file_path: Path to audio file to play.

        Raises:
            FileNotFoundError: If the audio file doesn't exist.
            Exception: If the audio file cannot be played.
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"Audio file not found: {file_path}")
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        if _use_sound_lib:
            self._play_with_sound_lib(path)
        else:
            self._play_with_fallback(path)

    def _play_with_sound_lib(self, path: Path) -> None:
        """Play audio using sound_lib (Windows)."""
        try:
            # Stop any currently playing sound
            if self._current_stream:
                self.stop()

            logger.info(f"Playing audio file: {path}")
            self._current_stream = stream.FileStream(file=str(path))
            self._current_stream.volume = self._convert_volume_to_decimal(self._volume)
            self._current_stream.play()

        except Exception as e:
            logger.error(f"Error playing audio file {path}: {e}")
            raise

    def _play_with_fallback(self, path: Path) -> None:
        """Play audio using playsound3 fallback."""
        try:
            import threading

            from playsound3 import playsound

            logger.info(f"Playing audio file (fallback): {path}")
            # Run in thread to avoid blocking
            thread = threading.Thread(target=playsound, args=(str(path),), daemon=True)
            thread.start()

        except ImportError:
            logger.error("playsound3 not installed, cannot play audio")
            raise
        except Exception as e:
            logger.error(f"Error playing audio file {path}: {e}")
            raise

    def stop(self) -> None:
        """Stop currently playing audio."""
        if _use_sound_lib and self._current_stream:
            try:
                logger.info("Stopping audio playback")
                self._current_stream.stop()
                self._current_stream.free()
                self._current_stream = None
            except Exception as e:
                logger.warning(f"Error stopping audio: {e}")
                self._current_stream = None

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        if _use_sound_lib and self._current_stream:
            try:
                return self._current_stream.is_playing
            except Exception:
                return False
        return False

    def cleanup(self) -> None:
        """Clean up audio resources. Call when shutting down."""
        global _bass_initialized

        logger.info("Cleaning up AudioPlayer resources")

        if self._current_stream:
            try:
                self._current_stream.stop()
                self._current_stream.free()
                self._current_stream = None
            except Exception as e:
                logger.warning(f"Error during AudioPlayer cleanup: {e}")

        # Free BASS library resources
        if _use_sound_lib and _bass_initialized:
            try:
                BASS_Free()
                _bass_initialized = False
                logger.info("BASS audio system freed")
            except Exception as e:
                logger.warning(f"Error freeing BASS audio system: {e}")
