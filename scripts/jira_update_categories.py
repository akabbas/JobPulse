#!/usr/bin/env python3
"""
Jira Category Update Script for JobPulse
Updates existing tickets with proper emoji-focused categories and removes duplicates
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

class JiraCategoryUpdater:
    """Jira ticket category updater using REST API v3"""
    
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
    
    def update_issue_labels(self, issue_key: str, new_labels: List[str]) -> bool:
        """Update issue labels"""
        try:
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
                logger.info(f"✅ Updated labels for {issue_key}: {new_labels}")
                return True
            else:
                logger.error(f"❌ Failed to update labels for {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error updating labels for {issue_key}: {e}")
            return False
    
    def update_issue_description(self, issue_key: str, new_description: str) -> bool:
        """Update issue description"""
        try:
            payload = {
                "fields": {
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": new_description
                                    }
                                ]
                            }
                        ]
                    }
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
                logger.info(f"✅ Updated description for {issue_key}")
                return True
            else:
                logger.error(f"❌ Failed to update description for {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error updating description for {issue_key}: {e}")
            return False
    
    def delete_issue(self, issue_key: str) -> bool:
        """Delete an issue (for removing duplicates)"""
        try:
            response = requests.delete(
                f"{self.base_url}/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Deleted duplicate issue {issue_key}")
                return True
            else:
                logger.error(f"❌ Failed to delete issue {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error deleting issue {issue_key}: {e}")
            return False
    
    def update_categories(self, tickets_file: str) -> bool:
        """Update ticket categories based on the new structure"""
        try:
            with open(tickets_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"🚀 Starting category updates for project {data['project']['key']}")
            
            # Test connection
            if not self.test_connection():
                return False
            
            # Category mapping for emoji-focused categories
            category_mapping = {
                "🚀 Data Upgrades": ["snowflake", "data", "analytics"],
                "🔧 Technical Upgrades": ["technical", "upgrade", "infrastructure"],
                "💰 Monetization Tasks": ["monetization", "premium", "revenue"],
                "This Week": ["urgent", "critical", "priority"],
                "To Do": ["backlog", "standard", "development"],
                "General Backlog": ["general", "foundation", "core"],
                "In Progress": ["active", "current", "working"]
            }
            
            # Update epics
            epic_updates = 0
            for epic_data in data.get("epics", []):
                # Find the corresponding Jira epic
                epic_key = f"JB-{101 + epic_updates}"  # Assuming sequential numbering
                category = epic_data.get("category", "To Do")
                
                # Update labels with category-specific tags
                new_labels = epic_data.get("labels", []) + category_mapping.get(category, [])
                if self.update_issue_labels(epic_key, new_labels):
                    epic_updates += 1
            
            # Update tasks
            task_updates = 0
            for task_data in data.get("tasks", []):
                # Find the corresponding Jira task
                task_key = f"JB-{107 + task_updates}"  # Assuming sequential numbering
                category = task_data.get("category", "To Do")
                
                # Update labels with category-specific tags
                new_labels = task_data.get("labels", []) + category_mapping.get(category, [])
                if self.update_issue_labels(task_key, new_labels):
                    task_updates += 1
            
            logger.info(f"✅ Category updates completed!")
            logger.info(f"📊 Updated {epic_updates} epics")
            logger.info(f"📊 Updated {task_updates} tasks")
            
            # Save summary
            summary = {
                "project": data["project"]["key"],
                "epics_updated": epic_updates,
                "tasks_updated": task_updates,
                "category_mapping": category_mapping
            }
            
            with open("jira_category_update_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Update summary saved to jira_category_update_summary.json")
            logger.info(f"🎉 Category updates completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Update failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    tickets_file = os.getenv("TICKETS_FILE", "JIRA_TICKETS_FINAL_CATEGORIZED.json")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    if not os.path.exists(tickets_file):
        logger.error(f"❌ Tickets file not found: {tickets_file}")
        sys.exit(1)
    
    # Create updater
    updater = JiraCategoryUpdater(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Update categories
    success = updater.update_categories(tickets_file)
    
    if success:
        logger.info("🎉 All category updates completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Update failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
