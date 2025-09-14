#!/usr/bin/env python3
"""
Test script for new Greenhouse and Lever scrapers
Tests that they work without 403 errors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.greenhouse_scraper import GreenhouseScraper
from scrapers.lever_scraper import LeverScraper

def test_greenhouse_scraper():
    """Test Greenhouse scraper"""
    print("🌱 Testing Greenhouse Scraper...")
    
    try:
        scraper = GreenhouseScraper()
        
        # Test getting companies
        print("  - Getting companies...")
        companies = scraper.get_companies()
        print(f"    ✅ Found {len(companies)} companies")
        
        # Test job search
        print("  - Searching for 'Python Developer' jobs...")
        jobs = scraper.search_jobs('Python Developer', limit=5)
        print(f"    ✅ Found {len(jobs)} jobs")
        
        if jobs:
            print("    📋 Sample job:")
            job = jobs[0]
            print(f"      Title: {job.get('title', 'N/A')}")
            print(f"      Company: {job.get('company', 'N/A')}")
            print(f"      Location: {job.get('location', 'N/A')}")
            print(f"      Source: {job.get('source', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_lever_scraper():
    """Test Lever scraper"""
    print("🔗 Testing Lever Scraper...")
    
    try:
        scraper = LeverScraper()
        
        # Test job search
        print("  - Searching for 'Software Engineer' jobs...")
        jobs = scraper.search_jobs('Software Engineer', limit=5)
        print(f"    ✅ Found {len(jobs)} jobs")
        
        if jobs:
            print("    📋 Sample job:")
            job = jobs[0]
            print(f"      Title: {job.get('title', 'N/A')}")
            print(f"      Company: {job.get('company', 'N/A')}")
            print(f"      Location: {job.get('location', 'N/A')}")
            print(f"      Source: {job.get('source', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing New Job Sources (Greenhouse & Lever)")
    print("=" * 50)
    
    greenhouse_success = test_greenhouse_scraper()
    print()
    
    lever_success = test_lever_scraper()
    print()
    
    print("=" * 50)
    print("📊 Test Results:")
    print(f"  Greenhouse: {'✅ PASS' if greenhouse_success else '❌ FAIL'}")
    print(f"  Lever: {'✅ PASS' if lever_success else '❌ PASS'}")
    
    if greenhouse_success and lever_success:
        print("\n🎉 All new scrapers are working correctly!")
        print("   No 403 errors encountered - using API-based approach")
    else:
        print("\n⚠️  Some scrapers failed. Check the errors above.")
    
    return greenhouse_success and lever_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)








