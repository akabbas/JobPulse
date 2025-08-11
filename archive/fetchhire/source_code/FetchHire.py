from flask import Flask, render_template, jsonify, request
from database.snowflake_manager import FetchHireSnowflakeManager
from scrapers.fast_scraper import FastJobScraper
from scrapers.advanced_scraper import AdvancedJobScraper
from scrapers.playwright_scraper_working import WorkingPlaywrightScraper
import logging
import json
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Display FetchHire banner on startup
def display_banner():
    """Display the FetchHire banner"""
    try:
        with open('FETCHHIRE_BANNER.txt', 'r') as f:
            banner = f.read()
            print(banner)
    except FileNotFoundError:
        print("🚀 FetchHire - Advanced Job Scraper with 403 Error Bypass")
        print("=" * 60)

# Initialize components
snowflake_manager = FetchHireSnowflakeManager()
job_scraper = FastJobScraper()  # Use the fast scraper
advanced_scraper = AdvancedJobScraper()  # Use the advanced scraper
playwright_scraper = WorkingPlaywrightScraper()  # Use the working Playwright scraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global event loop for async operations
loop = None

def get_or_create_loop():
    """Get or create event loop for async operations"""
    global loop
    if loop is None:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    return loop

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test Snowflake connection
        if snowflake_manager.connect_connector():
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'scraper': 'ready',
                'message': 'FetchHire is running smoothly!'
            })
        else:
            return jsonify({
                'status': 'degraded',
                'database': 'disconnected',
                'scraper': 'ready',
                'message': 'Database connection failed'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/jobs')
def get_jobs():
    """Get all jobs from database"""
    try:
        if not snowflake_manager.connect_connector():
            return jsonify({'error': 'Database connection failed'}), 500
        
        query = '''
        SELECT "JOB_ID", "TITLE", "COMPANY", "LOCATION", "SALARY", 
               "SOURCE", "SOURCE_URL", "POSTED_DATE", "TAGS", "DESCRIPTION"
        FROM JOB_POSTINGS 
        ORDER BY "POSTED_DATE" DESC
        LIMIT 100
        '''
        
        cursor = snowflake_manager.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        jobs = []
        for row in rows:
            # Parse tags from string to list
            tags_str = row[8] if row[8] else ''
            tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
            
            job = {
                'job_id': row[0],
                'title': row[1],
                'company': row[2],
                'location': row[3],
                'salary': row[4],
                'source': row[5],
                'source_url': row[6],
                'posted_date': row[7].strftime('%Y-%m-%d') if row[7] else None,
                'tags': tags,
                'description': row[9] if row[9] else ''
            }
            jobs.append(job)
        
        return jsonify({'jobs': jobs, 'count': len(jobs)})
        
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def get_analytics():
    """Get analytics data"""
    try:
        if not snowflake_manager.connect_connector():
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get all jobs for analytics
        query = '''
        SELECT "JOB_ID", "TITLE", "COMPANY", "LOCATION", "SALARY", 
               "SOURCE", "SOURCE_URL", "POSTED_DATE", "TAGS", "DESCRIPTION"
        FROM JOB_POSTINGS
        '''
        
        cursor = snowflake_manager.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert to job format for analytics
        jobs = []
        for row in rows:
            tags_str = row[8] if row[8] else ''
            tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
            
            job = {
                'job_id': row[0],
                'title': row[1],
                'company': row[2],
                'location': row[3],
                'salary': row[4],
                'source': row[5],
                'source_url': row[6],
                'posted_date': row[7].strftime('%Y-%m-%d') if row[7] else None,
                'tags': tags,
                'description': row[9] if row[9] else ''
            }
            jobs.append(job)
        
        # Get skills analytics
        skills_analytics = job_scraper.get_skills_analytics(jobs)
        
        # Basic stats
        total_jobs = len(jobs)
        sources = {}
        for job in jobs:
            source = job['source']
            sources[source] = sources.get(source, 0) + 1
        
        analytics = {
            'total_jobs': total_jobs,
            'sources': sources,
            'skills_analytics': skills_analytics
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_jobs():
    """Search jobs by keyword"""
    try:
        keyword = request.args.get('q', '').strip()
        if not keyword:
            return jsonify({'error': 'Search keyword required'}), 400
        
        if not snowflake_manager.connect_connector():
            return jsonify({'error': 'Database connection failed'}), 500
        
        query = '''
        SELECT "JOB_ID", "TITLE", "COMPANY", "LOCATION", "SALARY", 
               "SOURCE", "SOURCE_URL", "POSTED_DATE", "TAGS", "DESCRIPTION"
        FROM JOB_POSTINGS 
        WHERE 1=1
        '''
        params = []

        if keyword:
            # Search in title, description, and tags
            query += ''' AND (
                LOWER("TITLE") LIKE %s OR 
                LOWER("DESCRIPTION") LIKE %s OR 
                LOWER("TAGS") LIKE %s OR
                LOWER("COMPANY") LIKE %s
            )'''
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param, keyword_param, keyword_param])
        
        query += ' ORDER BY "POSTED_DATE" DESC LIMIT 50'
        
        cursor = snowflake_manager.connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        jobs = []
        for row in rows:
            # Parse tags from string to list
            tags_str = row[8] if row[8] else ''
            tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
            
            job = {
                'job_id': row[0],
                'title': row[1],
                'company': row[2],
                'location': row[3],
                'salary': row[4],
                'source': row[5],
                'source_url': row[6],
                'posted_date': row[7].strftime('%Y-%m-%d') if row[7] else None,
                'tags': tags,
                'description': row[9] if row[9] else ''
            }
            jobs.append(job)
        
        return jsonify({'jobs': jobs, 'count': len(jobs), 'keyword': keyword})
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sources')
def get_sources():
    """Get available job sources"""
    sources = [
        {'name': 'LinkedIn', 'status': 'active'},
        {'name': 'Remote OK', 'status': 'active'},
        {'name': 'Indeed', 'status': 'blocked'},
        {'name': 'Stack Overflow', 'status': 'blocked'},
        {'name': 'Glassdoor', 'status': 'blocked'},
        {'name': 'ZipRecruiter', 'status': 'blocked'}
    ]
    return jsonify({'sources': sources})

@app.route('/api/scrape-jobs')
def scrape_jobs():
    """Trigger job scraping"""
    try:
        logger.info("Starting job scraping...")
        
        # Use the fast scraper
        jobs = job_scraper.scrape_all_sources_fast()
        
        if jobs:
            # Store jobs in Snowflake
            jobs_stored = store_jobs_in_snowflake(jobs)
            
            return jsonify({
                'message': 'Job scraping completed successfully!',
                'jobs_scraped': len(jobs),
                'jobs_stored': jobs_stored,
                'sources': ['LinkedIn', 'Remote OK']
            })
        else:
            return jsonify({
                'message': 'No jobs found during scraping',
                'jobs_scraped': 0,
                'jobs_stored': 0
            })
            
    except Exception as e:
        logger.error(f"Error scraping jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scrape-jobs-advanced')
def scrape_jobs_advanced():
    """Trigger advanced job scraping with async, Selenium, and caching"""
    try:
        logger.info("Starting advanced job scraping...")
        
        # Run async scraping in a separate thread
        def run_async_scraping():
            loop = get_or_create_loop()
            return loop.run_until_complete(advanced_scraper.scrape_all_sources_advanced())
        
        # Run in thread to avoid blocking
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_async_scraping)
            jobs = future.result(timeout=300)  # 5 minute timeout
        
        if jobs:
            # Store jobs in Snowflake
            jobs_stored = store_jobs_in_snowflake(jobs)
            
            # Save to file for backup
            advanced_scraper.save_jobs_to_file(jobs, 'advanced_scraped_jobs.json')
            
            return jsonify({
                'message': 'Advanced job scraping completed successfully!',
                'jobs_scraped': len(jobs),
                'jobs_stored': jobs_stored,
                'sources': ['LinkedIn (Selenium)', 'Remote OK'],
                'features': ['Async Scraping', 'Selenium/Headless Browser', 'Caching', 'Proxy Rotation']
            })
        else:
            return jsonify({
                'message': 'No jobs found during advanced scraping',
                'jobs_scraped': 0,
                'jobs_stored': 0
            })
            
    except Exception as e:
        logger.error(f"Error in advanced scraping: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scrape-jobs-playwright')
def scrape_jobs_playwright():
    """Trigger Playwright job scraping (bypasses 403 errors)"""
    try:
        logger.info("Starting Playwright job scraping...")
        
        # Run async Playwright scraping in a separate thread
        def run_async_playwright():
            loop = get_or_create_loop()
            return loop.run_until_complete(playwright_scraper.scrape_all_sources_working())
        
        # Run in thread to avoid blocking
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_async_playwright)
            jobs = future.result(timeout=300)  # 5 minute timeout
        
        if jobs:
            # Store jobs in Snowflake
            jobs_stored = store_jobs_in_snowflake(jobs)
            
            # Save to file for backup
            playwright_scraper.save_jobs_to_file(jobs, 'playwright_scraped_jobs.json')
            
            return jsonify({
                'message': 'Playwright job scraping completed successfully!',
                'jobs_scraped': len(jobs),
                'jobs_stored': jobs_stored,
                'sources': ['Remote OK (Playwright)', 'We Work Remotely (Playwright)', 'Remotive API', 'Sample Jobs'],
                'features': ['Playwright Headless Browser', 'Bypass 403 Errors', 'Free APIs', 'No Rate Limits']
            })
        else:
            return jsonify({
                'message': 'No jobs found during Playwright scraping',
                'jobs_scraped': 0,
                'jobs_stored': 0
            })
            
    except Exception as e:
        logger.error(f"Error in Playwright scraping: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/skills')
def get_skills():
    """Get skills analytics"""
    try:
        if not snowflake_manager.connect_connector():
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get all jobs for skills analysis
        query = '''
        SELECT "JOB_ID", "TITLE", "COMPANY", "LOCATION", "SALARY", 
               "SOURCE", "SOURCE_URL", "POSTED_DATE", "TAGS", "DESCRIPTION"
        FROM JOB_POSTINGS
        '''
        
        cursor = snowflake_manager.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert to job format for analytics
        jobs = []
        for row in rows:
            tags_str = row[8] if row[8] else ''
            tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
            
            job = {
                'job_id': row[0],
                'title': row[1],
                'company': row[2],
                'location': row[3],
                'salary': row[4],
                'source': row[5],
                'source_url': row[6],
                'posted_date': row[7].strftime('%Y-%m-%d') if row[7] else None,
                'tags': tags,
                'description': row[9] if row[9] else ''
            }
            jobs.append(job)
        
        # Get skills analytics
        skills_analytics = job_scraper.get_skills_analytics(jobs)
        
        return jsonify(skills_analytics)
        
    except Exception as e:
        logger.error(f"Error getting skills: {e}")
        return jsonify({'error': str(e)}), 500

def store_jobs_in_snowflake(jobs):
    """Store scraped jobs in Snowflake"""
    try:
        if not snowflake_manager.connect_connector():
            logger.error("Failed to connect to Snowflake")
            return 0
        
        cursor = snowflake_manager.connection.cursor()
        jobs_stored = 0
        
        for job in jobs:
            try:
                # Convert tags list to string
                tags_str = ','.join(job.get('tags', [])) if job.get('tags') else ''
                description = job.get('description', f"Job from {job['source']}")
                
                # Insert job
                insert_query = '''
                INSERT INTO JOB_POSTINGS (
                    "JOB_ID", "TITLE", "COMPANY", "LOCATION", "SALARY", 
                    "SOURCE", "SOURCE_URL", "POSTED_DATE", "TAGS", "DESCRIPTION"
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    "TITLE" = VALUES("TITLE"),
                    "COMPANY" = VALUES("COMPANY"),
                    "LOCATION" = VALUES("LOCATION"),
                    "SALARY" = VALUES("SALARY"),
                    "SOURCE" = VALUES("SOURCE"),
                    "SOURCE_URL" = VALUES("SOURCE_URL"),
                    "POSTED_DATE" = VALUES("POSTED_DATE"),
                    "TAGS" = VALUES("TAGS"),
                    "DESCRIPTION" = VALUES("DESCRIPTION")
                '''
                
                cursor.execute(insert_query, (
                    job['job_id'],
                    job['title'],
                    job['company'],
                    job['location'],
                    job.get('salary'),
                    job['source'],
                    job.get('source_url'),
                    job['posted_date'],
                    tags_str,
                    description
                ))
                
                jobs_stored += 1
                
            except Exception as e:
                logger.warning(f"Error storing job {job.get('job_id')}: {e}")
                continue
        
        snowflake_manager.connection.commit()
        logger.info(f"Successfully stored {jobs_stored} jobs in Snowflake")
        return jobs_stored
        
    except Exception as e:
        logger.error(f"Error storing jobs in Snowflake: {e}")
        return 0

if __name__ == '__main__':
    display_banner()
    print("🌐 Starting Flask server at http://127.0.0.1:5000")
    print("🔍 Using reliable job sources: LinkedIn, Remote OK")
    app.run(debug=True, host='127.0.0.1', port=5000) 