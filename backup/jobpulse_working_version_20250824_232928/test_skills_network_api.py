#!/usr/bin/env python3
"""
Test script for the Skills Network API endpoint
Run this to verify the API is working correctly
"""

import requests
import json
import sys

def test_skills_network_api():
    """Test the skills network API endpoint"""
    
    # Base URL for your Flask app
    base_url = "http://localhost:5002"
    
    print("🧪 Testing Skills Network API Endpoints")
    print("=" * 50)
    
    # Test 1: Basic skills network data
    print("\n1️⃣ Testing /api/skills-network")
    try:
        response = requests.get(f"{base_url}/api/skills-network")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                skills_count = len(data['data']['skills'])
                connections_count = len(data['data']['co_occurrences'])
                print(f"✅ Success! Found {skills_count} skills and {connections_count} connections")
                
                # Show some sample data
                print("\n📊 Sample Skills:")
                for skill, count in list(data['data']['skills'].items())[:5]:
                    print(f"   • {skill}: {count} jobs")
                
                print("\n🔗 Sample Connections:")
                for connection, count in list(data['data']['co_occurrences'].items())[:5]:
                    print(f"   • {connection}: {count} co-occurrences")
                    
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error testing skills network API: {e}")
        return False
    
    # Test 2: Skills network with filters
    print("\n2️⃣ Testing /api/skills-network with filters")
    try:
        params = {
            'min_frequency': 3,
            'min_co_occurrence': 2
        }
        response = requests.get(f"{base_url}/api/skills-network", params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                skills_count = len(data['data']['skills'])
                connections_count = len(data['data']['co_occurrences'])
                print(f"✅ Filtered results: {skills_count} skills and {connections_count} connections")
            else:
                print(f"❌ Filtered API returned error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing filtered skills network API: {e}")
    
    # Test 3: Skills network stats
    print("\n3️⃣ Testing /api/skills-network/stats")
    try:
        response = requests.get(f"{base_url}/api/skills-network/stats")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['stats']
                print(f"✅ Stats endpoint working:")
                print(f"   • Available filters: {', '.join(stats['available_filters'])}")
                print(f"   • Data sources: {', '.join(stats['data_sources'])}")
                print(f"   • Version: {stats['version']}")
            else:
                print(f"❌ Stats API returned error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing stats API: {e}")
    
    # Test 4: Available searches endpoint
    print("\n4️⃣ Testing /api/skills-network/searches")
    try:
        response = requests.get(f"{base_url}/api/skills-network/searches")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Available searches endpoint working:")
                print(f"   • Total searches: {data['total_searches']}")
                if data['searches']:
                    print(f"   • Latest search: {data['searches'][0]['keyword']} ({data['searches'][0]['job_count']} jobs)")
                else:
                    print("   • No searches available yet")
            else:
                print(f"❌ Available searches API returned error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing available searches API: {e}")
    
    # Test 5: Skills network demo page
    print("\n5️⃣ Testing /skills-network demo page")
    try:
        response = requests.get(f"{base_url}/skills-network")
        if response.status_code == 200:
            if "Skills Network" in response.text:
                print("✅ Demo page loads successfully")
            else:
                print("⚠️  Demo page loaded but content may be incomplete")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing demo page: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Testing Complete!")
    print("\nTo view the skills network visualization:")
    print(f"🌐 Open: {base_url}/skills-network")
    print(f"📊 API: {base_url}/api/skills-network")
    print(f"🔍 Available searches: {base_url}/api/skills-network/searches")
    
    return True

def test_api_response_format():
    """Test that the API returns the correct format for vis-network"""
    
    print("\n🔍 Testing API Response Format for vis-network")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/api/skills-network")
        if response.status_code == 200:
            data = response.json()
            
            # Check required structure
            required_fields = ['success', 'data']
            data_fields = ['skills', 'co_occurrences']
            
            print("📋 Checking response structure...")
            for field in required_fields:
                if field in data:
                    print(f"   ✅ {field}: Present")
                else:
                    print(f"   ❌ {field}: Missing")
                    return False
            
            for field in data_fields:
                if field in data['data']:
                    print(f"   ✅ data.{field}: Present")
                else:
                    print(f"   ❌ data.{field}: Missing")
                    return False
            
            # Check data types
            print("\n🔍 Checking data types...")
            if isinstance(data['data']['skills'], dict):
                print("   ✅ skills: Dictionary format ✓")
            else:
                print(f"   ❌ skills: Expected dict, got {type(data['data']['skills'])}")
                return False
            
            if isinstance(data['data']['co_occurrences'], dict):
                print("   ✅ co_occurrences: Dictionary format ✓")
            else:
                print(f"   ❌ co_occurrences: Expected dict, got {type(data['data']['co_occurrences'])}")
                return False
            
            # Check sample data format
            print("\n📊 Sample data validation...")
            if data['data']['skills']:
                sample_skill = list(data['data']['skills'].items())[0]
                print(f"   ✅ Sample skill: {sample_skill[0]} (frequency: {sample_skill[1]})")
            else:
                print("   ⚠️  No skills data available")
            
            if data['data']['co_occurrences']:
                sample_connection = list(data['data']['co_occurrences'].items())[0]
                print(f"   ✅ Sample connection: {sample_connection[0]} (count: {sample_connection[1]})")
            else:
                print("   ⚠️  No connection data available")
            
            print("\n✅ API response format is compatible with vis-network!")
            return True
            
        else:
            print(f"❌ Could not test format: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API format: {e}")
        return False

if __name__ == "__main__":
    print("🚀 JobPulse Skills Network API Tester")
    print("Make sure your Flask app is running on localhost:5000")
    
    try:
        # Test basic functionality
        if test_skills_network_api():
            # Test response format
            test_api_response_format()
        else:
            print("\n❌ Basic API tests failed. Check your Flask app.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        sys.exit(1)
