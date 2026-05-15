"""Centralized logger configuration."""
from __future__ import annotations

import logging
import sys

from app.config import settings


def configure_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root = logging.getLogger()
    if root.handlers:
        # already configured
        root.setLevel(level)
        return
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
