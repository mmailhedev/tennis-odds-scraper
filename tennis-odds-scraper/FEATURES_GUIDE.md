# 🚀 Complete Feature Guide - Tennis Odds Scraper

This guide covers all three major features: Dashboard, API, and Arbitrage Comparator.

---

## 📊 Feature 1: Streamlit Dashboard

### What it Does
Interactive web interface with:
- Real-time odds visualization
- Interactive charts (Plotly)
- Best value bets table
- Tournament filtering
- Auto-refresh capability
- CSV/Excel export

### How to Use

#### Start the Dashboard
```bash
streamlit run dashboard.py
```

The dashboard will open automatically at `http://localhost:8501`

#### Dashboard Features

**1. Scraping Controls (Sidebar)**
- Select bookmaker
- Click "Scrape Now" to fetch data
- Enable "Auto-refresh" for live updates (30s interval)

**2. Filters (Sidebar)**
- Max Margin slider: Filter by bookmaker margin
- Min Odds slider: Show only matches above odds threshold

**3. Key Metrics (Top)**
- Total Matches
- Average Margin
- Number of Tournaments
- Best Value (lowest margin)

**4. Visual Analysis (Tabs)**
- **Odds Distribution**: Histogram showing market assessment
- **By Tournament**: Compare margins across tournaments
- **Probability Analysis**: Scatter plot of implied probabilities

**5. Best Value Bets Table**
- Top 10 matches with lowest margins
- Sorted automatically

**6. Search & Filter**
- Search by player or tournament name
- Real-time filtering

**7. Export (Sidebar)**
- Choose CSV or Excel
- Click "Export" to save data

### Screenshots Needed for Portfolio

1. Dashboard overview (full page)
2. Interactive chart with hover details
3. Best value bets table
4. Filter controls in action

---

## 🔌 Feature 2: FastAPI REST API

### What it Does
Professional REST API with:
- Multiple endpoints for odds data
- Automatic documentation (Swagger UI)
- Data validation (Pydantic)
- Error handling
- CORS support

### How to Use

#### Start the API Server
```bash
python api.py
# or
uvicorn api:app --reload
```

Server runs at `http://localhost:8000`

#### Access Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

#### 1. GET `/` - Root
```bash
curl http://localhost:8000/
```
Returns API information and available endpoints.

#### 2. GET `/health` - Health Check
```bash
curl http://localhost:8000/health
```
Check if API is running.

#### 3. GET `/matches` - Get All Matches
```bash
# Get all matches
curl http://localhost:8000/matches

# With filters
curl "http://localhost:8000/matches?tournament=ATP&max_margin=5.0&limit=10"
```

**Query Parameters:**
- `bookmaker`: Bookmaker name (default: oddsportal)
- `tournament`: Filter by tournament (partial match)
- `min_odds`: Minimum odds threshold
- `max_margin`: Maximum bookmaker margin (%)
- `limit`: Limit number of results

**Response:**
```json
[
  {
    "timestamp": "2025-01-15 10:30:00",
    "bookmaker": "oddsportal",
    "tournament": "ATP Australian Open",
    "player1": "Djokovic N.",
    "player2": "Federer R.",
    "odds_player1": 1.50,
    "odds_player2": 2.80,
    "implied_prob1": 66.67,
    "implied_prob2": 35.71,
    "bookmaker_margin": 2.38,
    "match_date": "2025-01-20",
    "match_time": "14:00",
    "url": "https://..."
  }
]
```

#### 4. GET `/stats` - Overall Statistics
```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "total_matches": 45,
  "unique_tournaments": 8,
  "unique_bookmakers": 1,
  "avg_odds": 2.15,
  "avg_margin": 4.52,
  "min_margin": 1.85,
  "max_margin": 8.32,
  "best_value_matches": [...]
}
```

#### 5. GET `/best-value` - Best Value Matches
```bash
curl "http://localhost:8000/best-value?limit=5"
```

Returns top N matches with lowest margins.

#### 6. GET `/player/{player_name}` - Player Matches
```bash
curl http://localhost:8000/player/Djokovic
```

Get all matches for a specific player (case-insensitive).

#### 7. GET `/tournament/{tournament_name}` - Tournament Matches
```bash
curl "http://localhost:8000/tournament/ATP Australian Open"
```

#### 8. GET `/tournaments` - Available Tournaments
```bash
curl http://localhost:8000/tournaments
```

**Response:**
```json
[
  {
    "name": "ATP Australian Open",
    "url": "https://..."
  }
]
```

#### 9. GET `/arbitrage` - Arbitrage Opportunities
```bash
curl "http://localhost:8000/arbitrage?min_profit=0.5"
```

Find potential arbitrage opportunities.

### Using the API in Python

```python
import requests

# Get all matches
response = requests.get('http://localhost:8000/matches')
matches = response.json()

# Get filtered matches
response = requests.get(
    'http://localhost:8000/matches',
    params={
        'tournament': 'ATP',
        'max_margin': 5.0,
        'limit': 10
    }
)
filtered = response.json()

# Get statistics
stats = requests.get('http://localhost:8000/stats').json()
print(f"Total matches: {stats['total_matches']}")
print(f"Average margin: {stats['avg_margin']}%")
```

### Using the API in JavaScript

```javascript
// Fetch matches
fetch('http://localhost:8000/matches?tournament=ATP&limit=10')
  .then(response => response.json())
  .then(data => {
    console.log('Matches:', data);
  });

// Fetch stats
fetch('http://localhost:8000/stats')
  .then(response => response.json())
  .then(stats => {
    console.log(`Total: ${stats.total_matches}`);
    console.log(`Avg Margin: ${stats.avg_margin}%`);
  });
```

---

## 🎯 Feature 3: Multi-Bookmaker Comparator & Arbitrage Detector

### What it Does
Advanced analysis tool:
- Compare odds across multiple bookmakers
- Find arbitrage opportunities (risk-free profit)
- Identify value bets (low margins)
- Calculate optimal bet distribution
- Generate comprehensive reports

### How to Use

#### Method 1: Command Line

```bash
python comparator.py
```

This will:
1. Scrape all bookmakers
2. Find arbitrage opportunities
3. Find value bets
4. Compare bookmakers
5. Print results

#### Method 2: Python Script

```python
from comparator import OddsComparator

# Create comparator
with OddsComparator() as comparator:
    # Scrape all bookmakers
    matches = comparator.scrape_all_bookmakers()
    print(f"Scraped {len(matches)} matches")
    
    # Find arbitrage (risk-free profit)
    arbitrage = comparator.find_arbitrage_opportunities(
        matches,
        min_profit=0.5  # Minimum 0.5% profit
    )
    
    if arbitrage:
        for opp in arbitrage:
            print(f"\n💰 ARBITRAGE FOUND!")
            print(f"Match: {opp['player1']} vs {opp['player2']}")
            print(f"Odds: {opp['best_odds1']} ({opp['bookmaker1']}) - "
                  f"{opp['best_odds2']} ({opp['bookmaker2']})")
            print(f"Profit: {opp['profit_pct']}%")
            print(f"Bet Distribution:")
            print(f"  - {opp['stake1_pct']}% on {opp['player1']}")
            print(f"  - {opp['stake2_pct']}% on {opp['player2']}")
    
    # Find value bets
    value_bets = comparator.find_value_bets(
        matches,
        margin_threshold=3.0  # Margin < 3%
    )
    
    print(f"\n✨ Found {len(value_bets)} value bets")
    
    # Compare bookmakers
    comparison = comparator.compare_bookmakers(matches)
    print("\n📊 Bookmaker Comparison:")
    print(comparison)
```

### Understanding Arbitrage

**What is Arbitrage?**
Arbitrage is when you can bet on all outcomes of a match and **guarantee a profit** regardless of the result.

**Example:**
```
Match: Player A vs Player B

Bookmaker 1: Player A @ 2.10
Bookmaker 2: Player B @ 2.10

Inverse sum: (1/2.10) + (1/2.10) = 0.952

Since 0.952 < 1.0, this is ARBITRAGE!

Profit: ((1/0.952) - 1) * 100 = 5.04%

If you bet 100€:
- Bet 52.38€ on Player A @ 2.10 (returns 110€)
- Bet 47.62€ on Player B @ 2.10 (returns 100€)
Total stake: 100€
Guaranteed return: 105.04€
Profit: 5.04€ (5.04%)
```

### API Functions

#### Generate Full Report
```python
from comparator import OddsComparator

with OddsComparator() as comparator:
    matches = comparator.scrape_all_bookmakers()
    report = comparator.generate_report(matches)
    
    print(f"Total matches: {report['total_matches']}")
    print(f"Arbitrage opportunities: {report['arbitrage_count']}")
    print(f"Value bets: {report['value_bets_count']}")
```

#### Quick Functions
```python
from comparator import compare_odds, find_arbitrage

# Quick comparison
report = compare_odds()

# Quick arbitrage search
arbitrage = find_arbitrage(min_profit=1.0)
```

### Export Results

```python
from comparator import OddsComparator
from exporters import ExcelExporter
import pandas as pd

with OddsComparator() as comparator:
    matches = comparator.scrape_all_bookmakers()
    
    # Find arbitrage
    arbitrage = comparator.find_arbitrage_opportunities(matches)
    
    # Export to Excel
    if arbitrage:
        df = pd.DataFrame(arbitrage)
        exporter = ExcelExporter()
        
        # Convert to dict format for exporter
        exporter.export(
            df.to_dict('records'),
            'arbitrage_opportunities.xlsx',
            include_summary=True
        )
```

---

## 🎬 Demo Workflow

### Complete Portfolio Demo

```bash
# 1. Start Dashboard in one terminal
streamlit run dashboard.py

# 2. Start API in another terminal
python api.py

# 3. Run comparator analysis
python comparator.py

# 4. Test API endpoints
curl http://localhost:8000/stats

# 5. Access dashboard at http://localhost:8501
# 6. Access API docs at http://localhost:8000/docs
```

---

## 📸 Portfolio Screenshots Checklist

For your portfolio/GitHub README, capture:

### Dashboard
- [ ] Full dashboard view
- [ ] Interactive charts (with hover)
- [ ] Best value bets table
- [ ] Filters in action
- [ ] Export functionality

### API
- [ ] Swagger UI (http://localhost:8000/docs)
- [ ] Example API response (JSON)
- [ ] Terminal showing API request
- [ ] Multiple endpoints listed

### Comparator
- [ ] Terminal output showing arbitrage found
- [ ] Bookmaker comparison table
- [ ] Value bets list
- [ ] Example calculations

---

## 🚀 Presentation Tips

When showing this in an interview or on GitHub:

1. **Start with Dashboard** (visual impact)
   - "I built an interactive dashboard with real-time data"
   - Show filtering and charts

2. **Show API** (backend skills)
   - "I created a REST API with automatic documentation"
   - Demo Swagger UI
   - Show a curl request

3. **Explain Arbitrage** (business logic)
   - "I implemented arbitrage detection algorithms"
   - Show profitable opportunity
   - Explain the math

4. **Mention Skills**
   - Web scraping (BeautifulSoup, requests)
   - Data processing (pandas)
   - API development (FastAPI)
   - Frontend (Streamlit)
   - Algorithms (arbitrage detection)
   - Error handling & logging
   - Clean architecture

---

## 🎯 Key Selling Points

1. **Complete Full-Stack Project**
   - Backend (scrapers, API)
   - Frontend (dashboard)
   - Data processing
   - Business logic

2. **Production-Ready Code**
   - Error handling
   - Logging
   - Type hints
   - Documentation
   - Tests (can add)

3. **Scalable Architecture**
   - Easy to add bookmakers
   - Modular design
   - Configuration-based

4. **Real Business Value**
   - Arbitrage detection = real money
   - Value bet identification
   - Market analysis

---

## 🔗 Quick Links

- Dashboard: `streamlit run dashboard.py` → http://localhost:8501
- API: `python api.py` → http://localhost:8000
- API Docs: http://localhost:8000/docs
- Comparator: `python comparator.py`

---

Voilà ! Tu as maintenant **trois fonctionnalités impressionnantes** pour ton portfolio ! 🎉
