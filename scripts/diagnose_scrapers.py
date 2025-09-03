#!/usr/bin/env python3
"""
Diagnostic Script for LinkedIn and Indeed Scrapers
This script runs the scrapers in debug mode to identify why they're failing
"""

import asyncio
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import scrapers directly to avoid import chain issues
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers'))

class ScraperDiagnostic:
    """Diagnostic tool for LinkedIn and Indeed scrapers"""
    
    def __init__(self):
        self.setup_logging()
        self.diagnostic_dir = Path("diagnostic_output")
        self.diagnostic_dir.mkdir(exist_ok=True)
        
        # Test URLs for each platform
        self.test_urls = {
            'linkedin': 'https://www.linkedin.com/jobs/search?keywords=python%20developer&location=United%20States',
            'indeed': 'https://www.indeed.com/jobs?q=python+developer&l=United+States'
        }
        
        # Expected selectors for each platform
        self.expected_selectors = {
            'linkedin': {
                'job_cards': 'div.base-card',
                'job_title': 'h3.base-search-card__title',
                'company_name': 'h4.base-search-card__subtitle',
                'location': 'span.job-search-card__location',
                'job_link': 'a.base-card__full-link',
                'snippet': 'div.base-search-card__snippet'
            },
            'indeed': {
                'job_cards': 'div.job_seen_beacon',
                'job_title': 'h2.jobTitle',
                'company_name': 'span.companyName',
                'location': 'div.companyLocation',
                'job_link': 'a.jcs-JobTitle',
                'snippet': 'div.job-snippet'
            }
        }
    
    def setup_logging(self):
        """Setup logging for diagnostics"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/scraper_diagnostic.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def diagnose_linkedin_scraper(self):
        """Diagnose LinkedIn scraper issues"""
        print("\n🔍 Diagnosing LinkedIn Scraper...")
        print("=" * 50)
        
        try:
            # Test with Playwright
            await self._test_with_playwright('linkedin')
            
            # Test with requests
            await self._test_with_requests('linkedin')
            
            # Test scraper class
            await self._test_scraper_class('linkedin')
            
        except Exception as e:
            print(f"❌ LinkedIn diagnosis failed: {e}")
            self.logger.error(f"LinkedIn diagnosis error: {e}")
    
    async def diagnose_indeed_scraper(self):
        """Diagnose Indeed scraper issues"""
        print("\n🔍 Diagnosing Indeed Scraper...")
        print("=" * 50)
        
        try:
            # Test with Playwright
            await self._test_with_playwright('indeed')
            
            # Test with requests
            await self._test_with_requests('indeed')
            
            # Test scraper class
            await self._test_scraper_class('indeed')
            
        except Exception as e:
            print(f"❌ Indeed diagnosis failed: {e}")
            self.logger.error(f"Indeed diagnosis error: {e}")
    
    async def _test_with_playwright(self, platform: str):
        """Test scraping with Playwright for visual debugging"""
        print(f"\n📱 Testing {platform.title()} with Playwright...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)  # Visible for debugging
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                # Navigate to the test URL
                url = self.test_urls[platform]
                print(f"   Navigating to: {url}")
                
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                await page.wait_for_timeout(5000)
                
                # Take screenshot
                screenshot_path = self.diagnostic_dir / f"{platform}_page_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"   📸 Screenshot saved: {screenshot_path}")
                
                # Save HTML content
                html_content = await page.content()
                html_path = self.diagnostic_dir / f"{platform}_page_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"   📄 HTML saved: {html_path}")
                
                # Test selectors
                await self._test_selectors_on_page(page, platform)
                
                await browser.close()
                
        except Exception as e:
            print(f"   ❌ Playwright test failed: {e}")
            self.logger.error(f"Playwright test failed for {platform}: {e}")
    
    async def _test_selectors_on_page(self, page, platform: str):
        """Test if expected selectors exist on the page"""
        print(f"   🔍 Testing selectors for {platform}...")
        
        selectors = self.expected_selectors[platform]
        
        for selector_name, selector in selectors.items():
            try:
                elements = await page.query_selector_all(selector)
                count = len(elements)
                print(f"      {selector_name}: {selector} -> Found {count} elements")
                
                if count == 0:
                    print(f"         ⚠️  WARNING: No elements found for {selector_name}")
                    
                    # Try to find similar elements
                    await self._find_similar_elements(page, selector_name, selector)
                
            except Exception as e:
                print(f"      {selector_name}: {selector} -> ERROR: {e}")
    
    async def _find_similar_elements(self, page, selector_name: str, original_selector: str):
        """Find similar elements when the expected selector fails"""
        try:
            # Try common variations
            variations = [
                original_selector.replace('div.', ''),
                original_selector.replace('h3.', ''),
                original_selector.replace('h4.', ''),
                original_selector.replace('span.', ''),
                original_selector.replace('a.', ''),
                original_selector.split('.')[-1] if '.' in original_selector else original_selector
            ]
            
            for variation in variations:
                try:
                    elements = await page.query_selector_all(f'[class*="{variation}"]')
                    if elements:
                        print(f"         💡 Found similar elements with: [class*=\"{variation}\"] -> {len(elements)} elements")
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"         ❌ Error finding similar elements: {e}")
    
    async def _test_with_requests(self, platform: str):
        """Test scraping with requests to check for blocking"""
        print(f"\n🌐 Testing {platform.title()} with requests...")
        
        try:
            url = self.test_urls[platform]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Content Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Test selectors
                selectors = self.expected_selectors[platform]
                for selector_name, selector in selectors.items():
                    elements = soup.select(selector)
                    print(f"      {selector_name}: {selector} -> Found {len(elements)} elements")
                    
                    if len(elements) == 0:
                        print(f"         ⚠️  WARNING: No elements found for {selector_name}")
                        
                        # Save problematic HTML section
                        await self._save_problematic_html(soup, platform, selector_name)
                
                # Save the full HTML for inspection
                html_path = self.diagnostic_dir / f"{platform}_requests_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup.prettify()))
                print(f"   📄 Full HTML saved: {html_path}")
                
            elif response.status_code == 403:
                print("   ❌ BLOCKED: Received 403 Forbidden - Site is blocking requests")
                print("   💡 Solution: Use Playwright with stealth mode")
                
            elif response.status_code == 429:
                print("   ❌ RATE LIMITED: Received 429 Too Many Requests")
                print("   💡 Solution: Add delays between requests")
                
                        else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                    
                except Exception as e:
            print(f"   ❌ Requests test failed: {e}")
            self.logger.error(f"Requests test failed for {platform}: {e}")
    
    async def _save_problematic_html(self, soup, platform: str, selector_name: str):
        """Save a section of HTML around where the selector should be"""
        try:
            # Try to find the main content area
            main_content = soup.find('main') or soup.find('div', {'id': 'main'}) or soup.find('body')
            
            if main_content:
                # Save a section of the HTML for debugging
                html_section = str(main_content)[:10000]  # First 10KB
                
                section_path = self.diagnostic_dir / f"{platform}_{selector_name}_section_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(section_path, 'w', encoding='utf-8') as f:
                    f.write(f"<!-- Section around {selector_name} for {platform} -->\n")
                    f.write(html_section)
                
                print(f"         📄 Problematic HTML section saved: {section_path}")
                
        except Exception as e:
            print(f"         ❌ Error saving HTML section: {e}")
    
    async def _test_scraper_class(self, platform: str):
        """Test the actual scraper class"""
        print(f"\n🧪 Testing {platform.title()} scraper class...")
        
        try:
            if platform == 'linkedin':
                from linkedin_scraper import LinkedInScraper
                scraper = LinkedInScraper()
            else:
                from indeed_scraper import IndeedScraper
                scraper = IndeedScraper()
            
            # Test with a small limit
            jobs = scraper.search_jobs('python developer', 'United States', limit=5)
            
            print(f"   Jobs found: {len(jobs)}")
            
            if jobs:
                print("   ✅ Scraper is working!")
                for i, job in enumerate(jobs[:3]):
                    print(f"      Job {i+1}: {job.get('title', 'No title')} at {job.get('company', 'No company')}")
            else:
                print("   ❌ Scraper returned no jobs")
                print("   💡 This confirms the selector issue identified above")
                
        except Exception as e:
            print(f"   ❌ Scraper class test failed: {e}")
            self.logger.error(f"Scraper class test failed for {platform}: {e}")
    
    def generate_diagnostic_report(self):
        """Generate a comprehensive diagnostic report"""
        print("\n📋 Generating Diagnostic Report...")
        print("=" * 50)
        
        report_path = self.diagnostic_dir / f"scraper_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w') as f:
            f.write("# Scraper Diagnostic Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write("This report contains the results of diagnosing LinkedIn and Indeed scrapers.\n\n")
            
            f.write("## Files Generated\n\n")
            f.write("- Screenshots: Visual evidence of what the scrapers see\n")
            f.write("- HTML files: Full page content for inspection\n")
            f.write("- Section files: Problematic HTML sections\n")
            f.write("- Logs: Detailed error logs\n\n")
            
            f.write("## Common Issues and Solutions\n\n")
            f.write("### 1. 403 Forbidden Errors\n")
            f.write("- **Cause**: Site is blocking automated requests\n")
            f.write("- **Solution**: Use Playwright with stealth mode\n\n")
            
            f.write("### 2. Changed CSS Selectors\n")
            f.write("- **Cause**: Website updated their HTML structure\n")
            f.write("- **Solution**: Update selectors in scraper files\n\n")
            
            f.write("### 3. Rate Limiting\n")
            f.write("- **Cause**: Too many requests too quickly\n")
            f.write("- **Solution**: Add delays between requests\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review the generated files to identify the specific issue\n")
            f.write("2. Update the appropriate scraper file with new selectors\n")
            f.write("3. Test the updated scraper\n")
            f.write("4. Run this diagnostic again to confirm the fix\n")
        
        print(f"📄 Diagnostic report saved: {report_path}")
    
    async def run_full_diagnosis(self):
        """Run the complete diagnostic process"""
        print("🚀 Starting Scraper Diagnostic Process")
        print("=" * 60)
        print(f"Output directory: {self.diagnostic_dir.absolute()}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        try:
            # Diagnose both scrapers
            await self.diagnose_linkedin_scraper()
            await self.diagnose_indeed_scraper()
            
            # Generate report
            self.generate_diagnostic_report()
            
            print("\n🎉 Diagnostic process completed!")
            print("\n📁 Check the following files:")
            print(f"   - Screenshots: {self.diagnostic_dir}")
            print(f"   - HTML files: {self.diagnostic_dir}")
            print(f"   - Logs: logs/scraper_diagnostic.log")
            print(f"   - Report: {self.diagnostic_dir}")
            
        except Exception as e:
            print(f"\n❌ Diagnostic process failed: {e}")
            self.logger.error(f"Diagnostic process failed: {e}")

async def main():
    """Main function to run the diagnostic"""
    diagnostic = ScraperDiagnostic()
    await diagnostic.run_full_diagnosis()

if __name__ == "__main__":
    asyncio.run(main())


