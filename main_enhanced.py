#!/usr/bin/env python3
"""
Enhanced JobPulse - Main Application
Integrates multiple scrapers and advanced search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.indeed_scraper import IndeedScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.stackoverflow_scraper import StackOverflowScraper
from scrapers.dice_scraper import DiceScraper
from scrapers.remoteok_scraper import RemoteOKScraper
from scrapers.weworkremotely_scraper import WeWorkRemotelyScraper
from scrapers.api_sources_scraper import APISourcesScraper
from scrapers.reddit_scraper import RedditScraper
from data_processing.data_cleaner import DataCleaner
from analysis.skill_trends import SkillTrendsAnalyzer
from database.postgresql_manager import JobPulsePostgreSQLManager
from database.snowflake_manager import JobPulseSnowflakeManager
import logging
import json
from datetime import datetime
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize scrapers
        indeed_scraper = IndeedScraper()
        linkedin_scraper = LinkedInScraper()
        stackoverflow_scraper = StackOverflowScraper()
        dice_scraper = DiceScraper()
        remoteok_scraper = RemoteOKScraper()
        weworkremotely_scraper = WeWorkRemotelyScraper()
        api_scraper = APISourcesScraper()
        reddit_scraper = RedditScraper()
        
        # Initialize data processors
        data_cleaner = DataCleaner()
        skill_analyzer = SkillTrendsAnalyzer()
        
        # Initialize database managers
        postgres_manager = JobPulsePostgreSQLManager()
        snowflake_manager = JobPulseSnowflakeManager()
        
        # Search parameters
        keyword = "software engineer"
        location = "United States"
        limit_per_source = 50  # Increased from 25 to 50 per source
        
        all_jobs = []
        
        # Indeed jobs
        try:
            logger.info("Scraping Indeed...")
            indeed_jobs = indeed_scraper.search_jobs(keyword, location, limit_per_source)
            all_jobs.extend(indeed_jobs)
            logger.info(f"Found {len(indeed_jobs)} jobs on Indeed")
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
        
        # LinkedIn jobs
        try:
            logger.info("Scraping LinkedIn...")
            linkedin_jobs = linkedin_scraper.search_jobs(keyword, location, limit_per_source)
            all_jobs.extend(linkedin_jobs)
            logger.info(f"Found {len(linkedin_jobs)} jobs on LinkedIn")
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        
        # Stack Overflow jobs
        try:
            logger.info("Scraping Stack Overflow...")
            stackoverflow_jobs = stackoverflow_scraper.search_jobs(keyword, location, limit_per_source)
            all_jobs.extend(stackoverflow_jobs)
            logger.info(f"Found {len(stackoverflow_jobs)} jobs on Stack Overflow")
        except Exception as e:
            logger.error(f"Error scraping Stack Overflow: {e}")
        
        # Dice jobs
        try:
            logger.info("Scraping Dice...")
            dice_jobs = dice_scraper.search_jobs(keyword, location, limit_per_source)
            all_jobs.extend(dice_jobs)
            logger.info(f"Found {len(dice_jobs)} jobs on Dice")
        except Exception as e:
            logger.error(f"Error scraping Dice: {e}")
        
        # Remote OK jobs
        try:
            logger.info("Scraping Remote OK...")
            remoteok_jobs = remoteok_scraper.search_jobs(keyword, location, limit_per_source)
            all_jobs.extend(remoteok_jobs)
            logger.info(f"Found {len(remoteok_jobs)} jobs on Remote OK")
        except Exception as e:
            logger.error(f"Error scraping Remote OK: {e}")
        
        # We Work Remotely jobs
        try:
            logger.info("Scraping We Work Remotely...")
            weworkremotely_jobs = weworkremotely_scraper.search_jobs(keyword, location, limit_per_source)
            all_jobs.extend(weworkremotely_jobs)
            logger.info(f"Found {len(weworkremotely_jobs)} jobs on We Work Remotely")
        except Exception as e:
            logger.error(f"Error scraping We Work Remotely: {e}")
        
        # API sources
        try:
            logger.info("Searching API sources...")
            api_jobs = api_scraper.search_jobs(keyword, location, limit_per_source)
            all_jobs.extend(api_jobs)
            logger.info(f"Found {len(api_jobs)} jobs from API sources")
        except Exception as e:
            logger.error(f"Error with API sources: {e}")
        
        # Reddit sources
        try:
            logger.info("Searching Reddit sources...")
            reddit_jobs = reddit_scraper.search_jobs(keyword, location, limit_per_source)
            all_jobs.extend(reddit_jobs)
            logger.info(f"Found {len(reddit_jobs)} jobs from Reddit")
        except Exception as e:
            logger.error(f"Error with Reddit sources: {e}")
        
        logger.info(f"Total jobs collected: {len(all_jobs)}")
        
        # Clean and process data
        if all_jobs:
            df = data_cleaner.clean_job_data(all_jobs)
            logger.info(f"Cleaned {len(df)} job records")
            
            # Analyze skills
            skill_analysis = skill_analyzer.analyze_skill_frequency(df)
            logger.info(f"Skill analysis completed")
            
            # Save to databases
            try:
                postgres_manager.save_jobs_batch(all_jobs)
                logger.info("Saved jobs to PostgreSQL")
            except Exception as e:
                logger.error(f"Error saving to PostgreSQL: {e}")
            
            try:
                snowflake_manager.save_jobs_batch(all_jobs)
                logger.info("Saved jobs to Snowflake")
            except Exception as e:
                logger.error(f"Error saving to Snowflake: {e}")
            
            # Create output directory
            os.makedirs('output', exist_ok=True)
            
            # Save results
            results = {
                'timestamp': datetime.now().isoformat(),
                'keyword': keyword,
                'location': location,
                'total_jobs': len(all_jobs),
                'sources': {
                    'indeed': len(indeed_jobs) if 'indeed_jobs' in locals() else 0,
                    'linkedin': len(linkedin_jobs) if 'linkedin_jobs' in locals() else 0,
                    'stackoverflow': len(stackoverflow_jobs) if 'stackoverflow_jobs' in locals() else 0,
                    'dice': len(dice_jobs) if 'dice_jobs' in locals() else 0,
                    'remoteok': len(remoteok_jobs) if 'remoteok_jobs' in locals() else 0,
                    'weworkremotely': len(weworkremotely_jobs) if 'weworkremotely_jobs' in locals() else 0,
                    'api_sources': len(api_jobs) if 'api_jobs' in locals() else 0,
                    'reddit': len(reddit_jobs) if 'reddit_jobs' in locals() else 0
                },
                'skill_analysis': skill_analysis,
                'top_skills': skill_analysis.get('programming_languages', [])[:10]
            }
            
            with open('output/results.json', 'w') as f:
                json.dump(results, f, indent=2)
            
            # Print summary
            print(f"\n{'='*50}")
            print(f"JOB MARKET ANALYSIS RESULTS")
            print(f"{'='*50}")
            print(f"Keyword: {keyword}")
            print(f"Location: {location}")
            print(f"Total Jobs: {len(all_jobs)}")
            print(f"\nJobs by Source:")
            for source, count in results['sources'].items():
                print(f"  {source}: {count}")
            print(f"\nTop Skills:")
            for skill, percentage in results['top_skills']:
                print(f"  {skill}: {percentage:.1f}%")
            print(f"{'='*50}")
            
        else:
            logger.warning("No jobs found")
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main() 