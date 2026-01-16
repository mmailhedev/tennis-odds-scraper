# Tennis Odds Scraper - Usage Examples

This document provides detailed examples for using the tennis odds scraper.

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Command Line Examples](#command-line-examples)
3. [Python Script Examples](#python-script-examples)
4. [Advanced Usage](#advanced-usage)
5. [Adding New Bookmakers](#adding-new-bookmakers)

---

## Basic Usage

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with defaults (CSV output)
python main.py

# Run with Excel output
python main.py --format excel
```

---

## Command Line Examples

### Export Formats

```bash
# Export to CSV (default)
python main.py

# Export to Excel
python main.py --format excel

# Export to both CSV and Excel
python main.py --format both
```

### Custom Output

```bash
# Custom filename
python main.py --output my_tennis_data.csv

# Custom output directory
python main.py --output-dir ./results

# With summary (Excel only)
python main.py --format excel --summary
```

### Advanced Options

```bash
# Append to existing CSV file
python main.py --append --output daily_odds.csv

# Skip calculated fields
python main.py --no-calculations

# Verbose logging
python main.py --verbose
```

### Complete Example

```bash
python main.py \
  --bookmaker oddsportal \
  --format excel \
  --output "australian_open_2025.xlsx" \
  --output-dir ./tournaments \
  --summary \
  --verbose
```

---

## Python Script Examples

### Example 1: Basic Scraping

```python
from scrapers import OddsportalScraper
from exporters import CSVExporter

# Initialize scraper
scraper = OddsportalScraper()

# Scrape matches
matches = scraper.scrape_tennis_matches()

# Export to CSV
exporter = CSVExporter()
exporter.export(matches, 'tennis_odds.csv')

# Cleanup
scraper.close()

print(f"Scraped {len(matches)} matches")
```

### Example 2: Using Context Manager

```python
from scrapers import OddsportalScraper
from exporters import ExcelExporter

# Context manager handles cleanup automatically
with OddsportalScraper() as scraper:
    matches = scraper.scrape_tennis_matches()
    
    # Export with summary
    exporter = ExcelExporter()
    exporter.export(
        matches,
        'tennis_odds.xlsx',
        include_summary=True
    )

print("Done!")
```

### Example 3: Multiple Bookmakers

```python
from scrapers import OddsportalScraper
# from scrapers import Bet365Scraper  # When implemented
from exporters import ExcelExporter

all_matches = []

# Scrape from multiple bookmakers
bookmakers = [
    OddsportalScraper(),
    # Bet365Scraper(),  # Add when implemented
]

for scraper in bookmakers:
    try:
        matches = scraper.scrape_tennis_matches()
        all_matches.extend(matches)
        print(f"Scraped {len(matches)} from {scraper.bookmaker_name}")
    finally:
        scraper.close()

# Export combined data
exporter = ExcelExporter()
exporter.export(all_matches, 'combined_odds.xlsx')

print(f"Total: {len(all_matches)} matches")
```

### Example 4: Filtering and Processing

```python
from scrapers import OddsportalScraper
from exporters import CSVExporter
import pandas as pd

# Scrape matches
with OddsportalScraper() as scraper:
    matches = scraper.scrape_tennis_matches()

# Convert to DataFrame for processing
df = pd.DataFrame(matches)

# Filter for specific tournament
atp_matches = df[df['tournament'].str.contains('ATP', na=False)]

# Filter for low-margin matches (better value)
df['margin'] = df.apply(
    lambda row: ((1/row['odds_player1'] + 1/row['odds_player2']) - 1) * 100,
    axis=1
)
low_margin = df[df['margin'] < 5.0]

# Export filtered data
exporter = CSVExporter()
exporter.export(low_margin.to_dict('records'), 'low_margin_matches.csv')

print(f"Found {len(low_margin)} low-margin matches")
```

### Example 5: Scheduled Scraping

```python
import schedule
import time
from scrapers import OddsportalScraper
from exporters import CSVExporter
from datetime import datetime

def scrape_and_save():
    """Scrape matches and append to daily file."""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f'odds_{timestamp}.csv'
    
    with OddsportalScraper() as scraper:
        matches = scraper.scrape_tennis_matches()
    
    if matches:
        exporter = CSVExporter()
        exporter.append_to_csv(matches, filename)
        print(f"[{datetime.now()}] Scraped {len(matches)} matches")

# Schedule every 2 hours
schedule.every(2).hours.do(scrape_and_save)

print("Starting scheduled scraper...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Example 6: Error Handling

```python
from scrapers import OddsportalScraper
from exporters import CSVExporter, ExcelExporter
from utils import get_logger

logger = get_logger('my_scraper')

def safe_scrape():
    """Scrape with comprehensive error handling."""
    matches = []
    
    try:
        # Initialize scraper
        scraper = OddsportalScraper()
        
        # Scrape with timeout handling
        matches = scraper.scrape_tennis_matches()
        
        if not matches:
            logger.warning("No matches found")
            return
        
        logger.info(f"Scraped {len(matches)} matches")
        
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        return
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return
    
    finally:
        if 'scraper' in locals():
            scraper.close()
    
    # Export with fallback
    try:
        exporter = ExcelExporter()
        exporter.export(matches, 'tennis_odds.xlsx')
    except Exception as e:
        logger.warning(f"Excel export failed, trying CSV: {e}")
        csv_exporter = CSVExporter()
        csv_exporter.export(matches, 'tennis_odds.csv')

safe_scrape()
```

---

## Advanced Usage

### Custom Configuration

```python
from scrapers import OddsportalScraper

scraper = OddsportalScraper()

# Adjust rate limiting
scraper.set_rate_limit(3.0)  # 3 seconds between requests

# Scrape specific tournament
matches = scraper.scrape_specific_tournament('atp-australian-open')

scraper.close()
```

### Get Available Tournaments

```python
from scrapers import OddsportalScraper

with OddsportalScraper() as scraper:
    tournaments = scraper.get_available_tournaments()
    
    for t in tournaments:
        print(f"{t['name']}: {t['url']}")
```

### Export by Tournament

```python
from scrapers import OddsportalScraper
from exporters import ExcelExporter

with OddsportalScraper() as scraper:
    matches = scraper.scrape_tennis_matches()

exporter = ExcelExporter()
exporter.export_by_tournament(matches, 'tournaments.xlsx')
```

### Calculate Statistics

```python
from scrapers import OddsportalScraper
from utils import calculate_implied_probability, calculate_bookmaker_margin
import pandas as pd

with OddsportalScraper() as scraper:
    matches = scraper.scrape_tennis_matches()

df = pd.DataFrame(matches)

# Add statistics
df['prob1'] = df['odds_player1'].apply(calculate_implied_probability)
df['prob2'] = df['odds_player2'].apply(calculate_implied_probability)
df['margin'] = df.apply(
    lambda row: calculate_bookmaker_margin(
        row['odds_player1'],
        row['odds_player2']
    ),
    axis=1
)

# Find best value bets (lowest margins)
best_value = df.nsmallest(10, 'margin')
print(best_value[['player1', 'player2', 'margin', 'tournament']])
```

---

## Adding New Bookmakers

### Step 1: Create Scraper Class

Create `scrapers/newbookmaker_scraper.py`:

```python
from scrapers.base_scraper import BaseScraper
from typing import List, Dict, Any

class NewBookmakerScraper(BaseScraper):
    """Scraper for NewBookmaker.com"""
    
    def __init__(self):
        super().__init__('newbookmaker')
        self.tennis_url = self.config.get('tennis_url')
    
    def scrape_tennis_matches(self) -> List[Dict[str, Any]]:
        """Scrape matches from NewBookmaker."""
        # Fetch page
        html = self.fetch_page(self.tennis_url)
        if not html:
            return []
        
        # Parse HTML
        soup = self.parse_html(html)
        
        # Extract matches (implement your logic here)
        matches = []
        
        # Example: find match containers
        match_rows = soup.select('div.match-row')
        
        for row in match_rows:
            player1 = row.select_one('.player1').get_text(strip=True)
            player2 = row.select_one('.player2').get_text(strip=True)
            odds1 = float(row.select_one('.odds1').get_text(strip=True))
            odds2 = float(row.select_one('.odds2').get_text(strip=True))
            
            match = {
                'timestamp': format_timestamp(),
                'player1': player1,
                'player2': player2,
                'odds_player1': odds1,
                'odds_player2': odds2,
                'bookmaker': self.bookmaker_name,
                'tournament': 'Unknown',
                'match_date': None,
                'match_time': None
            }
            
            if self.validate_match(match):
                matches.append(match)
        
        return matches
```

### Step 2: Add Configuration

Add to `config/bookmakers.json`:

```json
{
  "newbookmaker": {
    "name": "NewBookmaker",
    "base_url": "https://www.newbookmaker.com",
    "tennis_url": "https://www.newbookmaker.com/tennis",
    "rate_limit": 2.0,
    "timeout": 30,
    "max_retries": 3,
    "headers": {
      "User-Agent": "Mozilla/5.0..."
    }
  }
}
```

### Step 3: Add Scraping Rules

Add to `config/scraping_rules.json`:

```json
{
  "newbookmaker": {
    "description": "Scraping rules for NewBookmaker",
    "css_selectors": {
      "match_row": "div.match-row",
      "player1": ".player1",
      "player2": ".player2",
      "odds1": ".odds1",
      "odds2": ".odds2"
    }
  }
}
```

### Step 4: Update Imports

Add to `scrapers/__init__.py`:

```python
from .newbookmaker_scraper import NewBookmakerScraper

__all__ = [
    'BaseScraper',
    'OddsportalScraper',
    'NewBookmakerScraper'
]
```

### Step 5: Use It

```python
from scrapers import NewBookmakerScraper
from exporters import CSVExporter

with NewBookmakerScraper() as scraper:
    matches = scraper.scrape_tennis_matches()

exporter = CSVExporter()
exporter.export(matches, 'newbookmaker_odds.csv')
```

---

## Tips and Best Practices

1. **Rate Limiting**: Always respect website rate limits
2. **Error Handling**: Use try-except blocks for robust scraping
3. **Logging**: Enable verbose mode (`--verbose`) for debugging
4. **Data Validation**: Check scraped data before exporting
5. **Scheduling**: Use cron jobs or task schedulers for automated scraping
6. **Backup**: Save data incrementally to avoid data loss

---

## Troubleshooting

### No matches scraped
- Check if website structure changed
- Verify CSS selectors in `scraping_rules.json`
- Enable verbose logging: `python main.py --verbose`

### Connection errors
- Increase timeout in `bookmakers.json`
- Check internet connection
- Verify website is accessible

### Export errors
- Ensure output directory exists
- Check file permissions
- Verify data format is correct

---

For more information, see README.md or check the logs in the `logs/` directory.
