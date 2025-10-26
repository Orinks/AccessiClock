"""
Soundpack management for Accessible Talking Clock.

Handles loading and accessing soundpack audio files for different chime themes.
"""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class Soundpack:
    """Manages loading and accessing soundpack audio files."""
    
    # Required chime types for a complete soundpack
    REQUIRED_CHIMES = ["hour", "half", "quarter"]
    
    def __init__(self, name: str, base_path: Path):
        """
        Initialize soundpack with name and base directory.
        
        Args:
            name: Name of the soundpack (e.g., "classic", "nature", "digital")
            base_path: Base directory containing soundpack subdirectories
        """
        self.name = name
        self.base_path = Path(base_path)
        self._loaded = False
        self._sound_paths = {}
    
    def load(self) -> bool:
        """
        Load and validate all sound files.
        
        Returns:
            True if all required sounds are present and valid, False otherwise
        """
        logger.info(f"Loading soundpack: {self.name}")
        
        # Get soundpack directory
        soundpack_dir = self.base_path / self.name
        
        # Check if directory exists
        if not soundpack_dir.exists():
            logger.error(f"Soundpack directory not found: {soundpack_dir}")
            return False
        
        if not soundpack_dir.is_dir():
            logger.error(f"Soundpack path is not a directory: {soundpack_dir}")
            return False
        
        # Check for all required sound files
        missing_files = []
        for chime_type in self.REQUIRED_CHIMES:
            sound_file = soundpack_dir / f"{chime_type}.wav"
            if not sound_file.exists():
                missing_files.append(f"{chime_type}.wav")
            else:
                self._sound_paths[chime_type] = sound_file
        
        if missing_files:
            logger.error(f"Soundpack '{self.name}' missing required files: {missing_files}")
            self._sound_paths.clear()
            return False
        
        self._loaded = True
        logger.info(f"Soundpack '{self.name}' loaded successfully with {len(self._sound_paths)} sounds")
        return True
    
    def get_sound_path(self, chime_type: str) -> Path:
        """
        Get path to specific chime sound.
        
        Args:
            chime_type: Type of chime ("hour", "half", "quarter")
            
        Returns:
            Path to the sound file
            
        Raises:
            RuntimeError: If soundpack not loaded
            ValueError: If chime_type is invalid
        """
        if not self._loaded:
            raise RuntimeError(f"Soundpack '{self.name}' not loaded. Call load() first.")
        
        if chime_type not in self.REQUIRED_CHIMES:
            raise ValueError(f"Invalid chime type: {chime_type}. Must be one of {self.REQUIRED_CHIMES}")
        
        return self._sound_paths[chime_type]
    
    @property
    def is_loaded(self) -> bool:
        """Check if soundpack is fully loaded."""
        return self._loaded
    
    @property
    def available_chimes(self) -> List[str]:
        """Get list of available chime types."""
        if not self._loaded:
            return []
        return list(self._sound_paths.keys())
    
    def __str__(self) -> str:
        """String representation of soundpack."""
        status = "loaded" if self._loaded else "not loaded"
        return f"Soundpack('{self.name}', {status})"
    
    def __repr__(self) -> str:
        """Developer representation of soundpack."""
        return f"Soundpack(name='{self.name}', base_path='{self.base_path}', loaded={self._loaded})"


class SoundpackManager:
    """Manages collection of soundpacks and current selection."""
    
    def __init__(self, sounds_directory: Path):
        """
        Initialize manager with base sounds directory.
        
        Args:
            sounds_directory: Directory containing soundpack subdirectories
        """
        self.sounds_directory = Path(sounds_directory)
        self._soundpacks = {}
        self._current_soundpack = None
    
    def discover_soundpacks(self) -> List[str]:
        """
        Scan directory for available soundpacks.
        
        Returns:
            List of soundpack names (directory names in sounds_directory)
        """
        logger.info(f"Discovering soundpacks in: {self.sounds_directory}")
        
        if not self.sounds_directory.exists():
            logger.warning(f"Sounds directory not found: {self.sounds_directory}")
            return []
        
        soundpacks = []
        for item in self.sounds_directory.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                soundpacks.append(item.name)
        
        logger.info(f"Found {len(soundpacks)} soundpacks: {soundpacks}")
        return sorted(soundpacks)
    
    def load_soundpack(self, name: str) -> bool:
        """
        Load specific soundpack.
        
        Args:
            name: Name of soundpack to load
            
        Returns:
            True if successfully loaded, False otherwise
        """
        logger.info(f"Loading soundpack: {name}")
        
        # Create Soundpack object if not already cached
        if name not in self._soundpacks:
            soundpack = Soundpack(name, self.sounds_directory)
            if not soundpack.load():
                return False
            self._soundpacks[name] = soundpack
        
        # Set as current soundpack
        self._current_soundpack = self._soundpacks[name]
        logger.info(f"Current soundpack set to: {name}")
        return True
    
    def get_soundpack(self, name: str) -> Optional[Soundpack]:
        """
        Get loaded soundpack by name.
        
        Args:
            name: Name of soundpack
            
        Returns:
            Soundpack object if loaded, None otherwise
        """
        return self._soundpacks.get(name)
    
    @property
    def current_soundpack(self) -> Optional[Soundpack]:
        """Get currently selected soundpack."""
        return self._current_soundpack
    
    @property
    def available_soundpacks(self) -> List[str]:
        """Get list of discovered soundpack names."""
        return self.discover_soundpacks()
