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


class TestClockPackLoaderEdgeCases:
    """Tests for clock_pack_loader edge cases and error paths (issue #12)."""

    def test_discover_packs_nonexistent_directory(self):
        """discover_packs should return empty dict when directory doesn't exist."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader

        loader = ClockPackLoader(Path("/tmp/nonexistent_clocks_dir_12345"))
        packs = loader.discover_packs()
        assert packs == {}

    def test_discover_packs_skips_files(self):
        """discover_packs should skip regular files (non-directories)."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            clocks_dir = Path(tmpdir)

            # Create a regular file at top level (not a directory)
            (clocks_dir / "not_a_pack.txt").write_text("just a file")

            # Create a valid pack too
            (clocks_dir / "valid_pack").mkdir()
            (clocks_dir / "valid_pack" / "clock.json").write_text(
                json.dumps({"name": "Valid", "version": "1.0.0"})
            )

            loader = ClockPackLoader(clocks_dir)
            packs = loader.discover_packs()

            assert len(packs) == 1
            assert "valid_pack" in packs

    def test_discover_packs_handles_clock_pack_error(self):
        """discover_packs should skip packs that raise ClockPackError."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            clocks_dir = Path(tmpdir)

            # Create a pack with invalid JSON manifest
            (clocks_dir / "bad_pack").mkdir()
            (clocks_dir / "bad_pack" / "clock.json").write_text("{invalid json!!")

            # Create a valid pack
            (clocks_dir / "good_pack").mkdir()
            (clocks_dir / "good_pack" / "clock.json").write_text(
                json.dumps({"name": "Good", "version": "1.0.0"})
            )

            loader = ClockPackLoader(clocks_dir)
            packs = loader.discover_packs()

            # Bad pack skipped, good pack loaded
            assert len(packs) == 1
            assert "good_pack" in packs
            assert "bad_pack" not in packs

    def test_discover_packs_handles_generic_exception(self):
        """discover_packs should skip packs that raise unexpected exceptions."""
        from unittest.mock import patch

        from accessiclock.services.clock_pack_loader import ClockPackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            clocks_dir = Path(tmpdir)

            # Create a pack with a valid manifest
            (clocks_dir / "error_pack").mkdir()
            (clocks_dir / "error_pack" / "clock.json").write_text(
                json.dumps({"name": "Error", "version": "1.0.0"})
            )

            loader = ClockPackLoader(clocks_dir)

            # Patch load_pack to raise a generic exception
            with patch.object(loader, "load_pack", side_effect=RuntimeError("disk error")):
                packs = loader.discover_packs()

            assert packs == {}

    def test_load_pack_invalid_json(self):
        """load_pack should raise ClockPackError for invalid JSON."""
        from accessiclock.services.clock_pack_loader import ClockPackError, ClockPackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "broken"
            pack_dir.mkdir()
            (pack_dir / "clock.json").write_text("not valid json {{{")

            loader = ClockPackLoader(Path(tmpdir))

            with pytest.raises(ClockPackError, match="Invalid JSON"):
                loader.load_pack("broken")

    def test_load_pack_missing_version_field(self):
        """load_pack should raise ClockPackError when 'version' is missing."""
        from accessiclock.services.clock_pack_loader import ClockPackError, ClockPackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "no_version"
            pack_dir.mkdir()
            (pack_dir / "clock.json").write_text(
                json.dumps({"name": "Test Pack", "author": "Test"})
            )

            loader = ClockPackLoader(Path(tmpdir))

            with pytest.raises(ClockPackError, match="Missing required field"):
                loader.load_pack("no_version")

    def test_validate_pack_unsupported_audio_format(self):
        """validate_pack should report unsupported audio formats."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "bad_format"
            pack_dir.mkdir()

            manifest = {
                "name": "Bad Format",
                "version": "1.0.0",
                "sounds": {"hour": "hour.xyz"},
            }
            (pack_dir / "clock.json").write_text(json.dumps(manifest))

            # Create the file with unsupported extension
            (pack_dir / "hour.xyz").touch()

            loader = ClockPackLoader(Path(tmpdir))
            pack_info = loader.load_pack("bad_format")

            is_valid, errors = loader.validate_pack(pack_info)
            assert is_valid is False
            assert any("Unsupported audio format" in e for e in errors)

    def test_get_pack_returns_none_for_missing(self):
        """get_pack should return None for an uncached pack ID."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = ClockPackLoader(Path(tmpdir))
            assert loader.get_pack("nonexistent") is None

    def test_refresh_clears_and_rediscovers(self):
        """refresh should clear the cache and re-discover packs."""
        from accessiclock.services.clock_pack_loader import ClockPackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            clocks_dir = Path(tmpdir)

            # Start with one pack
            (clocks_dir / "pack1").mkdir()
            (clocks_dir / "pack1" / "clock.json").write_text(
                json.dumps({"name": "Pack 1", "version": "1.0.0"})
            )

            loader = ClockPackLoader(clocks_dir)
            packs = loader.discover_packs()
            assert len(packs) == 1

            # Add another pack
            (clocks_dir / "pack2").mkdir()
            (clocks_dir / "pack2" / "clock.json").write_text(
                json.dumps({"name": "Pack 2", "version": "1.0.0"})
            )

            # Refresh should find both
            packs = loader.refresh()
            assert len(packs) == 2
            assert "pack1" in packs
            assert "pack2" in packs
