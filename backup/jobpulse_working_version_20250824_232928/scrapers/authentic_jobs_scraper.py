import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import TECH_SKILLS

class AuthenticJobsScraper:
    """Scraper for Authentic Jobs (Tech-heavy remote jobs)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.base_url = "https://authenticjobs.com"
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/authentic_jobs_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "Remote", limit: int = 25) -> List[Dict]:
        """Search for jobs on Authentic Jobs"""
        try:
            self.logger.info(f"Searching Authentic Jobs for '{keyword}'")
            
            # Authentic Jobs search URL
            search_url = f"{self.base_url}/jobs"
            
            # Add search parameters
            params = {
                'search': keyword,
                'location': location
            }
            
            time.sleep(random.uniform(1, 2))  # Be respectful
            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            jobs = self._parse_authentic_jobs_page(response.text, keyword, limit)
            
            self.logger.info(f"Found {len(jobs)} jobs from Authentic Jobs")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error searching Authentic Jobs: {e}")
            return []
    
    def _parse_authentic_jobs_page(self, html_content: str, keyword: str, limit: int) -> List[Dict]:
        """Parse Authentic Jobs listings page"""
        jobs = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # Look for job listings - try multiple selectors
            job_listings = soup.find_all('div', {'class': 'job-listing'})
            
            # Alternative selectors if the above doesn't work
            if not job_listings:
                job_listings = soup.find_all(['div', 'article'], {'class': re.compile(r'job|listing|post', re.I)})
            
            # If still no results, try looking for any div with job-related content
            if not job_listings:
                job_listings = soup.find_all('div', string=re.compile(r'engineer|developer|designer|manager', re.I))
            
            for listing in job_listings[:limit]:
                try:
                    job = self._extract_job_info(listing, keyword)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.debug(f"Error extracting job from listing: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error parsing Authentic Jobs HTML: {e}")
        
        return jobs[:limit]
    
    def _extract_job_info(self, listing, keyword: str) -> Optional[Dict]:
        """Extract job information from a listing element"""
        try:
            # Extract title
            title_elem = listing.find(['h2', 'h3', 'h4']) or listing.find('a', {'class': 'job-title'})
            title = title_elem.get_text(strip=True) if title_elem else f"{keyword} Position"
            
            # Extract company
            company_elem = listing.find(['div', 'span'], {'class': re.compile(r'company|employer', re.I)})
            company = company_elem.get_text(strip=True) if company_elem else "Company Not Specified"
            
            # Extract location
            location_elem = listing.find(['div', 'span'], {'class': re.compile(r'location|place', re.I)})
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            
            # Extract description/snippet
            snippet_elem = listing.find(['div', 'p'], {'class': re.compile(r'description|summary|snippet', re.I)})
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else f"Join our team as a {keyword}"
            
            # Extract URL
            url_elem = listing.find('a')
            job_url = url_elem.get('href') if url_elem else f"{self.base_url}/jobs"
            if job_url.startswith('/'):
                job_url = self.base_url + job_url
            
            # Extract skills from title and snippet
            skills = self._extract_skills(snippet, title)
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'snippet': snippet,
                'salary': 'Competitive',  # Authentic Jobs usually doesn't show salary
                'job_url': job_url,
                'skills': skills,
                'search_keyword': keyword,
                'source': 'authentic_jobs',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.debug(f"Error extracting job info: {e}")
            return None
    
    def _extract_skills(self, snippet: str, title: str) -> List[str]:
        """Extract skills from job title and description"""
        skills = []
        
        # Combine title and snippet for skill extraction
        text = f"{title} {snippet}".lower()
        
        # Check for common tech skills
        for skill in TECH_SKILLS:
            if skill.lower() in text:
                skills.append(skill)
        
        return skills[:5]  # Limit to 5 skills
