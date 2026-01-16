# 🎾 Tennis Odds Scraper - Command Cheat Sheet

Quick reference for all commands and usage patterns.

---

## 🚀 Setup & Installation

```bash
# Clone repository
git clone <repository-url>
cd tennis-odds-scraper

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate              # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit; import fastapi; print('✅ All dependencies installed')"
```

---

## 📊 Dashboard Commands

```bash
# Start dashboard
streamlit run dashboard.py

# Start on specific port
streamlit run dashboard.py --server.port 8502

# Start without browser auto-open
streamlit run dashboard.py --server.headless true
```

**Access**: http://localhost:8501

---

## 🔌 API Commands

```bash
# Start API server
python api.py

# Start with uvicorn (alternative)
uvicorn api:app --reload

# Start on specific port
uvicorn api:app --port 8080 --reload

# Start for production (no reload)
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🎯 Comparator Commands

```bash
# Run comparator (interactive)
python comparator.py

# Import in script
python -c "from comparator import find_arbitrage; print(find_arbitrage())"
```

---

## 📥 CLI Scraping Commands

```bash
# Basic scraping (CSV output)
python main.py

# Excel output
python main.py --format excel

# Excel with summary
python main.py --format excel --summary

# Custom filename
python main.py --output my_odds.csv

# Custom output directory
python main.py --output-dir ./results

# Both CSV and Excel
python main.py --format both

# Append to existing CSV
python main.py --append --output daily_odds.csv

# Verbose logging
python main.py --verbose

# Complete example
python main.py \
  --format excel \
  --summary \
  --output "australian_open.xlsx" \
  --output-dir ./tournaments \
  --verbose
```

---

## 🧪 Testing Commands

```bash
# Run all tests (if you add tests)
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_scraper.py

# Verbose output
pytest -v
```

---

## 🔍 API Testing Commands

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get all matches
curl http://localhost:8000/matches

# Get filtered matches
curl "http://localhost:8000/matches?tournament=ATP&limit=10"

# Get statistics
curl http://localhost:8000/stats

# Get best value bets
curl "http://localhost:8000/best-value?limit=5"

# Get player matches
curl http://localhost:8000/player/Djokovic

# Get tournament matches
curl "http://localhost:8000/tournament/Australian%20Open"

# Get tournaments
curl http://localhost:8000/tournaments

# Find arbitrage
curl "http://localhost:8000/arbitrage?min_profit=0.5"
```

### Using httpie (prettier)

```bash
# Install httpie
pip install httpie

# Get matches
http GET http://localhost:8000/matches

# With parameters
http GET http://localhost:8000/matches tournament==ATP limit==10

# Get stats
http GET http://localhost:8000/stats
```

### Using Python requests

```python
import requests

# Get matches
r = requests.get('http://localhost:8000/matches')
matches = r.json()

# With filters
params = {'tournament': 'ATP', 'max_margin': 5.0, 'limit': 10}
r = requests.get('http://localhost:8000/matches', params=params)
filtered = r.json()

# Get stats
r = requests.get('http://localhost:8000/stats')
stats = r.json()
```

---

## 📝 Python Script Examples

### Basic Scraping

```python
from scrapers import OddsportalScraper
from exporters import CSVExporter

# Scrape and export
with OddsportalScraper() as scraper:
    matches = scraper.scrape_tennis_matches()

exporter = CSVExporter()
exporter.export(matches, 'tennis_odds.csv')
```

### API Usage

```python
import requests

# Get data from API
response = requests.get('http://localhost:8000/matches')
matches = response.json()

print(f"Found {len(matches)} matches")
```

### Arbitrage Detection

```python
from comparator import OddsComparator

with OddsComparator() as comparator:
    matches = comparator.scrape_all_bookmakers()
    arbitrage = comparator.find_arbitrage_opportunities(matches)
    
    for opp in arbitrage:
        print(f"Profit: {opp['profit_pct']}%")
```

---

## 🛠️ Development Commands

```bash
# Format code with black (if installed)
black .

# Sort imports with isort (if installed)
isort .

# Type checking with mypy (if installed)
mypy .

# Linting with flake8 (if installed)
flake8 .
```

---

## 📦 Deployment Commands

### Local

```bash
# Run everything locally
# Terminal 1
streamlit run dashboard.py

# Terminal 2
python api.py

# Terminal 3
python comparator.py
```

### VPS (Linux Server)

```bash
# SSH to server
ssh user@your-server-ip

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y

# Clone and setup
git clone <your-repo>
cd tennis-odds-scraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with nohup (background)
nohup python api.py > api.log 2>&1 &
nohup streamlit run dashboard.py > dashboard.log 2>&1 &

# Check if running
ps aux | grep python

# View logs
tail -f api.log
tail -f dashboard.log
```

### Using screen (recommended for VPS)

```bash
# Install screen
sudo apt install screen

# Start screen session for API
screen -S api
python api.py
# Press Ctrl+A then D to detach

# Start screen session for dashboard
screen -S dashboard
streamlit run dashboard.py
# Press Ctrl+A then D to detach

# List screens
screen -ls

# Reattach to screen
screen -r api
screen -r dashboard

# Kill screen
screen -X -S api quit
```

---

## 🔄 Automation Commands

### Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line to scrape every 2 hours
0 */2 * * * cd /path/to/tennis-odds-scraper && /path/to/venv/bin/python main.py >> /var/log/scraper.log 2>&1

# Add line to scrape daily at 9 AM
0 9 * * * cd /path/to/tennis-odds-scraper && /path/to/venv/bin/python main.py

# View cron logs
tail -f /var/log/scraper.log
```

### Task Scheduler (Windows)

```powershell
# Create task that runs daily at 9 AM
schtasks /create /tn "TennisOddsScraper" /tr "C:\path\to\python.exe C:\path\to\main.py" /sc daily /st 09:00
```

### Python Scheduler

```python
# scheduler.py
import schedule
import time
from main import main

schedule.every(2).hours.do(main)

while True:
    schedule.run_pending()
    time.sleep(60)
```

Run:
```bash
python scheduler.py
```

---

## 🐛 Debugging Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check specific package
pip show streamlit

# Reinstall package
pip install --force-reinstall streamlit

# Check logs
cat logs/scraper_*.log

# Tail logs in real-time
tail -f logs/scraper_*.log

# Run with Python debugger
python -m pdb main.py

# Check port usage
lsof -i :8000    # Mac/Linux
netstat -ano | findstr :8000    # Windows
```

---

## 🧹 Cleanup Commands

```bash
# Remove pycache
find . -type d -name "__pycache__" -exec rm -r {} +

# Remove log files
rm -rf logs/*.log

# Remove data files
rm -rf data/*.csv data/*.xlsx

# Remove virtual environment
rm -rf venv

# Clean everything
find . -type d -name "__pycache__" -exec rm -r {} +
rm -rf logs/*.log
rm -rf data/*.csv data/*.xlsx
```

---

## 📊 Monitoring Commands

```bash
# Monitor API health
watch -n 5 curl http://localhost:8000/health

# Monitor with stats
watch -n 10 'curl -s http://localhost:8000/stats | python -m json.tool'

# Check API response time
time curl http://localhost:8000/matches > /dev/null

# Monitor logs
tail -f logs/scraper_*.log

# Monitor system resources
top
htop    # If installed
```

---

## 🔒 Security Commands

```bash
# Generate secret key for API (if needed)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check for security issues (if safety installed)
pip install safety
safety check

# Update all packages
pip list --outdated
pip install --upgrade <package>
```

---

## 📤 Export & Backup Commands

```bash
# Export Python environment
pip freeze > requirements.txt

# Backup data
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/

# Copy to remote server
scp backup_*.tar.gz user@server:/backup/

# Download from server
scp user@server:/path/tennis_odds.csv ./
```

---

## 🎯 Quick Workflows

### Complete Demo Workflow

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test basic scraping
python main.py --verbose

# 3. Start dashboard (Terminal 1)
streamlit run dashboard.py

# 4. Start API (Terminal 2)
python api.py

# 5. Test API
curl http://localhost:8000/stats

# 6. Run comparator (Terminal 3)
python comparator.py
```

### Daily Usage Workflow

```bash
# Morning: Scrape and analyze
python main.py --format excel --summary --output daily_$(date +%Y%m%d).xlsx

# Check for arbitrage
python comparator.py

# Export for analysis
python -c "from scrapers import OddsportalScraper; from exporters import ExcelExporter; ..."
```

---

## 🆘 Common Issues & Solutions

### Issue: streamlit command not found
```bash
# Solution
pip install streamlit
# Or
python -m streamlit run dashboard.py
```

### Issue: Port already in use
```bash
# Find process using port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
streamlit run dashboard.py --server.port 8502
uvicorn api:app --port 8080
```

### Issue: Module not found
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

# Reinstall requirements
pip install -r requirements.txt
```

---

## 📚 Quick Reference URLs

- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

---

**Keep this cheat sheet handy! 📌**
