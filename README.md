# 🎾 Tennis Odds Scraper - Complete Analysis Suite

A professional-grade web scraping and data analysis platform for tennis betting odds, featuring interactive dashboard, REST API, and arbitrage detection algorithms.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

---

## 🎬 Data Sources & Modes

This project supports **multiple data sources** for maximum flexibility and reliability:

### Demo Mode (Default) ✅
- **Simulated realistic data** for stable demonstrations
- Always works (no external dependencies)
- Perfect for portfolio presentations and client demos
- 12 realistic tennis matches with varied odds
- Includes top ATP/WTA players (Djokovic, Alcaraz, Sinner, Swiatek, etc.)

### Production Mode - Web Scraping ⚙️
- **Real web scraping** from Oddsportal
- May require updates if website structure changes
- Full scraping implementation visible in code
- Toggle available in dashboard sidebar

### Production Mode - The Odds API 🆕 ⭐
- **Real-time odds data** from 200+ bookmakers via official API
- **500 free requests/month** (no credit card required)
- **100% reliable** - no scraping maintenance needed
- Automatic tournament detection (ATP, WTA, Grand Slams)
- Always up-to-date with current matches
- Get your free API key at: https://the-odds-api.com

**Why multiple modes?**

This is a **professional software engineering practice**:
- **Reliability**: Demos never break due to external dependencies
- **Flexibility**: Easy to swap data sources (scraping, API, database)
- **Separation of Concerns**: Business logic independent from data acquisition
- **Industry Standard**: Same approach used by production apps (dev/staging/prod environments)

**What matters most:**
The core value is the **architecture and features**, not just the data source:
- 🏗️ Clean, modular architecture
- 📊 Interactive dashboard with real-time visualization
- 🔌 Professional REST API with auto-documentation
- 🎯 Advanced arbitrage detection algorithms

> **Note:** Real-world applications use similar patterns. ML projects use pre-loaded datasets for demos, analytics dashboards use sample data for presentations, and payment systems have sandbox/production modes.

---

## 🌟 Main Features

### 📊 1. Interactive Dashboard (Streamlit)
Real-time visualization and analysis interface
- Interactive Plotly charts with hover details
- Demo/Production mode toggle with multiple data sources
- Auto-refresh for live odds monitoring (30s intervals)
- Advanced filtering (margin, odds, tournament)
- Best value bets identification
- Player/tournament search
- One-click export to CSV/Excel with download button

### 🔌 2. REST API (FastAPI)
Professional API with automatic documentation
- 9 comprehensive endpoints
- Swagger UI auto-documentation
- Pydantic data validation
- Advanced filtering capabilities
- Statistics and analytics endpoints
- CORS support for web integration

### 🎯 3. Arbitrage Detector & Multi-Bookmaker Comparator
Advanced market analysis and opportunity detection
- Multi-bookmaker odds comparison
- Arbitrage opportunity detection (risk-free profit)
- Value bet identification (low margins)
- Optimal stake distribution calculator
- Comprehensive market reports
- Bookmaker performance analysis

### ⚙️ Data Collection Options
Flexible and extensible data acquisition
- **Demo Mode**: Instant simulated data
- **Web Scraping**: Oddsportal integration
- **The Odds API**: Real-time data from 200+ bookmakers
- Modular architecture (easy to add sources)
- Automatic retry logic with exponential backoff
- Rate limiting and ethical scraping
- Comprehensive error handling

---

## 🛠️ Tech Stack

**Backend & Data Collection:**
- Python 3.11+
- BeautifulSoup4 & lxml (HTML parsing)
- Requests (HTTP)
- Pandas (data processing)
- The Odds API (real-time odds data)

**Dashboard:**
- Streamlit (web interface)
- Plotly (interactive charts)

**API:**
- FastAPI (REST framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)

**Export:**
- OpenPyXL (Excel formatting)
- CSV export with pandas

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd tennis-odds-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Setup The Odds API (Optional - for Production Mode)

```bash
# 1. Get free API key at https://the-odds-api.com (500 requests/month free)

# 2. Create .env file in project root
echo "ODDS_API_KEY=your_api_key_here" > .env

# 3. Test the API
python scrapers/theodds_scraper.py
```

### Basic Usage

#### 1. Launch Dashboard (Recommended)
```bash
streamlit run dashboard.py
```
Opens at http://localhost:8501

**In the dashboard:**
- Select **Demo Mode** (default) for reliable presentation
- Or **Production Mode - Web Scraping** to test scraping
- Or **Production Mode - The Odds API** for real-time data
- Click **"Scrape Now"** to fetch data
- Explore charts, filter matches, export data

#### 2. Test The Odds API Directly
```bash
# Quick test to see available tennis tournaments
python scrapers/theodds_scraper.py

# Output example:
# 🎾 Available tennis sports:
#   • tennis_atp_aus_open_singles (ATP Australian Open)
#   • tennis_wta_aus_open_singles (WTA Australian Open)
```

#### 3. Start API Server
```bash
python api.py
```
- API at http://localhost:8000  
- Docs at http://localhost:8000/docs

#### 4. Run Arbitrage Detector
```bash
python comparator.py
```

#### 5. Command Line Scraping
```bash
python main.py --format excel --summary
```

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute getting started guide
- **[FEATURES_GUIDE.md](FEATURES_GUIDE.md)** - Complete feature documentation
- **[EXAMPLES.md](EXAMPLES.md)** - Code examples and use cases
- **[DATA_MODES.md](DATA_MODES.md)** - Demo vs Production explained
- **[API_MODE_README.md](API_MODE_README.md)** - The Odds API integration guide
- **[COMMANDS.md](COMMANDS.md)** - Command reference

---

## 📁 Project Structure

```
tennis-odds-scraper/
├── dashboard.py                        # Streamlit dashboard ⭐
├── api.py                              # FastAPI REST API ⭐
├── comparator.py                       # Arbitrage detector ⭐
├── main.py                             # CLI scraper
├── scrapers/
│   ├── base_scraper.py                # Abstract base class
│   ├── oddsportal_scraper.py          # Web scraping (Oddsportal)
│   ├── theodds_scraper.py             # The Odds API integration ⭐
│   └── demo_scraper.py                # Demo data generator
├── exporters/
│   ├── csv_exporter.py                # CSV export
│   └── excel_exporter.py              # Excel with formatting
├── utils/
│   ├── logger.py                      # Logging system
│   └── helpers.py                     # Helper functions
├── config/
│   ├── bookmakers.json                # Bookmaker configs
│   └── scraping_rules.json            # CSS selectors
├── .env.example                        # Environment variables template
└── requirements.txt                    # Dependencies
```

---

## 💡 Use Cases

### 1. Real-time Data via The Odds API
```python
from scrapers.theodds_scraper import TheOddsAPIScraper
import os

api_key = os.getenv('ODDS_API_KEY')

with TheOddsAPIScraper(api_key) as scraper:
    # Automatically detects available tennis sports
    matches = scraper.scrape_tennis_matches()
    
    for match in matches:
        print(f"{match['player1']} vs {match['player2']}")
        print(f"Tournament: {match['tournament']}")
        print(f"Odds: {match['odds_player1']} / {match['odds_player2']}")
        print(f"Best bookmaker: {match['bookmaker']}")
```

### 2. Market Analysis (Demo Mode)
```python
from scrapers.demo_scraper import DemoScraper
import pandas as pd

with DemoScraper() as scraper:
    matches = scraper.scrape_tennis_matches()

df = pd.DataFrame(matches)
print(f"Average margin: {df['bookmaker_margin'].mean():.2f}%")
```

### 3. API Integration
```python
import requests

response = requests.get('http://localhost:8000/best-value?limit=5')
for match in response.json():
    print(f"{match['player1']} vs {match['player2']}")
    print(f"Margin: {match['bookmaker_margin']}%")
```

### 4. Arbitrage Detection
```python
from comparator import OddsComparator

with OddsComparator() as comparator:
    matches = comparator.scrape_all_bookmakers()
    arbitrage = comparator.find_arbitrage_opportunities(matches)
    
    for opp in arbitrage:
        print(f"💰 Profit: {opp['profit_pct']}%")
```

---

## 📊 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/matches` | All matches with filters |
| `/stats` | Overall statistics |
| `/best-value` | Lowest margin matches |
| `/player/{name}` | Player-specific matches |
| `/tournament/{name}` | Tournament matches |
| `/arbitrage` | Arbitrage opportunities |

**Full API documentation:** http://localhost:8000/docs

---

## 🔑 The Odds API - Key Features

### Why Use The Odds API?

✅ **Zero Maintenance** - No scraping to break  
✅ **Always Current** - Real-time tournament data  
✅ **Multiple Bookmakers** - 200+ sources in one call  
✅ **Free Tier** - 500 requests/month (perfect for demos)  
✅ **Automatic Detection** - Finds active tournaments (Grand Slams, ATP, WTA)  

### How It Works

The scraper automatically:
1. Fetches available tennis sports from API
2. Filters for active tournaments
3. Adapts to current events (Australian Open, Wimbledon, etc.)
4. Never breaks between tournaments

**Example during Australian Open:**
```
✅ tennis_atp_aus_open_singles → ATP Australian Open
✅ tennis_wta_aus_open_singles → WTA Australian Open
```

**Example during Wimbledon:**
```
✅ tennis_atp_wimbledon_singles → ATP Wimbledon
✅ tennis_wta_wimbledon_singles → WTA Wimbledon
```

---

## ⚖️ Legal & Ethics

- Respect robots.txt files
- Implement rate limiting
- Use for personal/research purposes only
- Check each website's terms of service

**For portfolio/demonstrations**, Demo Mode is recommended to avoid legal concerns while showcasing technical skills.

**The Odds API** is an official, legal data source with explicit permission for use.

---

## 📈 Performance

- **Demo mode**: Instant (no network calls)
- **The Odds API**: ~200-500ms per request
- **Web scraping**: 5-15s depending on network
- **API response**: <100ms average
- **Dashboard**: Real-time updates
- **Memory usage**: ~50MB typical

---

## 🔗 Quick Links

- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **The Odds API**: https://the-odds-api.com

---

## 🆕 Recent Updates

### v2.0 - The Odds API Integration
- Added official API integration for production use
- Automatic tournament detection (no more 404 errors)
- 500 free requests/month tier
- Zero maintenance required
- Real-time data from 200+ bookmakers

---

**Built with ❤️ for data analysis and betting insights**