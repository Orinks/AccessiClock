"""
AccessiClock wxPython application.

Main application class with screen reader accessibility support.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import wx

from .paths import Paths

if TYPE_CHECKING:
    from .ui.main_window import MainWindow

logger = logging.getLogger(__name__)


class AccessiClockApp(wx.App):
    """AccessiClock application using wxPython."""

    def __init__(self, portable_mode: bool = False):
        """
        Initialize the AccessiClock application.

        Args:
            portable_mode: If True, use portable mode (config alongside app).
        """
        self._portable_mode = portable_mode

        # Set up paths
        self.paths = Paths(portable_mode=portable_mode)

        # UI components (initialized in OnInit)
        self.main_window: MainWindow | None = None

        # Audio player (initialized in OnInit)
        self.audio_player = None

        # Configuration
        self.config: dict = {}

        # Clock state
        self.current_volume: int = 50
        self.selected_clock: str = "default"
        self.chime_hourly: bool = True
        self.chime_half_hour: bool = False
        self.chime_quarter_hour: bool = False

        super().__init__()

    def OnInit(self) -> bool:
        """Initialize the application (wxPython entry point)."""
        logger.info("Starting AccessiClock application (wxPython)")

        try:
            # Initialize audio player
            self._init_audio()

            # Load configuration
            self._load_config()

            # Create main window
            from .ui.main_window import MainWindow

            self.main_window = MainWindow(self)
            self.main_window.Show()
            self.SetTopWindow(self.main_window)

            logger.info("AccessiClock initialized successfully")
            return True

        except Exception as e:
            logger.exception(f"Failed to initialize AccessiClock: {e}")
            wx.MessageBox(
                f"Failed to start AccessiClock:\n\n{e}",
                "Startup Error",
                wx.OK | wx.ICON_ERROR,
            )
            return False

    def _init_audio(self) -> None:
        """Initialize the audio player."""
        try:
            from .audio.player import AudioPlayer

            self.audio_player = AudioPlayer(volume_percent=self.current_volume)
            logger.info("Audio player initialized")
        except Exception as e:
            logger.warning(f"Audio player initialization failed: {e}")
            self.audio_player = None

    def _load_config(self) -> None:
        """Load configuration from file."""
        config_file = self.paths.config_file
        if config_file.exists():
            try:
                import json

                with open(config_file, encoding="utf-8") as f:
                    self.config = json.load(f)

                # Apply loaded settings
                self.current_volume = self.config.get("volume", 50)
                self.selected_clock = self.config.get("clock", "default")
                self.chime_hourly = self.config.get("chime_hourly", True)
                self.chime_half_hour = self.config.get("chime_half_hour", False)
                self.chime_quarter_hour = self.config.get("chime_quarter_hour", False)

                logger.info(f"Configuration loaded from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

    def save_config(self) -> None:
        """Save configuration to file."""
        import json

        self.config.update(
            {
                "volume": self.current_volume,
                "clock": self.selected_clock,
                "chime_hourly": self.chime_hourly,
                "chime_half_hour": self.chime_half_hour,
                "chime_quarter_hour": self.chime_quarter_hour,
            }
        )

        try:
            config_file = self.paths.config_file
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def set_volume(self, volume: int) -> None:
        """Set the audio volume."""
        self.current_volume = max(0, min(100, volume))
        if self.audio_player:
            self.audio_player.set_volume(self.current_volume)
        self.save_config()

    def play_test_sound(self) -> bool:
        """Play a test sound. Returns True if successful."""
        if not self.audio_player:
            logger.warning("No audio player available")
            return False

        try:
            # TODO: Play actual clock chime from selected clock pack
            # For now, try to find a test sound
            test_sound = self.paths.app_dir / "audio" / "test_sound.wav"
            if test_sound.exists():
                self.audio_player.play_sound(str(test_sound))
                return True
            else:
                logger.warning(f"Test sound not found at {test_sound}")
                return False
        except Exception as e:
            logger.error(f"Failed to play test sound: {e}")
            return False

    def OnExit(self) -> int:
        """Clean up before exit."""
        logger.info("AccessiClock shutting down")

        # Save configuration
        self.save_config()

        # Clean up audio
        if self.audio_player:
            try:
                self.audio_player.cleanup()
            except Exception as e:
                logger.warning(f"Error cleaning up audio: {e}")

        return 0
