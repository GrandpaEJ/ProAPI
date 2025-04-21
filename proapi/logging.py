"""
Logging module for ProAPI framework.

This module provides logging functionality using Loguru.
"""

import os
import sys
from typing import Dict, Any, Optional, Union, List

from loguru import logger

# Default log format
DEFAULT_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Default log level
DEFAULT_LEVEL = "INFO"

# Default log rotation
DEFAULT_ROTATION = "10 MB"

# Default log retention
DEFAULT_RETENTION = "1 week"

# Default log compression
DEFAULT_COMPRESSION = "zip"

def setup_logger(
    level: str = DEFAULT_LEVEL,
    format: Optional[str] = None,
    sink: Union[str, List[Dict[str, Any]], None] = None,
    rotation: str = DEFAULT_ROTATION,
    retention: str = DEFAULT_RETENTION,
    compression: str = DEFAULT_COMPRESSION,
    **kwargs
) -> None:
    """
    Setup the logger with the given configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log format
        sink: Log sink (file path, list of sinks, or None for stderr)
        rotation: Log rotation (e.g. "10 MB", "1 day")
        retention: Log retention (e.g. "1 week", "1 month")
        compression: Log compression (e.g. "zip", "gz")
        **kwargs: Additional logger configuration
    """
    # Use default format if none provided
    if format is None:
        format = DEFAULT_FORMAT

    # Remove default handler
    logger.remove()

    # Add stderr handler with the given format
    logger.add(
        sys.stderr,
        format=format,
        level=level,
        **kwargs
    )

    # Add file handler if sink is a string (file path)
    if isinstance(sink, str):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(sink)), exist_ok=True)

        # Add file handler
        logger.add(
            sink,
            format=format,
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            **kwargs
        )

    # Add multiple handlers if sink is a list
    elif isinstance(sink, list):
        for s in sink:
            s_path = s.get("path")
            s_format = s.get("format", format)
            s_level = s.get("level", level)
            s_rotation = s.get("rotation", rotation)
            s_retention = s.get("retention", retention)
            s_compression = s.get("compression", compression)

            # Create directory if it doesn't exist and path is a string
            if isinstance(s_path, str):
                os.makedirs(os.path.dirname(os.path.abspath(s_path)), exist_ok=True)

            # Add handler
            logger.add(
                s_path,
                format=s_format,
                level=s_level,
                rotation=s_rotation,
                retention=s_retention,
                compression=s_compression,
                **kwargs
            )

def get_logger(name: str = "proapi"):
    """
    Get a logger with the given name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logger.bind(name=name)

# Create default logger
app_logger = get_logger()
