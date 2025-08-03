#!/usr/bin/env python3
"""
Comprehensive Test Script for Enhanced Job Market Analytics
Tests all new functionality: multiple scrapers, search engine, Flask app, and database integration
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all new modules can be imported"""
    print("Testing imports...")
    
    try:
        from scrapers.linkedin_scraper import LinkedInScraper
        print("✅ LinkedInScraper imported successfully")
    except ImportError as e:
        print(f"❌ LinkedInScraper import failed: {e}")
        return False
    
    try:
        from scrapers.stackoverflow_scraper import StackOverflowScraper
        print("✅ StackOverflowScraper imported successfully")
    except ImportError as e:
        print(f"❌ StackOverflowScraper import failed: {e}")
        return False
    
    try:
        from search_engine import SearchCriteria, filter_jobs
        print("✅ SearchEngine imported successfully")
    except ImportError as e:
        print(f"❌ SearchEngine import failed: {e}")
        return False
    
    try:
        from database.db_manager import DatabaseManager
        print("✅ DatabaseManager imported successfully")
    except ImportError as e:
        print(f"❌ DatabaseManager import failed: {e}")
        return False
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    return True

def test_scrapers():
    """Test the new scrapers with sample data"""
    print("\nTesting scrapers...")
    
    try:
        from scrapers.linkedin_scraper import LinkedInScraper
        from scrapers.stackoverflow_scraper import StackOverflowScraper
        
        # Test LinkedIn scraper
        linkedin_scraper = LinkedInScraper()
        linkedin_jobs = linkedin_scraper.search_jobs("python developer", limit=2)
        print(f"✅ LinkedIn scraper returned {len(linkedin_jobs)} jobs")
        
        # Test Stack Overflow scraper
        stackoverflow_scraper = StackOverflowScraper()
        stackoverflow_jobs = stackoverflow_scraper.search_jobs("python developer", limit=2)
        print(f"✅ Stack Overflow scraper returned {len(stackoverflow_jobs)} jobs")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def test_search_engine():
    """Test the search engine functionality"""
    print("\nTesting search engine...")
    
    try:
        from search_engine import SearchCriteria, filter_jobs
        
        # Sample job data
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'company': 'Tech Corp',
                'location': 'San Francisco, CA',
                'salary': '$120,000 - $150,000',
                'skills': ['python', 'react', 'aws'],
                'salary_min': 120000,
                'salary_max': 150000
            },
            {
                'title': 'Junior JavaScript Developer',
                'company': 'Startup Inc',
                'location': 'New York, NY',
                'salary': '$60,000 - $80,000',
                'skills': ['javascript', 'react', 'node.js'],
                'salary_min': 60000,
                'salary_max': 80000
            }
        ]
        
        # Test filtering by skills
        criteria = SearchCriteria(
            keywords=['python'],
            skills_required=['python'],
            salary_min=100000
        )
        
        filtered_jobs = filter_jobs(sample_jobs, criteria)
        print(f"✅ Search engine filtered {len(filtered_jobs)} jobs from {len(sample_jobs)} total")
        
        return True
        
    except Exception as e:
        print(f"❌ Search engine test failed: {e}")
        return False

def test_data_processing():
    """Test data processing with new scrapers"""
    print("\nTesting data processing...")
    
    try:
        from scrapers.linkedin_scraper import LinkedInScraper
        from data_processing.data_cleaner import DataCleaner
        
        # Get sample data from LinkedIn
        linkedin_scraper = LinkedInScraper()
        jobs = linkedin_scraper.search_jobs("software engineer", limit=3)
        
        if jobs:
            # Test data cleaning
            cleaner = DataCleaner()
            df = cleaner.clean_job_data(jobs)
            print(f"✅ Data processing successful - processed {len(df)} jobs")
            return True
        else:
            print("⚠️ No jobs found for data processing test")
            return True
            
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization"""
    print("\nTesting Flask app...")
    
    try:
        from web_dashboard.app import app
        
        # Test that app can be created
        with app.test_client() as client:
            response = client.get('/')
            print("✅ Flask app created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_database_integration():
    """Test database integration (without actual database)"""
    print("\nTesting database integration...")
    
    try:
        from database.db_manager import DatabaseManager
        
        # Test database manager creation (without actual connection)
        db_manager = DatabaseManager('sqlite:///test.db')
        print("✅ Database manager created successfully")
        
        # Test model creation
        from database.db_manager import JobPosting
        print("✅ JobPosting model created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

def test_enhanced_main():
    """Test the enhanced main application"""
    print("\nTesting enhanced main application...")
    
    try:
        # Import the enhanced main module
        import main_enhanced
        print("✅ Enhanced main application imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced main application test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ENHANCED JOB MARKET ANALYTICS - COMPREHENSIVE TEST")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Scraper Tests", test_scrapers),
        ("Search Engine Tests", test_search_engine),
        ("Data Processing Tests", test_data_processing),
        ("Flask App Tests", test_flask_app),
        ("Database Integration Tests", test_database_integration),
        ("Enhanced Main Tests", test_enhanced_main)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\nYour enhanced job market analytics project is ready!")
        print("\nTo run the enhanced application:")
        print("   python main_enhanced.py")
        print("\nTo run the Flask dashboard:")
        print("   cd web_dashboard && python app.py")
        print("\nTo test with database:")
        print("   # Set DATABASE_URL environment variable")
        print("   # Then run: python main_enhanced.py")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main() 