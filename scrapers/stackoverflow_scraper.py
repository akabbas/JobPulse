import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
from config.settings import HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS
import asyncio
from playwright.async_api import async_playwright

class StackOverflowScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = "https://stackoverflowjobs.com"
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
        """Search for jobs using Playwright to bypass anti-bot measures"""
        try:
            # Try Playwright first (more reliable)
            self.logger.info("Attempting to scrape Stack Overflow using Playwright...")
            jobs = asyncio.run(self._search_with_playwright(keyword, location, limit))
            if jobs:
                self.logger.info(f"Successfully scraped {len(jobs)} jobs from Stack Overflow using Playwright")
                return jobs
        except Exception as e:
            self.logger.warning(f"Playwright scraping failed: {e}")
        
        # Fallback to requests-based scraping
        self.logger.info("Falling back to requests-based scraping...")
        return self._search_with_requests(keyword, location, limit)
    
    def _search_with_requests(self, keyword: str, location: str, limit: int) -> List[Dict]:
        """Fallback method using requests (may get blocked)"""
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
                
                # Navigate to Stack Overflow jobs page
                search_url = f"{self.base_url}/jobs?q={keyword}&l={location}"
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                
                # Wait for job listings to load - Stack Overflow Jobs uses different selectors
                await page.wait_for_selector('div.job-result', timeout=10000)
                
                # Extract jobs from the page
                job_elements = await page.query_selector_all('div.job-result')
                
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
            # Extract job information using Playwright selectors
            title = await job_elem.query_selector('h2.mb4')
            title_text = await title.text_content() if title else ""
            
            company = await job_elem.query_selector('h3.mb4')
            company_text = await company.text_content() if company else ""
            
            location = await job_elem.query_selector('span.fc-black-500')
            location_text = await location.text_content() if location else ""
            
            # Get job URL
            job_link = await job_elem.query_selector('a.s-link')
            job_url = await job_link.get_attribute('href') if job_link else ""
            if job_url and not job_url.startswith('http'):
                job_url = self.base_url + job_url
            
            # Get snippet
            snippet = await job_elem.query_selector('div.ps-relative')
            snippet_text = await snippet.text_content() if snippet else ""
            
            # Extract skills
            skills = self._extract_skills(snippet_text)
            
            job_data = {
                'title': title_text.strip(),
                'company': company_text.strip(),
                'location': location_text.strip(),
                'salary': '',  # Stack Overflow doesn't show salary on search page
                'snippet': snippet_text.strip(),
                'job_url': job_url,
                'skills': skills,
                'search_keyword': keyword,
                'source': 'stackoverflow',
                'scraped_at': datetime.now().isoformat()
            }
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error extracting Playwright job data: {str(e)}")
            return None
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