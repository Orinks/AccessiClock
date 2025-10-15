"""
Clock module for AccessiClock.
Handles time retrieval and formatting.
"""
from datetime import datetime


class Clock:
    """Clock class to handle time operations."""

    def __init__(self):
        """Initialize the clock."""
        pass

    def get_time_string(self, format_12h=True):
        """
        Get the current time as a formatted string.
        
        Args:
            format_12h: If True, use 12-hour format. Otherwise use 24-hour format.
            
        Returns:
            str: Formatted time string
        """
        now = datetime.now()
        if format_12h:
            return now.strftime("%I:%M:%S %p")
        else:
            return now.strftime("%H:%M:%S")

    def get_hour(self):
        """
        Get the current hour (0-23).
        
        Returns:
            int: Current hour
        """
        return datetime.now().hour

    def get_minute(self):
        """
        Get the current minute (0-59).
        
        Returns:
            int: Current minute
        """
        return datetime.now().minute

    def get_second(self):
        """
        Get the current second (0-59).
        
        Returns:
            int: Current second
        """
        return datetime.now().second
