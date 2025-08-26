import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
from config.settings import HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS

class StackOverflowScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = "https://stackoverflow.com/jobs"
        self.setup_logging()
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/stackoverflow_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 50) -> List[Dict]:
        jobs = []
        page = 1
        while len(jobs) < limit:
            try:
                search_url = f"{self.base_url}"
                params = {
                    'q': keyword,
                    'l': location,
                    'pg': page
                }
                self.logger.info(f"Searching Stack Overflow page {page} for '{keyword}'")
                time.sleep(random.uniform(1, 3))
                response = self.session.get(search_url, params=params, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', {'class': '-job'})
                if not job_cards:
                    self.logger.warning("No job cards found on Stack Overflow page")
                    break
                for card in job_cards:
                    if len(jobs) >= limit:
                        break
                    job_data = self._extract_job_data(card, keyword)
                    if job_data:
                        jobs.append(job_data)
                page += 1
            except Exception as e:
                self.logger.error(f"Error scraping Stack Overflow page {page}: {str(e)}")
                break
        self.logger.info(f"Scraped {len(jobs)} jobs from Stack Overflow for '{keyword}'")
        return jobs
    def _extract_job_data(self, card, keyword: str) -> Optional[Dict]:
        try:
            title_elem = card.find('h2', {'class': 'mb4'})
            title = title_elem.get_text(strip=True) if title_elem else ""
            company_elem = card.find('h3', {'class': 'mb4'})
            company = company_elem.get_text(strip=True) if company_elem else ""
            location_elem = card.find('span', {'class': 'fc-black-500'})
            location = location_elem.get_text(strip=True) if location_elem else ""
            job_link = card.find('a', {'class': 's-link'})
            job_url = self.base_url + job_link['href'] if job_link else ""
            snippet_elem = card.find('div', {'class': 'ps-relative'})
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            skills = self._extract_skills(snippet)
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary': '',
                'snippet': snippet,
                'job_url': job_url,
                'skills': skills,
                'search_keyword': keyword,
                'source': 'stackoverflow',
                'scraped_at': datetime.now().isoformat()
            }
            return job_data
        except Exception as e:
            self.logger.error(f"Error extracting Stack Overflow job data: {str(e)}")
            return None
    def _extract_skills(self, text: str) -> List[str]:
        skills = []
        text_lower = text.lower()
        for category, skill_list in TECH_SKILLS.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    skills.append(skill)
        return list(set(skills)) 