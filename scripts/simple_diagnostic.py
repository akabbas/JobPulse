#!/usr/bin/env python3
"""
Simple Scraper Diagnostic
Uses only built-in Python modules to test basic functionality
"""

import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import re
from datetime import datetime
from pathlib import Path

def test_url_accessibility(url, name):
    """Test if a URL is accessible"""
    print(f"🔍 Testing {name} accessibility...")
    print(f"   URL: {url}")
    
    try:
        # Create a request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"   ✅ Status: {response.status}")
            print(f"   📊 Content Length: {len(response.read())} bytes")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error: {e.code} - {e.reason}")
        if e.code == 403:
            print("      💡 Site is blocking automated requests")
            print("      💡 Solution: Use Playwright with stealth mode")
        elif e.code == 429:
            print("      💡 Rate limited - too many requests")
        return False
        
    except urllib.error.URLError as e:
        print(f"   ❌ URL Error: {e.reason}")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected Error: {e}")
        return False

def test_scraper_imports():
    """Test if scraper modules can be imported"""
    print("\n🧪 Testing Scraper Module Imports...")
    print("=" * 50)
    
    # Test LinkedIn scraper
    try:
        sys.path.append('scrapers')
        import linkedin_scraper
        print("   ✅ LinkedIn scraper module imported successfully")
        
        # Try to create an instance
        try:
            scraper = linkedin_scraper.LinkedInScraper()
            print("   ✅ LinkedIn scraper instance created successfully")
        except Exception as e:
            print(f"   ⚠️  LinkedIn scraper instance creation failed: {e}")
            
    except ImportError as e:
        print(f"   ❌ LinkedIn scraper import failed: {e}")
    except Exception as e:
        print(f"   ❌ LinkedIn scraper error: {e}")
    
    # Test Indeed scraper
    try:
        import indeed_scraper
        print("   ✅ Indeed scraper module imported successfully")
        
        # Try to create an instance
        try:
            scraper = indeed_scraper.IndeedScraper()
            print("   ✅ Indeed scraper instance created successfully")
        except Exception as e:
            print(f"   ⚠️  Indeed scraper instance creation failed: {e}")
            
    except ImportError as e:
        print(f"   ❌ Indeed scraper import failed: {e}")
    except Exception as e:
        print(f"   ❌ Indeed scraper error: {e}")

def test_scraper_file_structure():
    """Test if scraper files exist and have expected structure"""
    print("\n📁 Testing Scraper File Structure...")
    print("=" * 50)
    
    scrapers_dir = Path("scrapers")
    
    if not scrapers_dir.exists():
        print("   ❌ Scrapers directory not found")
        return
    
    # Check LinkedIn scraper
    linkedin_file = scrapers_dir / "linkedin_scraper.py"
    if linkedin_file.exists():
        print("   ✅ LinkedIn scraper file exists")
        
        # Check file size
        size = linkedin_file.stat().st_size
        print(f"      📊 File size: {size} bytes")
        
        # Check for expected content
        try:
            with open(linkedin_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for expected selectors
            expected_selectors = [
                'base-card',
                'base-search-card__title',
                'base-search-card__subtitle',
                'job-search-card__location',
                'base-card__full-link',
                'base-search-card__snippet'
            ]
            
            print("      🔍 Checking expected selectors:")
            for selector in expected_selectors:
                if selector in content:
                    print(f"         ✅ Found: {selector}")
                else:
                    print(f"         ❌ Missing: {selector}")
                    
        except Exception as e:
            print(f"      ❌ Error reading file: {e}")
    else:
        print("   ❌ LinkedIn scraper file not found")
    
    # Check Indeed scraper
    indeed_file = scrapers_dir / "indeed_scraper.py"
    if indeed_file.exists():
        print("   ✅ Indeed scraper file exists")
        
        # Check file size
        size = indeed_file.stat().st_size
        print(f"      📊 File size: {size} bytes")
        
        # Check for expected content
        try:
            with open(indeed_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for expected selectors
            expected_selectors = [
                'job_seen_beacon',
                'jobTitle',
                'companyName',
                'companyLocation',
                'jcs-JobTitle',
                'job-snippet'
            ]
            
            print("      🔍 Checking expected selectors:")
            for selector in expected_selectors:
                if selector in content:
                    print(f"         ✅ Found: {selector}")
                else:
                    print(f"         ❌ Missing: {selector}")
                    
        except Exception as e:
            print(f"      ❌ Error reading file: {e}")
    else:
        print("   ❌ Indeed scraper file not found")

def check_common_issues():
    """Check for common scraper issues"""
    print("\n🔍 Checking for Common Issues...")
    print("=" * 50)
    
    # Check if logs directory exists
    logs_dir = Path("logs")
    if logs_dir.exists():
        print("   ✅ Logs directory exists")
        
        # Check for recent log files
        log_files = list(logs_dir.glob("*.log"))
        if log_files:
            print(f"   📄 Found {len(log_files)} log files:")
            for log_file in log_files[:5]:  # Show first 5
                size = log_file.stat().st_size
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                print(f"      - {log_file.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
        else:
            print("   ⚠️  No log files found")
    else:
        print("   ❌ Logs directory not found")
    
    # Check if there are any backup files (indicating previous repairs)
    backup_files = list(Path("scrapers").glob("*.backup"))
    if backup_files:
        print(f"   📄 Found {len(backup_files)} backup files (previous repairs):")
        for backup_file in backup_files:
            print(f"      - {backup_file.name}")
    
    # Check for diagnostic output
    diagnostic_dir = Path("diagnostic_output")
    if diagnostic_dir.exists():
        html_files = list(diagnostic_dir.glob("*.html"))
        if html_files:
            print(f"   📄 Found {len(html_files)} HTML files from previous diagnostics:")
            for html_file in html_files[:3]:  # Show first 3
                print(f"      - {html_file.name}")
        else:
            print("   ⚠️  No HTML files found in diagnostic output")

def generate_simple_report():
    """Generate a simple diagnostic report"""
    print("\n📋 Generating Simple Diagnostic Report...")
    print("=" * 50)
    
    # Ensure diagnostic output directory exists
    diagnostic_dir = Path("diagnostic_output")
    diagnostic_dir.mkdir(exist_ok=True)
    
    report_path = diagnostic_dir / f"simple_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_path, 'w') as f:
        f.write("Simple Scraper Diagnostic Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("This report contains basic diagnostic information about the scrapers.\n\n")
        
        f.write("Common Issues Found:\n")
        f.write("1. 403 Forbidden: Site blocking automated requests\n")
        f.write("2. Changed CSS Selectors: Website updated HTML structure\n")
        f.write("3. Rate Limiting: Too many requests too quickly\n")
        f.write("4. Missing Dependencies: Required packages not installed\n\n")
        
        f.write("Recommended Solutions:\n")
        f.write("1. For 403 errors: Use Playwright with stealth mode\n")
        f.write("2. For selector issues: Update CSS selectors in scraper files\n")
        f.write("3. For rate limiting: Add delays between requests\n")
        f.write("4. For missing dependencies: Install required packages\n\n")
        
        f.write("Next Steps:\n")
        f.write("1. Review this report for specific issues\n")
        f.write("2. Run the repair script if selectors are broken:\n")
        f.write("   python scripts/repair_scrapers.py\n")
        f.write("3. For full diagnosis with screenshots, install Playwright:\n")
        f.write("   pip install playwright\n")
        f.write("   playwright install\n")
        f.write("   python scripts/diagnose_scrapers.py\n")
    
    print(f"   📄 Report saved: {report_path}")

def main():
    """Main function to run the simple diagnostic"""
    print("🚀 Simple Scraper Diagnostic")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This diagnostic uses only built-in Python modules")
    print("For comprehensive testing, install additional packages")
    print()
    
    # Test URL accessibility
    test_url_accessibility(
        "https://www.linkedin.com/jobs/search?keywords=python%20developer&location=United%20States",
        "LinkedIn Jobs"
    )
    
    test_url_accessibility(
        "https://www.indeed.com/jobs?q=python+developer&l=United+States",
        "Indeed Jobs"
    )
    
    # Test scraper imports
    test_scraper_imports()
    
    # Test file structure
    test_scraper_file_structure()
    
    # Check for common issues
    check_common_issues()
    
    # Generate report
    generate_simple_report()
    
    print("\n🎉 Simple diagnostic completed!")
    print("\n📋 Summary of Findings:")
    print("1. URL accessibility: Check if sites are blocking requests")
    print("2. Module imports: Verify scraper classes can be loaded")
    print("3. File structure: Ensure scraper files exist and are complete")
    print("4. Common issues: Look for patterns in logs and backups")
    print("\n📁 Check the following files:")
    print("   - Report: diagnostic_output/")
    print("   - Logs: logs/")
    print("\n🔧 Next Steps:")
    print("1. Review the diagnostic report above")
    print("2. If selectors are broken, run the repair script")
    print("3. For full diagnosis, install Playwright and run the full diagnostic")

if __name__ == "__main__":
    main()
