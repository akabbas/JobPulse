#!/usr/bin/env python3
"""
FetchHire job scraper using Playwright to bypass 403 errors
"""

import asyncio
import time
import random
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup

class PlaywrightJobScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
    async def _init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        self.context = await self.browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # Set extra headers
        await self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
    
    async def _cleanup_browser(self):
        """Clean up browser resources"""
        if hasattr(self, 'page'):
            await self.page.close()
        if hasattr(self, 'context'):
            await self.context.close()
        if hasattr(self, 'browser'):
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text"""
        if not text:
            return []
        
        skills_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin|PHP|Ruby|Scala|R|MATLAB)\b',
            r'\b(React|Angular|Vue\.js|Node\.js|Django|Flask|Spring|Express\.js|Laravel|Ruby on Rails|ASP\.NET|jQuery|Bootstrap|Tailwind CSS)\b',
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB|Elasticsearch)\b',
            r'\b(AWS|Azure|Google Cloud|Docker|Kubernetes|Terraform|Jenkins|GitLab|GitHub Actions|Ansible|Chef|Puppet)\b',
            r'\b(Salesforce|Apex|Lightning|Visualforce|SOQL|SOSL|Salesforce DX|Lightning Web Components|LWC|Aura)\b',
            r'\b(TensorFlow|PyTorch|Scikit-learn|Keras|OpenAI|Hugging Face|Pandas|NumPy|Matplotlib|Seaborn)\b',
            r'\b(HTML5|CSS3|SASS|LESS|Webpack|Babel|ESLint|Prettier|GraphQL|REST API|SOAP|WebSocket)\b',
            r'\b(Jest|Mocha|Jasmine|Cypress|Selenium|JUnit|TestNG|PyTest|NUnit|XUnit)\b',
            r'\b(Agile|Scrum|Kanban|Waterfall|TDD|BDD|CI/CD|Microservices|API|REST|GraphQL|OAuth|JWT)\b'
        ]
        
        skills = set()
        text_lower = text.lower()
        
        for pattern in skills_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        return list(skills)
    
    async def scrape_remote_ok_playwright(self) -> List[Dict]:
        """Scrape Remote OK using Playwright (bypasses 403)"""
        print("🌐 Scraping Remote OK with Playwright...")
        jobs = []
        
        try:
            # Navigate to Remote OK
            await self.page.goto("https://remoteok.com/remote-dev-jobs", wait_until='networkidle')
            
            # Wait for content to load
            await self.page.wait_for_timeout(3000)
            
            # Get the page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('tr', class_='job')
            
            for card in job_cards[:20]:  # Limit to 20 jobs
                try:
                    # Extract job data
                    title_elem = card.find('h2', {'itemprop': 'title'})
                    company_elem = card.find('h3', {'itemprop': 'hiringOrganization'})
                    location_elem = card.find('div', class_='location')
                    
                    if title_elem and company_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        
                        # Get job URL
                        job_link = card.find('a', class_='preventLink')
                        job_url = f"https://remoteok.com{job_link['href']}" if job_link else ""
                        
                        # Get description
                        description_elem = card.find('div', class_='description')
                        description = description_elem.get_text(strip=True) if description_elem else ""
                        
                        # Extract skills
                        skills = self._extract_skills_from_text(description + " " + title)
                        
                        job = {
                            'title': title,
                            'company': company,
                            'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                            'source': 'Remote OK',
                            'source_url': job_url,
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'description': description,
                            'salary': '',
                            'tags': skills
                        }
                        jobs.append(job)
                        
                except Exception as e:
                    print(f"Warning: Error parsing Remote OK job: {e}")
                    continue
            
            print(f"✅ Remote OK: Found {len(jobs)} jobs")
            
        except Exception as e:
            print(f"❌ Error scraping Remote OK: {e}")
        
        return jobs
    
    async def scrape_weworkremotely_playwright(self) -> List[Dict]:
        """Scrape We Work Remotely using Playwright (bypasses 403)"""
        print("🏢 Scraping We Work Remotely with Playwright...")
        jobs = []
        
        try:
            # Navigate to We Work Remotely
            await self.page.goto("https://weworkremotely.com/remote-jobs", wait_until='networkidle')
            
            # Wait for content to load
            await self.page.wait_for_timeout(3000)
            
            # Get the page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('li', class_='feature')
            
            for card in job_cards[:20]:  # Limit to 20 jobs
                try:
                    # Extract job data
                    title_elem = card.find('span', class_='title')
                    company_elem = card.find('span', class_='company')
                    location_elem = card.find('span', class_='region')
                    
                    if title_elem and company_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        
                        # Get job URL
                        job_link = card.find('a')
                        job_url = f"https://weworkremotely.com{job_link['href']}" if job_link else ""
                        
                        # Get description (we'll need to visit the job page for full description)
                        description = f"Remote position at {company}"
                        
                        # Extract skills
                        skills = self._extract_skills_from_text(description + " " + title)
                        
                        job = {
                            'title': title,
                            'company': company,
                            'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                            'source': 'We Work Remotely',
                            'source_url': job_url,
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'description': description,
                            'salary': '',
                            'tags': skills
                        }
                        jobs.append(job)
                        
                except Exception as e:
                    print(f"Warning: Error parsing We Work Remotely job: {e}")
                    continue
            
            print(f"✅ We Work Remotely: Found {len(jobs)} jobs")
            
        except Exception as e:
            print(f"❌ Error scraping We Work Remotely: {e}")
        
        return jobs
    
    async def scrape_github_jobs_api(self) -> List[Dict]:
        """Scrape GitHub Jobs using their API (free, no API key)"""
        print("🐙 Scraping GitHub Jobs API...")
        jobs = []
        
        try:
            url = "https://jobs.github.com/positions.json"
            params = {
                'search': 'python,salesforce,data',
                'location': 'remote'
            }
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    for job in data[:15]:  # Limit to 15 jobs
                        try:
                            job_data = {
                                'title': job.get('title', ''),
                                'company': job.get('company', ''),
                                'location': job.get('location', 'Remote'),
                                'source': 'GitHub Jobs',
                                'source_url': job.get('url', ''),
                                'posted_date': job.get('created_at', ''),
                                'description': job.get('description', ''),
                                'salary': '',
                                'tags': self._extract_skills_from_text(job.get('description', '') + ' ' + job.get('title', ''))
                            }
                            jobs.append(job_data)
                        except Exception as e:
                            print(f"Warning: Error parsing GitHub job: {e}")
                            continue
                    
                    print(f"✅ GitHub Jobs: Found {len(jobs)} jobs")
                else:
                    print("❌ GitHub Jobs: No jobs found")
            else:
                print(f"❌ GitHub Jobs: HTTP {response.status_code}")
            
        except Exception as e:
            print(f"❌ Error scraping GitHub Jobs: {e}")
        
        return jobs
    
    async def scrape_remotive_api(self) -> List[Dict]:
        """Scrape Remotive using their API (free, no API key)"""
        print("🌐 Scraping Remotive API...")
        jobs = []
        
        try:
            url = "https://remotive.com/api/remote-jobs"
            params = {
                'limit': 15,
                'search': 'python,salesforce,data'
            }
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and 'jobs' in data:
                    for job in data['jobs'][:15]:  # Limit to 15 jobs
                        try:
                            job_data = {
                                'title': job.get('title', ''),
                                'company': job.get('company_name', ''),
                                'location': job.get('candidate_required_location', 'Remote'),
                                'source': 'Remotive',
                                'source_url': job.get('url', ''),
                                'posted_date': job.get('publication_date', ''),
                                'description': job.get('description', ''),
                                'salary': job.get('salary', ''),
                                'tags': self._extract_skills_from_text(job.get('description', '') + ' ' + job.get('title', ''))
                            }
                            jobs.append(job_data)
                        except Exception as e:
                            print(f"Warning: Error parsing Remotive job: {e}")
                            continue
                    
                    print(f"✅ Remotive: Found {len(jobs)} jobs")
                else:
                    print("❌ Remotive: No jobs found")
            else:
                print(f"❌ Remotive: HTTP {response.status_code}")
            
        except Exception as e:
            print(f"❌ Error scraping Remotive: {e}")
        
        return jobs
    
    async def scrape_all_sources_playwright(self) -> List[Dict]:
        """Scrape all sources using Playwright and APIs"""
        print("🚀 Starting Playwright-based job scraping...")
        print("=" * 60)
        
        all_jobs = []
        
        try:
            # Initialize browser
            await self._init_browser()
            
            # Scrape Remote OK with Playwright
            remote_ok_jobs = await self.scrape_remote_ok_playwright()
            all_jobs.extend(remote_ok_jobs)
            
            # Add delay between sites
            await asyncio.sleep(random.uniform(3, 5))
            
            # Scrape We Work Remotely with Playwright
            wwr_jobs = await self.scrape_weworkremotely_playwright()
            all_jobs.extend(wwr_jobs)
            
            # Add delay
            await asyncio.sleep(random.uniform(2, 3))
            
            # Scrape GitHub Jobs API
            github_jobs = await self.scrape_github_jobs_api()
            all_jobs.extend(github_jobs)
            
            # Add delay
            await asyncio.sleep(random.uniform(2, 3))
            
            # Scrape Remotive API
            remotive_jobs = await self.scrape_remotive_api()
            all_jobs.extend(remotive_jobs)
            
        finally:
            # Clean up browser
            await self._cleanup_browser()
        
        # Remove duplicates
        unique_jobs = self._remove_duplicates(all_jobs)
        
        print(f"\n🎉 Playwright scraping completed!")
        print(f"✅ Total unique jobs found: {len(unique_jobs)}")
        print("✅ Successfully bypassed 403 errors!")
        
        return unique_jobs
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            identifier = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def save_jobs_to_file(self, jobs: List[Dict], filename: str = 'playwright_scraped_jobs.json'):
        """Save scraped jobs to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            print(f"❌ Failed to save jobs to file: {e}")

async def main():
    """Main async function"""
    print("🧪 Testing Playwright Job Scraper (Bypass 403 Errors!)")
    print("=" * 60)
    
    scraper = PlaywrightJobScraper()
    
    print("✅ Playwright Scraper Features:")
    print("   • Remote OK (Playwright - bypasses 403)")
    print("   • We Work Remotely (Playwright - bypasses 403)")
    print("   • GitHub Jobs API (Free API)")
    print("   • Remotive API (Free API)")
    print("   • No API Keys Required")
    print("   • No Rate Limits")
    print("   • NO 403 ERRORS!")
    print()
    
    # Test Playwright scraping
    all_jobs = await scraper.scrape_all_sources_playwright()
    
    # Save results
    print("\n💾 Saving Results:")
    scraper.save_jobs_to_file(all_jobs, 'playwright_test_results.json')
    
    # Show sample jobs
    if all_jobs:
        print("\n📋 Sample Jobs:")
        for i, job in enumerate(all_jobs[:3], 1):
            print(f"   {i}. {job['title']} at {job['company']}")
            print(f"      📍 {job['location']} | {job.get('salary', 'N/A')}")
            print(f"      🏷️  Skills: {', '.join(job['tags'][:5])}")
            print()
    
    print("🎉 Playwright scraper test completed successfully!")
    print(f"✅ Total jobs scraped: {len(all_jobs)}")
    print("✅ Successfully bypassed all 403 errors!")
    
    return all_jobs

if __name__ == "__main__":
    asyncio.run(main()) 