"""Log Message Factory."""

import logging
from datetime import datetime, timezone
from typing import ClassVar

from adb_auto_player.ipc import LogLevel, LogMessage

from .traceback_helper import TracebackHelper


class LogMessageFactory:
    """LogMessageFactory."""

    _LEVEL_MAPPING: ClassVar[dict[int, str]] = {
        logging.DEBUG: LogLevel.DEBUG,
        logging.INFO: LogLevel.INFO,
        logging.WARNING: LogLevel.WARNING,
        logging.ERROR: LogLevel.ERROR,
        logging.CRITICAL: LogLevel.FATAL,
    }

    @staticmethod
    def create_log_message(
        record: logging.LogRecord,
        message: str | None = None,
        html_class: str | None = None,
        profile_index: int | None = None,
    ) -> LogMessage:
        """Create a new LogMessage from a log record."""
        source_info = TracebackHelper.extract_source_info(record)
        return LogMessage(
            level=LogMessageFactory._LEVEL_MAPPING.get(record.levelno, LogLevel.DEBUG),
            message=message if message else record.getMessage(),
            timestamp=datetime.now().astimezone(timezone.utc),
            source_file=source_info.source_file,
            function_name=source_info.function_name,
            line_number=source_info.line_number,
            html_class=html_class,
            profile_index=profile_index,
        )
