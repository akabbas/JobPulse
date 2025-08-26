import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS
import asyncio
from playwright.async_api import async_playwright

class DiceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = "https://www.dice.com"
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/dice_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """Search for jobs using Playwright to bypass anti-bot measures"""
        try:
            # Try Playwright first (more reliable)
            self.logger.info("Attempting to scrape Dice using Playwright...")
            jobs = asyncio.run(self._search_with_playwright(keyword, location, limit))
            if jobs:
                self.logger.info(f"Successfully scraped {len(jobs)} jobs from Dice using Playwright")
                return jobs
        except Exception as e:
            self.logger.warning(f"Playwright scraping failed: {e}")
        
        # Fallback to requests-based scraping
        self.logger.info("Falling back to requests-based scraping...")
        return self._search_with_requests(keyword, location, limit)
    
    def _search_with_requests(self, keyword: str, location: str, limit: int) -> List[Dict]:
        """Fallback method using requests (may get blocked)"""
        jobs = []
        page = 0
        
        while len(jobs) < limit:
            try:
                search_url = f"{self.base_url}/jobs"
                params = {
                    'q': keyword,
                    'location': location,
                    'page': page + 1
                }
                self.logger.info(f"Searching Dice page {page + 1} for '{keyword}'")
                time.sleep(random.uniform(2, 4))
                response = self.session.get(search_url, params=params, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', {'class': 'card-body'})
                if not job_cards:
                    self.logger.warning("No job cards found on Dice page")
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
                self.logger.error(f"Error scraping Dice page {page}: {str(e)}")
                break
        self.logger.info(f"Scraped {len(jobs)} jobs from Dice for '{keyword}'")
        return jobs
    
    async def _search_with_playwright(self, keyword: str, location: str, limit: int) -> List[Dict]:
        """Search using Playwright to bypass anti-bot measures"""
        jobs = []
        
        async with async_playwright() as p:
            try:
                # Launch browser with stealth mode
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                # Add stealth scripts
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)
                
                page = await context.new_page()
                
                # Navigate to Dice search page
                search_url = f"{self.base_url}/jobs?q={keyword}&location={location}"
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                
                # Wait for job listings to load - Dice uses different selectors
                await page.wait_for_selector('div.card-body', timeout=10000)
                
                # Extract jobs from the page
                job_elements = await page.query_selector_all('div.card-body')
                
                for job_elem in job_elements[:limit]:
                    try:
                        job_data = await self._extract_job_data_playwright(job_elem, keyword)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting job data: {e}")
                        continue
                
                await browser.close()
                
            except Exception as e:
                self.logger.error(f"Playwright error: {e}")
                if 'browser' in locals():
                    await browser.close()
        
        return jobs
    
    async def _extract_job_data_playwright(self, job_elem, keyword: str) -> Optional[Dict]:
            """Extract job data from Playwright element"""
            try:
                # Extract job information using actual Dice selectors
                title = await job_elem.query_selector('h5.card-title')
                title_text = await title.text_content() if title else ""
                
                company = await job_elem.query_selector('span.company')
                company_text = await company.text_content() if company else ""
                
                location = await job_elem.query_selector('span.location')
                location_text = await location.text_content() if location else ""
                
                # Get job URL
                job_link = await job_elem.query_selector('a.card-title-link')
                job_url = await job_link.get_attribute('href') if job_link else ""
                if job_url and not job_url.startswith('http'):
                    job_url = self.base_url + job_url
                
                # Get snippet
                snippet = await job_elem.query_selector('div.card-description')
                snippet_text = await snippet.text_content() if snippet else ""
                
                # Extract skills
                skills = self._extract_skills(snippet_text, title_text)
                
                job_data = {
                    'title': title_text.strip(),
                    'company': company_text.strip(),
                    'location': location_text.strip(),
                    'salary': '',  # Dice doesn't show salary on search page
                    'snippet': snippet_text.strip(),
                    'job_url': job_url,
                    'skills': skills,
                    'search_keyword': keyword,
                    'source': 'dice',
                    'scraped_at': datetime.now().isoformat()
                }
                
                return job_data
                
            except Exception as e:
                self.logger.error(f"Error extracting Playwright job data: {str(e)}")
                return None
    
    def _extract_job_data(self, card, keyword: str) -> Optional[Dict]:
        try:
            # Job title
            title_elem = card.find('h5', {'class': 'card-title'})
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Company name
            company_elem = card.find('span', {'class': 'company'})
            company = company_elem.get_text(strip=True) if company_elem else ""
            
            # Location
            location_elem = card.find('span', {'class': 'location'})
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Job URL
            job_link = card.find('a', {'class': 'card-title-link'})
            job_url = self.base_url + job_link['href'] if job_link else ""
            
            # Salary (if available)
            salary_elem = card.find('span', {'class': 'salary'})
            salary = salary_elem.get_text(strip=True) if salary_elem else ""
            
            # Job description snippet
            snippet_elem = card.find('div', {'class': 'card-description'})
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
                'source': 'dice',
                'scraped_at': datetime.now().isoformat()
            }
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error extracting Dice job data: {str(e)}")
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