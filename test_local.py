#!/usr/bin/env python3
"""
Simple test script to verify local environment is working
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        import bs4
        print("✅ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"❌ BeautifulSoup import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import playwright
        print("✅ Playwright imported successfully")
    except ImportError as e:
        print(f"❌ Playwright import failed: {e}")
        return False
    
    return True

def test_scrapers():
    """Test that scraper modules can be imported"""
    print("\n🔍 Testing scraper imports...")
    
    try:
        from scrapers.enhanced_playwright_scraper import EnhancedPlaywrightScraper
        print("✅ Enhanced Playwright Scraper imported successfully")
    except ImportError as e:
        print(f"❌ Enhanced Playwright Scraper import failed: {e}")
        return False
    
    try:
        from scrapers.api_sources_scraper import APISourcesScraper
        print("✅ API Sources Scraper imported successfully")
    except ImportError as e:
        print(f"❌ API Sources Scraper import failed: {e}")
        return False
    
    return True

def test_app_import():
    """Test that the main app can be imported"""
    print("\n🔍 Testing app import...")
    
    try:
        # Add the parent directory to the path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Try to import the app
        from web_dashboard.app import app
        print("✅ Flask app imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Flask app import failed with error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing JobPulse Local Environment...\n")
    
    # Test basic imports
    if not test_imports():
        print("\n❌ Basic imports failed. Please check your virtual environment.")
        return False
    
    # Test scraper imports
    if not test_scrapers():
        print("\n❌ Scraper imports failed. Please check your scraper files.")
        return False
    
    # Test app import
    if not test_app_import():
        print("\n❌ App import failed. Please check your app.py file.")
        return False
    
    print("\n🎉 All tests passed! Your local environment is ready.")
    print("\n🚀 To start the development server:")
    print("   cd web_dashboard")
    print("   source ../venv/bin/activate")
    print("   python app.py")
    print("\n🌐 Then open your browser to: http://localhost:5001")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
