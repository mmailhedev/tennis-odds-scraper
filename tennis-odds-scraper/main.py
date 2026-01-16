"""
Main execution script for tennis odds scraper.
Provides command-line interface for scraping and exporting tennis odds data.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from scrapers import OddsportalScraper
from exporters import CSVExporter, ExcelExporter
from utils import get_logger, Timer, ensure_directory


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Scrape tennis betting odds from multiple bookmakers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Scrape and export to CSV (default)
  python main.py
  
  # Export to Excel
  python main.py --format excel
  
  # Custom output filename
  python main.py --output my_odds.csv
  
  # Scrape specific bookmaker
  python main.py --bookmaker oddsportal
  
  # Include summary sheet (Excel only)
  python main.py --format excel --summary
        '''
    )
    
    parser.add_argument(
        '--bookmaker',
        type=str,
        default='oddsportal',
        choices=['oddsportal'],
        help='Bookmaker to scrape (default: oddsportal)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        default='csv',
        choices=['csv', 'excel', 'both'],
        help='Export format (default: csv)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output filename (without path). Default: tennis_odds_YYYY-MM-DD'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory (default: data)'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Include summary sheet (Excel only)'
    )
    
    parser.add_argument(
        '--no-calculations',
        action='store_true',
        help='Skip calculated fields (implied probability, margin)'
    )
    
    parser.add_argument(
        '--append',
        action='store_true',
        help='Append to existing file instead of overwriting (CSV only)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def get_scraper(bookmaker: str):
    """
    Get scraper instance for bookmaker.
    
    Args:
        bookmaker: Bookmaker name
        
    Returns:
        Scraper instance
        
    Raises:
        ValueError: If bookmaker not supported
    """
    scrapers = {
        'oddsportal': OddsportalScraper
    }
    
    if bookmaker not in scrapers:
        raise ValueError(f"Unsupported bookmaker: {bookmaker}")
    
    return scrapers[bookmaker]()


def generate_filename(format_type: str, custom_name: str = None) -> str:
    """
    Generate output filename with timestamp.
    
    Args:
        format_type: 'csv' or 'excel'
        custom_name: Custom filename (optional)
        
    Returns:
        Filename with extension
    """
    if custom_name:
        # Use custom name, add extension if missing
        filename = Path(custom_name)
        if not filename.suffix:
            ext = '.csv' if format_type == 'csv' else '.xlsx'
            filename = filename.with_suffix(ext)
        return str(filename)
    
    # Generate default filename with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d')
    ext = '.csv' if format_type == 'csv' else '.xlsx'
    return f'tennis_odds_{timestamp}{ext}'


def scrape_matches(bookmaker: str, logger) -> list:
    """
    Scrape matches from bookmaker.
    
    Args:
        bookmaker: Bookmaker name
        logger: Logger instance
        
    Returns:
        List of match dictionaries
    """
    logger.info(f"Starting scrape from {bookmaker}")
    
    try:
        scraper = get_scraper(bookmaker)
        
        with Timer(f'Scraping {bookmaker}'):
            matches = scraper.scrape_tennis_matches()
        
        scraper.close()
        
        logger.info(f"Successfully scraped {len(matches)} matches")
        return matches
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return []


def export_data(matches: list, args, logger) -> None:
    """
    Export scraped data to file(s).
    
    Args:
        matches: List of match dictionaries
        args: Parsed command-line arguments
        logger: Logger instance
    """
    if not matches:
        logger.warning("No matches to export")
        return
    
    # Ensure output directory exists
    ensure_directory(args.output_dir)
    
    include_calc = not args.no_calculations
    
    # Export to CSV
    if args.format in ['csv', 'both']:
        csv_exporter = CSVExporter(args.output_dir)
        filename = generate_filename('csv', args.output)
        
        try:
            if args.append and args.format == 'csv':
                filepath = csv_exporter.append_to_csv(matches, filename)
                logger.info(f"Appended to CSV: {filepath}")
            else:
                filepath = csv_exporter.export(
                    matches,
                    filename,
                    include_calculations=include_calc
                )
                logger.info(f"Exported to CSV: {filepath}")
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
    
    # Export to Excel
    if args.format in ['excel', 'both']:
        excel_exporter = ExcelExporter(args.output_dir)
        filename = generate_filename('excel', args.output)
        
        try:
            filepath = excel_exporter.export(
                matches,
                filename,
                include_summary=args.summary,
                include_calculations=include_calc
            )
            logger.info(f"Exported to Excel: {filepath}")
        except Exception as e:
            logger.error(f"Excel export failed: {e}")


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Setup logger
    logger = get_logger('main')
    
    if args.verbose:
        logger.setLevel('DEBUG')
    
    logger.info("="*60)
    logger.info("Tennis Odds Scraper - Starting")
    logger.info("="*60)
    
    try:
        # Scrape matches
        matches = scrape_matches(args.bookmaker, logger)
        
        if not matches:
            logger.error("No matches scraped. Exiting.")
            sys.exit(1)
        
        # Export data
        export_data(matches, args, logger)
        
        logger.info("="*60)
        logger.info("Scraping completed successfully")
        logger.info("="*60)
        
    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
