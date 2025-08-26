#!/usr/bin/env python3
"""
Lever Company List Repair Script
Systematically finds correct identifiers for broken companies in the Lever scraper
"""

import requests
import json
import time
import random
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeverCompanyRepair:
    """Repairs broken company identifiers for Lever scraper"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JobPulse/1.0 (https://github.com/akabbas/JobPulse)',
            'Accept': 'application/json'
        })
        
        # Companies from the current Lever scraper
        self.current_companies = [
            'stripe', 'coinbase', 'robinhood', 'doordash', 'instacart',
            'notion', 'figma', 'linear', 'vercel', 'netlify', 'supabase',
            'planetscale', 'github', 'shopify', 'twilio', 'slack'
        ]
        
        # Common naming variations to try
        self.naming_variations = [
            # Standard variations
            '{company}',
            '{company}-technologies',
            '{company}-tech',
            '{company}-careers',
            '{company}-jobs',
            '{company}-inc',
            '{company}-llc',
            '{company}-corp',
            
            # Hyphenated variations
            '{company}-{company}',
            '{company}-team',
            '{company}-engineering',
            '{company}-software',
            
            # Abbreviated variations
            '{company}tech',
            '{company}careers',
            '{company}jobs',
            
            # Common company-specific variations
            'stripe-stripe',
            'coinbase-coinbase',
            'robinhood-robinhood',
            'doordash-doordash',
            'instacart-instacart',
            'notion-so',
            'figma-figma',
            'linear-linear',
            'vercel-vercel',
            'netlify-netlify',
            'supabase-supabase',
            'planetscale-planetscale',
            'github-github',
            'shopify-shopify',
            'twilio-twilio',
            'slack-slack',
            
            # Stock ticker variations
            'stripe-stripe',
            'coin-coinbase',
            'hood-robinhood',
            'dash-doordash',
            'cart-instacart',
            'notion-so',
            'figma-figma',
            'linear-linear',
            'vercel-vercel',
            'netlify-netlify',
            'supabase-supabase',
            'planetscale-planetscale',
            'github-github',
            'shop-shopify',
            'twlo-twilio',
            'work-slack'
        ]
        
        # Company-specific known identifiers
        self.known_identifiers = {
            'stripe': ['stripe-stripe', 'stripe-technologies', 'stripeinc'],
            'coinbase': ['coinbase-coinbase', 'coin-coinbase', 'coinbase-tech'],
            'robinhood': ['robinhood-robinhood', 'hood-robinhood', 'robinhood-tech'],
            'doordash': ['doordash-doordash', 'dash-doordash', 'doordash-tech'],
            'instacart': ['instacart-instacart', 'cart-instacart', 'instacart-tech'],
            'notion': ['notion-so', 'notion-software', 'notion-inc'],
            'figma': ['figma-figma', 'figma-design', 'figma-inc'],
            'linear': ['linear-linear', 'linear-app', 'linear-software'],
            'vercel': ['vercel-vercel', 'vercel-platform', 'vercel-inc'],
            'netlify': ['netlify-netlify', 'netlify-platform', 'netlify-inc'],
            'supabase': ['supabase-supabase', 'supabase-inc'],
            'planetscale': ['planetscale-planetscale', 'planetscale-database'],
            'github': ['github-github', 'github-inc', 'github-software'],
            'shopify': ['shopify-shopify', 'shop-shopify', 'shopify-tech'],
            'twilio': ['twilio-twilio', 'twlo-twilio', 'twilio-communications'],
            'slack': ['slack-slack', 'work-slack', 'slack-technologies']
        }
    
    def test_company_identifier(self, identifier: str) -> Tuple[bool, int, str]:
        """Test if a company identifier is valid"""
        try:
            api_url = f"https://api.lever.co/v0/postings/{identifier}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                jobs_data = response.json()
                job_count = len(jobs_data) if isinstance(jobs_data, list) else 0
                return True, response.status_code, f"Found {job_count} jobs"
            else:
                return False, response.status_code, "No jobs found"
                
        except Exception as e:
            return False, 0, str(e)
    
    def find_company_career_page(self, company: str) -> Optional[str]:
        """Try to find the company's career page to extract correct identifier"""
        career_urls = [
            f"https://jobs.lever.co/{company}",
            f"https://careers.{company}.com",
            f"https://jobs.{company}.com",
            f"https://{company}.com/careers",
            f"https://{company}.com/jobs",
            f"https://{company}.com/join-us",
            f"https://{company}.com/team",
            f"https://{company}.com/about/careers",
            f"https://{company}.com/about/jobs"
        ]
        
        for url in career_urls:
            try:
                response = self.session.get(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    # Look for Lever redirects or links
                    if 'lever.co' in response.url or 'lever.co' in response.text:
                        # Extract company identifier from URL
                        parsed = urlparse(response.url)
                        if 'lever.co' in parsed.netloc:
                            path_parts = parsed.path.strip('/').split('/')
                            if path_parts:
                                return path_parts[0]
                    return url
            except:
                continue
        
        return None
    
    def repair_company(self, company: str) -> Optional[str]:
        """Attempt to repair a single company identifier"""
        logger.info(f"🔍 Repairing company: {company}")
        
        # First, try known identifiers for this company
        if company in self.known_identifiers:
            for identifier in self.known_identifiers[company]:
                logger.info(f"  Testing known identifier: {identifier}")
                is_valid, status, message = self.test_company_identifier(identifier)
                if is_valid:
                    logger.info(f"  ✅ Found working identifier: {identifier}")
                    return identifier
                time.sleep(random.uniform(0.5, 1.0))
        
        # Try naming variations
        for variation in self.naming_variations:
            identifier = variation.format(company=company)
            logger.info(f"  Testing variation: {identifier}")
            is_valid, status, message = self.test_company_identifier(identifier)
            if is_valid:
                logger.info(f"  ✅ Found working identifier: {identifier}")
                return identifier
            time.sleep(random.uniform(0.5, 1.0))
        
        # Try to find career page
        logger.info(f"  🔍 Searching for career page...")
        career_page = self.find_company_career_page(company)
        if career_page:
            logger.info(f"  Found career page: {career_page}")
        
        logger.warning(f"  ❌ Could not find working identifier for {company}")
        return None
    
    def repair_all_companies(self) -> Dict[str, Optional[str]]:
        """Repair all companies in the current list"""
        logger.info("🚀 Starting Lever company repair process...")
        
        results = {}
        
        for company in self.current_companies:
            working_identifier = self.repair_company(company)
            results[company] = working_identifier
            
            # Add delay between companies
            time.sleep(random.uniform(1.0, 2.0))
        
        return results
    
    def generate_updated_company_list(self, repair_results: Dict[str, Optional[str]]) -> List[str]:
        """Generate the updated company list for the scraper"""
        updated_list = []
        
        # Add repaired companies
        for company, identifier in repair_results.items():
            if identifier:
                updated_list.append(identifier)
                logger.info(f"✅ Added repaired company: {company} -> {identifier}")
            else:
                logger.warning(f"❌ Could not repair: {company}")
        
        return updated_list
    
    def save_results(self, repair_results: Dict[str, Optional[str]], updated_list: List[str]):
        """Save repair results and updated company list"""
        # Save detailed results
        results_data = {
            'repair_results': repair_results,
            'updated_company_list': updated_list,
            'current_companies': self.current_companies,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('lever_repair_results.json', 'w') as f:
            json.dump(results_data, f, indent=2)
        
        # Save updated company list for easy copy-paste
        with open('lever_updated_companies.txt', 'w') as f:
            f.write("# Updated Lever Companies List\n")
            f.write("# Copy this list to scrapers/lever_scraper.py\n\n")
            f.write("self.lever_companies = [\n")
            for company in updated_list:
                f.write(f"    '{company}',\n")
            f.write("]\n")
        
        logger.info("💾 Results saved to lever_repair_results.json")
        logger.info("💾 Updated company list saved to lever_updated_companies.txt")
    
    def print_summary(self, repair_results: Dict[str, Optional[str]], updated_list: List[str]):
        """Print a summary of the repair process"""
        print("\n" + "="*60)
        print("🔧 LEVER COMPANY REPAIR SUMMARY")
        print("="*60)
        
        print(f"\n📊 Original companies: {len(self.current_companies)}")
        
        repaired_count = sum(1 for result in repair_results.values() if result)
        print(f"📊 Successfully repaired: {repaired_count}")
        print(f"📊 Still broken: {len(self.current_companies) - repaired_count}")
        print(f"📊 Total companies in updated list: {len(updated_list)}")
        
        print(f"\n✅ REPAIRED COMPANIES:")
        for company, identifier in repair_results.items():
            if identifier:
                print(f"  {company} -> {identifier}")
        
        print(f"\n❌ STILL BROKEN:")
        for company, identifier in repair_results.items():
            if not identifier:
                print(f"  {company}")
        
        print(f"\n📋 NEXT STEPS:")
        print("1. Copy the updated company list from lever_updated_companies.txt")
        print("2. Replace the lever_companies list in scrapers/lever_scraper.py")
        print("3. Test the scraper with: python test_scrapers.py")
        print("="*60)

def main():
    """Main execution function"""
    repair_tool = LeverCompanyRepair()
    
    # Repair all companies
    repair_results = repair_tool.repair_all_companies()
    
    # Generate updated company list
    updated_list = repair_tool.generate_updated_company_list(repair_results)
    
    # Save results
    repair_tool.save_results(repair_results, updated_list)
    
    # Print summary
    repair_tool.print_summary(repair_results, updated_list)

if __name__ == "__main__":
    main()
