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

class FastJobScraper:
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
    
    def _random_delay(self, min_delay=0.5, max_delay=1.5):
        """Add minimal random delay to avoid rate limiting"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
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
    
    def scrape_linkedin_fast(self, max_pages=1) -> List[Dict]:
        """Fast LinkedIn scraping with minimal search terms"""
        jobs = []
        
        # Only the most important search terms for speed
        search_terms = [
            'salesforce developer',
            'salesforce admin',
            'revops engineer',
            'python automation',
            'api integration'
        ]
        
        for search_term in search_terms:
            try:
                self.logger.info(f"Fast scraping LinkedIn for: {search_term}")
                self._rotate_user_agent()
                
                # LinkedIn jobs search parameters
                params = {
                    'keywords': search_term,
                    'location': 'United States',
                    'f_TPR': 'r86400',  # Last 24 hours
                    'start': 0,
                    'position': 1,
                    'pageNum': 1
                }
                
                response = self.session.get("https://www.linkedin.com/jobs/search", params=params, timeout=10)
                
                if response.status_code == 403:
                    self.logger.warning(f"LinkedIn returned 403 for '{search_term}', skipping...")
                    continue
                
                if response.status_code != 200:
                    self.logger.warning(f"LinkedIn returned {response.status_code} for '{search_term}'")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='base-card')
                
                for card in job_cards[:25]:  # Get more jobs per page
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
                            
                            # Get description from snippet
                            description_elem = card.find('div', class_='base-search-card__snippet')
                            description = description_elem.get_text(strip=True) if description_elem else ""
                            
                            # Extract skills from snippet
                            skills = self._extract_skills_from_text(description)
                            
                            # Add search term as skill if it's a technology
                            if any(tech in search_term.lower() for tech in ['salesforce', 'python', 'api', 'automation']):
                                skills.append(search_term.split()[0].title())
                            
                            job = {
                                'title': title,
                                'company': company,
                                'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                                'salary': None,
                                'tags': skills,
                                'source': 'LinkedIn',
                                'source_url': job_url,
                                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                                'job_id': f"linkedin_{hash(title + company + search_term)}",
                                'description': description,
                                'search_term': search_term
                            }
                            jobs.append(job)
                            
                    except Exception as e:
                        self.logger.warning(f"Error parsing LinkedIn job: {e}")
                        continue
                
                # Minimal delay
                self._random_delay(0.5, 1.0)
                
            except Exception as e:
                self.logger.error(f"Error scraping LinkedIn for '{search_term}': {e}")
                continue
        
        return jobs
    
    def scrape_remote_ok_fast(self) -> List[Dict]:
        """Fast Remote OK scraping"""
        jobs = []
        base_url = "https://remoteok.com"
        
        try:
            self.logger.info("Fast scraping Remote OK")
            self._rotate_user_agent()
            
            response = self.session.get(f"{base_url}/remote-dev-jobs", timeout=10)
            
            if response.status_code == 403:
                self.logger.warning("Remote OK returned 403, skipping...")
                return jobs
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('tr', class_='job')
            
            for card in job_cards[:30]:  # Get more jobs
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
            
        except Exception as e:
            self.logger.error(f"Error scraping Remote OK: {e}")
        
        return jobs
    
    def scrape_all_sources_fast(self) -> List[Dict]:
        """Fast scraping from all sources"""
        all_jobs = []
        
        self.logger.info("Starting FAST job scraping...")
        
        # Only use the fastest sources
        sources = [
            ('LinkedIn Fast', self.scrape_linkedin_fast),
            ('Remote OK Fast', self.scrape_remote_ok_fast),
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
    
    def save_jobs_to_file(self, jobs: List[Dict], filename: str = 'fast_scraped_jobs.json'):
        """Save scraped jobs to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving jobs to file: {e}")

if __name__ == "__main__":
    scraper = FastJobScraper()
    jobs = scraper.scrape_all_sources_fast()
    scraper.save_jobs_to_file(jobs)
    print(f"✅ Fast scraped {len(jobs)} jobs successfully!")
    
    # Test skills analytics
    if jobs:
        analytics = scraper.get_skills_analytics(jobs)
        print(f"📊 Skills Analytics:")
        print(f"Total skills found: {analytics['total_skills']}")
        print(f"Unique skills: {analytics['unique_skills']}")
        print(f"Top 10 skills: {analytics['top_skills'][:10]}") 