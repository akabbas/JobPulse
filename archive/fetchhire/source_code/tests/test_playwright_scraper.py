#!/usr/bin/env python3
"""
Test script for Playwright job scraper
"""

import asyncio
import sys
import os

# Add the scrapers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

from playwright_scraper import PlaywrightJobScraper

async def test_playwright_scraper():
    """Test the Playwright scraper"""
    print("🧪 Testing Playwright Job Scraper")
    print("=" * 50)
    
    scraper = PlaywrightJobScraper()
    
    try:
        # Test the scraper
        jobs = await scraper.scrape_all_sources_playwright()
        
        # Save results
        scraper.save_jobs_to_file(jobs, 'playwright_test_results.json')
        
        print(f"\n✅ Test completed successfully!")
        print(f"✅ Total jobs scraped: {len(jobs)}")
        
        return jobs
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(test_playwright_scraper()) 