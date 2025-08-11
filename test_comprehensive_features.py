#!/usr/bin/env python3
"""Comprehensive test of all enhanced scraper features"""

import asyncio
import sys
import os
import json

# Add scrapers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

from enhanced_playwright_scraper import EnhancedPlaywrightScraper

async def test_all_features():
    """Test all enhanced scraper features"""
    print("🧪 Testing All Enhanced Scraper Features")
    print("=" * 50)
    
    try:
        # Initialize scraper
        scraper = EnhancedPlaywrightScraper(headless=True)
        
        # Test 1: Skills Extraction
        print("\n🔍 Test 1: Skills Extraction")
        sample_text = """
        We're looking for a Python Developer with React experience.
        Must know Django, Flask, PostgreSQL, and AWS.
        Experience with Docker, Kubernetes, and CI/CD pipelines.
        Knowledge of Agile, Scrum, and TDD methodologies.
        """
        skills = scraper._extract_skills_from_text(sample_text)
        print(f"   Extracted skills: {', '.join(skills)}")
        
        # Test 2: Individual Source Scraping
        print("\n🌐 Test 2: Individual Source Scraping")
        
        # Test Remotive API (most reliable)
        print("   Testing Remotive API...")
        remotive_jobs = await scraper.scrape_remotive_api("Python", 3)
        print(f"   Remotive: {len(remotive_jobs)} jobs found")
        
        # Test 3: Concurrent Scraping
        print("\n⚡ Test 3: Concurrent Scraping")
        print("   Starting concurrent scrape for 'Developer'...")
        all_results = await scraper.scrape_all_sources("Developer", 3)
        
        # Display results
        print(f"\n📊 Final Results:")
        for source, jobs in all_results.items():
            if source != 'all_sources':
                print(f"   {source}: {len(jobs)} jobs")
        
        print(f"🎯 Total unique jobs (after deduplication): {len(all_results['all_sources'])}")
        
        # Test 4: Duplicate Removal
        print("\n🔄 Test 4: Duplicate Removal")
        print(f"   Jobs before deduplication: {sum(len(jobs) for source, jobs in all_results.items() if source != 'all_sources')}")
        print(f"   Jobs after deduplication: {len(all_results['all_sources'])}")
        
        # Test 5: Data Quality
        print("\n📋 Test 5: Data Quality")
        if all_results['all_sources']:
            sample_job = all_results['all_sources'][0]
            print(f"   Sample job structure:")
            for key, value in sample_job.items():
                if key == 'description' and value:
                    print(f"     {key}: {str(value)[:100]}...")
                else:
                    print(f"     {key}: {value}")
        
        # Test 6: Save Results
        print("\n💾 Test 6: Save Results")
        filename = 'comprehensive_test_results.json'
        scraper.save_jobs_to_file(all_results['all_sources'], filename)
        print(f"   Results saved to {filename}")
        
        # Test 7: Skills Analysis
        print("\n🎯 Test 7: Skills Analysis")
        all_skills = set()
        for job in all_results['all_sources']:
            if 'tags' in job and job['tags']:
                all_skills.update(job['tags'])
            if 'description' in job and job['description']:
                job_skills = scraper._extract_skills_from_text(job['description'])
                all_skills.update(job_skills)
        
        print(f"   Total unique skills found: {len(all_skills)}")
        print(f"   Skills: {', '.join(sorted(list(all_skills))[:10])}{'...' if len(all_skills) > 10 else ''}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_all_features())
    sys.exit(0 if success else 1)
