"""
Multi-Bookmaker Odds Comparator and Arbitrage Detector
Compares odds across multiple bookmakers and identifies arbitrage opportunities.
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime
import pandas as pd

from scrapers import OddsportalScraper
from utils import get_logger, calculate_bookmaker_margin

logger = get_logger('comparator')


class OddsComparator:
    """
    Compare odds across multiple bookmakers and find value opportunities.
    """
    
    def __init__(self):
        """Initialize comparator with available scrapers"""
        self.scrapers = {
            'oddsportal': OddsportalScraper()
        }
        # Add more scrapers as they're implemented:
        # 'bet365': Bet365Scraper(),
        # 'unibet': UnibetScraper(),
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close all scrapers"""
        self.close_all()
    
    def scrape_all_bookmakers(self) -> List[Dict]:
        """
        Scrape odds from all available bookmakers.
        
        Returns:
            List of all matches from all bookmakers
        """
        all_matches = []
        
        for bookmaker_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping from {bookmaker_name}...")
                matches = scraper.scrape_tennis_matches()
                all_matches.extend(matches)
                logger.info(f"Scraped {len(matches)} matches from {bookmaker_name}")
            except Exception as e:
                logger.error(f"Error scraping {bookmaker_name}: {e}")
                continue
        
        return all_matches
    
    def normalize_player_names(self, player: str) -> str:
        """
        Normalize player names for comparison.
        
        Args:
            player: Player name
            
        Returns:
            Normalized player name
        """
        # Remove extra spaces
        player = ' '.join(player.split())
        
        # Convert to title case
        player = player.title()
        
        # Handle common abbreviations
        player = player.replace('N.', 'Novak')
        player = player.replace('R.', 'Rafael')
        
        return player
    
    def group_matches_by_players(self, matches: List[Dict]) -> Dict[Tuple[str, str], List[Dict]]:
        """
        Group matches by player matchup across bookmakers.
        
        Args:
            matches: List of all matches
            
        Returns:
            Dictionary mapping (player1, player2) to list of matches
        """
        grouped = {}
        
        for match in matches:
            # Create normalized key (always alphabetically sorted)
            players = sorted([
                self.normalize_player_names(match['player1']),
                self.normalize_player_names(match['player2'])
            ])
            key = tuple(players)
            
            if key not in grouped:
                grouped[key] = []
            
            grouped[key].append(match)
        
        return grouped
    
    def find_best_odds_per_match(self, matches: List[Dict]) -> pd.DataFrame:
        """
        Find the best available odds for each match across all bookmakers.
        
        Args:
            matches: List of all matches
            
        Returns:
            DataFrame with best odds per match
        """
        if not matches:
            return pd.DataFrame()
        
        df = pd.DataFrame(matches)
        
        # Group by match and find best odds
        best_odds = df.groupby(['player1', 'player2']).agg({
            'odds_player1': 'max',
            'odds_player2': 'max',
            'tournament': 'first',
            'match_date': 'first',
            'match_time': 'first'
        }).reset_index()
        
        # Add bookmaker names for best odds
        for idx, row in best_odds.iterrows():
            # Find bookmaker with best odds for player 1
            mask1 = (df['player1'] == row['player1']) & \
                    (df['player2'] == row['player2']) & \
                    (df['odds_player1'] == row['odds_player1'])
            best_odds.loc[idx, 'bookmaker_player1'] = df[mask1]['bookmaker'].iloc[0]
            
            # Find bookmaker with best odds for player 2
            mask2 = (df['player1'] == row['player1']) & \
                    (df['player2'] == row['player2']) & \
                    (df['odds_player2'] == row['odds_player2'])
            best_odds.loc[idx, 'bookmaker_player2'] = df[mask2]['bookmaker'].iloc[0]
        
        return best_odds
    
    def calculate_arbitrage(self, odds1: float, odds2: float) -> Tuple[bool, float, float, float]:
        """
        Calculate if arbitrage opportunity exists and optimal bet distribution.
        
        Args:
            odds1: Odds for player 1
            odds2: Odds for player 2
            
        Returns:
            Tuple of (is_arbitrage, profit_pct, stake1_pct, stake2_pct)
        """
        if odds1 <= 0 or odds2 <= 0:
            return False, 0.0, 0.0, 0.0
        
        # Calculate inverse sum
        inverse_sum = (1 / odds1) + (1 / odds2)
        
        # Check if arbitrage exists (inverse sum < 1)
        is_arbitrage = inverse_sum < 1.0
        
        if is_arbitrage:
            # Calculate profit percentage
            profit_pct = ((1 / inverse_sum) - 1) * 100
            
            # Calculate optimal stake distribution
            stake1_pct = (1 / odds1) / inverse_sum * 100
            stake2_pct = (1 / odds2) / inverse_sum * 100
            
            return True, profit_pct, stake1_pct, stake2_pct
        
        return False, 0.0, 0.0, 0.0
    
    def find_arbitrage_opportunities(
        self,
        matches: List[Dict],
        min_profit: float = 0.0
    ) -> List[Dict]:
        """
        Find arbitrage betting opportunities across bookmakers.
        
        Args:
            matches: List of all matches
            min_profit: Minimum profit percentage to include
            
        Returns:
            List of arbitrage opportunities
        """
        logger.info("Searching for arbitrage opportunities...")
        
        grouped = self.group_matches_by_players(matches)
        arbitrage_opps = []
        
        for (player1, player2), match_group in grouped.items():
            if len(match_group) < 2:
                # Need at least 2 bookmakers for arbitrage
                continue
            
            # Find best odds for each player
            best_odds1 = max(m['odds_player1'] for m in match_group)
            best_odds2 = max(m['odds_player2'] for m in match_group)
            
            # Get bookmakers offering these odds
            bookmaker1 = next(
                m['bookmaker'] for m in match_group
                if m['odds_player1'] == best_odds1
            )
            bookmaker2 = next(
                m['bookmaker'] for m in match_group
                if m['odds_player2'] == best_odds2
            )
            
            # Check for arbitrage
            is_arb, profit, stake1, stake2 = self.calculate_arbitrage(best_odds1, best_odds2)
            
            if is_arb and profit >= min_profit:
                # Get match details
                sample_match = match_group[0]
                
                arbitrage_opps.append({
                    'player1': player1,
                    'player2': player2,
                    'tournament': sample_match.get('tournament', 'Unknown'),
                    'best_odds1': best_odds1,
                    'best_odds2': best_odds2,
                    'bookmaker1': bookmaker1,
                    'bookmaker2': bookmaker2,
                    'profit_pct': round(profit, 2),
                    'stake1_pct': round(stake1, 2),
                    'stake2_pct': round(stake2, 2),
                    'match_date': sample_match.get('match_date'),
                    'match_time': sample_match.get('match_time'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        logger.info(f"Found {len(arbitrage_opps)} arbitrage opportunities")
        return arbitrage_opps
    
    def find_value_bets(
        self,
        matches: List[Dict],
        margin_threshold: float = 3.0
    ) -> List[Dict]:
        """
        Find value betting opportunities (low margin bets).
        
        Args:
            matches: List of matches
            margin_threshold: Maximum acceptable margin
            
        Returns:
            List of value bets
        """
        value_bets = []
        
        for match in matches:
            margin = calculate_bookmaker_margin(
                match['odds_player1'],
                match['odds_player2']
            )
            
            if margin and margin < margin_threshold:
                value_bets.append({
                    **match,
                    'calculated_margin': round(margin, 2)
                })
        
        # Sort by margin (best value first)
        value_bets.sort(key=lambda x: x['calculated_margin'])
        
        logger.info(f"Found {len(value_bets)} value bets with margin < {margin_threshold}%")
        return value_bets
    
    def compare_bookmakers(self, matches: List[Dict]) -> pd.DataFrame:
        """
        Compare average margins across bookmakers.
        
        Args:
            matches: List of all matches
            
        Returns:
            DataFrame with bookmaker comparison
        """
        if not matches:
            return pd.DataFrame()
        
        df = pd.DataFrame(matches)
        
        # Calculate margin for each match
        df['margin'] = df.apply(
            lambda row: calculate_bookmaker_margin(
                row['odds_player1'],
                row['odds_player2']
            ),
            axis=1
        )
        
        # Group by bookmaker and calculate stats
        comparison = df.groupby('bookmaker').agg({
            'margin': ['mean', 'min', 'max', 'count']
        }).round(2)
        
        comparison.columns = ['Avg_Margin', 'Min_Margin', 'Max_Margin', 'Match_Count']
        comparison = comparison.sort_values('Avg_Margin')
        
        return comparison
    
    def generate_report(self, matches: List[Dict]) -> Dict:
        """
        Generate comprehensive comparison report.
        
        Args:
            matches: List of all matches
            
        Returns:
            Dictionary containing report data
        """
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_matches': len(matches),
            'bookmakers': list(set(m['bookmaker'] for m in matches)),
            'tournaments': list(set(m.get('tournament', 'Unknown') for m in matches)),
        }
        
        # Best odds per match
        best_odds_df = self.find_best_odds_per_match(matches)
        if not best_odds_df.empty:
            report['best_odds_sample'] = best_odds_df.head(10).to_dict('records')
        
        # Arbitrage opportunities
        arbitrage = self.find_arbitrage_opportunities(matches, min_profit=0.0)
        report['arbitrage_count'] = len(arbitrage)
        report['arbitrage_opportunities'] = arbitrage[:10]  # Top 10
        
        # Value bets
        value_bets = self.find_value_bets(matches, margin_threshold=3.0)
        report['value_bets_count'] = len(value_bets)
        report['value_bets_sample'] = value_bets[:10]
        
        # Bookmaker comparison
        comparison_df = self.compare_bookmakers(matches)
        if not comparison_df.empty:
            report['bookmaker_comparison'] = comparison_df.to_dict('index')
        
        return report
    
    def close_all(self):
        """Close all scraper connections"""
        for scraper in self.scrapers.values():
            try:
                scraper.close()
            except:
                pass


# Standalone functions for easy use
def compare_odds() -> Dict:
    """
    Quick function to compare odds across all bookmakers.
    
    Returns:
        Comparison report
    """
    with OddsComparator() as comparator:
        matches = comparator.scrape_all_bookmakers()
        return comparator.generate_report(matches)


def find_arbitrage(min_profit: float = 0.0) -> List[Dict]:
    """
    Quick function to find arbitrage opportunities.
    
    Args:
        min_profit: Minimum profit percentage
        
    Returns:
        List of arbitrage opportunities
    """
    with OddsComparator() as comparator:
        matches = comparator.scrape_all_bookmakers()
        return comparator.find_arbitrage_opportunities(matches, min_profit)


# Example usage
if __name__ == '__main__':
    print("🎾 Tennis Odds Comparator\n")
    
    # Create comparator
    with OddsComparator() as comparator:
        # Scrape all bookmakers
        print("📊 Scraping odds from all bookmakers...")
        matches = comparator.scrape_all_bookmakers()
        print(f"✅ Collected {len(matches)} matches\n")
        
        # Find arbitrage
        print("🔍 Searching for arbitrage opportunities...")
        arbitrage = comparator.find_arbitrage_opportunities(matches)
        
        if arbitrage:
            print(f"\n💰 Found {len(arbitrage)} arbitrage opportunities:\n")
            for opp in arbitrage[:5]:  # Show top 5
                print(f"  {opp['player1']} vs {opp['player2']}")
                print(f"  Odds: {opp['best_odds1']} ({opp['bookmaker1']}) - "
                      f"{opp['best_odds2']} ({opp['bookmaker2']})")
                print(f"  Profit: {opp['profit_pct']}%")
                print(f"  Stakes: {opp['stake1_pct']}% / {opp['stake2_pct']}%\n")
        else:
            print("  No arbitrage opportunities found.\n")
        
        # Find value bets
        print("🎯 Finding value bets (margin < 3%)...")
        value_bets = comparator.find_value_bets(matches, margin_threshold=3.0)
        
        if value_bets:
            print(f"\n✨ Found {len(value_bets)} value bets:\n")
            for bet in value_bets[:5]:  # Show top 5
                print(f"  {bet['player1']} vs {bet['player2']}")
                print(f"  Odds: {bet['odds_player1']} - {bet['odds_player2']}")
                print(f"  Margin: {bet['calculated_margin']}% ({bet['bookmaker']})\n")
        
        # Bookmaker comparison
        print("📈 Bookmaker Comparison:")
        comparison = comparator.compare_bookmakers(matches)
        print(comparison)
