"""
AccessiClock - Main application using Toga framework.
An accessible clock app for the blind and visually impaired.
"""
try:
    import toga
    from toga.style import Pack
    from toga.style.pack import COLUMN, ROW
    TOGA_AVAILABLE = True
except ImportError:
    # Allow import even when toga is not installed for testing purposes
    TOGA_AVAILABLE = False
    toga = None
    Pack = None
    COLUMN = None
    ROW = None

from datetime import datetime
import threading
import time

from .clock import Clock
from .tts import TTSEngine
from .soundpack import SoundPackManager


class AccessiClock(toga.App if TOGA_AVAILABLE else object):
    """Main AccessiClock application."""

    def __init__(self, *args, **kwargs):
        """Initialize the AccessiClock app."""
        if TOGA_AVAILABLE:
            super().__init__(*args, **kwargs)
        else:
            # Mock initialization for testing
            self.formal_name = kwargs.get('formal_name', args[0] if args else 'AccessiClock')
            self.app_id = kwargs.get('app_id', args[1] if len(args) > 1 else 'com.orinks.accessiclock')
            self.main_window = None

    def startup(self):
        """
        Construct and show the Toga application.
        
        Returns:
            toga.Box: The main box containing the UI
        """
        if not TOGA_AVAILABLE:
            # Return a mock object for testing
            class MockBox:
                pass
            return MockBox()
        
        # Initialize components
        self.clock = Clock()
        self.tts_engine = TTSEngine()
        self.soundpack_manager = SoundPackManager()
        
        # Create main box
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Time display label
        self.time_label = toga.Label(
            "00:00:00",
            style=Pack(padding=5, font_size=32, text_align='center')
        )
        
        # Button to announce time
        announce_button = toga.Button(
            "Announce Time",
            on_press=self.announce_time,
            style=Pack(padding=5)
        )
        
        # Button to toggle 12/24 hour format
        self.format_12h = True
        self.format_button = toga.Button(
            "Switch to 24-hour",
            on_press=self.toggle_format,
            style=Pack(padding=5)
        )
        
        # Soundpack selection
        soundpack_box = toga.Box(style=Pack(direction=ROW, padding=5))
        soundpack_label = toga.Label("Soundpack:", style=Pack(padding_right=5))
        
        available_packs = self.soundpack_manager.get_available_packs()
        self.soundpack_selection = toga.Selection(
            items=available_packs if available_packs else ["default"],
            style=Pack(flex=1)
        )
        
        soundpack_box.add(soundpack_label)
        soundpack_box.add(self.soundpack_selection)
        
        # Add all widgets to main box
        main_box.add(self.time_label)
        main_box.add(announce_button)
        main_box.add(self.format_button)
        main_box.add(soundpack_box)
        
        # Create main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
        
        # Start clock update thread
        self.running = True
        self.update_thread = threading.Thread(target=self._update_clock, daemon=True)
        self.update_thread.start()
        
        return main_box

    def _update_clock(self):
        """Update the clock display every second."""
        while self.running:
            time_str = self.clock.get_time_string(format_12h=self.format_12h)
            self.time_label.text = time_str
            time.sleep(1)

    def announce_time(self, widget):
        """
        Announce the current time using TTS.
        
        Args:
            widget: The button widget that triggered this callback
        """
        time_str = self.clock.get_time_string(format_12h=self.format_12h)
        # Format time for speech
        hour = self.clock.get_hour()
        minute = self.clock.get_minute()
        
        if self.format_12h:
            period = "AM" if hour < 12 else "PM"
            display_hour = hour % 12
            if display_hour == 0:
                display_hour = 12
            speech = f"The time is {display_hour} {minute:02d} {period}"
        else:
            speech = f"The time is {hour} {minute:02d}"
        
        self.tts_engine.speak(speech, wait=False)

    def toggle_format(self, widget):
        """
        Toggle between 12-hour and 24-hour time format.
        
        Args:
            widget: The button widget that triggered this callback
        """
        self.format_12h = not self.format_12h
        if self.format_12h:
            self.format_button.text = "Switch to 24-hour"
        else:
            self.format_button.text = "Switch to 12-hour"


def main():
    """Main entry point for the application."""
    return AccessiClock(
        'AccessiClock',
        'com.orinks.accessiclock',
        description="Clock app with customizable soundpacks and TTS/AI voices"
    )


if __name__ == '__main__':
    main().main_loop()
