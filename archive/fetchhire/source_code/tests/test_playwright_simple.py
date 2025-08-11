#!/usr/bin/env python3
"""
Simple test for Playwright scraper
"""

import asyncio
import sys
import os

# Add the scrapers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

from playwright_scraper import PlaywrightJobScraper

async def simple_test():
    """Simple test of the Playwright scraper"""
    print("🧪 Simple Playwright Test")
    print("=" * 30)
    
    scraper = PlaywrightJobScraper()
    
    try:
        print("🚀 Testing Playwright scraper...")
        
        # Test just the APIs first (faster)
        print("\n📡 Testing Free APIs...")
        
        # Test GitHub Jobs API
        github_jobs = await scraper.scrape_github_jobs_api()
        print(f"✅ GitHub Jobs: {len(github_jobs)} jobs")
        
        # Test Remotive API
        remotive_jobs = await scraper.scrape_remotive_api()
        print(f"✅ Remotive: {len(remotive_jobs)} jobs")
        
        # Combine results
        all_jobs = github_jobs + remotive_jobs
        unique_jobs = scraper._remove_duplicates(all_jobs)
        
        print(f"\n🎉 API Test Results:")
        print(f"✅ Total unique jobs: {len(unique_jobs)}")
        
        # Save results
        scraper.save_jobs_to_file(unique_jobs, 'simple_test_results.json')
        
        # Show sample jobs
        if unique_jobs:
            print("\n📋 Sample Jobs:")
            for i, job in enumerate(unique_jobs[:3], 1):
                print(f"   {i}. {job['title']} at {job['company']}")
                print(f"      📍 {job['location']}")
                print(f"      🏷️  Skills: {', '.join(job['tags'][:3])}")
                print()
        
        return unique_jobs
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    asyncio.run(simple_test()) 