"""Tests for accessiclock.services.clock_service module.

TDD: These tests are written before the implementation.
"""

from datetime import datetime, time
from unittest.mock import MagicMock, patch

import pytest


class TestChimeScheduling:
    """Test chime scheduling logic."""

    def test_should_chime_hourly_at_top_of_hour(self):
        """Should trigger hourly chime at XX:00:00."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = True
        
        # 3:00:00 PM - should chime
        test_time = time(15, 0, 0)
        assert service.should_chime_now(test_time) == "hour"

    def test_should_not_chime_hourly_when_disabled(self):
        """Should not chime when hourly chimes disabled."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = False
        
        test_time = time(15, 0, 0)
        assert service.should_chime_now(test_time) is None

    def test_should_chime_half_hour(self):
        """Should trigger half-hour chime at XX:30:00."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_half_hour = True
        
        test_time = time(15, 30, 0)
        assert service.should_chime_now(test_time) == "half_hour"

    def test_should_chime_quarter_hour_at_15(self):
        """Should trigger quarter-hour chime at XX:15:00."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_quarter_hour = True
        
        test_time = time(15, 15, 0)
        assert service.should_chime_now(test_time) == "quarter_hour"

    def test_should_chime_quarter_hour_at_45(self):
        """Should trigger quarter-hour chime at XX:45:00."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_quarter_hour = True
        
        test_time = time(15, 45, 0)
        assert service.should_chime_now(test_time) == "quarter_hour"

    def test_should_not_chime_at_random_time(self):
        """Should not chime at non-interval times."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = True
        service.chime_half_hour = True
        service.chime_quarter_hour = True
        
        test_time = time(15, 23, 45)  # Random time
        assert service.should_chime_now(test_time) is None

    def test_hourly_takes_precedence_over_quarter(self):
        """Hourly chime should take precedence at XX:00."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = True
        service.chime_quarter_hour = True  # Also enabled
        
        test_time = time(15, 0, 0)
        # Should return hour, not quarter_hour
        assert service.should_chime_now(test_time) == "hour"

    def test_half_hour_takes_precedence_over_quarter(self):
        """Half-hour chime should take precedence at XX:30."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_half_hour = True
        service.chime_quarter_hour = True  # Also enabled
        
        test_time = time(15, 30, 0)
        assert service.should_chime_now(test_time) == "half_hour"


class TestChimeTracking:
    """Test that chimes don't repeat within the same minute."""

    def test_chime_not_repeated_same_minute(self):
        """Should not chime twice in the same minute."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = True
        
        test_time = time(15, 0, 0)
        
        # First check - should chime
        assert service.should_chime_now(test_time) == "hour"
        service.mark_chimed(test_time)
        
        # Second check same minute - should not chime
        test_time_later = time(15, 0, 30)
        assert service.should_chime_now(test_time_later) is None

    def test_chime_allowed_next_interval(self):
        """Should chime again at next interval."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = True
        
        # Chime at 3:00
        service.mark_chimed(time(15, 0, 0))
        
        # Should chime at 4:00
        assert service.should_chime_now(time(16, 0, 0)) == "hour"


class TestGetCurrentHour:
    """Test hour extraction for hourly chimes."""

    def test_get_hour_12h_format(self):
        """Should return hour in 12-hour format."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        
        assert service.get_hour_12h(time(0, 0)) == 12   # Midnight
        assert service.get_hour_12h(time(1, 0)) == 1
        assert service.get_hour_12h(time(12, 0)) == 12  # Noon
        assert service.get_hour_12h(time(13, 0)) == 1
        assert service.get_hour_12h(time(23, 0)) == 11


class TestQuietHours:
    """Test quiet hours feature."""

    def test_no_chime_during_quiet_hours(self):
        """Should not chime during configured quiet hours."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = True
        service.quiet_start = time(23, 0)  # 11 PM
        service.quiet_end = time(7, 0)     # 7 AM
        
        # 2 AM - within quiet hours
        assert service.should_chime_now(time(2, 0, 0)) is None
        
        # Midnight - within quiet hours
        assert service.should_chime_now(time(0, 0, 0)) is None

    def test_chime_outside_quiet_hours(self):
        """Should chime outside quiet hours."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = True
        service.quiet_start = time(23, 0)
        service.quiet_end = time(7, 0)
        
        # 10 AM - outside quiet hours
        assert service.should_chime_now(time(10, 0, 0)) == "hour"

    def test_quiet_hours_disabled_by_default(self):
        """Quiet hours should be disabled by default."""
        from accessiclock.services.clock_service import ClockService
        
        service = ClockService()
        service.chime_hourly = True
        
        # Should chime at any hour when quiet hours disabled
        assert service.should_chime_now(time(3, 0, 0)) == "hour"
