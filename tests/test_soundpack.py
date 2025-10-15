"""
Tests for soundpack system.
"""
import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from accessiclock.soundpack import SoundPack, SoundPackManager


class TestSoundPack(unittest.TestCase):
    """Test cases for SoundPack class."""

    def test_soundpack_creation(self):
        """Test that a SoundPack can be created."""
        pack = SoundPack("test_pack", "/fake/path")
        self.assertEqual(pack.name, "test_pack")
        self.assertEqual(pack.path, "/fake/path")


class TestSoundPackManager(unittest.TestCase):
    """Test cases for SoundPackManager class."""

    def test_soundpack_manager(self):
        """Test that SoundPackManager can be created."""
        manager = SoundPackManager()
        self.assertIsNotNone(manager)

    def test_soundpack_manager_loads_packs(self):
        """Test that SoundPackManager can load soundpacks."""
        manager = SoundPackManager()
        # Should at least have a default soundpack
        packs = manager.get_available_packs()
        self.assertIsInstance(packs, list)


if __name__ == '__main__':
    unittest.main()
