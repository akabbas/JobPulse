from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/jobmarket')

Base = declarative_base()

class JobPosting(Base):
    """SQLAlchemy model for job postings"""
    __tablename__ = 'job_postings'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    company = Column(String(200))
    location = Column(String(200))
    salary = Column(String(100))
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10))
    snippet = Column(Text)
    job_url = Column(String(1000))
    skills = Column(JSON)
    search_keyword = Column(String(200))
    source = Column(String(50))
    job_level = Column(String(50))
    job_type = Column(String(50))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    skills_count = Column(Integer)
    has_salary = Column(String(10))
    scraped_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/database.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(self.engine)
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def save_jobs(self, jobs: List[Dict]) -> int:
        """Save jobs to database"""
        session = self.Session()
        saved_count = 0
        
        try:
            for job_data in jobs:
                # Convert scraped_at string to datetime if needed
                if isinstance(job_data.get('scraped_at'), str):
                    job_data['scraped_at'] = datetime.fromisoformat(job_data['scraped_at'].replace('Z', '+00:00'))
                
                # Create JobPosting object
                job_posting = JobPosting(**job_data)
                session.add(job_posting)
                saved_count += 1
            
            session.commit()
            self.logger.info(f"Saved {saved_count} jobs to database")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving jobs to database: {str(e)}")
            raise
        finally:
            session.close()
        
        return saved_count
    
    def get_jobs_by_criteria(self, 
                           keyword: Optional[str] = None,
                           source: Optional[str] = None,
                           location: Optional[str] = None,
                           limit: int = 100) -> List[Dict]:
        """Get jobs from database based on criteria"""
        session = self.Session()
        
        try:
            query = session.query(JobPosting)
            
            if keyword:
                query = query.filter(JobPosting.title.ilike(f'%{keyword}%'))
            
            if source:
                query = query.filter(JobPosting.source == source)
            
            if location:
                query = query.filter(JobPosting.location.ilike(f'%{location}%'))
            
            jobs = query.limit(limit).all()
            
            # Convert to list of dictionaries
            jobs_dict = []
            for job in jobs:
                job_dict = {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'salary': job.salary,
                    'salary_min': job.salary_min,
                    'salary_max': job.salary_max,
                    'snippet': job.snippet,
                    'job_url': job.job_url,
                    'skills': job.skills,
                    'search_keyword': job.search_keyword,
                    'source': job.source,
                    'job_level': job.job_level,
                    'job_type': job.job_type,
                    'scraped_at': job.scraped_at.isoformat() if job.scraped_at else None
                }
                jobs_dict.append(job_dict)
            
            self.logger.info(f"Retrieved {len(jobs_dict)} jobs from database")
            return jobs_dict
            
        except Exception as e:
            self.logger.error(f"Error retrieving jobs from database: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_skill_statistics(self) -> Dict:
        """Get skill statistics from database"""
        session = self.Session()
        
        try:
            # Get all skills from database
            result = session.execute(text("""
                SELECT skills FROM job_postings 
                WHERE skills IS NOT NULL AND skills != '[]'
            """))
            
            all_skills = []
            for row in result:
                if row[0]:  # skills column
                    all_skills.extend(row[0])
            
            # Count skills
            from collections import Counter
            skill_counts = Counter(all_skills)
            
            # Calculate percentages
            total_jobs = session.query(JobPosting).count()
            skill_percentages = {skill: (count / total_jobs) * 100 
                               for skill, count in skill_counts.items()}
            
            return {
                'total_jobs': total_jobs,
                'skill_counts': dict(skill_counts),
                'skill_percentages': skill_percentages
            }
            
        except Exception as e:
            self.logger.error(f"Error getting skill statistics: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_jobs_by_skills(self, required_skills: List[str]) -> List[Dict]:
        """Get jobs that have specific skills"""
        session = self.Session()
        
        try:
            # Build query to find jobs with required skills
            query = session.query(JobPosting)
            
            for skill in required_skills:
                query = query.filter(JobPosting.skills.contains([skill]))
            
            jobs = query.all()
            
            # Convert to list of dictionaries
            jobs_dict = []
            for job in jobs:
                job_dict = {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'salary': job.salary,
                    'skills': job.skills,
                    'source': job.source,
                    'scraped_at': job.scraped_at.isoformat() if job.scraped_at else None
                }
                jobs_dict.append(job_dict)
            
            return jobs_dict
            
        except Exception as e:
            self.logger.error(f"Error getting jobs by skills: {str(e)}")
            raise
        finally:
            session.close()
    
    def cleanup_old_jobs(self, days_old: int = 30):
        """Remove jobs older than specified days"""
        session = self.Session()
        
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            deleted_count = session.query(JobPosting).filter(
                JobPosting.scraped_at < cutoff_date
            ).delete()
            
            session.commit()
            self.logger.info(f"Deleted {deleted_count} old jobs from database")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error cleaning up old jobs: {str(e)}")
            raise
        finally:
            session.close()

# Snowflake integration stub
class SnowflakeManager:
    """Stub for Snowflake integration"""
    def __init__(self, account: str, user: str, password: str, warehouse: str, database: str):
        self.account = account
        self.user = user
        self.password = password
        self.warehouse = warehouse
        self.database = database
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/snowflake.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Connect to Snowflake"""
        try:
            import snowflake.connector
            self.conn = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                database=self.database
            )
            self.logger.info("Connected to Snowflake successfully")
        except Exception as e:
            self.logger.error(f"Error connecting to Snowflake: {str(e)}")
            raise
    
    def save_jobs_to_snowflake(self, jobs: List[Dict]):
        """Save jobs to Snowflake"""
        # Implementation would go here
        # Requires snowflake-connector-python package
        self.logger.info(f"Would save {len(jobs)} jobs to Snowflake")
        pass 