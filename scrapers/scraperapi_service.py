#!/usr/bin/env python3
"""
ScraperAPI Service Integration
Uses ScraperAPI REST API instead of proxy mode
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import time

@dataclass
class ScraperAPIJob:
    """Job data from ScraperAPI"""
    title: str
    company: str
    location: str
    salary: str = ""
    snippet: str = ""
    job_url: str = ""
    skills: List[str] = None
    source: str = "indeed"
    scraping_method: str = "scraperapi"

    def __post_init__(self):
        if self.skills is None:
            self.skills = []

class ScraperAPIService:
    """ScraperAPI service for job scraping"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.scraperapi.com/"
        self.logger = logging.getLogger(__name__)
        
    async def scrape_indeed_jobs(self, keyword: str, location: str = "United States", limit: int = 100) -> List[Dict]:
        """Scrape Indeed jobs using ScraperAPI"""
        jobs = []
        page_num = 0
        
        self.logger.info(f"Starting ScraperAPI job search for '{keyword}' in {location}")
        
        while len(jobs) < limit:
            try:
                # Construct Indeed URL
                indeed_url = f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}"
                if page_num > 0:
                    indeed_url += f"&start={page_num * 10}"
                
                self.logger.info(f"Scraping page {page_num + 1}: {indeed_url}")
                
                # ScraperAPI parameters - try different country codes
                country_codes = ['us', 'ca', 'gb', 'au']  # Try different countries
                country_code = country_codes[page_num % len(country_codes)]
                
                params = {
                    'api_key': self.api_key,
                    'url': indeed_url,
                    'render': 'true',  # Enable JavaScript rendering
                    'country_code': country_code,  # Rotate country codes
                    'premium': 'true'  # Use premium proxies
                }
                
                # Make request to ScraperAPI
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.base_url, params=params, timeout=30) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            page_jobs = self._extract_jobs_from_html(html_content, keyword)
                            
                            if not page_jobs:
                                self.logger.warning(f"No jobs found on page {page_num + 1}")
                                break
                            
                            # Add jobs to results
                            for job in page_jobs:
                                if len(jobs) >= limit:
                                    break
                                jobs.append(job)
                            
                            self.logger.info(f"Found {len(page_jobs)} jobs on page {page_num + 1}")
                            page_num += 1
                            
                            # Add delay between requests
                            await asyncio.sleep(2)
                            
                        else:
                            self.logger.error(f"ScraperAPI request failed: {response.status}")
                            break
                            
            except Exception as e:
                self.logger.error(f"Error scraping page {page_num + 1}: {e}")
                break
        
        self.logger.info(f"ScraperAPI search completed: {len(jobs)} jobs found")
        return jobs
    
    def _extract_jobs_from_html(self, html_content: str, keyword: str) -> List[Dict]:
        """Extract job data from HTML content"""
        from bs4 import BeautifulSoup
        
        jobs = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if this is a homepage (no job listings)
        if 'jobsearch-Layout' in html_content and 'jobsearch-Header-h1' in html_content:
            self.logger.info("Detected Indeed homepage - no job listings on this page")
            return jobs
        
        # Find job cards - try multiple selectors for different Indeed versions
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        if not job_cards:
            # Try alternative selectors for different Indeed versions
            job_cards = soup.find_all('div', {'data-jk': True})
        
        if not job_cards:
            # Try Italian Indeed selectors
            job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')
        
        if not job_cards:
            # Try more generic selectors
            job_cards = soup.find_all('div', {'class': lambda x: x and 'job' in x.lower()})
        
        self.logger.info(f"Found {len(job_cards)} job cards in HTML")
        
        for card in job_cards:
            try:
                # Extract job title
                title_elem = card.find('h2', class_='jobTitle')
                if not title_elem:
                    title_elem = card.find('h2')
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # Extract company
                company_elem = card.find('span', {'data-testid': 'company-name'})
                if not company_elem:
                    company_elem = card.find('span', class_='companyName')
                company = company_elem.get_text(strip=True) if company_elem else ""
                
                # Extract location
                location_elem = card.find('div', {'data-testid': 'text-location'})
                if not location_elem:
                    location_elem = card.find('div', class_='companyLocation')
                location = location_elem.get_text(strip=True) if location_elem else ""
                
                # Extract job URL
                job_link = card.find('a', class_='jcs-JobTitle')
                if not job_link:
                    job_link = card.find('a', {'data-testid': 'job-title'})
                job_url = ""
                if job_link and job_link.get('href'):
                    href = job_link['href']
                    job_url = f"https://www.indeed.com{href}" if href.startswith('/') else href
                
                # Extract snippet
                snippet_elem = card.find('div', class_='job-snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                # Extract salary
                salary_elem = card.find('div', class_='metadata')
                if salary_elem:
                    salary_span = salary_elem.find('span', class_='salary-snippet')
                    salary = salary_span.get_text(strip=True) if salary_span else ""
                else:
                    salary = ""
                
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
                    'scraping_method': 'scraperapi'
                }
                
                if title and company:  # Only add if we have essential data
                    jobs.append(job_data)
                    
            except Exception as e:
                self.logger.debug(f"Error extracting job data: {e}")
                continue
        
        return jobs
    
    def _extract_skills(self, text: str, title: str = "") -> List[str]:
        """Extract skills from job text"""
        # Common programming languages and technologies
        skills_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'spring', 'sql', 'postgresql', 'mysql',
            'mongodb', 'redis', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'git', 'jenkins', 'ci/cd', 'agile', 'scrum', 'rest', 'api', 'graphql',
            'machine learning', 'ai', 'data science', 'pandas', 'numpy', 'tensorflow',
            'pytorch', 'scikit-learn', 'linux', 'bash', 'shell', 'terraform',
            'ansible', 'elasticsearch', 'kafka', 'rabbitmq', 'microservices'
        ]
        
        found_skills = []
        combined_text = f"{title} {text}".lower()
        
        for skill in skills_keywords:
            if skill in combined_text:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limit to 10 skills
