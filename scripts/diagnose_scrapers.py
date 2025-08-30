#!/usr/bin/env python3
"""
JobPulse Scraper Diagnostic Script
Systematically tests each scraper to identify why they might be failing
and provides clear next steps for fixing them.
"""

import sys
import os
import asyncio
import time
import requests
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ScraperDiagnostic:
    """Diagnostic tool for JobPulse scrapers"""
    
    def __init__(self):
        self.results = []
        self.screenshot_dir = Path("diagnostic_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
    def print_header(self):
        """Print diagnostic header"""
        print("🔍 JobPulse Scraper Diagnostic Tool")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("This script will test each scraper systematically to identify issues.")
        print()
    
    def test_dice_scraper(self):
        """Test Dice scraper connectivity and selectors"""
        print("🧪 Testing Dice Scraper...")
        
        try:
            # Test 1: Basic connectivity
            print("  📡 Testing connectivity...")
            response = requests.get("https://www.dice.com/jobs?q=python&location=United+States", 
                                 timeout=10, 
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
            
            if response.status_code == 200:
                print("    ✅ HTTP 200 - Site accessible")
                connectivity_status = "✅ Working"
            else:
                print(f"    ⚠️ HTTP {response.status_code} - Site may have issues")
                connectivity_status = "⚠️ Needs Fixing"
            
            # Test 2: Check if expected content exists
            print("  🔍 Checking page content...")
            if "card-body" in response.text:
                print("    ✅ Expected 'card-body' class found in HTML")
                content_status = "✅ Working"
            else:
                print("    ❌ Expected 'card-body' class NOT found in HTML")
                content_status = "❌ Broken"
            
            # Test 3: Check for job listings
            if "job" in response.text.lower() and "python" in response.text.lower():
                print("    ✅ Job-related content detected")
                job_content_status = "✅ Working"
            else:
                print("    ⚠️ Limited job content detected")
                job_content_status = "⚠️ Needs Fixing"
            
            # Overall status
            if all(status.startswith("✅") for status in [connectivity_status, content_status, job_content_status]):
                overall_status = "✅ Working"
                specific_issue = "No issues detected"
                recommended_fix = "Scraper should work correctly"
            elif any(status.startswith("❌") for status in [connectivity_status, content_status, job_content_status]):
                overall_status = "❌ Broken"
                specific_issue = "Page structure has changed or site is blocking access"
                recommended_fix = "Update HTML selectors and check for anti-bot measures"
            else:
                overall_status = "⚠️ Needs Fixing"
                specific_issue = "Site accessible but content structure may have changed"
                recommended_fix = "Verify current HTML structure and update selectors"
            
            self.results.append({
                'scraper': 'Dice',
                'status': overall_status,
                'specific_issue': specific_issue,
                'recommended_fix': recommended_fix,
                'details': {
                    'connectivity': connectivity_status,
                    'content': content_status,
                    'job_content': job_content_status
                }
            })
            
        except Exception as e:
            print(f"    ❌ Error testing Dice: {e}")
            self.results.append({
                'scraper': 'Dice',
                'status': '❌ Broken',
                'specific_issue': f'Connection failed: {str(e)}',
                'recommended_fix': 'Check network connectivity and site availability',
                'details': {'error': str(e)}
            })
        
        print()
    
    def test_stackoverflow_scraper(self):
        """Test Stack Overflow scraper connectivity and selectors"""
        print("🧪 Testing Stack Overflow Scraper...")
        
        try:
            # Test 1: Basic connectivity
            print("  📡 Testing connectivity...")
            response = requests.get("https://stackoverflowjobs.com/jobs?q=python&l=United+States", 
                                 timeout=10,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
            
            if response.status_code == 200:
                print("    ✅ HTTP 200 - Site accessible")
                connectivity_status = "✅ Working"
            else:
                print(f"    ⚠️ HTTP {response.status_code} - Site may have issues")
                connectivity_status = "⚠️ Needs Fixing"
            
            # Test 2: Check if expected content exists
            print("  🔍 Checking page content...")
            if "job-result" in response.text:
                print("    ✅ Expected 'job-result' class found in HTML")
                content_status = "✅ Working"
            else:
                print("    ❌ Expected 'job-result' class NOT found in HTML")
                content_status = "❌ Broken"
            
            # Test 3: Check for job listings
            if "job" in response.text.lower() and "python" in response.text.lower():
                print("    ✅ Job-related content detected")
                job_content_status = "✅ Working"
            else:
                print("    ⚠️ Limited job content detected")
                job_content_status = "⚠️ Needs Fixing"
            
            # Overall status
            if all(status.startswith("✅") for status in [connectivity_status, content_status, job_content_status]):
                overall_status = "✅ Working"
                specific_issue = "No issues detected"
                recommended_fix = "Scraper should work correctly"
            elif any(status.startswith("❌") for status in [connectivity_status, content_status, job_content_status]):
                overall_status = "❌ Broken"
                specific_issue = "Page structure has changed or site is blocking access"
                recommended_fix = "Update HTML selectors and check for anti-bot measures"
            else:
                overall_status = "⚠️ Needs Fixing"
                specific_issue = "Site accessible but content structure may have changed"
                recommended_fix = "Verify current HTML structure and update selectors"
            
            self.results.append({
                'scraper': 'Stack Overflow',
                'status': overall_status,
                'specific_issue': specific_issue,
                'recommended_fix': recommended_fix,
                'details': {
                    'connectivity': connectivity_status,
                    'content': content_status,
                    'job_content': job_content_status
                }
            })
            
        except Exception as e:
            print(f"    ❌ Error testing Stack Overflow: {e}")
            self.results.append({
                'scraper': 'Stack Overflow',
                'status': '❌ Broken',
                'specific_issue': f'Connection failed: {str(e)}',
                'recommended_fix': 'Check network connectivity and site availability',
                'details': {'error': str(e)}
            })
        
        print()
    
    def test_greenhouse_scraper(self):
        """Test Greenhouse scraper API endpoints"""
        print("🧪 Testing Greenhouse Scraper...")
        
        # Test companies from the scraper
        test_companies = [
            'airbnb', 'uber', 'lyft', 'pinterest', 'stripe', 'coinbase',
            'robinhood', 'doordash', 'instacart', 'notion', 'figma',
            'linear', 'vercel', 'netlify', 'supabase', 'planetscale',
            'github', 'shopify', 'twilio', 'slack', 'discord', 'zoom'
        ]
        
        working_companies = []
        broken_companies = []
        
        print("  📡 Testing API endpoints for companies...")
        
        for company in test_companies:
            try:
                api_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    jobs_data = response.json()
                    job_count = len(jobs_data.get('jobs', []))
                    print(f"    ✅ {company}: {job_count} jobs available")
                    working_companies.append(company)
                elif response.status_code == 404:
                    print(f"    ❌ {company}: Company not found (404)")
                    broken_companies.append(company)
                else:
                    print(f"    ⚠️ {company}: HTTP {response.status_code}")
                    broken_companies.append(company)
                
                # Small delay to be respectful
                time.sleep(0.1)
                
            except Exception as e:
                print(f"    ❌ {company}: Error - {e}")
                broken_companies.append(company)
        
        # Calculate success rate
        total_companies = len(test_companies)
        working_count = len(working_companies)
        success_rate = (working_count / total_companies) * 100
        
        print(f"  📊 Results: {working_count}/{total_companies} companies working ({success_rate:.1f}%)")
        
        # Determine overall status
        if success_rate >= 80:
            overall_status = "✅ Working"
            specific_issue = f"Most companies working ({success_rate:.1f}% success rate)"
            recommended_fix = "Scraper should work well with current company list"
        elif success_rate >= 50:
            overall_status = "⚠️ Needs Fixing"
            specific_issue = f"Moderate success rate ({success_rate:.1f}%) - some companies broken"
            recommended_fix = "Update company list to remove broken companies"
        else:
            overall_status = "❌ Broken"
            specific_issue = f"Low success rate ({success_rate:.1f}%) - most companies broken"
            recommended_fix = "Research current working company identifiers and update list"
        
        self.results.append({
            'scraper': 'Greenhouse',
            'status': overall_status,
            'specific_issue': specific_issue,
            'recommended_fix': recommended_fix,
            'details': {
                'working_companies': working_companies,
                'broken_companies': broken_companies,
                'success_rate': success_rate
            }
        })
        
        print()
    
    def test_lever_scraper(self):
        """Test Lever scraper API endpoints"""
        print("🧪 Testing Lever Scraper...")
        
        # Test companies from the scraper
        test_companies = [
            'stripe', 'coinbase', 'robinhood', 'doordash', 'instacart',
            'notion', 'figma', 'linear', 'vercel', 'netlify', 'supabase',
            'planetscale', 'github', 'shopify', 'twilio', 'slack'
        ]
        
        working_companies = []
        broken_companies = []
        
        print("  📡 Testing API endpoints for companies...")
        
        for company in test_companies:
            try:
                api_url = f"https://api.lever.co/v0/postings/{company}"
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    jobs_data = response.json()
                    job_count = len(jobs_data)
                    print(f"    ✅ {company}: {job_count} jobs available")
                    working_companies.append(company)
                elif response.status_code == 404:
                    print(f"    ❌ {company}: Company not found (404)")
                    broken_companies.append(company)
                else:
                    print(f"    ⚠️ {company}: HTTP {response.status_code}")
                    broken_companies.append(company)
                
                # Small delay to be respectful
                time.sleep(0.1)
                
            except Exception as e:
                print(f"    ❌ {company}: Error - {e}")
                broken_companies.append(company)
        
        # Calculate success rate
        total_companies = len(test_companies)
        working_count = len(working_companies)
        success_rate = (working_count / total_companies) * 100
        
        print(f"  📊 Results: {working_count}/{total_companies} companies working ({success_rate:.1f}%)")
        
        # Determine overall status
        if success_rate >= 80:
            overall_status = "✅ Working"
            specific_issue = f"Most companies working ({success_rate:.1f}% success rate)"
            recommended_fix = "Scraper should work well with current company list"
        elif success_rate >= 50:
            overall_status = "⚠️ Needs Fixing"
            specific_issue = f"Moderate success rate ({success_rate:.1f}%) - some companies broken"
            recommended_fix = "Update company list to remove broken companies"
        else:
            overall_status = "❌ Broken"
            specific_issue = f"Low success rate ({success_rate:.1f}%) - most companies broken"
            recommended_fix = "Research current working company identifiers and update list"
        
        self.results.append({
            'scraper': 'Lever',
            'status': overall_status,
            'specific_issue': specific_issue,
            'recommended_fix': recommended_fix,
            'details': {
                'working_companies': working_companies,
                'broken_companies': broken_companies,
                'success_rate': success_rate
            }
        })
        
        print()
    
    async def test_playwright_selectors(self):
        """Test Playwright selectors for Dice and Stack Overflow"""
        print("🌐 Testing Playwright Selectors...")
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                
                # Test Dice
                print("  🎯 Testing Dice selectors...")
                try:
                    page = await browser.new_page()
                    await page.goto("https://www.dice.com/jobs?q=python&location=United+States", timeout=30000)
                    await page.wait_for_load_state('networkidle')
                    
                    # Take screenshot
                    screenshot_path = self.screenshot_dir / "dice_jobs_page.png"
                    await page.screenshot(path=str(screenshot_path))
                    print(f"    📸 Screenshot saved: {screenshot_path}")
                    
                    # Test selectors
                    selectors_to_test = [
                        'div.card-body',
                        'h5.card-title',
                        'span.company',
                        'span.location',
                        'a.card-title-link'
                    ]
                    
                    for selector in selectors_to_test:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"    ✅ Selector '{selector}': {len(elements)} elements found")
                        else:
                            print(f"    ❌ Selector '{selector}': No elements found")
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"    ❌ Error testing Dice: {e}")
                
                # Test Stack Overflow
                print("  🎯 Testing Stack Overflow selectors...")
                try:
                    page = await browser.new_page()
                    await page.goto("https://stackoverflowjobs.com/jobs?q=python&l=United+States", timeout=30000)
                    await page.wait_for_load_state('networkidle')
                    
                    # Take screenshot
                    screenshot_path = self.screenshot_dir / "stackoverflow_jobs_page.png"
                    await page.screenshot(path=str(screenshot_path))
                    print(f"    📸 Screenshot saved: {screenshot_path}")
                    
                    # Test selectors
                    selectors_to_test = [
                        'div.job-result',
                        'h2.job-title',
                        'h3.company-name',
                        'span.location',
                        'a.job-link'
                    ]
                    
                    for selector in selectors_to_test:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"    ✅ Selector '{selector}': {len(elements)} elements found")
                        else:
                            print(f"    ❌ Selector '{selector}': No elements found")
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"    ❌ Error testing Stack Overflow: {e}")
                
                await browser.close()
                
        except ImportError:
            print("  ⚠️ Playwright not installed. Install with: pip install playwright")
        except Exception as e:
            print(f"  ❌ Error testing Playwright: {e}")
        
        print()
    
    def print_summary_table(self):
        """Print a summary table of all results"""
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 80)
        print(f"{'Scraper':<20} {'Status':<15} {'Issue':<50}")
        print("-" * 80)
        
        for result in self.results:
            status_icon = result['status'].split()[0]  # Get the emoji
            status_text = result['status'].split()[1]  # Get the text
            issue = result['specific_issue'][:47] + "..." if len(result['specific_issue']) > 50 else result['specific_issue']
            
            print(f"{result['scraper']:<20} {status_icon} {status_text:<12} {issue}")
        
        print("-" * 80)
        print()
    
    def print_detailed_recommendations(self):
        """Print detailed recommendations for each scraper"""
        print("🔧 DETAILED RECOMMENDATIONS")
        print("=" * 80)
        
        for result in self.results:
            print(f"\n📋 {result['scraper']} - {result['status']}")
            print(f"   Issue: {result['specific_issue']}")
            print(f"   Fix: {result['recommended_fix']}")
            
            if 'details' in result:
                if 'working_companies' in result['details']:
                    print(f"   Working Companies: {', '.join(result['details']['working_companies'][:5])}{'...' if len(result['details']['working_companies']) > 5 else ''}")
                    print(f"   Broken Companies: {', '.join(result['details']['broken_companies'][:5])}{'...' if len(result['details']['broken_companies']) > 5 else ''}")
                    print(f"   Success Rate: {result['details']['success_rate']:.1f}%")
                elif 'details' in result['details']:
                    for key, value in result['details'].items():
                        if key != 'error':
                            print(f"   {key.title()}: {value}")
        
        print("\n" + "=" * 80)
    
    def save_report(self):
        """Save the diagnostic report to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"diagnostic_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("JobPulse Scraper Diagnostic Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for result in self.results:
                f.write(f"Scraper: {result['scraper']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Issue: {result['specific_issue']}\n")
                f.write(f"Fix: {result['recommended_fix']}\n")
                f.write("-" * 30 + "\n")
        
        print(f"📄 Detailed report saved to: {report_file}")
    
    async def run_diagnostics(self):
        """Run all diagnostic tests"""
        self.print_header()
        
        # Test each scraper
        self.test_dice_scraper()
        self.test_stackoverflow_scraper()
        self.test_greenhouse_scraper()
        self.test_lever_scraper()
        
        # Test Playwright selectors
        await self.test_playwright_selectors()
        
        # Print results
        self.print_summary_table()
        self.print_detailed_recommendations()
        self.save_report()
        
        print("🎯 NEXT STEPS:")
        print("1. Review the diagnostic results above")
        print("2. Check the screenshots in the 'diagnostic_screenshots' folder")
        print("3. Update company lists for API-based scrapers")
        print("4. Adjust Playwright selectors based on current page structure")
        print("5. Test the updated scrapers individually")
        print("6. Re-run this diagnostic to verify fixes")

async def main():
    """Main function"""
    diagnostic = ScraperDiagnostic()
    await diagnostic.run_diagnostics()

if __name__ == "__main__":
    asyncio.run(main())

