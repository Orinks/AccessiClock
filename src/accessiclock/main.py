"""Main entry point for AccessiClock."""

from __future__ import annotations

import argparse
import logging
import sys

from .core.logging_setup import configure_logging
from .paths import Paths

logger = logging.getLogger(__name__)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AccessiClock")
    parser.add_argument(
        "--portable",
        action="store_true",
        help="Store config and logs beside the app (portable mode)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the AccessiClock application."""
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    paths = Paths(portable_mode=args.portable)
    log_file = configure_logging(paths.logs_dir)
    logger.info("Starting AccessiClock (portable=%s)", args.portable)
    logger.info("Logging to %s", log_file)

    try:
        from accessiclock.app import AccessiClockApp

        app = AccessiClockApp(portable_mode=args.portable)
        app.MainLoop()
        logger.info("AccessiClock exited cleanly")
        return 0
    except Exception:
        logger.exception("Failed to start AccessiClock")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
