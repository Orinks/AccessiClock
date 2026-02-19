from pathlib import Path

from accessiclock.core.settings import AppSettings, load_settings, save_settings


def test_load_settings_defaults_for_missing_file(tmp_path: Path):
    settings = load_settings(tmp_path / "missing.json")
    assert settings == AppSettings()


def test_load_settings_clamps_volume(tmp_path: Path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"volume": 999, "clock": "digital"}', encoding="utf-8")

    settings = load_settings(config_file)
    assert settings.volume == 100
    assert settings.clock == "digital"


def test_save_and_load_round_trip(tmp_path: Path):
    config_file = tmp_path / "nested" / "config.json"
    expected = AppSettings(volume=25, clock="westminster", chime_half_hour=True)

    save_settings(config_file, expected)
    loaded = load_settings(config_file)

    assert loaded == expected
