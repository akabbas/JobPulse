#!/usr/bin/env python3
"""
Repair Script for LinkedIn and Indeed Scrapers
Automatically fixes common CSS selector issues based on diagnostic results
"""

import os
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ScraperRepair:
    """Automated repair tool for LinkedIn and Indeed scrapers"""
    
    def __init__(self):
        self.setup_logging()
        self.diagnostic_dir = Path("diagnostic_output")
        self.scrapers_dir = Path("scrapers")
        
        # Common selector patterns and alternatives
        self.selector_alternatives = {
            'linkedin': {
                'base-card': [
                    'div[class*="base-card"]',
                    'div[class*="job-card"]',
                    'div[class*="search-result"]',
                    'div[class*="job-result"]',
                    'div[class*="card"]'
                ],
                'base-search-card__title': [
                    'h3[class*="title"]',
                    'h3[class*="job-title"]',
                    'h2[class*="title"]',
                    'h2[class*="job-title"]',
                    'a[class*="job-title"]'
                ],
                'base-search-card__subtitle': [
                    'h4[class*="subtitle"]',
                    'h4[class*="company"]',
                    'span[class*="company"]',
                    'div[class*="company"]'
                ],
                'job-search-card__location': [
                    'span[class*="location"]',
                    'div[class*="location"]',
                    'span[class*="job-location"]',
                    'div[class*="job-location"]'
                ],
                'base-card__full-link': [
                    'a[class*="full-link"]',
                    'a[class*="job-link"]',
                    'a[class*="title"]',
                    'a[href*="/jobs/"]'
                ],
                'base-search-card__snippet': [
                    'div[class*="snippet"]',
                    'div[class*="description"]',
                    'div[class*="summary"]',
                    'p[class*="description"]'
                ]
            },
            'indeed': {
                'job_seen_beacon': [
                    'div[class*="job_seen_beacon"]',
                    'div[class*="job_seen"]',
                    'div[class*="beacon"]',
                    'div[class*="job-card"]',
                    'div[class*="job-result"]'
                ],
                'jobTitle': [
                    'h2[class*="jobTitle"]',
                    'h2[class*="title"]',
                    'a[class*="jobTitle"]',
                    'a[class*="title"]',
                    'h3[class*="jobTitle"]'
                ],
                'companyName': [
                    'span[class*="companyName"]',
                    'span[class*="company"]',
                    'div[class*="company"]',
                    'a[class*="company"]'
                ],
                'companyLocation': [
                    'div[class*="companyLocation"]',
                    'div[class*="location"]',
                    'span[class*="location"]',
                    'div[class*="job-location"]'
                ],
                'jcs-JobTitle': [
                    'a[class*="jcs-JobTitle"]',
                    'a[class*="jobTitle"]',
                    'a[class*="title"]',
                    'a[href*="/viewjob"]'
                ],
                'job-snippet': [
                    'div[class*="job-snippet"]',
                    'div[class*="snippet"]',
                    'div[class*="description"]',
                    'div[class*="summary"]'
                ]
            }
        }
    
    def setup_logging(self):
        """Setup logging for repair operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/scraper_repair.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def find_best_selectors(self, platform: str, html_file: Path) -> dict:
        """Analyze HTML file to find the best working selectors"""
        print(f"🔍 Analyzing HTML file for {platform}: {html_file}")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Test different selector strategies
            best_selectors = {}
            expected_selectors = self.selector_alternatives[platform]
            
            for selector_name, alternatives in expected_selectors.items():
                best_selector = None
                max_elements = 0
                
                for alternative in alternatives:
                    try:
                        elements = soup.select(alternative)
                        if len(elements) > max_elements:
                            max_elements = len(elements)
                            best_selector = alternative
                    except Exception as e:
                        self.logger.debug(f"Selector {alternative} failed: {e}")
                        continue
                
                if best_selector and max_elements > 0:
                    best_selectors[selector_name] = best_selector
                    print(f"   ✅ {selector_name}: {best_selector} -> {max_elements} elements")
                else:
                    print(f"   ❌ {selector_name}: No working selector found")
                    best_selectors[selector_name] = alternatives[0]  # Use first as fallback
            
            return best_selectors
            
        except Exception as e:
            print(f"   ❌ Error analyzing HTML: {e}")
            self.logger.error(f"Error analyzing HTML for {platform}: {e}")
            return {}
    
    def update_linkedin_scraper(self, new_selectors: dict):
        """Update LinkedIn scraper with new selectors"""
        print("\n🔧 Updating LinkedIn Scraper...")
        
        linkedin_file = self.scrapers_dir / "linkedin_scraper.py"
        
        if not linkedin_file.exists():
            print("   ❌ LinkedIn scraper file not found")
            return False
        
        try:
            with open(linkedin_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create backup
            backup_file = linkedin_file.with_suffix('.py.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   📄 Backup created: {backup_file}")
            
            # Update selectors
            updated_content = content
            
            # Map selector names to variable names in the code
            selector_mapping = {
                'base-card': 'base-card',
                'base-search-card__title': 'base-search-card__title',
                'base-search-card__subtitle': 'base-search-card__subtitle',
                'job-search-card__location': 'job-search-card__location',
                'base-card__full-link': 'base-card__full-link',
                'base-search-card__snippet': 'base-search-card__snippet'
            }
            
            for selector_name, new_selector in new_selectors.items():
                if selector_name in selector_mapping:
                    old_selector = f"'{selector_mapping[selector_name]}'"
                    new_selector_clean = new_selector.replace('"', '\\"')
                    new_selector_clean = f"'{new_selector_clean}'"
                    
                    # Replace the selector in the code
                    pattern = rf"'{selector_mapping[selector_name]}'"
                    if re.search(pattern, updated_content):
                        updated_content = re.sub(pattern, new_selector_clean, updated_content)
                        print(f"      Updated {selector_name}: {old_selector} -> {new_selector_clean}")
                    else:
                        print(f"      ⚠️  Could not find selector {selector_name} in code")
            
            # Write updated content
            with open(linkedin_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("   ✅ LinkedIn scraper updated successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Error updating LinkedIn scraper: {e}")
            self.logger.error(f"Error updating LinkedIn scraper: {e}")
            return False
    
    def update_indeed_scraper(self, new_selectors: dict):
        """Update Indeed scraper with new selectors"""
        print("\n🔧 Updating Indeed Scraper...")
        
        indeed_file = self.scrapers_dir / "indeed_scraper.py"
        
        if not indeed_file.exists():
            print("   ❌ Indeed scraper file not found")
            return False
        
        try:
            with open(indeed_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create backup
            backup_file = indeed_file.with_suffix('.py.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   📄 Backup created: {backup_file}")
            
            # Update selectors
            updated_content = content
            
            # Map selector names to variable names in the code
            selector_mapping = {
                'job_seen_beacon': 'job_seen_beacon',
                'jobTitle': 'jobTitle',
                'companyName': 'companyName',
                'companyLocation': 'companyLocation',
                'jcs-JobTitle': 'jcs-JobTitle',
                'job-snippet': 'job-snippet'
            }
            
            for selector_name, new_selector in new_selectors.items():
                if selector_name in selector_mapping:
                    old_selector = f"'{selector_mapping[selector_name]}'"
                    new_selector_clean = new_selector.replace('"', '\\"')
                    new_selector_clean = f"'{new_selector_clean}'"
                    
                    # Replace the selector in the code
                    pattern = rf"'{selector_mapping[selector_name]}'"
                    if re.search(pattern, updated_content):
                        updated_content = re.sub(pattern, new_selector_clean, updated_content)
                        print(f"      Updated {selector_name}: {old_selector} -> {new_selector_clean}")
                    else:
                        print(f"      ⚠️  Could not find selector {selector_name} in code")
            
            # Write updated content
            with open(indeed_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("   ✅ Indeed scraper updated successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Error updating Indeed scraper: {e}")
            self.logger.error(f"Error updating Indeed scraper: {e}")
            return False
    
    def test_updated_scraper(self, platform: str) -> bool:
        """Test the updated scraper to ensure it works"""
        print(f"\n🧪 Testing updated {platform.title()} scraper...")
        
        try:
            if platform == 'linkedin':
                from scrapers.linkedin_scraper import LinkedInScraper
                scraper = LinkedInScraper()
            else:
                from scrapers.indeed_scraper import IndeedScraper
                scraper = IndeedScraper()
            
            # Test with a small search
            jobs = scraper.search_jobs('python developer', 'United States', limit=3)
            
            if jobs and len(jobs) > 0:
                print(f"   ✅ Success! Found {len(jobs)} jobs")
                for i, job in enumerate(jobs[:2]):
                    print(f"      Job {i+1}: {job.get('title', 'No title')} at {job.get('company', 'No company')}")
                return True
            else:
                print("   ❌ No jobs found - scraper still not working")
                return False
                
        except Exception as e:
            print(f"   ❌ Scraper test failed: {e}")
            self.logger.error(f"Scraper test failed for {platform}: {e}")
            return False
    
    def find_latest_html_files(self) -> dict:
        """Find the latest HTML files from diagnostic output"""
        html_files = {}
        
        if not self.diagnostic_dir.exists():
            print("❌ Diagnostic output directory not found")
            print("   Run the diagnostic script first: python scripts/diagnose_scrapers.py")
            return {}
        
        # Find latest HTML files for each platform
        for platform in ['linkedin', 'indeed']:
            pattern = f"{platform}_page_html_*.html"
            files = list(self.diagnostic_dir.glob(pattern))
            
            if files:
                # Get the most recent file
                latest_file = max(files, key=lambda f: f.stat().st_mtime)
                html_files[platform] = latest_file
                print(f"📄 Found {platform} HTML file: {latest_file.name}")
            else:
                print(f"⚠️  No HTML files found for {platform}")
        
        return html_files
    
    def run_repair(self):
        """Run the complete repair process"""
        print("🚀 Starting Scraper Repair Process")
        print("=" * 50)
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Find latest HTML files
        html_files = self.find_latest_html_files()
        
        if not html_files:
            print("\n❌ No HTML files found for repair")
            print("   Please run the diagnostic script first:")
            print("   python scripts/diagnose_scrapers.py")
            return
        
        repair_results = {}
        
        # Repair each platform
        for platform, html_file in html_files.items():
            print(f"\n🔧 Repairing {platform.title()} scraper...")
            print("-" * 40)
            
            # Find best selectors
            best_selectors = self.find_best_selectors(platform, html_file)
            
            if not best_selectors:
                print(f"   ❌ Could not determine selectors for {platform}")
                continue
            
            # Update scraper
            if platform == 'linkedin':
                success = self.update_linkedin_scraper(best_selectors)
            else:
                success = self.update_indeed_scraper(best_selectors)
            
            if success:
                # Test the updated scraper
                test_success = self.test_updated_scraper(platform)
                repair_results[platform] = {
                    'updated': True,
                    'tested': test_success,
                    'selectors': best_selectors
                }
                
                if test_success:
                    print(f"   🎉 {platform.title()} scraper repaired and tested successfully!")
                else:
                    print(f"   ⚠️  {platform.title()} scraper updated but test failed")
            else:
                repair_results[platform] = {
                    'updated': False,
                    'tested': False,
                    'selectors': {}
                }
                print(f"   ❌ {platform.title()} scraper repair failed")
        
        # Generate repair report
        self.generate_repair_report(repair_results)
        
        print("\n🎯 REPAIR SUMMARY:")
        for platform, result in repair_results.items():
            status = "✅ Repaired" if result['updated'] and result['tested'] else "⚠️ Partially Fixed" if result['updated'] else "❌ Failed"
            print(f"   {platform.title()}: {status}")
        
        print("\n📋 Next Steps:")
        print("1. Review the repair results above")
        print("2. Test the scrapers manually if needed")
        print("3. Run the diagnostic script again to verify fixes")
        print("4. Check the logs for any remaining issues")
    
    def generate_repair_report(self, repair_results: dict):
        """Generate a repair report"""
        print("\n📋 Generating Repair Report...")
        
        report_path = self.diagnostic_dir / f"scraper_repair_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w') as f:
            f.write("# Scraper Repair Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Repair Results\n\n")
            
            for platform, result in repair_results.items():
                f.write(f"### {platform.title()}\n\n")
                f.write(f"- **Status**: {'✅ Repaired' if result['updated'] and result['tested'] else '⚠️ Partially Fixed' if result['updated'] else '❌ Failed'}\n")
                f.write(f"- **Updated**: {'Yes' if result['updated'] else 'No'}\n")
                f.write(f"- **Tested**: {'Yes' if result['tested'] else 'No'}\n\n")
                
                if result['selectors']:
                    f.write("**New Selectors**:\n\n")
                    for selector_name, selector in result['selectors'].items():
                        f.write(f"- `{selector_name}`: `{selector}`\n")
                    f.write("\n")
            
            f.write("## Files Modified\n\n")
            f.write("- `scrapers/linkedin_scraper.py` (with backup)\n")
            f.write("- `scrapers/indeed_scraper.py` (with backup)\n")
            f.write("- Backup files: `*.py.backup`\n\n")
            
            f.write("## Verification\n\n")
            f.write("To verify the repair worked:\n\n")
            f.write("1. Run the diagnostic script again:\n")
            f.write("   ```bash\n")
            f.write("   python scripts/diagnose_scrapers.py\n")
            f.write("   ```\n\n")
            f.write("2. Test the scrapers manually\n")
            f.write("3. Check the logs for any errors\n")
        
        print(f"📄 Repair report saved: {report_path}")

def main():
    """Main function to run the repair process"""
    repair = ScraperRepair()
    repair.run_repair()

if __name__ == "__main__":
    main()
