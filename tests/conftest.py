"""Pytest configuration and fixtures for AccessiClock tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from accessiclock.paths import Paths


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_paths(temp_dir):
    """Create a Paths instance pointing to temp directory."""
    with patch("accessiclock.paths.Paths.data_dir", new_callable=lambda: property(lambda self: temp_dir)):
        from accessiclock.paths import Paths
        paths = Paths(portable_mode=True)
        # Override data_dir to use temp
        paths._test_data_dir = temp_dir
        yield paths


@pytest.fixture
def sample_clock_pack(temp_dir) -> Path:
    """Create a sample clock pack for testing."""
    clock_dir = temp_dir / "clocks" / "test_clock"
    clock_dir.mkdir(parents=True)
    
    manifest = {
        "name": "Test Clock",
        "author": "Test Author",
        "description": "A test clock pack",
        "version": "1.0.0",
        "sounds": {
            "hour": "hour.wav",
            "half_hour": "half_hour.wav",
            "preview": "preview.wav",
        }
    }
    
    with open(clock_dir / "clock.json", "w") as f:
        json.dump(manifest, f)
    
    # Create dummy audio files
    for sound_file in manifest["sounds"].values():
        (clock_dir / sound_file).touch()
    
    return clock_dir


@pytest.fixture
def mock_wx():
    """Mock wx module for headless testing."""
    mock = MagicMock()
    mock.App = MagicMock
    mock.Frame = MagicMock
    mock.Panel = MagicMock
    mock.BoxSizer = MagicMock
    mock.Timer = MagicMock
    mock.VERTICAL = 0
    mock.HORIZONTAL = 1
    mock.DEFAULT_FRAME_STYLE = 0
    mock.TE_READONLY = 0
    mock.TE_CENTER = 0
    mock.CB_READONLY = 0
    mock.EVT_TIMER = MagicMock()
    mock.EVT_BUTTON = MagicMock()
    mock.EVT_COMBOBOX = MagicMock()
    mock.EVT_CHECKBOX = MagicMock()
    mock.EVT_CLOSE = MagicMock()
    mock.EVT_MENU = MagicMock()
    mock.ID_ANY = -1
    mock.ID_EXIT = 0
    mock.ID_ABOUT = 0
    mock.ID_PREFERENCES = 0
    return mock


@pytest.fixture
def config_file(temp_dir) -> Path:
    """Create a test config file."""
    config_path = temp_dir / "config.json"
    config = {
        "volume": 75,
        "clock": "westminster",
        "chime_hourly": True,
        "chime_half_hour": True,
        "chime_quarter_hour": False,
    }
    with open(config_path, "w") as f:
        json.dump(config, f)
    return config_path
