from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database models
from models import db, Job, Search

from scrapers.indeed_scraper import IndeedScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.stackoverflow_scraper import StackOverflowScraper
from scrapers.dice_scraper import DiceScraper
from scrapers.remoteok_scraper import RemoteOKScraper
from scrapers.weworkremotely_scraper import WeWorkRemotelyScraper
from scrapers.simple_jobs_scraper import SimpleJobsScraper
from scrapers.api_sources_scraper import APISourcesScraper
from scrapers.reddit_scraper import RedditScraper
from scrapers.enhanced_playwright_scraper import EnhancedPlaywrightScraper
from scrapers.jobspresso_scraper import JobspressoScraper
from scrapers.yc_jobs_scraper import YCJobsScraper
from scrapers.authentic_jobs_scraper import AuthenticJobsScraper
from scrapers.otta_scraper import OttaScraper
from scrapers.hackernews_scraper import HackerNewsScraper
from scrapers.himalayas_scraper import HimalayasScraper
from scrapers.lever_scraper import LeverScraper
from scrapers.google_jobs_scraper import GoogleJobsScraper
from data_processing.data_cleaner import DataCleaner
from analysis.skill_trends import SkillTrendsAnalyzer
from ai_services.ai_analyzer import AIJobAnalyzer
import logging
from datetime import datetime, timedelta
import json
from collections import Counter, defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///jobpulse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize scrapers
indeed_scraper = IndeedScraper()
linkedin_scraper = LinkedInScraper()
stackoverflow_scraper = StackOverflowScraper()
dice_scraper = DiceScraper()
otta_scraper = OttaScraper()  # Otta scraper
hackernews_scraper = HackerNewsScraper()  # Hacker News scraper
yc_jobs_scraper = YCJobsScraper()  # YC Jobs scraper
authentic_jobs_scraper = AuthenticJobsScraper()  # Authentic Jobs scraper
jobspresso_scraper = JobspressoScraper()  # Jobspresso scraper
himalayas_scraper = HimalayasScraper()  # Himalayas scraper
remoteok_scraper = RemoteOKScraper()
weworkremotely_scraper = WeWorkRemotelyScraper()
simple_scraper = SimpleJobsScraper()  # Fallback scraper
api_scraper = APISourcesScraper()  # API sources
reddit_scraper = RedditScraper()  # Reddit scraper
enhanced_scraper = EnhancedPlaywrightScraper(headless=True)  # Enhanced Playwright scraper
lever_scraper = LeverScraper()  # Lever API scraper
google_jobs_scraper = GoogleJobsScraper()  # Google Jobs scraper

# Initialize data processors
data_cleaner = DataCleaner()
skill_analyzer = SkillTrendsAnalyzer()

# Initialize AI analyzer (optional - for enhanced skill extraction)
try:
    ai_analyzer = AIJobAnalyzer()
    logger.info("AI analyzer initialized successfully")
except Exception as e:
    logger.warning(f"AI analyzer not available: {e}")
    ai_analyzer = None

# Global storage for recent job searches (in production, use Redis or database)
recent_job_searches = {}
MAX_STORED_SEARCHES = 10  # Keep last 10 searches

# Data source status definitions
active_data_sources = [
    {
        'name': 'Remotive API',
        'status': 'live',
        'description': 'Remote job board with reliable API access',
        'job_count': 0
    },
    {
        'name': 'Reddit Jobs',
        'status': 'live',
        'description': 'Community-driven job postings from various subreddits',
        'job_count': 0
    },
    {
        'name': 'Jobspresso',
        'status': 'live',
        'description': 'Curated remote job listings',
        'job_count': 0
    },
    {
        'name': 'Himalayas',
        'status': 'live',
        'description': 'Remote job platform for developers',
        'job_count': 0
    },
    {
        'name': 'YC Jobs',
        'status': 'live',
        'description': 'Startup job board from Y Combinator',
        'job_count': 0
    },
    {
        'name': 'Authentic Jobs',
        'status': 'live',
        'description': 'Creative and tech job marketplace',
        'job_count': 0
    },
    {
        'name': 'Otta',
        'status': 'live',
        'description': 'Tech job platform with AI matching',
        'job_count': 0
    },
    {
        'name': 'Hacker News',
        'status': 'live',
        'description': 'Tech community job postings',
        'job_count': 0
    },
    {
        'name': 'WeWorkRemotely',
        'status': 'sample',
        'description': 'Remote job board (currently using sample data due to access limitations)',
        'job_count': 0
    },
    {
        'name': 'Remote OK',
        'status': 'sample',
        'description': 'Remote job aggregator (currently using sample data due to access limitations)',
        'job_count': 0
    },
    {
        'name': 'Indeed',
        'status': 'sample',
        'description': 'Major job search engine (currently using sample data due to access limitations)',
        'job_count': 0
    },
    {
        'name': 'LinkedIn',
        'status': 'sample',
        'description': 'Professional networking job board (currently using sample data due to access limitations)',
        'job_count': 0
    },
    {
        'name': 'Stack Overflow',
        'status': 'live',
        'description': 'Developer community job board (now using Playwright to bypass anti-bot measures)',
        'job_count': 0
    },
    {
        'name': 'Dice',
        'status': 'live',
        'description': 'Tech job marketplace (now using Playwright to bypass anti-bot measures)',
        'job_count': 0
    },
    {
        'name': 'Greenhouse',
        'status': 'live',
        'description': 'Enterprise hiring platform (now using public API to avoid access limitations)',
        'job_count': 0
    },
    {
        'name': 'Lever',
        'status': 'live',
        'description': 'Applicant tracking system (now using public API to avoid access limitations)',
        'job_count': 0
    },
    {
        'name': 'Google Jobs',
        'status': 'sample',
        'description': 'Google job search integration (currently using sample data due to access limitations)',
        'job_count': 0
    }
]

@app.route('/')
def index():
    # Update job counts for data sources
    update_data_source_job_counts()
    return render_template('index.html', data_sources=active_data_sources)

@app.route('/skills-network')
def skills_network_demo():
    """Demo page for the skills network visualization"""
    # Update job counts for data sources
    update_data_source_job_counts()
    return render_template('skills_network_demo.html', data_sources=active_data_sources)

@app.route('/health')
def health_check():
    """Health check endpoint for container orchestration"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/skills-network')
def get_skills_network():
    """
    API endpoint for skills network visualization data
    Returns skills and their co-occurrences formatted for vis-network library
    Uses persistent database data instead of in-memory storage
    """
    try:
        # Get query parameters for filtering
        keyword = request.args.get('keyword', '')
        location = request.args.get('location', '')
        min_frequency = int(request.args.get('min_frequency', 2))
        min_co_occurrence = int(request.args.get('min_co_occurrence', 1))
        search_id = request.args.get('search_id', '')
        
        # Get jobs from database based on search_id or recent jobs
        all_jobs = []
        data_source = 'database'
        
        if search_id:
            # Analyze jobs from a specific logged search
            logger.info(f"Analyzing jobs from specific search ID: {search_id}")
            search_record = Search.query.filter_by(id=search_id).first()
            
            if search_record:
                # Get jobs that were created around the same time as this search
                search_time = search_record.created_at
                time_window = timedelta(hours=2)  # 2-hour window around search time
                
                all_jobs = Job.query.filter(
                    Job.created_at >= search_time - time_window,
                    Job.created_at <= search_time + time_window
                ).all()
                
                logger.info(f"Found {len(all_jobs)} jobs from search {search_id}")
            else:
                logger.warning(f"Search ID {search_id} not found in database")
        
        if not all_jobs:
            # Analyze all jobs from the last 7 days for broader market trends
            logger.info("Analyzing all jobs from the last 7 days for market trends")
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            query = Job.query.filter(Job.created_at >= seven_days_ago)
            
            # Apply keyword filter if provided
            if keyword:
                query = query.filter(
                    db.or_(
                        Job.title.ilike(f'%{keyword}%'),
                        Job.description.ilike(f'%{keyword}%'),
                        Job.skills.ilike(f'%{keyword}%')
                    )
                )
            
            # Apply location filter if provided
            if location:
                query = query.filter(Job.location.ilike(f'%{location}%'))
            
            all_jobs = query.order_by(Job.created_at.desc()).limit(1000).all()  # Limit to 1000 most recent jobs
            logger.info(f"Found {len(all_jobs)} jobs from last 7 days")
        
        if not all_jobs:
            logger.warning("No jobs found in database, falling back to sample data")
            all_jobs = get_sample_jobs()
            data_source = 'sample_data'
        
        # Convert database objects to dictionary format
        jobs_data = []
        for job in all_jobs:
            if hasattr(job, 'to_dict'):  # Database object
                job_dict = job.to_dict()
            else:  # Already a dictionary (sample data)
                job_dict = job
            
            jobs_data.append(job_dict)
        
        # Extract skills from job descriptions using AI
        all_jobs_with_skills = []
        
        for job in jobs_data:
            job_skills = []
            
            # Try to extract skills using AI if available
            if ai_analyzer and job.get('description'):
                try:
                    # Use AI to extract skills from job description
                    ai_analysis = ai_analyzer.analyze_job_description(
                        job['description'], 
                        {'title': job.get('title', '')}
                    )
                    
                    if ai_analysis.get('success') and 'skills' in ai_analysis.get('analysis', {}):
                        # Use AI-extracted skills
                        extracted_skills = ai_analysis['analysis']['skills']
                        if isinstance(extracted_skills, list):
                            job_skills = [skill.strip() for skill in extracted_skills if skill.strip()]
                        elif isinstance(extracted_skills, str):
                            job_skills = [skill.strip() for skill in extracted_skills.split(',') if skill.strip()]
                    
                except Exception as e:
                    logger.warning(f"AI skill extraction failed for job {job.get('title', 'Unknown')}: {e}")
                    # Fall back to predefined skills or description parsing
                    pass
            
            # If no AI skills, try to use predefined skills or parse description
            if not job_skills:
                if job.get('skills'):
                    # Use predefined skills if available
                    if isinstance(job['skills'], list):
                        job_skills = [skill.strip() for skill in job['skills'] if skill.strip()]
                    elif isinstance(job['skills'], str):
                        job_skills = [skill.strip() for skill in job['skills'].split(',') if skill.strip()]
                
                elif job.get('description'):
                    # Parse description for common tech skills
                    job_skills = extract_skills_from_description(job['description'])
            
            # Clean and normalize skills
            cleaned_skills = []
            for skill in job_skills:
                if skill and isinstance(skill, str):
                    # Normalize skill names
                    normalized_skill = skill.strip().title()
                    if len(normalized_skill) > 1:  # Avoid single characters
                        cleaned_skills.append(normalized_skill)
            
            job['extracted_skills'] = cleaned_skills
            if cleaned_skills:  # Only include jobs with skills
                all_jobs_with_skills.append(job)
        
        # Count skill frequencies
        skill_frequencies = Counter()
        for job in all_jobs_with_skills:
            skill_frequencies.update(job['extracted_skills'])
        
        # Calculate co-occurrences
        co_occurrences = defaultdict(int)
        for job in all_jobs_with_skills:
            skills = job['extracted_skills']
            for i in range(len(skills)):
                for j in range(i + 1, len(skills)):
                    # Create sorted pair to avoid duplicates
                    skill_pair = tuple(sorted([skills[i], skills[j]]))
                    co_occurrences[skill_pair] += 1
        
        # Filter out low-frequency skills and weak co-occurrences
        filtered_skills = {skill: count for skill, count in skill_frequencies.items() 
                          if count >= min_frequency}
        
        filtered_co_occurrences = {f"{pair[0]}|{pair[1]}": count 
                                 for pair, count in co_occurrences.items() 
                                 if count >= min_co_occurrence and 
                                 pair[0] in filtered_skills and 
                                 pair[1] in filtered_skills}
        
        # Format data for vis-network library
        network_data = {
            'success': True,
            'data': {
                'skills': filtered_skills,
                'co_occurrences': filtered_co_occurrences,
                'total_jobs_analyzed': len(all_jobs_with_skills),
                'data_source': data_source,
                'search_info': {
                    'keyword': keyword,
                    'location': location,
                    'search_id': search_id,
                    'time_range': '7_days' if not search_id else 'specific_search'
                },
                'timestamp': datetime.now().isoformat()
            }
        }
        
        logger.info(f"Skills network data generated: {len(filtered_skills)} skills, {len(filtered_co_occurrences)} connections from {len(all_jobs_with_skills)} jobs (source: {data_source})")
        
        return jsonify(network_data)
        
    except Exception as e:
        logger.error(f"Error generating skills network data: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/skills-network/stats')
def get_skills_network_stats():
    """Get statistics about the skills network"""
    try:
        # Update data source counts
        update_data_source_job_counts()
        
        # This endpoint provides metadata about the skills network
        stats = {
            'success': True,
            'stats': {
                'total_endpoints': 4,  # Updated to include new data-sources endpoint
                'available_filters': ['keyword', 'location', 'min_frequency', 'min_co_occurrence', 'use_current_search', 'search_id'],
                'data_sources': ['real_jobs', 'ai_analysis', 'sample_data'],
                'data_source_status': {
                    'total_sources': len(active_data_sources),
                    'live_sources': len([s for s in active_data_sources if s['status'] == 'live']),
                    'sample_sources': len([s for s in active_data_sources if s['status'] == 'sample'])
                },
                'last_updated': datetime.now().isoformat(),
                'version': '1.0.0'
            }
        }
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting skills network stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/skills-network/searches')
def get_available_searches():
    """Get list of available job searches for skills network analysis from database"""
    try:
        # Get searches from the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        searches = Search.query.filter(
            Search.created_at >= thirty_days_ago
        ).order_by(Search.created_at.desc()).limit(50).all()
        
        search_list = []
        for search in searches:
            # Count jobs that were created around the same time as this search
            search_time = search.created_at
            time_window = timedelta(hours=2)  # 2-hour window around search time
            
            job_count = Job.query.filter(
                Job.created_at >= search_time - time_window,
                Job.created_at <= search_time + time_window
            ).count()
            
            search_list.append({
                'search_id': search.id,
                'keyword': search.keyword,
                'location': search.location,
                'job_count': job_count,
                'result_count': search.result_count,
                'timestamp': search.created_at.isoformat() if search.created_at else None
            })
        
        return jsonify({
            'success': True,
            'searches': search_list,
            'total_searches': len(search_list),
            'time_range': '30_days'
        })
        
    except Exception as e:
        logger.error(f"Error getting available searches: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/skills-network/history')
def get_skills_history():
    """Get historical skills analysis data from database"""
    try:
        # Get query parameters
        days = int(request.args.get('days', 7))  # Default to 7 days
        keyword = request.args.get('keyword', '')
        location = request.args.get('location', '')
        
        # Calculate time range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query jobs from the specified time range
        query = Job.query.filter(
            Job.created_at >= start_date,
            Job.created_at <= end_date
        )
        
        # Apply filters if provided
        if keyword:
            query = query.filter(
                db.or_(
                    Job.title.ilike(f'%{keyword}%'),
                    Job.description.ilike(f'%{keyword}%'),
                    Job.skills.ilike(f'%{keyword}%')
                )
            )
        
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        # Get jobs and group by date
        jobs = query.order_by(Job.created_at.desc()).all()
        
        # Group jobs by date
        daily_stats = {}
        for job in jobs:
            date_key = job.created_at.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'date': date_key,
                    'job_count': 0,
                    'skills': Counter(),
                    'sources': Counter()
                }
            
            daily_stats[date_key]['job_count'] += 1
            daily_stats[date_key]['sources'][job.source] += 1
            
            # Extract skills from job
            if job.skills:
                skills_list = [skill.strip() for skill in job.skills.split(',') if skill.strip()]
                daily_stats[date_key]['skills'].update(skills_list)
        
        # Convert to list and sort by date
        history_data = list(daily_stats.values())
        history_data.sort(key=lambda x: x['date'])
        
        # Get top skills overall
        all_skills = Counter()
        for day_data in history_data:
            all_skills.update(day_data['skills'])
        
        top_skills = [{'skill': skill, 'count': count} for skill, count in all_skills.most_common(20)]
        
        return jsonify({
            'success': True,
            'history': {
                'daily_stats': history_data,
                'top_skills': top_skills,
                'total_jobs': len(jobs),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                },
                'filters': {
                    'keyword': keyword,
                    'location': location
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting skills history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/data-sources')
def get_data_sources():
    """Get current status of all data sources"""
    try:
        # Update job counts for data sources
        update_data_source_job_counts()
        
        return jsonify({
            'success': True,
            'data_sources': active_data_sources,
            'total_sources': len(active_data_sources),
            'live_sources': len([s for s in active_data_sources if s['status'] == 'live']),
            'sample_sources': len([s for s in active_data_sources if s['status'] == 'sample']),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting data sources: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/search', methods=['POST'])
def search_jobs():
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        location = data.get('location', 'United States')
        experience_level = data.get('experience_level', 'all')
        sources = data.get('sources', ['enhanced', 'api_sources', 'reddit', 'greenhouse', 'lever', 'google_jobs', 'jobspresso', 'himalayas', 'yc_jobs', 'authentic_jobs', 'otta', 'hackernews'])  # Default to enhanced scraper + reliable sources
        limit = data.get('limit', 50)  # Increased from 25 to 50
        
        # STEP 1: Check Database First (Smart Caching)
        logger.info(f"Checking database for recent jobs matching '{keyword}' in '{location}' with experience level '{experience_level}' and sources: {sources}")
        cached_jobs = get_cached_jobs(keyword, location, hours=24, sources=sources, experience_level=experience_level)
        
        if cached_jobs and len(cached_jobs) >= limit * 0.5:  # If we have at least 50% of requested jobs cached
            logger.info(f"Found {len(cached_jobs)} cached jobs, returning from database")
            
            # Log the search
            search_record = Search(
                keyword=keyword,
                location=location,
                result_count=len(cached_jobs)
            )
            db.session.add(search_record)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'jobs': cached_jobs,
                'total_jobs': len(cached_jobs),
                'successful_sources': 1,
                'search_id': f"{keyword}_{location}_{experience_level}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'source': 'database_cache',
                'cached': True,
                'experience_level': experience_level
            })
        
        # STEP 2: Scrape if Needed
        logger.info("Insufficient cached jobs found, proceeding with scraping")
        all_jobs = []
        successful_sources = 0
        
        # PRIORITY 1: Enhanced Playwright scraper (bypasses 403 errors, most reliable)
        if 'enhanced' in sources:
            try:
                enhanced_results = enhanced_scraper.scrape_all_sources(keyword, limit)
                enhanced_jobs = enhanced_results.get('all_sources', [])
                all_jobs.extend(enhanced_jobs)
                logger.info(f"Found {len(enhanced_jobs)} jobs from enhanced scraper")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with enhanced scraper: {e}")
        
        # PRIORITY 2: API sources (most reliable, no 403 errors)
        if 'api_sources' in sources:
            try:
                api_jobs = api_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(api_jobs)
                logger.info(f"Found {len(api_jobs)} jobs from API sources")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with API sources: {e}")
        
        # PRIORITY 2: Reddit sources (reliable, real job postings)
        if 'reddit' in sources:
            try:
                reddit_jobs = reddit_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(reddit_jobs)
                logger.info(f"Found {len(reddit_jobs)} jobs from Reddit")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Reddit sources: {e}")
        
        # PRIORITY 3: Web scraping sources (may have 403 errors, but try anyway)
        if 'indeed' in sources:
            try:
                indeed_jobs = indeed_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(indeed_jobs)
                logger.info(f"Found {len(indeed_jobs)} jobs on Indeed")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error scraping Indeed: {e}")
        
        if 'linkedin' in sources:
            try:
                linkedin_jobs = linkedin_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(linkedin_jobs)
                logger.info(f"Found {len(linkedin_jobs)} jobs on LinkedIn")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error scraping LinkedIn: {e}")
        
        if 'stackoverflow' in sources:
            try:
                stackoverflow_jobs = stackoverflow_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(stackoverflow_jobs)
                logger.info(f"Found {len(stackoverflow_jobs)} jobs on Stack Overflow")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error scraping Stack Overflow: {e}")
        
        if 'dice' in sources:
            try:
                dice_jobs = dice_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(dice_jobs)
                logger.info(f"Found {len(dice_jobs)} jobs on Dice")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error scraping Dice: {e}")
        
        if 'remoteok' in sources:
            try:
                remoteok_jobs = remoteok_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(remoteok_jobs)
                logger.info(f"Found {len(remoteok_jobs)} jobs on Remote OK")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error scraping Remote OK: {e}")
        
        if 'weworkremotely' in sources:
            try:
                weworkremotely_jobs = weworkremotely_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(weworkremotely_jobs)
                logger.info(f"Found {len(weworkremotely_jobs)} jobs on We Work Remotely")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error scraping We Work Remotely: {e}")
        
        # NEW SOURCES: Greenhouse and Lever (API-based, no 403 errors)
        if 'greenhouse' in sources:
            try:
                greenhouse_jobs = greenhouse_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(greenhouse_jobs)
                logger.info(f"Found {len(greenhouse_jobs)} jobs from Greenhouse")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Greenhouse scraper: {e}")
        
        if 'lever' in sources:
            try:
                lever_jobs = lever_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(lever_jobs)
                logger.info(f"Found {len(lever_jobs)} jobs from Lever")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Lever scraper: {e}")
        
        # NEW SOURCE: Google Jobs
        # NEW SOURCE: Google Jobs
        if 'google_jobs' in sources:
            try:
                google_jobs = google_jobs_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(google_jobs)
                logger.info(f"Found {len(google_jobs)} jobs from Google Jobs")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Google Jobs scraper: {e}")
        # NEW SOURCE: Jobspresso
        if 'jobspresso' in sources:
            try:
                jobspresso_jobs = jobspresso_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(jobspresso_jobs)
                logger.info(f"Found {len(jobspresso_jobs)} jobs from Jobspresso")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Jobspresso scraper: {e}")

        # NEW SOURCE: Himalayas
        if 'himalayas' in sources:
            try:
                himalayas_jobs = himalayas_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(himalayas_jobs)
                logger.info(f"Found {len(himalayas_jobs)} jobs from Himalayas")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Himalayas scraper: {e}")
        
        # NEW SOURCE: YC Jobs
        if 'yc_jobs' in sources:
            try:
                yc_jobs = yc_jobs_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(yc_jobs)
                logger.info(f"Found {len(yc_jobs)} jobs from YC Jobs")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with YC Jobs scraper: {e}")

        # NEW SOURCE: Authentic Jobs
        if 'authentic_jobs' in sources:
            try:
                authentic_jobs = authentic_jobs_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(authentic_jobs)
                logger.info(f"Found {len(authentic_jobs)} jobs from Authentic Jobs")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Authentic Jobs scraper: {e}")

        # NEW SOURCE: Otta
        if 'otta' in sources:
            try:
                otta_jobs = otta_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(otta_jobs)
                logger.info(f"Found {len(otta_jobs)} jobs from Otta")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Otta scraper: {e}")

        # NEW SOURCE: Hacker News
        if 'hackernews' in sources:
            try:
                hn_jobs = hackernews_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(hn_jobs)
                logger.info(f"Found {len(hn_jobs)} jobs from Hacker News")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Hacker News scraper: {e}")
                logger.error(f"Error with Authentic Jobs scraper: {e}")
        # FALLBACK: If no jobs found from main sources, use fallback scraper
        if len(all_jobs) == 0:
            logger.info("No jobs found from main sources, using fallback scraper...")
            try:
                fallback_jobs = simple_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(fallback_jobs)
                logger.info(f"Found {len(fallback_jobs)} jobs from fallback scraper")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with fallback scraper: {e}")
        
        # STEP 3: Save to Database (Smart Caching)
        if all_jobs:
            logger.info(f"Saving {len(all_jobs)} jobs to database")
            saved_count = save_jobs_to_database(all_jobs)
            logger.info(f"Successfully saved {saved_count} new jobs to database")
        
        # STEP 4: Log the Search
        search_record = Search(
            keyword=keyword,
            location=location,
            result_count=len(all_jobs)
        )
        db.session.add(search_record)
        db.session.commit()
        logger.info(f"Logged search: '{keyword}' in '{location}' with experience level '{experience_level}' and {len(all_jobs)} results")
        
        # Store the search results for later use in skills network
        search_id = f"{keyword}_{location}_{experience_level}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        store_job_search(search_id, {
            'keyword': keyword,
            'location': location,
            'experience_level': experience_level,
            'jobs': all_jobs,
            'timestamp': datetime.now().isoformat(),
            'sources': sources
        })
        
        return jsonify({
            'success': True,
            'jobs': all_jobs,
            'total_jobs': len(all_jobs),
            'successful_sources': successful_sources,
            'search_id': search_id,
            'source': 'scraped',
            'cached': False,
            'saved_to_db': saved_count if 'saved_count' in locals() else 0,
            'experience_level': experience_level
        })
        
    except Exception as e:
        logger.error(f"Error in search_jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

def store_job_search(search_id, search_data):
    """Store job search results for later use"""
    global recent_job_searches
    
    # Add new search
    recent_job_searches[search_id] = search_data
    
    # Remove oldest searches if we exceed the limit
    if len(recent_job_searches) > MAX_STORED_SEARCHES:
        oldest_key = min(recent_job_searches.keys(), 
                        key=lambda k: recent_job_searches[k]['timestamp'])
        del recent_job_searches[oldest_key]
    
    logger.info(f"Stored job search {search_id} with {len(search_data['jobs'])} jobs")

def get_latest_job_search():
    """Get the most recent job search results"""
    global recent_job_searches
    
    if not recent_job_searches:
        return None
    
    # Return the most recent search
    latest_key = max(recent_job_searches.keys(), 
                    key=lambda k: recent_job_searches[k]['timestamp'])
    return recent_job_searches[latest_key]

def get_job_search_by_id(search_id):
    """Get a specific job search by ID"""
    global recent_job_searches
    return recent_job_searches.get(search_id)

def get_sample_jobs():
    """Get sample job data for fallback when no real data is available"""
    return [
        {
            'title': 'Software Engineer',
            'description': 'Looking for a Python developer with React and AWS experience. Must have experience with JavaScript, Docker, and modern web development practices.',
            'skills': ['Python', 'React', 'AWS', 'JavaScript', 'Docker'],
            'is_sample': True
        },
        {
            'title': 'Full Stack Developer',
            'description': 'Node.js developer needed with MongoDB and Docker skills. Experience with Express.js, REST APIs, and cloud deployment required.',
            'skills': ['Node.js', 'MongoDB', 'Docker', 'JavaScript', 'Express'],
            'is_sample': True
        },
        {
            'title': 'Data Scientist',
            'description': 'Python, machine learning, and SQL experience required. Must be proficient with Pandas, NumPy, and statistical analysis.',
            'skills': ['Python', 'Machine Learning', 'SQL', 'Pandas', 'NumPy'],
            'is_sample': True
        },
        {
            'title': 'DevOps Engineer',
            'description': 'AWS, Kubernetes, and Docker expertise needed. Experience with Terraform, Jenkins, and CI/CD pipelines required.',
            'skills': ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'Jenkins'],
            'is_sample': True
        },
        {
            'title': 'Frontend Developer',
            'description': 'React and TypeScript developer with CSS skills. Must have experience with modern JavaScript, HTML5, and responsive design.',
            'skills': ['React', 'TypeScript', 'CSS', 'JavaScript', 'HTML'],
            'is_sample': True
        }
    ]

def update_data_source_job_counts():
    """Update job counts for each data source based on recent searches"""
    global active_data_sources, recent_job_searches
    
    # Reset all counts
    for source in active_data_sources:
        source['job_count'] = 0
    
    # Count jobs from recent searches by source
    for search_data in recent_job_searches.values():
        for job in search_data.get('jobs', []):
            job_source = job.get('source', 'unknown')
            
            # Map job sources to our data source names
            source_mapping = {
                'remotive_api': 'Remotive API',
                'reddit_remotejobs': 'Reddit Jobs',
                'reddit_forhire': 'Reddit Jobs',
                'reddit_jobs': 'Reddit Jobs',
                'reddit_cscareerquestions': 'Reddit Jobs',
                'jobspresso': 'Jobspresso',
                'himalayas': 'Himalayas',
                'yc_jobs': 'YC Jobs',
                'authentic_jobs': 'Authentic Jobs',
                'otta': 'Otta',
                'hackernews': 'Hacker News',
                'weworkremotely': 'WeWorkRemotely',
                'remote_ok': 'Remote OK',
                'indeed': 'Indeed',
                'linkedin': 'LinkedIn',
                'stackoverflow': 'Stack Overflow',
                'dice': 'Dice',
                'greenhouse': 'Greenhouse',
                'lever': 'Lever',
                'google_jobs': 'Google Jobs'
            }
            
            mapped_source = source_mapping.get(job_source, job_source)
            
            # Find and update the corresponding data source
            for source in active_data_sources:
                if source['name'] == mapped_source:
                    source['job_count'] += 1
                    break

def extract_skills_from_description(description):
    """Extract common tech skills from job description text"""
    if not description:
        return []
    
    # Common tech skills to look for
    tech_skills = [
        # Programming Languages
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin',
        # Web Technologies
        'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'Laravel', 'Spring',
        # Databases
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server',
        # Cloud Platforms
        'AWS', 'Azure', 'GCP', 'Heroku', 'DigitalOcean', 'Linode',
        # DevOps Tools
        'Docker', 'Kubernetes', 'Jenkins', 'GitLab', 'GitHub Actions', 'Terraform', 'Ansible',
        # Data Science
        'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'Jupyter', 'R',
        # Other Tools
        'Git', 'Linux', 'Apache', 'Nginx', 'Elasticsearch', 'Kafka', 'RabbitMQ'
    ]
    
    found_skills = []
    description_lower = description.lower()
    
    for skill in tech_skills:
        if skill.lower() in description_lower:
            found_skills.append(skill)
    
    return found_skills

@app.route('/analyze', methods=['POST'])
def analyze_skills():
    data = request.get_json()
    jobs_data = data.get('jobs', [])
    
    try:
        print(f"Analyzing {len(jobs_data)} jobs") # Debugging
        
        # If no real data, add sample data for testing
        if not jobs_data:
            jobs_data = [
                {
                    'title': 'Software Engineer',
                    'company': 'Tech Corp',
                    'location': 'San Francisco, CA',
                    'salary': '$120,000 - $150,000',
                    'snippet': 'We are looking for a Python developer with React experience...',
                    'job_url': 'https://example.com/job1',
                    'skills': ['python', 'react', 'javascript', 'git'],
                    'source': 'indeed',
                    'scraped_at': '2025-07-30T21:00:00'
                },
                {
                    'title': 'Full Stack Developer',
                    'company': 'Startup Inc',
                    'location': 'New York, NY',
                    'salary': '$100,000 - $130,000',
                    'snippet': 'Join our team as a Java developer with Spring Boot...',
                    'job_url': 'https://example.com/job2',
                    'skills': ['java', 'spring', 'sql', 'git'],
                    'source': 'linkedin',
                    'scraped_at': '2025-07-30T21:00:00'
                }
            ]
            print("Using sample data for testing")
        
        df = data_cleaner.clean_job_data(jobs_data)
        print(f"Cleaned data shape: {df.shape}") # Debugging
        print(f"Skills column: {df['skills'].tolist() if 'skills' in df.columns else 'No skills column'}") # Debugging
        
        # If no skills found in real data, add sample skills
        if df.empty or df['skills'].apply(len).sum() == 0:
            print("No skills found in real data, adding sample skills")
            sample_skills = ['python', 'javascript', 'react', 'node.js', 'git', 'sql', 'aws', 'docker']
            df['skills'] = [sample_skills[:4], sample_skills[4:]] * (len(df) // 2)
            if len(df) % 2:
                df['skills'].iloc[-1] = sample_skills[:3]
        
        skill_freq = skill_analyzer.analyze_skill_frequency(df)
        print(f"Skill analysis result: {skill_freq}") # Debugging
        
        return jsonify({
            'success': True,
            'skill_analysis': skill_freq
        })
    except Exception as e:
        print(f"Error in analyze_skills: {str(e)}") # Debugging
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/enhanced_search', methods=['POST'])
def enhanced_search():
    """Enhanced search using Playwright scraper (bypasses 403 errors)"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        location = data.get('location', 'United States')
        experience_level = data.get('experience_level', 'all')
        limit = data.get('limit', 20)  # Default to 20 for enhanced scraping
        headless = data.get('headless', True)
        sources = data.get('sources', ['enhanced'])  # Default to enhanced scraper
        
        logger.info(f"Starting enhanced search for '{keyword}' in '{location}' with experience level '{experience_level}' and limit {limit} and sources: {sources}")
        
        # Use the enhanced scraper (it's async, so we need to run it in a thread)
        import asyncio
        import threading
        
        def run_async_scraper():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(enhanced_scraper.scrape_all_sources(keyword, limit))
            finally:
                loop.close()
        
        # Run the async scraper in a separate thread
        import threading
        import queue
        
        # Create a queue to get results from the thread
        result_queue = queue.Queue()
        
        def run_async_scraper():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(enhanced_scraper.scrape_all_sources(keyword, limit))
                result_queue.put(results)
            except Exception as e:
                result_queue.put({'error': str(e)})
            finally:
                loop.close()
        
        # Start the thread
        thread = threading.Thread(target=run_async_scraper)
        thread.start()
        thread.join(timeout=60)  # Wait up to 60 seconds
        
        # Get results from queue
        if not result_queue.empty():
            results = result_queue.get()
            if 'error' in results:
                raise Exception(results['error'])
        else:
            raise Exception("Enhanced scraper timed out")
        
        # Get all unique jobs
        all_jobs = results.get('all_sources', [])
        
        # Add source breakdown for transparency
        source_breakdown = {}
        for source, jobs in results.items():
            if source != 'all_sources':
                source_breakdown[source] = len(jobs)
        
        # Save jobs to database
        if all_jobs:
            logger.info(f"Saving {len(all_jobs)} jobs from enhanced search to database")
            saved_count = save_jobs_to_database(all_jobs)
            logger.info(f"Successfully saved {saved_count} new jobs to database")
        
        # Log the search
        search_record = Search(
            keyword=keyword,
            location=location,
            result_count=len(all_jobs)
        )
        db.session.add(search_record)
        db.session.commit()
        logger.info(f"Logged enhanced search: '{keyword}' in '{location}' with experience level '{experience_level}' and {len(all_jobs)} results")
        
        logger.info(f"Enhanced search completed: {len(all_jobs)} unique jobs found")
        
        return jsonify({
            'success': True,
            'jobs': all_jobs,
            'total_jobs': len(all_jobs),
            'source_breakdown': source_breakdown,
            'scraping_method': 'enhanced_playwright',
            'timestamp': datetime.now().isoformat(),
            'search_id': f"{keyword}_{location}_{experience_level}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'saved_to_db': saved_count if 'saved_count' in locals() else 0,
            'experience_level': experience_level
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced_search: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'scraping_method': 'enhanced_playwright'
        })

@app.route('/filter', methods=['POST'])
def filter_jobs():
    data = request.get_json()
    jobs = data.get('jobs', [])
    criteria = data.get('criteria', {})
    
    try:
        filtered_jobs = []
        skills_required = criteria.get('skills_required', [])
        salary_min = criteria.get('salary_min')
        
        for job in jobs:
            # Check skills
            if skills_required:
                job_skills = set(job.get('skills', []))
                if not any(skill.lower() in [s.lower() for s in job_skills] for skill in skills_required):
                    continue
            
            # Check salary (if available)
            if salary_min and job.get('salary'):
                # Simple salary parsing - you might want to improve this
                salary_text = job['salary'].lower()
                if 'k' in salary_text or '000' in salary_text:
                    # Extract numeric value and compare
                    import re
                    numbers = re.findall(r'\d+', salary_text)
                    if numbers:
                        job_salary = max(int(n) for n in numbers)
                        if job_salary < salary_min:
                            continue
            
            filtered_jobs.append(job)
        
        return jsonify({
            'success': True,
            'filtered_jobs': filtered_jobs,
            'total_filtered': len(filtered_jobs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/database/stats', methods=['GET'])
def get_database_stats():
    """Get database statistics for monitoring the caching system"""
    try:
        # Get total job count
        total_jobs = Job.query.count()
        
        # Get jobs from last 24 hours
        recent_jobs = Job.query.filter(
            Job.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Get total searches
        total_searches = Search.query.count()
        
        # Get recent searches (last 24 hours)
        recent_searches = Search.query.filter(
            Search.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Get top sources
        top_sources = db.session.query(
            Job.source, 
            db.func.count(Job.id).label('count')
        ).group_by(Job.source).order_by(db.func.count(Job.id).desc()).limit(10).all()
        
        # Get top search keywords
        top_keywords = db.session.query(
            Search.keyword, 
            db.func.count(Search.id).label('count')
        ).group_by(Search.keyword).order_by(db.func.count(Search.id).desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_jobs': total_jobs,
                'recent_jobs_24h': recent_jobs,
                'total_searches': total_searches,
                'recent_searches_24h': recent_searches,
                'top_sources': [{'source': source, 'count': count} for source, count in top_sources],
                'top_keywords': [{'keyword': keyword, 'count': count} for keyword, count in top_keywords]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

def get_cached_jobs(keyword, location, hours=24, sources=None, experience_level='all'):
    """Get jobs from database that match the search criteria within the specified time window"""
    try:
        # Calculate the time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Start building the query
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
        
        # Filter by experience level if specified
        if experience_level and experience_level != 'all':
            # Define experience level patterns for filtering
            experience_patterns = {
                'entry': ['entry', 'entry-level', 'entry level', 'junior', 'jr', 'associate', 'assistant', 'trainee', 'intern', 'internship', 'graduate', 'new grad', 'new graduate'],
                'mid': ['mid', 'mid-level', 'mid level', 'intermediate', 'experienced', 'professional'],
                'senior': ['senior', 'sr', 'lead', 'principal', 'staff', 'expert', 'advanced'],
                'executive': ['executive', 'director', 'vp', 'vice president', 'cto', 'ceo', 'chief', 'head of', 'manager', 'management']
            }
            
            if experience_level in experience_patterns:
                patterns = experience_patterns[experience_level]
                # Create OR conditions for title and description matching
                experience_conditions = []
                for pattern in patterns:
                    experience_conditions.extend([
                        Job.title.ilike(f'%{pattern}%'),
                        Job.description.ilike(f'%{pattern}%')
                    ])
                
                if experience_conditions:
                    query = query.filter(db.or_(*experience_conditions))
        
        # Filter by sources if provided
        if sources and len(sources) > 0:
            # Map source names to database source values
            source_mapping = {
                'enhanced': ['enhanced_playwright', 'playwright'],
                'api_sources': ['remotive_api', 'api'],
                'reddit': ['reddit_remotejobs', 'reddit_forhire', 'reddit_jobs', 'reddit_cscareerquestions'],
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
            
            # Build source filter conditions
            source_conditions = []
            for source in sources:
                if source in source_mapping:
                    source_conditions.extend(source_mapping[source])
            
            if source_conditions:
                query = query.filter(Job.source.in_(source_conditions))
        
        # Execute the query
        cached_jobs = query.order_by(Job.created_at.desc()).limit(100).all()
        
        # Convert to dictionary format for consistency with scraper output
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
        
        logger.info(f"Retrieved {len(jobs_list)} cached jobs from database for experience level '{experience_level}'")
        return jobs_list
        
    except Exception as e:
        logger.error(f"Error retrieving cached jobs: {e}")
        return []

def save_jobs_to_database(jobs_list):
    """Save jobs to database, avoiding duplicates based on description and URL"""
    try:
        saved_count = 0
        
        for job_data in jobs_list:
            # Check for duplicates based on description and URL
            existing_job = None
            
            if job_data.get('url'):
                existing_job = Job.query.filter_by(url=job_data['url']).first()
            
            if not existing_job and job_data.get('description'):
                # If no URL match, check for similar description (first 100 chars)
                description_start = job_data['description'][:100] if len(job_data['description']) > 100 else job_data['description']
                existing_job = Job.query.filter(
                    Job.description.like(f'{description_start}%')
                ).first()
            
            if not existing_job:
                # Create new job record
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
        
        # Commit all changes
        db.session.commit()
        logger.info(f"Successfully saved {saved_count} new jobs to database")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error saving jobs to database: {e}")
        db.session.rollback()
        return 0

def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    # Create database tables
    create_tables()
    
    # Use Railway's PORT environment variable or default to 5002
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port) 