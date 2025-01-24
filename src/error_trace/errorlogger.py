import os
import sys
import time
import traceback
import inspect
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
from enum import Enum
from src.config.appconfig import env_config


class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Logger:
    """
    A comprehensive logger that handles info, warning, and error logging with detailed information.
    """

    def __init__(self, log_dir: str = "src/logs"):
        """
        Initialize the logger with a specified log directory.

        Args:
            log_dir (str): Directory path where log files will be stored
        """
        self.log_dir = Path(log_dir)
        self.log_files = {
            LogLevel.INFO: self.log_dir / "info.log",
            LogLevel.WARNING: self.log_dir / "warning.log",
            LogLevel.ERROR: self.log_dir / "error.log",
        }
        self._ensure_log_directory()

    def _ensure_log_directory(self) -> None:
        """Create the log directory if it doesn't exist."""
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_caller_info(self, tb=None) -> tuple[str, str]:
        """
        Get information about the calling function and its parent.

        Args:
            tb: Optional traceback object for error logging

        Returns:
            tuple: (current_function_name, parent_function_name)
        """
        if tb:
            # For error logging, use traceback
            tb_list = traceback.extract_tb(tb)
            error_frame = tb_list[-1]
            error_function = error_frame.name
            parent_function = tb_list[-2].name if len(tb_list) > 1 else "Unknown"
        else:
            # For info and warning, use inspect
            stack = inspect.stack()
            error_function = stack[2].function if len(stack) > 2 else "Unknown"
            parent_function = stack[3].function if len(stack) > 3 else "Unknown"

        return error_function, parent_function

    def _format_message(
        self,
        level: LogLevel,
        message: str,
        error: Optional[Exception] = None,
        additional_info: Optional[dict] = None,
    ) -> str:
        """
        Format the log message with relevant information.

        Args:
            level: LogLevel enum indicating the type of log
            message: The main message to log
            error: Optional exception object for error logging
            additional_info: Optional dictionary with additional context

        Returns:
            str: Formatted log message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_function, parent_function = self._get_caller_info(
            sys.exc_info()[2] if error else None
        )

        log_msg = [
            "=" * 80,
            f"TIMESTAMP: {timestamp}",
            f"LEVEL: {level.value}",
            f"FUNCTION: {current_function}",
            f"PARENT FUNCTION: {parent_function}",
            "-" * 80,
            f"MESSAGE: {message}",
        ]

        if error:
            log_msg.extend(
                [
                    f"ERROR TYPE: {error.__class__.__name__}",
                    f"ERROR MESSAGE: {str(error)}",
                    "-" * 80,
                    "FULL TRACEBACK:",
                    traceback.format_exc(),
                ]
            )

        # Add additional context if provided
        default_context = {
            "ai_engineer": "ayo",
            "environment": env_config.env,
        }
        
        # Merge default context with provided additional info
        if additional_info:
            default_context.update(additional_info)

        log_msg.extend(
            [
                "-" * 80,
                "CONTEXT:",
                "\n".join(f"{k}: {v}" for k, v in default_context.items()),
            ]
        )

        log_msg.append("=" * 80 + "\n")
        return "\n".join(log_msg)

    def _write_log(self, level: LogLevel, message: str) -> None:
        """Write the message to the appropriate log file."""
        try:
            with open(self.log_files[level], "a", encoding="utf-8") as f:
                f.write(message)
        except Exception as e:
            print(f"Logging failed: {str(e)}", file=sys.stderr)

    def info(self, message: str, additional_info: Optional[dict] = None) -> None:
        """
        Log an informational message.

        Args:
            message: The message to log
            additional_info: Optional dictionary with additional context
        """
        log_message = self._format_message(LogLevel.INFO, message, additional_info=additional_info)
        self._write_log(LogLevel.INFO, log_message)

    def warning(self, message: str, additional_info: Optional[dict] = None) -> None:
        """
        Log a warning message.

        Args:
            message: The warning message to log
            additional_info: Optional dictionary with additional context
        """
        log_message = self._format_message(LogLevel.WARNING, message, additional_info=additional_info)
        self._write_log(LogLevel.WARNING, log_message)

    def error(
        self,
        error: Exception,
        additional_info: Optional[dict] = None,
    ) -> None:
        """
        Log an error with full stack trace and context information.

        Args:
            error: The exception to log
            additional_info: Optional dictionary with additional context
        """
        log_message = self._format_message(
            LogLevel.ERROR, "An error occurred", error, additional_info
        )
        self._write_log(LogLevel.ERROR, log_message)

    def clear_logs(self, level: Optional[LogLevel] = None) -> None:
        """
        Clear log files.

        Args:
            level: Optional LogLevel to clear specific log file. If None, clears all logs.
        """
        try:
            if level:
                with open(self.log_files[level], "w", encoding="utf-8") as f:
                    f.write("")
            else:
                for log_file in self.log_files.values():
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write("")
        except Exception as e:
            print(f"Failed to clear logs: {str(e)}", file=sys.stderr)

    def view_logs(self,log_type: str)->str:
        """
        Read and return the contents of the specified log file in plain text.

        Args:
            log_type (str): The type of log to view (info, warning, error).

        Returns:
            PlainTextResponse: The contents of the log file or an error message.
        """

        match log_type.lower():
            case "error":
                log_file = self.log_files.get(LogLevel.ERROR)
            case "info":
                log_file = self.log_files.get(LogLevel.INFO)
            case "warning":
                log_file = self.log_files.get(LogLevel.WARNING)
            case _:
                log_file = None

        if not log_file:
            return f"Invalid log type: {log_type}. Valid types are: info, warning, error."

        try:
            if not os.path.exists(log_file):
                return f"Log file '{log_type}' not found."

            with open(log_file, "r", encoding="utf-8") as file:
                logs = file.read()

            return logs or "Log file is empty."
        except Exception as e:
            return f"Failed to read log file: {e}"
        
# Initialize the logger
system_logger = Logger()