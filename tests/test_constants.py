"""Tests for accessiclock.constants module."""


from accessiclock.constants import (
    APP_NAME,
    APP_VERSION,
    CLOCK_MANIFEST_FILENAME,
    DEFAULT_VOLUME,
    INTERVAL_HALF_HOUR,
    INTERVAL_HOURLY,
    INTERVAL_QUARTER_HOUR,
    REQUIRED_CLOCK_SOUNDS,
    SUPPORTED_AUDIO_FORMATS,
    TIME_FORMAT_12H,
    TIME_FORMAT_24H,
    VOLUME_LEVELS,
)


class TestAppConstants:
    """Test application identity constants."""

    def test_app_name_is_string(self):
        assert isinstance(APP_NAME, str)
        assert len(APP_NAME) > 0

    def test_app_version_format(self):
        """Version should be semantic versioning format."""
        assert isinstance(APP_VERSION, str)
        parts = APP_VERSION.split(".")
        assert len(parts) >= 2  # At least major.minor


class TestTimeFormats:
    """Test time format string constants."""

    def test_12h_format_contains_am_pm(self):
        assert "%p" in TIME_FORMAT_12H or "%P" in TIME_FORMAT_12H

    def test_24h_format_uses_24h_hour(self):
        assert "%H" in TIME_FORMAT_24H

    def test_formats_are_valid_strftime(self):
        """Formats should be usable with strftime."""
        from datetime import datetime
        
        now = datetime.now()
        # Should not raise
        now.strftime(TIME_FORMAT_12H)
        now.strftime(TIME_FORMAT_24H)


class TestIntervals:
    """Test chime interval constants."""

    def test_hourly_is_60_minutes(self):
        assert INTERVAL_HOURLY == 60

    def test_half_hour_is_30_minutes(self):
        assert INTERVAL_HALF_HOUR == 30

    def test_quarter_hour_is_15_minutes(self):
        assert INTERVAL_QUARTER_HOUR == 15


class TestVolumeLevels:
    """Test volume level constants."""

    def test_volume_levels_is_list(self):
        assert isinstance(VOLUME_LEVELS, list)

    def test_volume_levels_start_at_zero(self):
        assert VOLUME_LEVELS[0] == 0

    def test_volume_levels_end_at_100(self):
        assert VOLUME_LEVELS[-1] == 100

    def test_volume_levels_are_ascending(self):
        assert sorted(VOLUME_LEVELS) == VOLUME_LEVELS

    def test_default_volume_in_levels(self):
        assert DEFAULT_VOLUME in VOLUME_LEVELS


class TestClockPackConstants:
    """Test clock pack related constants."""

    def test_manifest_filename(self):
        assert CLOCK_MANIFEST_FILENAME == "clock.json"

    def test_required_sounds_not_empty(self):
        assert len(REQUIRED_CLOCK_SOUNDS) > 0

    def test_hour_sound_required(self):
        assert "hour" in REQUIRED_CLOCK_SOUNDS or any(
            "hour" in s for s in REQUIRED_CLOCK_SOUNDS
        )

    def test_supported_formats_include_wav(self):
        assert ".wav" in SUPPORTED_AUDIO_FORMATS
