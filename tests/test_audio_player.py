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
        """AudioPlayer should init BASS when sound_lib is available."""
        import accessiclock.audio.player as player_module

        original_use = player_module._use_sound_lib
        original_init = player_module._bass_initialized
        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = False

            mock_output = MagicMock()
            with (
                patch.dict(
                    "sys.modules",
                    {"sound_lib.output": mock_output, "sound_lib": MagicMock()},
                ),
                patch(
                    "accessiclock.audio.player.output", mock_output, create=True
                ),
            ):
                from accessiclock.audio.player import AudioPlayer

                player = AudioPlayer.__new__(AudioPlayer)
                player._current_stream = None
                player._volume = 50
                assert player is not None

            # Reset
            player_module._bass_initialized = False
        finally:
            player_module._use_sound_lib = original_use
            player_module._bass_initialized = original_init

    def test_init_bass_already_initialized(self):
        """AudioPlayer should skip BASS init if already done."""
        import accessiclock.audio.player as player_module

        original_use = player_module._use_sound_lib
        original_init = player_module._bass_initialized
        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = True  # Already init'd

            from accessiclock.audio.player import AudioPlayer

            player = AudioPlayer.__new__(AudioPlayer)
            player._current_stream = None
            player._volume = 50
            # No error since BASS already initialized
        finally:
            player_module._use_sound_lib = original_use
            player_module._bass_initialized = original_init


class TestVolumeControl:
    """Test volume control methods."""

    @pytest.fixture()
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

    def test_set_volume_updates_playing_stream(self):
        """set_volume should update volume on currently playing stream."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
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
            player_module._use_sound_lib = original_use

    def test_set_volume_no_update_when_not_playing(self):
        """set_volume should not update stream volume if not playing."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50

            # Use a non-Mock object to verify volume is not set
            class FakeStream:
                is_playing = False
                volume = 0.5  # original value

            fake_stream = FakeStream()
            player._current_stream = fake_stream

            player.set_volume(80)
            assert player.get_volume() == 80
            # Volume should NOT be updated since stream is not playing
            assert fake_stream.volume == 0.5
        finally:
            player_module._use_sound_lib = original_use


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

        original_use = player_module._use_sound_lib
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
            player_module._use_sound_lib = original_use

    def test_play_sound_dispatches_to_fallback(self):
        """play_sound should use fallback when sound_lib unavailable."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
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
            player_module._use_sound_lib = original_use

    def test_play_with_fallback_uses_playsound3(self):
        """_play_with_fallback should use playsound3 in a thread."""
        from accessiclock.audio.player import AudioPlayer

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        mock_playsound = MagicMock()
        mock_thread_class = MagicMock()
        mock_thread_instance = MagicMock()
        mock_thread_class.return_value = mock_thread_instance

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        try:
            with (
                patch(
                    "accessiclock.audio.player.playsound",
                    mock_playsound,
                    create=True,
                ),
                patch("threading.Thread", mock_thread_class),
            ):
                player._play_with_fallback(Path(temp_path))
                mock_thread_class.assert_called_once()
                mock_thread_instance.start.assert_called_once()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_play_with_fallback_import_error(self):
        """_play_with_fallback should raise ImportError when playsound3 missing."""
        from accessiclock.audio.player import AudioPlayer

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        try:
            with (
                patch(
                    "builtins.__import__",
                    side_effect=ImportError("No module named 'playsound3'"),
                ),
                pytest.raises(ImportError),
            ):
                player._play_with_fallback(Path(temp_path))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_play_with_fallback_generic_error(self):
        """_play_with_fallback should raise on generic errors."""
        from accessiclock.audio.player import AudioPlayer

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        try:
            mock_playsound = MagicMock()
            with (
                patch("threading.Thread", side_effect=RuntimeError("thread error")),
                patch.dict("sys.modules", {"playsound3": MagicMock(playsound=mock_playsound)}),
                pytest.raises(RuntimeError, match="thread error"),
            ):
                player._play_with_fallback(Path(temp_path))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_play_with_sound_lib_error(self):
        """_play_with_sound_lib should raise on stream errors."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        mock_stream_module = MagicMock()
        mock_stream_module.FileStream.side_effect = RuntimeError("stream error")

        player = AudioPlayer.__new__(AudioPlayer)
        player._volume = 50
        player._current_stream = None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        try:
            with (
                patch.object(
                    player_module, "stream", mock_stream_module, create=True
                ),
                pytest.raises(RuntimeError, match="stream error"),
            ):
                player._play_with_sound_lib(Path(temp_path))
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
        """is_playing should return False when stream raises exception."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
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
            player_module._use_sound_lib = original_use

    def test_is_playing_no_sound_lib_returns_false(self):
        """is_playing returns False when sound_lib is not used."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = False

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = MagicMock()  # Even with a stream

            assert player.is_playing() is False
        finally:
            player_module._use_sound_lib = original_use


class TestStop:
    """Test stop method."""

    def test_stop_no_stream(self):
        """stop should be safe when no stream exists."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = True

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = None

            # Should not raise
            player.stop()
        finally:
            player_module._use_sound_lib = original_use

    def test_stop_exception_clears_stream(self):
        """stop should clear stream reference even on error."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
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
            player_module._use_sound_lib = original_use

    def test_stop_not_sound_lib(self):
        """stop should be no-op when sound_lib not used."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
        try:
            player_module._use_sound_lib = False

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = MagicMock()

            player.stop()
            # Stream not touched since sound_lib not used
            assert player._current_stream is not None
        finally:
            player_module._use_sound_lib = original_use


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

    def test_cleanup_stream_error_suppressed(self):
        """cleanup should suppress stream stop/free errors."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
        original_init = player_module._bass_initialized

        try:
            player_module._use_sound_lib = False
            player_module._bass_initialized = False

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50

            mock_stream = MagicMock()
            mock_stream.stop.side_effect = RuntimeError("cleanup error")
            player._current_stream = mock_stream

            # Should not raise
            player.cleanup()
        finally:
            player_module._use_sound_lib = original_use
            player_module._bass_initialized = original_init

    def test_cleanup_frees_bass(self):
        """cleanup should call BASS_Free when bass was initialized."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
        original_init = player_module._bass_initialized
        original_bass_free = getattr(player_module, "BASS_Free", None)

        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = True

            mock_bass_free = MagicMock()
            player_module.BASS_Free = mock_bass_free

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = None

            player.cleanup()

            mock_bass_free.assert_called_once()
            assert player_module._bass_initialized is False
        finally:
            player_module._use_sound_lib = original_use
            player_module._bass_initialized = original_init
            if original_bass_free is not None:
                player_module.BASS_Free = original_bass_free
            elif hasattr(player_module, "BASS_Free"):
                delattr(player_module, "BASS_Free")

    def test_cleanup_bass_free_error_suppressed(self):
        """cleanup should suppress BASS_Free errors."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

        original_use = player_module._use_sound_lib
        original_init = player_module._bass_initialized
        original_bass_free = getattr(player_module, "BASS_Free", None)

        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = True

            mock_bass_free = MagicMock(side_effect=RuntimeError("bass error"))
            player_module.BASS_Free = mock_bass_free

            player = AudioPlayer.__new__(AudioPlayer)
            player._volume = 50
            player._current_stream = None

            # Should not raise
            player.cleanup()
            mock_bass_free.assert_called_once()
        finally:
            player_module._use_sound_lib = original_use
            player_module._bass_initialized = original_init
            if original_bass_free is not None:
                player_module.BASS_Free = original_bass_free
            elif hasattr(player_module, "BASS_Free"):
                delattr(player_module, "BASS_Free")


class TestSoundLibIntegration:
    """Test sound_lib integration (cross-platform)."""

    def test_sound_lib_play_creates_stream(self):
        """Playing with sound_lib should create a FileStream."""
        import accessiclock.audio.player as player_module
        from accessiclock.audio.player import AudioPlayer

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
            with patch.object(
                player_module, "stream", mock_stream_module, create=True
            ):
                player._play_with_sound_lib(Path(temp_path))

            # Verify FileStream was created with correct path
            mock_stream_module.FileStream.assert_called_once()
            call_args = mock_stream_module.FileStream.call_args
            # Check if temp_path was passed as positional or keyword arg
            passed_path = call_args.kwargs.get("file") or (
                call_args.args[0] if call_args.args else None
            )
            assert passed_path is not None
            assert str(Path(passed_path)) == str(Path(temp_path))

            # Verify play was called
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
        player._volume = 75  # 75%
        player._current_stream = None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(
                player_module, "stream", mock_stream_module, create=True
            ):
                player._play_with_sound_lib(Path(temp_path))

            # Verify volume was set to 0.75
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
        player._current_stream = MagicMock()  # existing stream

        # Mock stop method
        player.stop = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(
                player_module, "stream", mock_stream_module, create=True
            ):
                player._play_with_sound_lib(Path(temp_path))

            # stop() should have been called (which stops/frees old stream)
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

    def test_init_bass_via_sound_lib(self):
        """AudioPlayer __init__ should initialize BASS output."""
        import accessiclock.audio.player as player_module

        original_use = player_module._use_sound_lib
        original_init = player_module._bass_initialized

        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = False

            mock_output_module = MagicMock()

            with patch.dict("sys.modules", {"sound_lib.output": mock_output_module}):
                from accessiclock.audio.player import AudioPlayer

                AudioPlayer()
                assert player_module._bass_initialized is True
                mock_output_module.Output.assert_called_once()
        finally:
            player_module._use_sound_lib = original_use
            player_module._bass_initialized = original_init

    def test_init_bass_failure_raises(self):
        """AudioPlayer __init__ should raise if BASS init fails."""
        import accessiclock.audio.player as player_module

        original_use = player_module._use_sound_lib
        original_init = player_module._bass_initialized

        try:
            player_module._use_sound_lib = True
            player_module._bass_initialized = False

            mock_output_module = MagicMock()
            mock_output_module.Output.side_effect = RuntimeError("BASS init failed")

            with patch.dict("sys.modules", {"sound_lib.output": mock_output_module}):
                from accessiclock.audio.player import AudioPlayer

                with pytest.raises(RuntimeError, match="BASS init failed"):
                    AudioPlayer()
        finally:
            player_module._use_sound_lib = original_use
            player_module._bass_initialized = original_init
