"""
Scraper Manager for JobPulse Plugin Architecture

This module manages the coordination and execution of all scrapers
using the new plugin-based architecture.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

from .base_scraper import BaseScraper, ScraperRegistry, ScraperType, ScraperError


class ScraperManager:
    """
    Manages the coordination and execution of all scrapers.
    
    This class provides a high-level interface for executing job searches
    across multiple scrapers with proper error handling, rate limiting,
    and result aggregation.
    """
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize the scraper manager.
        
        Args:
            max_workers: Maximum number of concurrent scraper executions
        """
        self.registry = ScraperRegistry()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.total_searches = 0
        self.successful_searches = 0
        self.failed_searches = 0
        self.average_response_time = 0.0
    
    def register_scraper(self, scraper: BaseScraper):
        """Register a scraper with the manager"""
        self.registry.register_scraper(scraper)
        self.logger.info(f"Registered scraper: {scraper.name} (type: {scraper.scraper_type.value}, priority: {scraper.priority})")
    
    def register_scrapers(self, scrapers: List[BaseScraper]):
        """Register multiple scrapers at once"""
        for scraper in scrapers:
            self.register_scraper(scraper)
    
    def search_jobs(self, keyword: str, location: str = "United States", 
                   limit: int = 100, sources: List[str] = None, 
                   experience_level: str = "all", **kwargs) -> Dict[str, Any]:
        """
        Execute a job search across multiple scrapers.
        
        Args:
            keyword: Job search keyword
            location: Location to search in
            limit: Maximum number of jobs to return
            sources: List of source names to use (None for all available)
            experience_level: Experience level filter
            **kwargs: Additional search parameters
            
        Returns:
            Dictionary containing search results and metadata
        """
        start_time = time.time()
        self.total_searches += 1
        
        try:
            # Get scrapers for this search
            scrapers = self.registry.get_scrapers_for_search(sources, location)
            
            if not scrapers:
                raise ScraperError(f"No available scrapers found for location: {location}")
            
            self.logger.info(f"Executing job search: '{keyword}' in '{location}' with {len(scrapers)} scrapers")
            
            # Execute scrapers in parallel
            results = self._execute_scrapers_parallel(scrapers, keyword, location, limit, **kwargs)
            
            # Aggregate and process results
            aggregated_results = self._aggregate_results(results, limit, experience_level)
            
            # Update performance metrics
            response_time = time.time() - start_time
            self._update_performance_metrics(response_time, True)
            
            self.logger.info(f"Search completed successfully in {response_time:.2f}s. Found {len(aggregated_results['jobs'])} jobs from {len(scrapers)} scrapers")
            
            return aggregated_results
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_performance_metrics(response_time, False)
            
            self.logger.error(f"Search failed after {response_time:.2f}s: {str(e)}")
            raise ScraperError(f"Job search failed: {str(e)}")
    
    def _execute_scrapers_parallel(self, scrapers: List[BaseScraper], keyword: str, 
                                  location: str, limit: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute multiple scrapers in parallel.
        
        Args:
            scrapers: List of scrapers to execute
            keyword: Job search keyword
            location: Location to search in
            limit: Maximum number of jobs to return
            **kwargs: Additional search parameters
            
        Returns:
            List of results from each scraper
        """
        results = []
        
        # Submit all scraper tasks
        future_to_scraper = {}
        for scraper in scrapers:
            future = self.executor.submit(
                self._execute_single_scraper, scraper, keyword, location, limit, **kwargs
            )
            future_to_scraper[future] = scraper
        
        # Collect results as they complete
        for future in as_completed(future_to_scraper, timeout=300):  # 5 minute timeout
            scraper = future_to_scraper[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Scraper {scraper.name} failed: {str(e)}")
                scraper.record_error(e)
                
                # Add failed result for tracking
                results.append({
                    'scraper_name': scraper.name,
                    'success': False,
                    'error': str(e),
                    'jobs': [],
                    'execution_time': 0
                })
        
        return results
    
    def _execute_single_scraper(self, scraper: BaseScraper, keyword: str, 
                               location: str, limit: int, **kwargs) -> Dict[str, Any]:
        """
        Execute a single scraper.
        
        Args:
            scraper: Scraper to execute
            keyword: Job search keyword
            location: Location to search in
            limit: Maximum number of jobs to return
            **kwargs: Additional search parameters
            
        Returns:
            Dictionary containing scraper results
        """
        start_time = time.time()
        
        try:
            # Check if scraper can handle this location
            if not scraper.can_handle_location(location):
                return {
                    'scraper_name': scraper.name,
                    'success': False,
                    'error': f"Scraper cannot handle location: {location}",
                    'jobs': [],
                    'execution_time': 0
                }
            
            # Execute the scraper
            jobs = scraper.search_jobs(keyword, location, limit, **kwargs)
            
            # Record success
            scraper.record_success(len(jobs))
            
            execution_time = time.time() - start_time
            
            return {
                'scraper_name': scraper.name,
                'success': True,
                'jobs': jobs,
                'execution_time': execution_time,
                'job_count': len(jobs)
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            scraper.record_error(e)
            
            return {
                'scraper_name': scraper.name,
                'success': False,
                'error': str(e),
                'jobs': [],
                'execution_time': execution_time
            }
    
    def _aggregate_results(self, results: List[Dict[str, Any]], limit: int, 
                          experience_level: str) -> Dict[str, Any]:
        """
        Aggregate results from multiple scrapers.
        
        Args:
            results: List of results from each scraper
            limit: Maximum number of jobs to return
            experience_level: Experience level filter
            
        Returns:
            Aggregated results dictionary
        """
        all_jobs = []
        successful_scrapers = 0
        total_jobs_found = 0
        
        # Collect all successful results
        for result in results:
            if result['success']:
                successful_scrapers += 1
                total_jobs_found += result.get('job_count', 0)
                
                # Apply experience level filtering if needed
                if experience_level != "all":
                    filtered_jobs = self._filter_jobs_by_experience(result['jobs'], experience_level)
                    all_jobs.extend(filtered_jobs)
                else:
                    all_jobs.extend(result['jobs'])
        
        # Remove duplicates based on job URL
        unique_jobs = self._remove_duplicate_jobs(all_jobs)
        
        # Limit results
        final_jobs = unique_jobs[:limit]
        
        # Calculate execution statistics
        execution_stats = {
            'total_scrapers': len(results),
            'successful_scrapers': successful_scrapers,
            'failed_scrapers': len(results) - successful_scrapers,
            'total_jobs_found': total_jobs_found,
            'unique_jobs_returned': len(final_jobs),
            'average_execution_time': sum(r.get('execution_time', 0) for r in results) / len(results) if results else 0
        }
        
        return {
            'success': True,
            'jobs': final_jobs,
            'total_jobs': len(final_jobs),
            'execution_stats': execution_stats,
            'scraper_results': results
        }
    
    def _filter_jobs_by_experience(self, jobs: List[Dict[str, Any]], 
                                  experience_level: str) -> List[Dict[str, Any]]:
        """
        Filter jobs by experience level.
        
        Args:
            jobs: List of jobs to filter
            experience_level: Experience level to filter by
            
        Returns:
            Filtered list of jobs
        """
        if experience_level == "all":
            return jobs
        
        # Experience level keywords
        experience_keywords = {
            "entry": ["entry", "entry-level", "junior", "jr", "associate", "trainee", "intern"],
            "mid": ["mid", "mid-level", "intermediate", "experienced"],
            "senior": ["senior", "sr", "lead", "principal", "staff"],
            "executive": ["executive", "director", "vp", "cto", "ceo", "head of"]
        }
        
        keywords = experience_keywords.get(experience_level.lower(), [])
        
        filtered_jobs = []
        for job in jobs:
            title = job.get('title', '').lower()
            description = job.get('snippet', '').lower()
            
            # Check if any experience keywords are present
            if any(keyword in title or keyword in description for keyword in keywords):
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _remove_duplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate jobs based on URL and title.
        
        Args:
            jobs: List of jobs to deduplicate
            
        Returns:
            Deduplicated list of jobs
        """
        seen_urls = set()
        seen_titles = set()
        unique_jobs = []
        
        for job in jobs:
            url = job.get('job_url', '')
            title = job.get('title', '').lower().strip()
            
            # Check for duplicates
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
            elif title and title not in seen_titles:
                seen_titles.add(title)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _update_performance_metrics(self, response_time: float, success: bool):
        """Update performance tracking metrics"""
        if success:
            self.successful_searches += 1
        else:
            self.failed_searches += 1
        
        # Update average response time
        if self.total_searches == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_searches - 1) + response_time) 
                / self.total_searches
            )
    
    def get_manager_status(self) -> Dict[str, Any]:
        """Get status information about the scraper manager"""
        return {
            'total_searches': self.total_searches,
            'successful_searches': self.successful_searches,
            'failed_searches': self.failed_searches,
            'success_rate': self.successful_searches / self.total_searches if self.total_searches > 0 else 0,
            'average_response_time': self.average_response_time,
            'max_workers': self.max_workers,
            'registry_status': self.registry.get_registry_status()
        }
    
    def cleanup(self):
        """Clean up resources used by the manager"""
        self.executor.shutdown(wait=True)
        
        # Clean up all scrapers
        for scraper in self.registry.get_all_scrapers():
            try:
                scraper.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up scraper {scraper.name}: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


class ScraperManagerFactory:
    """
    Factory class for creating and configuring scraper managers.
    
    This class provides convenient methods for setting up scraper managers
    with different configurations.
    """
    
    @staticmethod
    def create_default_manager() -> ScraperManager:
        """Create a scraper manager with default configuration"""
        return ScraperManager(max_workers=5)
    
    @staticmethod
    def create_high_performance_manager() -> ScraperManager:
        """Create a scraper manager optimized for high performance"""
        return ScraperManager(max_workers=10)
    
    @staticmethod
    def create_conservative_manager() -> ScraperManager:
        """Create a scraper manager with conservative resource usage"""
        return ScraperManager(max_workers=3)
    
    @staticmethod
    def create_manager_with_scrapers(scrapers: List[BaseScraper], 
                                   max_workers: int = 5) -> ScraperManager:
        """
        Create a scraper manager and register the provided scrapers.
        
        Args:
            scrapers: List of scrapers to register
            max_workers: Maximum number of concurrent workers
            
        Returns:
            Configured scraper manager
        """
        manager = ScraperManager(max_workers=max_workers)
        manager.register_scrapers(scrapers)
        return manager
