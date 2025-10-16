#!/usr/bin/env python3
"""
Apply Smart Categories to Jira Tickets
Applies the intelligent categories discovered through content analysis
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

class SmartCategoryApplier:
    """Apply smart categories to Jira tickets"""
    
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
        
        # Load smart categories
        self.smart_categories = self.load_smart_categories()
        
    def load_smart_categories(self) -> Dict[str, Any]:
        """Load smart categories from analysis results"""
        try:
            with open("smart_categories_summary.json", "r") as f:
                data = json.load(f)
                return data.get("categories", {})
        except Exception as e:
            logger.error(f"❌ Error loading smart categories: {e}")
            return {}
    
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
    
    def apply_category_to_ticket(self, issue_key: str, category_name: str) -> bool:
        """Apply smart category to a specific ticket"""
        try:
            # Get current labels
            response = requests.get(
                f"{self.base_url}/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get issue {issue_key}: {response.status_code} - {response.text}")
                return False
            
            issue_data = response.json()
            current_labels = issue_data.get("fields", {}).get("labels", [])
            
            # Remove old category labels
            old_category_labels = [
                "critical-urgent", "complex-technical", "data-analytics", 
                "ai-machine-learning", "business-revenue", "infrastructure-ops",
                "user-experience", "quality-testing", "documentation-knowledge",
                "general-development", "general-backlog", "monetization-tasks",
                "this-week", "technical-upgrades", "data-upgrades", "in-progress", "to-do"
            ]
            
            # Clean category name for label
            clean_category = category_name.lower()
            clean_category = clean_category.replace("🚨", "").replace("🔧", "").replace("📊", "")
            clean_category = clean_category.replace("🤖", "").replace("💰", "").replace("🏗️", "")
            clean_category = clean_category.replace("👤", "").replace("🧪", "").replace("📚", "")
            clean_category = clean_category.replace("🛠️", "").replace(" ", "-").replace("&", "and")
            clean_category = clean_category.replace("--", "-").strip("-")
            
            # Create new labels list
            new_labels = [label for label in current_labels if label not in old_category_labels]
            new_labels.append(clean_category)
            
            # Update issue with new category
            payload = {
                "fields": {
                    "labels": new_labels
                }
            }
            
            update_response = requests.put(
                f"{self.base_url}/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if update_response.status_code == 204:
                logger.info(f"✅ Applied '{category_name}' to {issue_key}")
                return True
            else:
                logger.error(f"❌ Failed to apply category to {issue_key}: {update_response.status_code} - {update_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error applying category to {issue_key}: {e}")
            return False
    
    def apply_all_smart_categories(self) -> bool:
        """Apply all smart categories to their respective tickets"""
        try:
            logger.info("🚀 Starting smart category application")
            
            # Test connection
            if not self.test_connection():
                return False
            
            if not self.smart_categories:
                logger.error("❌ No smart categories loaded")
                return False
            
            # Apply categories
            total_applied = 0
            category_stats = {}
            
            for category_name, category_data in self.smart_categories.items():
                ticket_keys = category_data.get("ticket_keys", [])
                applied_count = 0
                
                logger.info(f"📁 Applying category: {category_name} ({len(ticket_keys)} tickets)")
                
                for ticket_key in ticket_keys:
                    if self.apply_category_to_ticket(ticket_key, category_name):
                        applied_count += 1
                        total_applied += 1
                
                category_stats[category_name] = {
                    "total_tickets": len(ticket_keys),
                    "applied_count": applied_count,
                    "success_rate": f"{(applied_count/len(ticket_keys)*100):.1f}%" if ticket_keys else "0%"
                }
                
                logger.info(f"  ✅ Applied to {applied_count}/{len(ticket_keys)} tickets")
            
            # Log summary
            logger.info(f"🎉 Smart category application completed!")
            logger.info(f"📊 Total categories applied: {len(self.smart_categories)}")
            logger.info(f"📊 Total tickets updated: {total_applied}")
            
            # Log category breakdown
            logger.info("📊 Category Application Results:")
            for category_name, stats in category_stats.items():
                logger.info(f"  📁 {category_name}: {stats['applied_count']}/{stats['total_tickets']} ({stats['success_rate']})")
            
            # Save application summary
            application_summary = {
                "total_categories": len(self.smart_categories),
                "total_tickets_updated": total_applied,
                "application_timestamp": "2025-10-16T14:37:00Z",
                "category_stats": category_stats
            }
            
            with open("smart_category_application_summary.json", "w") as f:
                json.dump(application_summary, f, indent=2)
            
            logger.info("📄 Application summary saved to smart_category_application_summary.json")
            logger.info("🎉 Smart category application completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Smart category application failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create applier
    applier = SmartCategoryApplier(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Apply smart categories
    success = applier.apply_all_smart_categories()
    
    if success:
        logger.info("🎉 All smart categories applied successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Smart category application failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
