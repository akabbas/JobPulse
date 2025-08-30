"""
JobPulse Scrapers Package

This package contains all the job scraping functionality for JobPulse,
including the new plugin architecture and legacy scrapers.
"""

# New Plugin Architecture
from .base_scraper import (
    BaseScraper,
    ScraperType,
    ScraperStatus,
    ScraperError,
    ScraperRegistry
)

from .scraper_manager import (
    ScraperManager,
    ScraperManagerFactory
)

from .plugin_config import (
    ScraperConfig,
    ScraperCategory,
    PluginLoader,
    create_default_plugin_loader,
    create_custom_plugin_loader,
    get_scraper_categories,
    DEFAULT_SCRAPER_CONFIGS
)

# Legacy scrapers (for backward compatibility)
try:
    from .indeed_scraper import IndeedScraper
    from .linkedin_scraper import LinkedInScraper
    from .stackoverflow_scraper import StackOverflowScraper
    from .dice_scraper import DiceScraper
    from .remoteok_scraper import RemoteOKScraper
    from .weworkremotely_scraper import WeWorkRemotelyScraper
    from .simple_jobs_scraper import SimpleJobsScraper
    from .api_sources_scraper import APISourcesScraper
    from .reddit_scraper import RedditScraper
    from .enhanced_playwright_scraper import EnhancedPlaywrightScraper
    from .jobspresso_scraper import JobspressoScraper
    from .yc_jobs_scraper import YCJobsScraper
    from .authentic_jobs_scraper import AuthenticJobsScraper
    from .otta_scraper import OttaScraper
    from .hackernews_scraper import HackerNewsScraper
    from .himalayas_scraper import HimalayasScraper
    from .lever_scraper import LeverScraper
    from .google_jobs_scraper import GoogleJobsScraper
    from .greenhouse_scraper import GreenhouseScraper
    from .robust_scraper import RobustScraper
    from .glassdoor_scraper import GlassdoorScraper
except ImportError as e:
    # Some scrapers might not be available
    pass

# Version information
__version__ = "2.0.0"
__author__ = "JobPulse Team"

# Package-level documentation
__doc__ = """
JobPulse Scrapers Package v2.0.0

This package provides a comprehensive job scraping solution with:

🔌 Plugin Architecture:
- BaseScraper: Abstract base class for all scrapers
- ScraperManager: Coordinates multiple scrapers
- PluginLoader: Dynamic scraper loading and configuration

📊 Scraper Types:
- WEB_SCRAPER: Traditional web scraping
- API_SCRAPER: API-based scrapers
- PLAYWRIGHT_SCRAPER: Playwright-based scrapers
- ENHANCED_SCRAPER: Anti-detection scrapers
- FALLBACK_SCRAPER: Fallback/mock data scrapers

🚀 Key Features:
- Parallel execution with configurable workers
- Automatic error handling and retry logic
- Comprehensive monitoring and statistics
- Easy configuration and customization
- Automatic resource management

📚 Quick Start:
    from scrapers import create_default_plugin_loader, ScraperManagerFactory
    
    # Load all configured scrapers
    loader = create_default_plugin_loader()
    scrapers = loader.load_scrapers()
    
    # Create manager
    manager = ScraperManagerFactory.create_manager_with_scrapers(
        list(scrapers.values())
    )
    
    # Execute search
    results = manager.search_jobs(
        keyword="software engineer",
        location="United States",
        limit=50
    )

For more information, see README_PLUGIN_ARCHITECTURE.md
"""

# Convenience functions for easy access
def create_scraper_manager(max_workers: int = 5):
    """
    Create a scraper manager with default configuration.
    
    Args:
        max_workers: Maximum number of concurrent workers
        
    Returns:
        Configured ScraperManager instance
    """
    loader = create_default_plugin_loader()
    scrapers = loader.load_scrapers()
    return ScraperManagerFactory.create_manager_with_scrapers(
        list(scrapers.values()),
        max_workers=max_workers
    )


def get_available_scrapers():
    """
    Get list of available scraper IDs.
    
    Returns:
        List of scraper IDs that can be loaded
    """
    loader = create_default_plugin_loader()
    return loader.get_enabled_scrapers()


def get_scraper_info(scraper_id: str):
    """
    Get information about a specific scraper.
    
    Args:
        scraper_id: ID of the scraper
        
    Returns:
        ScraperConfig object or None if not found
    """
    loader = create_default_plugin_loader()
    return loader.get_scraper_config(scraper_id)


# Export main classes and functions
__all__ = [
    # Plugin Architecture
    'BaseScraper',
    'ScraperType', 
    'ScraperStatus',
    'ScraperError',
    'ScraperRegistry',
    'ScraperManager',
    'ScraperManagerFactory',
    'ScraperConfig',
    'ScraperCategory',
    'PluginLoader',
    
    # Convenience functions
    'create_default_plugin_loader',
    'create_custom_plugin_loader',
    'create_scraper_manager',
    'get_scraper_categories',
    'get_available_scrapers',
    'get_scraper_info',
    
    # Configuration
    'DEFAULT_SCRAPER_CONFIGS',
    
    # Legacy scrapers (for backward compatibility)
    'IndeedScraper',
    'LinkedInScraper', 
    'StackOverflowScraper',
    'DiceScraper',
    'RemoteOKScraper',
    'WeWorkRemotelyScraper',
    'SimpleJobsScraper',
    'APISourcesScraper',
    'RedditScraper',
    'EnhancedPlaywrightScraper',
    'JobspressoScraper',
    'YCJobsScraper',
    'AuthenticJobsScraper',
    'OttaScraper',
    'HackerNewsScraper',
    'HimalayasScraper',
    'LeverScraper',
    'GoogleJobsScraper',
    'GreenhouseScraper',
    'RobustScraper',
    'GlassdoorScraper',
]
