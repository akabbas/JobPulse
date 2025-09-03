#!/usr/bin/env python3
"""
Simple Indeed Diagnosis
Checks the actual HTML structure of Indeed job pages
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright

async def diagnose_indeed():
    """Simple Indeed page diagnosis"""
    print("🔍 Simple Indeed Page Diagnosis")
    print("=" * 40)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate to Indeed
            url = "https://www.indeed.com/jobs?q=python+developer&l=United+States"
            print(f"🌐 Navigating to: {url}")
            
            await page.goto(url, wait_until='networkidle')
            await asyncio.sleep(3)
            
            print("✅ Page loaded")
            
            # Check for job cards
            print("\n📋 Checking job card selectors...")
            
            selectors = [
                'div.job_seen_beacon',
                'div[data-jk]',
                'div.jobsearch-SerpJobCard',
                'div[data-testid="job-card"]'
            ]
            
            for selector in selectors:
                try:
                    elements = await page.locator(selector).all()
                    print(f"   {selector}: {len(elements)} found")
                    
                    if len(elements) > 0:
                        # Check first element
                        first = elements[0]
                        html = await first.inner_html()
                        print(f"   📄 HTML sample: {html[:100]}...")
                        
                        # Check title
                        title_elem = await first.locator('h2.jobTitle').first
                        if title_elem:
                            title = await title_elem.text_content()
                            print(f"   🏷️  Title: {title[:50]}...")
                        else:
                            print("   🏷️  Title: Not found")
                        
                        # Check company
                        company_elem = await first.locator('span[data-testid="company-name"]').first
                        if company_elem:
                            company = await company_elem.text_content()
                            print(f"   🏢 Company: {company[:50]}...")
                        else:
                            print("   🏢 Company: Not found")
                        
                        break
                        
                except Exception as e:
                    print(f"   {selector}: Error - {e}")
            
            # Save HTML
            html_content = await page.content()
            html_file = Path("indeed_simple_diagnosis.html")
            html_file.write_text(html_content)
            print(f"\n💾 Saved HTML to: {html_file}")
            
            # Take screenshot
            await page.screenshot(path="indeed_simple_diagnosis.png")
            print(f"📸 Saved screenshot to: indeed_simple_diagnosis.png")
            
        finally:
            await browser.close()
    
    print("\n✅ Diagnosis completed!")

if __name__ == "__main__":
    asyncio.run(diagnose_indeed())
