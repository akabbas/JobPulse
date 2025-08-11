#!/usr/bin/env python3
"""
Robust test for Playwright scraper with error handling
"""

import asyncio
import sys
import os
import requests
import time

# Add the scrapers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

from playwright_scraper import PlaywrightJobScraper

def test_network_connectivity():
    """Test basic network connectivity"""
    print("🌐 Testing Network Connectivity...")
    
    test_urls = [
        ("https://httpbin.org/get", "Basic HTTP"),
        ("https://api.github.com", "GitHub API"),
        ("https://remotive.com/api/remote-jobs", "Remotive API"),
    ]
    
    for url, name in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"⚠️  {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")

async def test_playwright_browser():
    """Test Playwright browser functionality"""
    print("\n🤖 Testing Playwright Browser...")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Test a simple page
            await page.goto("https://httpbin.org/get")
            content = await page.content()
            
            if "httpbin" in content.lower():
                print("✅ Playwright browser: Working")
            else:
                print("❌ Playwright browser: Failed to load page")
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Playwright browser test failed: {e}")

async def test_scraper_components():
    """Test individual scraper components"""
    print("\n🔧 Testing Scraper Components...")
    
    scraper = PlaywrightJobScraper()
    
    # Test skills extraction
    test_text = "We need a Python developer with Django and AWS experience"
    skills = scraper._extract_skills_from_text(test_text)
    if skills:
        print(f"✅ Skills extraction: {skills}")
    else:
        print("❌ Skills extraction: Failed")
    
    # Test duplicate removal
    test_jobs = [
        {'title': 'Python Developer', 'company': 'TechCorp'},
        {'title': 'Python Developer', 'company': 'TechCorp'},
        {'title': 'Java Developer', 'company': 'TechCorp'}
    ]
    unique_jobs = scraper._remove_duplicates(test_jobs)
    if len(unique_jobs) == 2:
        print("✅ Duplicate removal: Working")
    else:
        print("❌ Duplicate removal: Failed")

async def test_api_endpoints():
    """Test API endpoints with better error handling"""
    print("\n📡 Testing API Endpoints...")
    
    scraper = PlaywrightJobScraper()
    
    # Test GitHub Jobs with better error handling
    try:
        github_jobs = await scraper.scrape_github_jobs_api()
        print(f"✅ GitHub Jobs API: {len(github_jobs)} jobs")
    except Exception as e:
        print(f"❌ GitHub Jobs API: {e}")
    
    # Test Remotive with better error handling
    try:
        remotive_jobs = await scraper.scrape_remotive_api()
        print(f"✅ Remotive API: {len(remotive_jobs)} jobs")
    except Exception as e:
        print(f"❌ Remotive API: {e}")

async def test_playwright_scraping():
    """Test Playwright scraping of websites"""
    print("\n🌐 Testing Playwright Website Scraping...")
    
    scraper = PlaywrightJobScraper()
    
    try:
        # Initialize browser
        await scraper._init_browser()
        
        # Test a simple website first
        await scraper.page.goto("https://httpbin.org/get")
        content = await scraper.page.content()
        
        if "httpbin" in content.lower():
            print("✅ Playwright navigation: Working")
        else:
            print("❌ Playwright navigation: Failed")
        
        # Clean up
        await scraper._cleanup_browser()
        
    except Exception as e:
        print(f"❌ Playwright scraping test failed: {e}")
        # Try to clean up
        try:
            await scraper._cleanup_browser()
        except:
            pass

async def main():
    """Main test function"""
    print("🧪 Robust Playwright Test Suite")
    print("=" * 40)
    
    # Test network connectivity
    test_network_connectivity()
    
    # Test Playwright browser
    await test_playwright_browser()
    
    # Test scraper components
    await test_scraper_components()
    
    # Test API endpoints
    await test_api_endpoints()
    
    # Test Playwright scraping
    await test_playwright_scraping()
    
    print("\n🎉 Test suite completed!")
    print("Check the results above to see what's working.")

if __name__ == "__main__":
    asyncio.run(main()) 