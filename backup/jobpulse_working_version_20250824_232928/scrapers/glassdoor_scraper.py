import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
from config.settings import HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS

class GlassdoorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = "https://www.glassdoor.com"
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/glassdoor_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """
        Search for jobs on Glassdoor based on keyword and location
        Note: This is a simplified version for testing
        """
        # For testing, return sample data
        sample_jobs = [
            {
                'title': f'Sample {keyword} Position',
                'company': 'Sample Company',
                'location': location,
                'salary': '$80,000 - $120,000',
                'snippet': f'We are looking for a {keyword} with experience in Python, React, and AWS.',
                'job_url': 'https://example.com',
                'skills': ['python', 'react', 'aws'],
                'search_keyword': keyword,
                'source': 'glassdoor',
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        self.logger.info(f"Returning {len(sample_jobs)} sample jobs for '{keyword}'")
        return sample_jobs 