"""
Centralized logging configuration for ChroniSense application.

This module provides consistent logging setup across all modules with:
- Configurable log levels via environment variable
- Consistent format with timestamp, level, module, and message
- Support for both console and file logging
- Human-readable output for debugging
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(app=None):
    """
    Configure logging for the application.
    
    Args:
        app: Flask application instance (optional)
        
    Returns:
        Logger instance
    """
    # Get log level from environment variable, default to INFO
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Define log format with timestamp, level, module name, function, and message
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Console handler - always enabled
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # File handler - rotating log files
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'chronisense.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Set logging level for third-party libraries to WARNING to reduce noise
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    
    # Log the configuration
    root_logger.info(f"Logging configured with level: {log_level_str}")
    root_logger.info(f"Log file location: {os.path.join(log_dir, 'chronisense.log')}")
    
    if app:
        app.logger.info("Application logger initialized")
    
    return root_logger


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
