#!/usr/bin/env python3
"""
Test script to verify the enhanced scraper can dynamically identify and use all Playwright-capable scrapers
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_enhanced_scraper():
    """Test the enhanced scraper's dynamic scraper detection"""
    try:
        print("🚀 Testing Enhanced Playwright Scraper...")
        print("=" * 60)
        
        # Import the enhanced scraper
        from scrapers.enhanced_playwright_scraper import EnhancedPlaywrightScraper
        
        # Create scraper instance
        scraper = EnhancedPlaywrightScraper(headless=True)
        print("✅ Enhanced scraper instance created")
        
        # Test dynamic scraper detection
        print("\n🔍 Testing dynamic scraper detection...")
        playwright_scrapers = scraper._get_playwright_scrapers()
        
        print(f"\n📊 Found {len(playwright_scrapers)} Playwright-capable scrapers:")
        for name, scraper_instance in playwright_scrapers.items():
            capabilities = []
            if hasattr(scraper_instance, '_search_with_playwright'):
                capabilities.append("Playwright")
            if hasattr(scraper_instance, 'scrape_jobs'):
                capabilities.append("Standard")
            if name.endswith('_enhanced'):
                capabilities.append("Enhanced")
            
            print(f"  📋 {name}: {', '.join(capabilities)}")
        
        # Test a small scraping operation
        print(f"\n🚀 Testing comprehensive scraping with keyword 'python developer'...")
        print("This will attempt to use ALL available scrapers...")
        
        start_time = datetime.now()
        results = await scraper.scrape_all_sources("python developer", limit=10)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n⏱️  Scraping completed in {duration:.2f} seconds")
        print(f"📊 Results summary:")
        
        total_jobs = 0
        successful_sources = 0
        
        for source, jobs in results.items():
            if source != 'all_sources':
                if jobs:
                    successful_sources += 1
                    total_jobs += len(jobs)
                    print(f"  ✅ {source}: {len(jobs)} jobs")
                else:
                    print(f"  ❌ {source}: 0 jobs")
        
        print(f"\n🎯 Final Results:")
        print(f"  📈 Successful sources: {successful_sources}/{len(playwright_scrapers)}")
        print(f"  💼 Total jobs found: {total_jobs}")
        print(f"  🔄 Unique jobs: {len(results.get('all_sources', []))}")
        
        # Save results for inspection
        output_file = f"enhanced_scraper_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Cleanup
        await scraper.cleanup()
        print("\n🧹 Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Enhanced Scraper Test Suite")
    print("=" * 60)
    
    try:
        # Run the async test
        success = asyncio.run(test_enhanced_scraper())
        
        if success:
            print("\n🎉 All tests passed! Enhanced scraper is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
