#!/usr/bin/env python3
"""
Test script for the new Data Sources functionality
Run this to verify the data sources info is working correctly
"""

import requests
import json

def test_data_sources():
    """Test the data sources functionality"""
    
    base_url = "http://localhost:5002"
    
    print("🧪 Testing Data Sources Functionality")
    print("=" * 50)
    
    # Test 1: Data Sources API endpoint
    print("\n1️⃣ Testing /api/data-sources")
    try:
        response = requests.get(f"{base_url}/api/data-sources")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                sources = data['data_sources']
                live_count = data['live_sources']
                sample_count = data['sample_sources']
                total_count = data['total_sources']
                
                print(f"✅ Success! Found {total_count} total sources:")
                print(f"   • Live Sources: {live_count}")
                print(f"   • Sample Sources: {sample_count}")
                
                print("\n📊 Sample Data Sources:")
                for source in sources[:5]:
                    status_icon = "✅" if source['status'] == 'live' else "⚠️"
                    print(f"   {status_icon} {source['name']}: {source['status']} ({source['job_count']} jobs)")
                    
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on localhost:5002")
        return False
    except Exception as e:
        print(f"❌ Error testing data sources API: {e}")
        return False
    
    # Test 2: Updated Skills Network Stats
    print("\n2️⃣ Testing /api/skills-network/stats (updated)")
    try:
        response = requests.get(f"{base_url}/api/skills-network/stats")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['stats']
                data_source_status = stats.get('data_source_status', {})
                
                print(f"✅ Stats endpoint working with data source info:")
                print(f"   • Total Endpoints: {stats['total_endpoints']}")
                print(f"   • Total Sources: {data_source_status.get('total_sources', 'N/A')}")
                print(f"   • Live Sources: {data_source_status.get('live_sources', 'N/A')}")
                print(f"   • Sample Sources: {data_source_status.get('sample_sources', 'N/A')}")
                
            else:
                print(f"❌ Stats API returned error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing updated stats API: {e}")
    
    # Test 3: Main page with data sources info
    print("\n3️⃣ Testing main page with data sources info")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            content = response.text
            if "Data Sources Status" in content:
                print("✅ Main page includes data sources info")
            else:
                print("❌ Main page missing data sources info")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing main page: {e}")
    
    # Test 4: Skills Network demo page
    print("\n4️⃣ Testing skills network demo page")
    try:
        response = requests.get(f"{base_url}/skills-network")
        if response.status_code == 200:
            content = response.text
            if "Data Sources Status" in content:
                print("✅ Demo page includes data sources info")
            else:
                print("❌ Demo page missing data sources info")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing demo page: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Data Sources Testing Complete!")
    print("\n🌐 To view the data sources info:")
    print(f"   • Main Dashboard: {base_url}/")
    print(f"   • Skills Network Demo: {base_url}/skills-network")
    print(f"   • Data Sources API: {base_url}/api/data-sources")
    print(f"   • Updated Stats: {base_url}/api/skills-network/stats")
    
    return True

if __name__ == "__main__":
    test_data_sources()





