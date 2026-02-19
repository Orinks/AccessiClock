import logging
from pathlib import Path

from accessiclock.core.logging_setup import configure_logging


def test_configure_logging_creates_log_file(tmp_path: Path):
    log_file = configure_logging(tmp_path)

    logging.getLogger("accessiclock.test").info("hello log")

    assert log_file.exists()
    assert "hello log" in log_file.read_text(encoding="utf-8")
