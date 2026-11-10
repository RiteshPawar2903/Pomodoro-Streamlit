"""
Structured Logging Module for Zen Pomodoro Clock.
Conforms to IEEE Std 730 Software Quality Assurance and OpenTelemetry structured logging guidelines.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from config import CONFIG


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects for centralized log ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "env": CONFIG.env,
        }

        if hasattr(record, "metadata") and isinstance(record.metadata, dict):
            log_obj["metadata"] = record.metadata

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def get_logger(name: str) -> logging.Logger:
    """Return a configured structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        log_level = getattr(logging, CONFIG.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)
    return logger
