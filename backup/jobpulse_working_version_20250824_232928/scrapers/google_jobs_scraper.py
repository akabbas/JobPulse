import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
import logging
import time
import random

logger = logging.getLogger(__name__)

class GoogleJobsScraper:
    """Scraper for Google Jobs search results"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.base_url = "https://www.google.com/search"
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 20) -> List[Dict]:
        """Search for jobs using Google Jobs"""
        try:
            logger.info(f"Searching Google Jobs for '{keyword}' in {location}")
            
            # Construct search query
            query = f"{keyword} jobs {location}"
            
            # Google Jobs search parameters
            params = {
                'q': query,
                'ibp': 'htl;jobs',  # This triggers Google Jobs
                'hl': 'en',
                'gl': 'us'
            }
            
            # Make the request
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse the response
            jobs = self._parse_google_jobs(response.text, keyword, limit)
            
            logger.info(f"Found {len(jobs)} jobs from Google Jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching Google Jobs: {e}")
            # Don't return sample data, just return empty list
            return []
    
    def _parse_google_jobs(self, html_content: str, keyword: str, limit: int) -> List[Dict]:
        """Parse Google Jobs HTML content"""
        jobs = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # Look for Google Jobs structured data
            job_listings = soup.find_all('div', {'class': 'g'})
            
            # If no Google Jobs data found, try parsing regular search results
            if not job_listings:
                job_listings = soup.find_all('div', {'class': 'tF2Cxc'})
            
            # If still no results, try alternative selectors
            if not job_listings:
                job_listings = soup.find_all(['div', 'article'], {'class': re.compile(r'job|position|listing|result', re.I)})
            
            for listing in job_listings[:limit]:
                try:
                    job = self._extract_job_info(listing, keyword)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Error extracting job from listing: {e}")
                    continue
            
            # If no structured data found, try alternative parsing
            if not jobs:
                jobs = self._parse_alternative_format(soup, keyword, limit)
                
        except Exception as e:
            logger.error(f"Error parsing Google Jobs HTML: {e}")
        
        return jobs[:limit]
    
    def _extract_job_info(self, listing, keyword: str) -> Optional[Dict]:
        """Extract job information from a listing element"""
        try:
            # Extract title
            title_elem = listing.find('h3') or listing.find('a')
            title = title_elem.get_text(strip=True) if title_elem else f"{keyword} Position"
            
            # Extract company
            company_elem = listing.find('div', {'class': 'company'}) or listing.find('span', {'class': 'company'})
            company = company_elem.get_text(strip=True) if company_elem else "Company Not Specified"
            
            # Extract location
            location_elem = listing.find('div', {'class': 'location'}) or listing.find('span', {'class': 'location'})
            location = location_elem.get_text(strip=True) if location_elem else "Location Not Specified"
            
            # Extract snippet
            snippet_elem = listing.find('div', {'class': 'snippet'}) or listing.find('span', {'class': 'snippet'})
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else f"Join our team as a {keyword}"
            
            # Extract URL
            url_elem = listing.find('a')
            job_url = url_elem.get('href') if url_elem else f"https://www.google.com/search?q={keyword}+jobs"
            
            # Extract skills from title and snippet
            skills = self._extract_skills(title, snippet, keyword)
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'snippet': snippet,
                'salary': 'Competitive',  # Google Jobs usually doesn't show salary
                'posted_date': datetime.now().isoformat(),
                'source': 'Google Jobs',
                'job_url': job_url,
                'skills': skills,
                'department': self._extract_department(title),
                'job_type': 'Full-time'  # Default assumption
            }
            
        except Exception as e:
            logger.debug(f"Error extracting job info: {e}")
            return None
    
    def _parse_alternative_format(self, soup, keyword: str, limit: int) -> List[Dict]:
        """Parse alternative Google Jobs format"""
        jobs = []
        
        try:
            # Look for job cards in different formats
            job_cards = soup.find_all(['div', 'article'], {'class': re.compile(r'job|position|listing', re.I)})
            
            for card in job_cards[:limit]:
                try:
                    job = self._extract_from_card(card, keyword)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Error extracting from card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in alternative parsing: {e}")
        
        return jobs
    
    def _extract_from_card(self, card, keyword: str) -> Optional[Dict]:
        """Extract job info from a job card"""
        try:
            # Try to find title in various formats
            title = self._find_text_in_card(card, ['h1', 'h2', 'h3', 'h4', '.title', '.job-title'])
            if not title:
                title = f"{keyword} Position"
            
            # Try to find company
            company = self._find_text_in_card(card, ['.company', '.employer', '.organization'])
            if not company:
                company = "Company Not Specified"
            
            # Try to find location
            location = self._find_text_in_card(card, ['.location', '.place', '.city'])
            if not location:
                location = "Location Not Specified"
            
            # Try to find description
            snippet = self._find_text_in_card(card, ['.description', '.summary', '.snippet'])
            if not snippet:
                snippet = f"Join our team as a {keyword}"
            
            # Extract skills
            skills = self._extract_skills(title, snippet, keyword)
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'snippet': snippet,
                'salary': 'Competitive',
                'posted_date': datetime.now().isoformat(),
                'source': 'Google Jobs',
                'job_url': 'https://www.google.com/search?ibp=htl;jobs',
                'skills': skills,
                'department': self._extract_department(title),
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            logger.debug(f"Error extracting from card: {e}")
            return None
    
    def _find_text_in_card(self, card, selectors: List[str]) -> str:
        """Find text content using multiple selectors"""
        for selector in selectors:
            try:
                elem = card.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text:
                        return text
            except:
                continue
        return ""
    
    def _extract_skills(self, title: str, snippet: str, keyword: str) -> List[str]:
        """Extract skills from job title and description"""
        skills = [keyword.lower()]
        
        # Common tech skills to look for
        tech_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'postgresql', 'mongodb', 'redis', 'git', 'sql',
            'machine learning', 'ai', 'data science', 'devops', 'frontend', 'backend'
        ]
        
        text = f"{title} {snippet}".lower()
        for skill in tech_skills:
            if skill in text:
                skills.append(skill)
        
        return list(set(skills))[:5]  # Limit to 5 skills
    
    def _extract_department(self, title: str) -> str:
        """Extract department from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['engineer', 'developer', 'programmer']):
            return 'Engineering'
        elif any(word in title_lower for word in ['designer', 'ui', 'ux']):
            return 'Design'
        elif any(word in title_lower for word in ['data', 'analyst', 'scientist']):
            return 'Data Science'
        elif any(word in title_lower for word in ['product', 'manager']):
            return 'Product'
        else:
            return 'General'
    
    def _get_sample_jobs(self, keyword: str, location: str, limit: int) -> List[Dict]:
        """Return sample jobs when scraping fails"""
        sample_jobs = []
        
        for i in range(min(limit, 5)):
            sample_jobs.append({
                'title': f'{keyword.title()} at Sample Company {i+1}',
                'company': f'Sample Company {i+1}',
                'location': location,
                'snippet': f'Sample {keyword} position - Google Jobs temporarily unavailable',
                'salary': 'Competitive',
                'posted_date': datetime.now().isoformat(),
                'source': 'Google Jobs (Sample)',
                'job_url': 'https://www.google.com/search?ibp=htl;jobs',
                'skills': [keyword.lower(), 'sample', 'google_jobs'],
                'department': 'Engineering',
                'job_type': 'Full-time'
            })
        
        return sample_jobs
    
    def get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information"""
        try:
            response = self.session.get(job_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract additional details
            details = {
                'full_description': soup.get_text()[:1000],  # First 1000 chars
                'requirements': self._extract_requirements(soup),
                'benefits': self._extract_benefits(soup),
                'application_deadline': None
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return {}
    
    def _extract_requirements(self, soup) -> List[str]:
        """Extract job requirements"""
        requirements = []
        # Look for requirements sections
        req_sections = soup.find_all(['div', 'section'], string=re.compile(r'requirements|qualifications|skills', re.I))
        
        for section in req_sections:
            req_items = section.find_all(['li', 'p'])
            for item in req_items:
                text = item.get_text(strip=True)
                if text and len(text) > 10:
                    requirements.append(text)
        
        return requirements[:5]  # Limit to 5 requirements
    
    def _extract_benefits(self, soup) -> List[str]:
        """Extract job benefits"""
        benefits = []
        # Look for benefits sections
        benefit_sections = soup.find_all(['div', 'section'], string=re.compile(r'benefits|perks|what we offer', re.I))
        
        for section in benefit_sections:
            benefit_items = section.find_all(['li', 'p'])
            for item in benefit_items:
                text = item.get_text(strip=True)
                if text and len(text) > 10:
                    benefits.append(text)
        
        return benefits[:5]  # Limit to 5 benefits
