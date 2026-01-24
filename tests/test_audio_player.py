"""Tests for accessiclock.audio.player module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestAudioPlayerInit:
    """Test AudioPlayer initialization."""

    def test_init_default_volume(self):
        """AudioPlayer should initialize with default 50% volume."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            assert player.get_volume() == 50

    def test_init_custom_volume(self):
        """AudioPlayer should accept custom initial volume."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer(volume_percent=75)
            assert player.get_volume() == 75

    def test_init_volume_clamped_high(self):
        """Volume above 100 should be clamped to 100."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer(volume_percent=150)
            assert player.get_volume() == 100

    def test_init_volume_clamped_low(self):
        """Volume below 0 should be clamped to 0."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer(volume_percent=-50)
            assert player.get_volume() == 0


class TestVolumeControl:
    """Test volume control methods."""

    @pytest.fixture
    def player(self):
        """Create an AudioPlayer with mocked backend."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            return AudioPlayer(volume_percent=50)

    def test_set_volume(self, player):
        """set_volume should update volume level."""
        player.set_volume(75)
        assert player.get_volume() == 75

    def test_set_volume_clamped_high(self, player):
        """set_volume should clamp values above 100."""
        player.set_volume(200)
        assert player.get_volume() == 100

    def test_set_volume_clamped_low(self, player):
        """set_volume should clamp values below 0."""
        player.set_volume(-10)
        assert player.get_volume() == 0

    def test_volume_decimal_conversion(self, player):
        """Volume should convert correctly to decimal."""
        assert player._convert_volume_to_decimal(0) == 0.0
        assert player._convert_volume_to_decimal(50) == 0.5
        assert player._convert_volume_to_decimal(100) == 1.0


class TestPlaySound:
    """Test sound playback methods."""

    def test_play_nonexistent_file_raises(self):
        """Playing a nonexistent file should raise FileNotFoundError."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            with pytest.raises(FileNotFoundError):
                player.play_sound("/nonexistent/path/to/audio.wav")

    def test_play_sound_with_fallback(self):
        """play_sound should use fallback when sound_lib unavailable."""
        # Skip if neither playsound3 nor sound_lib available
        try:
            from playsound3 import playsound
            playsound_available = True
        except ImportError:
            playsound_available = False
        
        if not playsound_available:
            pytest.skip("playsound3 not available")
        
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
            
            try:
                # Mock playsound in the module where it's used
                import accessiclock.audio.player as player_module
                with patch.object(player_module, "playsound", create=True) as mock_playsound:
                    player.play_sound(temp_path)
            finally:
                Path(temp_path).unlink(missing_ok=True)


class TestIsPlaying:
    """Test is_playing method."""

    def test_is_playing_initially_false(self):
        """is_playing should return False when nothing is playing."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            assert player.is_playing() is False


class TestCleanup:
    """Test cleanup method."""

    def test_cleanup_no_error_when_nothing_playing(self):
        """cleanup should not raise when nothing is playing."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer
            
            player = AudioPlayer()
            # Should not raise
            player.cleanup()

    def test_cleanup_stops_playback(self):
        """cleanup should stop any current playback."""
        from accessiclock.audio.player import AudioPlayer
        
        # Create player instance directly with mocked stream
        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        mock_current = MagicMock()
        player._current_stream = mock_current
        
        # Mock cleanup to avoid BASS_Free issues
        import accessiclock.audio.player as player_module
        original_use_sound_lib = player_module._use_sound_lib
        original_bass_init = player_module._bass_initialized
        
        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = False  # Skip BASS_Free
            
            player.cleanup()
            
            mock_current.stop.assert_called_once()
            mock_current.free.assert_called_once()
        finally:
            player_module._use_sound_lib = original_use_sound_lib
            player_module._bass_initialized = original_bass_init


class TestSoundLibIntegration:
    """Test sound_lib integration (cross-platform)."""

    def test_sound_lib_play_creates_stream(self):
        """Playing with sound_lib should create a FileStream."""
        from accessiclock.audio.player import AudioPlayer
        import accessiclock.audio.player as player_module
        
        # Create a mock stream module
        mock_stream_module = MagicMock()
        mock_file_stream = MagicMock()
        mock_stream_module.FileStream.return_value = mock_file_stream
        
        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None
        
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        try:
            # Patch stream in the module
            with patch.object(player_module, "stream", mock_stream_module, create=True):
                player._play_with_sound_lib(Path(temp_path))
            
            # Verify FileStream was created with correct path
            mock_stream_module.FileStream.assert_called_once()
            call_kwargs = mock_stream_module.FileStream.call_args
            assert temp_path in str(call_kwargs)
            
            # Verify play was called
            mock_file_stream.play.assert_called_once()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_sound_lib_sets_volume_on_stream(self):
        """Playing should set volume on the stream."""
        from accessiclock.audio.player import AudioPlayer
        import accessiclock.audio.player as player_module
        
        mock_stream_module = MagicMock()
        mock_file_stream = MagicMock()
        mock_stream_module.FileStream.return_value = mock_file_stream
        
        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 75  # 75%
        player._current_stream = None
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        try:
            with patch.object(player_module, "stream", mock_stream_module, create=True):
                player._play_with_sound_lib(Path(temp_path))
            
            # Verify volume was set to 0.75
            assert mock_file_stream.volume == 0.75
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_sound_lib_stops_previous_stream(self):
        """Playing a new sound should stop the previous stream."""
        from accessiclock.audio.player import AudioPlayer
        import accessiclock.audio.player as player_module
        
        mock_stream_module = MagicMock()
        mock_old_stream = MagicMock()
        mock_new_stream = MagicMock()
        mock_stream_module.FileStream.return_value = mock_new_stream
        
        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = mock_old_stream
        
        # Mock stop method
        player.stop = MagicMock()
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        try:
            with patch.object(player_module, "stream", mock_stream_module, create=True):
                player._play_with_sound_lib(Path(temp_path))
            
            # stop() should have been called (which stops/frees old stream)
            player.stop.assert_called_once()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_sound_lib_is_playing_checks_stream(self):
        """is_playing should check the stream's is_playing property."""
        from accessiclock.audio.player import AudioPlayer
        import accessiclock.audio.player as player_module
        
        original_use_sound_lib = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True
            
            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            
            # No stream - not playing
            player._current_stream = None
            assert player.is_playing() is False
            
            # Stream playing
            mock_stream = MagicMock()
            mock_stream.is_playing = True
            player._current_stream = mock_stream
            assert player.is_playing() is True
            
            # Stream stopped
            mock_stream.is_playing = False
            assert player.is_playing() is False
        finally:
            player_module._use_sound_lib = original_use_sound_lib

    def test_sound_lib_stop_frees_stream(self):
        """stop should stop and free the current stream."""
        from accessiclock.audio.player import AudioPlayer
        import accessiclock.audio.player as player_module
        
        original_use_sound_lib = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True
            
            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            
            mock_stream = MagicMock()
            player._current_stream = mock_stream
            
            player.stop()
            
            mock_stream.stop.assert_called_once()
            mock_stream.free.assert_called_once()
            assert player._current_stream is None
        finally:
            player_module._use_sound_lib = original_use_sound_lib
