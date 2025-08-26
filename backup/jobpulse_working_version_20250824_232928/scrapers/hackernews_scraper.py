import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re
from config.settings import TECH_SKILLS

class HackerNewsScraper:
    """Scraper for Hacker News 'Who\'s Hiring' threads"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.base_url = "https://news.ycombinator.com"
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/hackernews_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(self, keyword: str, location: str = "Remote", limit: int = 25) -> List[Dict]:
        """Search for jobs in Hacker News 'Who\'s Hiring' threads"""
        try:
            self.logger.info(f"Searching Hacker News for '{keyword}'")
            
            # Find the latest "Who's Hiring" thread
            who_is_hiring_url = self._find_who_is_hiring_thread()
            if not who_is_hiring_url:
                self.logger.warning("Could not find 'Who\'s Hiring' thread")
                return []
            
            # Scrape the thread for job postings
            jobs = self._scrape_who_is_hiring_thread(who_is_hiring_url, keyword, limit)
            
            self.logger.info(f"Found {len(jobs)} jobs from Hacker News")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error searching Hacker News: {e}")
            return []
    
    def _find_who_is_hiring_thread(self) -> Optional[str]:
        """Find the latest 'Who\'s Hiring' thread"""
        try:
            # Search for "Who's Hiring" threads
            search_url = f"{self.base_url}/from?site=news.ycombinator.com"
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for "Who's Hiring" links
            who_is_hiring_links = soup.find_all('a', string=re.compile(r'Who.*Hiring', re.I))
            
            if who_is_hiring_links:
                # Get the most recent one
                latest_thread = who_is_hiring_links[0]
                thread_url = latest_thread.get('href')
                if thread_url:
                    if thread_url.startswith('/'):
                        return self.base_url + thread_url
                    return thread_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding 'Who\'s Hiring\' thread: {e}")
            return None
    
    def _scrape_who_is_hiring_thread(self, thread_url: str, keyword: str, limit: int) -> List[Dict]:
        """Scrape job postings from a 'Who\'s Hiring' thread"""
        jobs = []
        try:
            response = self.session.get(thread_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for comment threads (job postings)
            comment_threads = soup.find_all('tr', {'class': 'athing'})
            
            for thread in comment_threads[:limit]:
                try:
                    # Extract comment text
                    comment_elem = thread.find_next_sibling('tr')
                    if comment_elem:
                        comment_text = comment_elem.get_text()
                        
                        # Check if comment contains job-related keywords
                        if self._is_job_posting(comment_text, keyword):
                            job = self._extract_job_from_comment(comment_text, keyword)
                            if job:
                                jobs.append(job)
                                
                except Exception as e:
                    self.logger.debug(f"Error extracting job from comment: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping thread: {e}")
        
        return jobs[:limit]
    
    def _is_job_posting(self, comment_text: str, keyword: str) -> bool:
        """Check if a comment is a job posting"""
        job_indicators = [
            'hiring', 'looking for', 'seeking', 'position', 'role',
            'developer', 'engineer', 'programmer', 'designer', 'manager',
            'full-time', 'part-time', 'contract', 'remote', 'onsite'
        ]
        
        comment_lower = comment_text.lower()
        keyword_lower = keyword.lower()
        
        # Check if it contains job indicators or the search keyword
        return any(indicator in comment_lower for indicator in job_indicators) or keyword_lower in comment_lower
    
    def _extract_job_from_comment(self, comment_text: str, keyword: str) -> Optional[Dict]:
        """Extract job information from a comment"""
        try:
            # Try to extract company name (usually at the beginning)
            lines = comment_text.split('\n')
            company = "Company Not Specified"
            
            # Look for company name in first few lines
            for line in lines[:3]:
                line = line.strip()
                if line and len(line) < 100 and not line.startswith('http'):
                    company = line
                    break
            
            # Extract title (try to find it in the comment)
            title = f"{keyword.title()} Position"
            title_patterns = [
                r'(?i)(senior|junior|lead|principal)?\s*(software engineer|developer|programmer|designer|manager)',
                r'(?i)(python|javascript|react|node|full.?stack|frontend|backend|devops|data)\s*(engineer|developer|scientist)'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, comment_text)
                if match:
                    title = match.group(0).title()
                    break
            
            # Extract location
            location = "Remote"
            location_patterns = [
                r'(?i)(remote|onsite|hybrid)',
                r'(?i)(san francisco|new york|london|berlin|amsterdam)',
                r'(?i)(united states|uk|germany|netherlands)'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, comment_text)
                if match:
                    location = match.group(0)
                    break
            
            # Extract skills
            skills = self._extract_skills(comment_text, title)
            
            return {
                'title': title,
                'company': company,
                'snippet': comment_text[:200] + '...' if len(comment_text) > 200 else comment_text,
                'salary': 'Competitive',  # HN usually doesn't show salary
                'job_url': self.base_url,  # Link to HN thread
                'skills': skills,
                'search_keyword': keyword,
                'source': 'hackernews',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.debug(f"Error extracting job from comment: {e}")
            return None
    
    def _extract_skills(self, comment_text: str, title: str) -> List[str]:
        """Extract skills from comment text and title"""
        skills = []
        
        # Combine title and comment for skill extraction
        text = f"{title} {comment_text}".lower()
        
        # Check for common tech skills
        for skill in TECH_SKILLS:
            if skill.lower() in text:
                skills.append(skill)
        
        return skills[:5]  # Limit to 5 skills
