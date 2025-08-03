import requests
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import TECH_SKILLS

class RedditScraper:
    """
    Scraper for Reddit job subreddits
    """
    
    def __init__(self):
        self.setup_logging()
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/reddit_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """Search jobs from Reddit subreddits"""
        all_jobs = []
        
        # List of most active job-related subreddits
        subreddits = [
            'remotejobs',      # Most active for remote jobs
            'forhire',         # Freelance and contract work
            'jobs',            # General job postings
            'cscareerquestions' # Tech career discussions
        ]
        
        for subreddit in subreddits:
            try:
                jobs = self._search_subreddit(subreddit, keyword, limit // len(subreddits))
                all_jobs.extend(jobs)
                self.logger.info(f"Found {len(jobs)} jobs from r/{subreddit}")
                time.sleep(random.uniform(1, 2))  # Be respectful to Reddit
            except Exception as e:
                self.logger.error(f"Error searching r/{subreddit}: {e}")
        
        return all_jobs[:limit]
    
    def _search_subreddit(self, subreddit: str, keyword: str, limit: int) -> List[Dict]:
        """Search a specific subreddit for job posts"""
        jobs = []
        try:
            # Use Reddit's JSON API
            url = f"{self.base_url}/r/{subreddit}/search.json"
            params = {
                'q': keyword,
                'restrict_sr': 'on',
                'sort': 'new',
                't': 'month',
                'limit': min(limit, 25)  # Reddit API limit
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                for post in posts:
                    post_data = post.get('data', {})
                    
                    # Check if it's a job post
                    if self._is_job_post(post_data, keyword):
                        job_data = {
                            'title': post_data.get('title', ''),
                            'company': self._extract_company(post_data.get('title', '')),
                            'location': self._extract_location(post_data.get('title', '')),
                            'salary': self._extract_salary(post_data.get('selftext', '')),
                            'snippet': post_data.get('selftext', '')[:200] + '...',
                            'job_url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'skills': self._extract_skills(post_data.get('selftext', ''), post_data.get('title', '')),
                            'search_keyword': keyword,
                            'source': f'reddit_{subreddit}',
                            'scraped_at': datetime.now().isoformat()
                        }
                        jobs.append(job_data)
                        
                        if len(jobs) >= limit:
                            break
        except Exception as e:
            self.logger.error(f"Error searching subreddit {subreddit}: {e}")
        
        return jobs
    
    def _is_job_post(self, post_data: Dict, keyword: str) -> bool:
        """Check if a Reddit post is a job posting"""
        title = post_data.get('title', '').lower()
        text = post_data.get('selftext', '').lower()
        
        # Job-related keywords
        job_keywords = [
            'hiring', 'looking for', 'seeking', 'wanted', 'position', 'role',
            'developer', 'engineer', 'programmer', 'coder', 'full-time', 'part-time',
            'remote', 'freelance', 'contract', 'salary', 'compensation'
        ]
        
        # Check if title contains job keywords
        for job_keyword in job_keywords:
            if job_keyword in title:
                return True
        
        # Check if text contains job keywords
        for job_keyword in job_keywords:
            if job_keyword in text:
                return True
        
        # Check if it matches the search keyword
        if keyword.lower() in title or keyword.lower() in text:
            return True
        
        return False
    
    def _extract_company(self, title: str) -> str:
        """Extract company name from Reddit post title"""
        # Common patterns in Reddit job posts
        patterns = [
            r'\[([^\]]+)\]',  # [Company Name]
            r'\(([^)]+)\)',   # (Company Name)
            r'at\s+([A-Z][a-zA-Z\s&]+)',  # at Company Name
            r'for\s+([A-Z][a-zA-Z\s&]+)',  # for Company Name
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1).strip()
        
        return "Reddit Company"
    
    def _extract_location(self, title: str) -> str:
        """Extract location from Reddit post title"""
        # Common location patterns
        patterns = [
            r'\[([^\]]+)\]',  # [Location]
            r'\(([^)]+)\)',   # (Location)
            r'in\s+([A-Z][a-zA-Z\s,]+)',  # in Location
            r'at\s+([A-Z][a-zA-Z\s,]+)',  # at Location
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                location = match.group(1).strip()
                if any(word in location.lower() for word in ['remote', 'anywhere', 'worldwide']):
                    return "Remote"
                return location
        
        return "Remote"  # Default for Reddit jobs
    
    def _extract_salary(self, text: str) -> str:
        """Extract salary information from Reddit post text"""
        # Salary patterns
        patterns = [
            r'\$(\d{2,3})k?\s*-\s*\$(\d{2,3})k?',  # $80k - $120k
            r'\$(\d{2,3})k?',  # $100k
            r'(\d{2,3})k?\s*-\s*(\d{2,3})k?',  # 80k - 120k
            r'(\d{2,3})k?',  # 100k
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    return f"${match.group(1)}k - ${match.group(2)}k"
                else:
                    return f"${match.group(1)}k"
        
        return ""
    
    def _extract_skills(self, text: str, title: str) -> List[str]:
        """Extract skills from Reddit post text and title"""
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