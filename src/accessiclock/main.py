"""Main entry point for AccessiClock."""

import logging
import sys


def main() -> int:
    """Run the AccessiClock application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting AccessiClock")

    try:
        from accessiclock.app import AccessiClockApp

        app = AccessiClockApp()
        app.MainLoop()
        return 0
    except Exception as e:
        logger.exception(f"Failed to start AccessiClock: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
