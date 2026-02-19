from accessiclock.core.shortcuts import build_shortcut_help, default_shortcuts


def test_default_shortcuts_contains_core_actions():
    names = [shortcut.action for shortcut in default_shortcuts()]
    assert "Test chime" in names
    assert "Announce current time" in names


def test_build_shortcut_help_is_readable_text():
    help_text = build_shortcut_help()
    assert "F5" in help_text
    assert "Ctrl+," in help_text
    assert "|" in help_text
