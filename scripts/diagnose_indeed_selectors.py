#!/usr/bin/env python3
"""
Diagnose Indeed Selectors
Checks the actual HTML structure of Indeed job pages to identify correct selectors
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.indeed_scraper import StealthIndeedScraper

async def diagnose_indeed_selectors():
    """Diagnose Indeed page structure and selectors"""
    print("🔍 Diagnosing Indeed Page Structure and Selectors")
    print("=" * 60)
    
    try:
        # Initialize scraper
        scraper = StealthIndeedScraper(use_proxy=False)  # Use direct connection for diagnosis
        
        from playwright.async_api import async_playwright
        async with async_playwright() as playwright:
            # Create browser
            browser = await scraper._create_stealth_browser()
            
            try:
                # Create context
                context = await scraper._create_stealth_context(browser)
                
                try:
                    # Create page
                    page = await context.new_page()
                    
                    # Navigate to Indeed
                    search_url = "https://www.indeed.com/jobs?q=python+developer&l=United+States"
                    print(f"🌐 Navigating to: {search_url}")
                    
                    await page.goto(search_url, wait_until='networkidle')
                    await asyncio.sleep(3)
                    
                    print("✅ Page loaded successfully")
                    
                    # Check for job cards
                    print("\n📋 Checking for job cards...")
                    
                    # Try different selectors for job cards
                    selectors_to_try = [
                        'div.job_seen_beacon',
                        'div[data-jk]',
                        'div.jobsearch-SerpJobCard',
                        'div[data-testid="job-card"]',
                        'div.jobCard',
                        'div[class*="job"]',
                        'div[class*="card"]'
                    ]
                    
                    for selector in selectors_to_try:
                        try:
                            elements = await page.locator(selector).all()
                            print(f"   {selector}: {len(elements)} elements found")
                            
                            if len(elements) > 0:
                                # Get first element's HTML structure
                                first_element = elements[0]
                                html = await first_element.inner_html()
                                print(f"   📄 Sample HTML (first 200 chars): {html[:200]}...")
                                
                                # Check for title elements
                                title_selectors = [
                                    'h2.jobTitle',
                                    'h2[data-testid="job-title"]',
                                    'h2',
                                    'a[data-testid="job-title"]',
                                    'a.jcs-JobTitle'
                                ]
                                
                                print(f"   🏷️  Checking title selectors:")
                                for title_selector in title_selectors:
                                    try:
                                        title_elem = await first_element.locator(title_selector).first
                                        if title_elem:
                                            title_text = await title_elem.text_content()
                                            print(f"      {title_selector}: '{title_text[:50]}...'")
                                        else:
                                            print(f"      {title_selector}: Not found")
                                    except Exception as e:
                                        print(f"      {title_selector}: Error - {e}")
                                
                                # Check for company elements
                                company_selectors = [
                                    'span[data-testid="company-name"]',
                                    'span.companyName',
                                    'div[data-testid="company-name"]',
                                    'span[class*="company"]'
                                ]
                                
                                print(f"   🏢 Checking company selectors:")
                                for company_selector in company_selectors:
                                    try:
                                        company_elem = await first_element.locator(company_selector).first
                                        if company_elem:
                                            company_text = await company_elem.text_content()
                                            print(f"      {company_selector}: '{company_text[:50]}...'")
                                        else:
                                            print(f"      {company_selector}: Not found")
                                    except Exception as e:
                                        print(f"      {company_selector}: Error - {e}")
                                
                                # Check for location elements
                                location_selectors = [
                                    'div[data-testid="text-location"]',
                                    'div.companyLocation',
                                    'span[data-testid="text-location"]',
                                    'div[class*="location"]'
                                ]
                                
                                print(f"   📍 Checking location selectors:")
                                for location_selector in location_selectors:
                                    try:
                                        location_elem = await first_element.locator(location_selector).first
                                        if location_elem:
                                            location_text = await location_elem.text_content()
                                            print(f"      {location_selector}: '{location_text[:50]}...'")
                                        else:
                                            print(f"      {location_selector}: Not found")
                                    except Exception as e:
                                        print(f"      {location_selector}: Error - {e}")
                                
                                print()
                                break  # Found working selector, stop checking others
                                
                        except Exception as e:
                            print(f"   {selector}: Error - {e}")
                    
                    # Save page HTML for manual inspection
                    html_content = await page.content()
                    html_file = Path("indeed_page_diagnosis.html")
                    html_file.write_text(html_content)
                    print(f"💾 Saved page HTML to: {html_file}")
                    
                    # Take screenshot
                    screenshot_file = Path("indeed_page_diagnosis.png")
                    await page.screenshot(path=str(screenshot_file))
                    print(f"📸 Saved screenshot to: {screenshot_file}")
                    
                finally:
                    await page.close()
                    
            finally:
                await context.close()
                
            finally:
                await browser.close()
        
        print("\n✅ Diagnosis completed successfully!")
        print("📋 Check the saved HTML file and screenshot for manual inspection")
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function"""
    await diagnose_indeed_selectors()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Diagnosis interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
