# 🚀 JobPulse Local Development Guide

## Quick Start

### 1. Setup Local Environment
```bash
# Make scripts executable
chmod +x setup_local.sh start_local.sh

# Run setup script
./setup_local.sh
```

### 2. Test Environment
```bash
# Test that everything is working
python test_local.py
```

### 3. Start Development Server
```bash
# Option 1: Use the start script
./start_local.sh

# Option 2: Manual start
cd web_dashboard
source ../venv/bin/activate
python app.py
```

### 4. Access the Application
Open your browser and go to: **http://localhost:5001**

## 🔧 Development Workflow

### Making Changes
1. **Edit files** in your preferred editor
2. **Save changes** - Flask auto-reloads in debug mode
3. **Test immediately** - no rebuild needed!
4. **Check logs** in the terminal for debugging

### Testing API Endpoints
```bash
# Test regular search
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "python developer", "limit": 5}'

# Test enhanced search
curl -X POST http://localhost:5001/enhanced_search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "python developer", "limit": 5}'

# Test health check
curl http://localhost:5001/health
```

### Viewing Logs
```bash
# View scraper logs
tail -f logs/enhanced_playwright_scraper.log
tail -f logs/api_sources_scraper.log

# View app logs (in terminal where you started the server)
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'flask'"
```bash
# Solution: Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. "Address already in use"
```bash
# Solution: Kill existing processes
lsof -ti:5001 | xargs kill -9
# or
pkill -f "python app.py"
```

#### 3. Playwright browser issues
```bash
# Solution: Reinstall Playwright browsers
playwright install chromium
playwright install-deps
```

#### 4. Import errors with scrapers
```bash
# Solution: Check file paths and syntax
python test_local.py
```

### Debug Mode
The Flask app runs in debug mode locally, which means:
- **Auto-reload** when files change
- **Detailed error messages**
- **Interactive debugger** on errors

## 📁 Project Structure

```
JobPulse/
├── web_dashboard/          # Main Flask application
│   ├── app.py             # Main application file
│   └── templates/         # HTML templates
├── scrapers/              # All scraper modules
│   ├── enhanced_playwright_scraper.py
│   ├── api_sources_scraper.py
│   └── ... (other scrapers)
├── data_processing/       # Data cleaning and processing
├── analysis/             # Skills analysis and trends
├── config/               # Configuration files
├── logs/                 # Log files (created automatically)
├── data/                 # Data storage
├── output/               # Output files
└── venv/                 # Virtual environment
```

## 🚀 Deployment Workflow

### Local Development (Fast)
1. **Make changes** to code
2. **Test immediately** on localhost:5000
3. **Debug easily** with print statements
4. **Iterate quickly** - no rebuilds needed

### Docker Deployment (When Ready)
1. **Test everything locally** first
2. **Commit changes** to git
3. **Deploy to Docker** only when ready
4. **Much faster** since you know it works

## 🔍 Useful Commands

### Development
```bash
# Start local server
./start_local.sh

# Test environment
python test_local.py

# View logs
tail -f logs/*.log

# Install new dependencies
pip install package_name
```

### Docker (when needed)
```bash
# Build and start Docker
docker-compose up -d

# View Docker logs
docker-compose logs app

# Stop Docker
docker-compose down
```

## 🎯 Benefits of Local Development

### ⚡ Speed
- **No Docker rebuilds** (saves 2-3 minutes per test)
- **Instant feedback** on changes
- **Quick debugging** with print statements

### 🔍 Better Debugging
- **Direct access** to logs
- **Interactive debugging** with breakpoints
- **Real-time error messages**

### 🛠️ Easier Development
- **Hot reload** (Flask debug mode)
- **Direct file editing** and testing
- **No container isolation** issues

## 📝 Tips for Efficient Development

1. **Use the test script** to verify your environment
2. **Check logs** for debugging information
3. **Test API endpoints** with curl
4. **Use print statements** for quick debugging
5. **Commit frequently** to git
6. **Only deploy to Docker** when features are complete

## 🆘 Getting Help

If you encounter issues:

1. **Run the test script**: `python test_local.py`
2. **Check the logs**: `tail -f logs/*.log`
3. **Verify virtual environment**: `which python` (should point to venv)
4. **Check Flask installation**: `python -c "import flask; print(flask.__version__)"`

---

**Happy coding! 🚀**
