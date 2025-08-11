#!/usr/bin/env python3
"""Test the enhanced Playwright scraper"""

import asyncio
import sys
import os

# Add scrapers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

from enhanced_playwright_scraper import EnhancedPlaywrightScraper

async def test_enhanced_scraper():
    """Test the enhanced scraper"""
    print("🧪 Testing Enhanced Playwright Scraper...")
    
    try:
        # Initialize scraper
        scraper = EnhancedPlaywrightScraper(headless=True)
        
        # Test scraping
        print("🚀 Starting test scrape...")
        results = await scraper.scrape_all_sources("Python Developer", 5)
        
        # Display results
        print(f"\n✅ Scraping completed successfully!")
        print(f"📊 Results:")
        for source, jobs in results.items():
            if source != 'all_sources':
                print(f"   {source}: {len(jobs)} jobs")
        
        print(f"🎯 Total unique jobs: {len(results['all_sources'])}")
        
        # Save results
        scraper.save_jobs_to_file(results['all_sources'], 'test_results.json')
        print("💾 Results saved to test_results.json")
        
        # Show sample job data
        if results['all_sources']:
            print(f"\n📋 Sample job data:")
            sample_job = results['all_sources'][0]
            print(f"   Title: {sample_job.get('title', 'N/A')}")
            print(f"   Company: {sample_job.get('company', 'N/A')}")
            print(f"   Source: {sample_job.get('source', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_scraper())
    sys.exit(0 if success else 1)
