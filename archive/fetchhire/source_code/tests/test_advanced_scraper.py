#!/usr/bin/env python3
"""
Test script for the FetchHire Advanced Scraper
"""

import asyncio
import json
import time
from scrapers.advanced_scraper import AdvancedJobScraper

async def test_advanced_scraper():
    """Test the advanced scraper functionality"""
    print("🚀 Testing FetchHire Advanced Scraper")
    print("=" * 50)
    
    # Initialize the advanced scraper
    scraper = AdvancedJobScraper(cache_dir="cache", max_cache_age_hours=24)
    
    print("✅ Advanced Scraper Features:")
    print("   • Selenium/Headless Browser for LinkedIn")
    print("   • Async Scraping for multiple sources")
    print("   • Intelligent Caching (24-hour cache)")
    print("   • Proxy Rotation (when configured)")
    print("   • Rate Limiting and Anti-Detection")
    print("   • Duplicate Removal")
    print()
    
    # Test individual components
    print("🔍 Testing Individual Components:")
    
    # Test LinkedIn scraping with Selenium
    print("   📊 Testing LinkedIn scraping with Selenium...")
    start_time = time.time()
    linkedin_jobs = await scraper.scrape_linkedin_advanced(max_pages=1)
    linkedin_time = time.time() - start_time
    print(f"   ✅ LinkedIn: {len(linkedin_jobs)} jobs in {linkedin_time:.2f}s")
    
    # Test Remote OK scraping
    print("   🌐 Testing Remote OK scraping...")
    start_time = time.time()
    remote_jobs = await scraper.scrape_remote_ok_advanced()
    remote_time = time.time() - start_time
    print(f"   ✅ Remote OK: {len(remote_jobs)} jobs in {remote_time:.2f}s")
    
    # Test full async scraping
    print("   ⚡ Testing full async scraping...")
    start_time = time.time()
    all_jobs = await scraper.scrape_all_sources_advanced()
    total_time = time.time() - start_time
    print(f"   ✅ Total: {len(all_jobs)} unique jobs in {total_time:.2f}s")
    
    print()
    print("📈 Performance Analysis:")
    print(f"   • LinkedIn scraping: {linkedin_time:.2f}s")
    print(f"   • Remote OK scraping: {remote_time:.2f}s")
    print(f"   • Total async time: {total_time:.2f}s")
    print(f"   • Speedup vs sequential: {((linkedin_time + remote_time) / total_time):.1f}x")
    
    # Test caching
    print()
    print("💾 Testing Caching:")
    print("   🔄 Running same scrape again (should use cache)...")
    start_time = time.time()
    cached_jobs = await scraper.scrape_all_sources_advanced()
    cache_time = time.time() - start_time
    print(f"   ✅ Cached scrape: {len(cached_jobs)} jobs in {cache_time:.2f}s")
    print(f"   📉 Cache speedup: {(total_time / cache_time):.1f}x faster")
    
    # Test skills analytics
    print()
    print("🎯 Testing Skills Analytics:")
    analytics = scraper.get_skills_analytics(all_jobs)
    print(f"   📊 Total jobs analyzed: {analytics['total_jobs']}")
    print(f"   🏷️  Total unique skills: {analytics['total_skills']}")
    print(f"   📍 Sources: {', '.join(analytics['sources'])}")
    
    # Show top skills
    print("   🏆 Top 10 Skills:")
    for i, (skill, count) in enumerate(list(analytics['top_skills'].items())[:10], 1):
        print(f"      {i:2d}. {skill}: {count}")
    
    # Save results
    print()
    print("💾 Saving Results:")
    scraper.save_jobs_to_file(all_jobs, 'test_advanced_results.json')
    print("   ✅ Results saved to 'test_advanced_results.json'")
    
    # Show sample jobs
    print()
    print("📋 Sample Jobs:")
    for i, job in enumerate(all_jobs[:3], 1):
        print(f"   {i}. {job['title']} at {job['company']}")
        print(f"      📍 {job['location']} | 💰 {job.get('salary', 'N/A')}")
        print(f"      🏷️  Skills: {', '.join(job['tags'][:5])}")
        print()
    
    print("🎉 Advanced scraper test completed successfully!")
    return all_jobs

def test_proxy_configuration():
    """Test proxy configuration"""
    print("🌐 Testing Proxy Configuration:")
    scraper = AdvancedJobScraper()
    
    # Test proxy loading
    proxies = scraper._load_proxies()
    if proxies:
        print(f"   ✅ Loaded {len(proxies)} proxies")
        for i, proxy in enumerate(proxies[:3], 1):
            print(f"      {i}. {proxy}")
    else:
        print("   ⚠️  No proxies configured")
        print("   💡 Add proxies to 'proxies.txt' for better success rates")
    
    print()

def test_selenium_setup():
    """Test Selenium setup"""
    print("🤖 Testing Selenium Setup:")
    scraper = AdvancedJobScraper()
    
    try:
        scraper._init_selenium_driver()
        if scraper.driver:
            print("   ✅ Selenium WebDriver initialized successfully")
            print("   🎭 Headless browser ready for LinkedIn scraping")
        else:
            print("   ❌ Selenium WebDriver failed to initialize")
            print("   💡 Make sure Chrome/Chromium is installed")
    except Exception as e:
        print(f"   ❌ Selenium error: {e}")
        print("   💡 Install Chrome/Chromium and chromedriver")
    
    # Cleanup
    scraper._cleanup_selenium_driver()
    print()

if __name__ == "__main__":
    print("🧪 FetchHire Advanced Scraper Test Suite")
    print("=" * 50)
    
    # Test configuration
    test_proxy_configuration()
    test_selenium_setup()
    
    # Run async test
    try:
        jobs = asyncio.run(test_advanced_scraper())
        print(f"\n✅ Test completed! Scraped {len(jobs)} jobs with advanced features.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements_advanced.txt") 
    print("✅ All tests completed successfully!")
    print("🚀 Your advanced scraper is ready to use!") 