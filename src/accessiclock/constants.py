"""Application constants for AccessiClock."""

# Application info
APP_NAME = "AccessiClock"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Orinks"

# Default paths
DEFAULT_CONFIG_FILENAME = "config.json"
DEFAULT_CLOCKS_DIRNAME = "clocks"

# Time formats
TIME_FORMAT_12H = "%I:%M:%S %p"
TIME_FORMAT_24H = "%H:%M:%S"
TIME_FORMAT_12H_NO_SECONDS = "%I:%M %p"
TIME_FORMAT_24H_NO_SECONDS = "%H:%M"

# Clock intervals (in minutes)
INTERVAL_HOURLY = 60
INTERVAL_HALF_HOUR = 30
INTERVAL_QUARTER_HOUR = 15

# Volume levels (percentage)
VOLUME_LEVELS = [0, 25, 50, 75, 100]
DEFAULT_VOLUME = 50

# TTS settings
TTS_RATE_DEFAULT = 150  # Words per minute
TTS_RATE_MIN = 50
TTS_RATE_MAX = 300

# Community clocks repository (future)
COMMUNITY_REPO_OWNER = "orinks"
COMMUNITY_REPO_NAME = "accessiclock-clocks"

# Sound file extensions
SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".ogg", ".flac"]

# Clock pack manifest filename
CLOCK_MANIFEST_FILENAME = "clock.json"

# Required sounds in a clock pack
REQUIRED_CLOCK_SOUNDS = [
    "hour",      # Hourly chime (or hour_1 through hour_12)
    "preview",   # Short preview sound
]

OPTIONAL_CLOCK_SOUNDS = [
    "half_hour",
    "quarter_hour",
    "three_quarter",
    "startup",
    "alarm",
]
