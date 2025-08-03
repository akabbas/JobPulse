import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS

class RemoteOKScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = "https://remoteok.com"
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/remoteok_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        jobs = []
        page = 0
        
        while len(jobs) < limit:
            try:
                search_url = f"{self.base_url}/remote-{keyword.replace(' ', '-')}-jobs"
                if page > 0:
                    search_url += f"?page={page + 1}"
                
                self.logger.info(f"Searching Remote OK page {page + 1} for '{keyword}'")
                time.sleep(random.uniform(2, 4))
                response = self.session.get(search_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('tr', {'class': 'job'})
                if not job_cards:
                    self.logger.warning("No job cards found on Remote OK page")
                    break
                for card in job_cards:
                    if len(jobs) >= limit:
                        break
                    job_data = self._extract_job_data(card, keyword)
                    if job_data:
                        jobs.append(job_data)
                page += 1
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                self.logger.error(f"Error scraping Remote OK page {page}: {str(e)}")
                break
        self.logger.info(f"Scraped {len(jobs)} jobs from Remote OK for '{keyword}'")
        return jobs
    
    def _extract_job_data(self, card, keyword: str) -> Optional[Dict]:
        try:
            # Job title
            title_elem = card.find('h2', {'itemprop': 'title'})
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Company name
            company_elem = card.find('h3', {'itemprop': 'hiringOrganization'})
            company = company_elem.get_text(strip=True) if company_elem else ""
            
            # Location (Remote jobs)
            location = "Remote"
            
            # Job URL
            job_link = card.find('a', {'class': 'preventLink'})
            job_url = self.base_url + job_link['href'] if job_link else ""
            
            # Salary (if available)
            salary_elem = card.find('span', {'class': 'salary'})
            salary = salary_elem.get_text(strip=True) if salary_elem else ""
            
            # Job description snippet
            snippet_elem = card.find('td', {'class': 'company_and_position'})
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            # Extract skills from snippet and title
            skills = self._extract_skills(snippet, title)
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'snippet': snippet,
                'job_url': job_url,
                'skills': skills,
                'search_keyword': keyword,
                'source': 'remoteok',
                'scraped_at': datetime.now().isoformat()
            }
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error extracting Remote OK job data: {str(e)}")
            return None
    
    def _extract_skills(self, text: str, title: str) -> List[str]:
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