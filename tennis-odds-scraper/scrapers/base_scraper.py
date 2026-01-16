"""
Base scraper class providing common functionality for all bookmaker scrapers.
This abstract class defines the interface and shared methods that all specific
bookmaker scrapers should implement or inherit.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from utils import get_logger, load_json_config, retry_on_failure, rate_limiter


class BaseScraper(ABC):
    """
    Abstract base class for bookmaker scrapers.
    Provides common HTTP functionality, rate limiting, and configuration management.
    """
    
    def __init__(self, bookmaker_name: str):
        """
        Initialize base scraper with configuration.
        
        Args:
            bookmaker_name: Name of bookmaker (must exist in bookmakers.json)
        """
        self.bookmaker_name = bookmaker_name
        self.logger = get_logger(f'scraper.{bookmaker_name}')
        
        # Load configurations
        self.config = self._load_bookmaker_config()
        self.rules = self._load_scraping_rules()
        
        # HTTP session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.config.get('headers', {}))
        
        # Rate limiting
        self.rate_limit = self.config.get('rate_limit', 2.0)
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        
        self.logger.info(f"Initialized {bookmaker_name} scraper")
    
    def _load_bookmaker_config(self) -> Dict[str, Any]:
        """
        Load bookmaker-specific configuration.
        
        Returns:
            Configuration dictionary
        """
        config_path = Path('config/bookmakers.json')
        all_configs = load_json_config(str(config_path))
        
        if self.bookmaker_name not in all_configs:
            raise ValueError(f"No configuration found for bookmaker: {self.bookmaker_name}")
        
        return all_configs[self.bookmaker_name]
    
    def _load_scraping_rules(self) -> Dict[str, Any]:
        """
        Load scraping rules (XPath/CSS selectors).
        
        Returns:
            Rules dictionary
        """
        rules_path = Path('config/scraping_rules.json')
        all_rules = load_json_config(str(rules_path))
        
        if self.bookmaker_name not in all_rules:
            self.logger.warning(f"No scraping rules found for {self.bookmaker_name}")
            return {}
        
        return all_rules[self.bookmaker_name]
    
    @retry_on_failure(max_attempts=3, delay=2.0, backoff=2.0)
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from URL with retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None on failure
        """
        try:
            self.logger.debug(f"Fetching: {url}")
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(self.rate_limit)
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            raise
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup.
        
        Args:
            html: HTML content string
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')
    
    def extract_text(self, element, selector: str, method: str = 'css') -> Optional[str]:
        """
        Extract text from element using CSS or XPath selector.
        
        Args:
            element: BeautifulSoup element
            selector: CSS or XPath selector
            method: 'css' or 'xpath'
            
        Returns:
            Extracted text or None
        """
        try:
            if method == 'css':
                found = element.select_one(selector)
                return found.get_text(strip=True) if found else None
            else:
                # XPath would require lxml element, convert if needed
                self.logger.warning("XPath not fully implemented in base class")
                return None
        except Exception as e:
            self.logger.debug(f"Error extracting with selector {selector}: {e}")
            return None
    
    def set_rate_limit(self, seconds: float) -> None:
        """
        Update rate limiting delay.
        
        Args:
            seconds: Seconds to wait between requests
        """
        self.rate_limit = seconds
        self.logger.info(f"Rate limit set to {seconds}s")
    
    def close(self) -> None:
        """
        Close HTTP session and cleanup resources.
        """
        self.session.close()
        self.logger.info(f"Closed {self.bookmaker_name} scraper")
    
    @abstractmethod
    def scrape_tennis_matches(self) -> List[Dict[str, Any]]:
        """
        Scrape tennis matches and odds from bookmaker.
        Must be implemented by subclasses.
        
        Returns:
            List of match dictionaries with format:
            {
                'timestamp': '2025-01-15 10:30:00',
                'tournament': 'ATP Australian Open',
                'player1': 'Djokovic N.',
                'player2': 'Federer R.',
                'odds_player1': 1.50,
                'odds_player2': 2.80,
                'bookmaker': 'oddsportal',
                'match_date': '2025-01-20',
                'match_time': '14:00'
            }
        """
        pass
    
    def validate_match(self, match: Dict[str, Any]) -> bool:
        """
        Validate match data structure.
        
        Args:
            match: Match dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['player1', 'player2', 'odds_player1', 'odds_player2']
        
        for field in required_fields:
            if field not in match or not match[field]:
                self.logger.warning(f"Invalid match data: missing {field}")
                return False
        
        return True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
