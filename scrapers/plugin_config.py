"""
Plugin Configuration for JobPulse Scraper Architecture

This module defines the configuration for loading and managing scrapers
in the new plugin-based architecture.
"""

from typing import Dict, List, Any, Type
from dataclasses import dataclass
from enum import Enum

from base_scraper import ScraperType, BaseScraper


@dataclass
class ScraperConfig:
    """Configuration for a single scraper"""
    name: str
    class_name: str
    module_path: str
    scraper_type: ScraperType
    priority: int
    enabled: bool = True
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


class ScraperCategory(Enum):
    """Categories for organizing scrapers"""
    PRIMARY = "primary"           # High-priority, reliable scrapers
    SECONDARY = "secondary"       # Medium-priority scrapers
    FALLBACK = "fallback"         # Low-priority, fallback scrapers
    ENHANCED = "enhanced"         # Enhanced scrapers with anti-detection
    EXPERIMENTAL = "experimental" # Experimental or beta scrapers


# Default scraper configurations
DEFAULT_SCRAPER_CONFIGS = {
    # Primary scrapers (highest priority, most reliable)
    "enhanced": ScraperConfig(
        name="Enhanced Playwright",
        class_name="EnhancedPlaywrightScraper",
        module_path="scrapers.enhanced_playwright_scraper",
        scraper_type=ScraperType.ENHANCED_SCRAPER,
        priority=1,
        config={"headless": True}
    ),
    
    "api_sources": ScraperConfig(
        name="API Sources",
        class_name="APISourcesScraper",
        module_path="scrapers.api_sources_scraper",
        scraper_type=ScraperType.API_SCRAPER,
        priority=1
    ),
    
    "reddit": ScraperConfig(
        name="Reddit Jobs",
        class_name="RedditScraper",
        module_path="scrapers.reddit_scraper",
        scraper_type=ScraperType.API_SCRAPER,
        priority=1
    ),
    
    # Secondary scrapers (medium priority)
    "greenhouse": ScraperConfig(
        name="Greenhouse",
        class_name="GreenhouseScraper",
        module_path="scrapers.greenhouse_scraper",
        scraper_type=ScraperType.API_SCRAPER,
        priority=2
    ),
    
    "lever": ScraperConfig(
        name="Lever",
        class_name="LeverScraper",
        module_path="scrapers.lever_scraper",
        scraper_type=ScraperType.API_SCRAPER,
        priority=2
    ),
    
    "google_jobs": ScraperConfig(
        name="Google Jobs",
        class_name="GoogleJobsScraper",
        module_path="scrapers.google_jobs_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=2
    ),
    
    "jobspresso": ScraperConfig(
        name="Jobspresso",
        class_name="JobspressoScraper",
        module_path="scrapers.jobspresso_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=2
    ),
    
    "himalayas": ScraperConfig(
        name="Himalayas",
        class_name="HimalayasScraper",
        module_path="scrapers.himalayas_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=2
    ),
    
    "yc_jobs": ScraperConfig(
        name="YC Jobs",
        class_name="YCJobsScraper",
        module_path="scrapers.yc_jobs_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=2
    ),
    
    "authentic_jobs": ScraperConfig(
        name="Authentic Jobs",
        class_name="AuthenticJobsScraper",
        module_path="scrapers.authentic_jobs_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=2
    ),
    
    "otta": ScraperConfig(
        name="Otta",
        class_name="OttaScraper",
        module_path="scrapers.otta_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=2
    ),
    
    "hackernews": ScraperConfig(
        name="Hacker News",
        class_name="HackerNewsScraper",
        module_path="scrapers.hackernews_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=2
    ),
    
    # Tertiary scrapers (lower priority, may have rate limiting)
    "indeed": ScraperConfig(
        name="Indeed",
        class_name="IndeedScraper",
        module_path="scrapers.indeed_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=3,
        config={"max_pages": 5}  # Limit pages to avoid rate limiting
    ),
    
    "linkedin": ScraperConfig(
        name="LinkedIn",
        class_name="LinkedInScraper",
        module_path="scrapers.linkedin_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=3,
        config={"max_pages": 3}
    ),
    
    "stackoverflow": ScraperConfig(
        name="Stack Overflow",
        class_name="StackOverflowScraper",
        module_path="scrapers.stackoverflow_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=3
    ),
    
    "dice": ScraperConfig(
        name="Dice",
        class_name="DiceScraper",
        module_path="scrapers.dice_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=3
    ),
    
    "remoteok": ScraperConfig(
        name="Remote OK",
        class_name="RemoteOKScraper",
        module_path="scrapers.remoteok_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=3
    ),
    
    "weworkremotely": ScraperConfig(
        name="We Work Remotely",
        class_name="WeWorkRemotelyScraper",
        module_path="scrapers.weworkremotely_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=3
    ),
    
    # Fallback scrapers (lowest priority, only used when others fail)
    "simple": ScraperConfig(
        name="Simple Jobs",
        class_name="SimpleJobsScraper",
        module_path="scrapers.simple_jobs_scraper",
        scraper_type=ScraperType.FALLBACK_SCRAPER,
        priority=5,
        enabled=False  # Disabled by default to avoid mock data
    ),
    
    "robust": ScraperConfig(
        name="Robust Scraper",
        class_name="RobustScraper",
        module_path="scrapers.robust_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=4
    ),
    
    "glassdoor": ScraperConfig(
        name="Glassdoor",
        class_name="GlassdoorScraper",
        module_path="scrapers.glassdoor_scraper",
        scraper_type=ScraperType.WEB_SCRAPER,
        priority=4
    )
}


class PluginLoader:
    """
    Loads and manages scraper plugins based on configuration.
    
    This class handles the dynamic loading of scraper modules and
    instantiation of scraper objects.
    """
    
    def __init__(self, configs: Dict[str, ScraperConfig] = None):
        """
        Initialize the plugin loader.
        
        Args:
            configs: Dictionary of scraper configurations
        """
        self.configs = configs or DEFAULT_SCRAPER_CONFIGS
        self.loaded_scrapers = {}
        self.loaded_classes = {}
    
    def load_scraper(self, scraper_id: str) -> BaseScraper:
        """
        Load a single scraper by ID.
        
        Args:
            scraper_id: ID of the scraper to load
            
        Returns:
            Loaded scraper instance
            
        Raises:
            ImportError: If the scraper module cannot be imported
            AttributeError: If the scraper class cannot be found
        """
        if scraper_id in self.loaded_scrapers:
            return self.loaded_scrapers[scraper_id]
        
        if scraper_id not in self.configs:
            raise ValueError(f"Unknown scraper ID: {scraper_id}")
        
        config = self.configs[scraper_id]
        
        try:
            # Import the module
            module = __import__(config.module_path, fromlist=[config.class_name])
            
            # Get the class
            scraper_class = getattr(module, config.class_name)
            
            # Store the loaded class
            self.loaded_classes[scraper_id] = scraper_class
            
            # Create instance with configuration
            if config.config:
                scraper_instance = scraper_class(**config.config)
            else:
                scraper_instance = scraper_class()
            
            # Override name and priority if specified in config
            if config.name != scraper_instance.name:
                scraper_instance.name = config.name
            if config.priority != scraper_instance.priority:
                scraper_instance.priority = config.priority
            
            # Store the instance
            self.loaded_scrapers[scraper_id] = scraper_instance
            
            return scraper_instance
            
        except ImportError as e:
            raise ImportError(f"Failed to import scraper module {config.module_path}: {e}")
        except AttributeError as e:
            raise AttributeError(f"Failed to find scraper class {config.class_name} in {config.module_path}: {e}")
        except Exception as e:
            raise Exception(f"Failed to instantiate scraper {scraper_id}: {e}")
    
    def load_scrapers(self, scraper_ids: List[str] = None) -> Dict[str, BaseScraper]:
        """
        Load multiple scrapers.
        
        Args:
            scraper_ids: List of scraper IDs to load (None for all enabled)
            
        Returns:
            Dictionary of loaded scrapers
        """
        if scraper_ids is None:
            # Load all enabled scrapers
            scraper_ids = [sid for sid, config in self.configs.items() if config.enabled]
        
        scrapers = {}
        for scraper_id in scraper_ids:
            try:
                scraper = self.load_scraper(scraper_id)
                scrapers[scraper_id] = scraper
            except Exception as e:
                print(f"Warning: Failed to load scraper {scraper_id}: {e}")
                continue
        
        return scrapers
    
    def get_scraper_config(self, scraper_id: str) -> ScraperConfig:
        """Get configuration for a specific scraper"""
        return self.configs.get(scraper_id)
    
    def update_scraper_config(self, scraper_id: str, **kwargs):
        """Update configuration for a specific scraper"""
        if scraper_id in self.configs:
            config = self.configs[scraper_id]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    def enable_scraper(self, scraper_id: str):
        """Enable a scraper"""
        if scraper_id in self.configs:
            self.configs[scraper_id].enabled = True
    
    def disable_scraper(self, scraper_id: str):
        """Disable a scraper"""
        if scraper_id in self.configs:
            self.configs[scraper_id].enabled = False
    
    def get_enabled_scrapers(self) -> List[str]:
        """Get list of enabled scraper IDs"""
        return [sid for sid, config in self.configs.items() if config.enabled]
    
    def get_scrapers_by_type(self, scraper_type: ScraperType) -> List[str]:
        """Get list of scraper IDs by type"""
        return [sid for sid, config in self.configs.items() 
                if config.enabled and config.scraper_type == scraper_type]
    
    def get_scrapers_by_priority(self, priority: int) -> List[str]:
        """Get list of scraper IDs by priority"""
        return [sid for sid, config in self.configs.items() 
                if config.enabled and config.priority == priority]
    
    def cleanup(self):
        """Clean up all loaded scrapers"""
        for scraper in self.loaded_scrapers.values():
            try:
                scraper.cleanup()
            except Exception as e:
                print(f"Warning: Failed to cleanup scraper {scraper.name}: {e}")
        
        self.loaded_scrapers.clear()
        self.loaded_classes.clear()


# Convenience functions for common operations
def create_default_plugin_loader() -> PluginLoader:
    """Create a plugin loader with default configurations"""
    return PluginLoader()


def create_custom_plugin_loader(configs: Dict[str, ScraperConfig]) -> PluginLoader:
    """Create a plugin loader with custom configurations"""
    return PluginLoader(configs)


def get_scraper_categories() -> Dict[ScraperCategory, List[str]]:
    """Get scrapers organized by category"""
    categories = {}
    for category in ScraperCategory:
        categories[category] = []
    
    for scraper_id, config in DEFAULT_SCRAPER_CONFIGS.items():
        if config.enabled:
            if config.priority == 1:
                categories[ScraperCategory.PRIMARY].append(scraper_id)
            elif config.priority == 2:
                categories[ScraperCategory.SECONDARY].append(scraper_id)
            elif config.priority >= 4:
                categories[ScraperCategory.FALLBACK].append(scraper_id)
            elif config.scraper_type == ScraperType.ENHANCED_SCRAPER:
                categories[ScraperCategory.ENHANCED].append(scraper_id)
            else:
                categories[ScraperCategory.EXPERIMENTAL].append(scraper_id)
    
    return categories
