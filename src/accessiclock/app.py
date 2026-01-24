"""
AccessiClock wxPython application.

Main application class with screen reader accessibility support.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import wx

from .audio.tts_engine import TTSEngine
from .paths import Paths
from .services.clock_pack_loader import ClockPackLoader
from .services.clock_service import ClockService

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

        # TTS engine (initialized in OnInit)
        self.tts_engine: TTSEngine | None = None

        # Services
        self.clock_service: ClockService | None = None
        self.clock_pack_loader: ClockPackLoader | None = None

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
            # Initialize services
            self._init_services()

            # Initialize audio player
            self._init_audio()

            # Initialize TTS engine
            self._init_tts()

            # Load configuration
            self._load_config()

            # Sync service settings with config
            self._sync_service_settings()

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

    def _init_services(self) -> None:
        """Initialize application services."""
        # Initialize clock service
        self.clock_service = ClockService()
        logger.info("Clock service initialized")

        # Initialize clock pack loader
        self.clock_pack_loader = ClockPackLoader(self.paths.clocks_dir)
        self.clock_pack_loader.discover_packs()
        logger.info(f"Discovered {len(self.clock_pack_loader._cache)} clock packs")

    def _sync_service_settings(self) -> None:
        """Sync service settings with loaded configuration."""
        if self.clock_service:
            self.clock_service.chime_hourly = self.chime_hourly
            self.clock_service.chime_half_hour = self.chime_half_hour
            self.clock_service.chime_quarter_hour = self.chime_quarter_hour
            logger.debug("Clock service settings synced with config")

    def _init_audio(self) -> None:
        """Initialize the audio player."""
        try:
            from .audio.player import AudioPlayer

            self.audio_player = AudioPlayer(volume_percent=self.current_volume)
            logger.info("Audio player initialized")
        except Exception as e:
            logger.warning(f"Audio player initialization failed: {e}")
            self.audio_player = None

    def _init_tts(self) -> None:
        """Initialize the TTS engine."""
        try:
            self.tts_engine = TTSEngine()
            logger.info(f"TTS engine initialized ({self.tts_engine.engine_type})")
        except Exception as e:
            logger.warning(f"TTS engine initialization failed: {e}")
            self.tts_engine = None

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

        # Sync with clock service
        self._sync_service_settings()

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

    def play_chime(self, chime_type: str) -> bool:
        """
        Play a chime sound from the selected clock pack.
        
        Args:
            chime_type: Type of chime ("hour", "half_hour", "quarter_hour", "preview").
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.audio_player:
            logger.warning("No audio player available")
            return False

        if not self.clock_pack_loader:
            logger.warning("No clock pack loader available")
            return False

        try:
            pack_info = self.clock_pack_loader.get_pack(self.selected_clock)
            if not pack_info:
                logger.warning(f"Clock pack not found: {self.selected_clock}")
                return False

            sound_path = pack_info.get_sound_path(chime_type)
            if not sound_path or not sound_path.exists():
                logger.warning(f"Sound not found: {chime_type} in {self.selected_clock}")
                return False

            self.audio_player.play_sound(str(sound_path))
            logger.info(f"Playing {chime_type} chime from {self.selected_clock}")
            return True

        except Exception as e:
            logger.error(f"Failed to play chime: {e}")
            return False

    def play_test_sound(self) -> bool:
        """Play a test/preview sound. Returns True if successful."""
        # Try to play preview from selected clock pack
        if self.play_chime("preview"):
            return True
        
        # Fall back to hour chime
        if self.play_chime("hour"):
            return True

        # Last resort: try built-in test sound
        if not self.audio_player:
            logger.warning("No audio player available")
            return False

        try:
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

    def announce_time(self, style: str = "simple") -> bool:
        """
        Announce the current time using TTS.
        
        Args:
            style: Time format style ("simple", "natural", "precise").
            
        Returns:
            True if announced, False if TTS unavailable.
        """
        if not self.tts_engine:
            logger.warning("TTS engine not available")
            return False

        from datetime import datetime

        current_time = datetime.now().time()
        self.tts_engine.speak_time(current_time, style=style)
        logger.info(f"Time announced: {current_time.strftime('%I:%M %p')}")
        return True

    def check_and_play_chime(self) -> str | None:
        """
        Check if a chime should play now and play it.
        
        Called by the main window's timer tick.
        
        Returns:
            The type of chime played, or None if no chime.
        """
        if not self.clock_service:
            return None

        from datetime import datetime

        current_time = datetime.now().time()
        chime_type = self.clock_service.should_chime_now(current_time)

        if chime_type:
            if self.play_chime(chime_type):
                self.clock_service.mark_chimed(current_time)
                return chime_type

        return None

    def get_available_clocks(self) -> list[str]:
        """
        Get list of available clock pack names.
        
        Returns:
            List of clock pack display names.
        """
        if not self.clock_pack_loader:
            return ["Default"]

        packs = self.clock_pack_loader._cache
        if not packs:
            return ["Default"]

        return [info.name for info in packs.values()]

    def get_clock_pack_ids(self) -> list[str]:
        """
        Get list of available clock pack IDs.
        
        Returns:
            List of clock pack IDs (directory names).
        """
        if not self.clock_pack_loader:
            return ["default"]

        return list(self.clock_pack_loader._cache.keys()) or ["default"]

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

        # Clean up TTS
        if self.tts_engine:
            try:
                self.tts_engine.cleanup()
            except Exception as e:
                logger.warning(f"Error cleaning up TTS: {e}")

        return 0
