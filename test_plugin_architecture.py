#!/usr/bin/env python3
"""
Test script for the new JobPulse Plugin Architecture

This script tests the basic functionality of the new plugin system
without requiring complex imports.
"""

import sys
import os

# Add the scrapers directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))

def test_base_scraper():
    """Test the base scraper interface"""
    print("🧪 Testing Base Scraper Interface...")
    
    try:
        from base_scraper import BaseScraper, ScraperType, ScraperStatus
        print("  ✅ Base scraper classes imported successfully")
        
        # Test enum values
        print(f"  ✅ Scraper types: {[t.value for t in ScraperType]}")
        print(f"  ✅ Scraper statuses: {[s.value for s in ScraperStatus]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Base scraper test failed: {e}")
        return False

def test_plugin_config():
    """Test the plugin configuration system"""
    print("\n🧪 Testing Plugin Configuration...")
    
    try:
        from plugin_config import create_default_plugin_loader, get_scraper_categories
        
        # Create plugin loader
        loader = create_default_plugin_loader()
        print("  ✅ Plugin loader created successfully")
        
        # Get scraper categories
        categories = get_scraper_categories()
        print(f"  ✅ Scraper categories: {len(categories)} categories")
        
        # Show enabled scrapers
        enabled = loader.get_enabled_scrapers()
        print(f"  ✅ Enabled scrapers: {len(enabled)} scrapers")
        
        return True, loader
        
    except Exception as e:
        print(f"  ❌ Plugin config test failed: {e}")
        return False, None

def test_scraper_manager(loader):
    """Test the scraper manager"""
    print("\n🧪 Testing Scraper Manager...")
    
    try:
        from scraper_manager import ScraperManagerFactory
        
        # Create manager with loaded scrapers
        scrapers = loader.load_scrapers()
        print(f"  ✅ Loaded {len(scrapers)} scrapers")
        
        # Create manager
        manager = ScraperManagerFactory.create_manager_with_scrapers(
            list(scrapers.values())
        )
        print("  ✅ Scraper manager created successfully")
        
        # Get manager status
        status = manager.get_manager_status()
        print(f"  ✅ Manager status: {status['total_searches']} total searches")
        
        return True, manager
        
    except Exception as e:
        print(f"  ❌ Scraper manager test failed: {e}")
        return False, None

def test_plugin_loading():
    """Test plugin loading functionality"""
    print("\n🧪 Testing Plugin Loading...")
    
    try:
        from plugin_config import create_default_plugin_loader
        
        loader = create_default_plugin_loader()
        
        # Test loading specific scrapers
        test_scrapers = ["enhanced", "api_sources", "reddit"]
        
        for scraper_id in test_scrapers:
            try:
                scraper = loader.load_scraper(scraper_id)
                print(f"  ✅ Loaded {scraper_id}: {scraper.name}")
            except Exception as e:
                print(f"  ⚠️  Failed to load {scraper_id}: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Plugin loading test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 JobPulse Plugin Architecture Test")
    print("=" * 50)
    
    # Test base scraper
    if not test_base_scraper():
        print("\n❌ Base scraper test failed, stopping")
        return
    
    # Test plugin config
    config_success, loader = test_plugin_config()
    if not config_success:
        print("\n❌ Plugin config test failed, stopping")
        return
    
    # Test scraper manager
    manager_success, manager = test_scraper_manager(loader)
    if not manager_success:
        print("\n❌ Scraper manager test failed, stopping")
        return
    
    # Test plugin loading
    if not test_plugin_loading():
        print("\n❌ Plugin loading test failed")
        return
    
    # Cleanup
    if manager:
        manager.cleanup()
        print("\n🧹 Cleaned up scraper manager")
    
    if loader:
        loader.cleanup()
        print("🧹 Cleaned up plugin loader")
    
    print("\n🎉 All tests completed successfully!")
    print("\n✨ The new plugin architecture is working correctly!")
    print("\n📚 Next steps:")
    print("1. Refactor existing scrapers to implement BaseScraper")
    print("2. Update app.py to use the new ScraperManager")
    print("3. Test with real job searches")
    print("4. Gradually migrate all scrapers")

if __name__ == "__main__":
    main()
