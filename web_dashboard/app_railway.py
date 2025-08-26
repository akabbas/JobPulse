#!/usr/bin/env python3
"""
JobPulse Flask Application - Railway Production Version
Enhanced with comprehensive Playwright scraping and smart caching
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from models import db, Job, Search

# Import scrapers
from scrapers import (
    enhanced_playwright_scraper, api_sources_scraper, reddit_scraper,
    greenhouse_scraper, lever_scraper, google_jobs_scraper,
    jobspresso_scraper, himalayas_scraper, yc_jobs_scraper,
    authentic_jobs_scraper, otta_scraper, hackernews_scraper,
    stackoverflow_scraper, dice_scraper, indeed_scraper,
    linkedin_scraper, remoteok_scraper, weworkremotely_scraper
)

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Database configuration - Railway provides DATABASE_URL for PostgreSQL
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Convert postgres:// to postgresql:// for newer versions
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///jobpulse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Production settings
app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'production')
app.config['DEBUG'] = app.config['FLASK_ENV'] == 'development'

# Initialize scrapers
enhanced_scraper = enhanced_playwright_scraper.EnhancedPlaywrightScraper(headless=True)
api_scraper = api_sources_scraper.APISourcesScraper()
reddit_scraper_instance = reddit_scraper.RedditScraper()
greenhouse_scraper_instance = greenhouse_scraper.GreenhouseScraper()
lever_scraper_instance = lever_scraper.LeverScraper()
google_jobs_scraper_instance = google_jobs_scraper.GoogleJobsScraper()
jobspresso_scraper_instance = jobspresso_scraper.JobspressoScraper()
himalayas_scraper_instance = himalayas_scraper.HimalayasScraper()
yc_jobs_scraper_instance = yc_jobs_scraper.YCJobsScraper()
authentic_jobs_scraper_instance = authentic_jobs_scraper.AuthenticJobsScraper()
otta_scraper_instance = otta_scraper.OttaScraper()
hackernews_scraper_instance = hackernews_scraper.HackerNewsScraper()
stackoverflow_scraper_instance = stackoverflow_scraper.StackOverflowScraper()
dice_scraper_instance = dice_scraper.DiceScraper()
indeed_scraper_instance = indeed_scraper.IndeedScraper()
linkedin_scraper_instance = linkedin_scraper.LinkedInScraper()
remoteok_scraper_instance = remoteok_scraper.RemoteOKScraper()
weworkremotely_scraper_instance = weworkremotely_scraper.WeWorkRemotelyScraper()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'environment': app.config['FLASK_ENV'],
        'database': 'connected' if db.engine.pool.checkedin() > 0 else 'disconnected'
    })

@app.route('/search', methods=['POST'])
def search_jobs():
    """Enhanced job search with smart caching and comprehensive scraping"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        location = data.get('location', 'United States')
        sources = data.get('sources', ['enhanced', 'api_sources', 'reddit', 'greenhouse', 'lever', 'google_jobs', 'jobspresso', 'himalayas', 'yc_jobs', 'authentic_jobs', 'otta', 'hackernews'])
        limit = data.get('limit', 50)
        
        logger.info(f"Search request: {keyword} in {location} with sources: {sources}")
        
        # Check database cache first
        cached_jobs = get_cached_jobs(keyword, location, hours=24, sources=sources)
        
        if cached_jobs and len(cached_jobs) >= limit * 0.5:
            logger.info(f"Returning {len(cached_jobs)} cached jobs")
            return jsonify({
                'success': True,
                'jobs': cached_jobs,
                'total_jobs': len(cached_jobs),
                'cached': True,
                'source': 'database_cache'
            })
        
        # Perform comprehensive scraping
        all_jobs = []
        successful_sources = 0
        
        # Enhanced Playwright scraper (comprehensive coverage)
        if 'enhanced' in sources:
            try:
                enhanced_results = await enhanced_scraper.scrape_all_sources(keyword, limit)
                enhanced_jobs = enhanced_results.get('all_sources', [])
                all_jobs.extend(enhanced_jobs)
                successful_sources += 1
                logger.info(f"Enhanced scraper: {len(enhanced_jobs)} jobs")
            except Exception as e:
                logger.error(f"Enhanced scraper error: {e}")
        
        # API sources (reliable)
        if 'api_sources' in sources:
            try:
                api_jobs = api_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(api_jobs)
                successful_sources += 1
                logger.info(f"API sources: {len(api_jobs)} jobs")
            except Exception as e:
                logger.error(f"API sources error: {e}")
        
        # Save jobs to database
        if all_jobs:
            saved_count = save_jobs_to_database(all_jobs)
            logger.info(f"Saved {saved_count} jobs to database")
        
        # Log search
        search_record = Search(keyword=keyword, location=location, result_count=len(all_jobs))
        db.session.add(search_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'jobs': all_jobs,
            'total_jobs': len(all_jobs),
            'successful_sources': successful_sources,
            'cached': False,
            'source': 'comprehensive_scraping'
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/enhanced_search', methods=['POST'])
def enhanced_search():
    """Enhanced search using comprehensive Playwright scraper"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        location = data.get('location', 'United States')
        limit = data.get('limit', 20)
        sources = data.get('sources', ['enhanced'])
        
        logger.info(f"Enhanced search: {keyword} in {location} with sources: {sources}")
        
        # Use enhanced scraper
        results = await enhanced_scraper.scrape_all_sources(keyword, limit)
        all_jobs = results.get('all_sources', [])
        
        # Save to database
        if all_jobs:
            saved_count = save_jobs_to_database(all_jobs)
            logger.info(f"Saved {saved_count} jobs from enhanced search")
        
        # Log search
        search_record = Search(keyword=keyword, location=location, result_count=len(all_jobs))
        db.session.add(search_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'jobs': all_jobs,
            'total_jobs': len(all_jobs),
            'source_breakdown': results.get('source_breakdown', {}),
            'scraping_method': 'enhanced_playwright',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Enhanced search error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/skills-network')
def get_skills_network():
    """Skills network API endpoint"""
    try:
        # Implementation for skills network
        return jsonify({'success': True, 'message': 'Skills network endpoint'})
    except Exception as e:
        logger.error(f"Skills network error: {e}")
        return jsonify({'success': False, 'error': str(e)})

def get_cached_jobs(keyword, location, hours=24, sources=None):
    """Get cached jobs from database"""
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = Job.query.filter(
            Job.created_at >= time_threshold,
            db.or_(
                Job.title.ilike(f'%{keyword}%'),
                Job.description.ilike(f'%{keyword}%'),
                Job.skills.ilike(f'%{keyword}%')
            )
        ).filter(
            db.or_(
                Job.location.ilike(f'%{location}%'),
                Job.location.is_(None),
                Job.location == ''
            )
        )
        
        if sources and len(sources) > 0:
            source_mapping = {
                'enhanced': ['enhanced_playwright', 'playwright'],
                'api_sources': ['remotive_api', 'api'],
                'reddit': ['reddit_remotejobs', 'reddit_forhire', 'reddit_jobs'],
                'greenhouse': ['greenhouse'],
                'lever': ['lever'],
                'google_jobs': ['google_jobs', 'google'],
                'jobspresso': ['jobspresso'],
                'himalayas': ['himalayas'],
                'yc_jobs': ['yc_jobs', 'ycombinator'],
                'authentic_jobs': ['authentic_jobs'],
                'otta': ['otta'],
                'hackernews': ['hackernews', 'hn'],
                'stackoverflow': ['stackoverflow', 'so'],
                'dice': ['dice'],
                'indeed': ['indeed'],
                'linkedin': ['linkedin'],
                'remoteok': ['remoteok'],
                'weworkremotely': ['weworkremotely']
            }
            
            source_conditions = []
            for source in sources:
                if source in source_mapping:
                    source_conditions.extend(source_mapping[source])
            
            if source_conditions:
                query = query.filter(Job.source.in_(source_conditions))
        
        cached_jobs = query.order_by(Job.created_at.desc()).limit(100).all()
        
        jobs_list = []
        for job in cached_jobs:
            jobs_list.append({
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'skills': job.skills.split(', ') if job.skills else [],
                'source': job.source,
                'url': job.url,
                'date_posted': job.date_posted.isoformat() if job.date_posted else None,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'cached': True
            })
        
        return jobs_list
        
    except Exception as e:
        logger.error(f"Cache retrieval error: {e}")
        return []

def save_jobs_to_database(jobs_list):
    """Save jobs to database with duplicate detection"""
    try:
        saved_count = 0
        
        for job_data in jobs_list:
            existing_job = None
            
            if job_data.get('url'):
                existing_job = Job.query.filter_by(url=job_data['url']).first()
            
            if not existing_job and job_data.get('description'):
                description_start = job_data['description'][:100] if len(job_data['description']) > 100 else job_data['description']
                existing_job = Job.query.filter(
                    Job.description.like(f'{description_start}%')
                ).first()
            
            if not existing_job:
                new_job = Job(
                    title=job_data.get('title', ''),
                    company=job_data.get('company', ''),
                    location=job_data.get('location', ''),
                    description=job_data.get('description', ''),
                    skills=', '.join(job_data.get('skills', [])) if job_data.get('skills') else '',
                    source=job_data.get('source', 'unknown'),
                    url=job_data.get('url', ''),
                    date_posted=datetime.fromisoformat(job_data['date_posted']) if job_data.get('date_posted') else None
                )
                
                db.session.add(new_job)
                saved_count += 1
        
        db.session.commit()
        return saved_count
        
    except Exception as e:
        logger.error(f"Database save error: {e}")
        db.session.rollback()
        return 0

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully!")

# Initialize database on startup
@app.before_first_request
def initialize_app():
    """Initialize application on first request"""
    create_tables()

if __name__ == '__main__':
    # Use Railway's PORT environment variable
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    create_tables()
    app.run(debug=debug, host='0.0.0.0', port=port)
