"""
Settings dialog for AccessiClock.

Provides UI for configuring application preferences including
voice settings, quiet hours, and display options.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import wx

if TYPE_CHECKING:
    from ...app import AccessiClockApp

logger = logging.getLogger(__name__)


class SettingsDialog(wx.Dialog):
    """
    Settings dialog for configuring AccessiClock preferences.
    
    Sections:
    - General: Time format, startup options
    - Voice: TTS settings, voice selection
    - Quiet Hours: When to silence chimes
    - Advanced: Logging, portable mode info
    """

    def __init__(self, parent: wx.Window, app: AccessiClockApp):
        """
        Initialize the settings dialog.
        
        Args:
            parent: Parent window.
            app: The AccessiClock application instance.
        """
        super().__init__(
            parent,
            title="AccessiClock Settings",
            size=(500, 450),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.app = app
        
        # Track changes
        self._changes_made = False
        
        # Create UI
        self._create_widgets()
        self._bind_events()
        self._load_settings()
        
        self.Centre()
        logger.info("Settings dialog opened")

    def _create_widgets(self) -> None:
        """Create all dialog widgets."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create notebook for tabbed sections
        notebook = wx.Notebook(panel)
        
        # General tab
        general_panel = self._create_general_tab(notebook)
        notebook.AddPage(general_panel, "General")
        
        # Voice tab
        voice_panel = self._create_voice_tab(notebook)
        notebook.AddPage(voice_panel, "Voice")
        
        # Quiet Hours tab
        quiet_panel = self._create_quiet_hours_tab(notebook)
        notebook.AddPage(quiet_panel, "Quiet Hours")
        
        # Advanced tab
        advanced_panel = self._create_advanced_tab(notebook)
        notebook.AddPage(advanced_panel, "Advanced")
        
        main_sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        # Button row
        button_sizer = wx.StdDialogButtonSizer()
        
        ok_btn = wx.Button(panel, wx.ID_OK, "OK")
        ok_btn.SetDefault()
        button_sizer.AddButton(ok_btn)
        
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        button_sizer.AddButton(cancel_btn)
        
        apply_btn = wx.Button(panel, wx.ID_APPLY, "Apply")
        button_sizer.AddButton(apply_btn)
        
        button_sizer.Realize()
        main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        
        panel.SetSizer(main_sizer)
        
        # Store references
        self.ok_btn = ok_btn
        self.cancel_btn = cancel_btn
        self.apply_btn = apply_btn

    def _create_general_tab(self, parent: wx.Notebook) -> wx.Panel:
        """Create the General settings tab."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Time format
        format_box = wx.StaticBox(panel, label="Time Format")
        format_sizer = wx.StaticBoxSizer(format_box, wx.VERTICAL)
        
        self.format_12h = wx.RadioButton(
            panel, label="12-hour (e.g., 3:30 PM)", style=wx.RB_GROUP
        )
        self.format_24h = wx.RadioButton(panel, label="24-hour (e.g., 15:30)")
        
        format_sizer.Add(self.format_12h, 0, wx.ALL, 5)
        format_sizer.Add(self.format_24h, 0, wx.ALL, 5)
        sizer.Add(format_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Startup options
        startup_box = wx.StaticBox(panel, label="Startup")
        startup_sizer = wx.StaticBoxSizer(startup_box, wx.VERTICAL)
        
        self.start_minimized = wx.CheckBox(panel, label="Start minimized to tray")
        self.start_with_windows = wx.CheckBox(panel, label="Start with Windows")
        self.play_startup_sound = wx.CheckBox(panel, label="Play startup sound")
        
        startup_sizer.Add(self.start_minimized, 0, wx.ALL, 5)
        startup_sizer.Add(self.start_with_windows, 0, wx.ALL, 5)
        startup_sizer.Add(self.play_startup_sound, 0, wx.ALL, 5)
        sizer.Add(startup_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Announce on focus
        self.announce_on_focus = wx.CheckBox(
            panel, label="Announce time when window gains focus"
        )
        sizer.Add(self.announce_on_focus, 0, wx.LEFT | wx.RIGHT, 10)
        
        panel.SetSizer(sizer)
        return panel

    def _create_voice_tab(self, parent: wx.Notebook) -> wx.Panel:
        """Create the Voice settings tab."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Voice selection
        voice_label = wx.StaticText(panel, label="Voice:")
        sizer.Add(voice_label, 0, wx.LEFT | wx.TOP, 10)
        
        # Get available voices
        voices = []
        if self.app.tts_engine:
            voices = self.app.tts_engine.list_voices()
        if not voices:
            voices = ["(Default system voice)"]
        
        self.voice_choice = wx.Choice(panel, choices=voices)
        self.voice_choice.SetName("Voice")
        self.voice_choice.SetSelection(0)
        sizer.Add(self.voice_choice, 0, wx.EXPAND | wx.ALL, 10)
        
        # Speech rate
        rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        rate_label = wx.StaticText(panel, label="Speech rate:")
        rate_sizer.Add(rate_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        self.rate_slider = wx.Slider(
            panel, value=150, minValue=50, maxValue=300,
            style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL
        )
        self.rate_slider.SetName("Speech rate")
        rate_sizer.Add(self.rate_slider, 1, wx.EXPAND)
        sizer.Add(rate_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Announcement style
        style_box = wx.StaticBox(panel, label="Announcement Style")
        style_sizer = wx.StaticBoxSizer(style_box, wx.VERTICAL)
        
        self.style_simple = wx.RadioButton(
            panel, label='Simple (e.g., "3:30 PM")', style=wx.RB_GROUP
        )
        self.style_natural = wx.RadioButton(
            panel, label='Natural (e.g., "Three thirty in the afternoon")'
        )
        self.style_precise = wx.RadioButton(
            panel, label='Precise (e.g., "3:30 and 15 seconds PM")'
        )
        
        style_sizer.Add(self.style_simple, 0, wx.ALL, 5)
        style_sizer.Add(self.style_natural, 0, wx.ALL, 5)
        style_sizer.Add(self.style_precise, 0, wx.ALL, 5)
        sizer.Add(style_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Test voice button
        self.test_voice_btn = wx.Button(panel, label="Test Voice")
        sizer.Add(self.test_voice_btn, 0, wx.LEFT, 10)
        
        panel.SetSizer(sizer)
        return panel

    def _create_quiet_hours_tab(self, parent: wx.Notebook) -> wx.Panel:
        """Create the Quiet Hours settings tab."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Enable quiet hours
        self.quiet_hours_enabled = wx.CheckBox(
            panel, label="Enable quiet hours (silence chimes during specified times)"
        )
        sizer.Add(self.quiet_hours_enabled, 0, wx.ALL, 10)
        
        # Time range
        time_box = wx.StaticBox(panel, label="Quiet Period")
        time_sizer = wx.StaticBoxSizer(time_box, wx.VERTICAL)
        
        # Start time
        start_sizer = wx.BoxSizer(wx.HORIZONTAL)
        start_label = wx.StaticText(panel, label="Start:")
        start_sizer.Add(start_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        self.quiet_start_hour = wx.SpinCtrl(
            panel, min=0, max=23, initial=22, size=(60, -1)
        )
        self.quiet_start_hour.SetName("Quiet hours start hour")
        start_sizer.Add(self.quiet_start_hour, 0, wx.RIGHT, 5)
        
        start_colon = wx.StaticText(panel, label=":")
        start_sizer.Add(start_colon, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.quiet_start_min = wx.SpinCtrl(
            panel, min=0, max=59, initial=0, size=(60, -1)
        )
        self.quiet_start_min.SetName("Quiet hours start minute")
        start_sizer.Add(self.quiet_start_min, 0)
        
        time_sizer.Add(start_sizer, 0, wx.ALL, 5)
        
        # End time
        end_sizer = wx.BoxSizer(wx.HORIZONTAL)
        end_label = wx.StaticText(panel, label="End:")
        end_sizer.Add(end_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        self.quiet_end_hour = wx.SpinCtrl(
            panel, min=0, max=23, initial=7, size=(60, -1)
        )
        self.quiet_end_hour.SetName("Quiet hours end hour")
        end_sizer.Add(self.quiet_end_hour, 0, wx.RIGHT, 5)
        
        end_colon = wx.StaticText(panel, label=":")
        end_sizer.Add(end_colon, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.quiet_end_min = wx.SpinCtrl(
            panel, min=0, max=59, initial=0, size=(60, -1)
        )
        self.quiet_end_min.SetName("Quiet hours end minute")
        end_sizer.Add(self.quiet_end_min, 0)
        
        time_sizer.Add(end_sizer, 0, wx.ALL, 5)
        
        sizer.Add(time_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Note about spanning midnight
        note = wx.StaticText(
            panel,
            label="Note: If start is after end, quiet hours span midnight\n"
                  "(e.g., 22:00 to 07:00 = 10 PM to 7 AM)"
        )
        note.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(note, 0, wx.ALL, 10)
        
        panel.SetSizer(sizer)
        return panel

    def _create_advanced_tab(self, parent: wx.Notebook) -> wx.Panel:
        """Create the Advanced settings tab."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Logging
        log_box = wx.StaticBox(panel, label="Logging")
        log_sizer = wx.StaticBoxSizer(log_box, wx.VERTICAL)
        
        self.enable_logging = wx.CheckBox(panel, label="Enable debug logging")
        log_sizer.Add(self.enable_logging, 0, wx.ALL, 5)
        
        open_logs_btn = wx.Button(panel, label="Open Logs Folder")
        log_sizer.Add(open_logs_btn, 0, wx.ALL, 5)
        self.open_logs_btn = open_logs_btn
        
        sizer.Add(log_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Data locations
        data_box = wx.StaticBox(panel, label="Data Locations")
        data_sizer = wx.StaticBoxSizer(data_box, wx.VERTICAL)
        
        config_label = wx.StaticText(
            panel, label=f"Config: {self.app.paths.config_file}"
        )
        data_sizer.Add(config_label, 0, wx.ALL, 5)
        
        clocks_label = wx.StaticText(
            panel, label=f"Clocks: {self.app.paths.clocks_dir}"
        )
        data_sizer.Add(clocks_label, 0, wx.ALL, 5)
        
        user_clocks_label = wx.StaticText(
            panel, label=f"User Clocks: {self.app.paths.user_clocks_dir}"
        )
        data_sizer.Add(user_clocks_label, 0, wx.ALL, 5)
        
        sizer.Add(data_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Reset button
        reset_btn = wx.Button(panel, label="Reset to Defaults")
        sizer.Add(reset_btn, 0, wx.LEFT, 10)
        self.reset_btn = reset_btn
        
        panel.SetSizer(sizer)
        return panel

    def _bind_events(self) -> None:
        """Bind event handlers."""
        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self._on_cancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self._on_apply, id=wx.ID_APPLY)
        
        self.test_voice_btn.Bind(wx.EVT_BUTTON, self._on_test_voice)
        self.open_logs_btn.Bind(wx.EVT_BUTTON, self._on_open_logs)
        self.reset_btn.Bind(wx.EVT_BUTTON, self._on_reset)
        
        # Track changes
        for ctrl in [self.format_12h, self.format_24h, self.start_minimized,
                     self.start_with_windows, self.play_startup_sound,
                     self.announce_on_focus, self.voice_choice, self.rate_slider,
                     self.style_simple, self.style_natural, self.style_precise,
                     self.quiet_hours_enabled, self.quiet_start_hour,
                     self.quiet_start_min, self.quiet_end_hour, self.quiet_end_min,
                     self.enable_logging]:
            if hasattr(ctrl, 'Bind'):
                ctrl.Bind(wx.EVT_CHECKBOX, self._on_change)
                ctrl.Bind(wx.EVT_RADIOBUTTON, self._on_change)
                ctrl.Bind(wx.EVT_CHOICE, self._on_change)
                ctrl.Bind(wx.EVT_SPINCTRL, self._on_change)
                ctrl.Bind(wx.EVT_SLIDER, self._on_change)

    def _load_settings(self) -> None:
        """Load current settings into controls."""
        config = self.app.config
        
        # Time format
        time_format = config.get("time_format", "12h")
        self.format_12h.SetValue(time_format == "12h")
        self.format_24h.SetValue(time_format == "24h")
        
        # Startup options
        self.start_minimized.SetValue(config.get("start_minimized", False))
        self.start_with_windows.SetValue(config.get("start_with_windows", False))
        self.play_startup_sound.SetValue(config.get("play_startup_sound", True))
        self.announce_on_focus.SetValue(config.get("announce_on_focus", False))
        
        # Voice settings
        if self.app.tts_engine:
            rate = config.get("speech_rate", 150)
            self.rate_slider.SetValue(rate)
        
        announcement_style = config.get("announcement_style", "simple")
        self.style_simple.SetValue(announcement_style == "simple")
        self.style_natural.SetValue(announcement_style == "natural")
        self.style_precise.SetValue(announcement_style == "precise")
        
        # Quiet hours
        self.quiet_hours_enabled.SetValue(config.get("quiet_hours_enabled", False))
        quiet_start = config.get("quiet_start", "22:00")
        quiet_end = config.get("quiet_end", "07:00")
        
        start_parts = quiet_start.split(":")
        end_parts = quiet_end.split(":")
        self.quiet_start_hour.SetValue(int(start_parts[0]))
        self.quiet_start_min.SetValue(int(start_parts[1]))
        self.quiet_end_hour.SetValue(int(end_parts[0]))
        self.quiet_end_min.SetValue(int(end_parts[1]))
        
        # Advanced
        self.enable_logging.SetValue(config.get("debug_logging", False))

    def _save_settings(self) -> None:
        """Save settings from controls to config."""
        config = self.app.config
        
        # Time format
        config["time_format"] = "12h" if self.format_12h.GetValue() else "24h"
        
        # Startup options
        config["start_minimized"] = self.start_minimized.GetValue()
        config["start_with_windows"] = self.start_with_windows.GetValue()
        config["play_startup_sound"] = self.play_startup_sound.GetValue()
        config["announce_on_focus"] = self.announce_on_focus.GetValue()
        
        # Voice settings
        config["speech_rate"] = self.rate_slider.GetValue()
        
        if self.style_simple.GetValue():
            config["announcement_style"] = "simple"
        elif self.style_natural.GetValue():
            config["announcement_style"] = "natural"
        else:
            config["announcement_style"] = "precise"
        
        # Quiet hours
        config["quiet_hours_enabled"] = self.quiet_hours_enabled.GetValue()
        config["quiet_start"] = f"{self.quiet_start_hour.GetValue():02d}:{self.quiet_start_min.GetValue():02d}"
        config["quiet_end"] = f"{self.quiet_end_hour.GetValue():02d}:{self.quiet_end_min.GetValue():02d}"
        
        # Advanced
        config["debug_logging"] = self.enable_logging.GetValue()
        
        # Update app state
        if self.app.tts_engine:
            self.app.tts_engine.set_rate(config["speech_rate"])
        
        if self.app.clock_service:
            if config["quiet_hours_enabled"]:
                from datetime import time
                start_h, start_m = map(int, config["quiet_start"].split(":"))
                end_h, end_m = map(int, config["quiet_end"].split(":"))
                self.app.clock_service.set_quiet_hours(
                    time(start_h, start_m),
                    time(end_h, end_m)
                )
            else:
                self.app.clock_service.quiet_hours_enabled = False
        
        # Save to file
        self.app.save_config()
        logger.info("Settings saved")

    def _on_change(self, event: wx.CommandEvent) -> None:
        """Track that changes were made."""
        self._changes_made = True
        event.Skip()

    def _on_ok(self, event: wx.CommandEvent) -> None:
        """Handle OK button - save and close."""
        self._save_settings()
        self.EndModal(wx.ID_OK)

    def _on_cancel(self, event: wx.CommandEvent) -> None:
        """Handle Cancel button - close without saving."""
        if self._changes_made:
            dlg = wx.MessageDialog(
                self,
                "You have unsaved changes. Discard them?",
                "Unsaved Changes",
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
            )
            if dlg.ShowModal() != wx.ID_YES:
                dlg.Destroy()
                return
            dlg.Destroy()
        
        self.EndModal(wx.ID_CANCEL)

    def _on_apply(self, event: wx.CommandEvent) -> None:
        """Handle Apply button - save without closing."""
        self._save_settings()
        self._changes_made = False

    def _on_test_voice(self, event: wx.CommandEvent) -> None:
        """Play a test voice announcement."""
        if self.app.tts_engine:
            # Temporarily apply rate
            rate = self.rate_slider.GetValue()
            self.app.tts_engine.set_rate(rate)
            
            # Get style
            if self.style_simple.GetValue():
                style = "simple"
            elif self.style_natural.GetValue():
                style = "natural"
            else:
                style = "precise"
            
            from datetime import datetime
            self.app.tts_engine.speak_time(datetime.now().time(), style=style)
        else:
            wx.MessageBox(
                "TTS engine is not available.",
                "Voice Test",
                wx.OK | wx.ICON_WARNING
            )

    def _on_open_logs(self, event: wx.CommandEvent) -> None:
        """Open the logs folder in file explorer."""
        import subprocess
        import sys
        
        logs_dir = self.app.paths.logs_dir
        
        if sys.platform == "win32":
            subprocess.run(["explorer", str(logs_dir)])
        elif sys.platform == "darwin":
            subprocess.run(["open", str(logs_dir)])
        else:
            subprocess.run(["xdg-open", str(logs_dir)])

    def _on_reset(self, event: wx.CommandEvent) -> None:
        """Reset all settings to defaults."""
        dlg = wx.MessageDialog(
            self,
            "Reset all settings to defaults?\n\nThis cannot be undone.",
            "Reset Settings",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            # Reset to defaults
            self.format_12h.SetValue(True)
            self.format_24h.SetValue(False)
            self.start_minimized.SetValue(False)
            self.start_with_windows.SetValue(False)
            self.play_startup_sound.SetValue(True)
            self.announce_on_focus.SetValue(False)
            self.rate_slider.SetValue(150)
            self.style_simple.SetValue(True)
            self.quiet_hours_enabled.SetValue(False)
            self.quiet_start_hour.SetValue(22)
            self.quiet_start_min.SetValue(0)
            self.quiet_end_hour.SetValue(7)
            self.quiet_end_min.SetValue(0)
            self.enable_logging.SetValue(False)
            
            self._changes_made = True
            logger.info("Settings reset to defaults")
        
        dlg.Destroy()
