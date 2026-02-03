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

    def test_init_with_sound_lib_initializes_bass(self):
        """When sound_lib is available and BASS not initialized, should init BASS."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        orig_init = player_module._bass_initialized
        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = False

            mock_output = MagicMock()
            mock_sound_lib = MagicMock()
            mock_sound_lib.output = mock_output
            with patch.dict(
                "sys.modules",
                {"sound_lib": mock_sound_lib, "sound_lib.output": mock_output},
            ):
                AudioPlayer(volume_percent=50)
                mock_output.Output.assert_called_once()
                assert player_module._bass_initialized is True
        finally:
            player_module._use_sound_lib = orig_use
            player_module._bass_initialized = orig_init

    def test_init_bass_already_initialized_skips(self):
        """When BASS already initialized, should not re-init."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        orig_init = player_module._bass_initialized
        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = True

            player = AudioPlayer(volume_percent=50)
            assert player.get_volume() == 50
        finally:
            player_module._use_sound_lib = orig_use
            player_module._bass_initialized = orig_init

    def test_init_bass_init_failure_raises(self):
        """When BASS init fails, should raise the exception."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        orig_init = player_module._bass_initialized
        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = False

            mock_output = MagicMock()
            mock_output.Output.side_effect = RuntimeError("BASS init failed")
            mock_sound_lib = MagicMock()
            mock_sound_lib.output = mock_output
            with (
                patch.dict(
                    "sys.modules",
                    {"sound_lib": mock_sound_lib, "sound_lib.output": mock_output},
                ),
                pytest.raises(RuntimeError, match="BASS init failed"),
            ):
                AudioPlayer(volume_percent=50)
        finally:
            player_module._use_sound_lib = orig_use
            player_module._bass_initialized = orig_init


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

    def test_set_volume_updates_active_stream(self):
        """set_volume should update stream volume when playing."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            mock_stream = MagicMock()
            mock_stream.is_playing = True
            player._current_stream = mock_stream

            player.set_volume(80)
            assert player.get_volume() == 80
            assert mock_stream.volume == 0.8
        finally:
            player_module._use_sound_lib = orig_use


class TestPlaySound:
    """Test sound playback methods."""

    def test_play_nonexistent_file_raises(self):
        """Playing a nonexistent file should raise FileNotFoundError."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer

            player = AudioPlayer()
            with pytest.raises(FileNotFoundError):
                player.play_sound("/nonexistent/path/to/audio.wav")

    def test_play_sound_dispatches_to_sound_lib(self):
        """play_sound should use sound_lib when available."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = None
            player._play_with_sound_lib = MagicMock()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            try:
                player.play_sound(temp_path)
                player._play_with_sound_lib.assert_called_once()
            finally:
                Path(temp_path).unlink(missing_ok=True)
        finally:
            player_module._use_sound_lib = orig_use

    def test_play_sound_dispatches_to_fallback(self):
        """play_sound should use fallback when sound_lib unavailable."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = False

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = None
            player._play_with_fallback = MagicMock()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            try:
                player.play_sound(temp_path)
                player._play_with_fallback.assert_called_once()
            finally:
                Path(temp_path).unlink(missing_ok=True)
        finally:
            player_module._use_sound_lib = orig_use

    def test_play_with_sound_lib_error_raises(self):
        """_play_with_sound_lib should re-raise on error."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        mock_stream_mod = MagicMock()
        mock_stream_mod.FileStream.side_effect = RuntimeError("stream error")

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        with (
            patch.object(player_module, "stream", mock_stream_mod, create=True),
            pytest.raises(RuntimeError, match="stream error"),
        ):
            player._play_with_sound_lib(Path("/tmp/test.wav"))

    def test_play_with_fallback_playsound3(self):
        """_play_with_fallback should launch a thread with playsound3."""
        from accessiclock.audio.player import AudioPlayer

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        mock_module = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            with (
                patch.dict("sys.modules", {"playsound3": mock_module}),
                patch("threading.Thread") as mock_thread_cls,
            ):
                mock_thread = MagicMock()
                mock_thread_cls.return_value = mock_thread
                player._play_with_fallback(Path(temp_path))
                mock_thread_cls.assert_called_once()
                mock_thread.start.assert_called_once()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_play_with_fallback_import_error(self):
        """_play_with_fallback should raise when playsound3 not installed."""
        from accessiclock.audio.player import AudioPlayer

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        with (
            patch.dict("sys.modules", {"playsound3": None}),
            pytest.raises(ImportError),
        ):
            player._play_with_fallback(Path("/tmp/test.wav"))

    def test_play_with_fallback_general_exception(self):
        """_play_with_fallback should re-raise general exceptions."""
        from accessiclock.audio.player import AudioPlayer

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        mock_module = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            with (
                patch.dict("sys.modules", {"playsound3": mock_module}),
                patch("threading.Thread", side_effect=RuntimeError("play failed")),
                pytest.raises(RuntimeError, match="play failed"),
            ):
                player._play_with_fallback(Path(temp_path))
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

    def test_is_playing_exception_returns_false(self):
        """is_playing should return False if stream raises."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            mock_stream = MagicMock()
            type(mock_stream).is_playing = property(
                lambda self: (_ for _ in ()).throw(RuntimeError("error"))
            )
            player._current_stream = mock_stream

            assert player.is_playing() is False
        finally:
            player_module._use_sound_lib = orig_use


class TestStop:
    """Test stop method."""

    def test_stop_exception_clears_stream(self):
        """stop() should set stream to None even if stop/free raise."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            mock_stream = MagicMock()
            mock_stream.stop.side_effect = RuntimeError("stop error")
            player._current_stream = mock_stream

            player.stop()
            assert player._current_stream is None
        finally:
            player_module._use_sound_lib = orig_use


class TestCleanup:
    """Test cleanup method."""

    def test_cleanup_no_error_when_nothing_playing(self):
        """cleanup should not raise when nothing is playing."""
        with patch("accessiclock.audio.player._use_sound_lib", False):
            from accessiclock.audio.player import AudioPlayer

            player = AudioPlayer()
            player.cleanup()

    def test_cleanup_stops_playback(self):
        """cleanup should stop any current playback."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use_sound_lib = player_module._use_sound_lib
        original_bass_init = player_module._bass_initialized

        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = False

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            mock_current = MagicMock()
            player._current_stream = mock_current

            player.cleanup()

            mock_current.stop.assert_called_once()
            mock_current.free.assert_called_once()
        finally:
            player_module._use_sound_lib = original_use_sound_lib
            player_module._bass_initialized = original_bass_init

    def test_cleanup_stream_error_handled(self):
        """cleanup should handle errors when stopping stream."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        orig_init = player_module._bass_initialized

        try:
            player_module._use_sound_lib = False
            player_module._bass_initialized = False

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            mock_current = MagicMock()
            mock_current.stop.side_effect = RuntimeError("cleanup error")
            player._current_stream = mock_current

            # Should not raise
            player.cleanup()
        finally:
            player_module._use_sound_lib = orig_use
            player_module._bass_initialized = orig_init

    def test_cleanup_frees_bass(self):
        """cleanup should call BASS_Free when sound_lib initialized."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        orig_init = player_module._bass_initialized
        orig_bass_free = getattr(player_module, "BASS_Free", None)

        mock_bass_free = MagicMock()

        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = True
            player_module.BASS_Free = mock_bass_free

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = None

            player.cleanup()

            mock_bass_free.assert_called_once()
            assert player_module._bass_initialized is False
        finally:
            player_module._use_sound_lib = orig_use
            player_module._bass_initialized = orig_init
            if orig_bass_free is not None:
                player_module.BASS_Free = orig_bass_free

    def test_cleanup_bass_free_error_handled(self):
        """cleanup should handle errors from BASS_Free."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        orig_use = player_module._use_sound_lib
        orig_init = player_module._bass_initialized
        orig_bass_free = getattr(player_module, "BASS_Free", None)

        mock_bass_free = MagicMock(side_effect=RuntimeError("bass error"))

        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = True
            player_module.BASS_Free = mock_bass_free

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = None

            # Should not raise
            player.cleanup()
            mock_bass_free.assert_called_once()
        finally:
            player_module._use_sound_lib = orig_use
            player_module._bass_initialized = orig_init
            if orig_bass_free is not None:
                player_module.BASS_Free = orig_bass_free


class TestSoundLibIntegration:
    """Test sound_lib integration (cross-platform)."""

    def test_sound_lib_play_creates_stream(self):
        """Playing with sound_lib should create a FileStream."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        mock_stream_module = MagicMock()
        mock_file_stream = MagicMock()
        mock_stream_module.FileStream.return_value = mock_file_stream

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(player_module, "stream", mock_stream_module, create=True):
                player._play_with_sound_lib(Path(temp_path))

            mock_stream_module.FileStream.assert_called_once()
            mock_file_stream.play.assert_called_once()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_sound_lib_sets_volume_on_stream(self):
        """Playing should set volume on the stream."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        mock_stream_module = MagicMock()
        mock_file_stream = MagicMock()
        mock_stream_module.FileStream.return_value = mock_file_stream

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 75
        player._current_stream = None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(player_module, "stream", mock_stream_module, create=True):
                player._play_with_sound_lib(Path(temp_path))

            assert mock_file_stream.volume == 0.75
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_sound_lib_stops_previous_stream(self):
        """Playing a new sound should stop the previous stream."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        mock_stream_module = MagicMock()
        mock_new_stream = MagicMock()
        mock_stream_module.FileStream.return_value = mock_new_stream

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = MagicMock()
        player.stop = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(player_module, "stream", mock_stream_module, create=True):
                player._play_with_sound_lib(Path(temp_path))

            player.stop.assert_called_once()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_sound_lib_is_playing_checks_stream(self):
        """is_playing should check the stream's is_playing property."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use_sound_lib = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50

            player._current_stream = None
            assert player.is_playing() is False

            mock_stream = MagicMock()
            mock_stream.is_playing = True
            player._current_stream = mock_stream
            assert player.is_playing() is True

            mock_stream.is_playing = False
            assert player.is_playing() is False
        finally:
            player_module._use_sound_lib = original_use_sound_lib

    def test_sound_lib_stop_frees_stream(self):
        """stop should stop and free the current stream."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

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
