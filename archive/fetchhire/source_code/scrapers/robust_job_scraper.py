import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging
from typing import List, Dict, Optional
import re
from collections import Counter

class RobustJobScraper:
    def __init__(self):
        self.session = requests.Session()
        # Enhanced user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        self.session.headers.update({
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
        })
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def _random_delay(self, min_delay=3, max_delay=8):
        """Add random delay to avoid rate limiting"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
    def _extract_skills_from_job_title(self, title: str) -> List[str]:
        """Extract skills from job title"""
        if not title:
            return []
        
        title_lower = title.lower()
        skills = []
        
        # Map job titles to likely skills
        title_skill_mapping = {
            'frontend': ['JavaScript', 'HTML5', 'CSS3', 'React', 'Angular', 'Vue.js'],
            'front-end': ['JavaScript', 'HTML5', 'CSS3', 'React', 'Angular', 'Vue.js'],
            'front end': ['JavaScript', 'HTML5', 'CSS3', 'React', 'Angular', 'Vue.js'],
            'backend': ['Python', 'Java', 'Node.js', 'PostgreSQL', 'MySQL', 'MongoDB'],
            'back-end': ['Python', 'Java', 'Node.js', 'PostgreSQL', 'MySQL', 'MongoDB'],
            'back end': ['Python', 'Java', 'Node.js', 'PostgreSQL', 'MySQL', 'MongoDB'],
            'full stack': ['JavaScript', 'Python', 'React', 'Node.js', 'PostgreSQL', 'MongoDB'],
            'fullstack': ['JavaScript', 'Python', 'React', 'Node.js', 'PostgreSQL', 'MongoDB'],
            'full-stack': ['JavaScript', 'Python', 'React', 'Node.js', 'PostgreSQL', 'MongoDB'],
            'machine learning': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy'],
            'ml': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy'],
            'ai': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy'],
            'artificial intelligence': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy'],
            'data': ['Python', 'SQL', 'Pandas', 'NumPy', 'PostgreSQL', 'MongoDB'],
            'devops': ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform', 'Git'],
            'mobile': ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Android', 'iOS'],
            'android': ['Java', 'Kotlin', 'Android', 'XML'],
            'ios': ['Swift', 'iOS', 'Xcode', 'Objective-C'],
            'python': ['Python', 'Django', 'Flask', 'Pandas', 'NumPy'],
            'java': ['Java', 'Spring', 'Maven', 'JUnit'],
            'javascript': ['JavaScript', 'Node.js', 'React', 'Express.js'],
            'react': ['React', 'JavaScript', 'HTML5', 'CSS3'],
            'angular': ['Angular', 'TypeScript', 'JavaScript', 'HTML5', 'CSS3'],
            'node': ['Node.js', 'JavaScript', 'Express.js', 'MongoDB'],
            'cloud': ['AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes'],
            'aws': ['AWS', 'Docker', 'Kubernetes', 'Terraform'],
            'azure': ['Azure', 'Docker', 'Kubernetes', 'Terraform'],
            'database': ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis'],
            'api': ['REST API', 'GraphQL', 'JavaScript', 'Python', 'Node.js'],
            'senior': ['Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 'AWS'],
            'junior': ['JavaScript', 'Python', 'React', 'HTML5', 'CSS3', 'Git'],
            'lead': ['Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 'AWS', 'Docker'],
            'architect': ['Python', 'Java', 'AWS', 'Docker', 'Kubernetes', 'Microservices'],
            'engineer': ['Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 'Git'],
            'developer': ['JavaScript', 'Python', 'React', 'Node.js', 'HTML5', 'CSS3']
        }
        
        # Check for matches in job title
        for keyword, skill_list in title_skill_mapping.items():
            if keyword in title_lower:
                skills.extend(skill_list)
        
        # Remove duplicates and return
        return list(set(skills))
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text"""
        if not text:
            return []
        
        # Common tech skills and frameworks
        skills_patterns = [
            # Programming Languages
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin|PHP|Ruby|Scala|R|MATLAB)\b',
            # Frameworks & Libraries
            r'\b(React|Angular|Vue\.js|Node\.js|Django|Flask|Spring|Express\.js|Laravel|Ruby on Rails|ASP\.NET|jQuery|Bootstrap|Tailwind CSS)\b',
            # Databases
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB|Elasticsearch)\b',
            # Cloud & DevOps
            r'\b(AWS|Azure|Google Cloud|Docker|Kubernetes|Terraform|Jenkins|GitLab|GitHub Actions|Ansible|Chef|Puppet)\b',
            # Tools & Platforms
            r'\b(Git|SVN|Jira|Confluence|Slack|Trello|Asana|Figma|Sketch|Adobe XD|Zeplin)\b',
            # AI & ML
            r'\b(TensorFlow|PyTorch|Scikit-learn|Keras|OpenAI|Hugging Face|Pandas|NumPy|Matplotlib|Seaborn)\b',
            # Mobile
            r'\b(React Native|Flutter|Xamarin|Ionic|Cordova|PhoneGap|Swift|Kotlin|Android|iOS)\b',
            # Web Technologies
            r'\b(HTML5|CSS3|SASS|LESS|Webpack|Babel|ESLint|Prettier|GraphQL|REST API|SOAP|WebSocket)\b',
            # Testing
            r'\b(Jest|Mocha|Jasmine|Cypress|Selenium|JUnit|TestNG|PyTest|NUnit|XUnit)\b',
            # Enterprise & CRM
            r'\b(Salesforce|Apex|Lightning|Visualforce|SOQL|SOSL|Salesforce DX|Lightning Web Components|LWC|Aura|Process Builder|Flow|Workflow|Validation Rules|Triggers|Custom Objects|Profiles|Permission Sets|Sharing Rules|Data Loader|Workbench|Developer Console|Setup|Administration|Integration|API|REST|SOAP|Bulk API|Streaming API|Platform Events|Custom Metadata|Custom Settings|External Objects|Big Objects|Platform Cache|Heroku|Einstein|Analytics|Reports|Dashboards|Charts|Wave Analytics|Einstein Analytics|Tableau CRM|Data Cloud|CDP|MuleSoft|Composer|Anypoint|API Gateway|Runtime Fabric|CloudHub|Hybrid|On-Premise|Cloud|Multi-Cloud|Hybrid Cloud|Private Cloud|Public Cloud|SaaS|PaaS|IaaS|Microservices|Event-Driven|Event Streaming|Kafka|RabbitMQ|ActiveMQ|Message Queues|Event Sourcing|CQRS|Domain-Driven Design|DDD|Clean Architecture|Hexagonal Architecture|Onion Architecture|SOLID Principles|Design Patterns|Gang of Four|GoF|Creational Patterns|Structural Patterns|Behavioral Patterns|Singleton|Factory|Builder|Prototype|Abstract Factory|Adapter|Bridge|Composite|Decorator|Facade|Flyweight|Proxy|Chain of Responsibility|Command|Interpreter|Iterator|Mediator|Memento|Observer|State|Strategy|Template Method|Visitor)\b',
            # Other Skills
            r'\b(Agile|Scrum|Kanban|Waterfall|TDD|BDD|CI/CD|Microservices|API|REST|GraphQL|OAuth|JWT)\b'
        ]
        
        skills = set()
        text_lower = text.lower()
        
        for pattern in skills_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        return list(skills)
    
    def scrape_linkedin_jobs(self, max_pages=2) -> List[Dict]:
        """Scrape LinkedIn Jobs with optimized search terms for speed"""
        jobs = []
        
        # Optimized search terms - focus on the most important ones
        search_terms = [
            # Core RevOps/CRM roles (most important)
            'salesforce developer',
            'salesforce admin',
            'revops engineer',
            'crm developer',
            'business systems analyst',
            'integration engineer',
            'python automation engineer',
            'api integration engineer',
            
            # Technology keywords (broader reach)
            'salesforce',
            'python automation',
            'api integrations',
            'workflow automation',
            'zapier',
            'crm automation'
        ]
        
        for search_term in search_terms:
            try:
                self.logger.info(f"Scraping LinkedIn for: {search_term}")
                
                for page in range(1, max_pages + 1):
                    self.logger.info(f"Scraping LinkedIn Jobs page {page} for '{search_term}'")
                    self._rotate_user_agent()
                    
                    # LinkedIn jobs search parameters
                    params = {
                        'keywords': search_term,
                        'location': 'United States',
                        'f_TPR': 'r86400',  # Last 24 hours
                        'start': (page - 1) * 25,
                        'position': 1,
                        'pageNum': page
                    }
                    
                    response = self.session.get("https://www.linkedin.com/jobs/search", params=params, timeout=15)
                    
                    if response.status_code == 403:
                        self.logger.warning(f"LinkedIn returned 403 on page {page} for '{search_term}', skipping...")
                        continue
                    
                    if response.status_code != 200:
                        self.logger.warning(f"LinkedIn returned {response.status_code} on page {page} for '{search_term}'")
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find job cards
                    job_cards = soup.find_all('div', class_='base-card')
                    
                    for card in job_cards[:20]:  # Get more jobs per page
                        try:
                            # Extract job data
                            title_elem = card.find('h3', class_='base-search-card__title')
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            location_elem = card.find('span', class_='job-search-card__location')
                            
                            if title_elem and company_elem:
                                # Get job link
                                job_link = card.find('a', class_='base-card__full-link')
                                job_url = job_link['href'] if job_link else None
                                
                                title = title_elem.get_text(strip=True)
                                company = company_elem.get_text(strip=True)
                                
                                # Get description from snippet (faster than fetching individual pages)
                                description_elem = card.find('div', class_='base-search-card__snippet')
                                description = description_elem.get_text(strip=True) if description_elem else ""
                                
                                # Extract skills from snippet and job title
                                skills_from_text = self._extract_skills_from_text(description)
                                skills_from_title = self._extract_skills_from_job_title(title)
                                
                                # Add search term as a skill if it's a technology
                                tech_keywords = ['salesforce', 'python', 'javascript', 'react', 'node.js', 'zapier', 'tray', 'snowflake', 'dbt', 'cpq', 'crm', 'revops', 'api', 'sql', 'automation']
                                if any(keyword in search_term.lower() for keyword in tech_keywords):
                                    # Extract the main technology from the search term
                                    for keyword in tech_keywords:
                                        if keyword in search_term.lower():
                                            skills_from_title.append(keyword.title())
                                            break
                                
                                # Combine skills and remove duplicates
                                all_skills = list(set(skills_from_text + skills_from_title))
                                
                                # Only fetch full description for first job of each search term to avoid rate limiting
                                if page == 1 and len([j for j in jobs if j.get('search_term') == search_term]) == 0:
                                    try:
                                        self.logger.info(f"Fetching full description for: {title}")
                                        job_response = self.session.get(job_url, timeout=10)
                                        
                                        if job_response.status_code == 200:
                                            job_soup = BeautifulSoup(job_response.content, 'html.parser')
                                            
                                            # Try multiple selectors for job description
                                            description_selectors = [
                                                'div[class*="show-more-less-html"]',
                                                'div[class*="description__text"]',
                                                'div[class*="job-description"]',
                                                'div[class*="job-view-layout"]',
                                                'div[class*="job-details-jobs-unified-top-card__job-description"]',
                                                'section[class*="description"]',
                                                'div[class*="jobs-description"]'
                                            ]
                                            
                                            for selector in description_selectors:
                                                job_description = job_soup.select_one(selector)
                                                if job_description:
                                                    full_description = job_description.get_text(strip=True)
                                                    # Extract additional skills from full description
                                                    additional_skills = self._extract_skills_from_text(full_description)
                                                    all_skills.extend(additional_skills)
                                                    all_skills = list(set(all_skills))  # Remove duplicates
                                                    break
                                            
                                    except Exception as e:
                                        self.logger.warning(f"Error fetching job description: {e}")
                                
                                # Log skills found for debugging
                                if all_skills:
                                    self.logger.info(f"Skills found for '{title}': {all_skills}")
                                
                                job = {
                                    'title': title,
                                    'company': company,
                                    'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                                    'salary': None,  # LinkedIn doesn't show salary in search
                                    'tags': all_skills,
                                    'source': 'LinkedIn',
                                    'source_url': job_url,
                                    'posted_date': datetime.now().strftime('%Y-%m-%d'),
                                    'job_id': f"linkedin_{hash(title + company + search_term)}",
                                    'description': description,  # Store description for search
                                    'search_term': search_term  # Track which search term found this job
                                }
                                jobs.append(job)
                                
                        except Exception as e:
                            self.logger.warning(f"Error parsing LinkedIn job: {e}")
                            continue
                    
                    # Shorter delay between pages
                    self._random_delay(1, 2)  # Reduced delay
                    
            except Exception as e:
                self.logger.error(f"Error scraping LinkedIn for '{search_term}': {e}")
                continue
        
        return jobs
    
    def scrape_glassdoor_jobs(self, max_pages=3) -> List[Dict]:
        """Scrape Glassdoor Jobs"""
        jobs = []
        base_url = "https://www.glassdoor.com/Job"
        
        try:
            for page in range(1, max_pages + 1):
                self.logger.info(f"Scraping Glassdoor Jobs page {page}")
                self._rotate_user_agent()
                
                params = {
                    'sc.keyword': 'software developer',
                    'locT': 'N',
                    'locId': '1',
                    'jobType': '',
                    'fromAge': '1',
                    'minSalary': '0',
                    'includeNoSalaryJobs': 'true',
                    'radius': '100',
                    'cityId': '-1',
                    'minRating': '0.0',
                    'industryId': '-1',
                    'sgocId': '-1',
                    'seniorityType': 'all',
                    'companyId': '-1',
                    'employerSizes': '0',
                    'applicationType': '0',
                    'remoteWorkType': '0'
                }
                
                if page > 1:
                    params['p.'] = page
                
                response = self.session.get(base_url, params=params, timeout=20)
                
                if response.status_code == 403:
                    self.logger.warning(f"Glassdoor returned 403 on page {page}, skipping...")
                    continue
                
                if response.status_code != 200:
                    self.logger.warning(f"Glassdoor returned {response.status_code} on page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='react-job-listing')
                
                for card in job_cards[:10]:  # Limit to 10 jobs per page
                    try:
                        # Extract job data
                        title_elem = card.find('a', class_='jobLink')
                        company_elem = card.find('a', class_='employer-name')
                        location_elem = card.find('span', class_='location')
                        
                        if title_elem and company_elem:
                            job_url = "https://www.glassdoor.com" + title_elem['href'] if title_elem.get('href') else None
                            
                            # Extract skills from job description
                            description_elem = card.find('div', class_='job-description')
                            description = description_elem.get_text(strip=True) if description_elem else ""
                            skills = self._extract_skills_from_text(description)
                            
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                                'salary': None,
                                'tags': skills,
                                'source': 'Glassdoor',
                                'source_url': job_url,
                                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                                'job_id': f"glassdoor_{hash(title_elem.get_text(strip=True) + company_elem.get_text(strip=True))}"
                            }
                            jobs.append(job)
                            
                    except Exception as e:
                        self.logger.warning(f"Error parsing Glassdoor job: {e}")
                        continue
                
                self._random_delay()
                
        except Exception as e:
            self.logger.error(f"Error scraping Glassdoor: {e}")
        
        return jobs
    
    def scrape_ziprecruiter_jobs(self, max_pages=3) -> List[Dict]:
        """Scrape ZipRecruiter Jobs"""
        jobs = []
        base_url = "https://www.ziprecruiter.com/candidate/search"
        
        try:
            for page in range(1, max_pages + 1):
                self.logger.info(f"Scraping ZipRecruiter Jobs page {page}")
                self._rotate_user_agent()
                
                params = {
                    'search': 'software developer',
                    'location': 'United States',
                    'radius': '25',
                    'page': page
                }
                
                response = self.session.get(base_url, params=params, timeout=20)
                
                if response.status_code == 403:
                    self.logger.warning(f"ZipRecruiter returned 403 on page {page}, skipping...")
                    continue
                
                if response.status_code != 200:
                    self.logger.warning(f"ZipRecruiter returned {response.status_code} on page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_result')
                
                for card in job_cards[:10]:  # Limit to 10 jobs per page
                    try:
                        # Extract job data
                        title_elem = card.find('h2', class_='job_title')
                        company_elem = card.find('span', class_='company_name')
                        location_elem = card.find('span', class_='location')
                        
                        if title_elem and company_elem:
                            job_link = card.find('a', class_='job_link')
                            job_url = job_link['href'] if job_link else None
                            
                            # Extract skills from job description
                            description_elem = card.find('div', class_='job_description')
                            description = description_elem.get_text(strip=True) if description_elem else ""
                            skills = self._extract_skills_from_text(description)
                            
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                                'salary': None,
                                'tags': skills,
                                'source': 'ZipRecruiter',
                                'source_url': job_url,
                                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                                'job_id': f"ziprecruiter_{hash(title_elem.get_text(strip=True) + company_elem.get_text(strip=True))}"
                            }
                            jobs.append(job)
                            
                    except Exception as e:
                        self.logger.warning(f"Error parsing ZipRecruiter job: {e}")
                        continue
                
                self._random_delay()
                
        except Exception as e:
            self.logger.error(f"Error scraping ZipRecruiter: {e}")
        
        return jobs
    
    def scrape_indeed_jobs(self, max_pages=3) -> List[Dict]:
        """Scrape Indeed Jobs with enhanced anti-detection"""
        jobs = []
        base_url = "https://www.indeed.com/jobs"
        
        try:
            for page in range(1, max_pages + 1):
                self.logger.info(f"Scraping Indeed Jobs page {page}")
                self._rotate_user_agent()
                
                # Indeed jobs search parameters
                params = {
                    'q': 'software developer',
                    'l': 'United States',
                    'fromage': '1',  # Last 24 hours
                    'start': (page - 1) * 10
                }
                
                response = self.session.get(base_url, params=params, timeout=20)
                
                if response.status_code == 403:
                    self.logger.warning(f"Indeed returned 403 on page {page}, skipping...")
                    continue
                
                if response.status_code != 200:
                    self.logger.warning(f"Indeed returned {response.status_code} on page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards[:8]:  # Limit to 8 jobs per page
                    try:
                        # Extract job data
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', class_='companyName')
                        location_elem = card.find('div', class_='companyLocation')
                        salary_elem = card.find('div', class_='salary-snippet')
                        
                        if title_elem and company_elem:
                            # Get job link
                            job_link = card.find('a', class_='jcs-JobTitle')
                            job_url = "https://www.indeed.com" + job_link['href'] if job_link else None
                            
                            # Extract skills from job description if available
                            description_elem = card.find('div', class_='job-snippet')
                            description = description_elem.get_text(strip=True) if description_elem else ""
                            skills = self._extract_skills_from_text(description)
                            
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                                'salary': salary_elem.get_text(strip=True) if salary_elem else None,
                                'tags': skills,
                                'source': 'Indeed',
                                'source_url': job_url,
                                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                                'job_id': f"indeed_{hash(title_elem.get_text(strip=True) + company_elem.get_text(strip=True))}"
                            }
                            jobs.append(job)
                            
                    except Exception as e:
                        self.logger.warning(f"Error parsing Indeed job: {e}")
                        continue
                
                self._random_delay()
                
        except Exception as e:
            self.logger.error(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def scrape_stack_overflow_jobs(self, max_pages=3) -> List[Dict]:
        """Scrape Stack Overflow Jobs with enhanced anti-detection"""
        jobs = []
        base_url = "https://stackoverflow.com/jobs"
        
        try:
            for page in range(1, max_pages + 1):
                self.logger.info(f"Scraping Stack Overflow Jobs page {page}")
                self._rotate_user_agent()
                
                # Stack Overflow jobs search parameters
                params = {
                    'q': 'software developer',
                    'l': 'United States',
                    'd': '1',  # Last 24 hours
                    'pg': page
                }
                
                response = self.session.get(base_url, params=params, timeout=20)
                
                if response.status_code == 403:
                    self.logger.warning(f"Stack Overflow returned 403 on page {page}, skipping...")
                    continue
                
                if response.status_code != 200:
                    self.logger.warning(f"Stack Overflow returned {response.status_code} on page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='-job')
                
                for card in job_cards[:8]:  # Limit to 8 jobs per page
                    try:
                        # Extract job data
                        title_elem = card.find('h2', class_='mb4')
                        company_elem = card.find('h3', class_='mb4')
                        location_elem = card.find('span', class_='fc-black-500')
                        
                        if title_elem and company_elem:
                            # Get job link
                            job_link = card.find('a', class_='s-link')
                            job_url = "https://stackoverflow.com" + job_link['href'] if job_link else None
                            
                            # Extract skills from job description if available
                            description_elem = card.find('div', class_='ps-relative')
                            description = description_elem.get_text(strip=True) if description_elem else ""
                            skills = self._extract_skills_from_text(description)
                            
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                                'salary': None,  # Stack Overflow doesn't show salary in search
                                'tags': skills,
                                'source': 'Stack Overflow',
                                'source_url': job_url,
                                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                                'job_id': f"stackoverflow_{hash(title_elem.get_text(strip=True) + company_elem.get_text(strip=True))}"
                            }
                            jobs.append(job)
                            
                    except Exception as e:
                        self.logger.warning(f"Error parsing Stack Overflow job: {e}")
                        continue
                
                self._random_delay()
                
        except Exception as e:
            self.logger.error(f"Error scraping Stack Overflow: {e}")
        
        return jobs
    
    def scrape_remote_ok(self, max_pages=2) -> List[Dict]:
        """Scrape Remote OK - very scrape-friendly"""
        jobs = []
        base_url = "https://remoteok.com"
        
        try:
            for page in range(1, max_pages + 1):
                self.logger.info(f"Scraping Remote OK page {page}")
                self._rotate_user_agent()
                
                url = f"{base_url}/remote-dev-jobs" if page == 1 else f"{base_url}/remote-dev-jobs?page={page}"
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 403:
                    self.logger.warning(f"Remote OK returned 403 on page {page}, skipping...")
                    continue
                
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('tr', class_='job')
                
                for card in job_cards:
                    try:
                        # Extract job data
                        title_elem = card.find('h2', {'itemprop': 'title'})
                        company_elem = card.find('h3', {'itemprop': 'hiringOrganization'})
                        location_elem = card.find('td', class_='location')
                        salary_elem = card.find('td', class_='salary')
                        tags_elem = card.find('td', class_='tags')
                        
                        if title_elem and company_elem:
                            job_url = base_url + card.find('a')['href'] if card.find('a') else None
                            
                            # Extract skills from tags
                            skills = [tag.get_text(strip=True) for tag in tags_elem.find_all('span')] if tags_elem else []
                            
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                                'salary': salary_elem.get_text(strip=True) if salary_elem else None,
                                'tags': skills,
                                'source': 'Remote OK',
                                'source_url': job_url,
                                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                                'job_id': f"remoteok_{hash(title_elem.get_text(strip=True) + company_elem.get_text(strip=True))}"
                            }
                            jobs.append(job)
                            
                    except Exception as e:
                        self.logger.warning(f"Error parsing Remote OK job: {e}")
                        continue
                
                self._random_delay()
                
        except Exception as e:
            self.logger.error(f"Error scraping Remote OK: {e}")
        
        return jobs
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape all sources and return combined results"""
        all_jobs = []
        
        self.logger.info("Starting job scraping from all sources...")
        
        # All sources including LinkedIn, Indeed, Stack Overflow, Glassdoor, ZipRecruiter
        sources = [
            ('LinkedIn', self.scrape_linkedin_jobs),
            ('Glassdoor', self.scrape_glassdoor_jobs),
            ('ZipRecruiter', self.scrape_ziprecruiter_jobs),
            ('Indeed', self.scrape_indeed_jobs),
            ('Stack Overflow', self.scrape_stack_overflow_jobs),
            ('Remote OK', self.scrape_remote_ok),
        ]
        
        for source_name, scraper_func in sources:
            try:
                self.logger.info(f"Scraping {source_name}...")
                jobs = scraper_func()
                all_jobs.extend(jobs)
                self.logger.info(f"Found {len(jobs)} jobs from {source_name}")
            except Exception as e:
                self.logger.error(f"Error scraping {source_name}: {e}")
        
        # Remove duplicates based on job_id
        unique_jobs = {job['job_id']: job for job in all_jobs}.values()
        
        self.logger.info(f"Total unique jobs found: {len(unique_jobs)}")
        return list(unique_jobs)
    
    def get_skills_analytics(self, jobs: List[Dict]) -> Dict:
        """Analyze skills from all jobs"""
        all_skills = []
        
        for job in jobs:
            if job.get('tags'):
                all_skills.extend(job['tags'])
        
        # Count skills
        skill_counts = Counter(all_skills)
        
        # Get top skills
        top_skills = skill_counts.most_common(20)
        
        # Categorize skills
        categories = {
            'Programming Languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Kotlin', 'PHP', 'Ruby', 'Scala', 'R', 'MATLAB'],
            'Frameworks & Libraries': ['React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring', 'Express.js', 'Laravel', 'Ruby on Rails', 'ASP.NET', 'jQuery', 'Bootstrap', 'Tailwind CSS'],
            'Databases': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server', 'Cassandra', 'DynamoDB', 'Elasticsearch'],
            'Cloud & DevOps': ['AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'GitLab', 'GitHub Actions', 'Ansible', 'Chef', 'Puppet'],
            'AI & ML': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Keras', 'OpenAI', 'Hugging Face', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn'],
            'Mobile': ['React Native', 'Flutter', 'Xamarin', 'Ionic', 'Cordova', 'PhoneGap', 'Swift', 'Kotlin', 'Android', 'iOS'],
            'Testing': ['Jest', 'Mocha', 'Jasmine', 'Cypress', 'Selenium', 'JUnit', 'TestNG', 'PyTest', 'NUnit', 'XUnit']
        }
        
        categorized_skills = {}
        for category, skills in categories.items():
            category_skills = [(skill, count) for skill, count in top_skills if skill in skills]
            if category_skills:
                categorized_skills[category] = category_skills
        
        return {
            'total_skills': len(all_skills),
            'unique_skills': len(skill_counts),
            'top_skills': top_skills,
            'categorized_skills': categorized_skills,
            'skill_distribution': dict(skill_counts)
        }
    
    def save_jobs_to_file(self, jobs: List[Dict], filename: str = 'scraped_jobs.json'):
        """Save scraped jobs to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving jobs to file: {e}")

if __name__ == "__main__":
    scraper = RobustJobScraper()
    jobs = scraper.scrape_all_sources()
    scraper.save_jobs_to_file(jobs)
    print(f"✅ Scraped {len(jobs)} jobs successfully!")
    
    # Test skills analytics
    if jobs:
        analytics = scraper.get_skills_analytics(jobs)
        print(f"📊 Skills Analytics:")
        print(f"Total skills found: {analytics['total_skills']}")
        print(f"Unique skills: {analytics['unique_skills']}")
        print(f"Top 10 skills: {analytics['top_skills'][:10]}") 