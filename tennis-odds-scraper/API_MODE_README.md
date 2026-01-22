# 🎾 API Mode - Real-Time Tennis Odds

## Overview

The Tennis Odds Scraper now includes **API Mode** - integration with The Odds API for real-time tennis betting odds from 200+ bookmakers worldwide.

## Features

✅ **Real-Time Data**
- Live ATP & WTA tournament matches
- Updates every 5-10 minutes
- Match winner, spreads, totals markets

✅ **Multiple Bookmakers**
- 200+ bookmakers globally
- Best odds extraction across all sources
- US, EU, UK, AU regions

✅ **Free Tier Available**
- 500 API requests per month (free)
- Enough for daily monitoring
- No credit card required

✅ **Production Ready**
- Robust error handling
- Rate limit tracking
- Compatible with existing dashboard/API

---

## Quick Start

### 1. Get API Key (Free)

1. Visit: https://the-odds-api.com/
2. Sign up (no credit card)
3. Copy your API key
4. You get 500 free requests/month

### 2. Configure

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env`:

```
ODDS_API_KEY=your_api_key_here
```

### 3. Test API Connection

```bash
python scrapers/theodds_scraper.py
```

Expected output:
```
🎾 Testing The Odds API Scraper...
==================================================

✅ Successfully scraped 15 matches
📊 API requests remaining: 499

📋 Sample match:
  Novak Djokovic vs Carlos Alcaraz
  Tournament: ATP Australian Open
  Odds: 2.15 / 1.72
  Bookmaker: Bet365
  Margin: 4.23%
```

### 4. Use in Dashboard

```bash
streamlit run dashboard.py
```

In the sidebar:
1. Select **"API Mode (Live)"**
2. Enter your API key (or use .env)
3. Click **"Scrape Now"**

---

## Usage Examples

### Python Script

```python
from scrapers.theodds_scraper import TheOddsAPIScraper
import os

api_key = os.getenv('ODDS_API_KEY')

with TheOddsAPIScraper(api_key) as scraper:
    # Fetch all tennis matches
    matches = scraper.scrape_tennis_matches(
        include_atp=True,
        include_wta=True
    )
    
    # Display
    for match in matches:
        print(f"{match['player1']} vs {match['player2']}")
        print(f"  Odds: {match['odds_player1']} / {match['odds_player2']}")
        print(f"  Margin: {match['bookmaker_margin']}%")
    
    # Check API status
    status = scraper.get_api_status()
    print(f"\nRequests remaining: {status['requests_remaining']}")
```

### API Integration (FastAPI)

Update your `api.py`:

```python
from scrapers.theodds_scraper import TheOddsAPIScraper
import os

@app.get("/matches/live")
async def get_live_matches():
    """Get live tennis matches from The Odds API"""
    
    api_key = os.getenv('ODDS_API_KEY')
    
    with TheOddsAPIScraper(api_key) as scraper:
        matches = scraper.scrape_tennis_matches()
        status = scraper.get_api_status()
    
    return {
        "matches": matches,
        "count": len(matches),
        "api_status": status
    }
```

---

## API Rate Limits

### Free Tier
- **500 requests per month**
- Resets monthly on sign-up anniversary
- No credit card required

### Request Usage
- Each call to `scrape_tennis_matches()` = **2 requests** (ATP + WTA)
- Monitor with `scraper.get_api_status()`

### Optimization Tips

**1. Cache Results**
```python
# Cache for 5 minutes
import time

cache = {'matches': None, 'timestamp': 0}
CACHE_DURATION = 300  # 5 minutes

def get_matches_cached():
    if time.time() - cache['timestamp'] > CACHE_DURATION:
        cache['matches'] = scraper.scrape_tennis_matches()
        cache['timestamp'] = time.time()
    
    return cache['matches']
```

**2. Fetch During Active Tournaments**
```python
# Only fetch during Grand Slams / major tournaments
import datetime

active_tournaments = [
    (1, 15, 1, 30),  # Australian Open (Jan 15-30)
    (5, 20, 6, 10),  # French Open (May 20 - Jun 10)
    # ...
]

def is_tournament_active():
    now = datetime.datetime.now()
    for start_month, start_day, end_month, end_day in active_tournaments:
        # Check if current date in range
        pass
```

**3. Selective Fetching**
```python
# Fetch only ATP or WTA
matches = scraper.scrape_tennis_matches(
    include_atp=True,
    include_wta=False  # Save 1 request
)
```

---

## Data Format

The Odds API returns data in this format (transformed to match existing structure):

```python
{
    'player1': 'Novak Djokovic',
    'player2': 'Carlos Alcaraz',
    'tournament': 'ATP Australian Open',
    'match_time': '2026-01-25 14:00',
    'odds_player1': 2.15,
    'odds_player2': 1.72,
    'bookmaker': 'Bet365',
    'bookmaker_margin': 4.23,
    'url': 'https://the-odds-api.com',
    'source': 'The Odds API (Live)',
    'bookmakers_count': 15,  # Number of bookmakers offering odds
    'api_match_id': 'abc123...',
    'last_update': '2026-01-21 10:30:45'
}
```

---

## Comparison: Demo vs Production vs API

| Feature | Demo Mode | Production Mode | API Mode |
|---------|-----------|-----------------|----------|
| **Data Source** | Simulated | Web Scraping | The Odds API |
| **Speed** | Instant | 10-30 sec | 2-5 sec |
| **Reliability** | 100% | ~85% (depends on site) | ~99% |
| **Updates** | Static | On-demand | Real-time |
| **Cost** | Free | Free | Free (500/mo) |
| **Bookmakers** | 1 (simulated) | 1 (Oddsportal) | 200+ |
| **Best For** | Demos/Testing | Technical showcase | Production use |

---

## Troubleshooting

### "API key required" Error

**Problem:** No API key configured

**Solution:**
```bash
# Option 1: Environment variable
export ODDS_API_KEY=your_key_here

# Option 2: .env file
echo "ODDS_API_KEY=your_key_here" > .env

# Option 3: Dashboard input
# Enter key directly in sidebar
```

### "403 Forbidden" Error

**Problem:** Invalid API key or rate limit exceeded

**Solution:**
1. Verify API key at https://the-odds-api.com/account
2. Check requests remaining with `scraper.get_api_status()`
3. Wait for monthly reset

### "No matches found" Warning

**Problem:** No live tennis matches at the moment

**Reason:** Off-season or between tournaments

**Solution:**
- Check tournament calendar
- Try during Grand Slams or ATP/WTA tour weeks
- Fall back to Demo Mode for testing

### Network/Proxy Issues

**Problem:** Cannot reach API from restricted networks

**Solution:**
```python
# Add proxy support
import os

os.environ['HTTP_PROXY'] = 'http://proxy.example.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.example.com:8080'
```

---

## Advanced Features

### Custom Regions

```python
# Get odds from specific regions
scraper.get_tennis_odds(
    sport='tennis_atp',
    regions='uk,au',  # UK and Australia bookmakers
    markets='h2h'
)
```

### Multiple Markets

```python
# Get spreads and totals in addition to match winner
scraper.get_tennis_odds(
    sport='tennis_atp',
    regions='us',
    markets='h2h,spreads,totals'
)
```

### American Odds Format

```python
# Get American odds instead of decimal
scraper.get_tennis_odds(
    sport='tennis_atp',
    regions='us',
    markets='h2h',
    odds_format='american'  # +150, -200, etc.
)
```

---

## API Documentation

Full API documentation: https://the-odds-api.com/liveapi/guides/v4/

### Endpoints Used

1. **`GET /v4/sports/{sport}/odds`**
   - Fetch odds for specific sport
   - Parameters: regions, markets, oddsFormat
   - Response: List of matches with bookmaker odds

### Sports Available

- `tennis_atp` - ATP Tour
- `tennis_wta` - WTA Tour
- `tennis_atp_australian_open` - Australian Open (during tournament)
- `tennis_atp_french_open` - French Open (during tournament)
- `tennis_wta_us_open` - US Open (during tournament)
- `tennis_atp_wimbledon` - Wimbledon (during tournament)

---

## Support

**The Odds API Support:**
- Docs: https://the-odds-api.com/liveapi/guides/v4/
- Email: support@the-odds-api.com

**Project Issues:**
- GitHub Issues: [Your repo]/issues
- Questions: Create an issue with `[API Mode]` tag

---

## Upgrading

### From Demo/Production to API Mode

No code changes needed! API Mode integrates seamlessly:

1. Get API key
2. Add to `.env`
3. Select "API Mode" in dashboard
4. Done! ✅

All existing features work:
- ✅ Dashboard charts
- ✅ FastAPI endpoints
- ✅ Arbitrage detection
- ✅ CSV/Excel export

---

## License

This integration respects The Odds API's terms of service.
Free tier usage is subject to fair use policies.

---

**Built with ❤️ for real-time sports betting analysis**
