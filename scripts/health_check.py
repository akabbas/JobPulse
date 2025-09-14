#!/usr/bin/env python3
"""
JobPulse System Health Check Dashboard
Real-time monitoring of all data sources and system components
"""

import sys
import os
import time
import asyncio
import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from colorama import init, Fore, Back, Style
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize colorama for cross-platform colored output
init(autoreset=True)

@dataclass
class HealthResult:
    """Health check result for a data source"""
    source_name: str
    status: str  # 'healthy', 'degraded', 'offline'
    jobs_found: int
    response_time: float
    error_message: Optional[str] = None
    test_query: str = "software engineer"
    location: str = "United States"

class JobPulseHealthChecker:
    """Comprehensive health checker for JobPulse system"""
    
    def __init__(self):
        self.base_url = "http://localhost:5002"
        self.results: List[HealthResult] = []
        self.start_time = time.time()
        
        # Define data sources to test
        self.data_sources = [
            {
                'name': 'Greenhouse',
                'description': 'Premium job board with 100% success rate',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['greenhouse']
                }
            },
            {
                'name': 'Remotive',
                'description': 'Remote job platform',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['remotive']
                }
            },
            {
                'name': 'Reddit Jobs',
                'description': 'Reddit job communities',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['reddit']
                }
            },
            {
                'name': 'Jobspresso',
                'description': 'Remote job aggregator',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['jobspresso']
                }
            },
            {
                'name': 'Himalayas',
                'description': 'Remote job platform',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['himalayas']
                }
            },
            {
                'name': 'YC Jobs',
                'description': 'Y Combinator job board',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['yc_jobs']
                }
            },
            {
                'name': 'Authentic Jobs',
                'description': 'Creative and tech jobs',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['authentic_jobs']
                }
            },
            {
                'name': 'Otta',
                'description': 'Tech job platform',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['otta']
                }
            },
            {
                'name': 'Hacker News',
                'description': 'HN Who is Hiring',
                'endpoint': '/search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'location': 'United States',
                    'limit': 10,
                    'sources': ['hackernews']
                }
            },
            {
                'name': 'Skills Network API',
                'description': 'AI-powered skills analysis',
                'endpoint': '/api/skills-network',
                'method': 'GET',
                'data': {}
            },
            {
                'name': 'Enhanced Search (Playwright)',
                'description': 'Browser automation for comprehensive coverage',
                'endpoint': '/enhanced_search',
                'method': 'POST',
                'data': {
                    'keyword': 'software engineer',
                    'limit': 10,
                    'headless': True
                }
            }
        ]
    
    def print_header(self):
        """Print the health check dashboard header"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}{Style.BRIGHT}🚀 JOBPULSE SYSTEM HEALTH CHECK DASHBOARD{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.WHITE}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}Base URL: {self.base_url}")
        print(f"{Fore.CYAN}{'='*80}\n")
    
    def test_data_source(self, source: Dict) -> HealthResult:
        """Test a single data source"""
        source_name = source['name']
        endpoint = source['endpoint']
        method = source['method']
        data = source['data']
        
        print(f"{Fore.YELLOW}🔍 Testing {source_name}...{Style.RESET_ALL}", end=" ", flush=True)
        
        start_time = time.time()
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == 'POST':
                response = requests.post(url, json=data, timeout=30)
            else:
                response = requests.get(url, params=data, timeout=30)
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                if 'jobs' in response_data:
                    jobs_found = len(response_data.get('jobs', []))
                    total_jobs = response_data.get('total_jobs', 0)
                    
                    # Determine status based on jobs found and response time
                    if jobs_found >= 5 and response_time < 5:
                        status = 'healthy'
                        print(f"{Fore.GREEN}✅ HEALTHY{Style.RESET_ALL}")
                    elif jobs_found >= 1 and response_time < 10:
                        status = 'degraded'
                        print(f"{Fore.YELLOW}⚠️  DEGRADED{Style.RESET_ALL}")
                    else:
                        status = 'offline'
                        print(f"{Fore.RED}❌ OFFLINE{Style.RESET_ALL}")
                    
                    return HealthResult(
                        source_name=source_name,
                        status=status,
                        jobs_found=jobs_found,
                        response_time=response_time,
                        test_query=data.get('keyword', 'software engineer')
                    )
                
                elif 'data' in response_data:
                    # Skills Network API response
                    data_source = response_data.get('data', {}).get('data_source', 'unknown')
                    if data_source == 'real_jobs':
                        status = 'healthy'
                        print(f"{Fore.GREEN}✅ HEALTHY{Style.RESET_ALL}")
                    else:
                        status = 'degraded'
                        print(f"{Fore.YELLOW}⚠️  DEGRADED{Style.RESET_ALL}")
                    
                    return HealthResult(
                        source_name=source_name,
                        status=status,
                        jobs_found=1,  # Skills network doesn't return job count
                        response_time=response_time,
                        test_query="skills analysis"
                    )
                
                else:
                    status = 'offline'
                    print(f"{Fore.RED}❌ OFFLINE{Style.RESET_ALL}")
                    return HealthResult(
                        source_name=source_name,
                        status=status,
                        jobs_found=0,
                        response_time=response_time,
                        error_message="Invalid response format"
                    )
            
            else:
                status = 'offline'
                print(f"{Fore.RED}❌ OFFLINE{Style.RESET_ALL}")
                return HealthResult(
                    source_name=source_name,
                    status=status,
                    jobs_found=0,
                    response_time=response_time,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            status = 'offline'
            print(f"{Fore.RED}❌ TIMEOUT{Style.RESET_ALL}")
            return HealthResult(
                source_name=source_name,
                status=status,
                jobs_found=0,
                response_time=30.0,
                error_message="Request timeout"
            )
            
        except requests.exceptions.ConnectionError:
            status = 'offline'
            print(f"{Fore.RED}❌ CONNECTION ERROR{Style.RESET_ALL}")
            return HealthResult(
                source_name=source_name,
                status=status,
                jobs_found=0,
                response_time=time.time() - start_time,
                error_message="Connection failed"
            )
            
        except Exception as e:
            status = 'offline'
            print(f"{Fore.RED}❌ ERROR{Style.RESET_ALL}")
            return HealthResult(
                source_name=source_name,
                status=status,
                jobs_found=0,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def run_health_checks(self) -> List[HealthResult]:
        """Run health checks for all data sources"""
        print(f"{Fore.CYAN}🔄 Running health checks for {len(self.data_sources)} data sources...{Style.RESET_ALL}\n")
        
        # Use ThreadPoolExecutor for concurrent testing
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(self.test_data_source, source): source 
                for source in self.data_sources
            }
            
            for future in as_completed(future_to_source):
                result = future.result()
                self.results.append(result)
        
        return self.results
    
    def print_results_table(self):
        """Print a beautiful results table"""
        print(f"\n{Fore.CYAN}{'='*100}")
        print(f"{Fore.CYAN}{Style.BRIGHT}📊 HEALTH CHECK RESULTS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*100}")
        
        # Table header
        print(f"{Fore.WHITE}{Style.BRIGHT}")
        print(f"{'Source':<25} {'Status':<12} {'Jobs':<8} {'Response':<10} {'Details':<30}")
        print(f"{'-'*25} {'-'*12} {'-'*8} {'-'*10} {'-'*30}")
        print(f"{Style.RESET_ALL}")
        
        # Table rows
        for result in self.results:
            # Status color coding
            if result.status == 'healthy':
                status_color = Fore.GREEN
                status_icon = "✅"
            elif result.status == 'degraded':
                status_color = Fore.YELLOW
                status_icon = "⚠️ "
            else:
                status_color = Fore.RED
                status_icon = "❌"
            
            # Format response time
            response_time_str = f"{result.response_time:.2f}s"
            
            # Format details
            details = result.error_message if result.error_message else f"Query: {result.test_query}"
            if len(details) > 28:
                details = details[:25] + "..."
            
            print(f"{Fore.WHITE}{result.source_name:<25} {status_color}{status_icon}{result.status.upper():<10} {result.jobs_found:<8} {response_time_str:<10} {details:<30}{Style.RESET_ALL}")
    
    def print_summary_stats(self):
        """Print summary statistics"""
        print(f"\n{Fore.CYAN}{'='*100}")
        print(f"{Fore.CYAN}{Style.BRIGHT}📈 SUMMARY STATISTICS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*100}")
        
        total_sources = len(self.results)
        healthy_sources = len([r for r in self.results if r.status == 'healthy'])
        degraded_sources = len([r for r in self.results if r.status == 'degraded'])
        offline_sources = len([r for r in self.results if r.status == 'offline'])
        
        total_jobs = sum(r.jobs_found for r in self.results)
        avg_response_time = sum(r.response_time for r in self.results) / total_sources if total_sources > 0 else 0
        
        # Calculate health score (0-100)
        health_score = (healthy_sources * 100 + degraded_sources * 50) / total_sources if total_sources > 0 else 0
        
        print(f"{Fore.WHITE}{Style.BRIGHT}")
        print(f"🏥 Overall Health Score: {self.get_health_score_color(health_score)}{health_score:.1f}%{Style.RESET_ALL}")
        print(f"⏱️  Total Check Time: {time.time() - self.start_time:.2f} seconds")
        print(f"📊 Total Jobs Found: {total_jobs}")
        print(f"⚡ Average Response Time: {avg_response_time:.2f} seconds")
        print(f"{Style.RESET_ALL}")
        
        print(f"\n{Fore.WHITE}{Style.BRIGHT}Source Status Breakdown:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Healthy Sources: {healthy_sources}/{total_sources} ({healthy_sources/total_sources*100:.1f}%){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Degraded Sources: {degraded_sources}/{total_sources} ({degraded_sources/total_sources*100:.1f}%){Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Offline Sources: {offline_sources}/{total_sources} ({offline_sources/total_sources*100:.1f}%){Style.RESET_ALL}")
    
    def get_health_score_color(self, score: float) -> str:
        """Get color for health score"""
        if score >= 80:
            return f"{Fore.GREEN}{Style.BRIGHT}"
        elif score >= 60:
            return f"{Fore.YELLOW}{Style.BRIGHT}"
        else:
            return f"{Fore.RED}{Style.BRIGHT}"
    
    def print_recommendations(self):
        """Print recommendations based on health check results"""
        print(f"\n{Fore.CYAN}{'='*100}")
        print(f"{Fore.CYAN}{Style.BRIGHT}💡 RECOMMENDATIONS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*100}")
        
        offline_sources = [r for r in self.results if r.status == 'offline']
        degraded_sources = [r for r in self.results if r.status == 'degraded']
        
        if offline_sources:
            print(f"{Fore.RED}🚨 Critical Issues:{Style.RESET_ALL}")
            for source in offline_sources:
                print(f"  • {source.source_name}: {source.error_message or 'No response'}")
            print()
        
        if degraded_sources:
            print(f"{Fore.YELLOW}⚠️  Performance Issues:{Style.RESET_ALL}")
            for source in degraded_sources:
                print(f"  • {source.source_name}: Slow response ({source.response_time:.2f}s) or few jobs ({source.jobs_found})")
            print()
        
        healthy_sources = [r for r in self.results if r.status == 'healthy']
        if healthy_sources:
            print(f"{Fore.GREEN}✅ Well Performing Sources:{Style.RESET_ALL}")
            for source in healthy_sources:
                print(f"  • {source.source_name}: {source.jobs_found} jobs in {source.response_time:.2f}s")
            print()
        
        # Overall recommendation
        total_sources = len(self.results)
        healthy_percentage = len(healthy_sources) / total_sources * 100
        
        if healthy_percentage >= 80:
            print(f"{Fore.GREEN}🎉 System Status: EXCELLENT - {healthy_percentage:.1f}% of sources are healthy{Style.RESET_ALL}")
        elif healthy_percentage >= 60:
            print(f"{Fore.YELLOW}📊 System Status: GOOD - {healthy_percentage:.1f}% of sources are healthy{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}🚨 System Status: NEEDS ATTENTION - Only {healthy_percentage:.1f}% of sources are healthy{Style.RESET_ALL}")
    
    def print_footer(self):
        """Print the dashboard footer"""
        print(f"\n{Fore.CYAN}{'='*100}")
        print(f"{Fore.CYAN}{Style.BRIGHT}🏁 HEALTH CHECK COMPLETED{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.CYAN}Total Duration: {time.time() - self.start_time:.2f} seconds")
        print(f"{Fore.CYAN}{'='*100}\n")
    
    def run_full_health_check(self):
        """Run the complete health check dashboard"""
        try:
            self.print_header()
            self.run_health_checks()
            self.print_results_table()
            self.print_summary_stats()
            self.print_recommendations()
            self.print_footer()
            
            # Return exit code based on health
            healthy_sources = len([r for r in self.results if r.status == 'healthy'])
            total_sources = len(self.results)
            health_percentage = healthy_sources / total_sources * 100
            
            if health_percentage >= 60:
                return 0  # Success
            else:
                return 1  # Warning
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Health check interrupted by user{Style.RESET_ALL}")
            return 1
        except Exception as e:
            print(f"\n{Fore.RED}❌ Health check failed: {e}{Style.RESET_ALL}")
            return 2

def main():
    """Main function"""
    print(f"{Fore.CYAN}🚀 Starting JobPulse System Health Check...{Style.RESET_ALL}")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5002/", timeout=5)
        if response.status_code != 200:
            print(f"{Fore.RED}❌ JobPulse server is not responding properly{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Make sure the server is running: python web_dashboard/app.py{Style.RESET_ALL}")
            return 1
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}❌ Cannot connect to JobPulse server{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Make sure the server is running: python web_dashboard/app.py{Style.RESET_ALL}")
        return 1
    
    # Run health check
    checker = JobPulseHealthChecker()
    return checker.run_full_health_check()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)





