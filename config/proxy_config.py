#!/usr/bin/env python3
"""
Proxy Rotation Service Configuration
Supports multiple proxy services for reliable access to Indeed
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ProxyServiceConfig:
    """Configuration for a proxy service"""
    name: str
    enabled: bool
    api_key: str
    base_url: str
    endpoints: Dict[str, str]
    authentication: Dict[str, str]
    rate_limits: Dict[str, int]
    geographic_targets: List[str]
    proxy_formats: List[str]

# Proxy Service Configurations
PROXY_SERVICES = {
    "scraperapi": ProxyServiceConfig(
        name="ScraperAPI",
        enabled=bool(os.getenv("SCRAPERAPI_ENABLED", "true").lower() == "true"),
        api_key=os.getenv("SCRAPERAPI_KEY", "a3bd3bc79e2078fc51691919e18ebfab"),
        base_url="http://api.scraperapi.com",
        endpoints={
            "proxy": "/api/v2/scrape",
            "account": "/api/v2/account",
            "proxy_list": "/api/v2/proxy"
        },
        authentication={
            "method": "api_key",
            "header": "X-API-Key"
        },
        rate_limits={
            "requests_per_minute": 1000,
            "concurrent_requests": 10
        },
        geographic_targets=[
            "us", "ca", "gb", "de", "fr", "nl", "se", "no", "dk", "fi",
            "ch", "at", "be", "ie", "it", "es", "pt", "au", "nz", "jp"
        ],
        proxy_formats=[
            "http://username:password@proxy.scraperapi.com:8081",
            "http://proxy.scraperapi.com:8081"
        ]
    ),
    
    "brightdata": ProxyServiceConfig(
        name="Bright Data",
        enabled=bool(os.getenv("BRIGHTDATA_ENABLED", "false").lower() == "true"),
        api_key=os.getenv("BRIGHTDATA_KEY", ""),
        base_url="https://brd.superproxy.io",
        endpoints={
            "proxy": "/",
            "account": "/api/account",
            "proxy_list": "/api/proxy"
        },
        authentication={
            "method": "username_password",
            "username": os.getenv("BRIGHTDATA_USERNAME", ""),
            "password": os.getenv("BRIGHTDATA_PASSWORD", "")
        },
        rate_limits={
            "requests_per_minute": 500,
            "concurrent_requests": 5
        },
        geographic_targets=[
            "us", "ca", "gb", "de", "fr", "nl", "se", "no", "dk", "fi",
            "ch", "at", "be", "ie", "it", "es", "pt", "au", "nz", "jp",
            "br", "mx", "ar", "cl", "co", "pe", "ve", "za", "ng", "ke"
        ],
        proxy_formats=[
            "http://username:password@brd.superproxy.io:22225",
            "http://brd.superproxy.io:22225"
        ]
    ),
    
    "oxylabs": ProxyServiceConfig(
        name="Oxylabs",
        enabled=bool(os.getenv("OXYLABS_ENABLED", "false").lower() == "true"),
        api_key=os.getenv("OXYLABS_KEY", ""),
        base_url="http://pr.oxylabs.io",
        endpoints={
            "proxy": "/",
            "account": "/api/account",
            "proxy_list": "/api/proxy"
        },
        authentication={
            "method": "username_password",
            "username": os.getenv("OXYLABS_USERNAME", ""),
            "password": os.getenv("OXYLABS_PASSWORD", "")
        },
        rate_limits={
            "requests_per_minute": 300,
            "concurrent_requests": 3
        },
        geographic_targets=[
            "us", "ca", "gb", "de", "fr", "nl", "se", "no", "dk", "fi",
            "ch", "at", "be", "ie", "it", "es", "pt", "au", "nz", "jp",
            "br", "mx", "ar", "cl", "co", "pe", "ve", "za", "ng", "ke",
            "in", "sg", "kr", "cn", "th", "vn", "my", "id", "ph"
        ],
        proxy_formats=[
            "http://username:password@pr.oxylabs.io:7777",
            "http://pr.oxylabs.io:7777"
        ]
    ),
    
    "free_proxies": ProxyServiceConfig(
        name="Free Proxy Pool",
        enabled=bool(os.getenv("FREE_PROXIES_ENABLED", "true").lower() == "true"),
        api_key="",
        base_url="",
        endpoints={},
        authentication={},
        rate_limits={
            "requests_per_minute": 50,
            "concurrent_requests": 2
        },
        geographic_targets=[
            "us", "ca", "gb", "de", "fr", "nl", "se", "no", "dk", "fi"
        ],
        proxy_formats=[
            "http://host:port",
            "https://host:port",
            "socks5://host:port"
        ]
    )
}

# Default proxy configuration
DEFAULT_PROXY_CONFIG = {
    "enabled": True,
    "rotation_strategy": "round_robin",  # round_robin, random, failover, geographic
    "max_failures": 3,
    "timeout": 30,
    "health_check_interval": 300,  # 5 minutes
    "max_proxies_per_request": 5,
    "geographic_preference": ["us", "ca", "gb", "de"],
    "fallback_to_direct": True,
    "retry_delay": 5,
    "exponential_backoff": True
}

# Proxy health check configuration
PROXY_HEALTH_CHECK = {
    "enabled": True,
    "test_urls": [
        "http://httpbin.org/ip",
        "https://api.ipify.org?format=json",
        "http://ip-api.com/json"
    ],
    "timeout": 10,
    "max_response_time": 5,
    "success_codes": [200, 201, 202],
    "check_interval": 300,  # 5 minutes
    "max_failures_before_removal": 3
}

# Geographic targeting configuration
GEOGRAPHIC_TARGETING = {
    "enabled": True,
    "default_location": "us",
    "location_mapping": {
        "us": ["United States", "USA", "America"],
        "ca": ["Canada", "Canadian"],
        "gb": ["United Kingdom", "UK", "England", "Scotland", "Wales"],
        "de": ["Germany", "Deutschland", "German"],
        "fr": ["France", "French"],
        "nl": ["Netherlands", "Dutch"],
        "au": ["Australia", "Australian"],
        "nz": ["New Zealand", "Kiwi"]
    },
    "proxy_rotation_by_location": True,
    "location_based_retry": True
}

# Rate limiting configuration
RATE_LIMITING = {
    "enabled": True,
    "global_requests_per_minute": 100,
    "global_requests_per_hour": 1000,
    "per_proxy_requests_per_minute": 20,
    "per_proxy_requests_per_hour": 200,
    "burst_limit": 10,
    "cooldown_period": 60,
    "adaptive_rate_limiting": True
}

# Authentication and security
AUTHENTICATION = {
    "store_credentials_in_env": True,
    "encrypt_api_keys": False,
    "rotate_credentials": False,
    "credential_rotation_interval": 86400,  # 24 hours
    "max_failed_auth_attempts": 3,
    "auth_failure_cooldown": 300  # 5 minutes
}

# Logging and monitoring
LOGGING = {
    "log_proxy_usage": True,
    "log_proxy_performance": True,
    "log_geographic_targeting": True,
    "log_rate_limiting": True,
    "log_authentication": True,
    "performance_metrics": True,
    "alert_on_failures": True
}

# Free proxy sources for fallback
FREE_PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt"
]

# Proxy quality scoring
PROXY_QUALITY_SCORING = {
    "enabled": True,
    "factors": {
        "response_time": 0.3,
        "uptime": 0.25,
        "geographic_location": 0.2,
        "anonymity_level": 0.15,
        "protocol_support": 0.1
    },
    "min_quality_score": 0.6,
    "quality_update_interval": 600,  # 10 minutes
    "score_decay_rate": 0.1  # Score decreases by 10% per interval if not used
}
