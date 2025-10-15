"""
TTS (Text-to-Speech) integration for AccessiClock.
"""
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

import threading


class TTSEngine:
    """Text-to-Speech engine wrapper using pyttsx3."""

    def __init__(self):
        """Initialize the TTS engine."""
        self.engine = None
        self._lock = threading.Lock()
        if PYTTSX3_AVAILABLE:
            self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the pyttsx3 engine."""
        try:
            self.engine = pyttsx3.init()
        except Exception as e:
            print(f"Warning: Could not initialize TTS engine: {e}")
            self.engine = None

    def speak(self, text, wait=True):
        """
        Speak the given text using TTS.
        
        Args:
            text: The text to speak
            wait: If True, wait for speech to complete. If False, speak asynchronously.
        """
        if self.engine is None:
            print(f"TTS not available, would speak: {text}")
            return

        if wait:
            with self._lock:
                self.engine.say(text)
                self.engine.runAndWait()
        else:
            # Speak asynchronously
            def _speak():
                with self._lock:
                    self.engine.say(text)
                    self.engine.runAndWait()
            
            thread = threading.Thread(target=_speak, daemon=True)
            thread.start()

    def set_rate(self, rate):
        """
        Set the speech rate.
        
        Args:
            rate: Speech rate in words per minute
        """
        if self.engine:
            self.engine.setProperty('rate', rate)

    def set_volume(self, volume):
        """
        Set the speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine:
            self.engine.setProperty('volume', volume)

    def get_voices(self):
        """
        Get available voices.
        
        Returns:
            list: List of available voice objects
        """
        if self.engine:
            return self.engine.getProperty('voices')
        return []

    def set_voice(self, voice_id):
        """
        Set the voice to use.
        
        Args:
            voice_id: ID of the voice to use
        """
        if self.engine:
            self.engine.setProperty('voice', voice_id)
