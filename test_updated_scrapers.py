#!/usr/bin/env python3
"""
Test script to verify that the updated scrapers are now working
and returning real data instead of sample data.
"""

import sys
import os
import asyncio
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dice_scraper():
    """Test the updated Dice scraper"""
    print("🧪 Testing Dice Scraper...")
    try:
        from scrapers.dice_scraper import DiceScraper
        
        scraper = DiceScraper()
        jobs = scraper.search_jobs("python", "United States", limit=5)
        
        if jobs:
            print(f"✅ Dice scraper SUCCESS: Found {len(jobs)} real jobs")
            for i, job in enumerate(jobs[:2]):  # Show first 2 jobs
                print(f"   {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"      Source: {job.get('source', 'N/A')}")
                print(f"      Skills: {job.get('skills', [])}")
                print()
            return True
        else:
            print("❌ Dice scraper FAILED: No jobs returned")
            return False
            
    except Exception as e:
        print(f"❌ Dice scraper ERROR: {e}")
        return False

def test_stackoverflow_scraper():
    """Test the updated Stack Overflow scraper"""
    print("🧪 Testing Stack Overflow Scraper...")
    try:
        from scrapers.stackoverflow_scraper import StackOverflowScraper
        
        scraper = StackOverflowScraper()
        jobs = scraper.search_jobs("python", "United States", limit=5)
        
        if jobs:
            print(f"✅ Stack Overflow scraper SUCCESS: Found {len(jobs)} real jobs")
            for i, job in enumerate(jobs[:2]):  # Show first 2 jobs
                print(f"   {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"      Source: {job.get('source', 'N/A')}")
                print(f"      Skills: {job.get('skills', [])}")
                print()
            return True
        else:
            print("❌ Stack Overflow scraper FAILED: No jobs returned")
            return False
            
    except Exception as e:
        print(f"❌ Stack Overflow scraper ERROR: {e}")
        return False

def test_greenhouse_scraper():
    """Test the new Greenhouse scraper"""
    print("🧪 Testing Greenhouse Scraper...")
    try:
        from scrapers.greenhouse_scraper import GreenhouseScraper
        
        scraper = GreenhouseScraper()
        jobs = scraper.search_jobs("python", "United States", limit=5)
        
        if jobs:
            print(f"✅ Greenhouse scraper SUCCESS: Found {len(jobs)} real jobs")
            for i, job in enumerate(jobs[:2]):  # Show first 2 jobs
                print(f"   {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"      Source: {job.get('source', 'N/A')}")
                print(f"      Skills: {job.get('skills', [])}")
                print()
            return True
        else:
            print("❌ Greenhouse scraper FAILED: No jobs returned")
            return False
            
    except Exception as e:
        print(f"❌ Greenhouse scraper ERROR: {e}")
        return False

def test_lever_scraper():
    """Test the updated Lever scraper"""
    print("🧪 Testing Lever Scraper...")
    try:
        from scrapers.lever_scraper import LeverScraper
        
        scraper = LeverScraper()
        jobs = scraper.search_jobs("python", "United States", limit=5)
        
        if jobs:
            print(f"✅ Lever scraper SUCCESS: Found {len(jobs)} real jobs")
            for i, job in enumerate(jobs[:2]):  # Show first 2 jobs
                print(f"   {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"      Source: {job.get('source', 'N/A')}")
                print(f"      Skills: {job.get('skills', [])}")
                print()
            return True
        else:
            print("❌ Lever scraper FAILED: No jobs returned")
            return False
            
    except Exception as e:
        print(f"❌ Lever scraper ERROR: {e}")
        return False

def test_skills_network_api():
    """Test the skills network API to see if it's using real data"""
    print("🧪 Testing Skills Network API...")
    try:
        import requests
        
        # Test the API endpoint
        response = requests.get("http://localhost:5002/api/skills-network?min_frequency=1&min_co_occurrence=1&use_current_search=false", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            data_source = data.get('data', {}).get('data_source', 'unknown')
            total_jobs = data.get('data', {}).get('total_jobs_analyzed', 0)
            
            print(f"✅ Skills Network API SUCCESS: {data_source}")
            print(f"   Total jobs analyzed: {total_jobs}")
            
            if data_source == 'real_jobs':
                print("   🎉 API is using REAL job data!")
                return True
            else:
                print("   ⚠️ API is still using sample data")
                return False
        else:
            print(f"❌ Skills Network API FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Skills Network API ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Updated JobPulse Scrapers")
    print("=" * 50)
    
    results = []
    
    # Test individual scrapers
    results.append(("Dice Scraper", test_dice_scraper()))
    print()
    
    results.append(("Stack Overflow Scraper", test_stackoverflow_scraper()))
    print()
    
    results.append(("Greenhouse Scraper", test_greenhouse_scraper()))
    print()
    
    results.append(("Lever Scraper", test_lever_scraper()))
    print()
    
    # Test the skills network API
    results.append(("Skills Network API", test_skills_network_api()))
    print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The scrapers are now working correctly.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


