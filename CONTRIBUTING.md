# Contributing to Accessible Talking Clock

Thank you for your interest in contributing to this project! This application is designed with accessibility as a core requirement.

## Accessibility First

All contributions must maintain or improve accessibility:

- ✅ All UI elements must be keyboard accessible
- ✅ Tab order must be logical and complete
- ✅ Screen readers (NVDA, JAWS, Windows Narrator) must announce all elements properly
- ✅ Focus indicators must be visible and clear
- ✅ Status updates must be announced to assistive technology

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `uv venv`
3. Activate: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
4. Install dependencies: `uv pip install briefcase toga sound_lib ipykernel matplotlib`
5. Run the app: `cd accessibletalkingclock && python -m briefcase dev`

## Testing Accessibility

Before submitting a pull request:

1. Install and start NVDA screen reader
2. Launch the application
3. Navigate using only the Tab key
4. Verify all controls are announced properly
5. Test button activation with Enter/Space keys
6. Ensure status messages are read by the screen reader

## Code Style

- Follow PEP 8 conventions
- Use meaningful variable names
- Add docstrings to functions and classes
- Include logging for user interactions
- Maintain existing code patterns

## Commit Messages

- Use clear, descriptive commit messages
- Reference issue numbers when applicable
- Include "Co-Authored-By: Memex <noreply@memex.tech>" for AI assistance

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Test accessibility thoroughly
4. Update documentation if needed
5. Submit a pull request with detailed description
6. Wait for review and address feedback

## Questions?

Open an issue for any questions or concerns about accessibility or development.
