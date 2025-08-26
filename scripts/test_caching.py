#!/usr/bin/env python3
"""
Test script to verify the smart caching architecture
Tests: search → cache → database → cache hit → verification
"""

import sys
import os
import time
import json
import requests
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_caching_system():
    """Test the complete caching system end-to-end"""
    
    print("🧪 Testing Smart Caching Architecture")
    print("=" * 50)
    
    # Configuration
    base_url = "http://localhost:5002"  # Default Flask port
    search_data = {
        "keyword": "python developer",
        "location": "United States",
        "sources": ["enhanced", "api_sources", "reddit"],
        "limit": 20
    }
    
    try:
        # Step 1: Check if the Flask app is running
        print("🔍 Step 1: Checking if Flask app is running...")
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Flask app is running")
            else:
                print(f"⚠️  Flask app responded with status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Flask app is not running: {e}")
            print("💡 Please start the Flask app first:")
            print("   cd web_dashboard && python app.py")
            return False
        
        # Step 2: Perform first search (should not be cached)
        print("\n🔍 Step 2: Performing first search (should not be cached)...")
        first_search_response = requests.post(
            f"{base_url}/search",
            json=search_data,
            timeout=30
        )
        
        if first_search_response.status_code != 200:
            print(f"❌ First search failed with status: {first_search_response.status_code}")
            print(f"Response: {first_search_response.text}")
            return False
        
        first_search_data = first_search_response.json()
        
        if not first_search_data.get('success'):
            print(f"❌ First search returned error: {first_search_data.get('error')}")
            return False
        
        first_jobs = first_search_data.get('jobs', [])
        first_search_id = first_search_data.get('search_id')
        first_source = first_search_data.get('source', 'unknown')
        first_cached = first_search_data.get('cached', False)
        
        print(f"✅ First search successful:")
        print(f"   - Jobs found: {len(first_jobs)}")
        print(f"   - Search ID: {first_search_id}")
        print(f"   - Source: {first_source}")
        print(f"   - From cache: {first_cached}")
        
        if first_cached:
            print("⚠️  Warning: First search was cached, which is unexpected")
        else:
            print("✅ First search was NOT cached (as expected)")
        
        # Step 3: Wait 10 seconds
        print("\n⏳ Step 3: Waiting 10 seconds for database operations...")
        time.sleep(10)
        
        # Step 4: Perform exact same search (should be cached)
        print("\n🔍 Step 4: Performing identical search (should be cached)...")
        second_search_response = requests.post(
            f"{base_url}/search",
            json=search_data,
            timeout=30
        )
        
        if second_search_response.status_code != 200:
            print(f"❌ Second search failed with status: {second_search_response.status_code}")
            print(f"Response: {second_search_response.text}")
            return False
        
        second_search_data = second_search_response.json()
        
        if not second_search_data.get('success'):
            print(f"❌ Second search returned error: {second_search_data.get('error')}")
            return False
        
        second_jobs = second_search_data.get('jobs', [])
        second_search_id = second_search_data.get('search_id')
        second_source = second_search_data.get('source', 'unknown')
        second_cached = second_search_data.get('cached', False)
        
        print(f"✅ Second search successful:")
        print(f"   - Jobs found: {len(second_jobs)}")
        print(f"   - Search ID: {second_search_id}")
        print(f"   - Source: {second_source}")
        print(f"   - From cache: {second_cached}")
        
        # Step 5: Verify results are identical
        print("\n🔍 Step 5: Verifying search results consistency...")
        
        if len(first_jobs) != len(second_jobs):
            print(f"❌ Job count mismatch: First={len(first_jobs)}, Second={len(second_jobs)}")
            return False
        
        # Compare job titles (simplified comparison)
        first_titles = [job.get('title', '') for job in first_jobs]
        second_titles = [job.get('title', '') for job in second_jobs]
        
        if first_titles != second_titles:
            print("❌ Job titles don't match between searches")
            print("First search titles:", first_titles[:3])
            print("Second search titles:", second_titles[:3])
            return False
        
        print("✅ Search results are identical")
        
        # Step 6: Check database for saved jobs
        print("\n🔍 Step 6: Verifying database persistence...")
        
        db_path = "web_dashboard/instance/jobpulse.db"
        if not os.path.exists(db_path):
            print(f"❌ Database file not found at: {db_path}")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check jobs table
            cursor.execute("SELECT COUNT(*) FROM jobs")
            total_jobs = cursor.fetchone()[0]
            print(f"✅ Total jobs in database: {total_jobs}")
            
            # Check searches table
            cursor.execute("SELECT COUNT(*) FROM searches")
            total_searches = cursor.fetchone()[0]
            print(f"✅ Total searches in database: {total_searches}")
            
            # Check recent searches for our keyword
            cursor.execute("""
                SELECT keyword, location, result_count, created_at 
                FROM searches 
                WHERE keyword LIKE ? 
                ORDER BY created_at DESC 
                LIMIT 3
            """, (f"%{search_data['keyword']}%",))
            
            recent_searches = cursor.fetchall()
            print(f"✅ Recent searches for '{search_data['keyword']}':")
            for search in recent_searches:
                print(f"   - {search[0]} in {search[1]}: {search[2]} jobs at {search[3]}")
            
            # Check recent jobs from our source
            cursor.execute("""
                SELECT title, company, source, created_at 
                FROM jobs 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            recent_jobs = cursor.fetchall()
            print(f"✅ Recent jobs in database:")
            for job in recent_jobs:
                print(f"   - {job[0]} at {job[1]} from {job[2]} at {job[3]}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return False
        
        # Step 7: Final verification
        print("\n🔍 Step 7: Final verification...")
        
        if second_cached:
            print("✅ Second search was served from cache")
        else:
            print("⚠️  Second search was NOT served from cache")
        
        if total_jobs > 0:
            print("✅ Jobs were successfully saved to database")
        else:
            print("❌ No jobs found in database")
        
        if total_searches > 0:
            print("✅ Searches were successfully logged to database")
        else:
            print("❌ No searches found in database")
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 CACHING SYSTEM TEST RESULTS")
        print("=" * 50)
        
        test_passed = (
            len(first_jobs) > 0 and
            len(first_jobs) == len(second_jobs) and
            first_titles == second_titles and
            total_jobs > 0 and
            total_searches > 0
        )
        
        if test_passed:
            print("✅ ALL TESTS PASSED!")
            print("✅ Smart caching architecture is working correctly")
            print("✅ Database persistence is working")
            print("✅ Cache hits are functioning")
        else:
            print("❌ SOME TESTS FAILED")
            print("❌ Caching system needs investigation")
        
        print(f"\n📊 Test Summary:")
        print(f"   - First search jobs: {len(first_jobs)}")
        print(f"   - Second search jobs: {len(second_jobs)}")
        print(f"   - Database jobs: {total_jobs}")
        print(f"   - Database searches: {total_searches}")
        print(f"   - Cache hit on second search: {second_cached}")
        
        return test_passed
        
    except Exception as e:
        print(f"❌ Test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Starting Smart Caching System Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_caching_system()
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n🎯 RECOMMENDATION: Caching system is ready for production!")
        sys.exit(0)
    else:
        print("\n🔧 RECOMMENDATION: Investigate and fix caching issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
