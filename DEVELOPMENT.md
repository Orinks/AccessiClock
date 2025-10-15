# AccessiClock Development Guide

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Orinks/AccessiClock.git
   cd AccessiClock
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running Tests

The project follows test-driven development (TDD) practices.

### Run all tests:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run a specific test file:
```bash
python -m unittest tests.test_clock -v
```

### Run with pytest (if installed):
```bash
pytest
pytest --cov=accessiclock --cov-report=html
```

## Code Structure

- **src/accessiclock/**: Main application code
  - `app.py`: Main Toga application and UI
  - `clock.py`: Core clock functionality
  - `tts.py`: Text-to-Speech integration
  - `soundpack.py`: Soundpack management system
  - `audio.py`: Audio playback using sound_lib

- **tests/**: Test suite
  - All test files follow the `test_*.py` naming convention
  - Uses Python's unittest framework

## Adding New Features

1. **Write tests first** (TDD approach):
   - Create test file in `tests/` directory
   - Write failing tests for the new feature

2. **Implement the feature**:
   - Add implementation in appropriate module
   - Ensure tests pass

3. **Update documentation**:
   - Update README.md if needed
   - Add docstrings to new functions/classes

## Building with Briefcase

### Create scaffold:
```bash
briefcase create
```

### Build application:
```bash
briefcase build
```

### Run in development mode:
```bash
briefcase dev
```

### Package for distribution:
```bash
briefcase package
```

## Optional Dependencies

The application handles missing optional dependencies gracefully:

- **toga**: GUI framework (required for UI, optional for testing)
- **pyttsx3**: TTS engine (optional, app will notify if unavailable)
- **sound_lib**: Audio playback (optional, app will notify if unavailable)

This design allows running tests without all dependencies installed.

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and single-purpose

## Accessibility Guidelines

When adding UI features:
- Ensure all interactive elements are keyboard accessible
- Provide text alternatives for visual elements
- Test with screen readers when possible
- Use clear, descriptive labels
- Maintain good color contrast ratios
