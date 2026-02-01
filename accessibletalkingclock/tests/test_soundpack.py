"""
Tests for the Soundpack class.

Following TDD/BDD approach - tests define expected behavior.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from accessibletalkingclock.soundpack import Soundpack


class TestSoundpackInitialization:
    """Test Soundpack object initialization."""
    
    def test_soundpack_creation(self):
        """Soundpack can be created with name and base path."""
        base_path = Path(tempfile.gettempdir()) / "test_sounds"
        soundpack = Soundpack("classic", base_path)
        
        assert soundpack.name == "classic"
        assert soundpack.base_path == base_path
    
    def test_soundpack_not_loaded_initially(self):
        """New soundpack is not loaded until load() is called."""
        base_path = Path(tempfile.gettempdir()) / "test_sounds"
        soundpack = Soundpack("classic", base_path)
        
        assert not soundpack.is_loaded


class TestSoundpackLoading:
    """Test soundpack loading behavior."""
    
    @pytest.fixture
    def temp_soundpack_dir(self):
        """Create temporary soundpack directory with test files."""
        temp_dir = Path(tempfile.gettempdir()) / "test_soundpack"
        soundpack_dir = temp_dir / "classic"
        soundpack_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy audio files
        (soundpack_dir / "hour.wav").write_text("dummy audio data")
        (soundpack_dir / "half.wav").write_text("dummy audio data")
        (soundpack_dir / "quarter.wav").write_text("dummy audio data")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_load_complete_soundpack(self, temp_soundpack_dir):
        """When soundpack has all required files, load() returns True."""
        soundpack = Soundpack("classic", temp_soundpack_dir)
        
        result = soundpack.load()
        
        assert result is True
        assert soundpack.is_loaded
    
    def test_load_missing_soundpack_directory(self):
        """When soundpack directory doesn't exist, load() returns False."""
        base_path = Path(tempfile.gettempdir()) / "nonexistent"
        soundpack = Soundpack("classic", base_path)
        
        result = soundpack.load()
        
        assert result is False
        assert not soundpack.is_loaded
    
    def test_load_incomplete_soundpack(self):
        """When soundpack is missing required files, load() returns False."""
        temp_dir = Path(tempfile.gettempdir()) / "test_incomplete"
        soundpack_dir = temp_dir / "classic"
        soundpack_dir.mkdir(parents=True, exist_ok=True)
        
        # Only create hour file, missing half and quarter
        (soundpack_dir / "hour.wav").write_text("dummy audio data")
        
        soundpack = Soundpack("classic", temp_dir)
        result = soundpack.load()
        
        assert result is False
        assert not soundpack.is_loaded
        
        # Cleanup
        shutil.rmtree(temp_dir)


class TestSoundpackSoundAccess:
    """Test accessing sound file paths from soundpack."""
    
    @pytest.fixture
    def loaded_soundpack(self):
        """Create and load a complete soundpack."""
        temp_dir = Path(tempfile.gettempdir()) / "test_access"
        soundpack_dir = temp_dir / "classic"
        soundpack_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy audio files
        (soundpack_dir / "hour.wav").write_text("dummy audio data")
        (soundpack_dir / "half.wav").write_text("dummy audio data")
        (soundpack_dir / "quarter.wav").write_text("dummy audio data")
        
        soundpack = Soundpack("classic", temp_dir)
        soundpack.load()
        
        yield soundpack
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_get_hour_sound_path(self, loaded_soundpack):
        """get_sound_path('hour') returns path to hour.wav."""
        path = loaded_soundpack.get_sound_path("hour")
        
        assert path.name == "hour.wav"
        assert path.exists()
    
    def test_get_half_sound_path(self, loaded_soundpack):
        """get_sound_path('half') returns path to half.wav."""
        path = loaded_soundpack.get_sound_path("half")
        
        assert path.name == "half.wav"
        assert path.exists()
    
    def test_get_quarter_sound_path(self, loaded_soundpack):
        """get_sound_path('quarter') returns path to quarter.wav."""
        path = loaded_soundpack.get_sound_path("quarter")
        
        assert path.name == "quarter.wav"
        assert path.exists()
    
    def test_get_invalid_chime_type(self, loaded_soundpack):
        """get_sound_path() raises ValueError for invalid chime type."""
        with pytest.raises(ValueError, match="Invalid chime type"):
            loaded_soundpack.get_sound_path("invalid")
    
    def test_get_sound_path_before_loading(self):
        """get_sound_path() raises RuntimeError if soundpack not loaded."""
        base_path = Path(tempfile.gettempdir()) / "test_sounds"
        soundpack = Soundpack("classic", base_path)
        
        with pytest.raises(RuntimeError, match="not loaded"):
            soundpack.get_sound_path("hour")


class TestSoundpackAvailableChimes:
    """Test querying available chimes in soundpack."""
    
    def test_available_chimes_when_loaded(self):
        """available_chimes property returns list of chime types when loaded."""
        temp_dir = Path(tempfile.gettempdir()) / "test_chimes"
        soundpack_dir = temp_dir / "classic"
        soundpack_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy audio files
        (soundpack_dir / "hour.wav").write_text("dummy audio data")
        (soundpack_dir / "half.wav").write_text("dummy audio data")
        (soundpack_dir / "quarter.wav").write_text("dummy audio data")
        
        soundpack = Soundpack("classic", temp_dir)
        soundpack.load()
        
        available = soundpack.available_chimes
        
        assert "hour" in available
        assert "half" in available
        assert "quarter" in available
        assert len(available) == 3
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_available_chimes_when_not_loaded(self):
        """available_chimes returns empty list when not loaded."""
        base_path = Path(tempfile.gettempdir()) / "test_sounds"
        soundpack = Soundpack("classic", base_path)
        
        assert soundpack.available_chimes == []


class TestSoundpackStringRepresentation:
    """Test string representation of soundpack."""
    
    def test_str_representation(self):
        """str(soundpack) returns descriptive string with name and status."""
        base_path = Path(tempfile.gettempdir()) / "test_sounds"
        soundpack = Soundpack("classic", base_path)
        
        result = str(soundpack)
        
        assert "classic" in result
        assert "not loaded" in result or "loaded" in result
