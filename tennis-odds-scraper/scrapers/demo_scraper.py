"""
Demo scraper with realistic fake data for portfolio demonstration.
Generates simulated tennis odds data for stable presentations.
"""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any


class DemoScraper:
    """
    Generate realistic tennis odds data for demonstration purposes.
    
    This scraper simulates real bookmaker data with realistic odds,
    player matchups, and tournament information. Perfect for demos
    and presentations where live scraping might fail.
    """
    
    def __init__(self):
        """Initialize demo scraper with realistic data pools"""
        self.bookmaker_name = 'oddsportal'
        
        # Top ATP/WTA players for realistic matchups
        self.players = [
            ("Djokovic N.", "Alcaraz C."),
            ("Sinner J.", "Medvedev D."),
            ("Rune H.", "Tsitsipas S."),
            ("Fritz T.", "Paul T."),
            ("Zverev A.", "Rublev A."),
            ("Ruud C.", "Hurkacz H."),
            ("De Minaur A.", "Dimitrov G."),
            ("Shelton B.", "Tiafoe F."),
            ("Auger-Aliassime F.", "Shapovalov D."),
            ("Norrie C.", "Draper J."),
            ("Sabalenka A.", "Swiatek I."),
            ("Gauff C.", "Rybakina E."),
        ]
        
        # Current ATP/WTA tournaments
        self.tournaments = [
            "ATP Australian Open",
            "ATP Dubai",
            "ATP Indian Wells",
            "ATP Miami Open",
            "ATP Madrid",
            "ATP Rome",
            "WTA Dubai",
            "WTA Indian Wells",
            "WTA Miami Open",
            "WTA Madrid"
        ]
    
    def scrape_tennis_matches(self) -> List[Dict[str, Any]]:
        """
        Generate realistic demo tennis matches with odds.
        
        Returns:
            List of match dictionaries with realistic odds and metadata
        """
        matches = []
        
        for i, (p1, p2) in enumerate(self.players):
            # Generate realistic odds
            # 70% balanced matches (1.6-2.2), 30% favorites (1.3-1.7 vs 2.2-3.5)
            is_balanced = random.random() > 0.3
            
            if is_balanced:
                # Balanced match - close odds
                odds1 = round(random.uniform(1.6, 2.2), 2)
                odds2 = round(random.uniform(1.6, 2.2), 2)
            else:
                # Favorite vs underdog
                if random.random() > 0.5:
                    odds1 = round(random.uniform(1.3, 1.7), 2)
                    odds2 = round(random.uniform(2.2, 3.5), 2)
                else:
                    odds1 = round(random.uniform(2.2, 3.5), 2)
                    odds2 = round(random.uniform(1.3, 1.7), 2)
            
            # Match date (next 7 days)
            days_ahead = random.randint(0, 7)
            match_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            match_time = f"{random.randint(10, 20)}:{random.choice(['00', '30'])}"
            
            match = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'bookmaker': self.bookmaker_name,
                'tournament': random.choice(self.tournaments),
                'player1': p1,
                'player2': p2,
                'odds_player1': odds1,
                'odds_player2': odds2,
                'match_date': match_date,
                'match_time': match_time,
                'url': f'https://www.oddsportal.com/tennis/match/{i}'
            }
            matches.append(match)
        
        return matches
    
    def get_available_tournaments(self) -> List[Dict[str, str]]:
        """Return list of available tournaments"""
        return [
            {'name': t, 'url': f'https://www.oddsportal.com/tennis/{t.lower().replace(" ", "-")}'}
            for t in self.tournaments
        ]
    
    def close(self):
        """No cleanup needed for demo scraper"""
        pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, *args):
        """Context manager exit"""
        self.close()
