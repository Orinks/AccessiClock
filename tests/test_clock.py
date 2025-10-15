"""
Tests for clock functionality.
"""
import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from accessiclock.clock import Clock


class TestClock(unittest.TestCase):
    """Test cases for Clock class."""

    def test_clock_creation(self):
        """Test that Clock can be created."""
        clock = Clock()
        self.assertIsNotNone(clock)

    def test_clock_get_time(self):
        """Test that clock can get current time."""
        clock = Clock()
        time_str = clock.get_time_string()
        self.assertIsInstance(time_str, str)
        self.assertGreater(len(time_str), 0)

    def test_clock_get_hour(self):
        """Test that clock can get current hour."""
        clock = Clock()
        hour = clock.get_hour()
        self.assertIsInstance(hour, int)
        self.assertGreaterEqual(hour, 0)
        self.assertLessEqual(hour, 23)


if __name__ == '__main__':
    unittest.main()
