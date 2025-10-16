#!/usr/bin/env python3
"""
Assign Categories to Jira Tickets Based on Problems They Solve
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

class CategoryAssignment:
    """Assign categories to Jira tickets based on problems they solve"""
    
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
        
        # Category mapping based on problems solved
        self.category_mapping = {
            "🚀 Data Upgrades": {
                "problems": ["snowflake integration", "data infrastructure", "analytics", "data sharing"],
                "keywords": ["snowflake", "data", "analytics", "cortex", "streamlit", "native-app"],
                "tickets": []
            },
            "🔧 Technical Upgrades": {
                "problems": ["infrastructure", "performance", "monitoring", "security", "reliability"],
                "keywords": ["redis", "caching", "rate-limiting", "health-check", "monitoring", "migration"],
                "tickets": []
            },
            "💰 Monetization Tasks": {
                "problems": ["revenue generation", "premium features", "business value"],
                "keywords": ["monetization", "premium", "revenue", "subscription", "billing"],
                "tickets": []
            },
            "This Week": {
                "problems": ["critical production issues", "broken functionality", "urgent fixes"],
                "keywords": ["broken", "critical", "urgent", "fix", "scraper", "dice", "stack-overflow"],
                "tickets": []
            },
            "To Do": {
                "problems": ["technical debt", "quality improvements", "standard development"],
                "keywords": ["migration", "testing", "documentation", "refactoring", "architecture"],
                "tickets": []
            },
            "General Backlog": {
                "problems": ["foundational features", "user experience", "core functionality"],
                "keywords": ["authentication", "user", "alerts", "notifications", "foundation"],
                "tickets": []
            },
            "In Progress": {
                "problems": ["currently active issues", "ongoing critical work"],
                "keywords": ["active", "current", "working", "progress"],
                "tickets": []
            }
        }
        
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
    
    def analyze_issue_for_category(self, issue_data: Dict[str, Any]) -> str:
        """Analyze issue to determine best category based on problem it solves"""
        try:
            summary = issue_data.get("fields", {}).get("summary", "").lower()
            description = issue_data.get("fields", {}).get("description", {})
            
            # Extract text from description
            description_text = ""
            if isinstance(description, dict) and "content" in description:
                for content in description.get("content", []):
                    if content.get("type") == "paragraph":
                        for para_content in content.get("content", []):
                            if para_content.get("type") == "text":
                                description_text += para_content.get("text", "").lower()
            
            # Combine summary and description for analysis
            full_text = f"{summary} {description_text}"
            
            # Score each category based on keyword matches
            category_scores = {}
            for category, config in self.category_mapping.items():
                score = 0
                for keyword in config["keywords"]:
                    if keyword.lower() in full_text:
                        score += 1
                category_scores[category] = score
            
            # Find the category with highest score
            best_category = max(category_scores, key=category_scores.get)
            
            # If no clear match, assign to "To Do" as default
            if category_scores[best_category] == 0:
                best_category = "To Do"
            
            logger.info(f"📊 {issue_data.get('key', 'Unknown')}: {best_category} (score: {category_scores[best_category]})")
            return best_category
            
        except Exception as e:
            logger.error(f"❌ Error analyzing issue: {e}")
            return "To Do"
    
    def update_issue_labels(self, issue_key: str, category: str) -> bool:
        """Update issue with category-specific labels"""
        try:
            # Get current labels
            issue_data = self.get_issue(issue_key)
            current_labels = issue_data.get("fields", {}).get("labels", [])
            
            # Add category-specific labels
            category_labels = self.category_mapping.get(category, {}).get("keywords", [])
            new_labels = list(set(current_labels + category_labels + [category]))
            
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
                logger.info(f"✅ Updated {issue_key} with category: {category}")
                return True
            else:
                logger.error(f"❌ Failed to update {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error updating {issue_key}: {e}")
            return False
    
    def assign_categories_to_all_tickets(self) -> bool:
        """Assign categories to all tickets in the project"""
        try:
            logger.info("🚀 Starting category assignment for all tickets")
            
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
                    "fields": "summary,description,labels",
                    "maxResults": 200
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get issues: {response.status_code} - {response.text}")
                return False
            
            issues = response.json().get("issues", [])
            logger.info(f"📋 Found {len(issues)} issues to categorize")
            
            # Process each issue
            categorized_count = 0
            category_counts = {}
            
            for issue in issues:
                issue_key = issue.get("key")
                category = self.analyze_issue_for_category(issue)
                
                if self.update_issue_labels(issue_key, category):
                    categorized_count += 1
                    category_counts[category] = category_counts.get(category, 0) + 1
                    self.category_mapping[category]["tickets"].append(issue_key)
            
            logger.info(f"✅ Category assignment completed!")
            logger.info(f"📊 Categorized {categorized_count} tickets")
            
            # Log category breakdown
            logger.info("📊 Category Breakdown:")
            for category, count in category_counts.items():
                logger.info(f"  {category}: {count} tickets")
            
            # Save summary
            summary = {
                "total_tickets": len(issues),
                "categorized_tickets": categorized_count,
                "category_counts": category_counts,
                "category_mapping": self.category_mapping
            }
            
            with open("category_assignment_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Assignment summary saved to category_assignment_summary.json")
            logger.info(f"🎉 Category assignment completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Category assignment failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create category assigner
    assigner = CategoryAssignment(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Assign categories
    success = assigner.assign_categories_to_all_tickets()
    
    if success:
        logger.info("🎉 All tickets categorized successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Category assignment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
