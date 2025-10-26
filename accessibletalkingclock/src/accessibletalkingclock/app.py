"""
Accessible Talking Clock - A desktop clock application designed for visually impaired users.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from accessibletalkingclock.audio import AudioPlayer
from accessibletalkingclock.soundpack import SoundpackManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AccessibleTalkingClock(toga.App):
    """Main application class for the Accessible Talking Clock."""
    
    def __init__(self, *args, **kwargs):
        """Initialize application."""
        super().__init__(*args, **kwargs)
        self._clock_task = None
        self._shutdown_flag = False
        self._last_chime_time = None  # Track last chime to prevent duplicates

    def startup(self):
        """Initialize the application interface."""
        logger.info("Starting Accessible Talking Clock application")
        
        # Initialize audio player (Phase 2)
        try:
            self.audio_player = AudioPlayer(volume_percent=50)
            logger.info("Audio player initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio player: {e}")
            self.audio_player = None
        
        # Initialize soundpack manager (Phase 3)
        try:
            sounds_dir = Path(__file__).parent / "resources" / "sounds"
            self.soundpack_manager = SoundpackManager(sounds_dir)
            
            # Discover available soundpacks
            available_packs = self.soundpack_manager.discover_soundpacks()
            logger.info(f"Discovered soundpacks: {available_packs}")
            
            # Load default soundpack
            default_soundpack = "classic"
            if default_soundpack in available_packs:
                if self.soundpack_manager.load_soundpack(default_soundpack):
                    logger.info(f"Default soundpack '{default_soundpack}' loaded successfully")
                else:
                    logger.error(f"Failed to load default soundpack '{default_soundpack}'")
            else:
                logger.warning(f"Default soundpack '{default_soundpack}' not found")
        except Exception as e:
            logger.error(f"Failed to initialize soundpack manager: {e}")
            self.soundpack_manager = None
        
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
        
        # Populate soundpack dropdown with discovered soundpacks (Phase 3)
        if self.soundpack_manager:
            available_packs = self.soundpack_manager.available_soundpacks
            # Capitalize pack names for display
            pack_items = [pack.capitalize() for pack in available_packs]
            default_value = "Classic" if "Classic" in pack_items else (pack_items[0] if pack_items else "Classic")
        else:
            pack_items = ["Classic", "Nature", "Digital"]
            default_value = "Classic"
        
        self.soundpack_selection = toga.Selection(
            items=pack_items,
            value=default_value,
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
        """Schedule regular clock display updates and automatic chiming."""
        async def update_clock(*args):
            while not self._shutdown_flag:
                try:
                    # Update clock display
                    current_time = datetime.now()
                    self.clock_display.value = current_time.strftime("%I:%M:%S %p")
                    
                    # Check if we should play a chime (Phase 3)
                    minute = current_time.minute
                    
                    # Prevent duplicate chimes - only chime once per minute
                    current_minute_key = (current_time.hour, current_time.minute)
                    if self._last_chime_time != current_minute_key:
                        chime_type = None
                        
                        # Determine chime type based on time and enabled intervals
                        if minute == 0 and self.hourly_switch.value:
                            chime_type = "hour"
                        elif minute == 30 and self.half_hour_switch.value:
                            chime_type = "half"
                        elif minute in (15, 45) and self.quarter_hour_switch.value:
                            chime_type = "quarter"
                        
                        # Play the chime if applicable
                        if chime_type:
                            self._play_chime(chime_type)
                            self._last_chime_time = current_minute_key
                    
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error updating clock display: {e}")
                    await asyncio.sleep(1)
            logger.info("Clock update task stopped")
        
        # Schedule the coroutine to run and store reference
        self._clock_task = self.add_background_task(update_clock)

    def _on_soundpack_change(self, widget):
        """Handle soundpack selection change."""
        selected = widget.value.lower()  # Convert display name to soundpack name
        logger.info(f"Soundpack changed to: {selected}")
        
        # Load the selected soundpack (Phase 3)
        if self.soundpack_manager:
            if self.soundpack_manager.load_soundpack(selected):
                self.status_label.text = f"Soundpack changed to {widget.value}"
                logger.info(f"Successfully loaded soundpack: {selected}")
            else:
                self.status_label.text = f"Failed to load {widget.value} soundpack"
                logger.error(f"Failed to load soundpack: {selected}")
        else:
            self.status_label.text = f"Soundpack changed to: {widget.value}"
            logger.warning("Soundpack manager not initialized")

    def _change_volume(self, widget):
        """Handle volume button press - cycle through volume levels."""
        volumes = [0, 25, 50, 75, 100]
        current_index = volumes.index(self.current_volume)
        next_index = (current_index + 1) % len(volumes)
        self.current_volume = volumes[next_index]
        
        # Update the volume label
        volume_label = widget.parent.children[0]  # Get the first child (volume label)
        volume_label.text = f"Volume: {self.current_volume}%"
        
        # Update audio player volume (Phase 2)
        if self.audio_player:
            self.audio_player.set_volume(self.current_volume)
        
        logger.info(f"Volume changed to: {self.current_volume}%")
        self.status_label.text = f"Volume set to {self.current_volume}%"

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
        """Test the current chime sound - plays hour chime from current soundpack."""
        current_soundpack_name = self.soundpack_selection.value
        logger.info(f"Testing hour chime for soundpack: {current_soundpack_name}")
        
        # Check if both audio player and soundpack manager are initialized
        if not self.audio_player:
            self.status_label.text = "Audio player not initialized"
            logger.warning("Audio player not initialized, cannot play test sound")
            return
        
        if not self.soundpack_manager or not self.soundpack_manager.current_soundpack:
            self.status_label.text = "No soundpack loaded"
            logger.warning("No soundpack loaded, cannot play test chime")
            return
        
        # Play hour chime from current soundpack (Phase 3)
        try:
            soundpack = self.soundpack_manager.current_soundpack
            hour_sound = soundpack.get_sound_path("hour")
            self.audio_player.play_sound(str(hour_sound))
            self.status_label.text = f"Playing {current_soundpack_name} hour chime at {self.current_volume}%"
            logger.info(f"Playing hour chime from {soundpack.name}: {hour_sound}")
        except Exception as e:
            self.status_label.text = f"Error playing chime: {str(e)}"
            logger.error(f"Error playing test chime: {e}")

    def _play_chime(self, chime_type: str):
        """
        Play a chime sound from the current soundpack.
        
        Args:
            chime_type: Type of chime to play ("hour", "half", "quarter")
        """
        if not self.audio_player:
            logger.warning("Cannot play chime: audio player not initialized")
            return
        
        if not self.soundpack_manager or not self.soundpack_manager.current_soundpack:
            logger.warning("Cannot play chime: no soundpack loaded")
            return
        
        try:
            soundpack = self.soundpack_manager.current_soundpack
            chime_path = soundpack.get_sound_path(chime_type)
            self.audio_player.play_sound(str(chime_path))
            logger.info(f"Playing {chime_type} chime from {soundpack.name}")
        except Exception as e:
            logger.error(f"Error playing {chime_type} chime: {e}")
    
    def _open_settings(self, widget):
        """Open the settings dialog."""
        logger.info("Opening settings dialog")
        self.status_label.text = "Settings dialog (to be implemented)"
        # Settings dialog will be implemented in Phase 4
    
    async def on_exit(self):
        """Clean up resources before application exits."""
        logger.info("Application exit handler called")
        
        # Signal clock task to stop
        self._shutdown_flag = True
        
        # Give the clock task time to stop gracefully
        try:
            await asyncio.sleep(0.5)
            logger.info("Clock update task stopped")
        except Exception as e:
            logger.warning(f"Error waiting for clock task: {e}")
        
        # Clean up audio player
        if self.audio_player:
            try:
                self.audio_player.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up audio player: {e}")
        
        logger.info("Application cleanup completed")
        
        # Allow the app to exit
        return True


def main():
    """Application entry point."""
    return AccessibleTalkingClock(
        'Accessible Talking Clock',
        'tech.memex.accessibletalkingclock'
    )
