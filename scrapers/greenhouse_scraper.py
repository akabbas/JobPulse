"""
Greenhouse Jobs Scraper for JobPulse
Uses Greenhouse's public API to avoid 403 errors and get real job data
"""

import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import time
import random

logger = logging.getLogger(__name__)

class GreenhouseScraper:
    """Greenhouse Jobs scraper using their public API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JobPulse/1.0 (https://github.com/akabbas/JobPulse)',
            'Accept': 'application/json'
        })
        
        # List of companies using Greenhouse (these are public and accessible)
        # Updated with only companies that have working API endpoints (100% success rate)
        self.greenhouse_companies = [
            'airbnb', 'lyft', 'pinterest', 'stripe', 'coinbase',
            'asana', 'dropbox', 'figma', 'gusto', 'hubspot',
            'instacart', 'robinhood', 'snowflake'
        ]
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 25) -> List[Dict]:
        """Search for jobs across multiple Greenhouse companies"""
        try:
            all_jobs = []
            
            for company in self.greenhouse_companies:
                try:
                    jobs = self.get_company_jobs(company, keyword)
                    all_jobs.extend(jobs)
                    
                    if len(all_jobs) >= limit:
                        break
                        
                    # Add delay between companies to be respectful
                    time.sleep(random.uniform(0.5, 1.5))
                        
                except Exception as e:
                    logger.debug(f"Error getting jobs for {company}: {e}")
                    continue
            
            # Remove duplicates and limit results
            unique_jobs = self.remove_duplicates(all_jobs)
            return unique_jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error in Greenhouse search: {e}")
            return []
    
    def get_company_jobs(self, company: str, keyword: str) -> List[Dict]:
        """Get jobs for a specific company using Greenhouse"""
        try:
            # Greenhouse API endpoint format
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
            
            response = self.session.get(api_url, timeout=30)
            if response.status_code == 200:
                jobs_data = response.json()
                
                filtered_jobs = []
                for job in jobs_data.get('jobs', []):
                    title = job.get('title', '').lower()
                    location = job.get('location', {}).get('name', '').lower()
                    department = job.get('departments', [{}])[0].get('name', '').lower()
                    
                    # Filter by keyword in title, location, or department
                    if (keyword.lower() in title or 
                        keyword.lower() in location or
                        keyword.lower() in department):
                        
                        job_info = {
                            'title': job.get('title', ''),
                            'company': company.title(),
                            'location': job.get('location', {}).get('name', ''),
                            'snippet': self.extract_snippet(job),
                            'salary': self.extract_salary(job),
                            'posted_date': job.get('updated_at', datetime.now().isoformat()),
                            'source': 'Greenhouse',
                            'job_url': job.get('absolute_url', ''),
                            'skills': self.extract_skills(job),
                            'department': department.title(),
                            'job_type': job.get('metadata', [{}])[0].get('value', '') if job.get('metadata') else '',
                            'experience_level': self.extract_experience_level(job)
                        }
                        filtered_jobs.append(job_info)
                
                return filtered_jobs
            else:
                logger.debug(f"Failed to get jobs for {company}: {response.status_code}")
                return []
                
        except Exception as e:
            logger.debug(f"Error getting company jobs for {company}: {e}")
            # Don't return sample data, just return empty list
            return []
    
    def extract_snippet(self, job: Dict) -> str:
        """Extract a snippet from job description"""
        content = job.get('content', '')
        if content:
            # Clean up the content and take first 200 characters
            cleaned = content.replace('\n', ' ').replace('\r', ' ').strip()
            return cleaned[:200] + '...' if len(cleaned) > 200 else cleaned
        return ''
    
    def extract_salary(self, job: Dict) -> str:
        """Extract salary information from job"""
        # Greenhouse sometimes has salary info in metadata
        metadata = job.get('metadata', [])
        
        # Check for salary fields in metadata
        salary_fields = ['salary', 'compensation', 'pay']
        for meta in metadata:
            if meta.get('name', '').lower() in salary_fields:
                return str(meta.get('value', ''))
        
        return ''
    
    def extract_experience_level(self, job: Dict) -> str:
        """Extract experience level from job"""
        # Check metadata for experience level
        metadata = job.get('metadata', [])
        for meta in metadata:
            if meta.get('name', '').lower() in ['experience', 'seniority', 'level']:
                return str(meta.get('value', ''))
        
        # Try to infer from title
        title = job.get('title', '').lower()
        if any(word in title for word in ['senior', 'lead', 'principal', 'staff']):
            return 'Senior'
        elif any(word in title for word in ['junior', 'entry', 'associate']):
            return 'Junior'
        elif any(word in title for word in ['intern', 'internship']):
            return 'Intern'
        
        return 'Mid-Level'
    
    def extract_skills(self, job: Dict) -> List[str]:
        """Extract skills from job description"""
        content = job.get('content', '')
        if not content:
            return []
        
        # Common tech skills
        common_skills = [
            'python', 'javascript', 'java', 'c++', 'go', 'rust', 'php', 'ruby',
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'machine learning', 'ai', 'data science', 'devops', 'frontend', 'backend',
            'typescript', 'node.js', 'graphql', 'rest api', 'microservices',
            'html', 'css', 'sass', 'less', 'webpack', 'babel', 'jest', 'cypress'
        ]
        
        found_skills = []
        content_lower = content.lower()
        
        for skill in common_skills:
            if skill in content_lower:
                found_skills.append(skill.title())
        
        return found_skills[:10]  # Limit to 10 skills
    
    def remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job.get('title', '').lower(), job.get('company', '').lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def get_job_details(self, job_url: str) -> Optional[Dict]:
        """Get detailed job information"""
        try:
            # Extract company and job ID from URL
            # URL format: https://boards.greenhouse.io/{company}/jobs/{job_id}
            parts = job_url.split('/')
            if len(parts) >= 6:
                company = parts[-3]
                job_id = parts[-1]
                
                api_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{job_id}"
                response = self.session.get(api_url, timeout=30)
                if response.status_code == 200:
                    return response.json()
            
            return None
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
    
    def get_company_info(self, company: str) -> Optional[Dict]:
        """Get information about a specific company"""
        try:
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
            response = self.session.get(api_url, timeout=30)
            if response.status_code == 200:
                jobs = response.json().get('jobs', [])
                if jobs:
                    # Return basic company info
                    departments = []
                    locations = []
                    
                    for job in jobs:
                        if job.get('departments'):
                            dept_name = job['departments'][0].get('name', '')
                            if dept_name:
                                departments.append(dept_name)
                        if job.get('location', {}).get('name'):
                            locations.append(job['location']['name'])
                    
                    return {
                        'name': company.title(),
                        'total_jobs': len(jobs),
                        'departments': list(set(departments)),
                        'locations': list(set(locations))
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            return None
