# 🎬 Data Modes Documentation

## Overview

The Tennis Odds Scraper supports two data acquisition modes to balance **reliability** and **authenticity**.

---

## Demo Mode

**Purpose:** Stable demonstrations and portfolio presentations

**Implementation:** `scrapers/demo_scraper.py`

### Features
- Generates 12 realistic tennis matches
- Includes current top ATP/WTA players:
  - Djokovic N., Alcaraz C., Sinner J., Medvedev D.
  - Sabalenka A., Swiatek I., Gauff C., Rybakina E.
  - And more...
- Realistic odds distribution:
  - 70% balanced matches (odds 1.6-2.2)
  - 30% favorite/underdog scenarios (odds 1.3-1.7 vs 2.2-3.5)
- Upcoming match dates (next 7 days)
- Varied tournaments (ATP/WTA majors and masters)

### When to Use
✅ Portfolio presentations
✅ Job interviews  
✅ Client demonstrations  
✅ Feature development and testing  
✅ Screenshots and documentation  

### Advantages
- ✅ Always works (100% uptime)
- ✅ Consistent data for comparisons
- ✅ No external dependencies
- ✅ Fast (instant generation)
- ✅ No rate limiting concerns
- ✅ No legal/ToS issues

---

## Production Mode

**Purpose:** Real-world data acquisition

**Implementation:** `scrapers/oddsportal_scraper.py`

### Features
- Web scraping from Oddsportal.com
- BeautifulSoup4 + Requests
- Rate limiting (respectful scraping)
- Retry logic with exponential backoff
- Error handling and logging

### When to Use
✅ Testing real scraping functionality  
✅ Demonstrating actual implementation  
✅ Research and analysis projects  
✅ Extending to other bookmakers  

### Challenges
- ⚠️ Websites change structure frequently
- ⚠️ May require CSS selector updates
- ⚠️ IP blocking risks
- ⚠️ Legal/ToS considerations

---

## Switching Between Modes

### In Dashboard
1. Open sidebar
2. Find "Data Source" section
3. Select mode via radio buttons
4. Click "Scrape Now"

### In Code
```python
# Demo mode
from scrapers.demo_scraper import DemoScraper
with DemoScraper() as scraper:
    matches = scraper.scrape_tennis_matches()

# Production mode
from scrapers import OddsportalScraper
with OddsportalScraper() as scraper:
    matches = scraper.scrape_tennis_matches()
```

---

## Why Both Modes?

### Professional Software Engineering
Real-world applications use similar patterns:
- **Development environments** use mock data
- **Staging environments** use sanitized data
- **Production environments** use live data

### Benefits
1. **Reliability**: Demos never fail
2. **Testability**: Easy to test features
3. **Flexibility**: Swap data sources easily
4. **Separation of Concerns**: Business logic independent of data source

### Industry Examples
- **ML projects**: Pre-loaded datasets for demos
- **Analytics dashboards**: Sample data for presentations
- **Payment systems**: Sandbox/production modes
- **APIs**: Mock responses for testing

---

## Data Quality

Both modes provide the same data structure:
```python
{
    'timestamp': str,        # "2025-01-19 10:30:00"
    'bookmaker': str,        # "oddsportal"
    'tournament': str,       # "ATP Australian Open"
    'player1': str,          # "Djokovic N."
    'player2': str,          # "Alcaraz C."
    'odds_player1': float,   # 1.85
    'odds_player2': float,   # 2.10
    'match_date': str,       # "2025-01-25"
    'match_time': str,       # "14:00"
    'url': str               # "https://..."
}
```

This ensures **all features work identically** regardless of mode.

---

## Best Practices

### For Demonstrations
- ✅ Use Demo Mode
- ✅ Explain both modes exist
- ✅ Show production code on GitHub
- ✅ Emphasize architecture over scraping

### For Development
- ✅ Start with Demo Mode (faster iteration)
- ✅ Test features with consistent data
- ✅ Switch to Production for integration tests
- ✅ Keep both modes functional

### For Deployment
- ✅ Default to Demo Mode for stability
- ✅ Document how to enable Production
- ✅ Add monitoring for Production mode
- ✅ Implement fallback to Demo if Production fails

---

## Conclusion

The dual-mode approach demonstrates:
- ✅ Professional software design
- ✅ Production-ready thinking
- ✅ User-focused reliability
- ✅ Clean architecture

It shows you understand that **good software is about solving problems reliably**, not just making things work once.

---

## Quick Reference

| Aspect | Demo Mode | Production Mode |
|--------|-----------|-----------------|
| **Speed** | Instant | 2-3 seconds |
| **Reliability** | 100% | Variable |
| **Data** | Simulated | Live |
| **Dependencies** | None | Website access |
| **Use Case** | Presentations | Research |
| **Legal** | No concerns | Check ToS |

---

**For any questions, see the main [README.md](README.md) or [FEATURES_GUIDE.md](FEATURES_GUIDE.md)**
