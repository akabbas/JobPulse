#!/usr/bin/env python3
"""
Advanced Proxy Rotation Manager
Integrates with multiple proxy services for reliable access
"""

import asyncio
import aiohttp
import time
import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib

from config.proxy_config import (
    PROXY_SERVICES, DEFAULT_PROXY_CONFIG, PROXY_HEALTH_CHECK,
    GEOGRAPHIC_TARGETING, RATE_LIMITING, FREE_PROXY_SOURCES
)

@dataclass
class ProxyInfo:
    """Information about a proxy"""
    id: str
    host: str
    port: int
    protocol: str
    username: Optional[str] = None
    password: Optional[str] = None
    country: str = "unknown"
    city: str = "unknown"
    isp: str = "unknown"
    anonymity: str = "unknown"
    response_time: float = 0.0
    uptime: float = 100.0
    last_used: datetime = field(default_factory=datetime.now)
    last_checked: datetime = field(default_factory=datetime.now)
    failure_count: int = 0
    success_count: int = 0
    quality_score: float = 0.0
    is_active: bool = True
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(f"{self.host}:{self.port}".encode()).hexdigest()[:8]
    
    @property
    def url(self) -> str:
        """Get proxy URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def dict_format(self) -> Dict[str, Any]:
        """Get proxy in dictionary format for Playwright"""
        proxy_dict = {
            'server': f"{self.host}:{self.port}"
        }
        if self.username and self.password:
            proxy_dict['username'] = self.username
            proxy_dict['password'] = self.password
        return proxy_dict

class ProxyHealthChecker:
    """Manages proxy health checking and scoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_urls = PROXY_HEALTH_CHECK['test_urls']
        self.timeout = PROXY_HEALTH_CHECK['timeout']
        self.max_response_time = PROXY_HEALTH_CHECK['max_response_time']
        self.success_codes = PROXY_HEALTH_CHECK['success_codes']
        self.max_failures = PROXY_HEALTH_CHECK['max_failures_before_removal']
    
    async def check_proxy_health(self, proxy: ProxyInfo) -> Tuple[bool, float]:
        """Check if a proxy is healthy and measure response time"""
        try:
            start_time = time.time()
            
            # Test with aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    random.choice(self.test_urls),
                    proxy=proxy.url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status in self.success_codes and response_time <= self.max_response_time:
                        return True, response_time
                    else:
                        return False, response_time
                        
        except Exception as e:
            self.logger.debug(f"Health check failed for {proxy.url}: {e}")
            return False, float('inf')
    
    def update_proxy_score(self, proxy: ProxyInfo, success: bool, response_time: float):
        """Update proxy quality score based on performance"""
        if success:
            proxy.success_count += 1
            proxy.failure_count = max(0, proxy.failure_count - 1)
            proxy.response_time = response_time
            proxy.last_used = datetime.now()
        else:
            proxy.failure_count += 1
            proxy.last_checked = datetime.now()
        
        # Calculate quality score
        uptime_factor = max(0, 100 - proxy.failure_count * 10) / 100
        response_factor = max(0, 1 - (response_time / self.max_response_time))
        success_factor = proxy.success_count / max(1, proxy.success_count + proxy.failure_count)
        
        proxy.quality_score = (
            uptime_factor * 0.4 +
            response_factor * 0.3 +
            success_factor * 0.3
        )
        
        # Mark as inactive if too many failures
        if proxy.failure_count >= self.max_failures:
            proxy.is_active = False
            self.logger.warning(f"Proxy {proxy.url} marked as inactive due to failures")

class ProxyRotationManager:
    """Manages proxy rotation and service integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or DEFAULT_PROXY_CONFIG
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.health_checker = ProxyHealthChecker()
        self.proxy_pools: Dict[str, List[ProxyInfo]] = {}
        self.active_proxies: List[ProxyInfo] = []
        self.failed_proxies: List[ProxyInfo] = []
        
        # Rate limiting
        self.request_counts: Dict[str, Dict[str, int]] = {}
        self.last_request_time: Dict[str, datetime] = {}
        
        # Geographic targeting
        self.geographic_proxies: Dict[str, List[ProxyInfo]] = {}
        
        # Initialize proxy pools
        self._initialize_proxy_pools()
    
    def _initialize_proxy_pools(self):
        """Initialize proxy pools from different services"""
        for service_name, service_config in PROXY_SERVICES.items():
            if service_config.enabled:
                self.proxy_pools[service_name] = []
                self.request_counts[service_name] = {
                    'minute': 0,
                    'hour': 0,
                    'last_minute': datetime.now(),
                    'last_hour': datetime.now()
                }
                self.last_request_time[service_name] = datetime.now()
    
    async def add_proxy(self, proxy_info: ProxyInfo, service: str = "manual"):
        """Add a proxy to the pool"""
        if service not in self.proxy_pools:
            self.proxy_pools[service] = []
        
        # Check if proxy already exists
        existing = next((p for p in self.proxy_pools[service] if p.id == proxy_info.id), None)
        if existing:
            self.logger.debug(f"Proxy {proxy_info.url} already exists in {service}")
            return
        
        # Add to pool
        self.proxy_pools[service].append(proxy_info)
        
        # Add to geographic mapping
        if proxy_info.country != "unknown":
            if proxy_info.country not in self.geographic_proxies:
                self.geographic_proxies[proxy_info.country] = []
            self.geographic_proxies[proxy_info.country].append(proxy_info)
        
        self.logger.info(f"Added proxy {proxy_info.url} to {service} pool")
    
    async def get_proxy(self, 
                        service: str = None, 
                        country: str = None, 
                        strategy: str = None) -> Optional[ProxyInfo]:
        """Get a proxy based on strategy and requirements"""
        strategy = strategy or self.config['rotation_strategy']
        
        if strategy == "geographic":
            return await self._get_geographic_proxy(country)
        elif strategy == "round_robin":
            return await self._get_round_robin_proxy(service)
        elif strategy == "random":
            return await self._get_random_proxy(service)
        elif strategy == "failover":
            return await self._get_failover_proxy(service)
        else:
            return await self._get_best_proxy(service)
    
    async def _get_geographic_proxy(self, country: str) -> Optional[ProxyInfo]:
        """Get proxy from specific geographic location"""
        if not country:
            country = GEOGRAPHIC_TARGETING['default_location']
        
        available_proxies = self.geographic_proxies.get(country, [])
        if not available_proxies:
            self.logger.warning(f"No proxies available for country: {country}")
            return None
        
        # Get best proxy by quality score
        best_proxy = max(available_proxies, key=lambda p: p.quality_score)
        if best_proxy.is_active and best_proxy.quality_score >= 0.6:
            return best_proxy
        
        return None
    
    async def _get_round_robin_proxy(self, service: str) -> Optional[ProxyInfo]:
        """Get proxy using round-robin strategy"""
        if service and service in self.proxy_pools:
            proxies = [p for p in self.proxy_pools[service] if p.is_active]
            if proxies:
                # Simple round-robin
                proxy = proxies[0]
                self.proxy_pools[service].remove(proxy)
                self.proxy_pools[service].append(proxy)
                return proxy
        
        # Fallback to any available proxy
        all_proxies = [p for pool in self.proxy_pools.values() for p in pool if p.is_active]
        if all_proxies:
            return random.choice(all_proxies)
        
        return None
    
    async def _get_random_proxy(self, service: str) -> Optional[ProxyInfo]:
        """Get random proxy"""
        if service and service in self.proxy_pools:
            proxies = [p for p in self.proxy_pools[service] if p.is_active]
            if proxies:
                return random.choice(proxies)
        
        # Fallback to any available proxy
        all_proxies = [p for pool in self.proxy_pools.values() for p in pool if p.is_active]
        if all_proxies:
            return random.choice(all_proxies)
        
        return None
    
    async def _get_failover_proxy(self, service: str) -> Optional[ProxyInfo]:
        """Get proxy using failover strategy (best quality first)"""
        all_proxies = []
        for pool_name, pool in self.proxy_pools.items():
            if not service or pool_name == service:
                all_proxies.extend([p for p in pool if p.is_active])
        
        if not all_proxies:
            return None
        
        # Sort by quality score and return best
        all_proxies.sort(key=lambda p: p.quality_score, reverse=True)
        return all_proxies[0]
    
    async def _get_best_proxy(self, service: str) -> Optional[ProxyInfo]:
        """Get best proxy based on quality score and availability"""
        return await self._get_failover_proxy(service)
    
    async def mark_proxy_failed(self, proxy: ProxyInfo, error: str = None):
        """Mark a proxy as failed"""
        proxy.failure_count += 1
        proxy.last_checked = datetime.now()
        
        if error:
            self.logger.warning(f"Proxy {proxy.url} failed: {error}")
        
        # Update quality score
        self.health_checker.update_proxy_score(proxy, False, float('inf'))
        
        # Move to failed list if too many failures
        if proxy.failure_count >= self.config['max_failures']:
            if proxy in self.active_proxies:
                self.active_proxies.remove(proxy)
            self.failed_proxies.append(proxy)
            self.logger.warning(f"Proxy {proxy.url} moved to failed list")
    
    async def mark_proxy_success(self, proxy: ProxyInfo, response_time: float):
        """Mark a proxy as successful"""
        proxy.success_count += 1
        proxy.last_used = datetime.now()
        proxy.response_time = response_time
        
        # Update quality score
        self.health_checker.update_proxy_score(proxy, True, response_time)
        
        # Move back to active if it was in failed list
        if proxy in self.failed_proxies:
            self.failed_proxies.remove(proxy)
            self.active_proxies.append(proxy)
    
    async def refresh_proxy_pools(self):
        """Refresh proxy pools from services"""
        for service_name, service_config in PROXY_SERVICES.items():
            if not service_config.enabled:
                continue
            
            try:
                if service_name == "scraperapi":
                    await self._refresh_scraperapi_pool(service_config)
                elif service_name == "brightdata":
                    await self._refresh_brightdata_pool(service_config)
                elif service_name == "oxylabs":
                    await self._refresh_oxylabs_pool(service_config)
                elif service_name == "free_proxies":
                    await self._refresh_free_proxy_pool(service_config)
                    
            except Exception as e:
                self.logger.error(f"Failed to refresh {service_name} pool: {e}")
    
    async def _refresh_scraperapi_pool(self, service_config):
        """Refresh ScraperAPI proxy pool"""
        try:
            # ScraperAPI uses a single proxy endpoint with different country parameters
            # We create multiple proxy configurations for different countries
            api_key = service_config.api_key
            
            # Create proxy configurations for different countries
            for country in service_config.geographic_targets[:10]:  # Limit to 10 countries
                proxy_info = ProxyInfo(
                    id=f"scraperapi_{country}",
                    host="proxy.scraperapi.com",
                    port=8081,
                    protocol="http",
                    username="scraperapi",
                    password=api_key,
                    country=country,
                    quality_score=0.9  # High quality score for ScraperAPI
                )
                await self.add_proxy(proxy_info, "scraperapi")
                
            self.logger.info(f"Added {len(service_config.geographic_targets[:10])} ScraperAPI proxies")
                        
        except Exception as e:
            self.logger.error(f"Failed to refresh ScraperAPI pool: {e}")
    
    async def _refresh_brightdata_pool(self, service_config):
        """Refresh Bright Data proxy pool"""
        try:
            # Bright Data typically provides static proxy endpoints
            # Add them to the pool if not already present
            username = service_config.authentication['username']
            password = service_config.authentication['password']
            
            for country in service_config.geographic_targets[:5]:  # Limit to 5 countries
                proxy_info = ProxyInfo(
                    host="brd.superproxy.io",
                    port=22225,
                    protocol="http",
                    username=username,
                    password=password,
                    country=country
                )
                await self.add_proxy(proxy_info, "brightdata")
                
        except Exception as e:
            self.logger.error(f"Failed to refresh Bright Data pool: {e}")
    
    async def _refresh_oxylabs_pool(self, service_config):
        """Refresh Oxylabs proxy pool"""
        try:
            username = service_config.authentication['username']
            password = service_config.authentication['password']
            
            for country in service_config.geographic_targets[:5]:
                proxy_info = ProxyInfo(
                    host="pr.oxylabs.io",
                    port=7777,
                    protocol="http",
                    username=username,
                    password=password,
                    country=country
                )
                await self.add_proxy(proxy_info, "oxylabs")
                
        except Exception as e:
            self.logger.error(f"Failed to refresh Oxylabs pool: {e}")
    
    async def _refresh_free_proxy_pool(self, service_config):
        """Refresh free proxy pool from public sources"""
        try:
            async with aiohttp.ClientSession() as session:
                for source_url in FREE_PROXY_SOURCES:
                    try:
                        async with session.get(source_url, timeout=10) as response:
                            if response.status == 200:
                                content = await response.text()
                                proxies = self._parse_free_proxy_list(content)
                                
                                for proxy_str in proxies[:20]:  # Limit to 20 proxies
                                    try:
                                        proxy_info = self._parse_proxy_string(proxy_str)
                                        if proxy_info:
                                            await self.add_proxy(proxy_info, "free_proxies")
                                    except Exception as e:
                                        continue
                                        
                    except Exception as e:
                        self.logger.debug(f"Failed to fetch from {source_url}: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Failed to refresh free proxy pool: {e}")
    
    def _parse_free_proxy_list(self, content: str) -> List[str]:
        """Parse free proxy list content"""
        lines = content.strip().split('\n')
        proxies = []
        
        for line in lines:
            line = line.strip()
            if ':' in line and len(line.split(':')) == 2:
                proxies.append(line)
        
        return proxies
    
    def _parse_proxy_string(self, proxy_str: str) -> Optional[ProxyInfo]:
        """Parse proxy string into ProxyInfo object"""
        try:
            if '://' in proxy_str:
                protocol, rest = proxy_str.split('://', 1)
            else:
                protocol = 'http'
                rest = proxy_str
            
            if '@' in rest:
                auth, host_port = rest.split('@', 1)
                username, password = auth.split(':', 1)
                host, port = host_port.split(':', 1)
            else:
                username = password = None
                host, port = rest.split(':', 1)
            
            return ProxyInfo(
                host=host,
                port=int(port),
                protocol=protocol,
                username=username,
                password=password
            )
            
        except Exception as e:
            self.logger.debug(f"Failed to parse proxy string {proxy_str}: {e}")
            return None
    
    async def health_check_all_proxies(self):
        """Perform health check on all proxies"""
        self.logger.info("Starting proxy health check...")
        
        for service_name, proxy_list in self.proxy_pools.items():
            for proxy in proxy_list:
                if proxy.is_active:
                    try:
                        is_healthy, response_time = await self.health_checker.check_proxy_health(proxy)
                        if is_healthy:
                            await self.mark_proxy_success(proxy, response_time)
                        else:
                            await self.mark_proxy_failed(proxy, "Health check failed")
                    except Exception as e:
                        await self.mark_proxy_failed(proxy, str(e))
        
        self.logger.info("Proxy health check completed")
    
    def get_proxy_statistics(self) -> Dict[str, Any]:
        """Get statistics about proxy pools"""
        stats = {
            'total_proxies': 0,
            'active_proxies': 0,
            'failed_proxies': len(self.failed_proxies),
            'services': {},
            'geographic_distribution': {},
            'quality_distribution': {
                'excellent': 0,
                'good': 0,
                'fair': 0,
                'poor': 0
            }
        }
        
        for service_name, proxy_list in self.proxy_pools.items():
            active_count = len([p for p in proxy_list if p.is_active])
            total_count = len(proxy_list)
            
            stats['services'][service_name] = {
                'total': total_count,
                'active': active_count,
                'failed': total_count - active_count
            }
            
            stats['total_proxies'] += total_count
            stats['active_proxies'] += active_count
        
        # Geographic distribution
        for country, proxies in self.geographic_proxies.items():
            active_count = len([p for p in proxies if p.is_active])
            if active_count > 0:
                stats['geographic_distribution'][country] = active_count
        
        # Quality distribution
        for proxy_list in self.proxy_pools.values():
            for proxy in proxy_list:
                if proxy.is_active:
                    if proxy.quality_score >= 0.8:
                        stats['quality_distribution']['excellent'] += 1
                    elif proxy.quality_score >= 0.6:
                        stats['quality_distribution']['good'] += 1
                    elif proxy.quality_score >= 0.4:
                        stats['quality_distribution']['fair'] += 1
                    else:
                        stats['quality_distribution']['poor'] += 1
        
        return stats
    
    async def cleanup(self):
        """Cleanup resources"""
        # Remove inactive proxies
        for service_name, proxy_list in self.proxy_pools.items():
            self.proxy_pools[service_name] = [p for p in proxy_list if p.is_active]
        
        # Clear failed proxies older than 1 hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.failed_proxies = [p for p in self.failed_proxies if p.last_checked > cutoff_time]
