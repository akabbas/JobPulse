#!/usr/bin/env python3
"""
Redistribute Tickets to Target Categories for JobPulse
Redistributes tickets to match exact target category distribution
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

class TicketRedistributor:
    """Redistribute tickets to match target category distribution"""
    
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
        
        # Target category distribution (exact requirements)
        self.target_distribution = {
            "General Backlog": 2,
            "💰 Monetization Tasks": 2,
            "This Week": 1,
            "🔧 Technical Upgrades": 4,
            "🚀 Data Upgrades": 3,
            "In Progress": 1,
            "To Do": 87  # Remaining tickets go to To Do
        }
        
        # Priority-based assignment rules
        self.assignment_rules = {
            "General Backlog": {
                "keywords": ["authentication", "user", "alerts", "notifications", "foundation", "core"],
                "priority": 1
            },
            "💰 Monetization Tasks": {
                "keywords": ["monetization", "premium", "revenue", "subscription", "billing", "business"],
                "priority": 2
            },
            "This Week": {
                "keywords": ["broken", "critical", "urgent", "fix", "scraper", "dice", "stack-overflow", "emergency"],
                "priority": 3
            },
            "🔧 Technical Upgrades": {
                "keywords": ["redis", "caching", "rate-limiting", "health-check", "monitoring", "migration", "infrastructure", "performance"],
                "priority": 4
            },
            "🚀 Data Upgrades": {
                "keywords": ["snowflake", "data", "analytics", "cortex", "streamlit", "native-app", "ai", "machine-learning"],
                "priority": 5
            },
            "In Progress": {
                "keywords": ["active", "current", "working", "progress", "ongoing"],
                "priority": 6
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
    
    def calculate_category_score(self, full_text: str, category: str) -> int:
        """Calculate score for a category based on content"""
        if category not in self.assignment_rules:
            return 0
            
        keywords = self.assignment_rules[category]["keywords"]
        score = 0
        
        for keyword in keywords:
            if keyword.lower() in full_text:
                score += 1
        
        # Bonus points for exact matches
        if category == "🚀 Data Upgrades" and any(k in full_text for k in ["snowflake", "data", "analytics"]):
            score += 3
        elif category == "This Week" and any(k in full_text for k in ["broken", "critical", "urgent", "fix"]):
            score += 3
        elif category == "🔧 Technical Upgrades" and any(k in full_text for k in ["redis", "caching", "monitoring"]):
            score += 3
        elif category == "💰 Monetization Tasks" and any(k in full_text for k in ["premium", "revenue", "monetization"]):
            score += 3
        elif category == "General Backlog" and any(k in full_text for k in ["user", "auth", "alerts"]):
            score += 3
        elif category == "In Progress" and any(k in full_text for k in ["active", "current", "working"]):
            score += 3
            
        return score
    
    def assign_ticket_to_category(self, issue_key: str, category: str) -> bool:
        """Assign ticket to specific category"""
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
                logger.info(f"✅ Assigned {issue_key} to {category}")
                return True
            else:
                logger.error(f"❌ Failed to assign {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error assigning {issue_key}: {e}")
            return False
    
    def redistribute_tickets_to_targets(self) -> bool:
        """Redistribute tickets to match target distribution"""
        try:
            logger.info("🚀 Starting ticket redistribution to target categories")
            
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
            logger.info(f"📋 Found {len(issues)} issues to redistribute")
            
            # Analyze all tickets and create priority list
            ticket_scores = []
            for issue in issues:
                issue_key = issue.get("key")
                full_text = self.extract_text_content(issue)
                
                # Calculate scores for each category
                scores = {}
                for category in self.assignment_rules.keys():
                    scores[category] = self.calculate_category_score(full_text, category)
                
                ticket_scores.append({
                    "issue_key": issue_key,
                    "scores": scores,
                    "best_category": max(scores, key=scores.get) if max(scores.values()) > 0 else "To Do"
                })
            
            # Sort by best category score
            ticket_scores.sort(key=lambda x: max(x["scores"].values()), reverse=True)
            
            # Distribute tickets to categories
            category_assignments = {category: [] for category in self.target_distribution.keys()}
            assigned_count = 0
            
            # First pass: assign based on best match
            for ticket in ticket_scores:
                issue_key = ticket["issue_key"]
                best_category = ticket["best_category"]
                
                # Check if category still has capacity
                if len(category_assignments[best_category]) < self.target_distribution[best_category]:
                    if self.assign_ticket_to_category(issue_key, best_category):
                        category_assignments[best_category].append(issue_key)
                        assigned_count += 1
                else:
                    # Try next best category
                    sorted_scores = sorted(ticket["scores"].items(), key=lambda x: x[1], reverse=True)
                    for category, score in sorted_scores:
                        if category != best_category and len(category_assignments[category]) < self.target_distribution[category]:
                            if self.assign_ticket_to_category(issue_key, category):
                                category_assignments[category].append(issue_key)
                                assigned_count += 1
                                break
                    else:
                        # Assign to To Do if no other category available
                        if len(category_assignments["To Do"]) < self.target_distribution["To Do"]:
                            if self.assign_ticket_to_category(issue_key, "To Do"):
                                category_assignments["To Do"].append(issue_key)
                                assigned_count += 1
            
            logger.info(f"✅ Ticket redistribution completed!")
            logger.info(f"📊 Redistributed {assigned_count} tickets")
            
            # Log category breakdown
            logger.info("📊 Target Category Distribution:")
            for category, target in self.target_distribution.items():
                actual = len(category_assignments[category])
                status = "✅" if actual == target else "⚠️" if actual < target else "❌"
                logger.info(f"  {status} {category}: {actual}/{target} tickets")
            
            # Save summary
            summary = {
                "total_tickets": len(issues),
                "redistributed_tickets": assigned_count,
                "target_distribution": self.target_distribution,
                "actual_distribution": {category: len(tickets) for category, tickets in category_assignments.items()},
                "category_assignments": category_assignments
            }
            
            with open("target_category_redistribution_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Redistribution summary saved to target_category_redistribution_summary.json")
            logger.info(f"🎉 Ticket redistribution completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ticket redistribution failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create redistributor
    redistributor = TicketRedistributor(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Redistribute tickets
    success = redistributor.redistribute_tickets_to_targets()
    
    if success:
        logger.info("🎉 All tickets redistributed to target categories successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Ticket redistribution failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
