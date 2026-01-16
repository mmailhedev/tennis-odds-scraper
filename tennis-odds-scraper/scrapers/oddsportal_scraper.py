"""
Oddsportal scraper implementation.
Scrapes tennis match odds from Oddsportal.com tennis section.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from scrapers.base_scraper import BaseScraper
from utils import clean_player_name, parse_odds, format_timestamp, Timer


class OddsportalScraper(BaseScraper):
    """
    Scraper for Oddsportal tennis betting odds.
    Handles the specific structure and data format of Oddsportal pages.
    """
    
    def __init__(self):
        """Initialize Oddsportal scraper."""
        super().__init__('oddsportal')
        
        # Oddsportal-specific URLs
        self.tennis_url = self.config.get('tennis_url')
        self.base_url = self.config.get('base_url')
    
    def scrape_tennis_matches(self, tournament_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape tennis matches from Oddsportal.
        
        Args:
            tournament_url: Specific tournament URL (optional, uses main tennis page if None)
            
        Returns:
            List of match dictionaries
        """
        with Timer(f'Scraping {self.bookmaker_name}'):
            url = tournament_url if tournament_url else self.tennis_url
            
            try:
                html = self.fetch_page(url)
                if not html:
                    self.logger.error("Failed to fetch page content")
                    return []
                
                soup = self.parse_html(html)
                matches = self._parse_matches(soup)
                
                self.logger.info(f"Successfully scraped {len(matches)} matches")
                return matches
                
            except Exception as e:
                self.logger.error(f"Error scraping matches: {e}")
                return []
    
    def _parse_matches(self, soup) -> List[Dict[str, Any]]:
        """
        Parse match data from BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of match dictionaries
        """
        matches = []
        
        # Note: Oddsportal structure may vary. This is a generic implementation.
        # You may need to adjust selectors based on actual page structure.
        
        # Try to find match containers using CSS selectors
        css_selectors = self.rules.get('css_selectors', {})
        match_rows = soup.select(css_selectors.get('match_row', 'div.eventRow'))
        
        if not match_rows:
            self.logger.warning("No match rows found. Page structure may have changed.")
            return matches
        
        for row in match_rows:
            try:
                match = self._parse_single_match(row)
                if match and self.validate_match(match):
                    matches.append(match)
            except Exception as e:
                self.logger.debug(f"Error parsing match row: {e}")
                continue
        
        return matches
    
    def _parse_single_match(self, row) -> Optional[Dict[str, Any]]:
        """
        Parse a single match row.
        
        Args:
            row: BeautifulSoup element representing a match row
            
        Returns:
            Match dictionary or None
        """
        css_selectors = self.rules.get('css_selectors', {})
        
        # Extract player names
        player1_elem = row.select_one(css_selectors.get('player1', 'div.participant-name'))
        player2_elem = row.select_one(css_selectors.get('player2', 'div.participant-name'))
        
        if not player1_elem or not player2_elem:
            return None
        
        player1 = clean_player_name(player1_elem.get_text(strip=True))
        player2 = clean_player_name(player2_elem.get_text(strip=True))
        
        # Extract odds
        odds1_elem = row.select_one(css_selectors.get('odds1', 'span.odds'))
        odds2_elem = row.select_one(css_selectors.get('odds2', 'span.odds'))
        
        odds1_str = odds1_elem.get_text(strip=True) if odds1_elem else None
        odds2_str = odds2_elem.get_text(strip=True) if odds2_elem else None
        
        odds1 = parse_odds(odds1_str)
        odds2 = parse_odds(odds2_str)
        
        if not odds1 or not odds2:
            return None
        
        # Extract tournament (if available)
        tournament = self._extract_tournament(row)
        
        # Extract match time/date (if available)
        match_time, match_date = self._extract_match_datetime(row)
        
        return {
            'timestamp': format_timestamp(),
            'tournament': tournament or 'Unknown',
            'player1': player1,
            'player2': player2,
            'odds_player1': odds1,
            'odds_player2': odds2,
            'bookmaker': self.bookmaker_name,
            'match_date': match_date,
            'match_time': match_time,
            'url': self._extract_match_url(row)
        }
    
    def _extract_tournament(self, row) -> Optional[str]:
        """
        Extract tournament name from match row.
        
        Args:
            row: BeautifulSoup element
            
        Returns:
            Tournament name or None
        """
        try:
            css_selectors = self.rules.get('css_selectors', {})
            tournament_elem = row.select_one(css_selectors.get('tournament', 'div.event__title'))
            
            if tournament_elem:
                return tournament_elem.get_text(strip=True)
        except Exception as e:
            self.logger.debug(f"Could not extract tournament: {e}")
        
        return None
    
    def _extract_match_datetime(self, row) -> tuple:
        """
        Extract match date and time from row.
        
        Args:
            row: BeautifulSoup element
            
        Returns:
            Tuple of (time, date) as strings
        """
        match_time = None
        match_date = None
        
        try:
            # Look for time element
            time_elem = row.select_one('.event__time, .time')
            if time_elem:
                match_time = time_elem.get_text(strip=True)
            
            # Look for date element
            date_elem = row.select_one('.event__date, .date')
            if date_elem:
                match_date = date_elem.get_text(strip=True)
        except Exception as e:
            self.logger.debug(f"Could not extract datetime: {e}")
        
        return match_time, match_date
    
    def _extract_match_url(self, row) -> Optional[str]:
        """
        Extract full match URL from row.
        
        Args:
            row: BeautifulSoup element
            
        Returns:
            Full match URL or None
        """
        try:
            link = row.select_one('a[href]')
            if link:
                href = link.get('href')
                if href.startswith('/'):
                    return f"{self.base_url}{href}"
                return href
        except Exception as e:
            self.logger.debug(f"Could not extract match URL: {e}")
        
        return None
    
    def scrape_specific_tournament(self, tournament_name: str) -> List[Dict[str, Any]]:
        """
        Scrape matches from a specific tournament.
        
        Args:
            tournament_name: Name or URL path of tournament
            
        Returns:
            List of match dictionaries
        """
        # Build tournament URL
        if tournament_name.startswith('http'):
            url = tournament_name
        else:
            url = f"{self.tennis_url}{tournament_name}/"
        
        self.logger.info(f"Scraping tournament: {tournament_name}")
        return self.scrape_tennis_matches(url)
    
    def get_available_tournaments(self) -> List[Dict[str, str]]:
        """
        Get list of available tennis tournaments.
        
        Returns:
            List of dictionaries with tournament info
        """
        try:
            html = self.fetch_page(self.tennis_url)
            if not html:
                return []
            
            soup = self.parse_html(html)
            tournaments = []
            
            # Find tournament links
            tournament_links = soup.select('a.tournament-link, a[href*="tennis"]')
            
            for link in tournament_links:
                name = link.get_text(strip=True)
                href = link.get('href')
                
                if name and href:
                    tournaments.append({
                        'name': name,
                        'url': f"{self.base_url}{href}" if href.startswith('/') else href
                    })
            
            self.logger.info(f"Found {len(tournaments)} tournaments")
            return tournaments
            
        except Exception as e:
            self.logger.error(f"Error getting tournaments: {e}")
            return []


# Example usage
if __name__ == '__main__':
    scraper = OddsportalScraper()
    
    try:
        # Scrape matches
        matches = scraper.scrape_tennis_matches()
        
        print(f"\nScraped {len(matches)} matches:")
        for match in matches[:5]:  # Show first 5
            print(f"\n{match['player1']} vs {match['player2']}")
            print(f"  Odds: {match['odds_player1']} - {match['odds_player2']}")
            print(f"  Tournament: {match['tournament']}")
    
    finally:
        scraper.close()
