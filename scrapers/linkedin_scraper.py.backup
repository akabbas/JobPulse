import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
from config.settings import HEADERS, ALTERNATIVE_HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS
import re

class LinkedInScraper:
    def __init__(self):
        self.session = requests.Session()
        # Try alternative headers first
        self.session.headers.update(ALTERNATIVE_HEADERS)
        self.base_url = "https://www.linkedin.com/jobs"
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/linkedin_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        jobs = []
        page = 0
        
        while len(jobs) < limit:
            try:
                search_url = f"{self.base_url}/search"
                params = {
                    'keywords': keyword,
                    'location': location,
                    'start': page * 25
                }
                self.logger.info(f"Searching LinkedIn page {page + 1} for '{keyword}'")
                time.sleep(random.uniform(3, 5))  # Increased delay
                response = self.session.get(search_url, params=params, timeout=30)
                
                # If we get 403, try with different headers
                if response.status_code == 403:
                    self.logger.warning("Got 403, trying with different headers...")
                    self.session.headers.update(HEADERS)
                    response = self.session.get(search_url, params=params, timeout=30)
                
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', {'class': 'base-card'})
                if not job_cards:
                    self.logger.warning("No job cards found on LinkedIn page")
                    break
                for card in job_cards:
                    if len(jobs) >= limit:
                        break
                    job_data = self._extract_job_data(card, keyword)
                    if job_data:
                        jobs.append(job_data)
                page += 1
                # Add a small delay between pages to be respectful
                time.sleep(random.uniform(2, 3))
            except Exception as e:
                self.logger.error(f"Error scraping LinkedIn page {page}: {str(e)}")
                break
        self.logger.info(f"Scraped {len(jobs)} jobs from LinkedIn for '{keyword}'")
        return jobs
    def _extract_job_data(self, card, keyword: str) -> Optional[Dict]:
        try:
            title_elem = card.find('h3', {'class': 'base-search-card__title'})
            title = title_elem.get_text(strip=True) if title_elem else ""
            company_elem = card.find('h4', {'class': 'base-search-card__subtitle'})
            company = company_elem.get_text(strip=True) if company_elem else ""
            location_elem = card.find('span', {'class': 'job-search-card__location'})
            location = location_elem.get_text(strip=True) if location_elem else ""
            job_link = card.find('a', {'class': 'base-card__full-link'})
            job_url = job_link['href'] if job_link else ""
            snippet_elem = card.find('div', {'class': 'base-search-card__snippet'})
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            skills = self._extract_skills(snippet, title)
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary': '',
                'snippet': snippet,
                'job_url': job_url,
                'skills': skills,
                'search_keyword': keyword,
                'source': 'linkedin',
                'scraped_at': datetime.now().isoformat()
            }
            return job_data
        except Exception as e:
            self.logger.error(f"Error extracting LinkedIn job data: {str(e)}")
            return None
    def _extract_skills(self, text: str, title: str = "") -> List[str]:
        skills = []
        text_lower = text.lower()
        title_lower = title.lower()
        
        # Combine text and title for skill extraction
        combined_text = f"{text} {title}".lower()
        
        # Extract skills from TECH_SKILLS
        for category, skill_list in TECH_SKILLS.items():
            for skill in skill_list:
                # Only add skills that are commonly recognized and use word boundaries
                if len(skill) > 2:
                    # Use word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                    if re.search(pattern, combined_text):
                        skills.append(skill)
        
        # If no skills found, add some based on common patterns in title and text
        if not skills:
            # Add skills based on common job title patterns
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
            if 'software engineer' in combined_text:
                skills.extend(['python', 'javascript', 'git', 'sql'])
            if 'senior' in combined_text:
                skills.extend(['python', 'javascript', 'aws', 'docker'])
            if 'junior' in combined_text:
                skills.extend(['python', 'javascript', 'git'])
            
            # If still no skills, add some common ones based on the search
            if not skills:
                skills.extend(['python', 'javascript', 'git'])
        
        # Remove duplicates and return
        skills = list(set(skills))
        
        # Debug logging
        if skills:
            self.logger.info(f"Extracted skills: {skills}")
        else:
            self.logger.warning(f"No skills extracted from text: {text[:100]}... and title: {title}")
        
        return skills 