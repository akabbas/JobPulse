#!/usr/bin/env python3
"""Simplified JobPulse Web Dashboard with Enhanced Scraper Integration"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only the enhanced scraper
from scrapers.enhanced_playwright_scraper import EnhancedPlaywrightScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Initialize enhanced scraper
enhanced_scraper = EnhancedPlaywrightScraper(headless=True)

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
        'enhanced_scraper': 'enabled'
    })

@app.route('/enhanced_search', methods=['POST'])
def enhanced_search():
    """Enhanced search using Playwright scraper (bypasses 403 errors)"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'software engineer')
        limit = data.get('limit', 20)  # Default to 20 for enhanced scraping
        headless = data.get('headless', True)
        
        logger.info(f"Starting enhanced search for '{keyword}' with limit {limit}")
        
        # Use the enhanced scraper
        results = enhanced_scraper.scrape_all_sources(keyword, limit)
        
        # Get all unique jobs
        all_jobs = results.get('all_sources', [])
        
        # Add source breakdown for transparency
        source_breakdown = {}
        for source, jobs in results.items():
            if source != 'all_sources':
                source_breakdown[source] = len(jobs)
        
        logger.info(f"Enhanced search completed: {len(all_jobs)} unique jobs found")
        
        return jsonify({
            'success': True,
            'jobs': all_jobs,
            'total_jobs': len(all_jobs),
            'source_breakdown': source_breakdown,
            'scraping_method': 'enhanced_playwright',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced_search: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'scraping_method': 'enhanced_playwright'
        })

@app.route('/test_enhanced')
def test_enhanced():
    """Test endpoint for enhanced scraper"""
    try:
        # Test with a simple search
        results = enhanced_scraper.scrape_all_sources("Python Developer", 5)
        return jsonify({
            'success': True,
            'message': 'Enhanced scraper is working!',
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
