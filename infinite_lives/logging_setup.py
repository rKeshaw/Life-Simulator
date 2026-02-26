from __future__ import annotations

import logging
import os
from typing import Any

import structlog


class JsonlFileHandler(logging.Handler):
    def __init__(self, path: str) -> None:
        super().__init__()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(message + "\n")


def configure_logging(session_id: str) -> structlog.stdlib.BoundLogger:
    jsonl_path = f"logs/session_{session_id}.jsonl"
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = []

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(message)s"))

    jsonl = JsonlFileHandler(jsonl_path)
    jsonl.setFormatter(logging.Formatter("%(message)s"))

    root.addHandler(console)
    root.addHandler(jsonl)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", key="timestamp_utc"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger().bind(session_id=session_id)


def log_event(logger: structlog.stdlib.BoundLogger, event_type: str, turn_id: int, payload: dict[str, Any]) -> None:
    logger.info(
        "simulation_event",
        event_type=event_type,
        turn_id=turn_id,
        payload=payload,
    )
