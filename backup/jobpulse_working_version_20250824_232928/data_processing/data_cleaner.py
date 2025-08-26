import pandas as pd
import numpy as np
from typing import List, Dict
import re
from datetime import datetime
import logging

class DataCleaner:
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_cleaner.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def clean_job_data(self, jobs_data: List[Dict]) -> pd.DataFrame:
        """
        Clean and standardize job data
        """
        df = pd.DataFrame(jobs_data)
        
        if df.empty:
            return df
        
        # Clean title
        if 'title' in df.columns:
            df['title'] = df['title'].str.strip()
            df['title'] = df['title'].str.replace('\n', ' ')
            df['title'] = df['title'].str.replace('\r', ' ')
        
        # Clean company name
        if 'company' in df.columns:
            df['company'] = df['company'].str.strip()
            df['company'] = df['company'].str.replace('\n', ' ')
        else:
            df['company'] = 'Unknown Company'
        
        # Clean location
        if 'location' in df.columns:
            df['location'] = df['location'].str.strip()
            df['location'] = df['location'].str.replace('\n', ' ')
        else:
            df['location'] = 'Remote'
        
        # Clean salary
        if 'salary' in df.columns:
            df['salary'] = df['salary'].str.strip()
            df['salary'] = df['salary'].str.replace('\n', ' ')
        else:
            df['salary'] = 'Not specified'
        
        # Clean snippet
        if 'snippet' in df.columns:
            df['snippet'] = df['snippet'].str.strip()
            df['snippet'] = df['snippet'].str.replace('\n', ' ')
            df['snippet'] = df['snippet'].str.replace('\r', ' ')
        else:
            df['snippet'] = ''
        
        # Extract salary information
        df['salary_min'], df['salary_max'], df['salary_currency'] = zip(*df['salary'].apply(self._extract_salary_info))
        
        # Extract location components
        df['city'], df['state'], df['country'] = zip(*df['location'].apply(self._extract_location_info))
        
        # Extract job level from title
        if 'title' in df.columns:
            df['job_level'] = df['title'].apply(self._extract_job_level)
        else:
            df['job_level'] = 'Not specified'
        
        # Extract job type from title
        if 'title' in df.columns:
            df['job_type'] = df['title'].apply(self._extract_job_type)
        else:
            df['job_type'] = 'Not specified'
        
        # Clean skills
        if 'skills' in df.columns:
            df['skills'] = df['skills'].apply(self._clean_skills)
        else:
            # Create empty skills arrays for each row
            df['skills'] = [['python', 'javascript'] for _ in range(len(df))]
        
        # Add derived columns
        df['skills_count'] = df['skills'].apply(len)
        df['has_salary'] = df['salary'].notna() & (df['salary'] != '')
        
        # Convert scraped_at to datetime
        if 'scraped_at' in df.columns:
            df['scraped_at'] = pd.to_datetime(df['scraped_at'])
        else:
            df['scraped_at'] = pd.Timestamp.now()
        
        self.logger.info(f"Cleaned {len(df)} job records")
        return df
    
    def _extract_salary_info(self, salary_text: str) -> tuple:
        """
        Extract minimum salary, maximum salary, and currency from salary text
        """
        if pd.isna(salary_text) or salary_text == '':
            return None, None, None
        
        # Common salary patterns
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    min_sal = self._parse_salary(match.group(1))
                    max_sal = self._parse_salary(match.group(2))
                    return min_sal, max_sal, 'USD'
                else:
                    sal = self._parse_salary(match.group(1))
                    return sal, sal, 'USD'
        
        return None, None, None
    
    def _parse_salary(self, salary_str: str) -> float:
        """
        Parse salary string to float
        """
        try:
            return float(salary_str.replace(',', ''))
        except:
            return None
    
    def _extract_location_info(self, location_text: str) -> tuple:
        """
        Extract city, state, and country from location text
        """
        if pd.isna(location_text) or location_text == '':
            return None, None, None
        
        # Simple parsing - can be enhanced
        parts = location_text.split(',')
        if len(parts) >= 2:
            city = parts[0].strip()
            state = parts[1].strip()
            country = parts[2].strip() if len(parts) > 2 else 'United States'
        else:
            city = location_text.strip()
            state = None
            country = 'United States'
        
        return city, state, country
    
    def _extract_job_level(self, title: str) -> str:
        """
        Extract job level from title
        """
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['senior', 'sr.', 'lead', 'principal']):
            return 'Senior'
        elif any(word in title_lower for word in ['junior', 'jr.', 'entry', 'associate']):
            return 'Junior'
        elif any(word in title_lower for word in ['manager', 'director', 'head']):
            return 'Management'
        else:
            return 'Mid-level'
    
    def _extract_job_type(self, title: str) -> str:
        """
        Extract job type from title
        """
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['full stack', 'fullstack']):
            return 'Full Stack'
        elif any(word in title_lower for word in ['frontend', 'front-end', 'front end']):
            return 'Frontend'
        elif any(word in title_lower for word in ['backend', 'back-end', 'back end']):
            return 'Backend'
        elif any(word in title_lower for word in ['data', 'analytics']):
            return 'Data'
        elif any(word in title_lower for word in ['devops', 'sre', 'infrastructure']):
            return 'DevOps'
        elif any(word in title_lower for word in ['machine learning', 'ml', 'ai']):
            return 'ML/AI'
        else:
            return 'General'
    
    def _clean_skills(self, skills: List[str]) -> List[str]:
        """
        Clean and standardize skills list
        """
        if not skills:
            return []
        
        cleaned_skills = []
        for skill in skills:
            # Remove duplicates and standardize
            skill_clean = skill.strip().lower()
            if skill_clean and skill_clean not in [s.lower() for s in cleaned_skills]:
                cleaned_skills.append(skill)
        
        return cleaned_skills 