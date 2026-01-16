"""
Helper utilities for the tennis odds scraper.
Common functions used across multiple modules.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from functools import wraps

from utils.logger import get_logger

logger = get_logger(__name__)


def load_json_config(config_path: str) -> Dict[str, Any]:
    """
    Load JSON configuration file.
    
    Args:
        config_path: Path to JSON config file
        
    Returns:
        Dictionary with configuration data
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.debug(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {config_path} - {e}")
        raise


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """
    Save dictionary to JSON file.
    
    Args:
        data: Dictionary to save
        filepath: Output file path
        indent: JSON indentation level
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.debug(f"Saved JSON data to {filepath}")
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        raise


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if not.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on failure with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def rate_limiter(min_interval: float):
    """
    Decorator to enforce minimum time interval between function calls.
    
    Args:
        min_interval: Minimum seconds between calls
        
    Returns:
        Decorated function
    """
    last_called = [0.0]  # Use list to allow modification in nested function
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        
        return wrapper
    return decorator


def parse_odds(odds_str: str) -> Optional[float]:
    """
    Parse odds string to float, handling various formats.
    
    Args:
        odds_str: Odds string (e.g., "1.50", "3/2", "150")
        
    Returns:
        Parsed odds as float, or None if invalid
    """
    if not odds_str or not isinstance(odds_str, str):
        return None
    
    odds_str = odds_str.strip()
    
    try:
        # Decimal format (e.g., "1.50")
        if '.' in odds_str or odds_str.isdigit():
            return float(odds_str)
        
        # Fractional format (e.g., "3/2")
        if '/' in odds_str:
            num, denom = odds_str.split('/')
            return (float(num) / float(denom)) + 1.0
        
        return None
    except (ValueError, ZeroDivisionError):
        logger.warning(f"Could not parse odds: {odds_str}")
        return None


def clean_player_name(name: str) -> str:
    """
    Clean and normalize player name.
    
    Args:
        name: Raw player name
        
    Returns:
        Cleaned player name
    """
    if not name:
        return ""
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Remove common suffixes/indicators
    name = name.replace('(ret)', '').replace('[RET]', '')
    
    return name.strip()


def format_timestamp(dt: Optional[datetime] = None, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object (defaults to now)
        format_str: Output format string
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def calculate_implied_probability(odds: float) -> float:
    """
    Calculate implied probability from decimal odds.
    
    Args:
        odds: Decimal odds
        
    Returns:
        Implied probability as percentage
    """
    if odds <= 0:
        return 0.0
    return (1 / odds) * 100


def calculate_bookmaker_margin(odds1: float, odds2: float) -> float:
    """
    Calculate bookmaker margin (overround) from two odds.
    
    Args:
        odds1: First outcome odds
        odds2: Second outcome odds
        
    Returns:
        Bookmaker margin as percentage
    """
    if odds1 <= 0 or odds2 <= 0:
        return 0.0
    
    prob1 = 1 / odds1
    prob2 = 1 / odds2
    
    return ((prob1 + prob2 - 1) * 100)


def validate_match_data(match: Dict[str, Any]) -> bool:
    """
    Validate that match data contains required fields.
    
    Args:
        match: Match data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['player1', 'player2', 'odds_player1', 'odds_player2']
    
    for field in required_fields:
        if field not in match or not match[field]:
            logger.warning(f"Match data missing required field: {field}")
            return False
    
    return True


class Timer:
    """
    Simple context manager for timing code execution.
    
    Usage:
        with Timer('My operation'):
            # code to time
            pass
    """
    
    def __init__(self, name: str = 'Operation'):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting: {self.name}")
        return self
    
    def __exit__(self, *args):
        elapsed = time.time() - self.start_time
        logger.info(f"Completed: {self.name} in {elapsed:.2f}s")
