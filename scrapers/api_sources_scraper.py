import requests
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import TECH_SKILLS

class APISourcesScraper:
    """
    Scraper that uses various job APIs to avoid 403 errors
    """
    
    def __init__(self):
        self.setup_logging()
        # API keys (you would need to get these from the respective services)
        self.adzuna_app_id = None  # Get from https://developer.adzuna.com/
        self.adzuna_app_key = None
        self.jsearch_api_key = None  # Get from https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/
        self.remotive_api_key = None  # Get from https://remotive.com/api
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/api_sources_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """Search jobs from multiple API sources"""
        all_jobs = []
        
        # Try Remotive API (free, no key required) - Most reliable
        try:
            remotive_jobs = self._search_remotive_api(keyword, limit // 2)
            all_jobs.extend(remotive_jobs)
            self.logger.info(f"Found {len(remotive_jobs)} jobs from Remotive API")
        except Exception as e:
            self.logger.error(f"Error with Remotive API: {e}")
        
        # Try GitHub Jobs API (free, no key required) - Very reliable
        try:
            github_jobs = self._search_github_jobs(keyword, limit // 2)
            all_jobs.extend(github_jobs)
            self.logger.info(f"Found {len(github_jobs)} jobs from GitHub Jobs API")
        except Exception as e:
            self.logger.error(f"Error with GitHub Jobs API: {e}")
        
        # Try Adzuna API (if keys are available)
        if self.adzuna_app_id and self.adzuna_app_key:
            try:
                adzuna_jobs = self._search_adzuna_api(keyword, location, limit // 3)
                all_jobs.extend(adzuna_jobs)
                self.logger.info(f"Found {len(adzuna_jobs)} jobs from Adzuna API")
            except Exception as e:
                self.logger.error(f"Error with Adzuna API: {e}")
        
        # Try JSearch API (if key is available)
        if self.jsearch_api_key:
            try:
                jsearch_jobs = self._search_jsearch_api(keyword, location, limit // 3)
                all_jobs.extend(jsearch_jobs)
                self.logger.info(f"Found {len(jsearch_jobs)} jobs from JSearch API")
            except Exception as e:
                self.logger.error(f"Error with JSearch API: {e}")
        
        return all_jobs[:limit]
    
    def _search_remotive_api(self, keyword: str, limit: int) -> List[Dict]:
        """Search Remotive API (free, no authentication required)"""
        jobs = []
        try:
            url = "https://remotive.com/api/remote-jobs"
            params = {
                'search': keyword,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for job in data.get('jobs', [])[:limit]:
                    job_data = {
                        'title': job.get('title', ''),
                        'company': job.get('company_name', ''),
                        'location': 'Remote',
                        'salary': job.get('salary', ''),
                        'snippet': job.get('description', '')[:200] + '...',
                        'job_url': job.get('url', ''),
                        'skills': self._extract_skills(job.get('description', ''), job.get('title', '')),
                        'search_keyword': keyword,
                        'source': 'remotive_api',
                        'scraped_at': datetime.now().isoformat()
                    }
                    jobs.append(job_data)
        except Exception as e:
            self.logger.error(f"Error with Remotive API: {e}")
        
        return jobs
    
    def _search_adzuna_api(self, keyword: str, location: str, limit: int) -> List[Dict]:
        """Search Adzuna API (requires API key)"""
        jobs = []
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                'app_id': self.adzuna_app_id,
                'app_key': self.adzuna_app_key,
                'results_per_page': limit,
                'what': keyword,
                'where': location
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for job in data.get('results', [])[:limit]:
                    job_data = {
                        'title': job.get('title', ''),
                        'company': job.get('company', {}).get('display_name', ''),
                        'location': job.get('location', {}).get('display_name', ''),
                        'salary': job.get('salary_min', '') + ' - ' + job.get('salary_max', '') if job.get('salary_min') else '',
                        'snippet': job.get('description', '')[:200] + '...',
                        'job_url': job.get('redirect_url', ''),
                        'skills': self._extract_skills(job.get('description', ''), job.get('title', '')),
                        'search_keyword': keyword,
                        'source': 'adzuna_api',
                        'scraped_at': datetime.now().isoformat()
                    }
                    jobs.append(job_data)
        except Exception as e:
            self.logger.error(f"Error with Adzuna API: {e}")
        
        return jobs
    
    def _search_jsearch_api(self, keyword: str, location: str, limit: int) -> List[Dict]:
        """Search JSearch API (requires RapidAPI key)"""
        jobs = []
        try:
            url = "https://jsearch.p.rapidapi.com/search"
            headers = {
                'X-RapidAPI-Key': self.jsearch_api_key,
                'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
            }
            params = {
                'query': keyword,
                'page': '1',
                'num_pages': '1',
                'country': 'us'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for job in data.get('data', [])[:limit]:
                    job_data = {
                        'title': job.get('job_title', ''),
                        'company': job.get('employer_name', ''),
                        'location': job.get('job_city', '') + ', ' + job.get('job_country', ''),
                        'salary': job.get('job_salary', ''),
                        'snippet': job.get('job_description', '')[:200] + '...',
                        'job_url': job.get('job_apply_link', ''),
                        'skills': self._extract_skills(job.get('job_description', ''), job.get('job_title', '')),
                        'search_keyword': keyword,
                        'source': 'jsearch_api',
                        'scraped_at': datetime.now().isoformat()
                    }
                    jobs.append(job_data)
        except Exception as e:
            self.logger.error(f"Error with JSearch API: {e}")
        
        return jobs
    
    def _search_github_jobs(self, keyword: str, limit: int) -> List[Dict]:
        """Search GitHub Jobs API (free, no authentication required)"""
        jobs = []
        try:
            url = "https://jobs.github.com/positions.json"
            params = {
                'description': keyword,
                'location': 'United States',
                'full_time': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
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