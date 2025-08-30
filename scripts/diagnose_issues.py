#!/usr/bin/env python3
"""
🚀 JobPulse Automated Testing Script
====================================

This script performs automated testing of critical user journeys in the JobPulse application.
It tests search functionality, skills network, empty states, and filter interactions.

Usage:
    python scripts/diagnose_issues.py [--base-url BASE_URL] [--verbose]

Author: JobPulse Team
Version: 1.0.0
"""

import requests
import json
import time
import sys
import argparse
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional
import re

class JobPulseTester:
    """Automated testing suite for JobPulse application."""
    
    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.session = requests.Session()
        self.test_results = []
        self.start_time = time.time()
        
        # Set reasonable timeout and headers
        self.session.timeout = 30
        self.session.headers.update({
            'User-Agent': 'JobPulse-Tester/1.0.0',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        print(f"🚀 JobPulse Automated Testing Suite")
        print(f"📍 Testing against: {self.base_url}")
        print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp and level."""
        timestamp = time.strftime('%H:%M:%S')
        if self.verbose or level in ["ERROR", "WARN"]:
            print(f"[{timestamp}] {level}: {message}")
    
    def test_endpoint_health(self) -> bool:
        """Test if the application is accessible."""
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self.log("✅ Application is accessible", "INFO")
                return True
            else:
                self.log(f"❌ Application returned status {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Cannot connect to application: {e}", "ERROR")
            return False
    
    def test_basic_search(self) -> Dict[str, Any]:
        """Test 1: Basic Search Functionality"""
        test_name = "Basic Search"
        self.log(f"🧪 Running {test_name}...")
        
        try:
            # Test data
            search_data = {
                "keyword": "software engineer",
                "location": "United States",
                "experience_level": "all",
                "sources": ["linkedin", "indeed", "remoteok"]
            }
            
            # Make search request
            response = self.session.post(
                urljoin(self.base_url, "/search"),
                json=search_data,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": f"Search endpoint returned status {response.status_code}",
                    "details": response.text[:200] if response.text else "No response body"
                }
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Response is not valid JSON",
                    "details": response.text[:200]
                }
            
            # Check response structure
            if not data:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Empty response from search endpoint",
                    "details": "Response is empty or null"
                }
            
            # Check for jobs
            jobs_found = False
            total_jobs = 0
            
            if isinstance(data, dict):
                # Enhanced search response format
                if data.get('success') and data.get('jobs'):
                    jobs_found = True
                    total_jobs = len(data['jobs'])
                elif data.get('success') and data.get('total_jobs'):
                    jobs_found = True
                    total_jobs = data['total_jobs']
                else:
                    # Regular search response format
                    for source, jobs in data.items():
                        if source != 'error' and isinstance(jobs, list):
                            jobs_found = True
                            total_jobs += len(jobs)
            elif isinstance(data, list):
                jobs_found = True
                total_jobs = len(data)
            
            if not jobs_found:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "No jobs found in search response",
                    "details": f"Response structure: {type(data).__name__}, Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}"
                }
            
            # Check job structure (if jobs exist)
            if total_jobs > 0:
                # Get first job to check structure
                first_job = None
                if isinstance(data, dict) and data.get('jobs'):
                    first_job = data['jobs'][0] if data['jobs'] else None
                elif isinstance(data, dict):
                    for source, jobs in data.items():
                        if source != 'error' and isinstance(jobs, list) and jobs:
                            first_job = jobs[0]
                            break
                elif isinstance(data, list) and data:
                    first_job = data[0]
                
                if first_job:
                    # Check required fields
                    required_fields = ['title', 'company', 'location']
                    missing_fields = [field for field in required_fields if not first_job.get(field)]
                    
                    if missing_fields:
                        return {
                            "test": test_name,
                            "status": "WARN",
                            "error": f"Job missing required fields: {missing_fields}",
                            "details": f"First job: {first_job}",
                            "jobs_found": total_jobs
                        }
            
            self.log(f"✅ {test_name} completed successfully - Found {total_jobs} jobs", "INFO")
            return {
                "test": test_name,
                "status": "PASS",
                "jobs_found": total_jobs,
                "response_time": response.elapsed.total_seconds()
            }
            
        except requests.exceptions.Timeout:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": "Search request timed out after 30 seconds",
                "details": "Request took longer than expected"
            }
        except requests.exceptions.RequestException as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Request failed: {e}",
                "details": str(e)
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Unexpected error: {e}",
                "details": str(e)
            }
    
    def test_skills_network(self) -> Dict[str, Any]:
        """Test 2: Skills Network API Endpoint"""
        test_name = "Skills Network API"
        self.log(f"🧪 Running {test_name}...")
        
        try:
            # Test the skills network endpoint
            response = self.session.get(
                urljoin(self.base_url, "/api/skills-network"),
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": f"Skills network endpoint returned status {response.status_code}",
                    "details": response.text[:200] if response.text else "No response body"
                }
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Skills network response is not valid JSON",
                    "details": response.text[:200]
                }
            
            # Check response structure
            if not isinstance(data, dict):
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Skills network response is not a dictionary",
                    "details": f"Response type: {type(data).__name__}"
                }
            
            # Check for expected fields
            expected_fields = ['nodes', 'edges']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": f"Skills network response missing required fields: {missing_fields}",
                    "details": f"Available fields: {list(data.keys())}"
                }
            
            # Check data types
            if not isinstance(data.get('nodes'), list):
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Skills network nodes field is not a list",
                    "details": f"Nodes type: {type(data.get('nodes')).__name__}"
                }
            
            if not isinstance(data.get('edges'), list):
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Skills network edges field is not a list",
                    "details": f"Edges type: {type(data.get('edges')).__name__}"
                }
            
            # Check if there's any data
            nodes_count = len(data.get('nodes', []))
            edges_count = len(data.get('edges', []))
            
            if nodes_count == 0 and edges_count == 0:
                return {
                    "test": test_name,
                    "status": "WARN",
                    "error": "Skills network has no data (nodes or edges)",
                    "details": "This might be expected if no jobs have been searched yet",
                    "nodes_count": nodes_count,
                    "edges_count": edges_count
                }
            
            self.log(f"✅ {test_name} completed successfully - {nodes_count} nodes, {edges_count} edges", "INFO")
            return {
                "test": test_name,
                "status": "PASS",
                "nodes_count": nodes_count,
                "edges_count": edges_count,
                "response_time": response.elapsed.total_seconds()
            }
            
        except requests.exceptions.Timeout:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": "Skills network request timed out after 30 seconds",
                "details": "Request took longer than expected"
            }
        except requests.exceptions.RequestException as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Skills network request failed: {e}",
                "details": str(e)
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Unexpected error in skills network test: {e}",
                "details": str(e)
            }
    
    def test_empty_state_handling(self) -> Dict[str, Any]:
        """Test 3: Empty State Triggers and Handling"""
        test_name = "Empty State Handling"
        self.log(f"🧪 Running {test_name}...")
        
        try:
            # Test with nonsense keyword
            search_data = {
                "keyword": "asdfghjkl",
                "location": "Nowhere",
                "experience_level": "all",
                "sources": ["linkedin", "indeed"]
            }
            
            response = self.session.post(
                urljoin(self.base_url, "/search"),
                json=search_data,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": f"Empty state test returned status {response.status_code}",
                    "details": response.text[:200] if response.text else "No response body"
                }
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Empty state test response is not valid JSON",
                    "details": response.text[:200]
                }
            
            # Check if response is empty (which is expected for nonsense search)
            jobs_found = 0
            
            if isinstance(data, dict):
                if data.get('success') and data.get('jobs'):
                    jobs_found = len(data['jobs'])
                elif data.get('success') and data.get('total_jobs'):
                    jobs_found = data['total_jobs']
                else:
                    # Regular search response format
                    for source, jobs in data.items():
                        if source != 'error' and isinstance(jobs, list):
                            jobs_found += len(jobs)
            elif isinstance(data, list):
                jobs_found = len(data)
            
            # For a nonsense search, we expect 0 jobs
            if jobs_found > 0:
                return {
                    "test": test_name,
                    "status": "WARN",
                    "error": f"Unexpectedly found {jobs_found} jobs for nonsense search",
                    "details": "This might indicate the search is too permissive or returning mock data"
                }
            
            # Check if the response indicates no results gracefully
            if isinstance(data, dict):
                # Look for error messages or empty result indicators
                has_error = data.get('error') is not None
                has_empty_indicator = any([
                    data.get('total_jobs') == 0,
                    data.get('jobs') == [],
                    all(len(jobs) == 0 for jobs in data.values() if isinstance(jobs, list))
                ])
                
                if not (has_error or has_empty_indicator):
                    return {
                        "test": test_name,
                        "status": "WARN",
                        "error": "Response doesn't clearly indicate empty results",
                        "details": f"Response structure: {data}"
                    }
            
            self.log(f"✅ {test_name} completed successfully - Gracefully handled empty results", "INFO")
            return {
                "test": test_name,
                "status": "PASS",
                "jobs_found": jobs_found,
                "response_time": response.elapsed.total_seconds()
            }
            
        except requests.exceptions.Timeout:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": "Empty state test request timed out after 30 seconds",
                "details": "Request took longer than expected"
            }
        except requests.exceptions.RequestException as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Empty state test request failed: {e}",
                "details": str(e)
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Unexpected error in empty state test: {e}",
                "details": str(e)
            }
    
    def test_filter_interactions(self) -> Dict[str, Any]:
        """Test 4: Filter Interactions and Search Modifications"""
        test_name = "Filter Interactions"
        self.log(f"🧪 Running {test_name}...")
        
        try:
            # Test different filter combinations
            filter_tests = [
                {
                    "name": "Entry Level Filter",
                    "data": {
                        "keyword": "developer",
                        "location": "United States",
                        "experience_level": "entry",
                        "sources": ["linkedin", "indeed"]
                    }
                },
                {
                    "name": "Senior Level Filter",
                    "data": {
                        "keyword": "developer",
                        "location": "United States",
                        "experience_level": "senior",
                        "sources": ["linkedin", "indeed"]
                    }
                },
                {
                    "name": "Limited Sources Filter",
                    "data": {
                        "keyword": "developer",
                        "location": "United States",
                        "experience_level": "all",
                        "sources": ["linkedin"]
                    }
                }
            ]
            
            results = []
            for filter_test in filter_tests:
                try:
                    response = self.session.post(
                        urljoin(self.base_url, "/search"),
                        json=filter_test["data"],
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            # Count jobs for this filter
                            jobs_count = 0
                            if isinstance(data, dict):
                                if data.get('success') and data.get('jobs'):
                                    jobs_count = len(data['jobs'])
                                elif data.get('success') and data.get('total_jobs'):
                                    jobs_count = data['total_jobs']
                                else:
                                    for source, jobs in data.items():
                                        if source != 'error' and isinstance(jobs, list):
                                            jobs_count += len(jobs)
                            elif isinstance(data, list):
                                jobs_count = len(data)
                            
                            results.append({
                                "filter": filter_test["name"],
                                "status": "PASS",
                                "jobs_found": jobs_count,
                                "response_time": response.elapsed.total_seconds()
                            })
                            
                        except json.JSONDecodeError:
                            results.append({
                                "filter": filter_test["name"],
                                "status": "FAIL",
                                "error": "Invalid JSON response"
                            })
                    else:
                        results.append({
                            "filter": filter_test["name"],
                            "status": "FAIL",
                            "error": f"HTTP {response.status_code}"
                        })
                        
                except requests.exceptions.RequestException as e:
                    results.append({
                        "filter": filter_test["name"],
                        "status": "FAIL",
                        "error": f"Request failed: {e}"
                    })
            
            # Analyze results
            passed_filters = [r for r in results if r["status"] == "PASS"]
            failed_filters = [r for r in results if r["status"] == "FAIL"]
            
            if failed_filters:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": f"{len(failed_filters)} filter tests failed",
                    "details": failed_filters,
                    "passed_filters": len(passed_filters),
                    "total_filters": len(results)
                }
            
            self.log(f"✅ {test_name} completed successfully - All {len(results)} filter combinations worked", "INFO")
            return {
                "test": test_name,
                "status": "PASS",
                "passed_filters": len(passed_filters),
                "total_filters": len(results),
                "filter_results": results
            }
            
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Unexpected error in filter interactions test: {e}",
                "details": str(e)
            }
    
    def test_enhanced_search(self) -> Dict[str, Any]:
        """Test 5: Enhanced Search (Playwright) Functionality"""
        test_name = "Enhanced Search"
        self.log(f"🧪 Running {test_name}...")
        
        try:
            # Test enhanced search endpoint
            search_data = {
                "keyword": "python developer",
                "location": "United States",
                "experience_level": "all",
                "limit": 10,
                "headless": True
            }
            
            response = self.session.post(
                urljoin(self.base_url, "/enhanced_search"),
                json=search_data,
                timeout=60  # Enhanced search might take longer
            )
            
            if response.status_code != 200:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": f"Enhanced search endpoint returned status {response.status_code}",
                    "details": response.text[:200] if response.text else "No response body"
                }
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Enhanced search response is not valid JSON",
                    "details": response.text[:200]
                }
            
            # Check response structure
            if not isinstance(data, dict):
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Enhanced search response is not a dictionary",
                    "details": f"Response type: {type(data).__name__}"
                }
            
            # Check for success flag
            if not data.get('success'):
                error_msg = data.get('error', 'Unknown error')
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": f"Enhanced search failed: {error_msg}",
                    "details": data
                }
            
            # Check for required fields
            required_fields = ['jobs', 'total_jobs', 'search_id']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": f"Enhanced search response missing required fields: {missing_fields}",
                    "details": f"Available fields: {list(data.keys())}"
                }
            
            # Check jobs data
            jobs = data.get('jobs', [])
            if not isinstance(jobs, list):
                return {
                    "test": test_name,
                    "status": "FAIL",
                    "error": "Enhanced search jobs field is not a list",
                    "details": f"Jobs type: {type(jobs).__name__}"
                }
            
            total_jobs = data.get('total_jobs', 0)
            if total_jobs != len(jobs):
                return {
                    "test": test_name,
                    "status": "WARN",
                    "error": "Total jobs count doesn't match actual jobs list length",
                    "details": f"Total: {total_jobs}, Actual: {len(jobs)}"
                }
            
            # Check source breakdown if available
            source_breakdown = data.get('source_breakdown', {})
            if source_breakdown and not isinstance(source_breakdown, dict):
                return {
                    "test": test_name,
                    "status": "WARN",
                    "error": "Source breakdown is not a dictionary",
                    "details": f"Source breakdown type: {type(source_breakdown).__name__}"
                }
            
            self.log(f"✅ {test_name} completed successfully - Found {total_jobs} jobs", "INFO")
            return {
                "test": test_name,
                "status": "PASS",
                "total_jobs": total_jobs,
                "jobs_count": len(jobs),
                "search_id": data.get('search_id'),
                "source_breakdown": source_breakdown,
                "response_time": response.elapsed.total_seconds()
            }
            
        except requests.exceptions.Timeout:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": "Enhanced search request timed out after 60 seconds",
                "details": "Request took longer than expected"
            }
        except requests.exceptions.RequestException as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Enhanced search request failed: {e}",
                "details": str(e)
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": f"Unexpected error in enhanced search test: {e}",
                "details": str(e)
            }
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all tests and return results."""
        tests = [
            self.test_basic_search,
            self.test_skills_network,
            self.test_empty_state_handling,
            self.test_filter_interactions,
            self.test_enhanced_search
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                self.test_results.append(result)
                
                # Add delay between tests to avoid overwhelming the server
                time.sleep(1)
                
            except Exception as e:
                self.test_results.append({
                    "test": test_func.__name__.replace('test_', '').replace('_', ' ').title(),
                    "status": "FAIL",
                    "error": f"Test execution failed: {e}",
                    "details": str(e)
                })
        
        return self.test_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        if not self.test_results:
            return "No test results available."
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        
        # Calculate total time
        total_time = time.time() - self.start_time
        
        # Generate report
        report = []
        report.append("=" * 60)
        report.append("🚀 JOBPULSE AUTOMATED TESTING REPORT")
        report.append("=" * 60)
        report.append(f"📍 Tested URL: {self.base_url}")
        report.append(f"⏰ Test Duration: {total_time:.2f} seconds")
        report.append(f"📊 Test Summary: {passed_tests} ✅ PASS, {warning_tests} ⚠️ WARN, {failed_tests} ❌ FAIL")
        report.append("=" * 60)
        report.append("")
        
        # Group results by status
        for status in ["PASS", "WARN", "FAIL"]:
            status_results = [r for r in self.test_results if r["status"] == status]
            if status_results:
                status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[status]
                report.append(f"{status_icon} {status} TESTS ({len(status_results)}):")
                report.append("-" * 40)
                
                for result in status_results:
                    test_name = result["test"]
                    report.append(f"  {status_icon} {test_name}")
                    
                    if "error" in result:
                        report.append(f"     Error: {result['error']}")
                    
                    if "details" in result:
                        details = str(result["details"])
                        if len(details) > 100:
                            details = details[:100] + "..."
                        report.append(f"     Details: {details}")
                    
                    if "response_time" in result:
                        report.append(f"     Response Time: {result['response_time']:.2f}s")
                    
                    if "jobs_found" in result:
                        report.append(f"     Jobs Found: {result['jobs_found']}")
                    
                    report.append("")
        
        # Overall assessment
        report.append("=" * 60)
        if failed_tests == 0 and warning_tests == 0:
            report.append("🎉 ALL TESTS PASSED! JobPulse is working perfectly.")
        elif failed_tests == 0:
            report.append("⚠️  Some tests had warnings, but no critical failures.")
        else:
            report.append(f"❌ {failed_tests} critical test(s) failed. Please investigate.")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = None) -> str:
        """Save the test report to a file."""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"jobpulse_test_report_{timestamp}.txt"
        
        report = self.generate_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.log(f"📄 Test report saved to: {filename}", "INFO")
            return filename
        except Exception as e:
            self.log(f"❌ Failed to save report: {e}", "ERROR")
            return None

def main():
    """Main function to run the JobPulse testing suite."""
    parser = argparse.ArgumentParser(
        description="JobPulse Automated Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/diagnose_issues.py                    # Test localhost:8000
  python scripts/diagnose_issues.py --base-url http://myapp.com  # Test remote URL
  python scripts/diagnose_issues.py --verbose          # Show detailed logs
  python scripts/diagnose_issues.py --save-report      # Save report to file
        """
    )
    
    parser.add_argument(
        '--base-url',
        default='http://localhost:8000',
        help='Base URL of the JobPulse application (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--save-report',
        action='store_true',
        help='Save test report to a file'
    )
    
    parser.add_argument(
        '--output-file',
        help='Custom filename for the test report'
    )
    
    args = parser.parse_args()
    
    try:
        # Create tester instance
        tester = JobPulseTester(base_url=args.base_url, verbose=args.verbose)
        
        # Check if application is accessible
        if not tester.test_endpoint_health():
            print("❌ Application is not accessible. Please check the URL and ensure the app is running.")
            sys.exit(1)
        
        # Run all tests
        print("🧪 Starting automated tests...")
        tester.run_all_tests()
        
        # Generate and display report
        report = tester.generate_report()
        print(report)
        
        # Save report if requested
        if args.save_report:
            filename = args.output_file or None
            saved_file = tester.save_report(filename)
            if saved_file:
                print(f"\n📄 Test report saved to: {saved_file}")
        
        # Exit with appropriate code
        failed_tests = len([r for r in tester.test_results if r["status"] == "FAIL"])
        if failed_tests > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
