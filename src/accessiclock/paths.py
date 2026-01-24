"""Path management for AccessiClock."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .constants import APP_NAME, DEFAULT_CLOCKS_DIRNAME, DEFAULT_CONFIG_FILENAME


class Paths:
    """Manages application paths for config, data, and resources."""

    def __init__(self, portable_mode: bool = False):
        """
        Initialize path manager.

        Args:
            portable_mode: If True, store all data alongside the executable.
        """
        self._portable_mode = portable_mode

    @property
    def app_dir(self) -> Path:
        """Get the application installation directory."""
        if getattr(sys, "frozen", False):
            # Running as compiled executable
            return Path(sys.executable).parent
        else:
            # Running from source
            return Path(__file__).parent

    @property
    def data_dir(self) -> Path:
        """Get the user data directory."""
        if self._portable_mode:
            path = self.app_dir / "data"
        else:
            # Use APPDATA on Windows, ~/.config on Linux/Mac
            if sys.platform == "win32":
                base = Path(os.environ.get("APPDATA", Path.home()))
            else:
                base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
            path = base / APP_NAME

        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def config_file(self) -> Path:
        """Get the configuration file path."""
        return self.data_dir / DEFAULT_CONFIG_FILENAME

    @property
    def clocks_dir(self) -> Path:
        """Get the clock packs directory."""
        # First check for bundled clocks in app dir
        bundled = self.app_dir / DEFAULT_CLOCKS_DIRNAME
        if bundled.exists():
            return bundled

        # Fall back to user data directory
        user_clocks = self.data_dir / DEFAULT_CLOCKS_DIRNAME
        user_clocks.mkdir(parents=True, exist_ok=True)
        return user_clocks

    @property
    def user_clocks_dir(self) -> Path:
        """Get the user's custom clock packs directory (always writable)."""
        path = self.data_dir / DEFAULT_CLOCKS_DIRNAME
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        """Get the logs directory."""
        path = self.data_dir / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path
