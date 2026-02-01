"""
AudioPlayer class for playing sound files with volume control.
Uses sound_lib library for thread-safe audio playback.
"""

import logging
from pathlib import Path
from sound_lib import stream

logger = logging.getLogger(__name__)

# Global flag to track if BASS has been initialized
_bass_initialized = False


class AudioPlayer:
    """
    Audio player for playing sound files with volume control.
    
    Uses sound_lib library which provides thread-safe audio playback
    without blocking the UI thread.
    """
    
    def __init__(self, volume_percent=50):
        """
        Initialize AudioPlayer.
        
        Args:
            volume_percent (int): Initial volume level (0-100). Defaults to 50.
        """
        global _bass_initialized
        
        # Initialize BASS audio library if not already initialized
        if not _bass_initialized:
            try:
                from sound_lib import output
                output.Output()  # Initialize default output device
                _bass_initialized = True
                logger.info("BASS audio system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize BASS audio system: {e}")
                raise
        
        self._current_stream = None
        self._volume = self._clamp_volume(volume_percent)
        logger.info(f"AudioPlayer initialized with volume {self._volume}%")
    
    def _clamp_volume(self, volume_percent):
        """
        Clamp volume to valid range (0-100).
        
        Args:
            volume_percent (int): Volume to clamp
            
        Returns:
            int: Clamped volume value
        """
        return max(0, min(100, volume_percent))
    
    def _convert_volume_to_decimal(self, volume_percent):
        """
        Convert volume percentage to decimal (0.0-1.0) for sound_lib.
        
        Args:
            volume_percent (int): Volume percentage (0-100)
            
        Returns:
            float: Volume as decimal (0.0-1.0)
        """
        return volume_percent / 100.0
    
    def get_volume(self):
        """
        Get current volume level.
        
        Returns:
            int: Current volume percentage (0-100)
        """
        return self._volume
    
    def set_volume(self, volume_percent):
        """
        Set volume level.
        
        Args:
            volume_percent (int): Volume level (0-100)
        """
        self._volume = self._clamp_volume(volume_percent)
        logger.info(f"Volume set to {self._volume}%")
        
        # Update volume of currently playing stream if any
        if self._current_stream and self.is_playing():
            self._current_stream.volume = self._convert_volume_to_decimal(self._volume)
    
    def play_sound(self, file_path):
        """
        Play an audio file.
        
        Args:
            file_path (str): Path to audio file to play
            
        Raises:
            FileNotFoundError: If the audio file doesn't exist
            Exception: If the audio file format is invalid or cannot be played
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            logger.error(f"Audio file not found: {file_path}")
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            # Stop any currently playing sound
            if self._current_stream:
                self.stop()
            
            # Create new stream and play
            logger.info(f"Playing audio file: {file_path}")
            self._current_stream = stream.FileStream(file=str(path))
            self._current_stream.volume = self._convert_volume_to_decimal(self._volume)
            self._current_stream.play()
            
        except Exception as e:
            logger.error(f"Error playing audio file {file_path}: {e}")
            raise
    
    def stop(self):
        """
        Stop currently playing audio.
        """
        if self._current_stream:
            try:
                logger.info("Stopping audio playback")
                self._current_stream.stop()
                self._current_stream.free()
                self._current_stream = None
            except Exception as e:
                logger.warning(f"Error stopping audio: {e}")
                self._current_stream = None
    
    def is_playing(self):
        """
        Check if audio is currently playing.
        
        Returns:
            bool: True if audio is playing, False otherwise
        """
        if self._current_stream:
            try:
                return self._current_stream.is_playing
            except Exception:
                # If we can't check status, assume not playing
                return False
        return False
    
    def cleanup(self):
        """
        Clean up audio resources.
        Should be called when shutting down the application.
        """
        global _bass_initialized
        
        logger.info("Cleaning up AudioPlayer resources")
        if self._current_stream:
            try:
                self._current_stream.stop()
                self._current_stream.free()
                self._current_stream = None
            except Exception as e:
                logger.warning(f"Error during AudioPlayer cleanup: {e}")
        
        # Note: BASS library cleanup is handled automatically by sound_lib
        # when the Output object is garbage collected
