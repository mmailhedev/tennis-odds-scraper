"""
Logging utility for the tennis odds scraper.
Provides consistent logging across all modules with file and console output.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class ScraperLogger:
    """
    Centralized logging configuration for the scraper.
    Creates both file and console handlers with appropriate formatting.
    """
    
    def __init__(self, name: str = 'tennis_scraper', log_dir: str = 'logs'):
        """
        Initialize logger with file and console handlers.
        
        Args:
            name: Logger name (typically module name)
            log_dir: Directory to store log files
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        Configure and return a logger instance with handlers.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        
        # Avoid duplicate handlers if logger already exists
        if logger.handlers:
            return logger
        
        # File handler - daily rotation
        log_filename = self.log_dir / f"scraper_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            Logger instance
        """
        return self.logger
    
    @staticmethod
    def get_scraper_logger(name: str = 'scraper') -> logging.Logger:
        """
        Static method to quickly get a logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        return ScraperLogger(name).get_logger()


# Convenience function for quick logger access
def get_logger(name: str = 'scraper') -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return ScraperLogger.get_scraper_logger(name)
