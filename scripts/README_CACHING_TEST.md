# Smart Caching System Test

This test script verifies that the entire smart caching architecture is working correctly.

## What It Tests

The test performs a comprehensive end-to-end verification of:

1. **First Search** → Scrapes jobs and saves to database
2. **Cache Verification** → Confirms jobs are stored in database
3. **Second Search** → Should return cached results
4. **Data Consistency** → Ensures both searches return identical results
5. **Database Persistence** → Verifies jobs and searches are saved

## Prerequisites

1. **Flask App Running**: The web dashboard must be running
2. **Database Ready**: Database tables must be created
3. **Virtual Environment**: Python dependencies must be installed

## How to Run

### Step 1: Start the Flask App
```bash
cd web_dashboard
source ../venv/bin/activate
python app.py
```

### Step 2: Run the Test (in a new terminal)
```bash
cd scripts
source ../venv/bin/activate
python test_caching.py
```

## Expected Output

### Successful Test:
```
🧪 Testing Smart Caching Architecture
==================================================
🔍 Step 1: Checking if Flask app is running...
✅ Flask app is running

🔍 Step 2: Performing first search (should not be cached)...
✅ First search successful:
   - Jobs found: 15
   - Search ID: python_developer_United_States_20250127_143022
   - Source: scraped
   - From cache: False
✅ First search was NOT cached (as expected)

⏳ Step 3: Waiting 10 seconds for database operations...

🔍 Step 4: Performing identical search (should be cached)...
✅ Second search successful:
   - Jobs found: 15
   - Search ID: python_developer_United_States_20250127_143032
   - Source: database_cache
   - From cache: True

🔍 Step 5: Verifying search results consistency...
✅ Search results are identical

🔍 Step 6: Verifying database persistence...
✅ Total jobs in database: 15
✅ Total searches in database: 2
✅ Recent searches for 'python developer':
   - python developer in United States: 15 jobs at 2025-01-27 14:30:32
   - python developer in United States: 15 jobs at 2025-01-27 14:30:22

🔍 Step 7: Final verification...
✅ Second search was served from cache
✅ Jobs were successfully saved to database
✅ Searches were successfully logged to database

==================================================
🎉 CACHING SYSTEM TEST RESULTS
==================================================
✅ ALL TESTS PASSED!
✅ Smart caching architecture is working correctly
✅ Database persistence is working
✅ Cache hits are functioning

📊 Test Summary:
   - First search jobs: 15
   - Second search jobs: 15
   - Database jobs: 15
   - Database searches: 2
   - Cache hit on second search: True

🎯 RECOMMENDATION: Caching system is ready for production!
```

### Failed Test:
If any step fails, the script will show detailed error information and recommendations.

## What Success Means

✅ **Caching System Working**: Jobs are cached after first search
✅ **Database Persistence**: Jobs and searches are saved to database
✅ **Cache Hits**: Subsequent searches return cached data
✅ **Data Consistency**: Cached results match original results
✅ **Performance**: Second search is much faster (no scraping)

## Troubleshooting

### Flask App Not Running
```
❌ Flask app is not running: Connection refused
💡 Please start the Flask app first:
   cd web_dashboard && python app.py
```

### Database Issues
- Ensure database tables are created
- Check database file permissions
- Verify SQLite is working

### Scraping Issues
- Check if scrapers are working
- Verify API keys and rate limits
- Check network connectivity

## Test Configuration

You can modify the test by editing these variables in `test_caching.py`:

```python
# Configuration
base_url = "http://localhost:5002"  # Flask app URL
search_data = {
    "keyword": "python developer",   # Search keyword
    "location": "United States",     # Search location
    "sources": ["enhanced", "api_sources", "reddit"],  # Data sources
    "limit": 20                      # Number of jobs to fetch
}
```

## Next Steps

After successful testing:

1. **Production Deployment**: The caching system is ready for production
2. **Performance Monitoring**: Monitor cache hit rates and response times
3. **Scaling**: The system can now handle more users efficiently
4. **Analytics**: Use the database for historical job market analysis
