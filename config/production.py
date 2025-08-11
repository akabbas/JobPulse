"""
Production configuration for JobPulse
Optimized for server deployment and avoiding 403 errors
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration settings"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://jobpulse:jobpulse123@localhost:5432/jobpulse')
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    # Scraping Configuration (Optimized to avoid 403 errors)
    SCRAPING_CONFIG = {
        # Use reliable sources first
        'priority_sources': ['api_sources', 'reddit', 'simple_jobs'],
        'fallback_sources': ['indeed', 'linkedin', 'stackoverflow'],
        
        # Rate limiting to avoid 403 errors
        'request_delay': 2.0,  # 2 seconds between requests
        'max_retries': 3,
        'timeout': 30,
        
        # User agent rotation
        'user_agents': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ],
        
        # Proxy configuration (if needed)
        'use_proxy': False,
        'proxy_list': [],
        
        # Session management
        'session_timeout': 300,  # 5 minutes
        'max_concurrent_requests': 5,
        
        # Data limits
        'max_jobs_per_source': 50,
        'max_total_jobs': 200,
        
        # Error handling
        'ignore_403_errors': True,
        'fallback_to_sample_data': True,
        'log_errors': True
    }
    
    # API Configuration
    API_CONFIG = {
        'indeed_api_key': os.environ.get('INDEED_API_KEY', ''),
        'linkedin_api_key': os.environ.get('LINKEDIN_API_KEY', ''),
        'github_api_key': os.environ.get('GITHUB_API_KEY', ''),
        'reddit_client_id': os.environ.get('REDDIT_CLIENT_ID', ''),
        'reddit_client_secret': os.environ.get('REDDIT_CLIENT_SECRET', ''),
        'reddit_user_agent': 'JobPulse/1.0'
    }
    
    # Logging Configuration
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'logs/production.log',
        'max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
    
    # Cache Configuration
    CACHE_CONFIG = {
        'type': 'redis',
        'default_timeout': 3600,  # 1 hour
        'key_prefix': 'jobpulse'
    }
    
    # Security Configuration
    SECURITY_CONFIG = {
        'cors_origins': ['*'],  # Configure appropriately for production
        'rate_limit': {
            'requests_per_minute': 60,
            'requests_per_hour': 1000
        }
    }
    
    # Performance Configuration
    PERFORMANCE_CONFIG = {
        'worker_processes': 4,
        'thread_pool_size': 20,
        'connection_pool_size': 10,
        'enable_compression': True,
        'enable_caching': True
    }
    
    @staticmethod
    def get_scraping_sources():
        """Get prioritized scraping sources to avoid 403 errors"""
        return {
            'primary': ['api_sources', 'reddit', 'simple_jobs'],
            'secondary': ['indeed', 'linkedin', 'stackoverflow'],
            'fallback': ['dice', 'remoteok', 'weworkremotely']
        }
    
    @staticmethod
    def get_request_headers():
        """Get rotating request headers to avoid detection"""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        } 