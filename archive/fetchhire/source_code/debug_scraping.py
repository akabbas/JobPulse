#!/usr/bin/env python3
"""
Debug script for testing scrapers
"""
from database.snowflake_manager import FetchHireSnowflakeManager
from scrapers.playwright_scraper_working import WorkingPlaywrightScraper
import asyncio
import json

async def main():
    print("🚀 FetchHire Debug Scraping Test")
    print("=" * 50)
    
    # Test database connection
    print("🔧 Testing database connection...")
    sf_manager = FetchHireSnowflakeManager()
    
    if not sf_manager.connect_connector():
        print("❌ Failed to connect to Snowflake")
        return
    
    print("✅ Connected to Snowflake")
    
    # Test scraping
    print("🔍 Testing scraper...")
    scraper = WorkingPlaywrightScraper()
    jobs = await scraper.scrape_all_sources()
    
    print(f"✅ Scraped {len(jobs)} jobs")
    print("Sample job:", json.dumps(jobs[0], indent=2) if jobs else "No jobs")
    
    # Test storing a single job
    if jobs:
        test_job = jobs[0]
        print(f"Testing storage of job: {test_job['title']}")
        
        # Check if job exists
        check_query = "SELECT COUNT(*) FROM JOB_POSTINGS WHERE job_id = %s"
        result = sf_manager.execute_query(check_query, [test_job['job_id']])
        print(f"Job exists: {result[0][0] if result else 'No result'}")
        
        if result and result[0][0] == 0:
            # Insert job
            insert_query = """
            INSERT INTO JOB_POSTINGS (
                job_id, title, company, location, salary, 
                source, source_url, posted_date, tags, description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            tags_str = ','.join(test_job.get('tags', [])) if test_job.get('tags') else ''
            description = f"Job from {test_job['source']}"
            
            params = [
                test_job['job_id'],
                test_job['title'],
                test_job['company'],
                test_job['location'],
                test_job.get('salary'),
                test_job['source'],
                test_job.get('source_url'),
                test_job['posted_date'],
                tags_str,
                description
            ]
            
            print("Inserting with params:", params)
            
            try:
                sf_manager.execute_query(insert_query, params)
                print("✅ Job inserted successfully!")
                
                # Verify insertion
                verify_query = "SELECT COUNT(*) FROM JOB_POSTINGS WHERE job_id = %s"
                verify_result = sf_manager.execute_query(verify_query, [test_job['job_id']])
                print(f"Verification: {verify_result[0][0] if verify_result else 'No result'} jobs found")
                
            except Exception as e:
                print(f"❌ Error inserting job: {e}")
        else:
            print("Job already exists")
    
    sf_manager.close()

if __name__ == "__main__":
    asyncio.run(main()) 