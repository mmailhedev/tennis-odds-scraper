"""
Scrapers package for tennis odds collection.
Contains base scraper class and bookmaker-specific implementations.
"""

from .base_scraper import BaseScraper
from .oddsportal_scraper import OddsportalScraper

__all__ = [
    'BaseScraper',
    'OddsportalScraper'
]