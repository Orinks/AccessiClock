"""
Soundpack system for AccessiClock.
Manages customizable sound collections for clock chimes.
"""
import os
from pathlib import Path


class SoundPack:
    """Represents a soundpack with audio files for clock chimes."""

    def __init__(self, name, path):
        """
        Initialize a SoundPack.
        
        Args:
            name: Name of the soundpack
            path: Path to the soundpack directory
        """
        self.name = name
        self.path = path
        self.sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        """Load sound file paths from the soundpack directory."""
        if os.path.exists(self.path):
            for file in os.listdir(self.path):
                if file.endswith(('.wav', '.mp3', '.ogg')):
                    sound_name = os.path.splitext(file)[0]
                    self.sounds[sound_name] = os.path.join(self.path, file)

    def get_sound(self, name):
        """
        Get the path to a specific sound file.
        
        Args:
            name: Name of the sound (without extension)
            
        Returns:
            str: Path to the sound file, or None if not found
        """
        return self.sounds.get(name)

    def get_all_sounds(self):
        """
        Get all available sounds in this pack.
        
        Returns:
            dict: Dictionary of sound names to file paths
        """
        return self.sounds.copy()


class SoundPackManager:
    """Manages multiple soundpacks for the application."""

    def __init__(self, soundpacks_dir=None):
        """
        Initialize the SoundPackManager.
        
        Args:
            soundpacks_dir: Directory containing soundpacks. If None, uses default.
        """
        if soundpacks_dir is None:
            # Try to find soundpacks directory relative to this file
            current_dir = Path(__file__).parent.parent.parent
            soundpacks_dir = current_dir / "soundpacks"
        
        self.soundpacks_dir = Path(soundpacks_dir)
        self.soundpacks = {}
        self._load_packs()

    def _load_packs(self):
        """Load all available soundpacks from the soundpacks directory."""
        if not self.soundpacks_dir.exists():
            print(f"Warning: Soundpacks directory not found: {self.soundpacks_dir}")
            # Create a default empty soundpack
            self.soundpacks["default"] = SoundPack("default", str(self.soundpacks_dir / "default"))
            return

        for pack_dir in self.soundpacks_dir.iterdir():
            if pack_dir.is_dir():
                pack_name = pack_dir.name
                self.soundpacks[pack_name] = SoundPack(pack_name, str(pack_dir))

        # Ensure we have at least a default pack
        if "default" not in self.soundpacks:
            default_path = self.soundpacks_dir / "default"
            default_path.mkdir(exist_ok=True)
            self.soundpacks["default"] = SoundPack("default", str(default_path))

    def get_pack(self, name):
        """
        Get a soundpack by name.
        
        Args:
            name: Name of the soundpack
            
        Returns:
            SoundPack: The requested soundpack, or None if not found
        """
        return self.soundpacks.get(name)

    def get_available_packs(self):
        """
        Get list of available soundpack names.
        
        Returns:
            list: List of soundpack names
        """
        return list(self.soundpacks.keys())

    def get_default_pack(self):
        """
        Get the default soundpack.
        
        Returns:
            SoundPack: The default soundpack
        """
        return self.soundpacks.get("default")
