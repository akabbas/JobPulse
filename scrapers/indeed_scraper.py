#!/usr/bin/env python3
"""
Professional Anti-Detection Indeed Scraper
Uses Playwright with advanced stealth techniques to bypass bot detection
"""

import asyncio
import time
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import pickle

# Playwright imports
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright_stealth import Stealth

# User agent rotation
from fake_useragent import UserAgent

# Configuration
from config.settings import TECH_SKILLS

# Proxy rotation
from scrapers.proxy_manager import ProxyRotationManager, ProxyInfo
from config.proxy_config import DEFAULT_PROXY_CONFIG, GEOGRAPHIC_TARGETING

class SessionManager:
    """Manages browser sessions and cookies to maintain state"""
    
    def __init__(self, session_dir: str = "sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.cookies_file = self.session_dir / "indeed_cookies.pkl"
        
    def save_session(self, context: BrowserContext):
        """Save browser context state"""
        try:
            cookies = context.cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
        except Exception as e:
            logging.warning(f"Failed to save session: {e}")
    
    def load_session(self, context: BrowserContext) -> bool:
        """Load browser context state"""
        try:
            if self.cookies_file.exists():
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                context.add_cookies(cookies)
                return True
        except Exception as e:
            logging.warning(f"Failed to load session: {e}")
        return False

class UserAgentRotator:
    """Manages rotation of realistic user agents"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.custom_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
        self.current_index = 0
    
    def get_next_agent(self) -> str:
        """Get next user agent in rotation"""
        if random.random() < 0.7:
            agent = self.custom_agents[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.custom_agents)
            return agent
        else:
            return self.ua.random

class HumanBehaviorSimulator:
    """Simulates realistic human behavior patterns"""
    
    async def random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add random delay between actions"""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    async def humanize_mouse_movement(self, page: Page):
        """Simulate realistic mouse movements"""
        try:
            viewport = page.viewport_size
            if not viewport:
                return
            
            start_x, start_y = random.randint(100, 300), random.randint(100, 200)
            end_x, end_y = random.randint(400, 700), random.randint(300, 500)
            
            # Move mouse along path
            for i in range(5):
                x = start_x + (end_x - start_x) * i / 4
                y = start_y + (end_y - start_y) * i / 4
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.01, 0.05))
                
        except Exception as e:
            logging.debug(f"Mouse movement simulation failed: {e}")
    
    async def humanize_scrolling(self, page: Page):
        """Simulate realistic scrolling behavior"""
        try:
            scroll_amount = random.randint(100, 500)
            steps = random.randint(3, 8)
            for i in range(steps):
                step_amount = scroll_amount // steps
                await page.mouse.wheel(0, step_amount)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            await self.random_delay(0.5, 1.5)
            
        except Exception as e:
            logging.debug(f"Scrolling simulation failed: {e}")

class StealthIndeedScraper:
    """Professional anti-detection Indeed scraper with advanced stealth techniques"""
    
    def __init__(self, 
                 use_proxy: bool = True, 
                 proxy_config: Dict[str, Any] = None,
                 geographic_targeting: bool = True):
        self.base_url = "https://www.indeed.com"
        self.setup_logging()
        
        # Initialize components
        self.session_manager = SessionManager()
        self.user_agent_rotator = UserAgentRotator()
        self.human_simulator = HumanBehaviorSimulator()
        
        # Proxy configuration
        self.use_proxy = use_proxy
        self.proxy_config = proxy_config or DEFAULT_PROXY_CONFIG
        self.geographic_targeting = geographic_targeting
        
        # Initialize proxy rotation manager
        if self.use_proxy:
            self.proxy_manager = ProxyRotationManager(self.proxy_config)
            self.logger.info("Proxy rotation manager initialized")
        else:
            self.proxy_manager = None
            self.logger.info("Proxy rotation disabled")
        
        # Stealth configuration
        self.stealth_config = {
            'viewport': {
                'width': random.randint(1200, 1920),
                'height': random.randint(800, 1080)
            },
            'user_agent': self.user_agent_rotator.get_next_agent(),
            'locale': 'en-US',
            'timezone_id': 'America/New_York'
        }
        
        # Browser fingerprinting evasion
        self.browser_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--no-first-run',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-notifications',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
        ]
        
        self.logger.info("Professional Stealth Indeed Scraper initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/stealth_indeed_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def _create_stealth_browser(self) -> Browser:
        """Create browser with advanced stealth capabilities"""
        try:
            playwright = await async_playwright().start()
            
            browser = await playwright.chromium.launch(
                headless=False,
                args=self.browser_args,
                slow_mo=100
            )
            
            self.logger.info("Stealth browser launched successfully")
            return browser
            
        except Exception as e:
            self.logger.error(f"Failed to create stealth browser: {e}")
            raise
    
    async def _create_stealth_context(self, browser: Browser, target_country: str = None) -> BrowserContext:
        """Create browser context with advanced stealth measures"""
        try:
            # Get proxy from rotation manager
            proxy = None
            proxy_dict = None
            
            if self.use_proxy and self.proxy_manager:
                try:
                    # Get proxy based on geographic targeting
                    if self.geographic_targeting and target_country:
                        proxy = await self.proxy_manager.get_proxy(
                            country=target_country,
                            strategy="geographic"
                        )
                        if proxy:
                            self.logger.info(f"Using geographic proxy: {proxy.url} ({proxy.country})")
                    
                    # Fallback to any available proxy
                    if not proxy:
                        proxy = await self.proxy_manager.get_proxy(strategy="failover")
                        if proxy:
                            self.logger.info(f"Using fallback proxy: {proxy.url}")
                    
                    if proxy:
                        proxy_dict = proxy.dict_format
                    else:
                        self.logger.warning("No proxies available, using direct connection")
                        
                except Exception as e:
                    self.logger.error(f"Failed to get proxy: {e}")
                    proxy_dict = None
            
            # Rotate user agent
            user_agent = self.user_agent_rotator.get_next_agent()
            self.stealth_config['user_agent'] = user_agent
            
            # Create context with stealth settings
            context = await browser.new_context(
                viewport=self.stealth_config['viewport'],
                user_agent=user_agent,
                locale=self.stealth_config['locale'],
                timezone_id=self.stealth_config['timezone_id'],
                proxy=proxy_dict,
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            # Apply playwright-stealth
            stealth_instance = Stealth()
            await stealth_instance.apply_stealth_async(context)
            
            # Apply additional advanced stealth measures
            await self._apply_advanced_stealth(context)
            
            # Load previous session if available
            self.session_manager.load_session(context)
            
            # Store proxy info for later use
            context._proxy_info = proxy
            
            self.logger.info("Advanced stealth context created with proxy rotation")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to create stealth context: {e}")
            raise
    
    async def _apply_advanced_stealth(self, context: BrowserContext):
        """Apply comprehensive stealth measures"""
        try:
            await context.add_init_script("""
                // Hide webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Fake plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Fake languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Fake Chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Hide automation indicators
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                
                // Fake hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });
                
                // Fake device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
            """)
            
            self.logger.info("Advanced stealth measures applied")
            
        except Exception as e:
            self.logger.warning(f"Failed to apply advanced stealth: {e}")
    

    
    async def _navigate_with_stealth(self, page: Page, url: str, max_retries: int = 3) -> bool:
        """Navigate to URL with comprehensive stealth measures and proxy retry logic"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Navigation attempt {attempt + 1}/{max_retries} to: {url}")
                
                # Add random delay before navigation
                await self.human_simulator.random_delay(1.0, 3.0)
                
                # Navigate with stealth
                start_time = time.time()
                response = await page.goto(
                    url,
                    wait_until='networkidle',
                    timeout=60000
                )
                response_time = time.time() - start_time
                
                # Check if we got blocked
                if response.status == 403 or response.status == 429:
                    self.logger.warning(f"Access blocked: HTTP {response.status}")
                    
                    # Mark proxy as failed if using one
                    if hasattr(page.context, '_proxy_info') and page.context._proxy_info:
                        await self.proxy_manager.mark_proxy_failed(
                            page.context._proxy_info, 
                            f"HTTP {response.status} blocked"
                        )
                    
                    # Try to get a new proxy for next attempt
                    if attempt < max_retries - 1:
                        await self._rotate_proxy_for_context(page.context)
                        continue
                    else:
                        return False
                
                # Apply human-like behavior
                await self.human_simulator.humanize_mouse_movement(page)
                await self.human_simulator.humanize_scrolling(page)
                
                # Check for CAPTCHA or blocking
                if await self._is_blocked(page):
                    self.logger.warning("Page appears to be blocked")
                    
                    # Mark proxy as failed if using one
                    if hasattr(page.context, '_proxy_info') and page.context._proxy_info:
                        await self.proxy_manager.mark_proxy_failed(
                            page.context._proxy_info, 
                            "Page blocked/CAPTCHA detected"
                        )
                    
                    # Try to get a new proxy for next attempt
                    if attempt < max_retries - 1:
                        await self._rotate_proxy_for_context(page.context)
                        continue
                    else:
                        return False
                
                # Mark proxy as successful if using one
                if hasattr(page.context, '_proxy_info') and page.context._proxy_info:
                    await self.proxy_manager.mark_proxy_success(
                        page.context._proxy_info, 
                        response_time
                    )
                
                # Save session state
                self.session_manager.save_session(page.context)
                
                self.logger.info(f"Navigation successful with stealth (attempt {attempt + 1})")
                return True
                
            except Exception as e:
                self.logger.error(f"Navigation attempt {attempt + 1} failed: {e}")
                
                # Mark proxy as failed if using one
                if hasattr(page.context, '_proxy_info') and page.context._proxy_info:
                    await self.proxy_manager.mark_proxy_failed(
                        page.context._proxy_info, 
                        str(e)
                    )
                
                # Try to get a new proxy for next attempt
                if attempt < max_retries - 1:
                    await self._rotate_proxy_for_context(page.context)
                    await asyncio.sleep(self.proxy_config.get('retry_delay', 5))
                    continue
                else:
                    return False
        
        return False
    
    def _get_target_country(self, location: str) -> str:
        """Determine target country for geographic proxy targeting"""
        if not self.geographic_targeting:
            return None
        
        location_lower = location.lower()
        
        # Map location to country code
        for country_code, location_names in GEOGRAPHIC_TARGETING['location_mapping'].items():
            for name in location_names:
                if name.lower() in location_lower:
                    self.logger.info(f"Targeting proxy from {country_code} for location: {location}")
                    return country_code
        
        # Default to US if no match found
        default_country = GEOGRAPHIC_TARGETING['default_location']
        self.logger.info(f"No specific country match, using default: {default_country}")
        return default_country
    
    async def _rotate_proxy_for_context(self, context: BrowserContext):
        """Rotate proxy for an existing context"""
        if not self.use_proxy or not self.proxy_manager:
            return
        
        try:
            # Get a new proxy
            new_proxy = await self.proxy_manager.get_proxy(strategy="failover")
            if new_proxy:
                # Update the context's proxy info
                context._proxy_info = new_proxy
                self.logger.info(f"Rotated to new proxy: {new_proxy.url}")
            else:
                self.logger.warning("No new proxies available for rotation")
                
        except Exception as e:
            self.logger.error(f"Failed to rotate proxy: {e}")
    
    async def _is_blocked(self, page: Page) -> bool:
        """Check if the page is blocked or shows CAPTCHA"""
        try:
            blocking_indicators = [
                '//h1[contains(text(), "Access Denied")]',
                '//h1[contains(text(), "Blocked")]',
                '//h1[contains(text(), "Forbidden")]',
                '//div[contains(text(), "CAPTCHA")]',
                '//div[contains(text(), "verify you are human")]',
                '//iframe[contains(@src, "captcha")]',
                '//div[contains(text(), "unusual traffic")]',
                '//div[contains(text(), "rate limit")]'
            ]
            
            for indicator in blocking_indicators:
                if await page.locator(indicator).count() > 0:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Blocking check failed: {e}")
            return False
    
    async def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """Search for jobs using advanced stealth techniques with proxy rotation"""
        jobs = []
        page_num = 0
        
        # Initialize proxy pools if using proxy rotation
        if self.use_proxy and self.proxy_manager:
            self.logger.info("Initializing proxy pools...")
            await self.proxy_manager.refresh_proxy_pools()
            
            # Perform initial health check
            await self.proxy_manager.health_check_all_proxies()
            
            # Log proxy statistics
            stats = self.proxy_manager.get_proxy_statistics()
            self.logger.info(f"Proxy pool status: {stats['active_proxies']}/{stats['total_proxies']} active")
        
        try:
            async with async_playwright() as playwright:
                # Create stealth browser
                browser = await self._create_stealth_browser()
                
                try:
                    # Determine target country for geographic targeting
                    target_country = self._get_target_country(location)
                    
                    # Create stealth context with geographic targeting
                    context = await self._create_stealth_context(browser, target_country)
                    
                    try:
                        # Create page
                        page = await context.new_page()
        
        while len(jobs) < limit:
            try:
                # Construct search URL
                search_url = f"{self.base_url}/jobs"
                params = {
                    'q': keyword,
                    'l': location,
                                    'start': page_num * 10
                                }
                                
                                if params['start'] > 0:
                                    search_url += f"?q={params['q']}&l={params['l']}&start={params['start']}"
                                else:
                                    search_url += f"?q={params['q']}&l={params['l']}"
                                
                                self.logger.info(f"Searching Indeed page {page_num + 1} for '{keyword}' in {location}")
                                
                                # Navigate with stealth and proxy retry logic
                                if not await self._navigate_with_stealth(page, search_url):
                                    self.logger.warning("Navigation failed after all retries")
                                    break
                                
                                # Wait for page to load completely
                                await page.wait_for_load_state('networkidle')
                                await self.human_simulator.random_delay(2.0, 5.0)
                                
                                # Extract job data
                                page_jobs = await self._extract_jobs_from_page(page, keyword)
                                
                                if not page_jobs:
                                    self.logger.warning("No jobs found on this page")
                    break
                
                                # Add jobs to results
                                for job in page_jobs:
                    if len(jobs) >= limit:
                        break
                                    jobs.append(job)
                                
                                self.logger.info(f"Found {len(page_jobs)} jobs on page {page_num + 1}")
                                
                                # Move to next page
                                page_num += 1
                                
                                # Add delay between pages
                                await self.human_simulator.random_delay(3.0, 8.0)
                                
                            except Exception as e:
                                self.logger.error(f"Error processing page {page_num}: {e}")
                                break
                        
                        self.logger.info(f"Scraped {len(jobs)} jobs for '{keyword}' using stealth techniques and proxy rotation")
                        
                    finally:
                        await page.close()
                        
                finally:
                    await context.close()
                    
        except Exception as e:
            self.logger.error(f"Stealth scraping failed: {e}")
        
        # Final proxy statistics
        if self.use_proxy and self.proxy_manager:
            final_stats = self.proxy_manager.get_proxy_statistics()
            self.logger.info(f"Final proxy statistics: {final_stats}")
        
        return jobs
    
    async def _extract_jobs_from_page(self, page: Page, keyword: str) -> List[Dict]:
        """Extract job information from the current page"""
        jobs = []
        
        try:
            # Wait for job cards to load
            await page.wait_for_selector('div.job_seen_beacon', timeout=10000)
            
            # Get all job cards
            job_cards = await page.locator('div.job_seen_beacon').all()
            
            self.logger.info(f"Found {len(job_cards)} job cards on page")
            
            for card in job_cards:
                try:
                    job_data = await self._extract_job_data_from_card(card, keyword)
                    if job_data:
                        jobs.append(job_data)
                
                    # Add small delay between extractions
                    await self.human_simulator.random_delay(0.1, 0.5)
                    
                except Exception as e:
                    self.logger.debug(f"Failed to extract job data: {e}")
                    continue
                
            except Exception as e:
            self.logger.error(f"Failed to extract jobs from page: {e}")
        
        return jobs
    
    async def _extract_job_data_from_card(self, card, keyword: str) -> Optional[Dict]:
        """Extract job information from a single job card"""
        try:
            # Job title
            title_elem = await card.locator('h2.jobTitle').first
            title = await title_elem.text_content() if title_elem else ""
            title = title.strip() if title else ""
            
            # Company name
            company_elem = await card.locator('span[data-testid="company-name"]').first
            company = await company_elem.text_content() if company_elem else ""
            company = company.strip() if company else ""
            
            # Location
            location_elem = await card.locator('div[data-testid="text-location"]').first
            location = await location_elem.text_content() if location_elem else ""
            location = location.strip() if location else ""
            
            # Job URL
            job_link = await card.locator('a.jcs-JobTitle').first
            job_url = ""
            if job_link:
                href = await job_link.get_attribute('href')
                if href:
                    job_url = self.base_url + href if href.startswith('/') else href
            
            # Job description snippet
            snippet_elem = await card.locator('div.job-snippet').first
            snippet = await snippet_elem.text_content() if snippet_elem else ""
            snippet = snippet.strip() if snippet else ""
            
            # Salary (if available)
            salary_elem = await card.locator('div.metadata.salary-snippet-container').first
            salary = await salary_elem.text_content() if salary_elem else ""
            salary = salary.strip() if salary else ""
            
            # Extract skills from snippet and title
            skills = self._extract_skills(snippet, title)
            
            # Create job data
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
                'scraped_at': datetime.now().isoformat(),
                'scraping_method': 'stealth_playwright'
            }
            
            return job_data if title and company else None
            
        except Exception as e:
            self.logger.debug(f"Failed to extract job data from card: {e}")
            return None
    
    def _extract_skills(self, text: str, title: str) -> List[str]:
        """Extract technical skills from job description text"""
        skills = []
        text_lower = text.lower()
        title_lower = title.lower()
        
        # Extract skills from TECH_SKILLS
        for category, skill_list in TECH_SKILLS.items():
            for skill in skill_list:
                if len(skill) > 2:
                    import re
                    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                    if re.search(pattern, text_lower) or re.search(pattern, title_lower):
                        skills.append(skill)
        
        # If no skills found, add some based on common patterns
        if not skills:
            if 'python' in title_lower:
                skills.append('Python')
            if 'developer' in title_lower:
                skills.append('Software Development')
            if 'engineer' in title_lower:
                skills.append('Engineering')
            if 'react' in title_lower:
                skills.append('React')
            if 'javascript' in title_lower:
                skills.append('JavaScript')
            if 'java' in title_lower:
                skills.append('Java')
            if 'data' in title_lower:
                skills.append('Data Analysis')
            if 'devops' in title_lower:
                skills.append('DevOps')
        
        return list(set(skills))
    
    async def close(self):
        """Clean up resources"""
        try:
            pass
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

# Backward compatibility - keep the old class name
class IndeedScraper(StealthIndeedScraper):
    """Backward compatibility wrapper"""
    def __init__(self, *args, **kwargs):
        # Extract proxy-related arguments for backward compatibility
        use_proxy = kwargs.pop('use_proxy', True)
        proxy_list = kwargs.pop('proxy_list', None)
        
        # Convert old proxy_list to new proxy_config if needed
        if proxy_list and not kwargs.get('proxy_config'):
            kwargs['proxy_config'] = {
                **DEFAULT_PROXY_CONFIG,
                'enabled': use_proxy
            }
        
        super().__init__(*args, **kwargs)
        self.logger.info("Using enhanced Indeed scraper with stealth capabilities and proxy rotation")
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """Synchronous wrapper for async search"""
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, super().search_jobs(keyword, location, limit))
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                return asyncio.run(super().search_jobs(keyword, location, limit))
        except Exception as e:
            self.logger.error(f"Synchronous search failed: {e}")
            return []
