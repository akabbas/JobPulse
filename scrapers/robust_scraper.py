import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import HEADERS, ALTERNATIVE_HEADERS, MOBILE_HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS

class RobustScraper:
    """
    Base class for robust web scraping with multiple fallback strategies
    """
    
    def __init__(self, base_url: str, scraper_name: str):
        self.base_url = base_url
        self.scraper_name = scraper_name
        self.session = requests.Session()
        self.setup_logging()
        self.setup_session()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/{self.scraper_name}_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_session(self):
        """Setup session with rotating headers"""
        self.session.headers.update(ALTERNATIVE_HEADERS)
        self.session.headers.update({
            'Referer': 'https://www.google.com/',
            'Sec-Fetch-User': '?1'
        })
    
    def make_request(self, url: str, params: Dict = None, max_retries: int = 3) -> Optional[requests.Response]:
        """Make a request with multiple fallback strategies"""
        headers_list = [ALTERNATIVE_HEADERS, HEADERS, MOBILE_HEADERS]
        
        for attempt in range(max_retries):
            try:
                # Try different headers
                headers = headers_list[attempt % len(headers_list)]
                self.session.headers.update(headers)
                
                # Add random delay
                time.sleep(random.uniform(2, 4))
                
                self.logger.info(f"Attempt {attempt + 1} for {url}")
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    self.logger.warning(f"403 error on attempt {attempt + 1}, trying different headers...")
                    continue
                else:
                    self.logger.error(f"HTTP {response.status_code} error")
                    break
                    
            except Exception as e:
                self.logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return None
                continue
        
        return None
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """Generic job search method - override in subclasses"""
        jobs = []
        page = 0
        
        while len(jobs) < limit:
            try:
                # Get search URL and params from subclass
                search_url, params = self.get_search_params(keyword, location, page)
                
                self.logger.info(f"Searching {self.scraper_name} page {page + 1} for '{keyword}'")
                
                response = self.make_request(search_url, params)
                if not response:
                    self.logger.error(f"Failed to get response from {self.scraper_name}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = self.find_job_cards(soup)
                
                if not job_cards:
                    self.logger.warning(f"No job cards found on {self.scraper_name} page")
                    break
                
                for card in job_cards:
                    if len(jobs) >= limit:
                        break
                    job_data = self._extract_job_data(card, keyword)
                    if job_data:
                        jobs.append(job_data)
                
                page += 1
                time.sleep(random.uniform(2, 3))
                
            except Exception as e:
                self.logger.error(f"Error scraping {self.scraper_name} page {page}: {str(e)}")
                break
        
        self.logger.info(f"Scraped {len(jobs)} jobs from {self.scraper_name} for '{keyword}'")
        return jobs
    
    def get_search_params(self, keyword: str, location: str, page: int) -> tuple:
        """Get search URL and parameters - override in subclasses"""
        raise NotImplementedError
    
    def find_job_cards(self, soup: BeautifulSoup) -> List:
        """Find job cards in the page - override in subclasses"""
        raise NotImplementedError
    
    def _extract_job_data(self, card, keyword: str) -> Optional[Dict]:
        """Extract job data from a card - override in subclasses"""
        raise NotImplementedError
    
    def _extract_skills(self, text: str, title: str) -> List[str]:
        """Extract skills from text and title"""
        skills = []
        text_lower = text.lower()
        title_lower = title.lower()
        combined_text = f"{text} {title}".lower()
        
        # Extract skills from TECH_SKILLS using word boundaries
        for category, skill_list in TECH_SKILLS.items():
            for skill in skill_list:
                if len(skill) > 2:
                    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                    if re.search(pattern, combined_text):
                        skills.append(skill)
        
        # If no skills found, add some based on common patterns
        if not skills:
            if 'python' in combined_text or 'developer' in combined_text:
                skills.extend(['python', 'javascript', 'git'])
            if 'react' in combined_text or 'frontend' in combined_text:
                skills.extend(['react', 'javascript', 'html', 'css'])
            if 'java' in combined_text:
                skills.extend(['java', 'spring', 'sql'])
            if 'data' in combined_text or 'analytics' in combined_text:
                skills.extend(['python', 'sql', 'pandas', 'numpy'])
            if 'devops' in combined_text or 'cloud' in combined_text:
                skills.extend(['aws', 'docker', 'kubernetes', 'terraform'])
            if 'machine learning' in combined_text or 'ai' in combined_text:
                skills.extend(['python', 'tensorflow', 'scikit-learn', 'pandas'])
            if 'full stack' in combined_text:
                skills.extend(['javascript', 'react', 'node.js', 'python', 'sql'])
            if 'backend' in combined_text:
                skills.extend(['python', 'java', 'sql', 'node.js'])
            if 'frontend' in combined_text:
                skills.extend(['javascript', 'react', 'html', 'css'])
            
            # If still no skills, add some common ones
            if not skills:
                skills.extend(['python', 'javascript', 'git'])
        
        skills = list(set(skills))
        
        if skills:
            self.logger.info(f"Extracted skills: {skills}")
        else:
            self.logger.warning(f"No skills extracted from text: {text[:100]}... and title: {title}")
        
        return skills 