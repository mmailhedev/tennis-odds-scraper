"""
The Odds API Scraper
Fetches real-time tennis odds from The Odds API
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TheOddsAPIScraper:
    """
    Scraper for The Odds API - real tennis betting odds
    
    Features:
    - Real-time ATP & WTA match odds
    - Multiple bookmakers (200+)
    - Match winner, spreads, totals markets
    - 500 free requests/month
    
    API Docs: https://the-odds-api.com/liveapi/guides/v4/
    """
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    # Available tennis sports
    SPORTS = {
        'ATP': 'tennis_atp',
        'WTA': 'tennis_wta',
        'ATP Challenger': 'tennis_atp_australian_open',  # During tournaments
    }
    
    def __init__(self, api_key: str):
        """
        Initialize The Odds API scraper
        
        Args:
            api_key: Your The Odds API key (get free at https://the-odds-api.com)
        """
        self.api_key = api_key
        self.remaining_requests = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TennisOddsScraper/1.0'
        })
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with error handling
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response
            
        Raises:
            Exception: If API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params['apiKey'] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            # Track remaining requests
            self.remaining_requests = response.headers.get('x-requests-remaining')
            logger.info(f"API requests remaining: {self.remaining_requests}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"The Odds API error: {str(e)}")
    
    def get_tennis_odds(
        self, 
        sport: str = 'tennis_atp',
        regions: str = 'us,eu',
        markets: str = 'h2h',
        odds_format: str = 'decimal'
    ) -> List[Dict]:
        """
        Fetch tennis odds for a specific sport
        
        Args:
            sport: Sport key (tennis_atp, tennis_wta, etc.)
            regions: Bookmaker regions (us, eu, uk, au)
            markets: Betting markets (h2h, spreads, totals)
            odds_format: Odds format (decimal, american)
            
        Returns:
            List of matches with odds from various bookmakers
        """
        endpoint = f"sports/{sport}/odds"
        
        params = {
            'regions': regions,
            'markets': markets,
            'oddsFormat': odds_format
        }
        
        logger.info(f"Fetching {sport} odds from The Odds API...")
        
        return self._make_request(endpoint, params)
    
    def scrape_tennis_matches(
        self,
        include_atp: bool = True,
        include_wta: bool = True
    ) -> List[Dict]:
        """
        Scrape tennis matches and convert to standard format
        (Compatible with existing dashboard/API structure)
        
        Args:
            include_atp: Include ATP matches
            include_wta: Include WTA matches
            
        Returns:
            List of matches in standardized format
        """
        all_matches = []
        
        try:
            # Fetch ATP matches
            if include_atp:
                atp_raw = self.get_tennis_odds('tennis_atp')
                atp_matches = self._transform_matches(atp_raw, 'ATP')
                all_matches.extend(atp_matches)
                logger.info(f"Fetched {len(atp_matches)} ATP matches")
            
            # Fetch WTA matches
            if include_wta:
                wta_raw = self.get_tennis_odds('tennis_wta')
                wta_matches = self._transform_matches(wta_raw, 'WTA')
                all_matches.extend(wta_matches)
                logger.info(f"Fetched {len(wta_matches)} WTA matches")
            
            logger.info(f"Total matches scraped: {len(all_matches)}")
            
            return all_matches
            
        except Exception as e:
            logger.error(f"Failed to scrape matches: {e}")
            raise
    
    def _transform_matches(self, api_matches: List[Dict], tour: str) -> List[Dict]:
        """
        Transform The Odds API format to our standard format
        
        Args:
            api_matches: Raw matches from API
            tour: Tournament tour (ATP/WTA)
            
        Returns:
            List of matches in standard format
        """
        transformed = []
        
        for match in api_matches:
            try:
                # Extract players
                player1 = match['home_team']
                player2 = match['away_team']
                
                # Get best odds from all bookmakers
                odds_data = self._extract_best_odds(match.get('bookmakers', []))
                
                # Build standard match dict
                match_dict = {
                    'player1': player1,
                    'player2': player2,
                    'tournament': match.get('sport_title', f'{tour} Tournament'),
                    'match_time': self._parse_datetime(match.get('commence_time')),
                    'odds_player1': odds_data['odds_player1'],
                    'odds_player2': odds_data['odds_player2'],
                    'bookmaker': odds_data['bookmaker'],
                    'bookmaker_margin': self._calculate_margin(
                        odds_data['odds_player1'],
                        odds_data['odds_player2']
                    ),
                    'url': f"https://the-odds-api.com",  # Generic URL
                    'source': 'The Odds API (Live)',
                    'bookmakers_count': len(match.get('bookmakers', [])),
                    'api_match_id': match.get('id'),
                    'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                transformed.append(match_dict)
                
            except Exception as e:
                logger.warning(f"Failed to transform match: {e}")
                continue
        
        return transformed
    
    def _extract_best_odds(self, bookmakers: List[Dict]) -> Dict:
        """
        Extract best odds across all bookmakers
        
        Args:
            bookmakers: List of bookmaker data
            
        Returns:
            Dict with best odds and bookmaker name
        """
        best_odds = {
            'odds_player1': 0,
            'odds_player2': 0,
            'bookmaker': 'Multiple'
        }
        
        best_bookmaker_name = None
        
        for bookmaker in bookmakers:
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':  # Match winner market
                    outcomes = market.get('outcomes', [])
                    
                    if len(outcomes) >= 2:
                        # Assume first outcome is player1, second is player2
                        odds1 = outcomes[0].get('price', 0)
                        odds2 = outcomes[1].get('price', 0)
                        
                        # Track highest odds for better value
                        if odds1 > best_odds['odds_player1']:
                            best_odds['odds_player1'] = odds1
                            best_bookmaker_name = bookmaker.get('title')
                        
                        if odds2 > best_odds['odds_player2']:
                            best_odds['odds_player2'] = odds2
                            if not best_bookmaker_name:
                                best_bookmaker_name = bookmaker.get('title')
        
        if best_bookmaker_name:
            best_odds['bookmaker'] = best_bookmaker_name
        
        return best_odds
    
    def _calculate_margin(self, odds1: float, odds2: float) -> float:
        """
        Calculate bookmaker margin (overround)
        
        Args:
            odds1: Odds for player 1
            odds2: Odds for player 2
            
        Returns:
            Margin percentage
        """
        if odds1 <= 0 or odds2 <= 0:
            return 0.0
        
        implied_prob_sum = (1 / odds1) + (1 / odds2)
        margin = (implied_prob_sum - 1) * 100
        
        return round(margin, 2)
    
    def _parse_datetime(self, iso_datetime: str) -> str:
        """
        Parse ISO datetime to readable format
        
        Args:
            iso_datetime: ISO format datetime string
            
        Returns:
            Formatted datetime string
        """
        try:
            dt = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return 'TBD'
    
    def get_api_status(self) -> Dict:
        """
        Get API usage status
        
        Returns:
            Dict with API status info
        """
        return {
            'requests_remaining': self.remaining_requests,
            'free_tier_limit': 500,
            'status': 'active' if self.remaining_requests else 'unknown'
        }


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Get API key from environment
    api_key = os.getenv('ODDS_API_KEY')
    
    if not api_key:
        print("❌ Error: ODDS_API_KEY not found in environment variables")
        print("Please create a .env file with: ODDS_API_KEY=your_key_here")
        exit(1)
    
    # Test scraper
    print("🎾 Testing The Odds API Scraper...")
    print("=" * 50)
    
    with TheOddsAPIScraper(api_key) as scraper:
        try:
            matches = scraper.scrape_tennis_matches()
            
            print(f"\n✅ Successfully scraped {len(matches)} matches")
            print(f"📊 API requests remaining: {scraper.remaining_requests}")
            
            if matches:
                print("\n📋 Sample match:")
                sample = matches[0]
                print(f"  {sample['player1']} vs {sample['player2']}")
                print(f"  Tournament: {sample['tournament']}")
                print(f"  Odds: {sample['odds_player1']} / {sample['odds_player2']}")
                print(f"  Bookmaker: {sample['bookmaker']}")
                print(f"  Margin: {sample['bookmaker_margin']}%")
            else:
                print("\n⚠️  No live matches found (may be off-season)")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
