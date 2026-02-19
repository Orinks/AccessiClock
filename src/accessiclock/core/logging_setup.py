"""Logging bootstrap for AccessiClock."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(logs_dir: Path, level: int = logging.INFO) -> Path:
    """Configure root logging to file + console and return log file path."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "accessiclock.log"

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return log_file
