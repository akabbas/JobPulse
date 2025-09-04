#!/usr/bin/env python3
"""
Quick API test script for local development
"""

import requests
import json
import time

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_search():
    """Test the search endpoint"""
    print("\n🔍 Testing search endpoint...")
    try:
        data = {
            "keyword": "python developer",
            "location": "Remote",
            "limit": 5
        }
        response = requests.post(
            "http://localhost:5001/search",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search endpoint working")
            print(f"📊 Found {result.get('total_jobs', 0)} jobs")
            print(f"🎯 Successful sources: {result.get('successful_sources', 0)}")
            return True
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
        return False

def test_enhanced_search():
    """Test the enhanced search endpoint"""
    print("\n🔍 Testing enhanced search endpoint...")
    try:
        data = {
            "keyword": "python developer",
            "location": "Remote",
            "limit": 5
        }
        response = requests.post(
            "http://localhost:5001/enhanced_search",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Enhanced search endpoint working")
            print(f"📊 Found {result.get('total_jobs', 0)} jobs")
            print(f"🎯 Scraping method: {result.get('scraping_method', 'unknown')}")
            return True
        else:
            print(f"❌ Enhanced search endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Enhanced search endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing JobPulse Local API...\n")
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test health endpoint
    if not test_health():
        print("\n❌ Server not responding. Make sure the Flask app is running on port 5001.")
        return False
    
    # Test search endpoint
    if not test_search():
        print("\n❌ Search endpoint failed.")
        return False
    
    # Test enhanced search endpoint
    if not test_enhanced_search():
        print("\n❌ Enhanced search endpoint failed.")
        return False
    
    print("\n🎉 All API tests passed! Your local environment is working perfectly.")
    print("\n🌐 You can now access the web interface at: http://localhost:5001")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)






