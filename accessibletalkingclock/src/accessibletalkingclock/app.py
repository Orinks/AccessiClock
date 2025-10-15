"""
Accessible Talking Clock - A desktop clock application designed for visually impaired users.
"""

import asyncio
import logging
from datetime import datetime
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AccessibleTalkingClock(toga.App):
    """Main application class for the Accessible Talking Clock."""

    def startup(self):
        """Initialize the application interface."""
        logger.info("Starting Accessible Talking Clock application")
        
        # Create the main window
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Clock display section - using TextInput for screen reader accessibility
        self.clock_display = toga.TextInput(
            value=self._get_current_time_string(),
            readonly=True,
            style=Pack(
                padding=(20, 0, 20, 0),
                text_align="center",
                font_size=32,
                font_weight="bold"
            )
        )
        
        # Status label for screen reader feedback
        self.status_label = toga.Label(
            text="Clock initialized. Use Tab to navigate controls.",
            style=Pack(
                padding=10,
                text_align="left",
                font_size=12
            )
        )
        
        # Controls section
        controls_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Soundpack selection
        soundpack_box = toga.Box(style=Pack(direction=ROW, padding=5))
        soundpack_label = toga.Label(
            text="Soundpack:",
            style=Pack(padding=(5, 10, 5, 0), width=100)
        )
        
        self.soundpack_selection = toga.Selection(
            items=["Classic (Westminster)", "Nature (Birds & Water)", "Digital (Beeps)"],
            value="Classic (Westminster)",
            style=Pack(flex=1, padding=5)
        )
        self.soundpack_selection.on_change = self._on_soundpack_change
        
        soundpack_box.add(soundpack_label)
        soundpack_box.add(self.soundpack_selection)
        
        # Volume control (simplified for Phase 1)
        volume_box = toga.Box(style=Pack(direction=ROW, padding=5))
        volume_label = toga.Label(
            text="Volume: 50%",
            style=Pack(padding=(5, 10, 5, 0), flex=1)
        )
        
        self.volume_button = toga.Button(
            text="Change Volume",
            on_press=self._change_volume,
            style=Pack(padding=5)
        )
        
        volume_box.add(volume_label)
        volume_box.add(self.volume_button)
        self.current_volume = 50
        
        # Interval configuration
        intervals_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        intervals_title = toga.Label(
            text="Chime Intervals:",
            style=Pack(padding=(0, 0, 10, 0), font_weight="bold")
        )
        
        self.hourly_switch = toga.Switch(
            text="Hourly chimes",
            value=True,
            style=Pack(padding=5)
        )
        self.hourly_switch.on_change = self._on_interval_change
        
        self.half_hour_switch = toga.Switch(
            text="Half-hour chimes",
            value=False,
            style=Pack(padding=5)
        )
        self.half_hour_switch.on_change = self._on_interval_change
        
        self.quarter_hour_switch = toga.Switch(
            text="Quarter-hour chimes",
            value=False,
            style=Pack(padding=5)
        )
        self.quarter_hour_switch.on_change = self._on_interval_change
        
        intervals_box.add(intervals_title)
        intervals_box.add(self.hourly_switch)
        intervals_box.add(self.half_hour_switch)
        intervals_box.add(self.quarter_hour_switch)
        
        # Test chime button
        test_button = toga.Button(
            text="Test Current Chime",
            on_press=self._test_chime,
            style=Pack(padding=10, width=200)
        )
        
        # Settings button
        settings_button = toga.Button(
            text="Settings",
            on_press=self._open_settings,
            style=Pack(padding=10, width=200)
        )
        
        # Add all components to the main layout
        controls_box.add(soundpack_box)
        controls_box.add(volume_box)
        controls_box.add(intervals_box)
        
        main_box.add(self.clock_display)
        main_box.add(controls_box)
        main_box.add(test_button)
        main_box.add(settings_button)
        main_box.add(self.status_label)
        
        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
        
        # Initialize audio system placeholder
        logger.info("Audio system initialization will be implemented in Phase 2")
        
        # Start the clock update timer
        self._schedule_clock_update()
        
        logger.info("Application startup completed successfully")

    def _get_current_time_string(self):
        """Get the current time as a formatted string."""
        return datetime.now().strftime("%I:%M:%S %p")

    def _schedule_clock_update(self):
        """Schedule regular clock display updates."""
        async def update_clock(*args):
            while True:
                try:
                    self.clock_display.value = self._get_current_time_string()
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error updating clock display: {e}")
                    await asyncio.sleep(1)
        
        # Schedule the coroutine to run
        self.add_background_task(update_clock)

    def _on_soundpack_change(self, widget):
        """Handle soundpack selection change."""
        logger.info(f"Soundpack changed to: {widget.value}")
        self.status_label.text = f"Soundpack changed to: {widget.value}"
        # Audio system integration will be implemented in Phase 2

    def _change_volume(self, widget):
        """Handle volume button press - cycle through volume levels."""
        volumes = [0, 25, 50, 75, 100]
        current_index = volumes.index(self.current_volume)
        next_index = (current_index + 1) % len(volumes)
        self.current_volume = volumes[next_index]
        
        # Update the volume label
        volume_label = widget.parent.children[0]  # Get the first child (volume label)
        volume_label.text = f"Volume: {self.current_volume}%"
        
        logger.info(f"Volume changed to: {self.current_volume}%")
        self.status_label.text = f"Volume set to {self.current_volume}%"
        # Audio system integration will be implemented in Phase 2

    def _on_interval_change(self, widget):
        """Handle interval switch changes."""
        intervals = []
        if self.hourly_switch.value:
            intervals.append("hourly")
        if self.half_hour_switch.value:
            intervals.append("half-hour")
        if self.quarter_hour_switch.value:
            intervals.append("quarter-hour")
        
        interval_text = ", ".join(intervals) if intervals else "none"
        logger.info(f"Chime intervals changed to: {interval_text}")
        self.status_label.text = f"Chime intervals: {interval_text}"
        # Timer system integration will be implemented in Phase 2

    def _test_chime(self, widget):
        """Test the current chime sound."""
        current_soundpack = self.soundpack_selection.value
        logger.info(f"Testing chime for soundpack: {current_soundpack}")
        self.status_label.text = f"Testing chime: {current_soundpack}"
        # Audio playback will be implemented in Phase 2

    def _open_settings(self, widget):
        """Open the settings dialog."""
        logger.info("Opening settings dialog")
        self.status_label.text = "Settings dialog (to be implemented)"
        # Settings dialog will be implemented in Phase 4


def main():
    """Application entry point."""
    return AccessibleTalkingClock(
        'Accessible Talking Clock',
        'tech.memex.accessibletalkingclock'
    )
