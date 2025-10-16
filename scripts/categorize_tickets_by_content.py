#!/usr/bin/env python3
"""
Categorize Tickets by Content for JobPulse
Assigns tickets to specific categories based on their content, acceptance criteria, and descriptions
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

class TicketCategorizer:
    """Categorize tickets based on their content and descriptions"""
    
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
        
        # Target category distribution
        self.target_categories = {
            "General Backlog": {
                "target_count": 2,
                "keywords": ["authentication", "user", "alerts", "notifications", "foundation", "core"],
                "tickets": []
            },
            "💰 Monetization Tasks": {
                "target_count": 2,
                "keywords": ["monetization", "premium", "revenue", "subscription", "billing", "business"],
                "tickets": []
            },
            "This Week": {
                "target_count": 1,
                "keywords": ["broken", "critical", "urgent", "fix", "scraper", "dice", "stack-overflow", "emergency"],
                "tickets": []
            },
            "🔧 Technical Upgrades": {
                "target_count": 4,
                "keywords": ["redis", "caching", "rate-limiting", "health-check", "monitoring", "migration", "infrastructure", "performance"],
                "tickets": []
            },
            "🚀 Data Upgrades": {
                "target_count": 3,
                "keywords": ["snowflake", "data", "analytics", "cortex", "streamlit", "native-app", "ai", "machine-learning"],
                "tickets": []
            },
            "In Progress": {
                "target_count": 1,
                "keywords": ["active", "current", "working", "progress", "ongoing"],
                "tickets": []
            },
            "To Do": {
                "target_count": 113,
                "keywords": ["migration", "testing", "documentation", "refactoring", "architecture", "plugin", "scraper"],
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
    
    def extract_text_content(self, issue_data: Dict[str, Any]) -> str:
        """Extract all text content from issue for analysis"""
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
            
            # Combine all text content
            full_text = f"{summary} {description_text}"
            return full_text
            
        except Exception as e:
            logger.error(f"❌ Error extracting text content: {e}")
            return ""
    
    def analyze_ticket_for_category(self, issue_data: Dict[str, Any]) -> str:
        """Analyze ticket to determine best category based on content"""
        try:
            full_text = self.extract_text_content(issue_data)
            
            # Score each category based on keyword matches
            category_scores = {}
            for category, config in self.target_categories.items():
                if category == "To Do":  # Skip To Do as it's the default
                    continue
                    
                score = 0
                for keyword in config["keywords"]:
                    if keyword.lower() in full_text:
                        score += 1
                
                # Bonus points for exact matches
                if any(keyword.lower() in full_text for keyword in ["snowflake", "data", "analytics"]):
                    if category == "🚀 Data Upgrades":
                        score += 3
                elif any(keyword.lower() in full_text for keyword in ["broken", "critical", "urgent", "fix"]):
                    if category == "This Week":
                        score += 3
                elif any(keyword.lower() in full_text for keyword in ["redis", "caching", "monitoring"]):
                    if category == "🔧 Technical Upgrades":
                        score += 3
                elif any(keyword.lower() in full_text for keyword in ["premium", "revenue", "monetization"]):
                    if category == "💰 Monetization Tasks":
                        score += 3
                elif any(keyword.lower() in full_text for keyword in ["user", "auth", "alerts"]):
                    if category == "General Backlog":
                        score += 3
                elif any(keyword.lower() in full_text for keyword in ["active", "current", "working"]):
                    if category == "In Progress":
                        score += 3
                
                category_scores[category] = score
            
            # Find the category with highest score
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                if category_scores[best_category] > 0:
                    return best_category
            
            # Default to To Do if no clear match
            return "To Do"
            
        except Exception as e:
            logger.error(f"❌ Error analyzing ticket: {e}")
            return "To Do"
    
    def update_issue_category(self, issue_key: str, category: str) -> bool:
        """Update issue with category assignment"""
        try:
            # Get current labels
            issue_data = self.get_issue(issue_key)
            current_labels = issue_data.get("fields", {}).get("labels", [])
            
            # Remove old category labels
            category_labels_to_remove = []
            for label in current_labels:
                if label in ["general-backlog", "monetization-tasks", "this-week", "technical-upgrades", "data-upgrades", "in-progress", "to-do"]:
                    category_labels_to_remove.append(label)
            
            # Add new category label
            category_label = category.lower().replace(" ", "-").replace("💰", "").replace("🚀", "").replace("🔧", "")
            new_labels = [label for label in current_labels if label not in category_labels_to_remove]
            new_labels.append(category_label)
            
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
                logger.info(f"✅ Categorized {issue_key} as: {category}")
                return True
            else:
                logger.error(f"❌ Failed to categorize {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error categorizing {issue_key}: {e}")
            return False
    
    def categorize_all_tickets(self) -> bool:
        """Categorize all tickets based on content"""
        try:
            logger.info("🚀 Starting ticket categorization based on content")
            
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
                category = self.analyze_ticket_for_category(issue)
                
                if self.update_issue_category(issue_key, category):
                    categorized_count += 1
                    category_counts[category] = category_counts.get(category, 0) + 1
                    self.target_categories[category]["tickets"].append(issue_key)
            
            logger.info(f"✅ Ticket categorization completed!")
            logger.info(f"📊 Categorized {categorized_count} tickets")
            
            # Log category breakdown
            logger.info("📊 Category Breakdown:")
            for category, count in category_counts.items():
                target = self.target_categories[category]["target_count"]
                status = "✅" if count == target else "⚠️" if count < target else "❌"
                logger.info(f"  {status} {category}: {count}/{target} tickets")
            
            # Save summary
            summary = {
                "total_tickets": len(issues),
                "categorized_tickets": categorized_count,
                "category_counts": category_counts,
                "target_categories": self.target_categories
            }
            
            with open("content_based_categorization_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Categorization summary saved to content_based_categorization_summary.json")
            logger.info(f"🎉 Ticket categorization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ticket categorization failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create categorizer
    categorizer = TicketCategorizer(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Categorize tickets
    success = categorizer.categorize_all_tickets()
    
    if success:
        logger.info("🎉 All tickets categorized by content successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Ticket categorization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
