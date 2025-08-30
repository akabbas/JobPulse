"""
Refactored Indeed Scraper implementing the new BaseScraper interface.

This is an example of how to refactor existing scrapers to work with
the new plugin architecture.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Optional, Any
import re

from base_scraper import BaseScraper, ScraperType, ScraperError
from config.settings import HEADERS, DELAY_BETWEEN_REQUESTS, TECH_SKILLS


class IndeedScraperRefactored(BaseScraper):
    """
    Refactored Indeed scraper implementing the BaseScraper interface.
    
    This scraper demonstrates how to convert existing scrapers to work
    with the new plugin architecture while maintaining all existing functionality.
    """
    
    def __init__(self):
        """Initialize the Indeed scraper with the new interface"""
        super().__init__(
            name="Indeed",
            scraper_type=ScraperType.WEB_SCRAPER,
            priority=3  # Medium priority - web scraping can be unreliable
        )
        
        # Indeed-specific configuration
        self.base_url = "https://www.indeed.com"
        self.max_pages = 10  # Maximum pages to scrape
        self.jobs_per_page = 10
        
        # Location support
        self.supported_locations = [
            "United States", "Canada", "United Kingdom", "Australia", 
            "Germany", "France", "Netherlands", "Sweden", "Norway", "Denmark"
        ]
    
    def _init_resources(self):
        """Initialize scraper-specific resources"""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
        # Add retry mechanism
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def search_jobs(self, keyword: str, location: str = "United States", 
                   limit: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for jobs on Indeed based on keyword and location.
        
        Args:
            keyword: Job search keyword
            location: Location to search in
            limit: Maximum number of jobs to return
            **kwargs: Additional search parameters
            
        Returns:
            List of job dictionaries with standardized format
            
        Raises:
            ScraperError: If the scraper encounters an error
        """
        try:
            jobs = []
            page = 0
            
            while len(jobs) < limit and page < self.max_pages:
                try:
                    # Construct search URL
                    search_url = f"{self.base_url}/jobs"
                    params = {
                        'q': keyword,
                        'l': location,
                        'start': page * self.jobs_per_page
                    }
                    
                    self.logger.info(f"Searching page {page + 1} for '{keyword}' in {location}")
                    
                    response = self.session.get(search_url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find job cards
                    job_cards = soup.find_all('div', {'class': 'job_seen_beacon'})
                    
                    if not job_cards:
                        self.logger.warning("No job cards found on this page")
                        break
                    
                    for card in job_cards:
                        if len(jobs) >= limit:
                            break
                        
                        job_data = self._extract_job_data(card, keyword)
                        if job_data:
                            jobs.append(job_data)
                    
                    page += 1
                    time.sleep(random.uniform(1, DELAY_BETWEEN_REQUESTS))
                    
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Request error on page {page}: {str(e)}")
                    if "403" in str(e):
                        self.update_status(ScraperType.BLOCKED)
                        raise ScraperError(f"Indeed is blocking requests: {str(e)}", self.name, e)
                    break
                except Exception as e:
                    self.logger.error(f"Error scraping page {page}: {str(e)}")
                    break
            
            self.logger.info(f"Scraped {len(jobs)} jobs for '{keyword}' from Indeed")
            return jobs
            
        except Exception as e:
            if not isinstance(e, ScraperError):
                raise ScraperError(f"Indeed scraping failed: {str(e)}", self.name, e)
            raise
    
    def _extract_job_data(self, card, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Extract job information from a job card.
        
        Args:
            card: BeautifulSoup element containing job data
            keyword: Search keyword for context
            
        Returns:
            Dictionary containing job data or None if extraction fails
        """
        try:
            # Job title
            title_elem = card.find('h2', {'class': 'jobTitle'})
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            if not title:
                return None
            
            # Company name
            company_elem = card.find('span', {'class': 'companyName'})
            company = company_elem.get_text(strip=True) if company_elem else ""
            
            # Location
            location_elem = card.find('div', {'class': 'companyLocation'})
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Job URL
            job_link = card.find('a', {'class': 'jcs-JobTitle'})
            job_url = self.base_url + job_link['href'] if job_link else ""
            
            # Salary (if available)
            salary_elem = card.find('div', {'class': 'metadata salary-snippet-container'})
            salary = salary_elem.get_text(strip=True) if salary_elem else ""
            
            # Job snippet/description
            snippet_elem = card.find('div', {'class': 'job-snippet'})
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            # Extract skills from title and snippet
            skills = self._extract_skills(title + " " + snippet, title)
            
            # Create standardized job data
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'snippet': snippet[:200] + '...' if len(snippet) > 200 else snippet,
                'job_url': job_url,
                'skills': skills,
                'search_keyword': keyword,
                'source': 'indeed',
                'scraped_at': datetime.now().isoformat(),
                'platform': 'indeed',
                'job_id': self._extract_job_id(job_url) if job_url else None
            }
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error extracting job data: {str(e)}")
            return None
    
    def _extract_skills(self, text: str, title: str) -> List[str]:
        """
        Extract technical skills from job text.
        
        Args:
            text: Job description text
            title: Job title
            
        Returns:
            List of detected technical skills
        """
        skills = []
        text_lower = (text + " " + title).lower()
        
        # Check for skills in the text
        for skill in TECH_SKILLS:
            if skill.lower() in text_lower:
                skills.append(skill)
        
        # Add some common variations
        skill_variations = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'react.js': 'React',
            'node.js': 'Node.js',
            'python3': 'Python',
            'aws': 'AWS',
            'gcp': 'Google Cloud',
            'azure': 'Azure'
        }
        
        for variation, skill in skill_variations.items():
            if variation in text_lower and skill not in skills:
                skills.append(skill)
        
        return skills[:10]  # Limit to top 10 skills
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        """Extract job ID from Indeed URL"""
        if not url:
            return None
        
        # Indeed URLs typically contain job IDs
        match = re.search(r'/jobs/view/([^/?]+)', url)
        if match:
            return match.group(1)
        
        return None
    
    def can_handle_location(self, location: str) -> bool:
        """
        Check if this scraper can handle a specific location.
        
        Args:
            location: Location string to check
            
        Returns:
            True if the scraper can handle this location
        """
        # Indeed works globally, but some locations may have better results
        location_lower = location.lower()
        
        # Check if it's a supported location
        for supported in self.supported_locations:
            if supported.lower() in location_lower or location_lower in supported.lower():
                return True
        
        # Default to True for most locations
        return True
    
    def get_supported_features(self) -> List[str]:
        """Get list of features supported by this scraper"""
        return ['basic_search', 'location_filtering', 'skill_extraction']
    
    def cleanup(self):
        """Clean up resources used by the scraper"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific job.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Detailed job information or None if not available
        """
        try:
            if not job_url or 'indeed.com' not in job_url:
                return None
            
            response = self.session.get(job_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed information
            description_elem = soup.find('div', {'class': 'job-description'})
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Extract additional details
            details = {}
            
            # Company details
            company_elem = soup.find('div', {'class': 'company-info'})
            if company_elem:
                details['company_info'] = company_elem.get_text(strip=True)
            
            # Job requirements
            requirements_elem = soup.find('div', {'class': 'job-requirements'})
            if requirements_elem:
                details['requirements'] = requirements_elem.get_text(strip=True)
            
            return {
                'description': description,
                'details': details,
                'full_url': job_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting job details: {str(e)}")
            return None
