"""Logging utilities for AICLI."""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_logger(
    level: str = "INFO",
    log_file: Optional[str] = None,
    rich_console: Optional[Console] = None
) -> logging.Logger:
    """Set up logging with Rich formatting."""
    
    # Create logger
    logger = logging.getLogger("aicli")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create console handler with Rich formatting
    console_handler = RichHandler(
        console=rich_console or Console(),
        rich_tracebacks=True,
        tracebacks_show_locals=level.upper() == "DEBUG",
        show_path=level.upper() == "DEBUG",
        show_time=False,
    )
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(message)s",
        datefmt="[%X]"
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.DEBUG)  # Always debug level for file
            
            file_formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    
    return logger


class AICliLogger:
    """Custom logger wrapper for AICLI with context."""
    
    def __init__(self, name: str, console: Optional[Console] = None):
        self.logger = logging.getLogger(f"aicli.{name}")
        self.console = console or Console()
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def tool_execution(self, tool_name: str, input_data: str, output: str):
        """Log tool execution."""
        self.debug(f"Tool '{tool_name}' executed with input: {input_data[:100]}...")
        if len(output) > 200:
            self.debug(f"Tool output: {output[:200]}...")
        else:
            self.debug(f"Tool output: {output}")
    
    def llm_call(self, provider: str, model: str, tokens_used: Optional[int] = None):
        """Log LLM API call."""
        message = f"LLM call: {provider}/{model}"
        if tokens_used:
            message += f" ({tokens_used} tokens)"
        self.debug(message)
    
    def session_event(self, event: str, session_name: Optional[str] = None):
        """Log session events."""
        message = f"Session {event}"
        if session_name:
            message += f": {session_name}"
        self.info(message)
    
    def file_operation(self, operation: str, filepath: str, success: bool = True):
        """Log file operations."""
        status = "✓" if success else "✗"
        self.info(f"{status} File {operation}: {filepath}")
    
    def error_with_context(self, error: Exception, context: str = ""):
        """Log error with context."""
        message = f"Error: {str(error)}"
        if context:
            message = f"{context} - {message}"
        self.error(message)