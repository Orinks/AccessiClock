"""
Tests for AccessiClock application.
"""
import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from accessiclock.app import AccessiClock


class TestAccessiClockApp(unittest.TestCase):
    """Test cases for AccessiClock app."""

    def test_app_creation(self):
        """Test that the AccessiClock app can be created."""
        app = AccessiClock('AccessiClock', 'com.orinks.accessiclock')
        self.assertEqual(app.formal_name, "AccessiClock")
        self.assertEqual(app.app_id, "com.orinks.accessiclock")

    def test_app_startup(self):
        """Test that the app startup method returns the main box."""
        app = AccessiClock('AccessiClock', 'com.orinks.accessiclock')
        main_box = app.startup()
        self.assertIsNotNone(main_box)


if __name__ == '__main__':
    unittest.main()
