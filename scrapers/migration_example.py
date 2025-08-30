"""
Migration Example: Using the New Plugin Architecture

This script demonstrates how to migrate from the old hardcoded scraper system
to the new plugin-based architecture.
"""

import logging
from typing import List, Dict, Any
import time

from base_scraper import ScraperType, ScraperError
from scraper_manager import ScraperManager, ScraperManagerFactory
from plugin_config import create_default_plugin_loader, get_scraper_categories


def setup_logging():
    """Setup logging for the migration example"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def demonstrate_old_vs_new_approach():
    """
    Demonstrate the difference between the old and new approaches.
    
    This shows how the new plugin architecture provides better organization,
    error handling, and extensibility.
    """
    print("🔄 MIGRATION EXAMPLE: OLD vs NEW APPROACH")
    print("=" * 60)
    
    # OLD APPROACH (from current app.py)
    print("\n📋 OLD APPROACH (Current app.py):")
    print("-" * 40)
    print("""
# Hardcoded scraper initialization
indeed_scraper = IndeedScraper()
linkedin_scraper = LinkedInScraper()
stackoverflow_scraper = StackOverflowScraper()
# ... many more individual scraper instances

# Manual scraper execution in search_jobs function
if 'enhanced' in sources:
    try:
        enhanced_results = enhanced_scraper.scrape_all_sources(keyword, limit)
        enhanced_jobs = enhanced_results.get('all_sources', [])
        all_jobs.extend(enhanced_jobs)
        successful_sources += 1
    except Exception as e:
        logger.error(f"Error with enhanced scraper: {e}")

if 'api_sources' in sources:
    try:
        api_jobs = api_scraper.search_jobs(keyword, location, limit)
        all_jobs.extend(api_jobs)
        successful_sources += 1
    except Exception as e:
        logger.error(f"Error with API sources: {e}")

# ... repeat for each scraper manually
    """)
    
    # NEW APPROACH (Plugin Architecture)
    print("\n🚀 NEW APPROACH (Plugin Architecture):")
    print("-" * 40)
    print("""
# Centralized scraper management
plugin_loader = create_default_plugin_loader()
scraper_manager = ScraperManagerFactory.create_manager_with_scrapers(
    plugin_loader.load_scrapers()
)

# Single method call handles all scrapers
results = scraper_manager.search_jobs(
    keyword="software engineer",
    location="United States",
    limit=50,
    sources=["enhanced", "api_sources", "reddit"],
    experience_level="senior"
)
    """)
    
    print("\n✨ BENEFITS OF NEW APPROACH:")
    print("-" * 40)
    print("✅ Centralized configuration and management")
    print("✅ Automatic error handling and retry logic")
    print("✅ Parallel execution for better performance")
    print("✅ Easy to add/remove scrapers")
    print("✅ Built-in monitoring and statistics")
    print("✅ Consistent interface across all scrapers")
    print("✅ Better resource management and cleanup")


def demonstrate_plugin_loading():
    """Demonstrate how to load and configure scrapers using the plugin system"""
    print("\n🔌 PLUGIN LOADING DEMONSTRATION")
    print("=" * 60)
    
    try:
        # Create plugin loader
        plugin_loader = create_default_plugin_loader()
        
        print(f"📦 Available scrapers: {len(plugin_loader.configs)}")
        print(f"🔓 Enabled scrapers: {len(plugin_loader.get_enabled_scrapers())}")
        
        # Show scraper categories
        categories = get_scraper_categories()
        print("\n📊 Scraper Categories:")
        for category, scraper_ids in categories.items():
            if scraper_ids:
                print(f"  {category.value.title()}: {', '.join(scraper_ids)}")
        
        # Load a specific scraper
        print("\n🔍 Loading specific scraper (enhanced):")
        enhanced_scraper = plugin_loader.load_scraper("enhanced")
        print(f"  Name: {enhanced_scraper.name}")
        print(f"  Type: {enhanced_scraper.scraper_type.value}")
        print(f"  Priority: {enhanced_scraper.priority}")
        print(f"  Features: {', '.join(enhanced_scraper.get_supported_features())}")
        
        # Load multiple scrapers
        print("\n🔍 Loading multiple scrapers (primary tier):")
        primary_scrapers = plugin_loader.load_scrapers(
            plugin_loader.get_scrapers_by_priority(1)
        )
        for scraper_id, scraper in primary_scrapers.items():
            print(f"  {scraper_id}: {scraper.name} ({scraper.scraper_type.value})")
        
        return plugin_loader, primary_scrapers
        
    except Exception as e:
        print(f"❌ Error loading plugins: {e}")
        return None, None


def demonstrate_scraper_manager(plugin_loader, scrapers):
    """Demonstrate the scraper manager functionality"""
    print("\n🎯 SCRAPER MANAGER DEMONSTRATION")
    print("=" * 60)
    
    if not scrapers:
        print("❌ No scrapers loaded, skipping manager demo")
        return
    
    try:
        # Create scraper manager
        scraper_manager = ScraperManagerFactory.create_manager_with_scrapers(
            list(scrapers.values())
        )
        
        print(f"📊 Manager created with {len(scrapers)} scrapers")
        print(f"🔧 Max workers: {scraper_manager.max_workers}")
        
        # Show registry status
        registry_status = scraper_manager.registry.get_registry_status()
        print(f"\n📈 Registry Status:")
        print(f"  Total scrapers: {registry_status['total_scrapers']}")
        print(f"  Available scrapers: {registry_status['available_scrapers']}")
        print(f"  Scrapers by type: {registry_status['scrapers_by_type']}")
        
        # Show individual scraper statuses
        print(f"\n🔍 Individual Scraper Status:")
        for scraper in scrapers.values():
            status = scraper.get_status()
            print(f"  {status['name']}: {status['status']} (Priority: {status['priority']})")
        
        return scraper_manager
        
    except Exception as e:
        print(f"❌ Error creating scraper manager: {e}")
        return None


def demonstrate_job_search(scraper_manager):
    """Demonstrate a job search using the new architecture"""
    print("\n🔍 JOB SEARCH DEMONSTRATION")
    print("=" * 60)
    
    if not scraper_manager:
        print("❌ No scraper manager available, skipping search demo")
        return
    
    try:
        print("🔍 Executing job search...")
        start_time = time.time()
        
        # Execute search
        results = scraper_manager.search_jobs(
            keyword="python developer",
            location="United States",
            limit=20,
            sources=["enhanced", "api_sources"],  # Use only primary scrapers
            experience_level="all"
        )
        
        search_time = time.time() - start_time
        
        print(f"✅ Search completed in {search_time:.2f}s")
        print(f"📊 Results:")
        print(f"  Total jobs found: {results['total_jobs']}")
        print(f"  Execution stats: {results['execution_stats']}")
        
        # Show scraper results
        print(f"\n🔍 Scraper Results:")
        for result in results['scraper_results']:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['scraper_name']}: {result.get('job_count', 0)} jobs in {result.get('execution_time', 0):.2f}s")
            if not result['success']:
                print(f"    Error: {result.get('error', 'Unknown error')}")
        
        # Show manager status
        manager_status = scraper_manager.get_manager_status()
        print(f"\n📈 Manager Status:")
        print(f"  Total searches: {manager_status['total_searches']}")
        print(f"  Success rate: {manager_status['success_rate']:.1%}")
        print(f"  Average response time: {manager_status['average_response_time']:.2f}s")
        
    except ScraperError as e:
        print(f"❌ Scraper error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def demonstrate_advanced_features(plugin_loader, scraper_manager):
    """Demonstrate advanced features of the plugin architecture"""
    print("\n🚀 ADVANCED FEATURES DEMONSTRATION")
    print("=" * 60)
    
    if not scraper_manager:
        print("❌ No scraper manager available, skipping advanced demo")
        return
    
    try:
        # Demonstrate dynamic scraper management
        print("🔧 Dynamic Scraper Management:")
        
        # Disable a scraper
        plugin_loader.disable_scraper("indeed")
        print("  ✅ Disabled Indeed scraper")
        
        # Enable a scraper
        plugin_loader.enable_scraper("simple")
        print("  ✅ Enabled Simple scraper")
        
        # Update scraper configuration
        plugin_loader.update_scraper_config("linkedin", priority=2)
        print("  ✅ Updated LinkedIn scraper priority to 2")
        
        # Show updated enabled scrapers
        enabled = plugin_loader.get_enabled_scrapers()
        print(f"  📊 Enabled scrapers: {', '.join(enabled)}")
        
        # Demonstrate scraper type filtering
        print(f"\n🔍 Scraper Type Filtering:")
        api_scrapers = plugin_loader.get_scrapers_by_type(ScraperType.API_SCRAPER)
        print(f"  API Scrapers: {', '.join(api_scrapers)}")
        
        web_scrapers = plugin_loader.get_scrapers_by_type(ScraperType.WEB_SCRAPER)
        print(f"  Web Scrapers: {', '.join(web_scrapers)}")
        
        # Demonstrate priority-based filtering
        print(f"\n🔍 Priority-based Filtering:")
        high_priority = plugin_loader.get_scrapers_by_priority(1)
        print(f"  High Priority (1): {', '.join(high_priority)}")
        
        medium_priority = plugin_loader.get_scrapers_by_priority(2)
        print(f"  Medium Priority (2): {', '.join(medium_priority)}")
        
    except Exception as e:
        print(f"❌ Error demonstrating advanced features: {e}")


def cleanup_resources(plugin_loader, scraper_manager):
    """Clean up resources used during the demonstration"""
    print("\n🧹 CLEANING UP RESOURCES")
    print("=" * 60)
    
    try:
        if scraper_manager:
            scraper_manager.cleanup()
            print("✅ Scraper manager cleaned up")
        
        if plugin_loader:
            plugin_loader.cleanup()
            print("✅ Plugin loader cleaned up")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")


def main():
    """Main demonstration function"""
    print("🚀 JOBPULSE PLUGIN ARCHITECTURE MIGRATION DEMONSTRATION")
    print("=" * 80)
    
    # Setup logging
    setup_logging()
    
    # Demonstrate old vs new approach
    demonstrate_old_vs_new_approach()
    
    # Demonstrate plugin loading
    plugin_loader, scrapers = demonstrate_plugin_loading()
    
    # Demonstrate scraper manager
    scraper_manager = demonstrate_scraper_manager(plugin_loader, scrapers)
    
    # Demonstrate job search
    demonstrate_job_search(scraper_manager)
    
    # Demonstrate advanced features
    demonstrate_advanced_features(plugin_loader, scraper_manager)
    
    # Cleanup
    cleanup_resources(plugin_loader, scraper_manager)
    
    print("\n🎉 DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print("\n📚 NEXT STEPS:")
    print("1. Refactor existing scrapers to implement BaseScraper interface")
    print("2. Update app.py to use the new ScraperManager")
    print("3. Test the new architecture with real searches")
    print("4. Gradually migrate all scrapers to the new system")
    print("5. Add new scrapers using the plugin architecture")


if __name__ == "__main__":
    main()
