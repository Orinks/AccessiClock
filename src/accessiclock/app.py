"""AccessiClock wxPython application."""

from __future__ import annotations

import logging
from datetime import time as dt_time
from typing import TYPE_CHECKING

import wx

from .audio.tts_engine import TTSEngine
from .core.settings import AppSettings, load_settings, save_settings
from .paths import Paths
from .services.clock_pack_loader import ClockPackLoader
from .services.clock_service import ClockService

if TYPE_CHECKING:
    from .ui.main_window import MainWindow

logger = logging.getLogger(__name__)


class AccessiClockApp(wx.App):
    """AccessiClock application using wxPython."""

    def __init__(self, portable_mode: bool = False):
        self._portable_mode = portable_mode
        self.paths = Paths(portable_mode=portable_mode)

        self.main_window: MainWindow | None = None
        self.audio_player = None
        self.tts_engine: TTSEngine | None = None
        self.clock_service: ClockService | None = None
        self.clock_pack_loader: ClockPackLoader | None = None

        self.settings = AppSettings()
        self.current_volume = self.settings.volume
        self.selected_clock = self.settings.clock
        self.chime_hourly = self.settings.chime_hourly
        self.chime_half_hour = self.settings.chime_half_hour
        self.chime_quarter_hour = self.settings.chime_quarter_hour

        super().__init__()

    def OnInit(self) -> bool:
        """Initialize the app and create the main window."""
        logger.info("Starting AccessiClock wxPython app")
        try:
            self._startup()
            return True
        except Exception:
            logger.exception("Startup failed")
            wx.MessageBox("AccessiClock could not start. See log file for details.", "Startup Error")
            return False

    def _startup(self) -> None:
        self._init_services()
        self._init_audio()
        self._init_tts()
        self._load_config()
        self._sync_service_settings()

        from .ui.main_window import MainWindow

        self.main_window = MainWindow(self)
        self.main_window.Show()
        self.SetTopWindow(self.main_window)

    def _init_services(self) -> None:
        self.clock_service = ClockService()
        self.clock_pack_loader = ClockPackLoader(self.paths.clocks_dir)
        self.clock_pack_loader.discover_packs()

    def _init_audio(self) -> None:
        try:
            from .audio.player import AudioPlayer

            self.audio_player = AudioPlayer(volume_percent=self.current_volume)
        except Exception:
            logger.warning("Audio player unavailable", exc_info=True)
            self.audio_player = None

    def _init_tts(self) -> None:
        try:
            self.tts_engine = TTSEngine()
        except Exception:
            logger.warning("TTS unavailable", exc_info=True)
            self.tts_engine = None

    def _sync_service_settings(self) -> None:
        if not self.clock_service:
            return
        self.clock_service.chime_hourly = self.chime_hourly
        self.clock_service.chime_half_hour = self.chime_half_hour
        self.clock_service.chime_quarter_hour = self.chime_quarter_hour

    def _load_config(self) -> None:
        self.settings = load_settings(self.paths.config_file)

        self.current_volume = self.settings.volume
        self.selected_clock = self.settings.clock
        self.chime_hourly = self.settings.chime_hourly
        self.chime_half_hour = self.settings.chime_half_hour
        self.chime_quarter_hour = self.settings.chime_quarter_hour

        if self.clock_service and self.settings.quiet_hours_enabled:
            try:
                sh, sm = map(int, self.settings.quiet_start.split(":"))
                eh, em = map(int, self.settings.quiet_end.split(":"))
                self.clock_service.set_quiet_hours(dt_time(sh, sm), dt_time(eh, em))
            except (TypeError, ValueError):
                logger.warning("Invalid quiet hours in config; disabling")
                self.clock_service.quiet_hours_enabled = False

    def save_config(self) -> None:
        if self.clock_service and self.clock_service.quiet_hours_enabled:
            quiet_enabled = True
            quiet_start = self.clock_service.quiet_start.strftime("%H:%M")
            quiet_end = self.clock_service.quiet_end.strftime("%H:%M")
        else:
            quiet_enabled = False
            quiet_start = self.settings.quiet_start
            quiet_end = self.settings.quiet_end

        self.settings = AppSettings(
            volume=self.current_volume,
            clock=self.selected_clock,
            chime_hourly=self.chime_hourly,
            chime_half_hour=self.chime_half_hour,
            chime_quarter_hour=self.chime_quarter_hour,
            quiet_hours_enabled=quiet_enabled,
            quiet_start=quiet_start,
            quiet_end=quiet_end,
        )
        self._sync_service_settings()
        save_settings(self.paths.config_file, self.settings)

    def set_volume(self, volume: int) -> None:
        self.current_volume = max(0, min(100, volume))
        if self.audio_player:
            self.audio_player.set_volume(self.current_volume)
        self.save_config()

    def play_chime(self, chime_type: str) -> bool:
        if not self.audio_player or not self.clock_pack_loader:
            return False
        try:
            pack_info = self.clock_pack_loader.get_pack(self.selected_clock)
            if not pack_info:
                return False
            sound_path = pack_info.get_sound_path(chime_type)
            if not sound_path or not sound_path.exists():
                return False
            self.audio_player.play_sound(str(sound_path))
            return True
        except Exception:
            logger.warning("Unable to play %s chime", chime_type, exc_info=True)
            return False

    def play_test_sound(self) -> bool:
        return self.play_chime("preview") or self.play_chime("hour")

    def announce_time(self, style: str = "simple") -> bool:
        if not self.tts_engine:
            return False
        from datetime import datetime

        self.tts_engine.speak_time(datetime.now().time(), style=style)
        return True

    def check_and_play_chime(self) -> str | None:
        if not self.clock_service:
            return None
        from datetime import datetime

        now = datetime.now().time()
        chime_type = self.clock_service.should_chime_now(now)
        if chime_type and self.play_chime(chime_type):
            self.clock_service.mark_chimed(now)
            return chime_type
        return None

    def get_available_clocks(self) -> list[str]:
        if not self.clock_pack_loader or not self.clock_pack_loader._cache:
            return ["Default"]
        return [info.name for info in self.clock_pack_loader._cache.values()]

    def OnExit(self) -> int:
        logger.info("Shutting down AccessiClock")
        self.save_config()

        if self.audio_player:
            try:
                self.audio_player.cleanup()
            except Exception:
                logger.warning("Audio cleanup failed", exc_info=True)
        if self.tts_engine:
            try:
                self.tts_engine.cleanup()
            except Exception:
                logger.warning("TTS cleanup failed", exc_info=True)
        return 0
