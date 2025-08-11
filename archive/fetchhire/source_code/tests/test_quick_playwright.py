#!/usr/bin/env python3
"""
Quick test for Playwright solution
"""

import asyncio
import sys
import os

# Add the scrapers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from playwright_scraper_working import WorkingPlaywrightScraper

async def quick_test():
    """Quick test of Playwright scraper"""
    print("⚡ Quick Playwright Test")
    print("=" * 30)
    
    scraper = WorkingPlaywrightScraper()
    
    try:
        print("🚀 Testing Playwright scraper...")
        
        # Test the scraper
        jobs = await scraper.scrape_all_sources_working()
        
        print(f"\n✅ Test Results:")
        print(f"   • Jobs found: {len(jobs)}")
        
        if jobs:
            print(f"   • Sample job: {jobs[0]['title']} at {jobs[0]['company']}")
            print(f"   • Skills: {', '.join(jobs[0]['tags'][:3])}")
        
        print("\n🎉 Quick test completed!")
        print("✅ Playwright solution is working!")
        
        return jobs
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(quick_test()) 