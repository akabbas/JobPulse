# Job Market Analytics Dashboard

A comprehensive web scraping and analytics project that analyzes software engineering job market trends from Indeed and Glassdoor.

## 🚀 Quick Start Guide

### 1. **Setup Your Environment**

```bash
# Navigate to your project directory
cd ~/Documents/job_market_analytics

# Activate your virtual environment
source ~/beautifulsoup_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Run the Application**

```bash
# Run the main application
python main.py
```

### 3. **View Results**

- Check the `output/` directory for generated charts and visualizations
- Check the `data/` directory for scraped job data
- Check the `logs/` directory for execution logs

## 📊 What You'll Get

The application will:
- Scrape job postings from Indeed and Glassdoor
- Extract technical skills from job descriptions
- Analyze skill trends and popularity
- Generate visualizations and reports
- Save data for further analysis

## 🛠️ Project Structure

```
job_market_analytics/
├── scrapers/              # Web scraping modules
│   ├── indeed_scraper.py
│   └── glassdoor_scraper.py
├── data_processing/       # Data cleaning and processing
│   └── data_cleaner.py
├── analysis/             # Data analysis and trends
│   └── skill_trends.py
├── config/               # Configuration settings
│   └── settings.py
├── output/               # Generated charts and reports
├── data/                 # Scraped job data
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
├── main.py              # Main application
└── README.md            # This file
```

## 🎯 Features

- **Multi-source scraping**: Indeed and Glassdoor
- **Skill extraction**: Automatically identifies technical skills
- **Data cleaning**: Standardizes and validates job data
- **Trend analysis**: Identifies popular skills and combinations
- **Visualization**: Creates comprehensive charts and graphs
- **Resume-ready**: Perfect for showcasing data engineering skills

## 📈 Sample Output

The application generates:
- **Skill frequency analysis** by category
- **Top skill combinations** in demand
- **Job type analysis** (Frontend, Backend, Full Stack, etc.)
- **Interactive visualizations** and charts
- **Summary reports** with key insights

## 🔧 Customization

### Adding New Skills
Edit `config/settings.py` to add new skills to track:

```python
TECH_SKILLS = {
    'programming_languages': [
        # Add new languages here
    ],
    'frameworks': [
        # Add new frameworks here
    ],
    # ... other categories
}
```

### Modifying Search Keywords
Edit the `SEARCH_KEYWORDS` list in `config/settings.py`:

```python
SEARCH_KEYWORDS = [
    'software engineer',
    'data scientist',
    'machine learning engineer',
    # Add your keywords here
]
```

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure you're in the correct directory and virtual environment is activated
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Permission Errors**: Check file permissions in output/ and logs/ directories
4. **Scraping Issues**: The scrapers include delays to be respectful to websites

### Debug Mode:
```bash
# Run with verbose logging
python main.py 2>&1 | tee debug.log
```

## 📊 Expected Results

After running the application, you should see:

1. **Console Output**: Real-time progress and summary statistics
2. **Generated Files**:
   - `output/skill_analysis.png` - Skills analysis charts
   - `output/skills_by_job_type.png` - Job type analysis
   - `data/jobs_YYYYMMDD_HHMMSS.csv` - Raw job data
   - `logs/main.log` - Application logs

3. **Sample Console Output**:
```
============================================================
TOP SOFTWARE ENGINEERING SKILLS ANALYSIS
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
SUMMARY REPORT
============================================================
Total jobs analyzed: 156
Jobs with salary info: 89
Average skills per job: 4.2
Most common job type: Full Stack
```

## 🎓 Learning Outcomes

By building this project, you'll learn:
- Web scraping with BeautifulSoup
- Data processing with Pandas
- Statistical analysis and visualization
- ETL pipeline development
- Python best practices
- Market research and analysis
- Database design concepts
- Business intelligence skills

## 🚀 Next Steps

1. **Extend the scrapers** to include more job sites
2. **Add database integration** (PostgreSQL, Snowflake)
3. **Create a web dashboard** using Flask/Django
4. **Add machine learning** for salary prediction
5. **Implement real-time monitoring** with alerts

## 📄 License

This project is for educational and portfolio purposes.

---

**Perfect for transitioning from Snowflake development to Python/SQL roles!** 