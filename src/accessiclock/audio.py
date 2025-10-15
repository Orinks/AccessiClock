"""
Audio playback module for AccessiClock using sound_lib.
Handles concurrent audio playback for soundpacks.
"""
try:
    from sound_lib.output import Output
    from sound_lib.stream import FileStream
    SOUND_LIB_AVAILABLE = True
except ImportError:
    SOUND_LIB_AVAILABLE = False
    Output = None
    FileStream = None

import os
import threading


class AudioPlayer:
    """Audio player using sound_lib for concurrent audio playback."""

    def __init__(self):
        """Initialize the audio player."""
        self.output = None
        self._lock = threading.Lock()
        if SOUND_LIB_AVAILABLE:
            self._initialize_output()

    def _initialize_output(self):
        """Initialize the sound_lib output."""
        try:
            self.output = Output()
        except Exception as e:
            print(f"Warning: Could not initialize audio output: {e}")
            self.output = None

    def play_sound(self, sound_path, volume=1.0):
        """
        Play a sound file.
        
        Args:
            sound_path: Path to the sound file
            volume: Volume level (0.0 to 1.0)
        """
        if not SOUND_LIB_AVAILABLE or self.output is None:
            print(f"Audio playback not available, would play: {sound_path}")
            return

        if not os.path.exists(sound_path):
            print(f"Sound file not found: {sound_path}")
            return

        try:
            stream = FileStream(file=sound_path, output=self.output)
            stream.volume = volume
            stream.play_blocking()
        except Exception as e:
            print(f"Error playing sound {sound_path}: {e}")

    def play_sound_async(self, sound_path, volume=1.0):
        """
        Play a sound file asynchronously (non-blocking).
        
        Args:
            sound_path: Path to the sound file
            volume: Volume level (0.0 to 1.0)
        """
        thread = threading.Thread(
            target=self.play_sound,
            args=(sound_path, volume),
            daemon=True
        )
        thread.start()

    def stop_all(self):
        """Stop all currently playing sounds."""
        if self.output:
            try:
                self.output.free()
                self._initialize_output()
            except Exception as e:
                print(f"Error stopping audio: {e}")
