from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import scrapers (these should work on Heroku)
try:
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
    from data_processing.data_cleaner import DataCleaner
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"Some scrapers not available: {e}")
    SCRAPERS_AVAILABLE = False

import logging
from datetime import datetime
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Initialize scrapers if available
if SCRAPERS_AVAILABLE:
    try:
        indeed_scraper = IndeedScraper()
        linkedin_scraper = LinkedInScraper()
        stackoverflow_scraper = StackOverflowScraper()
        dice_scraper = DiceScraper()
        remoteok_scraper = RemoteOKScraper()
        weworkremotely_scraper = WeWorkRemotelyScraper()
        simple_scraper = SimpleJobsScraper()
        api_scraper = APISourcesScraper()
        reddit_scraper = RedditScraper()
        enhanced_scraper = EnhancedPlaywrightScraper(headless=True)
        data_cleaner = DataCleaner()
        logger.info("All scrapers initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing scrapers: {e}")
        SCRAPERS_AVAILABLE = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for container orchestration"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'scrapers_available': SCRAPERS_AVAILABLE
    })

@app.route('/search', methods=['POST'])
def search_jobs():
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        location = data.get('location', 'United States')
        sources = data.get('sources', ['enhanced', 'api_sources', 'reddit'])
        limit = data.get('limit', 50)
        
        if not SCRAPERS_AVAILABLE:
            # Fallback to mock data if scrapers aren't available
            return jsonify({
                'success': True,
                'jobs': get_mock_jobs(keyword, location, limit),
                'total_jobs': limit,
                'successful_sources': 1,
                'message': 'Using mock data (scrapers not available on Heroku)'
            })
        
        all_jobs = []
        successful_sources = 0
        
        # PRIORITY 1: Enhanced Playwright scraper
        if 'enhanced' in sources:
            try:
                enhanced_results = enhanced_scraper.scrape_all_sources(keyword, limit)
                enhanced_jobs = enhanced_results.get('all_sources', [])
                all_jobs.extend(enhanced_jobs)
                logger.info(f"Found {len(enhanced_jobs)} jobs from enhanced scraper")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with enhanced scraper: {e}")
        
        # PRIORITY 2: API sources
        if 'api_sources' in sources:
            try:
                api_jobs = api_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(api_jobs)
                logger.info(f"Found {len(api_jobs)} jobs from API sources")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with API sources: {e}")
        
        # PRIORITY 3: Reddit sources
        if 'reddit' in sources:
            try:
                reddit_jobs = reddit_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(reddit_jobs)
                logger.info(f"Found {len(reddit_jobs)} jobs from Reddit")
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Reddit: {e}")
        
        # Add other sources if requested
        if 'indeed' in sources:
            try:
                indeed_jobs = indeed_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(indeed_jobs)
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with Indeed: {e}")
        
        if 'linkedin' in sources:
            try:
                linkedin_jobs = linkedin_scraper.search_jobs(keyword, location, limit)
                all_jobs.extend(linkedin_jobs)
                successful_sources += 1
            except Exception as e:
                logger.error(f"Error with LinkedIn: {e}")
        
        # Remove duplicates and clean data
        if all_jobs:
            try:
                all_jobs = data_cleaner.remove_duplicates(all_jobs)
                all_jobs = all_jobs[:limit]
            except Exception as e:
                logger.error(f"Error cleaning data: {e}")
        
        return jsonify({
            'success': True,
            'jobs': all_jobs,
            'total_jobs': len(all_jobs),
            'successful_sources': successful_sources,
            'keyword': keyword,
            'location': location
        })
        
    except Exception as e:
        logger.error(f"Error in search_jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/enhanced_search', methods=['POST'])
def enhanced_search():
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        limit = data.get('limit', 20)
        
        if not SCRAPERS_AVAILABLE:
            # Fallback to mock data
            return jsonify({
                'success': True,
                'jobs': get_mock_jobs(keyword, 'Remote', limit),
                'total_jobs': limit,
                'scraping_method': 'Mock Data (Enhanced Search)',
                'source_breakdown': {'Mock': limit},
                'enhanced': True
            })
        
        try:
            enhanced_results = enhanced_scraper.scrape_all_sources(keyword, limit)
            enhanced_jobs = enhanced_results.get('all_sources', [])
            
            # Clean and process jobs
            if enhanced_jobs:
                enhanced_jobs = data_cleaner.remove_duplicates(enhanced_jobs)
                enhanced_jobs = enhanced_jobs[:limit]
            
            source_breakdown = enhanced_results.get('source_breakdown', {})
            
            return jsonify({
                'success': True,
                'jobs': enhanced_jobs,
                'total_jobs': len(enhanced_jobs),
                'scraping_method': 'Playwright Enhanced Scraper',
                'source_breakdown': source_breakdown,
                'enhanced': True
            })
            
        except Exception as e:
            logger.error(f"Enhanced search error: {e}")
            # Fallback to mock data
            return jsonify({
                'success': True,
                'jobs': get_mock_jobs(keyword, 'Remote', limit),
                'total_jobs': limit,
                'scraping_method': 'Mock Data (Fallback)',
                'source_breakdown': {'Mock': limit},
                'enhanced': True
            })
            
    except Exception as e:
        logger.error(f"Error in enhanced_search: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_skills():
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])
        
        if not jobs:
            return jsonify({
                'success': False,
                'error': 'No jobs provided for analysis'
            }), 400
        
        # Extract skills from job descriptions and titles
        all_skills = []
        for job in jobs:
            # Extract from skills field if available
            if 'skills' in job and job['skills']:
                all_skills.extend(job['skills'])
            
            # Extract from description/snippet
            description = job.get('snippet', '') or job.get('description', '')
            if description:
                # Simple skill extraction (you can enhance this)
                skills_from_desc = extract_skills_from_text(description)
                all_skills.extend(skills_from_desc)
        
        # Count skill occurrences
        skill_counts = {}
        for skill in all_skills:
            skill_lower = skill.lower().strip()
            if skill_lower and len(skill_lower) > 1:
                skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
        
        # Calculate percentages
        total_jobs = len(jobs)
        skill_percentages = {}
        for skill, count in skill_counts.items():
            percentage = (count / total_jobs) * 100
            skill_percentages[skill] = percentage
        
        # Categorize skills
        skill_categories = categorize_skills(skill_percentages)
        
        return jsonify({
            'success': True,
            'skill_analysis': skill_categories,
            'total_jobs_analyzed': total_jobs
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_skills: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/filter', methods=['POST'])
def filter_jobs():
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])
        criteria = data.get('criteria', {})
        
        if not jobs:
            return jsonify({
                'success': False,
                'error': 'No jobs provided for filtering'
            }), 400
        
        filtered_jobs = jobs.copy()
        
        # Filter by required skills
        required_skills = criteria.get('skills_required', [])
        if required_skills:
            filtered_jobs = [
                job for job in filtered_jobs
                if has_required_skills(job, required_skills)
            ]
        
        # Filter by minimum salary
        salary_min = criteria.get('salary_min')
        if salary_min:
            filtered_jobs = [
                job for job in filtered_jobs
                if meets_salary_requirement(job, salary_min)
            ]
        
        return jsonify({
            'success': True,
            'filtered_jobs': filtered_jobs,
            'total_filtered': len(filtered_jobs),
            'original_total': len(jobs)
        })
        
    except Exception as e:
        logger.error(f"Error in filter_jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions
def get_mock_jobs(keyword, location, limit):
    """Generate realistic mock jobs for fallback"""
    mock_jobs = []
    companies = ['Tech Corp', 'Innovation Inc', 'Future Tech', 'Digital Solutions', 'AI Innovations']
    locations = [location, 'Remote', 'San Francisco, CA', 'New York, NY', 'Austin, TX']
    
    for i in range(min(limit, 10)):
        mock_jobs.append({
            'title': f'{keyword.title()} Developer',
            'company': companies[i % len(companies)],
            'location': locations[i % len(locations)],
            'snippet': f'Looking for a {keyword} developer with experience in modern technologies.',
            'salary': f'${80000 + i * 10000} - ${120000 + i * 15000}',
            'posted_date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Mock Data',
            'job_url': '#',
            'skills': ['Python', 'JavaScript', 'React', 'Node.js']
        })
    
    return mock_jobs

def extract_skills_from_text(text):
    """Extract potential skills from text"""
    # Common programming skills
    common_skills = [
        'python', 'javascript', 'java', 'c++', 'go', 'rust', 'php', 'ruby',
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return found_skills

def categorize_skills(skill_percentages):
    """Categorize skills into groups"""
    categories = {
        'programming_languages': [],
        'frameworks': [],
        'databases': [],
        'cloud_platforms': [],
        'tools': []
    }
    
    for skill, percentage in skill_percentages.items():
        if any(lang in skill.lower() for lang in ['python', 'javascript', 'java', 'c++', 'go', 'rust']):
            categories['programming_languages'].append([skill, percentage])
        elif any(fw in skill.lower() for fw in ['react', 'angular', 'vue', 'django', 'flask', 'spring']):
            categories['frameworks'].append([skill, percentage])
        elif any(db in skill.lower() for db in ['mysql', 'postgresql', 'mongodb', 'redis']):
            categories['databases'].append([skill, percentage])
        elif any(cloud in skill.lower() for cloud in ['aws', 'azure', 'gcp', 'docker', 'kubernetes']):
            categories['cloud_platforms'].append([skill, percentage])
        else:
            categories['tools'].append([skill, percentage])
    
    # Sort each category by percentage
    for category in categories:
        categories[category].sort(key=lambda x: x[1], reverse=True)
    
    return categories

def has_required_skills(job, required_skills):
    """Check if job has required skills"""
    job_skills = job.get('skills', [])
    job_description = job.get('snippet', '') or job.get('description', '')
    
    for required_skill in required_skills:
        # Check in skills list
        if any(required_skill.lower() in skill.lower() for skill in job_skills):
            return True
        # Check in description
        if required_skill.lower() in job_description.lower():
            return True
    
    return False

def meets_salary_requirement(job, min_salary):
    """Check if job meets minimum salary requirement"""
    salary = job.get('salary', '')
    if not salary:
        return True  # Assume it meets requirement if no salary info
    
    # Extract numbers from salary string
    numbers = re.findall(r'\d+', salary)
    if numbers:
        return int(numbers[0]) >= min_salary
    
    return True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
