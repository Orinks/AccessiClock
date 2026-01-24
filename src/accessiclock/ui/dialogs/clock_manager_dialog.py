"""
Clock Manager dialog for AccessiClock.

Provides UI for browsing, installing, and managing clock packs.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import wx

if TYPE_CHECKING:
    from ...app import AccessiClockApp
    from ...services.clock_pack_loader import ClockPackInfo

logger = logging.getLogger(__name__)


class ClockManagerDialog(wx.Dialog):
    """
    Dialog for managing clock packs.
    
    Features:
    - View installed clock packs with details
    - Preview clock pack sounds
    - Delete user-installed packs
    - Import clock packs from files
    """

    def __init__(self, parent: wx.Window, app: AccessiClockApp):
        """
        Initialize the clock manager dialog.
        
        Args:
            parent: Parent window.
            app: The AccessiClock application instance.
        """
        super().__init__(
            parent,
            title="Clock Manager",
            size=(600, 500),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.app = app
        
        # Currently selected pack
        self._selected_pack_id: str | None = None
        
        # Create UI
        self._create_widgets()
        self._bind_events()
        self._refresh_pack_list()
        
        self.Centre()
        logger.info("Clock manager dialog opened")

    def _create_widgets(self) -> None:
        """Create all dialog widgets."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left side - pack list
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        list_label = wx.StaticText(panel, label="Installed Clock Packs:")
        left_sizer.Add(list_label, 0, wx.BOTTOM, 5)
        
        self.pack_list = wx.ListBox(panel, style=wx.LB_SINGLE)
        left_sizer.Add(self.pack_list, 1, wx.EXPAND)
        
        # List buttons
        list_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.import_btn = wx.Button(panel, label="&Import...")
        list_btn_sizer.Add(self.import_btn, 0, wx.RIGHT, 5)
        
        self.delete_btn = wx.Button(panel, label="&Delete")
        self.delete_btn.Disable()
        list_btn_sizer.Add(self.delete_btn, 0)
        
        left_sizer.Add(list_btn_sizer, 0, wx.TOP, 10)
        
        main_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 10)
        
        # Right side - details
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        details_label = wx.StaticText(panel, label="Pack Details:")
        right_sizer.Add(details_label, 0, wx.BOTTOM, 5)
        
        # Details panel
        details_box = wx.StaticBox(panel, label="")
        details_sizer = wx.StaticBoxSizer(details_box, wx.VERTICAL)
        
        self.name_label = wx.StaticText(panel, label="Name: -")
        details_sizer.Add(self.name_label, 0, wx.ALL, 5)
        
        self.author_label = wx.StaticText(panel, label="Author: -")
        details_sizer.Add(self.author_label, 0, wx.ALL, 5)
        
        self.version_label = wx.StaticText(panel, label="Version: -")
        details_sizer.Add(self.version_label, 0, wx.ALL, 5)
        
        self.description_text = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 60)
        )
        details_sizer.Add(self.description_text, 0, wx.EXPAND | wx.ALL, 5)
        
        right_sizer.Add(details_sizer, 0, wx.EXPAND)
        
        # Sounds section
        sounds_label = wx.StaticText(panel, label="Sounds:")
        right_sizer.Add(sounds_label, 0, wx.TOP | wx.BOTTOM, 10)
        
        sounds_grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=10)
        sounds_grid.AddGrowableCol(0)
        
        self.preview_btns = {}
        for sound_type in ["hour", "half_hour", "quarter_hour", "preview"]:
            label = wx.StaticText(panel, label=f"{sound_type.replace('_', ' ').title()}:")
            sounds_grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
            
            btn = wx.Button(panel, label="▶ Play", size=(70, -1))
            btn.Disable()
            self.preview_btns[sound_type] = btn
            sounds_grid.Add(btn, 0)
        
        right_sizer.Add(sounds_grid, 0, wx.EXPAND)
        
        # Status label
        self.status_label = wx.StaticText(panel, label="")
        self.status_label.SetForegroundColour(wx.Colour(100, 100, 100))
        right_sizer.Add(self.status_label, 0, wx.TOP, 15)
        
        main_sizer.Add(right_sizer, 1, wx.EXPAND | wx.ALL, 10)
        
        # Separator and close button
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        
        close_btn = wx.Button(panel, wx.ID_CLOSE, "Close")
        btn_sizer.Add(close_btn, 0, wx.ALIGN_RIGHT)
        
        # Add to main
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_sizer.Add(main_sizer, 1, wx.EXPAND)
        outer_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        panel.SetSizer(outer_sizer)

    def _bind_events(self) -> None:
        """Bind event handlers."""
        self.pack_list.Bind(wx.EVT_LISTBOX, self._on_pack_selected)
        self.import_btn.Bind(wx.EVT_BUTTON, self._on_import)
        self.delete_btn.Bind(wx.EVT_BUTTON, self._on_delete)
        
        for sound_type, btn in self.preview_btns.items():
            btn.Bind(wx.EVT_BUTTON, lambda evt, st=sound_type: self._on_preview(st))
        
        self.Bind(wx.EVT_BUTTON, self._on_close, id=wx.ID_CLOSE)

    def _refresh_pack_list(self) -> None:
        """Refresh the list of installed clock packs."""
        self.pack_list.Clear()
        
        if not self.app.clock_pack_loader:
            return
        
        # Re-discover packs
        self.app.clock_pack_loader.discover_packs()
        
        # Populate list
        packs = self.app.clock_pack_loader._cache
        for pack_id, pack_info in packs.items():
            # Mark user-installed packs
            user_dir = self.app.paths.user_clocks_dir
            is_user = pack_info.path.is_relative_to(user_dir) if user_dir.exists() else False
            suffix = " (user)" if is_user else " (built-in)"
            
            self.pack_list.Append(f"{pack_info.name}{suffix}", pack_id)
        
        self._clear_details()

    def _clear_details(self) -> None:
        """Clear the details panel."""
        self.name_label.SetLabel("Name: -")
        self.author_label.SetLabel("Author: -")
        self.version_label.SetLabel("Version: -")
        self.description_text.SetValue("")
        self.status_label.SetLabel("")
        
        self.delete_btn.Disable()
        for btn in self.preview_btns.values():
            btn.Disable()
        
        self._selected_pack_id = None

    def _show_pack_details(self, pack_id: str) -> None:
        """Show details for a clock pack."""
        if not self.app.clock_pack_loader:
            return
        
        pack_info = self.app.clock_pack_loader.get_pack(pack_id)
        if not pack_info:
            self._clear_details()
            return
        
        self._selected_pack_id = pack_id
        
        # Update labels
        self.name_label.SetLabel(f"Name: {pack_info.name}")
        self.author_label.SetLabel(f"Author: {pack_info.author}")
        self.version_label.SetLabel(f"Version: {pack_info.version}")
        self.description_text.SetValue(pack_info.description)
        
        # Check if deletable (user-installed only)
        user_dir = self.app.paths.user_clocks_dir
        is_user = pack_info.path.is_relative_to(user_dir) if user_dir.exists() else False
        self.delete_btn.Enable(is_user)
        
        # Enable preview buttons for available sounds
        for sound_type, btn in self.preview_btns.items():
            sound_path = pack_info.get_sound_path(sound_type)
            btn.Enable(sound_path is not None and sound_path.exists())
        
        # Show status
        sounds_count = len([s for s in pack_info.sounds.values() if s])
        self.status_label.SetLabel(f"Location: {pack_info.path}\n{sounds_count} sounds available")

    def _on_pack_selected(self, event: wx.CommandEvent) -> None:
        """Handle pack selection."""
        selection = self.pack_list.GetSelection()
        if selection == wx.NOT_FOUND:
            self._clear_details()
            return
        
        pack_id = self.pack_list.GetClientData(selection)
        self._show_pack_details(pack_id)

    def _on_preview(self, sound_type: str) -> None:
        """Preview a sound from the selected pack."""
        if not self._selected_pack_id or not self.app.clock_pack_loader:
            return
        
        pack_info = self.app.clock_pack_loader.get_pack(self._selected_pack_id)
        if not pack_info:
            return
        
        sound_path = pack_info.get_sound_path(sound_type)
        if sound_path and sound_path.exists() and self.app.audio_player:
            self.app.audio_player.play_sound(str(sound_path))
            self.status_label.SetLabel(f"Playing: {sound_type}")
            logger.info(f"Previewing {sound_type} from {self._selected_pack_id}")

    def _on_import(self, event: wx.CommandEvent) -> None:
        """Import a clock pack from a ZIP file or folder."""
        dlg = wx.FileDialog(
            self,
            message="Import Clock Pack",
            wildcard="Clock Pack (*.zip)|*.zip|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )
        
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        
        source_path = Path(dlg.GetPath())
        dlg.Destroy()
        
        try:
            self._import_pack(source_path)
            self._refresh_pack_list()
            wx.MessageBox(
                "Clock pack imported successfully!",
                "Import Complete",
                wx.OK | wx.ICON_INFORMATION
            )
        except Exception as e:
            logger.exception(f"Failed to import clock pack: {e}")
            wx.MessageBox(
                f"Failed to import clock pack:\n\n{e}",
                "Import Error",
                wx.OK | wx.ICON_ERROR
            )

    def _import_pack(self, source_path: Path) -> None:
        """
        Import a clock pack from a ZIP file.
        
        Args:
            source_path: Path to the ZIP file.
            
        Raises:
            ValueError: If the pack is invalid.
        """
        import zipfile
        import json
        import tempfile
        
        user_dir = self.app.paths.user_clocks_dir
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract to temp first to validate
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            if source_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(source_path, 'r') as zf:
                    zf.extractall(tmp_path)
            else:
                raise ValueError("Only ZIP files are supported")
            
            # Find the manifest
            manifest_path = None
            for p in tmp_path.rglob("clock.json"):
                manifest_path = p
                break
            
            if not manifest_path:
                raise ValueError("No clock.json manifest found in archive")
            
            # Validate manifest
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
            
            if "name" not in manifest:
                raise ValueError("Manifest missing required 'name' field")
            
            # Determine pack folder
            pack_folder = manifest_path.parent
            pack_name = pack_folder.name
            
            # Generate unique ID if needed
            target_dir = user_dir / pack_name
            counter = 1
            while target_dir.exists():
                target_dir = user_dir / f"{pack_name}_{counter}"
                counter += 1
            
            # Copy to user directory
            shutil.copytree(pack_folder, target_dir)
            logger.info(f"Imported clock pack to {target_dir}")

    def _on_delete(self, event: wx.CommandEvent) -> None:
        """Delete the selected clock pack."""
        if not self._selected_pack_id or not self.app.clock_pack_loader:
            return
        
        pack_info = self.app.clock_pack_loader.get_pack(self._selected_pack_id)
        if not pack_info:
            return
        
        # Confirm deletion
        dlg = wx.MessageDialog(
            self,
            f"Delete clock pack '{pack_info.name}'?\n\nThis cannot be undone.",
            "Confirm Delete",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        
        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return
        dlg.Destroy()
        
        # Delete the folder
        try:
            shutil.rmtree(pack_info.path)
            logger.info(f"Deleted clock pack: {pack_info.path}")
            
            # If this was the selected clock, reset to default
            if self.app.selected_clock == self._selected_pack_id:
                self.app.selected_clock = "default"
                self.app.save_config()
            
            self._refresh_pack_list()
            wx.MessageBox(
                "Clock pack deleted.",
                "Deleted",
                wx.OK | wx.ICON_INFORMATION
            )
        except Exception as e:
            logger.exception(f"Failed to delete clock pack: {e}")
            wx.MessageBox(
                f"Failed to delete clock pack:\n\n{e}",
                "Delete Error",
                wx.OK | wx.ICON_ERROR
            )

    def _on_close(self, event: wx.CommandEvent) -> None:
        """Close the dialog."""
        self.EndModal(wx.ID_CLOSE)
