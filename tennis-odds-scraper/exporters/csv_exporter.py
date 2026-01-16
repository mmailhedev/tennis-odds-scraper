"""
CSV exporter for tennis match odds data.
Handles exporting scraped data to CSV format with proper formatting.
"""

from typing import List, Dict, Any
from pathlib import Path
import pandas as pd

from utils import get_logger, ensure_directory, format_timestamp


class CSVExporter:
    """
    Export tennis match data to CSV format.
    Provides flexible column ordering and formatting options.
    """
    
    def __init__(self, output_dir: str = 'data'):
        """
        Initialize CSV exporter.
        
        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = ensure_directory(output_dir)
        self.logger = get_logger('exporter.csv')
    
    def export(
        self,
        matches: List[Dict[str, Any]],
        filename: str,
        columns: List[str] = None,
        include_calculations: bool = True
    ) -> str:
        """
        Export matches to CSV file.
        
        Args:
            matches: List of match dictionaries
            filename: Output filename (without path)
            columns: List of columns to include (None = all)
            include_calculations: Add calculated fields (implied probability, margin)
            
        Returns:
            Full path to created CSV file
        """
        if not matches:
            self.logger.warning("No matches to export")
            return ""
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(matches)
            
            # Add calculated fields if requested
            if include_calculations:
                df = self._add_calculations(df)
            
            # Select and order columns
            if columns:
                available_cols = [col for col in columns if col in df.columns]
                df = df[available_cols]
            else:
                # Default column order
                default_order = [
                    'timestamp', 'bookmaker', 'tournament',
                    'player1', 'player2',
                    'odds_player1', 'odds_player2',
                    'implied_prob1', 'implied_prob2',
                    'bookmaker_margin',
                    'match_date', 'match_time', 'url'
                ]
                available_cols = [col for col in default_order if col in df.columns]
                df = df[available_cols]
            
            # Build output path
            filepath = self.output_dir / filename
            if not filepath.suffix:
                filepath = filepath.with_suffix('.csv')
            
            # Export to CSV
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            self.logger.info(f"Exported {len(matches)} matches to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def _add_calculations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add calculated fields to DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with additional columns
        """
        try:
            # Implied probability for each player
            if 'odds_player1' in df.columns:
                df['implied_prob1'] = df['odds_player1'].apply(
                    lambda x: round((1 / x) * 100, 2) if x and x > 0 else None
                )
            
            if 'odds_player2' in df.columns:
                df['implied_prob2'] = df['odds_player2'].apply(
                    lambda x: round((1 / x) * 100, 2) if x and x > 0 else None
                )
            
            # Bookmaker margin (overround)
            if 'odds_player1' in df.columns and 'odds_player2' in df.columns:
                df['bookmaker_margin'] = df.apply(
                    lambda row: self._calculate_margin(
                        row['odds_player1'],
                        row['odds_player2']
                    ),
                    axis=1
                )
        
        except Exception as e:
            self.logger.warning(f"Error adding calculations: {e}")
        
        return df
    
    @staticmethod
    def _calculate_margin(odds1: float, odds2: float) -> float:
        """
        Calculate bookmaker margin from two odds.
        
        Args:
            odds1: First outcome odds
            odds2: Second outcome odds
            
        Returns:
            Margin as percentage (rounded to 2 decimals)
        """
        if not odds1 or not odds2 or odds1 <= 0 or odds2 <= 0:
            return None
        
        prob1 = 1 / odds1
        prob2 = 1 / odds2
        margin = ((prob1 + prob2 - 1) * 100)
        
        return round(margin, 2)
    
    def export_summary(
        self,
        matches: List[Dict[str, Any]],
        filename: str = 'summary.csv'
    ) -> str:
        """
        Export summary statistics to CSV.
        
        Args:
            matches: List of match dictionaries
            filename: Output filename
            
        Returns:
            Full path to created CSV file
        """
        if not matches:
            return ""
        
        try:
            df = pd.DataFrame(matches)
            
            # Calculate summary statistics
            summary = {
                'total_matches': len(df),
                'unique_tournaments': df['tournament'].nunique() if 'tournament' in df else 0,
                'unique_bookmakers': df['bookmaker'].nunique() if 'bookmaker' in df else 0,
                'avg_odds_favorite': None,
                'avg_odds_underdog': None,
                'avg_margin': None
            }
            
            # Calculate average odds
            if 'odds_player1' in df.columns and 'odds_player2' in df.columns:
                all_odds = pd.concat([df['odds_player1'], df['odds_player2']])
                summary['avg_odds_favorite'] = round(all_odds.min(), 2)
                summary['avg_odds_underdog'] = round(all_odds.max(), 2)
            
            # Calculate average margin
            if 'bookmaker_margin' in df.columns:
                summary['avg_margin'] = round(df['bookmaker_margin'].mean(), 2)
            
            # Create summary DataFrame
            summary_df = pd.DataFrame([summary])
            
            # Export
            filepath = self.output_dir / filename
            summary_df.to_csv(filepath, index=False, encoding='utf-8')
            
            self.logger.info(f"Exported summary to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exporting summary: {e}")
            raise
    
    def append_to_csv(
        self,
        matches: List[Dict[str, Any]],
        filename: str
    ) -> str:
        """
        Append matches to existing CSV file.
        
        Args:
            matches: List of match dictionaries
            filename: Existing CSV filename
            
        Returns:
            Full path to CSV file
        """
        if not matches:
            return ""
        
        filepath = self.output_dir / filename
        
        try:
            # Convert new matches to DataFrame
            new_df = pd.DataFrame(matches)
            
            # Check if file exists
            if filepath.exists():
                # Read existing data
                existing_df = pd.read_csv(filepath)
                
                # Append new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # Remove duplicates (based on player names and timestamp)
                if all(col in combined_df.columns for col in ['player1', 'player2', 'timestamp']):
                    combined_df = combined_df.drop_duplicates(
                        subset=['player1', 'player2', 'bookmaker', 'timestamp'],
                        keep='last'
                    )
            else:
                combined_df = new_df
            
            # Save
            combined_df.to_csv(filepath, index=False, encoding='utf-8')
            
            self.logger.info(f"Appended {len(matches)} matches to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error appending to CSV: {e}")
            raise


# Example usage
if __name__ == '__main__':
    # Sample data
    sample_matches = [
        {
            'timestamp': '2025-01-15 10:00:00',
            'tournament': 'ATP Australian Open',
            'player1': 'Djokovic N.',
            'player2': 'Federer R.',
            'odds_player1': 1.50,
            'odds_player2': 2.80,
            'bookmaker': 'oddsportal',
            'match_date': '2025-01-20',
            'match_time': '14:00'
        }
    ]
    
    exporter = CSVExporter()
    output_file = exporter.export(sample_matches, 'test_export.csv')
    print(f"Exported to: {output_file}")
