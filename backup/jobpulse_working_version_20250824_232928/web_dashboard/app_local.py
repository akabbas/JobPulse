#!/usr/bin/env python3
"""Ultra-Simple JobPulse Local Development Server - No Scrapers, Instant Loading"""

from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = 'dev-secret-key-local-only'
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': 'local_development',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-local',
        'note': 'Local dev server - no scrapers loaded'
    })

@app.route('/search', methods=['POST'])
def search_jobs():
    """Mock search endpoint for local development"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        location = data.get('location', 'United States')
        
        # Return mock data for local development
        mock_jobs = [
            {
                'title': f'{keyword} - Local Dev',
                'company': 'Local Development Company',
                'location': location,
                'description': f'This is a mock job for {keyword} in {location} - Local development mode',
                'url': '#',
                'source': 'local_dev',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'salary': '$80k - $120k',
                'skills': ['python', 'flask', 'local development'],
                'job_type': 'Full-time'
            },
            {
                'title': f'Senior {keyword}',
                'company': 'Local Tech Corp',
                'location': location,
                'description': f'Mock senior position for {keyword} - Testing local environment',
                'url': '#',
                'source': 'local_dev',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'salary': '$100k - $150k',
                'skills': ['python', 'flask', 'docker', 'testing'],
                'job_type': 'Full-time'
            },
            {
                'title': f'Full Stack {keyword}',
                'company': 'Local Startup Inc',
                'location': location,
                'description': f'Mock full stack position for {keyword} - Testing skills analysis',
                'url': '#',
                'source': 'local_dev',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'salary': '$90k - $140k',
                'skills': ['javascript', 'react', 'node.js', 'mongodb'],
                'job_type': 'Full-time'
            },
            {
                'title': f'DevOps {keyword}',
                'company': 'Local Cloud Corp',
                'location': location,
                'description': f'Mock DevOps position for {keyword} - Testing cloud skills',
                'url': '#',
                'source': 'local_dev',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'salary': '$110k - $160k',
                'skills': ['aws', 'docker', 'kubernetes', 'jenkins'],
                'job_type': 'Full-time'
            },
            {
                'title': f'Data {keyword}',
                'company': 'Local Data Corp',
                'location': location,
                'description': f'Mock data position for {keyword} - Testing ML skills',
                'url': '#',
                'source': 'local_dev',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'salary': '$95k - $145k',
                'skills': ['python', 'tensorflow', 'pandas', 'numpy'],
                'job_type': 'Full-time'
            }
        ]
        
        return jsonify({
            'success': True,
            'jobs': mock_jobs,
            'total_jobs': len(mock_jobs),
            'note': 'Local development mode - Mock data only',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in mock search: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'note': 'Local development mode'
        })

@app.route('/enhanced_search', methods=['POST'])
def enhanced_search():
    """Mock enhanced search endpoint for local development"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        limit = data.get('limit', 5)
        
        # Return mock enhanced search results
        mock_enhanced_jobs = [
            {
                'title': f'Enhanced {keyword} - Local Dev',
                'company': 'Local Enhanced Corp',
                'location': 'Remote',
                'description': f'Mock enhanced job for {keyword} - Testing local enhanced search',
                'url': '#',
                'source': 'local_enhanced',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'salary': '$90k - $130k',
                'skills': ['python', 'playwright', 'enhanced scraping'],
                'job_type': 'Full-time'
            },
            {
                'title': f'Remote {keyword} - Enhanced',
                'company': 'Local Remote Corp',
                'location': 'Remote',
                'description': f'Mock remote position for {keyword} - Testing enhanced search',
                'url': '#',
                'source': 'local_enhanced',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'salary': '$85k - $125k',
                'skills': ['javascript', 'vue.js', 'remote work'],
                'job_type': 'Full-time'
            },
            {
                'title': f'Startup {keyword} - Enhanced',
                'company': 'Local Startup Enhanced',
                'location': 'Remote',
                'description': f'Mock startup position for {keyword} - Testing enhanced search',
                'url': '#',
                'source': 'local_enhanced',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'salary': '$75k - $115k',
                'skills': ['react', 'typescript', 'startup experience'],
                'job_type': 'Full-time'
            }
        ]
        
        return jsonify({
            'success': True,
            'jobs': mock_enhanced_jobs,
            'total_jobs': len(mock_enhanced_jobs),
            'source_breakdown': {'local_enhanced': len(mock_enhanced_jobs)},
            'scraping_method': 'local_mock',
            'note': 'Local development mode - Mock enhanced search',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in mock enhanced search: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'note': 'Local development mode'
        })

@app.route('/analyze', methods=['POST'])
def analyze_jobs():
    """Mock analysis endpoint for local development"""
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])
        
        # Mock analysis results
        analysis_result = {
            'total_jobs': len(jobs),
            'skills_analysis': {
                'programming_languages': [('python', 100.0), ('javascript', 50.0)],
                'frameworks': [('flask', 100.0), ('django', 25.0)],
                'databases': [('postgresql', 75.0), ('mongodb', 25.0)],
                'cloud_platforms': [('aws', 50.0), ('docker', 75.0)]
            },
            'note': 'Local development mode - Mock analysis'
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in mock analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'note': 'Local development mode'
        })

@app.route('/filter', methods=['POST'])
def filter_jobs():
    """Mock filter endpoint for local development"""
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])
        criteria = data.get('criteria', {})
        
        # Simple mock filtering
        filtered_jobs = jobs[:2] if len(jobs) > 2 else jobs
        
        return jsonify({
            'success': True,
            'filtered_jobs': filtered_jobs,
            'total_filtered': len(filtered_jobs),
            'note': 'Local development mode - Mock filtering'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'note': 'Local development mode'
        })

if __name__ == '__main__':
    print("🚀 Starting JobPulse Local Development Server...")
    print("📍 Server will be available at: http://localhost:5002")
    print("📝 Note: This is a mock server for local development only")
    print("🔍 Real scraping features are available on Docker (port 5001)")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5002)
