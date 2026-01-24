"""Clock pack discovery, loading, and validation."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from ..constants import CLOCK_MANIFEST_FILENAME, SUPPORTED_AUDIO_FORMATS

logger = logging.getLogger(__name__)


class ClockPackError(Exception):
    """Exception raised for clock pack errors."""
    pass


@dataclass
class ClockPackInfo:
    """Information about a clock pack."""
    
    pack_id: str
    name: str
    author: str
    description: str
    version: str
    path: Path
    sounds: dict[str, str] = field(default_factory=dict)

    def get_sound_path(self, sound_name: str) -> Path | None:
        """
        Get the full path to a sound file.
        
        Args:
            sound_name: Name of the sound (e.g., "hour", "half_hour").
            
        Returns:
            Full path to the sound file, or None if not found.
        """
        filename = self.sounds.get(sound_name)
        if filename is None:
            return None
        return self.path / filename


class ClockPackLoader:
    """
    Discovers, loads, and validates clock packs.
    
    Clock packs are directories containing:
    - clock.json: Manifest with metadata and sound mappings
    - *.wav/*.mp3: Audio files for chimes
    """

    REQUIRED_FIELDS = ["name", "version"]

    def __init__(self, clocks_dir: Path):
        """
        Initialize the clock pack loader.
        
        Args:
            clocks_dir: Directory containing clock pack subdirectories.
        """
        self.clocks_dir = clocks_dir
        self._cache: dict[str, ClockPackInfo] = {}

    def discover_packs(self) -> dict[str, ClockPackInfo]:
        """
        Discover all valid clock packs in the clocks directory.
        
        Returns:
            Dictionary mapping pack_id to ClockPackInfo.
        """
        packs: dict[str, ClockPackInfo] = {}
        
        if not self.clocks_dir.exists():
            logger.warning(f"Clocks directory does not exist: {self.clocks_dir}")
            return packs
        
        for item in self.clocks_dir.iterdir():
            if not item.is_dir():
                continue
            
            manifest_path = item / CLOCK_MANIFEST_FILENAME
            if not manifest_path.exists():
                logger.debug(f"Skipping {item.name}: no {CLOCK_MANIFEST_FILENAME}")
                continue
            
            try:
                pack_info = self.load_pack(item.name)
                packs[item.name] = pack_info
                logger.info(f"Discovered clock pack: {pack_info.name} ({item.name})")
            except ClockPackError as e:
                logger.warning(f"Invalid clock pack {item.name}: {e}")
            except Exception as e:
                logger.error(f"Error loading clock pack {item.name}: {e}")
        
        self._cache = packs
        return packs

    def load_pack(self, pack_id: str) -> ClockPackInfo:
        """
        Load a specific clock pack by ID.
        
        Args:
            pack_id: The directory name of the clock pack.
            
        Returns:
            ClockPackInfo with the pack's metadata.
            
        Raises:
            ClockPackError: If the pack is invalid or cannot be loaded.
        """
        pack_dir = self.clocks_dir / pack_id
        manifest_path = pack_dir / CLOCK_MANIFEST_FILENAME
        
        if not manifest_path.exists():
            raise ClockPackError(f"Manifest not found: {manifest_path}")
        
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            raise ClockPackError(f"Invalid JSON in manifest: {e}") from e
        
        # Validate required fields
        for field_name in self.REQUIRED_FIELDS:
            if field_name not in manifest:
                raise ClockPackError(f"Missing required field: {field_name}")
        
        return ClockPackInfo(
            pack_id=pack_id,
            name=manifest["name"],
            author=manifest.get("author", "Unknown"),
            description=manifest.get("description", ""),
            version=manifest["version"],
            path=pack_dir,
            sounds=manifest.get("sounds", {}),
        )

    def validate_pack(self, pack_info: ClockPackInfo) -> tuple[bool, list[str]]:
        """
        Validate a clock pack's sound files.
        
        Args:
            pack_info: The clock pack to validate.
            
        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors: list[str] = []
        
        for _sound_name, filename in pack_info.sounds.items():
            sound_path = pack_info.path / filename
            
            if not sound_path.exists():
                errors.append(f"Sound file not found: {filename}")
                continue
            
            # Check file extension
            if sound_path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
                errors.append(
                    f"Unsupported audio format for {filename}: {sound_path.suffix}"
                )
        
        return (len(errors) == 0, errors)

    def get_pack(self, pack_id: str) -> ClockPackInfo | None:
        """
        Get a cached clock pack by ID.
        
        Args:
            pack_id: The pack ID to retrieve.
            
        Returns:
            ClockPackInfo if found, None otherwise.
        """
        return self._cache.get(pack_id)

    def refresh(self) -> dict[str, ClockPackInfo]:
        """
        Refresh the pack cache by re-discovering all packs.
        
        Returns:
            Updated dictionary of discovered packs.
        """
        self._cache.clear()
        return self.discover_packs()
