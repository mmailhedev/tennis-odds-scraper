# 🎾 Tennis Odds Scraper - Complete Analysis Suite

A professional-grade web scraping and data analysis platform for tennis betting odds, featuring interactive dashboard, REST API, and arbitrage detection algorithms.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

---

## 🌟 Main Features

### 📊 1. Interactive Dashboard (Streamlit)
Real-time visualization and analysis interface
- Interactive Plotly charts with hover details
- Auto-refresh for live odds monitoring (30s intervals)
- Advanced filtering (margin, odds, tournament)
- Best value bets identification
- Player/tournament search
- One-click export to CSV/Excel

**[→ Dashboard Guide](FEATURES_GUIDE.md#feature-1-streamlit-dashboard)**

### 🔌 2. REST API (FastAPI)
Professional API with automatic documentation
- 9 comprehensive endpoints
- Swagger UI auto-documentation
- Pydantic data validation
- Advanced filtering capabilities
- Statistics and analytics endpoints
- CORS support for web integration

**[→ API Guide](FEATURES_GUIDE.md#feature-2-fastapi-rest-api)**

### 🎯 3. Arbitrage Detector & Multi-Bookmaker Comparator
Advanced market analysis and opportunity detection
- Multi-bookmaker odds comparison
- Arbitrage opportunity detection (risk-free profit)
- Value bet identification (low margins)
- Optimal stake distribution calculator
- Comprehensive market reports
- Bookmaker performance analysis

**[→ Comparator Guide](FEATURES_GUIDE.md#feature-3-multi-bookmaker-comparator--arbitrage-detector)**

### ⚙️ Core Scraping Engine
Robust and extensible data collection
- Modular architecture (easy to add bookmakers)
- Configuration-based setup (JSON)
- Automatic retry logic with exponential backoff
- Rate limiting and ethical scraping
- Comprehensive error handling
- Detailed logging system

---

## 🛠️ Tech Stack

**Backend & Scraping:**
- Python 3.11+
- BeautifulSoup4 & lxml (HTML parsing)
- Requests (HTTP)
- Pandas (data processing)

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

### Basic Usage

#### 1. Command Line Scraping
```bash
# Scrape and export to CSV
python main.py

# Export to Excel with summary
python main.py --format excel --summary

# Custom filename
python main.py --output my_odds.csv
```

#### 2. Launch Dashboard
```bash
streamlit run dashboard.py
```
Opens at http://localhost:8501

#### 3. Start API Server
```bash
python api.py
```
API at http://localhost:8000  
Docs at http://localhost:8000/docs

#### 4. Run Arbitrage Detector
```bash
python comparator.py
```

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute getting started guide
- **[FEATURES_GUIDE.md](FEATURES_GUIDE.md)** - Complete feature documentation
- **[EXAMPLES.md](EXAMPLES.md)** - Code examples and use cases

---

## 📁 Project Structure

```
tennis-odds-scraper/
├── config/                      # Configuration files
│   ├── bookmakers.json         # Bookmaker settings
│   └── scraping_rules.json     # CSS/XPath selectors
├── scrapers/                   # Scraper modules
│   ├── base_scraper.py        # Abstract base class
│   └── oddsportal_scraper.py  # Oddsportal implementation
├── exporters/                  # Export functionality
│   ├── csv_exporter.py        # CSV export
│   └── excel_exporter.py      # Excel export with formatting
├── utils/                      # Utilities
│   ├── logger.py              # Logging system
│   └── helpers.py             # Helper functions
├── data/                       # Output directory
├── logs/                       # Log files
├── dashboard.py                # Streamlit dashboard ⭐
├── api.py                      # FastAPI REST API ⭐
├── comparator.py               # Arbitrage detector ⭐
├── main.py                     # CLI script
└── requirements.txt            # Dependencies
```

---

## 💡 Use Cases

### 1. Market Analysis
```python
from scrapers import OddsportalScraper
import pandas as pd

with OddsportalScraper() as scraper:
    matches = scraper.scrape_tennis_matches()

df = pd.DataFrame(matches)
print(f"Average margin: {df['bookmaker_margin'].mean():.2f}%")
```

### 2. API Integration
```python
import requests

# Get best value bets
response = requests.get('http://localhost:8000/best-value?limit=5')
best_value = response.json()

for match in best_value:
    print(f"{match['player1']} vs {match['player2']}")
    print(f"Margin: {match['bookmaker_margin']}%\n")
```

### 3. Arbitrage Detection
```python
from comparator import OddsComparator

with OddsComparator() as comparator:
    matches = comparator.scrape_all_bookmakers()
    arbitrage = comparator.find_arbitrage_opportunities(matches)
    
    for opp in arbitrage:
        print(f"💰 Profit: {opp['profit_pct']}%")
        print(f"Stake distribution: {opp['stake1_pct']}% / {opp['stake2_pct']}%")
```

---

## 📊 API Examples

### Get All Matches
```bash
curl http://localhost:8000/matches
```

### Filter by Tournament
```bash
curl "http://localhost:8000/matches?tournament=ATP&limit=10"
```

### Get Statistics
```bash
curl http://localhost:8000/stats
```

### Find Best Value
```bash
curl "http://localhost:8000/best-value?limit=5"
```

**Full API documentation at** http://localhost:8000/docs

---

## 🎯 Adding New Bookmakers

1. Create scraper class:
```python
# scrapers/newbookmaker_scraper.py
from scrapers.base_scraper import BaseScraper

class NewBookmakerScraper(BaseScraper):
    def __init__(self):
        super().__init__('newbookmaker')
    
    def scrape_tennis_matches(self):
        # Your implementation
        pass
```

2. Add configuration in `config/bookmakers.json`
3. Add scraping rules in `config/scraping_rules.json`
4. Import in `scrapers/__init__.py`

**[→ Complete guide in EXAMPLES.md](EXAMPLES.md#adding-new-bookmakers)**

---

## 🎨 Dashboard Features

- **Real-time Data**: Auto-refresh every 30 seconds
- **Interactive Charts**: Hover for details, zoom, pan
- **Smart Filtering**: By margin, odds, tournament
- **Search**: Find specific players or tournaments
- **Export**: One-click CSV/Excel export
- **Responsive**: Works on mobile and desktop

![Dashboard Preview](screenshots/dashboard.png)

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/matches` | GET | All matches with filters |
| `/stats` | GET | Overall statistics |
| `/best-value` | GET | Lowest margin matches |
| `/player/{name}` | GET | Player-specific matches |
| `/tournament/{name}` | GET | Tournament matches |
| `/tournaments` | GET | Available tournaments |
| `/arbitrage` | GET | Arbitrage opportunities |

---

## 🧮 Arbitrage Detection

The comparator automatically detects arbitrage opportunities where you can bet on all outcomes and guarantee profit.

**Example:**
```
Match: Djokovic vs Federer
Bookmaker A: Djokovic @ 2.10
Bookmaker B: Federer @ 2.10

Inverse sum: (1/2.10) + (1/2.10) = 0.952 < 1.0 ✅

Profit: 5.04%
Stake distribution: 52.38% / 47.62%
```

---

## ⚖️ Legal & Ethics

**Important Notes:**
- Respect robots.txt files
- Implement rate limiting
- Use for personal/research purposes only
- Check each website's terms of service
- Don't overload servers

This tool includes built-in rate limiting and ethical scraping practices.

---

## 🐛 Troubleshooting

### No matches found
- Website structure may have changed
- Check `logs/` directory
- Enable verbose mode: `python main.py --verbose`

### Connection errors
- Increase timeout in `config/bookmakers.json`
- Check internet connection
- Verify website is accessible

### Dashboard won't start
```bash
pip install streamlit plotly
streamlit run dashboard.py
```

### API errors
```bash
pip install fastapi uvicorn pydantic
python api.py
```

---

## 📈 Performance

- **Scraping speed**: ~2 seconds per request (with rate limiting)
- **API response**: <100ms average
- **Dashboard**: Real-time updates
- **Memory usage**: ~50MB typical
- **Data processing**: Pandas-optimized

---

## 🤝 Contributing

Contributions welcome! To add a new bookmaker:

1. Fork the repository
2. Create feature branch
3. Add scraper following `base_scraper.py` pattern
4. Add tests
5. Submit pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with best practices for:
- Ethical web scraping
- Clean code architecture
- Professional data analysis
- Modern API design

---

## 📸 Screenshots

### Dashboard
![Dashboard Main](screenshots/dashboard_main.png)
![Interactive Charts](screenshots/charts.png)

### API Documentation
![Swagger UI](screenshots/swagger.png)

### Arbitrage Detection
![Arbitrage Results](screenshots/arbitrage.png)

---

## 🔗 Quick Links

- **Dashboard**: `streamlit run dashboard.py` → http://localhost:8501
- **API**: `python api.py` → http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Comparator**: `python comparator.py`

---

## 📊 Project Stats

- **Lines of Code**: ~3,000+
- **Files**: 20+
- **Features**: 3 major components
- **Endpoints**: 9 API routes
- **Bookmakers**: 1 (extensible)
- **Documentation**: Comprehensive

---

**Built with ❤️ for data analysis and betting insights**

For questions or issues, please open an issue on GitHub.
