"""
Utility functions for TMM.

Logging, error handling, and other helper functions.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from colorama import Fore, Style, init as colorama_init


# Initialize colorama for cross-platform color support
colorama_init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console."""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        """Format log record with colors."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None, console: bool = True):
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        console: Whether to log to console
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger('tmm')
    logger.setLevel(numeric_level)
    logger.handlers.clear()

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_formatter = ColoredFormatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = 'tmm') -> logging.Logger:
    """
    Get logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_path(path: Path, base_path: Optional[Path] = None) -> str:
    """
    Format path for display.

    Args:
        path: Path to format
        base_path: Base path to make relative to (optional)

    Returns:
        Formatted path string
    """
    if base_path:
        try:
            return str(path.relative_to(base_path))
        except ValueError:
            pass
    return str(path)


def print_success(message: str):
    """Print success message in green."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message in red."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message in cyan."""
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def print_header(message: str):
    """Print header message."""
    print(f"\n{Style.BRIGHT}{message}{Style.RESET_ALL}")
    print("=" * len(message))


def validate_directory(path: str, name: str = "Directory") -> Path:
    """
    Validate that a path exists and is a directory.

    Args:
        path: Path to validate
        name: Name for error messages

    Returns:
        Path object

    Raises:
        ValueError: If path is invalid
    """
    dir_path = Path(path)

    if not dir_path.exists():
        raise ValueError(f"{name} does not exist: {path}")

    if not dir_path.is_dir():
        raise ValueError(f"{name} is not a directory: {path}")

    return dir_path


def safe_str(value: Any) -> str:
    """
    Safely convert value to string.

    Args:
        value: Value to convert

    Returns:
        String representation
    """
    if value is None:
        return ''
    return str(value)
