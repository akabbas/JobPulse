#!/usr/bin/env python3
"""
JobPulse - Main Application
Analyzes software engineering job market trends using web scraping
"""

import os
import sys
import logging
from datetime import datetime
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.indeed_scraper import IndeedScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
from data_processing.data_cleaner import DataCleaner
from analysis.skill_trends import SkillTrendsAnalyzer
from config.settings import SEARCH_KEYWORDS

def setup_directories():
    """Create necessary directories"""
    directories = ['output', 'logs', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/main.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main application function"""
    logger = setup_logging()
    setup_directories()
    
    logger.info("Starting JobPulse Application")
    
    # Initialize components
    indeed_scraper = IndeedScraper()
    glassdoor_scraper = GlassdoorScraper()
    data_cleaner = DataCleaner()
    skill_analyzer = SkillTrendsAnalyzer()
    
    all_jobs = []
    
    # Scrape jobs from both sources
    for keyword in SEARCH_KEYWORDS:
        logger.info(f"Scraping jobs for keyword: {keyword}")
        
        # Scrape from Indeed
        try:
            indeed_jobs = indeed_scraper.search_jobs(keyword, limit=50)
            all_jobs.extend(indeed_jobs)
            logger.info(f"Scraped {len(indeed_jobs)} jobs from Indeed for '{keyword}'")
        except Exception as e:
            logger.error(f"Error scraping Indeed for '{keyword}': {str(e)}")
        
        # Scrape from Glassdoor
        try:
            glassdoor_jobs = glassdoor_scraper.search_jobs(keyword, limit=50)
            all_jobs.extend(glassdoor_jobs)
            logger.info(f"Scraped {len(glassdoor_jobs)} jobs from Glassdoor for '{keyword}'")
        except Exception as e:
            logger.error(f"Error scraping Glassdoor for '{keyword}': {str(e)}")
    
    if not all_jobs:
        logger.error("No jobs scraped. Exiting.")
        return
    
    # Clean and process data
    logger.info("Cleaning and processing job data...")
    df = data_cleaner.clean_job_data(all_jobs)
    
    # Save raw data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f'data/jobs_{timestamp}.csv', index=False)
    logger.info(f"Saved {len(df)} job records to data/jobs_{timestamp}.csv")
    
    # Analyze skills
    logger.info("Analyzing skill trends...")
    skill_freq = skill_analyzer.analyze_skill_frequency(df)
    
    # Print top skills by category
    print("\n" + "="*60)
    print("TOP SOFTWARE ENGINEERING SKILLS ANALYSIS")
    print("="*60)
    
    for category, skills in skill_freq.items():
        if skills:
            print(f"\n{category.replace('_', ' ').upper()}:")
            print("-" * 40)
            for skill, percentage in skills[:5]:  # Top 5
                print(f"{skill:20} {percentage:6.1f}%")
    
    # Create visualizations
    logger.info("Creating visualizations...")
    skill_analyzer.create_skill_visualizations(df)
    
    # Generate summary report
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)
    print(f"Total jobs analyzed: {len(df)}")
    print(f"Jobs with salary info: {df['has_salary'].sum()}")
    print(f"Average skills per job: {df['skills_count'].mean():.1f}")
    print(f"Most common job type: {df['job_type'].mode().iloc[0] if not df['job_type'].mode().empty else 'N/A'}")
    
    # Top skill combinations
    skill_combinations = skill_analyzer.analyze_skill_combinations(df, top_n=5)
    if skill_combinations:
        print(f"\nTop skill combinations:")
        for combo, count in skill_combinations:
            print(f"  {', '.join(combo)}: {count} jobs")
    
    logger.info("JobPulse completed successfully!")
    print(f"\nResults saved to: output/ and data/ directories")

if __name__ == "__main__":
    main() 