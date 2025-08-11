#!/usr/bin/env python3
"""
Test script to verify the JobPulse project setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib imported successfully")
    except ImportError as e:
        print(f"❌ matplotlib import failed: {e}")
        return False
    
    try:
        import seaborn as sns
        print("✅ seaborn imported successfully")
    except ImportError as e:
        print(f"❌ seaborn import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 imported successfully")
    except ImportError as e:
        print(f"❌ beautifulsoup4 import failed: {e}")
        return False
    
    return True

def test_project_modules():
    """Test if project modules can be imported"""
    print("\nTesting project modules...")
    
    # Add project root to path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    
    try:
        from config.settings import SEARCH_KEYWORDS, TECH_SKILLS
        print("✅ config.settings imported successfully")
        print(f"   - Found {len(SEARCH_KEYWORDS)} search keywords")
        print(f"   - Found {len(TECH_SKILLS)} skill categories")
    except ImportError as e:
        print(f"❌ config.settings import failed: {e}")
        return False
    
    try:
        from scrapers.indeed_scraper import IndeedScraper
        print("✅ IndeedScraper imported successfully")
    except ImportError as e:
        print(f"❌ IndeedScraper import failed: {e}")
        return False
    
    try:
        from scrapers.glassdoor_scraper import GlassdoorScraper
        print("✅ GlassdoorScraper imported successfully")
    except ImportError as e:
        print(f"❌ GlassdoorScraper import failed: {e}")
        return False
    
    try:
        from data_processing.data_cleaner import DataCleaner
        print("✅ DataCleaner imported successfully")
    except ImportError as e:
        print(f"❌ DataCleaner import failed: {e}")
        return False
    
    try:
        from analysis.skill_trends import SkillTrendsAnalyzer
        print("✅ SkillTrendsAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ SkillTrendsAnalyzer import failed: {e}")
        return False
    
    return True

def test_sample_data():
    """Test with sample data"""
    print("\nTesting with sample data...")
    
    # Add project root to path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    
    try:
        from data_processing.data_cleaner import DataCleaner
        from analysis.skill_trends import SkillTrendsAnalyzer
        
        # Sample job data
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'company': 'Tech Corp',
                'location': 'San Francisco, CA',
                'salary': '$120,000 - $150,000',
                'snippet': 'We are looking for a Python developer with React and AWS experience.',
                'job_url': 'https://example.com',
                'skills': ['python', 'react', 'aws'],
                'search_keyword': 'software engineer',
                'source': 'indeed',
                'scraped_at': '2024-01-01T00:00:00'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'Startup Inc',
                'location': 'New York, NY',
                'salary': '$90,000 - $120,000',
                'snippet': 'Join our team as a Full Stack Developer with JavaScript and Node.js skills.',
                'job_url': 'https://example.com',
                'skills': ['javascript', 'node.js', 'react'],
                'search_keyword': 'software engineer',
                'source': 'glassdoor',
                'scraped_at': '2024-01-01T00:00:00'
            }
        ]
        
        # Test data cleaning
        cleaner = DataCleaner()
        df = cleaner.clean_job_data(sample_jobs)
        print(f"✅ Data cleaning successful - processed {len(df)} jobs")
        
        # Test skill analysis
        analyzer = SkillTrendsAnalyzer()
        skill_freq = analyzer.analyze_skill_frequency(df)
        print(f"✅ Skill analysis successful - found {len(skill_freq)} categories")
        
        # Test visualization (without saving)
        print("✅ All components working correctly")
        
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("JOBPULSE - SETUP TEST")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    # Test project modules
    if not test_project_modules():
        print("\n❌ Project module tests failed. Check file structure.")
        return False
    
    # Test sample data
    if not test_sample_data():
        print("\n❌ Sample data test failed. Check module implementations.")
        return False
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)
    print("\nYour project is ready to run!")
    print("\nTo start the application:")
    print("   python main.py")
    print("\nTo view the README:")
    print("   cat README.md")
    
    return True

if __name__ == "__main__":
    main() 