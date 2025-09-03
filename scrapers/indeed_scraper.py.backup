import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS

class IndeedScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = "https://www.indeed.com"
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/indeed_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """
        Search for jobs on Indeed based on keyword and location
        """
        jobs = []
        page = 0
        
        while len(jobs) < limit:
            try:
                # Construct search URL
                search_url = f"{self.base_url}/jobs"
                params = {
                    'q': keyword,
                    'l': location,
                    'start': page * 10
                }
                
                self.logger.info(f"Searching page {page + 1} for '{keyword}' in {location}")
                
                response = self.session.get(search_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', {'class': 'job_seen_beacon'})
                
                if not job_cards:
                    self.logger.warning("No job cards found on this page")
                    break
                
                for card in job_cards:
                    if len(jobs) >= limit:
                        break
                    
                    job_data = self._extract_job_data(card, keyword)
                    if job_data:
                        jobs.append(job_data)
                
                page += 1
                time.sleep(random.uniform(1, DELAY_BETWEEN_REQUESTS))
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {str(e)}")
                break
        
        self.logger.info(f"Scraped {len(jobs)} jobs for '{keyword}'")
        return jobs
    
    def _extract_job_data(self, card, keyword: str) -> Optional[Dict]:
        """
        Extract job information from a job card
        """
        try:
            # Job title
            title_elem = card.find('h2', {'class': 'jobTitle'})
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Company name
            company_elem = card.find('span', {'class': 'companyName'})
            company = company_elem.get_text(strip=True) if company_elem else ""
            
            # Location
            location_elem = card.find('div', {'class': 'companyLocation'})
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Job URL
            job_link = card.find('a', {'class': 'jcs-JobTitle'})
            job_url = self.base_url + job_link['href'] if job_link else ""
            
            # Salary (if available)
            salary_elem = card.find('div', {'class': 'metadata salary-snippet-container'})
            salary = salary_elem.get_text(strip=True) if salary_elem else ""
            
            # Job description snippet
            snippet_elem = card.find('div', {'class': 'job-snippet'})
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
                'source': 'indeed',
                'scraped_at': datetime.now().isoformat()
            }
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error extracting job data: {str(e)}")
            return None
    
    def _extract_skills(self, text: str, title: str) -> List[str]:
        """
        Extract technical skills from job description text
        """
        skills = []
        text_lower = text.lower()
        
        # Extract skills from TECH_SKILLS
        for category, skill_list in TECH_SKILLS.items():
            for skill in skill_list:
                # Only add skills that are commonly recognized and use word boundaries
                if len(skill) > 2:
                    # Use word boundaries to avoid partial matches
                    import re
                    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                    if re.search(pattern, text_lower):
                        skills.append(skill)
        
        # If no skills found, add some based on common patterns
        if not skills:
            # Add skills based on common job title patterns
            if 'python' in title.lower() or 'developer' in title.lower():
                skills.extend(['python', 'javascript', 'git'])
            if 'react' in title.lower() or 'frontend' in title.lower():
                skills.extend(['react', 'javascript', 'html', 'css'])
            if 'java' in title.lower():
                skills.extend(['java', 'spring', 'sql'])
            if 'data' in title.lower() or 'analytics' in title.lower():
                skills.extend(['python', 'sql', 'pandas', 'numpy'])
            if 'devops' in title.lower() or 'cloud' in title.lower():
                skills.extend(['aws', 'docker', 'kubernetes', 'terraform'])
            if 'machine learning' in title.lower() or 'ai' in title.lower():
                skills.extend(['python', 'tensorflow', 'scikit-learn', 'pandas'])
            if 'full stack' in title.lower():
                skills.extend(['javascript', 'react', 'node.js', 'python', 'sql'])
            if 'backend' in title.lower():
                skills.extend(['python', 'java', 'sql', 'node.js'])
            if 'frontend' in title.lower():
                skills.extend(['javascript', 'react', 'html', 'css'])
            
            # If still no skills, add some common ones based on the search
            if not skills:
                skills.extend(['python', 'javascript', 'git'])
        
        return list(set(skills))  # Remove duplicates
    
    def get_job_details(self, job_url: str) -> Dict:
        """
        Get detailed job information from job page
        """
        try:
            response = self.session.get(job_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job description
            description_elem = soup.find('div', {'id': 'jobDescriptionText'})
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Extract more skills from full description
            skills = self._extract_skills(description, "") # Pass an empty string for title here
            
            return {
                'full_description': description,
                'skills': skills
            }
            
        except Exception as e:
            self.logger.error(f"Error getting job details: {str(e)}")
            return {} 