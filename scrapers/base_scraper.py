"""
Base Scraper Interface for JobPulse Plugin Architecture

This module defines the common interface that all scrapers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from enum import Enum
import logging
from datetime import datetime


class ScraperType(Enum):
    """Enumeration of scraper types for categorization"""
    WEB_SCRAPER = "web_scraper"           # Traditional web scraping (BeautifulSoup, Selenium)
    API_SCRAPER = "api_scraper"           # API-based scrapers
    PLAYWRIGHT_SCRAPER = "playwright"      # Playwright-based scrapers
    FALLBACK_SCRAPER = "fallback"         # Fallback/mock data scrapers
    ENHANCED_SCRAPER = "enhanced"         # Enhanced scrapers with anti-detection


class ScraperStatus(Enum):
    """Enumeration of scraper statuses"""
    ACTIVE = "active"                     # Scraper is working normally
    RATE_LIMITED = "rate_limited"         # Scraper is being rate limited
    BLOCKED = "blocked"                   # Scraper is blocked by the target site
    ERROR = "error"                       # Scraper has encountered an error
    DISABLED = "disabled"                 # Scraper is disabled


class BaseScraper(ABC):
    """
    Abstract base class that all scrapers must inherit from.
    
    This provides a common interface and shared functionality for all scrapers
    in the JobPulse system.
    """
    
    def __init__(self, name: str, scraper_type: ScraperType, priority: int = 1):
        """
        Initialize the base scraper.
        
        Args:
            name: Human-readable name for the scraper
            scraper_type: Type of scraper (see ScraperType enum)
            priority: Priority level (1=highest, 5=lowest) for execution order
        """
        self.name = name
        self.scraper_type = scraper_type
        self.priority = priority
        self.status = ScraperStatus.ACTIVE
        self.last_run = None
        self.success_count = 0
        self.error_count = 0
        self.total_jobs_scraped = 0
        
        # Setup logging
        self.setup_logging()
        
        # Initialize scraper-specific resources
        self._init_resources()
    
    def setup_logging(self):
        """Setup logging for the scraper"""
        # Ensure logs directory exists
        import os
        os.makedirs('logs', exist_ok=True)
        
        # Create logger specific to this scraper
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Only add handlers if they don't already exist
        if not self.logger.handlers:
            # File handler
            log_file = f"logs/{self.name.lower().replace(' ', '_')}_scraper.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def _init_resources(self):
        """
        Initialize scraper-specific resources (sessions, browsers, etc.).
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def search_jobs(self, keyword: str, location: str = "United States", 
                   limit: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for jobs based on keyword and location.
        
        Args:
            keyword: Job search keyword
            location: Location to search in
            limit: Maximum number of jobs to return
            **kwargs: Additional search parameters
            
        Returns:
            List of job dictionaries with standardized format
            
        Raises:
            ScraperError: If the scraper encounters an error
        """
        pass
    
    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific job.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Detailed job information or None if not available
        """
        # Default implementation returns None
        # Subclasses can override to provide detailed job information
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status and statistics for the scraper.
        
        Returns:
            Dictionary containing scraper status information
        """
        return {
            'name': self.name,
            'type': self.scraper_type.value,
            'status': self.status.value,
            'priority': self.priority,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'total_jobs_scraped': self.total_jobs_scraped,
            'success_rate': (self.success_count / (self.success_count + self.error_count) 
                           if (self.success_count + self.error_count) > 0 else 0)
        }
    
    def update_status(self, status: ScraperStatus):
        """Update the scraper status"""
        self.status = status
        self.logger.info(f"Scraper status updated to: {status.value}")
    
    def record_success(self, jobs_scraped: int = 0):
        """Record a successful scraping operation"""
        self.success_count += 1
        self.total_jobs_scraped += jobs_scraped
        self.last_run = datetime.now()
        self.status = ScraperStatus.ACTIVE
    
    def record_error(self, error: Exception):
        """Record an error during scraping"""
        self.error_count += 1
        self.last_run = datetime.now()
        self.status = ScraperStatus.ERROR
        self.logger.error(f"Scraper error: {str(error)}")
    
    def is_available(self) -> bool:
        """Check if the scraper is available for use"""
        return self.status in [ScraperStatus.ACTIVE, ScraperStatus.RATE_LIMITED]
    
    def can_handle_location(self, location: str) -> bool:
        """
        Check if the scraper can handle a specific location.
        
        Args:
            location: Location string to check
            
        Returns:
            True if the scraper can handle this location
        """
        # Default implementation - all scrapers can handle all locations
        # Subclasses can override to provide location-specific logic
        return True
    
    def get_supported_features(self) -> List[str]:
        """
        Get list of features supported by this scraper.
        
        Returns:
            List of supported feature strings
        """
        features = ['basic_search']
        
        if hasattr(self, 'get_job_details') and self.get_job_details.__code__ != BaseScraper.get_job_details.__code__:
            features.append('detailed_jobs')
        
        return features
    
    def cleanup(self):
        """Clean up resources used by the scraper"""
        # Default implementation does nothing
        # Subclasses should override to clean up resources (close browsers, sessions, etc.)
        pass
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, type={self.scraper_type.value}, priority={self.priority})"
    
    def __repr__(self):
        return self.__str__()


class ScraperError(Exception):
    """Base exception class for scraper errors"""
    
    def __init__(self, message: str, scraper_name: str = None, original_error: Exception = None):
        super().__init__(message)
        self.scraper_name = scraper_name
        self.original_error = original_error
    
    def __str__(self):
        if self.scraper_name:
            return f"[{self.scraper_name}] {super().__str__()}"
        return super().__str__()


class ScraperRegistry:
    """
    Registry for managing all available scrapers.
    
    This class provides a centralized way to register, discover, and manage scrapers.
    """
    
    def __init__(self):
        self._scrapers = {}
        self._scrapers_by_type = {}
        self._scrapers_by_priority = {}
    
    def register_scraper(self, scraper: BaseScraper):
        """Register a scraper with the registry"""
        self._scrapers[scraper.name] = scraper
        
        # Group by type
        if scraper.scraper_type not in self._scrapers_by_type:
            self._scrapers_by_type[scraper.scraper_type] = []
        self._scrapers_by_type[scraper.scraper_type].append(scraper)
        
        # Group by priority
        if scraper.priority not in self._scrapers_by_priority:
            self._scrapers_by_priority[scraper.priority] = []
        self._scrapers_by_priority[scraper.priority].append(scraper)
        
        # Sort by priority
        for priority in self._scrapers_by_priority:
            self._scrapers_by_priority[priority].sort(key=lambda x: x.name)
    
    def get_scraper(self, name: str) -> Optional[BaseScraper]:
        """Get a scraper by name"""
        return self._scrapers.get(name)
    
    def get_scrapers_by_type(self, scraper_type: ScraperType) -> List[BaseScraper]:
        """Get all scrapers of a specific type"""
        return self._scrapers_by_type.get(scraper_type, [])
    
    def get_scrapers_by_priority(self, priority: int) -> List[BaseScraper]:
        """Get all scrapers with a specific priority"""
        return self._scrapers_by_priority.get(priority, [])
    
    def get_all_scrapers(self) -> List[BaseScraper]:
        """Get all registered scrapers"""
        return list(self._scrapers.values())
    
    def get_available_scrapers(self) -> List[BaseScraper]:
        """Get all available (non-disabled) scrapers"""
        return [s for s in self._scrapers.values() if s.is_available()]
    
    def get_scrapers_for_search(self, sources: List[str] = None, 
                               location: str = "United States") -> List[BaseScraper]:
        """
        Get scrapers suitable for a specific search.
        
        Args:
            sources: List of source names to include (None for all)
            location: Location to search in
            
        Returns:
            List of scrapers sorted by priority
        """
        scrapers = []
        
        if sources:
            # Use specific sources
            for source in sources:
                scraper = self._scrapers.get(source)
                if scraper and scraper.is_available() and scraper.can_handle_location(location):
                    scrapers.append(scraper)
        else:
            # Use all available scrapers
            scrapers = [s for s in self._scrapers.values() 
                       if s.is_available() and s.can_handle_location(location)]
        
        # Sort by priority (lowest number = highest priority)
        scrapers.sort(key=lambda x: x.priority)
        return scrapers
    
    def unregister_scraper(self, name: str):
        """Unregister a scraper from the registry"""
        if name in self._scrapers:
            scraper = self._scrapers[name]
            
            # Remove from type groups
            if scraper.scraper_type in self._scrapers_by_type:
                self._scrapers_by_type[scraper.scraper_type] = [
                    s for s in self._scrapers_by_type[scraper.scraper_type] 
                    if s.name != name
                ]
            
            # Remove from priority groups
            if scraper.priority in self._scrapers_by_priority:
                self._scrapers_by_priority[scraper.priority] = [
                    s for s in self._scrapers_by_priority[scraper.priority] 
                    if s.name != name
                ]
            
            # Clean up scraper resources
            scraper.cleanup()
            
            # Remove from main registry
            del self._scrapers[name]
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get status information about the registry"""
        return {
            'total_scrapers': len(self._scrapers),
            'scrapers_by_type': {t.value: len(s) for t, s in self._scrapers_by_type.items()},
            'scrapers_by_priority': {p: len(s) for p, s in self._scrapers_by_priority.items()},
            'available_scrapers': len(self.get_available_scrapers()),
            'scraper_details': [s.get_status() for s in self._scrapers.values()]
        }
