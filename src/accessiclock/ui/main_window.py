"""
Main window for AccessiClock using wxPython.

Provides the primary UI with clock display, controls, and full
keyboard/screen reader accessibility.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

import wx

from ..constants import TIME_FORMAT_12H, VOLUME_LEVELS

if TYPE_CHECKING:
    from ..app import AccessiClockApp

logger = logging.getLogger(__name__)


class MainWindow(wx.Frame):
    """
    Main application window for AccessiClock.

    Features:
    - Large clock display (screen reader accessible)
    - Clock pack selection
    - Volume control
    - Chime interval configuration
    - Test and settings buttons
    """

    def __init__(self, app: AccessiClockApp):
        """
        Initialize the main window.

        Args:
            app: The AccessiClock application instance.
        """
        super().__init__(
            parent=None,
            title="AccessiClock",
            size=(500, 450),
            style=wx.DEFAULT_FRAME_STYLE,
        )
        self.app = app

        # Timer for clock updates
        self._clock_timer: wx.Timer | None = None

        # Create UI
        self._create_widgets()
        self._create_menu_bar()
        self._bind_events()
        self._setup_keyboard_shortcuts()

        # Start clock timer
        self._start_clock_timer()

        # Center window
        self.Centre()

        logger.info("Main window created")

    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Clock display - large, readable, screen reader accessible
        clock_label = wx.StaticText(panel, label="Current Time:")
        main_sizer.Add(clock_label, 0, wx.LEFT | wx.TOP, 10)

        self.clock_display = wx.TextCtrl(
            panel,
            value=self._get_current_time(),
            style=wx.TE_READONLY | wx.TE_CENTER,
            name="Current time display",
        )
        # Make it large and readable
        font = self.clock_display.GetFont()
        font.SetPointSize(28)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.clock_display.SetFont(font)
        main_sizer.Add(self.clock_display, 0, wx.EXPAND | wx.ALL, 10)

        # Status label for screen reader feedback
        self.status_label = wx.StaticText(
            panel,
            label="Ready. Use Tab to navigate controls.",
            name="Status",
        )
        main_sizer.Add(self.status_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Clock pack selection
        clock_sizer = wx.BoxSizer(wx.HORIZONTAL)
        clock_label = wx.StaticText(panel, label="Clock:")
        clock_sizer.Add(clock_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        # Get available clocks from app
        clock_choices = self.app.get_available_clocks()
        current_clock = self._get_clock_display_name(self.app.selected_clock)

        self.clock_selection = wx.ComboBox(
            panel,
            choices=clock_choices,
            value=current_clock if current_clock in clock_choices else clock_choices[0],
            style=wx.CB_READONLY,
            name="Clock pack selection",
        )
        clock_sizer.Add(self.clock_selection, 1, wx.EXPAND)
        main_sizer.Add(clock_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        main_sizer.AddSpacer(10)

        # Volume control
        volume_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.volume_label = wx.StaticText(
            panel,
            label=f"Volume: {self.app.current_volume}%",
        )
        volume_sizer.Add(self.volume_label, 1, wx.ALIGN_CENTER_VERTICAL)

        self.volume_button = wx.Button(panel, label="Change &Volume")
        volume_sizer.Add(self.volume_button, 0)
        main_sizer.Add(volume_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        main_sizer.AddSpacer(10)

        # Chime intervals
        intervals_label = wx.StaticText(panel, label="Chime Intervals:")
        intervals_label.SetFont(
            intervals_label.GetFont().Bold()
        )
        main_sizer.Add(intervals_label, 0, wx.LEFT, 10)

        self.hourly_checkbox = wx.CheckBox(panel, label="&Hourly chimes")
        self.hourly_checkbox.SetValue(self.app.chime_hourly)
        main_sizer.Add(self.hourly_checkbox, 0, wx.LEFT | wx.TOP, 15)

        self.half_hour_checkbox = wx.CheckBox(panel, label="Ha&lf-hour chimes")
        self.half_hour_checkbox.SetValue(self.app.chime_half_hour)
        main_sizer.Add(self.half_hour_checkbox, 0, wx.LEFT | wx.TOP, 15)

        self.quarter_hour_checkbox = wx.CheckBox(panel, label="&Quarter-hour chimes")
        self.quarter_hour_checkbox.SetValue(self.app.chime_quarter_hour)
        main_sizer.Add(self.quarter_hour_checkbox, 0, wx.LEFT | wx.TOP, 15)

        main_sizer.AddSpacer(15)

        # Action buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.test_button = wx.Button(panel, label="&Test Chime")
        button_sizer.Add(self.test_button, 0, wx.RIGHT, 10)

        self.announce_button = wx.Button(panel, label="&Announce Time")
        button_sizer.Add(self.announce_button, 0, wx.RIGHT, 10)

        self.settings_button = wx.Button(panel, label="&Settings")
        button_sizer.Add(self.settings_button, 0)

        main_sizer.Add(button_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(main_sizer)

    def _create_menu_bar(self) -> None:
        """Create the menu bar."""
        menubar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        settings_item = file_menu.Append(wx.ID_PREFERENCES, "&Settings\tCtrl+,")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4")
        menubar.Append(file_menu, "&File")

        # Clock menu
        clock_menu = wx.Menu()
        test_item = clock_menu.Append(wx.ID_ANY, "&Test Chime\tF5")
        announce_item = clock_menu.Append(wx.ID_ANY, "&Announce Time\tSpace")
        clock_menu.AppendSeparator()
        manage_item = clock_menu.Append(wx.ID_ANY, "&Manage Clocks...")
        menubar.Append(clock_menu, "&Clock")

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About AccessiClock")
        menubar.Append(help_menu, "&Help")

        self.SetMenuBar(menubar)

        # Bind menu events
        self.Bind(wx.EVT_MENU, self._on_settings, settings_item)
        self.Bind(wx.EVT_MENU, self._on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self._on_test_chime, test_item)
        self.Bind(wx.EVT_MENU, self._on_announce_time, announce_item)
        self.Bind(wx.EVT_MENU, self._on_manage_clocks, manage_item)
        self.Bind(wx.EVT_MENU, self._on_about, about_item)

    def _bind_events(self) -> None:
        """Bind event handlers."""
        # Window events
        self.Bind(wx.EVT_CLOSE, self._on_close)

        # Control events
        self.clock_selection.Bind(wx.EVT_COMBOBOX, self._on_clock_changed)
        self.volume_button.Bind(wx.EVT_BUTTON, self._on_change_volume)
        self.hourly_checkbox.Bind(wx.EVT_CHECKBOX, self._on_interval_changed)
        self.half_hour_checkbox.Bind(wx.EVT_CHECKBOX, self._on_interval_changed)
        self.quarter_hour_checkbox.Bind(wx.EVT_CHECKBOX, self._on_interval_changed)
        self.test_button.Bind(wx.EVT_BUTTON, self._on_test_chime)
        self.announce_button.Bind(wx.EVT_BUTTON, self._on_announce_time)
        self.settings_button.Bind(wx.EVT_BUTTON, self._on_settings)

    def _setup_keyboard_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Keyboard shortcuts are handled via menu accelerators (F5, Space, etc.)
        # defined in _create_menu_bar()

    def _start_clock_timer(self) -> None:
        """Start the clock update timer."""
        self._clock_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_clock_tick, self._clock_timer)
        self._clock_timer.Start(1000)  # Update every second
        logger.info("Clock timer started")

    def _get_current_time(self) -> str:
        """Get the current time as a formatted string."""
        return datetime.now().strftime(TIME_FORMAT_12H)

    def _get_clock_display_name(self, pack_id: str) -> str:
        """Get the display name for a clock pack ID."""
        if self.app.clock_pack_loader:
            pack_info = self.app.clock_pack_loader.get_pack(pack_id)
            if pack_info:
                return pack_info.name
        return pack_id.title()

    def _get_clock_pack_id(self, display_name: str) -> str:
        """Get the pack ID for a clock display name."""
        if self.app.clock_pack_loader:
            for pack_id, pack_info in self.app.clock_pack_loader._cache.items():
                if pack_info.name == display_name:
                    return pack_id
        return display_name.lower()

    # --- Event Handlers ---

    def _on_clock_tick(self, event: wx.TimerEvent) -> None:
        """Handle clock timer tick."""
        self.clock_display.SetValue(self._get_current_time())

        # Check for chime intervals and play sounds
        chime_played = self.app.check_and_play_chime()
        if chime_played:
            self._set_status(f"Playing {chime_played.replace('_', ' ')} chime")

    def _on_clock_changed(self, event: wx.CommandEvent) -> None:
        """Handle clock pack selection change."""
        display_name = self.clock_selection.GetValue()
        pack_id = self._get_clock_pack_id(display_name)
        self.app.selected_clock = pack_id
        self._set_status(f"Clock changed to: {display_name}")
        self.app.save_config()
        logger.info(f"Clock pack changed to: {pack_id} ({display_name})")

    def _on_change_volume(self, event: wx.CommandEvent) -> None:
        """Handle volume button press - cycle through volume levels."""
        try:
            current_index = VOLUME_LEVELS.index(self.app.current_volume)
        except ValueError:
            current_index = 2  # Default to 50%

        next_index = (current_index + 1) % len(VOLUME_LEVELS)
        new_volume = VOLUME_LEVELS[next_index]

        self.app.set_volume(new_volume)
        self.volume_label.SetLabel(f"Volume: {new_volume}%")
        self._set_status(f"Volume set to {new_volume}%")
        logger.info(f"Volume changed to: {new_volume}%")

    def _on_interval_changed(self, event: wx.CommandEvent) -> None:
        """Handle chime interval checkbox changes."""
        self.app.chime_hourly = self.hourly_checkbox.GetValue()
        self.app.chime_half_hour = self.half_hour_checkbox.GetValue()
        self.app.chime_quarter_hour = self.quarter_hour_checkbox.GetValue()

        intervals = []
        if self.app.chime_hourly:
            intervals.append("hourly")
        if self.app.chime_half_hour:
            intervals.append("half-hour")
        if self.app.chime_quarter_hour:
            intervals.append("quarter-hour")

        interval_text = ", ".join(intervals) if intervals else "none"
        self._set_status(f"Chime intervals: {interval_text}")
        self.app.save_config()
        logger.info(f"Chime intervals updated: {interval_text}")

    def _on_test_chime(self, event: wx.CommandEvent) -> None:
        """Handle test chime button/menu."""
        self._set_status("Playing test chime...")
        if self.app.play_test_sound():
            self._set_status(f"Test chime played at {self.app.current_volume}% volume")
        else:
            self._set_status("Could not play test chime - audio not available")

    def _on_announce_time(self, event: wx.CommandEvent) -> None:
        """Handle announce time button/menu."""
        current_time = self._get_current_time()
        
        if self.app.announce_time():
            self._set_status(f"Announced: {current_time}")
        else:
            # TTS not available, just show status
            self._set_status(f"The time is {current_time}")
        
        logger.info(f"Time announced: {current_time}")

    def _on_settings(self, event: wx.CommandEvent) -> None:
        """Handle settings button/menu."""
        from .dialogs import SettingsDialog
        
        dlg = SettingsDialog(self, self.app)
        dlg.ShowModal()
        dlg.Destroy()
        
        self._set_status("Settings updated")
        logger.info("Settings dialog closed")

    def _on_manage_clocks(self, event: wx.CommandEvent) -> None:
        """Handle manage clocks menu item."""
        from .dialogs import ClockManagerDialog
        
        dlg = ClockManagerDialog(self, self.app)
        dlg.ShowModal()
        dlg.Destroy()
        
        # Refresh clock selection in case packs changed
        self._refresh_clock_choices()
        self._set_status("Clock manager closed")
        logger.info("Clock manager dialog closed")
    
    def _refresh_clock_choices(self) -> None:
        """Refresh the clock pack dropdown."""
        clock_choices = self.app.get_available_clocks()
        current_selection = self.clock_selection.GetValue()
        
        self.clock_selection.Clear()
        for choice in clock_choices:
            self.clock_selection.Append(choice)
        
        # Try to restore selection
        if current_selection in clock_choices:
            self.clock_selection.SetValue(current_selection)
        elif clock_choices:
            self.clock_selection.SetSelection(0)

    def _on_about(self, event: wx.CommandEvent) -> None:
        """Show about dialog."""
        from ..constants import APP_NAME, APP_VERSION

        info = wx.adv.AboutDialogInfo()
        info.SetName(APP_NAME)
        info.SetVersion(APP_VERSION)
        info.SetDescription(
            "An accessible talking clock with customizable\n"
            "clock packs and AI voice support.\n\n"
            "Designed for screen reader users."
        )
        info.SetCopyright("© 2025 Orinks")
        info.SetWebSite("https://github.com/orinks/AccessiClock")

        wx.adv.AboutBox(info)

    def _on_exit(self, event: wx.CommandEvent) -> None:
        """Handle exit menu item."""
        self.Close()

    def _on_close(self, event: wx.CloseEvent) -> None:
        """Handle window close."""
        logger.info("Main window closing")

        # Stop timer
        if self._clock_timer:
            self._clock_timer.Stop()

        # Save config
        self.app.save_config()

        # Destroy window
        self.Destroy()

    def _set_status(self, message: str) -> None:
        """Update the status label."""
        self.status_label.SetLabel(message)
        logger.debug(f"Status: {message}")
