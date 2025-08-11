import asyncio
import aiohttp
import time
import random
import json
import logging
import hashlib
import pickle
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
import re
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
from urllib.parse import urljoin, urlparse

class AdvancedJobScraper:
    def __init__(self, cache_dir: str = "cache", max_cache_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_cache_age = timedelta(hours=max_cache_age_hours)
        self.logger = self._setup_logger()
        
        # Initialize cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Proxy configuration
        self.proxies = self._load_proxies()
        self.current_proxy_index = 0
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        # Selenium driver for headless browsing
        self.driver = None
        self.driver_lock = threading.Lock()
        
        # Rate limiting
        self.request_timestamps = {}
        self.min_delay = 1.0
        self.max_delay = 3.0
        
    def _setup_logger(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def _load_proxies(self) -> List[str]:
        """Load proxy list from file or use default free proxies"""
        proxy_file = "proxies.txt"
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        
        # Return some free proxy examples (you should replace with your own)
        return [
            # Add your proxy list here
            # "http://proxy1:port",
            # "http://proxy2:port",
        ]
    
    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy from rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key for URL and parameters"""
        cache_string = url
        if params:
            cache_string += json.dumps(params, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache is still valid"""
        if not os.path.exists(cache_path):
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
        return file_age < self.max_cache_age
    
    def _load_from_cache(self, cache_path: str) -> Optional[Dict]:
        """Load data from cache"""
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")
            return None
    
    def _save_to_cache(self, cache_path: str, data: Dict):
        """Save data to cache"""
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")
    
    def _init_selenium_driver(self):
        """Initialize Selenium WebDriver with headless configuration"""
        if self.driver is not None:
            return
        
        with self.driver_lock:
            if self.driver is not None:
                return
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=" + random.choice(self.user_agents))
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                self.logger.error(f"Failed to initialize Selenium driver: {e}")
                self.driver = None
    
    def _cleanup_selenium_driver(self):
        """Clean up Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    async def _rate_limited_request(self, session: aiohttp.ClientSession, url: str, 
                                  headers: Dict = None, proxy: str = None) -> Optional[str]:
        """Make rate-limited HTTP request"""
        # Rate limiting
        domain = urlparse(url).netloc
        if domain in self.request_timestamps:
            time_since_last = time.time() - self.request_timestamps[domain]
            if time_since_last < self.min_delay:
                await asyncio.sleep(self.min_delay - time_since_last)
        
        self.request_timestamps[domain] = time.time()
        
        # Prepare headers
        if headers is None:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        
        # Prepare proxy
        proxy_url = None
        if proxy:
            proxy_url = proxy
        
        try:
            async with session.get(url, headers=headers, proxy=proxy_url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
    
    async def _scrape_with_selenium(self, url: str, wait_for: str = None, timeout: int = 10) -> Optional[str]:
        """Scrape using Selenium for JavaScript-heavy sites"""
        self._init_selenium_driver()
        
        if not self.driver:
            return None
        
        try:
            with self.driver_lock:
                self.driver.get(url)
                
                if wait_for:
                    WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                    )
                
                # Random delay to simulate human behavior
                await asyncio.sleep(random.uniform(2, 5))
                
                return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Selenium scraping failed for {url}: {e}")
            return None
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text"""
        if not text:
            return []
        
        # Enhanced skills patterns
        skills_patterns = [
            # Programming Languages
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin|PHP|Ruby|Scala|R|MATLAB|Perl|Haskell|Clojure|Elixir|Erlang)\b',
            # Frameworks & Libraries
            r'\b(React|Angular|Vue\.js|Node\.js|Django|Flask|Spring|Express\.js|Laravel|Ruby on Rails|ASP\.NET|jQuery|Bootstrap|Tailwind CSS|Svelte|Next\.js|Nuxt\.js|Gatsby|Ember\.js|Backbone\.js)\b',
            # Databases
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB|Elasticsearch|Neo4j|InfluxDB|CouchDB|RethinkDB)\b',
            # Cloud & DevOps
            r'\b(AWS|Azure|Google Cloud|Docker|Kubernetes|Terraform|Jenkins|GitLab|GitHub Actions|Ansible|Chef|Puppet|Vagrant|Packer|Consul|Vault|Nomad)\b',
            # Tools & Platforms
            r'\b(Git|SVN|Jira|Confluence|Slack|Trello|Asana|Figma|Sketch|Adobe XD|Zeplin|InVision|Marvel|Principle|Framer|Protopie)\b',
            # AI & ML
            r'\b(TensorFlow|PyTorch|Scikit-learn|Keras|OpenAI|Hugging Face|Pandas|NumPy|Matplotlib|Seaborn|Plotly|Bokeh|Jupyter|Colab|Kaggle|FastAI|XGBoost|LightGBM|CatBoost)\b',
            # Mobile
            r'\b(React Native|Flutter|Xamarin|Ionic|Cordova|PhoneGap|Swift|Kotlin|Android|iOS|Xcode|Android Studio|Appium|Detox|Firebase)\b',
            # Web Technologies
            r'\b(HTML5|CSS3|SASS|LESS|Webpack|Babel|ESLint|Prettier|GraphQL|REST API|SOAP|WebSocket|WebRTC|Service Workers|PWA|AMP|WebAssembly|WebGL)\b',
            # Testing
            r'\b(Jest|Mocha|Jasmine|Cypress|Selenium|JUnit|TestNG|PyTest|NUnit|XUnit|Cucumber|Behave|Robot Framework|Playwright|Puppeteer|Protractor)\b',
            # Salesforce & CRM
            r'\b(Salesforce|Apex|Lightning|Visualforce|SOQL|SOSL|Salesforce DX|Lightning Web Components|LWC|Aura|Process Builder|Flow|Workflow|Validation Rules|Triggers|Custom Objects|Profiles|Permission Sets|Sharing Rules|Data Loader|Workbench|Developer Console|Setup|Administration|Integration|API|REST|SOAP|Bulk API|Streaming API|Platform Events|Custom Metadata|Custom Settings|External Objects|Big Objects|Platform Cache|Heroku|Einstein|Analytics|Reports|Dashboards|Charts|Wave Analytics|Einstein Analytics|Tableau CRM|Data Cloud|CDP|MuleSoft|Composer|Anypoint|API Gateway|Runtime Fabric|CloudHub|Hybrid|On-Premise|Cloud|Multi-Cloud|Hybrid Cloud|Private Cloud|Public Cloud|SaaS|PaaS|IaaS|Microservices|Event-Driven|Event Streaming|Kafka|RabbitMQ|ActiveMQ|Message Queues|Event Sourcing|CQRS|Domain-Driven Design|DDD|Clean Architecture|Hexagonal Architecture|Onion Architecture|SOLID Principles|Design Patterns|Gang of Four|GoF|Creational Patterns|Structural Patterns|Behavioral Patterns|Singleton|Factory|Builder|Prototype|Abstract Factory|Adapter|Bridge|Composite|Decorator|Facade|Flyweight|Proxy|Chain of Responsibility|Command|Interpreter|Iterator|Mediator|Memento|Observer|State|Strategy|Template Method|Visitor)\b',
            # Other Skills
            r'\b(Agile|Scrum|Kanban|Waterfall|TDD|BDD|CI/CD|Microservices|API|REST|GraphQL|OAuth|JWT|OAuth2|OpenID Connect|SAML|LDAP|Active Directory|SSO|MFA|2FA|Biometric|Fingerprint|Face Recognition|Iris Recognition|Voice Recognition|Speech Recognition|NLP|Natural Language Processing|Computer Vision|Image Recognition|Object Detection|Face Detection|Text Recognition|OCR|Optical Character Recognition|Document Processing|Form Processing|Invoice Processing|Receipt Processing|Contract Analysis|Legal Document Analysis|Medical Document Analysis|Financial Document Analysis|Insurance Document Analysis|Real Estate Document Analysis|Government Document Analysis|Academic Document Analysis|Research Document Analysis|Patent Analysis|Trademark Analysis|Copyright Analysis|Intellectual Property Analysis|IP Analysis|Patent Search|Trademark Search|Copyright Search|IP Search|Patent Filing|Trademark Filing|Copyright Filing|IP Filing|Patent Prosecution|Trademark Prosecution|Copyright Prosecution|IP Prosecution|Patent Litigation|Trademark Litigation|Copyright Litigation|IP Litigation|Patent Portfolio|Trademark Portfolio|Copyright Portfolio|IP Portfolio|Patent Strategy|Trademark Strategy|Copyright Strategy|IP Strategy|Patent Management|Trademark Management|Copyright Management|IP Management|Patent Analytics|Trademark Analytics|Copyright Analytics|IP Analytics|Patent Valuation|Trademark Valuation|Copyright Valuation|IP Valuation|Patent Licensing|Trademark Licensing|Copyright Licensing|IP Licensing|Patent Assignment|Trademark Assignment|Copyright Assignment|IP Assignment|Patent Transfer|Trademark Transfer|Copyright Transfer|IP Transfer|Patent Sale|Trademark Sale|Copyright Sale|IP Sale|Patent Purchase|Trademark Purchase|Copyright Purchase|IP Purchase|Patent Acquisition|Trademark Acquisition|Copyright Acquisition|IP Acquisition|Patent Merger|Trademark Merger|Copyright Merger|IP Merger|Patent Consolidation|Trademark Consolidation|Copyright Consolidation|IP Consolidation|Patent Divestiture|Trademark Divestiture|Copyright Divestiture|IP Divestiture|Patent Spin-off|Trademark Spin-off|Copyright Spin-off|IP Spin-off|Patent Joint Venture|Trademark Joint Venture|Copyright Joint Venture|IP Joint Venture|Patent Partnership|Trademark Partnership|Copyright Partnership|IP Partnership|Patent Collaboration|Trademark Collaboration|Copyright Collaboration|IP Collaboration|Patent Alliance|Trademark Alliance|Copyright Alliance|IP Alliance|Patent Consortium|Trademark Consortium|Copyright Consortium|IP Consortium|Patent Pool|Trademark Pool|Copyright Pool|IP Pool|Patent Clearinghouse|Trademark Clearinghouse|Copyright Clearinghouse|IP Clearinghouse|Patent Exchange|Trademark Exchange|Copyright Exchange|IP Exchange|Patent Marketplace|Trademark Marketplace|Copyright Marketplace|IP Marketplace|Patent Auction|Trademark Auction|Copyright Auction|IP Auction|Patent Broker|Trademark Broker|Copyright Broker|IP Broker|Patent Agent|Trademark Agent|Copyright Agent|IP Agent|Patent Attorney|Trademark Attorney|Copyright Attorney|IP Attorney|Patent Lawyer|Trademark Lawyer|Copyright Lawyer|IP Lawyer|Patent Consultant|Trademark Consultant|Copyright Consultant|IP Consultant|Patent Advisor|Trademark Advisor|Copyright Advisor|IP Advisor|Patent Expert|Trademark Expert|Copyright Expert|IP Expert|Patent Specialist|Trademark Specialist|Copyright Specialist|IP Specialist|Patent Professional|Trademark Professional|Copyright Professional|IP Professional|Patent Practitioner|Trademark Practitioner|Copyright Practitioner|IP Practitioner|Patent Representative|Trademark Representative|Copyright Representative|IP Representative|Patent Officer|Trademark Officer|Copyright Officer|IP Officer|Patent Administrator|Trademark Administrator|Copyright Administrator|IP Administrator|Patent Manager|Trademark Manager|Copyright Manager|IP Manager|Patent Director|Trademark Director|Copyright Director|IP Director|Patent VP|Trademark VP|Copyright VP|IP VP|Patent CTO|Trademark CTO|Copyright CTO|IP CTO|Patent CEO|Trademark CEO|Copyright CEO|IP CEO|Patent Founder|Trademark Founder|Copyright Founder|IP Founder|Patent Co-founder|Trademark Co-founder|Copyright Co-founder|IP Co-founder|Patent Partner|Trademark Partner|Copyright Partner|IP Partner|Patent Principal|Trademark Principal|Copyright Principal|IP Principal|Patent Senior|Trademark Senior|Copyright Senior|IP Senior|Patent Lead|Trademark Lead|Copyright Lead|IP Lead|Patent Head|Trademark Head|Copyright Head|IP Head|Patent Chief|Trademark Chief|Copyright Chief|IP Chief|Patent Executive|Trademark Executive|Copyright Executive|IP Executive|Patent Officer|Trademark Officer|Copyright Officer|IP Officer|Patent Administrator|Trademark Administrator|Copyright Administrator|IP Administrator|Patent Manager|Trademark Manager|Copyright Manager|IP Manager|Patent Director|Trademark Director|Copyright Director|IP Director|Patent VP|Trademark VP|Copyright VP|IP VP|Patent CTO|Trademark CTO|Copyright CTO|IP CTO|Patent CEO|Trademark CEO|Copyright CEO|IP CEO|Patent Founder|Trademark Founder|Copyright Founder|IP Founder|Patent Co-founder|Trademark Co-founder|Copyright Co-founder|IP Co-founder|Patent Partner|Trademark Partner|Copyright Partner|IP Partner|Patent Principal|Trademark Principal|Copyright Principal|IP Principal|Patent Senior|Trademark Senior|Copyright Senior|IP Senior|Patent Lead|Trademark Lead|Copyright Lead|IP Lead|Patent Head|Trademark Head|Copyright Head|IP Head|Patent Chief|Trademark Chief|Copyright Chief|IP Chief|Patent Executive|Trademark Executive|Copyright Executive|IP Executive)\b'
        ]
        
        skills = set()
        text_lower = text.lower()
        
        for pattern in skills_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        return list(skills)
    
    async def scrape_linkedin_advanced(self, max_pages: int = 3) -> List[Dict]:
        """Advanced LinkedIn scraping with Selenium and caching"""
        jobs = []
        search_terms = [
            'salesforce developer',
            'salesforce admin',
            'revops engineer',
            'python automation',
            'api integration',
            'data engineer',
            'machine learning engineer',
            'full stack developer',
            'devops engineer',
            'cloud architect'
        ]
        
        async with aiohttp.ClientSession() as session:
            for term in search_terms:
                for page in range(1, max_pages + 1):
                    cache_key = self._get_cache_key(f"linkedin_{term}_{page}")
                    cache_path = self._get_cache_path(cache_key)
                    
                    # Check cache first
                    if self._is_cache_valid(cache_path):
                        cached_data = self._load_from_cache(cache_path)
                        if cached_data:
                            jobs.extend(cached_data)
                            self.logger.info(f"Loaded {len(cached_data)} jobs from cache for {term} page {page}")
                            continue
                    
                    # Scrape with Selenium
                    url = f"https://www.linkedin.com/jobs/search/?keywords={term}&location=United%20States&start={(page-1)*25}"
                    
                    try:
                        html_content = await self._scrape_with_selenium(url, wait_for=".job-search-card")
                        
                        if html_content:
                            page_jobs = self._parse_linkedin_jobs(html_content, term)
                            jobs.extend(page_jobs)
                            
                            # Cache the results
                            self._save_to_cache(cache_path, page_jobs)
                            
                            self.logger.info(f"Scraped {len(page_jobs)} jobs from LinkedIn for {term} page {page}")
                            
                            # Random delay between pages
                            await asyncio.sleep(random.uniform(3, 7))
                        else:
                            self.logger.warning(f"Failed to scrape LinkedIn page {page} for {term}")
                    
                    except Exception as e:
                        self.logger.error(f"Error scraping LinkedIn {term} page {page}: {e}")
        
        return jobs
    
    def _parse_linkedin_jobs(self, html_content: str, search_term: str) -> List[Dict]:
        """Parse LinkedIn job listings from HTML"""
        jobs = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        job_cards = soup.find_all('div', class_='job-search-card')
        
        for card in job_cards:
            try:
                # Extract job title
                title_elem = card.find('h3', class_='base-search-card__title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Extract company
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                company = company_elem.get_text(strip=True) if company_elem else ''
                
                # Extract location
                location_elem = card.find('span', class_='job-search-card__location')
                location = location_elem.get_text(strip=True) if location_elem else ''
                
                # Extract job URL
                job_link = card.find('a', class_='base-card__full-link')
                job_url = job_link.get('href') if job_link else ''
                
                # Extract posted date
                date_elem = card.find('time')
                posted_date = date_elem.get('datetime') if date_elem else ''
                
                if title and company:
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'source': 'LinkedIn',
                        'source_url': job_url,
                        'posted_date': posted_date,
                        'search_term': search_term,
                        'description': '',
                        'salary': '',
                        'tags': self._extract_skills_from_text(title + ' ' + company)
                    }
                    jobs.append(job)
            
            except Exception as e:
                self.logger.warning(f"Error parsing LinkedIn job card: {e}")
                continue
        
        return jobs
    
    async def scrape_remote_ok_advanced(self) -> List[Dict]:
        """Advanced Remote OK scraping with caching"""
        cache_key = self._get_cache_key("remote_ok")
        cache_path = self._get_cache_path(cache_key)
        
        # Check cache first
        if self._is_cache_valid(cache_path):
            cached_data = self._load_from_cache(cache_path)
            if cached_data:
                self.logger.info(f"Loaded {len(cached_data)} jobs from Remote OK cache")
                return cached_data
        
        jobs = []
        url = "https://remoteok.com/remote-salesforce-jobs"
        
        async with aiohttp.ClientSession() as session:
            try:
                html_content = await self._rate_limited_request(session, url)
                
                if html_content:
                    jobs = self._parse_remote_ok_jobs(html_content)
                    
                    # Cache the results
                    self._save_to_cache(cache_path, jobs)
                    
                    self.logger.info(f"Scraped {len(jobs)} jobs from Remote OK")
                else:
                    self.logger.warning("Failed to scrape Remote OK")
            
            except Exception as e:
                self.logger.error(f"Error scraping Remote OK: {e}")
        
        return jobs
    
    def _parse_remote_ok_jobs(self, html_content: str) -> List[Dict]:
        """Parse Remote OK job listings"""
        jobs = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        job_rows = soup.find_all('tr', class_='job')
        
        for row in job_rows:
            try:
                # Extract job title
                title_elem = row.find('h2', attrs={'itemprop': 'title'})
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Extract company
                company_elem = row.find('h3', attrs={'itemprop': 'hiringOrganization'})
                company = company_elem.get_text(strip=True) if company_elem else ''
                
                # Extract location
                location_elem = row.find('td', class_='location')
                location = location_elem.get_text(strip=True) if location_elem else ''
                
                # Extract salary
                salary_elem = row.find('td', class_='salary')
                salary = salary_elem.get_text(strip=True) if salary_elem else ''
                
                # Extract job URL
                job_link = row.find('a', class_='preventLink')
                job_url = job_link.get('href') if job_link else ''
                if job_url and not job_url.startswith('http'):
                    job_url = f"https://remoteok.com{job_url}"
                
                # Extract posted date
                date_elem = row.find('td', class_='date')
                posted_date = date_elem.get_text(strip=True) if date_elem else ''
                
                if title and company:
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'source': 'Remote OK',
                        'source_url': job_url,
                        'posted_date': posted_date,
                        'salary': salary,
                        'description': '',
                        'tags': self._extract_skills_from_text(title + ' ' + company + ' ' + salary)
                    }
                    jobs.append(job)
            
            except Exception as e:
                self.logger.warning(f"Error parsing Remote OK job: {e}")
                continue
        
        return jobs
    
    async def scrape_all_sources_advanced(self) -> List[Dict]:
        """Scrape all sources asynchronously with advanced features"""
        self.logger.info("Starting advanced multi-source scraping...")
        
        # Create tasks for all sources
        tasks = [
            self.scrape_linkedin_advanced(max_pages=2),
            self.scrape_remote_ok_advanced(),
            # Add more sources here as needed
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_jobs = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Scraping task failed: {result}")
            else:
                all_jobs.extend(result)
        
        # Remove duplicates based on title and company
        unique_jobs = self._remove_duplicates(all_jobs)
        
        self.logger.info(f"Advanced scraping completed. Found {len(unique_jobs)} unique jobs.")
        
        # Cleanup Selenium driver
        self._cleanup_selenium_driver()
        
        return unique_jobs
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a unique identifier
            identifier = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def get_skills_analytics(self, jobs: List[Dict]) -> Dict:
        """Get skills analytics from scraped jobs"""
        all_skills = []
        source_skills = {}
        
        for job in jobs:
            skills = job.get('tags', [])
            source = job.get('source', 'Unknown')
            
            all_skills.extend(skills)
            
            if source not in source_skills:
                source_skills[source] = []
            source_skills[source].extend(skills)
        
        # Count skills
        skill_counts = Counter(all_skills)
        
        # Get top skills by source
        top_skills_by_source = {}
        for source, skills in source_skills.items():
            source_skill_counts = Counter(skills)
            top_skills_by_source[source] = dict(source_skill_counts.most_common(10))
        
        return {
            'total_jobs': len(jobs),
            'total_skills': len(skill_counts),
            'top_skills': dict(skill_counts.most_common(20)),
            'skills_by_source': top_skills_by_source,
            'sources': list(source_skills.keys())
        }
    
    def save_jobs_to_file(self, jobs: List[Dict], filename: str = 'advanced_scraped_jobs.json'):
        """Save scraped jobs to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False, default=str)
            self.logger.info(f"Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save jobs to file: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self._cleanup_selenium_driver() 