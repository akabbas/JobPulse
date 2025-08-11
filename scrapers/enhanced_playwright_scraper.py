#!/usr/bin/env python3
"""
Enhanced Playwright Scraper for JobPulse
Incorporates FetchHire's advanced 403 bypass technology
"""

import asyncio
import time
import random
import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup

class EnhancedPlaywrightScraper:
    """Advanced job scraper using Playwright to bypass 403 errors"""
    
    def __init__(self, headless: bool = True):
        """Initialize the enhanced Playwright scraper"""
        self.headless = headless
        self.setup_logging()
        
        # Rotating user agents (from FetchHire)
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Browser profiles for different contexts
        self.browser_profiles = [
            {'viewport': {'width': 1920, 'height': 1080}, 'locale': 'en-US'},
            {'viewport': {'width': 1366, 'height': 768}, 'locale': 'en-GB'},
            {'viewport': {'width': 1440, 'height': 900}, 'locale': 'en-CA'},
            {'viewport': {'width': 1536, 'height': 864}, 'locale': 'en-AU'}
        ]
        
        # Skills patterns (from FetchHire)
        self.skills_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin|PHP|Ruby|Scala|R|MATLAB)\b',
            r'\b(React|Angular|Vue\.js|Node\.js|Django|Flask|Spring|Express\.js|Laravel|Ruby on Rails|ASP\.NET|jQuery|Bootstrap|Tailwind CSS)\b',
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB|Elasticsearch)\b',
            r'\b(AWS|Azure|Google Cloud|Docker|Kubernetes|Terraform|Jenkins|GitLab|GitHub Actions|Ansible|Chef|Puppet)\b',
            r'\b(Salesforce|Apex|Lightning|Visualforce|SOQL|SOSL|Salesforce DX|Lightning Web Components|LWC|Aura)\b',
            r'\b(TensorFlow|PyTorch|Scikit-learn|Keras|OpenAI|Hugging Face|Pandas|NumPy|Matplotlib|Seaborn)\b',
            r'\b(HTML5|CSS3|SASS|LESS|Webpack|Babel|ESLint|Prettier|GraphQL|REST API|SOAP|WebSocket)\b',
            r'\b(Jest|Mocha|Jasmine|Cypress|Selenium|JUnit|TestNG|PyTest|NUnit|XUnit)\b',
            r'\b(Agile|Scrum|Kanban|Waterfall|TDD|BDD|CI/CD|Microservices|API|REST|GraphQL|OAuth|JWT)\b'
        ]
    
    def setup_logging(self):
        """Setup logging for the enhanced scraper"""
        # Ensure logs directory exists
        import os
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/enhanced_playwright_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def _init_browser(self):
        """Initialize Playwright browser with anti-detection measures"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with stealth options
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            
            # Create context with random profile
            profile = random.choice(self.browser_profiles)
            user_agent = random.choice(self.user_agents)
            
            self.context = await self.browser.new_context(
                user_agent=user_agent,
                viewport=profile['viewport'],
                locale=profile['locale'],
                timezone_id='America/New_York',
                permissions=['geolocation'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # NYC
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1'
                }
            )
            
            self.page = await self.context.new_page()
            
            # Add stealth scripts
            await self._add_stealth_scripts()
            
            self.logger.info(f"Browser initialized with user agent: {user_agent[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error initializing browser: {e}")
            raise
    
    async def _add_stealth_scripts(self):
        """Add stealth scripts to avoid detection"""
        try:
            # Override webdriver property
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Override plugins
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            # Override languages
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            # Override permissions
            await self.page.add_init_script("""
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            self.logger.info("Added stealth scripts to browser")
            
        except Exception as e:
            self.logger.warning(f"Error adding stealth scripts: {e}")
    
    async def _cleanup_browser(self):
        """Clean up browser resources"""
        try:
            if hasattr(self, 'page'):
                await self.page.close()
            if hasattr(self, 'context'):
                await self.context.close()
            if hasattr(self, 'browser'):
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            self.logger.info("Browser resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up browser: {e}")
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text (from FetchHire)"""
        if not text:
            return []
        
        skills = set()
        text_lower = text.lower()
        
        for pattern in self.skills_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        return list(skills)
    
    async def scrape_remote_ok(self, keyword: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Scrape Remote OK using Playwright (bypasses 403)"""
        self.logger.info("🌐 Scraping Remote OK with Playwright...")
        jobs = []
        
        try:
            await self._init_browser()
            
            # Navigate to Remote OK
            url = "https://remoteok.com/remote-dev-jobs"
            if keyword:
                url = f"https://remoteok.com/remote-{keyword}-jobs"
            
            await self.page.goto(url, wait_until='networkidle')
            await self.page.wait_for_timeout(random.randint(2000, 4000))
            
            # Wait for job listings to load
            await self.page.wait_for_selector('tr.job', timeout=10000)
            
            # Scroll to load more jobs
            await self._scroll_page(limit)
            
            # Extract job listings
            job_elements = await self.page.query_selector_all('tr.job')
            
            for i, job_elem in enumerate(job_elements[:limit]):
                try:
                    job_data = await self._extract_remote_ok_job(job_elem)
                    if job_data:
                        jobs.append(job_data)
                        self.logger.info(f"Extracted Remote OK job {i+1}: {job_data.get('title', 'Unknown')}")
                except Exception as e:
                    self.logger.warning(f"Error extracting Remote OK job {i+1}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping Remote OK: {e}")
        finally:
            await self._cleanup_browser()
        
        self.logger.info(f"Successfully scraped {len(jobs)} jobs from Remote OK")
        return jobs
    
    async def scrape_weworkremotely(self, keyword: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Scrape We Work Remotely using Playwright (bypasses 403)"""
        self.logger.info("🌐 Scraping We Work Remotely with Playwright...")
        jobs = []
        
        try:
            await self._init_browser()
            
            # Navigate to We Work Remotely
            url = "https://weworkremotely.com/categories/remote-programming-jobs"
            if keyword:
                url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
            
            await self.page.goto(url, wait_until='networkidle')
            await self.page.wait_for_timeout(random.randint(2000, 4000))
            
            # Wait for job listings to load
            await self.page.wait_for_selector('.jobs li', timeout=10000)
            
            # Scroll to load more jobs
            await self._scroll_page(limit)
            
            # Extract job listings
            job_elements = await self.page.query_selector_all('.jobs li')
            
            for i, job_elem in enumerate(job_elements[:limit]):
                try:
                    job_data = await self._extract_weworkremotely_job(job_elem)
                    if job_data:
                        jobs.append(job_data)
                        self.logger.info(f"Extracted We Work Remotely job {i+1}: {job_data.get('title', 'Unknown')}")
                except Exception as e:
                    self.logger.warning(f"Error extracting We Work Remotely job {i+1}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping We Work Remotely: {e}")
        finally:
            await self._cleanup_browser()
        
        self.logger.info(f"Successfully scraped {len(jobs)} jobs from We Work Remotely")
        return jobs
    
    async def scrape_remotive_api(self, keyword: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Scrape Remotive using their API (most reliable)"""
        self.logger.info("🌐 Scraping Remotive via API...")
        jobs = []
        
        try:
            # Remotive API endpoint
            url = "https://remotive.com/api/remote-jobs"
            if keyword:
                url = f"https://remotive.com/api/remote-jobs?search={keyword}"
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'jobs' in data:
                for i, job in enumerate(data['jobs'][:limit]):
                    try:
                        job_data = self._parse_remotive_job(job)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        self.logger.warning(f"Error parsing Remotive job {i+1}: {e}")
                        continue
            
        except Exception as e:
            self.logger.error(f"Error scraping Remotive: {e}")
        
        self.logger.info(f"Successfully scraped {len(jobs)} jobs from Remotive")
        return jobs
    
    async def _scroll_page(self, target_count: int):
        """Scroll page to load more content"""
        try:
            current_count = 0
            scroll_attempts = 0
            max_scrolls = 20
            
            while current_count < target_count and scroll_attempts < max_scrolls:
                # Get current job count
                current_count = await self.page.evaluate("""
                    () => {
                        const jobElements = document.querySelectorAll('tr.job, .jobs li, [data-testid="jobsearch-ResultsList"] > div');
                        return jobElements.length;
                    }
                """)
                
                if current_count >= target_count:
                    break
                
                # Scroll down
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.page.wait_for_timeout(random.randint(1000, 3000))
                
                # Wait for new content to load
                await self.page.wait_for_timeout(2000)
                
                scroll_attempts += 1
            
            self.logger.info(f"Scrolled {scroll_attempts} times, found {current_count} jobs")
            
        except Exception as e:
            self.logger.warning(f"Error during scrolling: {e}")
    
    async def _extract_remote_ok_job(self, job_elem) -> Optional[Dict[str, Any]]:
        """Extract job data from Remote OK job element"""
        try:
            # Extract job title
            title_elem = await job_elem.query_selector('td.company_and_position h2')
            title = await title_elem.text_content() if title_elem else "Unknown Title"
            
            # Extract company name
            company_elem = await job_elem.query_selector('td.company_and_position h3')
            company = await company_elem.text_content() if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = await job_elem.query_selector('td.location')
            location = await location_elem.text_content() if location_elem else "Remote"
            
            # Extract job URL
            job_link = await job_elem.query_selector('td.company_and_position h2 a')
            job_url = await job_link.get_attribute('href') if job_link else None
            if job_url:
                job_url = f"https://remoteok.com{job_url}"
            
            # Extract tags/skills
            tags_elem = await job_elem.query_selector('td.tags')
            tags_text = await tags_elem.text_content() if tags_elem else ""
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            
            # Extract salary if available
            salary_elem = await job_elem.query_selector('td.salary')
            salary = await salary_elem.text_content() if salary_elem else None
            
            # Extract posted date
            date_elem = await job_elem.query_selector('td.date')
            posted_date = await date_elem.text_content() if date_elem else None
            
            return {
                'title': title.strip(),
                'company': company.strip(),
                'location': location.strip(),
                'url': job_url,
                'tags': tags,
                'salary': salary.strip() if salary else None,
                'posted_date': posted_date.strip() if posted_date else None,
                'source': 'remote_ok',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting Remote OK job: {e}")
            return None
    
    async def _extract_weworkremotely_job(self, job_elem) -> Optional[Dict[str, Any]]:
        """Extract job data from We Work Remotely job element"""
        try:
            # Extract job title
            title_elem = await job_elem.query_selector('.title')
            title = await title_elem.text_content() if title_elem else "Unknown Title"
            
            # Extract company name
            company_elem = await job_elem.query_selector('.company')
            company = await company_elem.text_content() if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = await job_elem.query_selector('.region')
            location = await location_elem.text_content() if location_elem else "Remote"
            
            # Extract job URL
            job_link = await job_elem.query_selector('a')
            job_url = await job_link.get_attribute('href') if job_link else None
            if job_url:
                job_url = f"https://weworkremotely.com{job_url}"
            
            # Extract job type
            job_type_elem = await job_elem.query_selector('.job-type')
            job_type = await job_type_elem.text_content() if job_type_elem else "Full-time"
            
            return {
                'title': title.strip(),
                'company': company.strip(),
                'location': location.strip(),
                'url': job_url,
                'job_type': job_type.strip() if job_type else "Full-time",
                'source': 'weworkremotely',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting We Work Remotely job: {e}")
            return None
    
    def _parse_remotive_job(self, job: Dict) -> Optional[Dict[str, Any]]:
        """Parse Remotive API job data"""
        try:
            return {
                'title': job.get('title', 'Unknown Title'),
                'company': job.get('company_name', 'Unknown Company'),
                'location': job.get('candidate_required_location', 'Remote'),
                'url': job.get('url', None),
                'salary': job.get('salary', None),
                'job_type': job.get('employment_type', 'Full-time'),
                'description': job.get('description', ''),
                'tags': job.get('tags', []),
                'posted_date': job.get('publication_date', None),
                'source': 'remotive',
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"Error parsing Remotive job: {e}")
            return None
    
    async def scrape_all_sources(self, keyword: str = None, limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape all sources concurrently"""
        self.logger.info(f"🚀 Starting concurrent scraping for keyword: {keyword}")
        
        # Create scraping tasks
        tasks = [
            self.scrape_remote_ok(keyword, limit),
            self.scrape_weworkremotely(keyword, limit),
            self.scrape_remotive_api(keyword, limit)
        ]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_jobs = {}
        sources = ['remote_ok', 'weworkremotely', 'remotive']
        
        for i, result in enumerate(results):
            source = sources[i]
            if isinstance(result, Exception):
                self.logger.error(f"Error scraping {source}: {result}")
                all_jobs[source] = []
            else:
                all_jobs[source] = result
                self.logger.info(f"Successfully scraped {len(result)} jobs from {source}")
        
        # Remove duplicates across sources
        all_jobs['all_sources'] = self._remove_duplicates(all_jobs)
        
        self.logger.info(f"🎉 Scraping completed! Total unique jobs: {len(all_jobs['all_sources'])}")
        return all_jobs
    
    def _remove_duplicates(self, jobs_dict: Dict[str, List[Dict]]) -> List[Dict]:
        """Remove duplicate jobs across all sources"""
        all_jobs = []
        seen_titles = set()
        
        for source, jobs in jobs_dict.items():
            if source == 'all_sources':
                continue
            
            for job in jobs:
                # Create a unique identifier for the job
                job_id = f"{job.get('title', '')}_{job.get('company', '')}"
                
                if job_id not in seen_titles:
                    seen_titles.add(job_id)
                    all_jobs.append(job)
        
        return all_jobs
    
    def save_jobs_to_file(self, jobs: List[Dict], filename: str = 'enhanced_scraped_jobs.json'):
        """Save scraped jobs to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Jobs saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving jobs to file: {e}")

# Convenience function for synchronous usage
def scrape_jobs_enhanced(keyword: str = None, limit: int = 50, headless: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """Synchronous wrapper for enhanced job scraping"""
    scraper = EnhancedPlaywrightScraper(headless=headless)
    
    async def run_scraping():
        return await scraper.scrape_all_sources(keyword, limit)
    
    return asyncio.run(run_scraping())

if __name__ == "__main__":
    # Example usage
    async def main():
        scraper = EnhancedPlaywrightScraper(headless=False)
        
        # Scrape all sources
        all_jobs = await scraper.scrape_all_sources("Python Developer", 20)
        
        # Save results
        scraper.save_jobs_to_file(all_jobs['all_sources'])
        
        print(f"🎉 Scraping completed! Found {len(all_jobs['all_sources'])} unique jobs")
    
    asyncio.run(main())
