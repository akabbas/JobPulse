#!/usr/bin/env python3
"""
JobPulse System Health Check Dashboard - DEMO VERSION
Shows how the health check would look with a working system
"""

import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from colorama import init, Fore, Back, Style

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

class JobPulseHealthCheckerDemo:
    """Demo health checker showing expected results"""
    
    def __init__(self):
        self.results: List[HealthResult] = []
        self.start_time = time.time()
        
        # Demo results showing a healthy system
        self.demo_results = [
            HealthResult("Greenhouse", "healthy", 8, 1.23, test_query="software engineer"),
            HealthResult("Remotive", "healthy", 12, 2.45, test_query="software engineer"),
            HealthResult("Reddit Jobs", "healthy", 15, 1.87, test_query="software engineer"),
            HealthResult("Jobspresso", "healthy", 6, 2.12, test_query="software engineer"),
            HealthResult("Himalayas", "healthy", 9, 1.95, test_query="software engineer"),
            HealthResult("YC Jobs", "degraded", 3, 4.23, test_query="software engineer"),
            HealthResult("Authentic Jobs", "healthy", 7, 2.34, test_query="software engineer"),
            HealthResult("Otta", "healthy", 11, 1.76, test_query="software engineer"),
            HealthResult("Hacker News", "healthy", 18, 2.89, test_query="software engineer"),
            HealthResult("Skills Network API", "healthy", 1, 0.95, test_query="skills analysis"),
            HealthResult("Enhanced Search (Playwright)", "healthy", 14, 8.45, test_query="software engineer"),
        ]
    
    def print_header(self):
        """Print the health check dashboard header"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}{Style.BRIGHT}🚀 JOBPULSE SYSTEM HEALTH CHECK DASHBOARD{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.WHITE}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}Base URL: http://localhost:5002")
        print(f"{Fore.YELLOW}⚠️  DEMO MODE - Showing expected results{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}\n")
    
    def simulate_health_checks(self):
        """Simulate running health checks"""
        print(f"{Fore.CYAN}🔄 Running health checks for {len(self.demo_results)} data sources...{Style.RESET_ALL}\n")
        
        for i, result in enumerate(self.demo_results):
            # Simulate testing delay
            time.sleep(0.1)
            
            print(f"{Fore.YELLOW}🔍 Testing {result.source_name}...{Style.RESET_ALL}", end=" ", flush=True)
            
            if result.status == 'healthy':
                print(f"{Fore.GREEN}✅ HEALTHY{Style.RESET_ALL}")
            elif result.status == 'degraded':
                print(f"{Fore.YELLOW}⚠️  DEGRADED{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ OFFLINE{Style.RESET_ALL}")
            
            self.results.append(result)
    
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
    
    def print_demo_info(self):
        """Print demo information"""
        print(f"\n{Fore.YELLOW}{'='*100}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}📋 DEMO INFORMATION{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*100}")
        print(f"{Fore.WHITE}")
        print(f"🎯 This is a demo showing how the health check dashboard would look with a fully operational system.")
        print(f"🚀 To run the real health check:")
        print(f"   1. Start the JobPulse server: python web_dashboard/app.py")
        print(f"   2. Run the health check: python scripts/health_check.py")
        print(f"")
        print(f"📊 Key Features Demonstrated:")
        print(f"   • Real-time testing of all data sources")
        print(f"   • Color-coded status indicators (✅ Healthy, ⚠️ Degraded, ❌ Offline)")
        print(f"   • Response time and job count metrics")
        print(f"   • Overall system health score")
        print(f"   • Actionable recommendations")
        print(f"   • Professional dashboard layout")
        print(f"{Style.RESET_ALL}")
    
    def run_demo(self):
        """Run the complete demo health check dashboard"""
        try:
            self.print_header()
            self.simulate_health_checks()
            self.print_results_table()
            self.print_summary_stats()
            self.print_recommendations()
            self.print_demo_info()
            self.print_footer()
            
            return 0  # Success
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Demo interrupted by user{Style.RESET_ALL}")
            return 1
        except Exception as e:
            print(f"\n{Fore.RED}❌ Demo failed: {e}{Style.RESET_ALL}")
            return 2

def main():
    """Main function"""
    print(f"{Fore.CYAN}🚀 Starting JobPulse System Health Check Demo...{Style.RESET_ALL}")
    
    # Run demo
    checker = JobPulseHealthCheckerDemo()
    return checker.run_demo()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


