"""
Integration tests for soundpack system with real audio files.

Tests that the generated soundpacks can be discovered and loaded correctly.
"""

import pytest
from pathlib import Path
from accessibletalkingclock.soundpack import Soundpack, SoundpackManager


class TestRealSoundpacks:
    """Test integration with actual generated soundpack files."""
    
    @pytest.fixture
    def sounds_dir(self):
        """Get path to real sounds directory."""
        # Path from test file to sounds directory
        test_dir = Path(__file__).parent
        sounds_dir = test_dir.parent / "src" / "accessibletalkingclock" / "resources" / "sounds"
        return sounds_dir
    
    def test_classic_soundpack_loads(self, sounds_dir):
        """Classic soundpack loads successfully with all required files."""
        soundpack = Soundpack("classic", sounds_dir)
        
        result = soundpack.load()
        
        assert result is True
        assert soundpack.is_loaded
        assert "hour" in soundpack.available_chimes
        assert "half" in soundpack.available_chimes
        assert "quarter" in soundpack.available_chimes
    
    def test_nature_soundpack_loads(self, sounds_dir):
        """Nature soundpack loads successfully with all required files."""
        soundpack = Soundpack("nature", sounds_dir)
        
        result = soundpack.load()
        
        assert result is True
        assert soundpack.is_loaded
        assert len(soundpack.available_chimes) == 3
    
    def test_digital_soundpack_loads(self, sounds_dir):
        """Digital soundpack loads successfully with all required files."""
        soundpack = Soundpack("digital", sounds_dir)
        
        result = soundpack.load()
        
        assert result is True
        assert soundpack.is_loaded
        assert len(soundpack.available_chimes) == 3
    
    def test_all_sound_files_exist(self, sounds_dir):
        """All required sound files exist and are accessible."""
        required_files = [
            "classic/hour.wav",
            "classic/half.wav",
            "classic/quarter.wav",
            "nature/hour.wav",
            "nature/half.wav",
            "nature/quarter.wav",
            "digital/hour.wav",
            "digital/half.wav",
            "digital/quarter.wav",
        ]
        
        for file_path in required_files:
            full_path = sounds_dir / file_path
            assert full_path.exists(), f"Missing sound file: {file_path}"
            assert full_path.stat().st_size > 0, f"Empty sound file: {file_path}"


class TestSoundpackManagerIntegration:
    """Test SoundpackManager with real soundpacks."""
    
    @pytest.fixture
    def sounds_dir(self):
        """Get path to real sounds directory."""
        test_dir = Path(__file__).parent
        sounds_dir = test_dir.parent / "src" / "accessibletalkingclock" / "resources" / "sounds"
        return sounds_dir
    
    @pytest.fixture
    def manager(self, sounds_dir):
        """Create SoundpackManager with real sounds directory."""
        return SoundpackManager(sounds_dir)
    
    def test_discovers_all_soundpacks(self, manager):
        """SoundpackManager discovers all three soundpacks."""
        soundpacks = manager.discover_soundpacks()
        
        assert "classic" in soundpacks
        assert "nature" in soundpacks
        assert "digital" in soundpacks
        assert len(soundpacks) >= 3
    
    def test_loads_classic_soundpack(self, manager):
        """SoundpackManager can load classic soundpack."""
        result = manager.load_soundpack("classic")
        
        assert result is True
        assert manager.current_soundpack is not None
        assert manager.current_soundpack.name == "classic"
        assert manager.current_soundpack.is_loaded
    
    def test_loads_nature_soundpack(self, manager):
        """SoundpackManager can load nature soundpack."""
        result = manager.load_soundpack("nature")
        
        assert result is True
        assert manager.current_soundpack.name == "nature"
    
    def test_loads_digital_soundpack(self, manager):
        """SoundpackManager can load digital soundpack."""
        result = manager.load_soundpack("digital")
        
        assert result is True
        assert manager.current_soundpack.name == "digital"
    
    def test_switches_between_soundpacks(self, manager):
        """Can switch between different soundpacks."""
        # Load classic
        manager.load_soundpack("classic")
        assert manager.current_soundpack.name == "classic"
        
        # Switch to digital
        manager.load_soundpack("digital")
        assert manager.current_soundpack.name == "digital"
        
        # Switch to nature
        manager.load_soundpack("nature")
        assert manager.current_soundpack.name == "nature"
    
    def test_retrieves_sound_paths(self, manager):
        """Can retrieve sound file paths from loaded soundpack."""
        manager.load_soundpack("classic")
        soundpack = manager.current_soundpack
        
        hour_path = soundpack.get_sound_path("hour")
        half_path = soundpack.get_sound_path("half")
        quarter_path = soundpack.get_sound_path("quarter")
        
        assert hour_path.exists()
        assert half_path.exists()
        assert quarter_path.exists()
        assert hour_path.name == "hour.wav"
        assert half_path.name == "half.wav"
        assert quarter_path.name == "quarter.wav"
