#!/usr/bin/env python3
"""
Corporate Sprint Assignment Script for JobPulse
Assigns tickets to sprints based on complexity, innovation, and sequential order
"""

import json
import logging
import os
import sys
import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CorporateSprintAssigner:
    """Assign tickets to corporate sprints based on complexity and innovation"""
    
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
        
        # Corporate sprint structure
        self.sprint_structure = {
            "Sprint 1: Critical Foundation": {
                "story_points": 40,
                "team_size": 3,
                "risk_level": "Low",
                "focus": "Emergency fixes and system stability",
                "tickets": []
            },
            "Sprint 2: Infrastructure Hardening": {
                "story_points": 42,
                "team_size": 4,
                "risk_level": "Low",
                "focus": "System reliability and performance",
                "tickets": []
            },
            "Sprint 3: Data Foundation": {
                "story_points": 38,
                "team_size": 4,
                "risk_level": "Medium",
                "focus": "Core data infrastructure",
                "tickets": []
            },
            "Sprint 4: Plugin Architecture Migration": {
                "story_points": 45,
                "team_size": 5,
                "risk_level": "High",
                "focus": "System architecture modernization",
                "tickets": []
            },
            "Sprint 5: Advanced Data Analytics": {
                "story_points": 40,
                "team_size": 4,
                "risk_level": "Medium",
                "focus": "AI and analytics capabilities",
                "tickets": []
            },
            "Sprint 6: Enterprise Integration": {
                "story_points": 43,
                "team_size": 5,
                "risk_level": "High",
                "focus": "Enterprise-grade features",
                "tickets": []
            },
            "Sprint 7: Quality Assurance & Testing": {
                "story_points": 35,
                "team_size": 3,
                "risk_level": "Low",
                "focus": "Quality and reliability",
                "tickets": []
            },
            "Sprint 8: User Experience & Authentication": {
                "story_points": 38,
                "team_size": 4,
                "risk_level": "Medium",
                "focus": "User-facing features",
                "tickets": []
            },
            "Sprint 9: API & Integration Platform": {
                "story_points": 42,
                "team_size": 4,
                "risk_level": "Medium",
                "focus": "API development and integrations",
                "tickets": []
            },
            "Sprint 10: Monetization & Business Model": {
                "story_points": 36,
                "team_size": 3,
                "risk_level": "Medium",
                "focus": "Revenue generation",
                "tickets": []
            },
            "Sprint 11: Advanced Analytics & AI": {
                "story_points": 44,
                "team_size": 5,
                "risk_level": "High",
                "focus": "Cutting-edge AI features",
                "tickets": []
            },
            "Sprint 12: Market Expansion & Scale": {
                "story_points": 40,
                "team_size": 4,
                "risk_level": "High",
                "focus": "Business growth and scaling",
                "tickets": []
            }
        }
        
        # Ticket assignment rules based on categories
        self.assignment_rules = {
            "this-week": ["Sprint 1: Critical Foundation"],
            "technical-upgrades": ["Sprint 2: Infrastructure Hardening"],
            "data-upgrades": ["Sprint 3: Data Foundation", "Sprint 5: Advanced Data Analytics"],
            "to-do": ["Sprint 4: Plugin Architecture Migration", "Sprint 7: Quality Assurance & Testing"],
            "general-backlog": ["Sprint 8: User Experience & Authentication"],
            "monetization-tasks": ["Sprint 10: Monetization & Business Model"]
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
    
    def determine_sprint_for_ticket(self, issue_data: Dict[str, Any]) -> str:
        """Determine which sprint a ticket should be assigned to"""
        try:
            summary = issue_data.get("fields", {}).get("summary", "").lower()
            labels = issue_data.get("fields", {}).get("labels", [])
            
            # Check for category labels
            for label in labels:
                if label in self.assignment_rules:
                    sprints = self.assignment_rules[label]
                    # Return the first sprint for this category
                    return sprints[0]
            
            # Default assignment based on content analysis
            if any(keyword in summary for keyword in ["fix", "broken", "critical", "urgent"]):
                return "Sprint 1: Critical Foundation"
            elif any(keyword in summary for keyword in ["redis", "caching", "monitoring", "health"]):
                return "Sprint 2: Infrastructure Hardening"
            elif any(keyword in summary for keyword in ["snowflake", "data", "analytics"]):
                return "Sprint 3: Data Foundation"
            elif any(keyword in summary for keyword in ["plugin", "architecture", "migration"]):
                return "Sprint 4: Plugin Architecture Migration"
            elif any(keyword in summary for keyword in ["ai", "cortex", "streamlit"]):
                return "Sprint 5: Advanced Data Analytics"
            elif any(keyword in summary for keyword in ["enterprise", "native-app", "sharing"]):
                return "Sprint 6: Enterprise Integration"
            elif any(keyword in summary for keyword in ["test", "quality", "coverage"]):
                return "Sprint 7: Quality Assurance & Testing"
            elif any(keyword in summary for keyword in ["user", "auth", "profile", "alert"]):
                return "Sprint 8: User Experience & Authentication"
            elif any(keyword in summary for keyword in ["api", "documentation", "integration"]):
                return "Sprint 9: API & Integration Platform"
            elif any(keyword in summary for keyword in ["premium", "monetization", "revenue"]):
                return "Sprint 10: Monetization & Business Model"
            else:
                return "Sprint 7: Quality Assurance & Testing"  # Default fallback
                
        except Exception as e:
            logger.error(f"❌ Error determining sprint for ticket: {e}")
            return "Sprint 7: Quality Assurance & Testing"
    
    def update_issue_sprint(self, issue_key: str, sprint_name: str) -> bool:
        """Update issue with sprint assignment"""
        try:
            # Add sprint label to the issue
            issue_data = self.get_issue(issue_key)
            current_labels = issue_data.get("fields", {}).get("labels", [])
            
            # Add sprint label
            sprint_label = sprint_name.lower().replace(" ", "-").replace(":", "")
            new_labels = list(set(current_labels + [sprint_label]))
            
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
                logger.info(f"✅ Updated {issue_key} with sprint: {sprint_name}")
                return True
            else:
                logger.error(f"❌ Failed to update {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error updating {issue_key}: {e}")
            return False
    
    def assign_sprints_to_all_tickets(self) -> bool:
        """Assign all tickets to corporate sprints"""
        try:
            logger.info("🚀 Starting corporate sprint assignment for all tickets")
            
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
            logger.info(f"📋 Found {len(issues)} issues to assign to sprints")
            
            # Process each issue
            assigned_count = 0
            sprint_counts = {}
            
            for issue in issues:
                issue_key = issue.get("key")
                sprint_name = self.determine_sprint_for_ticket(issue)
                
                if self.update_issue_sprint(issue_key, sprint_name):
                    assigned_count += 1
                    sprint_counts[sprint_name] = sprint_counts.get(sprint_name, 0) + 1
                    self.sprint_structure[sprint_name]["tickets"].append(issue_key)
            
            logger.info(f"✅ Sprint assignment completed!")
            logger.info(f"📊 Assigned {assigned_count} tickets to sprints")
            
            # Log sprint breakdown
            logger.info("📊 Sprint Breakdown:")
            for sprint_name, count in sprint_counts.items():
                logger.info(f"  {sprint_name}: {count} tickets")
            
            # Save summary
            summary = {
                "total_tickets": len(issues),
                "assigned_tickets": assigned_count,
                "sprint_counts": sprint_counts,
                "sprint_structure": self.sprint_structure
            }
            
            with open("corporate_sprint_assignment_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Assignment summary saved to corporate_sprint_assignment_summary.json")
            logger.info(f"🎉 Corporate sprint assignment completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sprint assignment failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create sprint assigner
    assigner = CorporateSprintAssigner(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Assign sprints
    success = assigner.assign_sprints_to_all_tickets()
    
    if success:
        logger.info("🎉 All tickets assigned to corporate sprints successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Sprint assignment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
