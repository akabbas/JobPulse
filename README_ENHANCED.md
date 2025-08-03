# Enhanced Job Market Analytics Dashboard

A comprehensive web scraping and analytics project that analyzes software engineering job market trends from multiple sources with advanced search capabilities, web dashboard, and database integration.

## 🚀 New Features

### **Multiple Job Sources**
- **Indeed** - Primary job board scraping
- **LinkedIn** - Professional network job listings
- **Stack Overflow Jobs** - Developer-focused job board

### **Advanced Search Engine**
- Filter by specific job titles and keywords
- Search by required skills and experience level
- Salary range filtering
- Location-based filtering
- Multi-source search capabilities

### **Web Dashboard**
- Interactive Flask web application
- Real-time job search and filtering
- Skills analysis visualization
- Responsive Bootstrap UI

### **Database Integration**
- PostgreSQL support with SQLAlchemy ORM
- Snowflake integration stub
- Job data persistence and retrieval
- Advanced querying capabilities

## 🛠️ Quick Start

### **1. Setup Environment**
```bash
cd ~/Documents/job_market_analytics

# Activate virtual environment
source ~/beautifulsoup_env/bin/activate

# Install enhanced dependencies
pip install -r requirements.txt
```

### **2. Test Everything Works**
```bash
# Run comprehensive tests
python test_enhanced.py
```

### **3. Run Enhanced Application**
```bash
# Run the enhanced main application
python main_enhanced.py
```

### **4. Start Web Dashboard**
```bash
# Navigate to web dashboard
cd web_dashboard

# Start Flask app
python app.py

# Open browser to http://localhost:5000
```

## 📊 Enhanced Project Structure

```
job_market_analytics/
├── scrapers/                    # Multi-source scrapers
│   ├── indeed_scraper.py       # Indeed scraper
│   ├── linkedin_scraper.py     # LinkedIn scraper
│   └── stackoverflow_scraper.py # Stack Overflow scraper
├── search_engine.py            # Advanced search & filtering
├── data_processing/            # Data cleaning & processing
├── analysis/                   # Skills analysis & trends
├── database/                   # Database integration
│   └── db_manager.py          # PostgreSQL & Snowflake
├── web_dashboard/              # Flask web application
│   ├── app.py                 # Flask app
│   └── templates/             # HTML templates
│       └── index.html         # Dashboard UI
├── config/                     # Configuration settings
├── main_enhanced.py           # Enhanced main application
├── test_enhanced.py           # Comprehensive tests
└── requirements.txt            # Updated dependencies
```

## 🎯 Key Features

### **Multi-Source Scraping**
- Scrapes from 3 major job sites simultaneously
- Robust error handling and rate limiting
- Configurable search parameters
- Sample data fallback for testing

### **Advanced Search & Filtering**
```python
from search_engine import SearchCriteria, filter_jobs

# Create search criteria
criteria = SearchCriteria(
    keywords=['python developer', 'software engineer'],
    location='San Francisco',
    skills_required=['python', 'react', 'aws'],
    salary_min=80000,
    salary_max=150000
)

# Filter jobs
filtered_jobs = filter_jobs(all_jobs, criteria)
```

### **Web Dashboard Features**
- **Real-time Search**: Search across multiple job sites
- **Advanced Filtering**: Filter by skills, salary, location
- **Skills Analysis**: Interactive charts showing skill trends
- **Job Results**: Detailed job listings with skill badges
- **Responsive Design**: Works on desktop and mobile

### **Database Integration**
```python
from database.db_manager import DatabaseManager

# Initialize database
db_manager = DatabaseManager('postgresql://user:pass@localhost:5432/jobmarket')
db_manager.create_tables()

# Save jobs
db_manager.save_jobs(jobs)

# Query jobs
jobs = db_manager.get_jobs_by_criteria(
    keyword='python',
    location='San Francisco',
    limit=50
)
```

## 🔧 Configuration

### **Database Setup**
```bash
# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/jobmarket"

# Snowflake (optional)
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-user"
export SNOWFLAKE_PASSWORD="your-password"
```

### **Custom Search Keywords**
Edit `config/settings.py`:
```python
SEARCH_KEYWORDS = [
    'software engineer',
    'data engineer',
    'machine learning engineer',
    'full stack developer',
    'devops engineer'
]
```

## 📈 Sample Output

### **Enhanced Console Output**
```
============================================================
ENHANCED SOFTWARE ENGINEERING SKILLS ANALYSIS
============================================================

PROGRAMMING LANGUAGES:
----------------------------------------
python                   45.2%
javascript               38.7%
java                     32.1%
typescript               28.9%
c++                      15.4%

FRAMEWORKS:
----------------------------------------
react                    42.3%
node.js                  35.6%
express                  28.9%
django                   25.4%
flask                    18.7%

============================================================
ENHANCED SUMMARY REPORT
============================================================
Total jobs analyzed: 156
Jobs with salary info: 89
Average skills per job: 4.2
Most common job type: Full Stack

Jobs by source:
  indeed: 52 jobs
  linkedin: 48 jobs
  stackoverflow: 56 jobs
```

### **Web Dashboard Features**
- Interactive job search form
- Real-time skills analysis charts
- Advanced filtering options
- Job result cards with skill badges
- Responsive Bootstrap design

## 🧪 Testing

### **Run All Tests**
```bash
python test_enhanced.py
```

### **Test Individual Components**
```bash
# Test scrapers
python -c "from scrapers.linkedin_scraper import LinkedInScraper; print('✅ LinkedIn scraper works')"

# Test search engine
python -c "from search_engine import SearchCriteria; print('✅ Search engine works')"

# Test Flask app
cd web_dashboard && python -c "from app import app; print('✅ Flask app works')"
```

## 🚀 Deployment Options

### **Local Development**
```bash
# Run enhanced application
python main_enhanced.py

# Run web dashboard
cd web_dashboard && python app.py
```

### **Production Deployment**
```bash
# Set up PostgreSQL database
# Configure environment variables
# Deploy Flask app with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### **Docker Deployment**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "web_dashboard/app.py"]
```

## 🎓 Resume Impact

This enhanced project demonstrates:

### **Technical Skills**
- **Multi-source web scraping** with anti-bot handling
- **Advanced search algorithms** and filtering logic
- **Full-stack web development** with Flask
- **Database design** and ORM integration
- **API development** and RESTful endpoints
- **Data visualization** with Chart.js
- **Error handling** and logging

### **Business Value**
- **Market research** capabilities across multiple sources
- **Competitive analysis** and trend identification
- **Data-driven insights** for job market analysis
- **Scalable architecture** for enterprise use
- **User-friendly interface** for non-technical users

### **Advanced Features**
- **Real-time data processing** and analysis
- **Multi-threaded scraping** for performance
- **Database persistence** for historical analysis
- **Advanced filtering** and search capabilities
- **Responsive web design** for mobile users

## 🔮 Next Steps

1. **Add more job sites** (Glassdoor, Monster, etc.)
2. **Implement machine learning** for salary prediction
3. **Add user authentication** and saved searches
4. **Create mobile app** using React Native
5. **Add real-time notifications** for new jobs
6. **Implement advanced analytics** and reporting
7. **Add job application tracking** features

## 📄 License

This project is for educational and portfolio purposes.

---

**Perfect for transitioning from Snowflake development to Python/SQL roles with full-stack capabilities!** 