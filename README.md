# AccessiClock

An accessible clock application for the blind and visually impaired, built with Python and the Toga framework.

## Features

- **Accessible UI**: Built with the BeeWare Toga framework for cross-platform accessibility
- **Text-to-Speech**: Announces time using TTS (Text-to-Speech) integration via pyttsx3
- **Customizable Soundpacks**: Support for custom sound collections for clock chimes
- **Concurrent Audio**: Uses sound_lib for playing multiple audio streams simultaneously
- **12/24 Hour Format**: Toggle between 12-hour and 24-hour time formats
- **Test-Driven Development**: Comprehensive test suite ensuring reliability

## Requirements

- Python 3.8 or higher
- toga >= 0.4.0
- sound_lib >= 0.0.10
- pyttsx3 >= 2.90
- briefcase >= 0.3.0 (for building distributable packages)

## Installation

### For Development

1. Clone the repository:
```bash
git clone https://github.com/Orinks/AccessiClock.git
cd AccessiClock
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### For Testing

Install test dependencies:
```bash
pip install pytest pytest-cov toga-dummy
```

## Running the Application

### Using Python directly:
```bash
python -m src.accessiclock.app
```

### Using Briefcase (for packaged apps):
```bash
briefcase dev
```

## Running Tests

The project uses test-driven development with comprehensive test coverage.

### Using unittest (built-in):
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Using pytest (if installed):
```bash
pytest
```

## Project Structure

```
AccessiClock/
├── src/
│   └── accessiclock/
│       ├── __init__.py
│       ├── app.py          # Main Toga application
│       ├── clock.py        # Clock functionality
│       ├── tts.py          # Text-to-Speech integration
│       └── soundpack.py    # Soundpack management
├── tests/
│   ├── __init__.py
│   ├── test_app.py         # App tests
│   ├── test_clock.py       # Clock tests
│   ├── test_tts.py         # TTS tests
│   └── test_soundpack.py   # Soundpack tests
├── soundpacks/
│   └── default/            # Default soundpack directory
├── pyproject.toml          # Project configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Soundpacks

Soundpacks are collections of audio files used for clock chimes. They are stored in the `soundpacks/` directory.

### Creating a Custom Soundpack

1. Create a new directory in `soundpacks/` with your soundpack name
2. Add audio files (.wav, .mp3, or .ogg) to the directory
3. The soundpack will be automatically detected by the application

Example:
```
soundpacks/
├── default/
│   ├── chime.wav
│   └── tick.wav
└── mysoundpack/
    ├── custom_chime.wav
    └── custom_tick.wav
```

## Accessibility Features

- **Screen Reader Compatible**: Built with accessibility in mind using Toga
- **Keyboard Navigation**: Full keyboard support for all features
- **High Contrast**: Clear, readable interface
- **TTS Announcements**: Time announcements via text-to-speech

## Building Distributable Packages

Use Briefcase to build distributable packages for different platforms:

```bash
# Create the application scaffold
briefcase create

# Build the application
briefcase build

# Package the application
briefcase package

# Run the packaged application
briefcase run
```

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a pull request.

## License

MIT License - See LICENSE file for details

## Author

Orinks

## Acknowledgments

- Built with [BeeWare](https://beeware.org/) Toga framework
- Uses [pyttsx3](https://github.com/nateshmbhat/pyttsx3) for TTS
- Uses [sound_lib](https://github.com/Sammy1Am/sound_lib) for concurrent audio
