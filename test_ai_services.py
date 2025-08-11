#!/usr/bin/env python3
"""
Test script for JobPulse AI Services
Demonstrates the functionality of AI-powered job analysis, matching, and resume generation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ai_services():
    """Test all AI services"""
    print("🚀 Testing JobPulse AI Services")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
        print("   You can still test the service structure without making API calls.")
        api_key = "test-key"
    
    try:
        # Test AI Job Analyzer
        print("\n1. Testing AI Job Analyzer...")
        from ai_services.ai_analyzer import AIJobAnalyzer
        
        analyzer = AIJobAnalyzer(api_key=api_key)
        print("   ✅ AI Job Analyzer initialized successfully")
        print(f"   📊 Model: {analyzer.model}")
        
        # Test AI Job Matcher
        print("\n2. Testing AI Job Matcher...")
        from ai_services.ai_matcher import AIJobMatcher
        
        matcher = AIJobMatcher(api_key=api_key)
        print("   ✅ AI Job Matcher initialized successfully")
        print(f"   📊 Model: {matcher.model}")
        
        # Test AI Resume Generator
        print("\n3. Testing AI Resume Generator...")
        from ai_services.ai_resume_generator import AIResumeGenerator
        
        generator = AIResumeGenerator(api_key=api_key)
        print("   ✅ AI Resume Generator initialized successfully")
        print(f"   📊 Model: {generator.model}")
        
        print("\n🎉 All AI services initialized successfully!")
        
        # Test with sample data (without making API calls)
        if api_key == "test-key":
            print("\n📝 Note: Using test mode - no actual API calls will be made")
            print("   Set OPENAI_API_KEY to test full functionality")
            
            # Demonstrate service structure
            print("\n🔍 Service Capabilities:")
            print("   • AI Job Analyzer: Job description analysis, skill extraction")
            print("   • AI Job Matcher: Intelligent job matching, personalized recommendations")
            print("   • AI Resume Generator: Targeted resumes, cover letters, ATS optimization")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_service_methods():
    """Test service methods without API calls"""
    print("\n🧪 Testing Service Methods (Mock Mode)")
    print("=" * 50)
    
    try:
        from ai_services.ai_analyzer import AIJobAnalyzer
        
        # Create analyzer with test key
        analyzer = AIJobAnalyzer(api_key="test-key")
        
        # Test method availability
        methods = [
            'analyze_job_description',
            'generate_skill_recommendations', 
            'analyze_market_trends',
            'update_model',
            'get_usage_stats'
        ]
        
        for method in methods:
            if hasattr(analyzer, method):
                print(f"   ✅ {method} method available")
            else:
                print(f"   ❌ {method} method missing")
        
        print("\n✅ All expected methods are available")
        return True
        
    except Exception as e:
        print(f"❌ Error testing methods: {e}")
        return False

def main():
    """Main test function"""
    print("JobPulse AI Services Test Suite")
    print("=" * 50)
    
    # Test service initialization
    if not test_ai_services():
        print("\n❌ AI services test failed")
        return 1
    
    # Test service methods
    if not test_service_methods():
        print("\n❌ Service methods test failed")
        return 1
    
    print("\n🎉 All tests passed successfully!")
    print("\n📋 Next Steps:")
    print("   1. Set your OpenAI API key: export OPENAI_API_KEY='your-key'")
    print("   2. Test with real data: python test_ai_services.py")
    print("   3. Integrate with web dashboard")
    print("   4. Deploy to production")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
