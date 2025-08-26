"""
Lever Jobs Scraper for JobPulse
Uses Lever's public API to avoid 403 errors and get real job data
"""

import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class LeverScraper:
    """Lever Jobs scraper using their public API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JobPulse/1.0 (https://github.com/akabbas/JobPulse)',
            'Accept': 'application/json'
        })
        
        # List of companies using Lever (these are public and accessible)
        # Updated with companies that have working API endpoints
        self.lever_companies = [
            'stripe', 'coinbase', 'robinhood', 'doordash', 'instacart',
            'notion', 'figma', 'linear', 'vercel', 'netlify', 'supabase',
            'planetscale', 'github', 'shopify', 'twilio', 'slack'
        ]
    
    def search_jobs(self, keyword: str, location: str = "United States", limit: int = 25) -> List[Dict]:
        """Search for jobs across multiple Lever companies"""
        try:
            all_jobs = []
            
            for company in self.lever_companies:
                try:
                    jobs = self.get_company_jobs(company, keyword)
                    all_jobs.extend(jobs)
                    
                    if len(all_jobs) >= limit:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error getting jobs for {company}: {e}")
                    continue
            
            # Remove duplicates and limit results
            unique_jobs = self.remove_duplicates(all_jobs)
            return unique_jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error in Lever search: {e}")
            return []
    
    def get_company_jobs(self, company: str, keyword: str) -> List[Dict]:
        """Get jobs for a specific company using Lever"""
        try:
            # Lever API endpoint format
            api_url = f"https://api.lever.co/v0/postings/{company}"
            
            response = self.session.get(api_url)
            if response.status_code == 200:
                jobs_data = response.json()
                
                filtered_jobs = []
                for job in jobs_data:
                    title = job.get('text', '').lower()
                    location = job.get('categories', {}).get('location', '').lower()
                    team = job.get('categories', {}).get('team', '').lower()
                    
                    # Filter by keyword in title, location, or team
                    if (keyword.lower() in title or 
                        keyword.lower() in location or
                        keyword.lower() in team):
                        
                        job_info = {
                            'title': job.get('text', ''),
                            'company': company.title(),
                            'location': job.get('categories', {}).get('location', ''),
                            'snippet': self.extract_snippet(job),
                            'salary': self.extract_salary(job),
                            'posted_date': job.get('createdAt', datetime.now().isoformat()),
                            'source': 'Lever',
                            'job_url': job.get('hostedUrl', ''),
                            'skills': self.extract_skills(job),
                            'department': job.get('categories', {}).get('team', ''),
                            'job_type': job.get('categories', {}).get('commitment', ''),
                            'experience_level': job.get('categories', {}).get('seniority', '')
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
        description = job.get('descriptionPlain', '')
        if description:
            # Clean up the description and take first 200 characters
            cleaned = description.replace('\n', ' ').replace('\r', ' ').strip()
            return cleaned[:200] + '...' if len(cleaned) > 200 else cleaned
        return ''
    
    def extract_salary(self, job: Dict) -> str:
        """Extract salary information from job"""
        # Lever sometimes has salary info in metadata
        metadata = job.get('metadata', {})
        
        # Check for salary fields
        salary_fields = ['salary', 'compensation', 'pay']
        for field in salary_fields:
            if field in metadata:
                return str(metadata[field])
        
        return ''
    
    def extract_skills(self, job: Dict) -> List[str]:
        """Extract skills from job description"""
        description = job.get('descriptionPlain', '')
        if not description:
            return []
        
        # Common tech skills
        common_skills = [
            'python', 'javascript', 'java', 'c++', 'go', 'rust', 'php', 'ruby',
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'machine learning', 'ai', 'data science', 'devops', 'frontend', 'backend',
            'typescript', 'node.js', 'graphql', 'rest api', 'microservices'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill in description_lower:
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
            # Extract company and posting ID from URL
            # URL format: https://jobs.lever.co/{company}/{posting_id}
            parts = job_url.split('/')
            if len(parts) >= 5:
                company = parts[-2]
                posting_id = parts[-1]
                
                api_url = f"https://api.lever.co/v0/postings/{company}/{posting_id}"
                response = self.session.get(api_url)
                if response.status_code == 200:
                    return response.json()
            
            return None
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
    
    def _get_sample_jobs(self, company: str, keyword: str) -> List[Dict]:
        """Return sample jobs when API fails (temporary fallback)"""
        sample_jobs = [
            {
                'title': f'{keyword.title()} at {company.title()}',
                'company': company.title(),
                'location': 'Remote / United States',
                'snippet': f'⚠️ SAMPLE DATA: {keyword} position at {company.title()} - Lever API temporarily unavailable. This is not a real job posting.',
                'salary': 'Sample Data',
                'posted_date': datetime.now().isoformat(),
                'source': 'Lever (⚠️ SAMPLE DATA)',
                'job_url': f'https://jobs.lever.co/{company}',
                'skills': [keyword.lower(), 'sample', 'api_unavailable'],
                'department': 'Engineering',
                'job_type': 'Sample Data',
                'experience_level': 'Sample Data'
            }
        ]
        return sample_jobs

    def get_company_info(self, company: str) -> Optional[Dict]:
        """Get information about a specific company"""
        try:
            api_url = f"https://api.lever.co/v0/postings/{company}"
            response = self.session.get(api_url)
            if response.status_code == 200:
                jobs = response.json()
                if jobs:
                    # Return basic company info
                    departments = []
                    locations = []
                    
                    for job in jobs:
                        if job.get('categories', {}).get('team'):
                            departments.append(job.get('categories', {}).get('team'))
                        if job.get('categories', {}).get('location'):
                            locations.append(job.get('categories', {}).get('location'))
                    
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
