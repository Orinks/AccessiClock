"""Tests for clock pack loading and validation.

TDD: These tests are written before the implementation.
"""

import json
import tempfile
from pathlib import Path

import pytest


class TestClockPackLoader:
    """Test clock pack discovery and loading."""

    def test_discover_packs_in_directory(self):
        """Should find all clock packs in a directory."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            clocks_dir = Path(tmpdir)
            
            # Create two clock packs
            (clocks_dir / "pack1").mkdir()
            (clocks_dir / "pack1" / "clock.json").write_text(
                json.dumps({"name": "Pack 1", "version": "1.0.0", "author": "Test", "sounds": {}})
            )
            
            (clocks_dir / "pack2").mkdir()
            (clocks_dir / "pack2" / "clock.json").write_text(
                json.dumps({"name": "Pack 2", "version": "1.0.0", "author": "Test", "sounds": {}})
            )
            
            loader = ClockPackLoader(clocks_dir)
            packs = loader.discover_packs()
            
            assert len(packs) == 2
            assert "pack1" in packs
            assert "pack2" in packs

    def test_ignore_directories_without_manifest(self):
        """Should ignore directories without clock.json."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            clocks_dir = Path(tmpdir)
            
            # Valid pack
            (clocks_dir / "valid").mkdir()
            (clocks_dir / "valid" / "clock.json").write_text(
                json.dumps({"name": "Valid", "version": "1.0.0", "author": "Test", "sounds": {}})
            )
            
            # Invalid - no manifest
            (clocks_dir / "invalid").mkdir()
            (clocks_dir / "invalid" / "some_file.txt").write_text("not a clock pack")
            
            loader = ClockPackLoader(clocks_dir)
            packs = loader.discover_packs()
            
            assert len(packs) == 1
            assert "valid" in packs
            assert "invalid" not in packs


class TestClockPackManifest:
    """Test clock pack manifest parsing."""

    def test_load_manifest(self):
        """Should load and parse clock.json manifest."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir)
            manifest = {
                "name": "Westminster",
                "author": "AccessiClock Team",
                "description": "Classic Westminster chimes",
                "version": "1.0.0",
                "sounds": {
                    "hour": "hour.wav",
                    "half_hour": "half_hour.wav",
                }
            }
            (pack_dir / "clock.json").write_text(json.dumps(manifest))
            
            loader = ClockPackLoader(pack_dir.parent)
            pack_info = loader.load_pack(pack_dir.name)
            
            assert pack_info.name == "Westminster"
            assert pack_info.author == "AccessiClock Team"
            assert pack_info.version == "1.0.0"
            assert "hour" in pack_info.sounds

    def test_manifest_missing_required_fields(self):
        """Should raise error for manifest missing required fields."""
        from accessiclock.services.clock_pack_loader import ClockPackError, ClockPackLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "incomplete"
            pack_dir.mkdir()
            
            # Missing 'name' field
            manifest = {"version": "1.0.0", "sounds": {}}
            (pack_dir / "clock.json").write_text(json.dumps(manifest))
            
            loader = ClockPackLoader(Path(tmpdir))
            
            with pytest.raises(ClockPackError):
                loader.load_pack("incomplete")


class TestClockPackValidation:
    """Test clock pack validation."""

    def test_validate_sounds_exist(self):
        """Should validate that referenced sound files exist."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "test_pack"
            pack_dir.mkdir()
            
            manifest = {
                "name": "Test",
                "version": "1.0.0",
                "author": "Test",
                "sounds": {
                    "hour": "hour.wav",
                    "preview": "preview.wav",
                }
            }
            (pack_dir / "clock.json").write_text(json.dumps(manifest))
            
            # Create the sound files
            (pack_dir / "hour.wav").touch()
            (pack_dir / "preview.wav").touch()
            
            loader = ClockPackLoader(Path(tmpdir))
            pack_info = loader.load_pack("test_pack")
            
            is_valid, errors = loader.validate_pack(pack_info)
            assert is_valid is True
            assert len(errors) == 0

    def test_validation_fails_for_missing_sounds(self):
        """Should fail validation when sound files are missing."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "test_pack"
            pack_dir.mkdir()
            
            manifest = {
                "name": "Test",
                "version": "1.0.0",
                "author": "Test",
                "sounds": {
                    "hour": "hour.wav",  # File doesn't exist
                }
            }
            (pack_dir / "clock.json").write_text(json.dumps(manifest))
            
            loader = ClockPackLoader(Path(tmpdir))
            pack_info = loader.load_pack("test_pack")
            
            is_valid, errors = loader.validate_pack(pack_info)
            assert is_valid is False
            assert any("hour.wav" in str(e) for e in errors)


class TestClockPackInfo:
    """Test ClockPackInfo data class."""

    def test_pack_info_properties(self):
        """ClockPackInfo should have expected properties."""
        from accessiclock.services.clock_pack_loader import ClockPackInfo
        
        info = ClockPackInfo(
            pack_id="westminster",
            name="Westminster",
            author="Test",
            description="Classic chimes",
            version="1.0.0",
            path=Path("/clocks/westminster"),
            sounds={"hour": "hour.wav"},
        )
        
        assert info.pack_id == "westminster"
        assert info.name == "Westminster"
        assert info.author == "Test"
        assert info.version == "1.0.0"

    def test_get_sound_path(self):
        """Should return full path to sound file."""
        from accessiclock.services.clock_pack_loader import ClockPackInfo
        
        info = ClockPackInfo(
            pack_id="test",
            name="Test",
            author="Test",
            description="",
            version="1.0.0",
            path=Path("/clocks/test"),
            sounds={"hour": "hour.wav"},
        )
        
        sound_path = info.get_sound_path("hour")
        assert sound_path == Path("/clocks/test/hour.wav")

    def test_get_sound_path_missing(self):
        """Should return None for missing sound."""
        from accessiclock.services.clock_pack_loader import ClockPackInfo
        
        info = ClockPackInfo(
            pack_id="test",
            name="Test",
            author="Test",
            description="",
            version="1.0.0",
            path=Path("/clocks/test"),
            sounds={},
        )
        
        assert info.get_sound_path("nonexistent") is None
