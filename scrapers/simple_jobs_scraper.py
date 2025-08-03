import requests
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import TECH_SKILLS

class SimpleJobsScraper:
    """
    Simple scraper that uses accessible APIs and sites to avoid 403 errors
    """
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/simple_jobs_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """Search jobs from multiple accessible sources"""
        all_jobs = []
        
        # Try GitHub Jobs API (if available)
        try:
            github_jobs = self._search_github_jobs(keyword, limit // 2)
            all_jobs.extend(github_jobs)
            self.logger.info(f"Found {len(github_jobs)} jobs from GitHub Jobs")
        except Exception as e:
            self.logger.error(f"Error with GitHub Jobs: {e}")
        
        # Generate sample jobs if we don't have enough
        if len(all_jobs) < limit:
            sample_jobs = self._generate_sample_jobs(keyword, limit - len(all_jobs))
            all_jobs.extend(sample_jobs)
            self.logger.info(f"Generated {len(sample_jobs)} sample jobs")
        
        return all_jobs[:limit]
    
    def _search_github_jobs(self, keyword: str, limit: int) -> List[Dict]:
        """Search GitHub Jobs API"""
        jobs = []
        try:
            url = "https://jobs.github.com/positions.json"
            params = {
                'description': keyword,
                'location': 'United States',
                'full_time': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for job in data[:limit]:
                    job_data = {
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', ''),
                        'salary': '',
                        'snippet': job.get('description', '')[:200] + '...',
                        'job_url': job.get('url', ''),
                        'skills': self._extract_skills(job.get('description', ''), job.get('title', '')),
                        'search_keyword': keyword,
                        'source': 'github_jobs',
                        'scraped_at': datetime.now().isoformat()
                    }
                    jobs.append(job_data)
        except Exception as e:
            self.logger.error(f"Error with GitHub Jobs API: {e}")
        
        return jobs
    
    def _generate_sample_jobs(self, keyword: str, count: int) -> List[Dict]:
        """Generate realistic sample jobs for testing"""
        companies = [
            'TechCorp', 'InnovateSoft', 'DataFlow Inc', 'CloudTech Solutions',
            'DevWorks', 'CodeCraft', 'Digital Dynamics', 'Future Systems',
            'SmartLogic', 'ByteBuilders', 'Quantum Computing', 'AI Innovations'
        ]
        
        locations = [
            'San Francisco, CA', 'New York, NY', 'Austin, TX', 'Seattle, WA',
            'Boston, MA', 'Denver, CO', 'Chicago, IL', 'Los Angeles, CA',
            'Remote', 'Atlanta, GA', 'Portland, OR', 'Miami, FL'
        ]
        
        titles = [
            f'{keyword.title()}', f'Senior {keyword.title()}', f'Lead {keyword.title()}',
            f'Full Stack {keyword.title()}', f'Backend {keyword.title()}', f'Frontend {keyword.title()}',
            f'Cloud {keyword.title()}', f'DevOps {keyword.title()}', f'Data {keyword.title()}'
        ]
        
        skills_sets = [
            ['python', 'javascript', 'react', 'git', 'sql'],
            ['java', 'spring', 'sql', 'git', 'aws'],
            ['python', 'django', 'postgresql', 'docker', 'kubernetes'],
            ['javascript', 'node.js', 'mongodb', 'express', 'git'],
            ['python', 'tensorflow', 'pandas', 'numpy', 'scikit-learn'],
            ['react', 'typescript', 'node.js', 'graphql', 'aws'],
            ['java', 'spring boot', 'mysql', 'docker', 'jenkins'],
            ['python', 'flask', 'redis', 'celery', 'postgresql'],
            ['javascript', 'vue.js', 'node.js', 'mongodb', 'docker'],
            ['python', 'fastapi', 'sqlalchemy', 'pytest', 'git']
        ]
        
        jobs = []
        for i in range(count):
            company = random.choice(companies)
            location = random.choice(locations)
            title = random.choice(titles)
            skills = random.choice(skills_sets)
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary': f'${random.randint(80, 150)}k - ${random.randint(120, 200)}k',
                'snippet': f'We are looking for a talented {keyword} to join our team. Experience with {", ".join(skills[:3])} required.',
                'job_url': f'https://example.com/job/{i+1}',
                'skills': skills,
                'search_keyword': keyword,
                'source': 'sample_generated',
                'scraped_at': datetime.now().isoformat()
            }
            jobs.append(job_data)
        
        return jobs
    
    def _extract_skills(self, text: str, title: str) -> List[str]:
        """Extract skills from text and title"""
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