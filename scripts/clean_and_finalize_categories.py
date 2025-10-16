#!/usr/bin/env python3
"""
Clean and Finalize Categories for JobPulse
Removes old categories and ensures only problem-focused categories remain
"""

import json
import logging
import os
import sys
import requests
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CategoryCleaner:
    """Clean up categories and ensure only problem-focused categories remain"""
    
    def __init__(self, jira_site: str, api_token: str, email: str = None):
        self.jira_site = jira_site
        self.api_token = api_token
        self.email = email or "ammrabbasher@gmail.com"
        self.base_url = f"https://{jira_site}/rest/api/3"
        self.auth = (self.email, api_token)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Problem-focused categories mapping
        self.problem_categories = {
            "🚫 Anti-Bot Detection & Bypass": "anti-bot-detection-and-bypass",
            "🔌 Multi-Source Data Collection": "multi-source-data-collection", 
            "🤖 AI-Powered Job Analysis": "ai-powered-job-analysis",
            "🏗️ Production Infrastructure": "production-infrastructure",
            "📊 Data Analytics & Insights": "data-analytics-and-insights",
            "🔧 Plugin Architecture & Extensibility": "plugin-architecture-and-extensibility",
            "⚡ Performance & Optimization": "performance-optimization",
            "🛡️ Error Handling & Reliability": "error-handling-and-reliability",
            "👤 User Experience & Interface": "user-experience-and-interface",
            "🧪 Testing & Quality Assurance": "quality-and-testing",
            "📚 Documentation & Knowledge": "documentation-and-knowledge",
            "💰 Business & Monetization": "business-and-monetization"
        }
        
        # Old categories to remove
        self.old_categories = [
            "general-backlog", "monetization-tasks", "this-week", 
            "technical-upgrades", "data-upgrades", "to-do", "in-progress",
            "-data-upgrades", "-monetization-tasks", "-technical-upgrades",
            "critical-and-urgent", "complex-technical-work", "data-and-analytics",
            "ai-and-machine-learning", "business-and-revenue", "infrastructure-and-ops",
            "user-experience-and-interface", "quality-and-testing", "documentation-and-knowledge"
        ]
        
        # Sprint labels to keep
        self.sprint_labels = [
            "sprint-1-critical-foundation", "sprint-2-infrastructure-hardening",
            "sprint-3-data-foundation", "sprint-4-plugin-architecture-migration",
            "sprint-5-advanced-data-analytics", "sprint-6-enterprise-integration",
            "sprint-7-quality-assurance-&-testing", "sprint-8-user-experience-&-authentication",
            "sprint-9-api-&-integration-platform", "sprint-10-monetization-&-business-model",
            "sprint-11-advanced-analytics-&-ai", "sprint-12-market-expansion-&-scale"
        ]
        
    def test_connection(self) -> bool:
        """Test Jira API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/myself",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"✅ Connected to Jira as {user_info.get('displayName', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Connection failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get issue details"""
        try:
            response = requests.get(
                f"{self.base_url}/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get issue {issue_key}: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error getting issue {issue_key}: {e}")
            return {}
    
    def clean_issue_labels(self, issue_key: str) -> bool:
        """Clean up labels for a specific issue"""
        try:
            # Get current issue data
            issue_data = self.get_issue(issue_key)
            if not issue_data:
                return False
            
            current_labels = issue_data.get("fields", {}).get("labels", [])
            
            # Keep only problem-focused categories and sprint labels
            new_labels = []
            for label in current_labels:
                # Keep sprint labels
                if any(sprint in label for sprint in self.sprint_labels):
                    new_labels.append(label)
                # Keep problem-focused categories
                elif any(prob_cat in label for prob_cat in self.problem_categories.values()):
                    new_labels.append(label)
                # Keep technical labels that are not old categories
                elif not any(old_cat in label for old_cat in self.old_categories):
                    # Keep technical labels like 'api', 'database', 'testing', etc.
                    if any(tech in label for tech in ['api', 'database', 'testing', 'security', 'performance', 'monitoring', 'caching', 'redis', 'postgresql', 'docker', 'kubernetes', 'ci-cd', 'alembic', 'swagger', 'endpoints', 'middleware', 'health-check', 'rate-limiting', 'authentication', 'billing', 'premium', 'subscription', 'revenue', 'monetization', 'enterprise', 'packaging', 'integration', 'migration', 'refactoring', 'upgrade', 'stability', 'reliability', 'quality', 'standard', 'technical', 'development', 'foundation', 'core', 'priority', 'active', 'current', 'working', 'test', 'broken', 'fix', 'urgent', 'critical', 'alerts', 'notifications', 'dashboard', 'user', 'users', 'web-dashboard', 'scraper', 'scrapers', 'scraper-manager', 'selectors', 'dice', 'stack-overflow', 'greenhouse', 'lever', 'snowflake', 'cortex', 'streamlit', 'native-app', 'data-sharing', 'real-time', 'matching', 'analytics', 'data', 'ai', 'caching', 'redis', 'postgresql', 'docker', 'kubernetes', 'ci-cd', 'alembic', 'swagger', 'endpoints', 'middleware', 'health-check', 'rate-limiting', 'authentication', 'billing', 'premium', 'subscription', 'revenue', 'monetization', 'enterprise', 'packaging', 'integration', 'migration', 'refactoring', 'upgrade', 'stability', 'reliability', 'quality', 'standard', 'technical', 'development', 'foundation', 'core', 'priority', 'active', 'current', 'working', 'test', 'broken', 'fix', 'urgent', 'critical', 'alerts', 'notifications', 'dashboard', 'user', 'users', 'web-dashboard', 'scraper', 'scrapers', 'scraper-manager', 'selectors', 'dice', 'stack-overflow', 'greenhouse', 'lever', 'snowflake', 'cortex', 'streamlit', 'native-app', 'data-sharing', 'real-time', 'matching', 'analytics', 'data', 'ai']):
                        new_labels.append(label)
            
            # Update issue with cleaned labels
            payload = {
                "fields": {
                    "labels": new_labels
                }
            }
            
            response = requests.put(
                f"{self.base_url}/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Cleaned labels for {issue_key}")
                return True
            else:
                logger.error(f"❌ Failed to clean {issue_key}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error cleaning {issue_key}: {e}")
            return False
    
    def clean_all_issues(self) -> bool:
        """Clean up all issues"""
        try:
            logger.info("🚀 Starting category cleanup")
            
            # Test connection
            if not self.test_connection():
                return False
            
            # Get all issues in the project
            response = requests.get(
                f"{self.base_url}/search/jql",
                auth=self.auth,
                headers=self.headers,
                params={
                    "jql": "project = JB",
                    "fields": "summary,labels",
                    "maxResults": 200
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get issues: {response.status_code} - {response.text}")
                return False
            
            issues = response.json().get("issues", [])
            logger.info(f"📋 Found {len(issues)} issues to clean")
            
            # Clean each issue
            cleaned_count = 0
            cleanup_results = []
            
            for i, issue in enumerate(issues):
                issue_key = issue.get("key")
                logger.info(f"🧹 Cleaning issue {i+1}/{len(issues)}: {issue_key}")
                
                if self.clean_issue_labels(issue_key):
                    cleaned_count += 1
                    cleanup_results.append({
                        "issue_key": issue_key,
                        "cleaned": True
                    })
                else:
                    cleanup_results.append({
                        "issue_key": issue_key,
                        "cleaned": False
                    })
            
            # Log results
            logger.info(f"🎉 Category cleanup completed!")
            logger.info(f"📊 Cleaned {cleaned_count}/{len(issues)} issues")
            
            # Save results
            results = {
                "total_issues": len(issues),
                "cleaned_issues": cleaned_count,
                "cleanup_results": cleanup_results,
                "cleanup_timestamp": "2025-10-16T15:00:00Z"
            }
            
            with open("category_cleanup_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info("📄 Cleanup results saved to category_cleanup_results.json")
            logger.info("🎉 Category cleanup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Category cleanup failed: {e}")
            return False
    
    def verify_cleanup(self) -> bool:
        """Verify that cleanup was successful"""
        try:
            logger.info("🔍 Verifying category cleanup")
            
            # Get all issues and check their labels
            response = requests.get(
                f"{self.base_url}/search/jql",
                auth=self.auth,
                headers=self.headers,
                params={
                    "jql": "project = JB",
                    "fields": "summary,labels",
                    "maxResults": 200
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get issues: {response.status_code} - {response.text}")
                return False
            
            issues = response.json().get("issues", [])
            
            # Count categories
            from collections import Counter
            category_counts = Counter()
            old_category_counts = Counter()
            
            for issue in issues:
                labels = issue.get("fields", {}).get("labels", [])
                
                for label in labels:
                    # Check for problem-focused categories
                    if any(prob_cat in label for prob_cat in self.problem_categories.values()):
                        category_counts[label] += 1
                    
                    # Check for old categories
                    if any(old_cat in label for old_cat in self.old_categories):
                        old_category_counts[label] += 1
            
            logger.info("📊 Problem-Focused Categories:")
            for category, count in category_counts.most_common():
                logger.info(f"  📁 {category}: {count} tickets")
            
            if old_category_counts:
                logger.warning("⚠️ Old Categories Still Present:")
                for category, count in old_category_counts.most_common():
                    logger.warning(f"  🗑️ {category}: {count} tickets")
            else:
                logger.info("✅ No old categories found - cleanup successful!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create cleaner
    cleaner = CategoryCleaner(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Clean all issues
    success = cleaner.clean_all_issues()
    
    if success:
        # Verify cleanup
        cleaner.verify_cleanup()
        logger.info("🎉 Category cleanup and verification completed!")
        sys.exit(0)
    else:
        logger.error("❌ Category cleanup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
