#!/usr/bin/env python3
"""
Rebalance Sprint Assignments for JobPulse
Redistributes tickets more evenly across all 12 sprints
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

class SprintRebalancer:
    """Rebalance tickets across all 12 corporate sprints"""
    
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
        
        # Balanced sprint structure
        self.balanced_sprints = {
            "Sprint 1: Critical Foundation": {
                "story_points": 40,
                "team_size": 3,
                "risk_level": "Low",
                "focus": "Emergency fixes and system stability",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 2: Infrastructure Hardening": {
                "story_points": 42,
                "team_size": 4,
                "risk_level": "Low",
                "focus": "System reliability and performance",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 3: Data Foundation": {
                "story_points": 38,
                "team_size": 4,
                "risk_level": "Medium",
                "focus": "Core data infrastructure",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 4: Plugin Architecture Migration": {
                "story_points": 45,
                "team_size": 5,
                "risk_level": "High",
                "focus": "System architecture modernization",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 5: Advanced Data Analytics": {
                "story_points": 40,
                "team_size": 4,
                "risk_level": "Medium",
                "focus": "AI and analytics capabilities",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 6: Enterprise Integration": {
                "story_points": 43,
                "team_size": 5,
                "risk_level": "High",
                "focus": "Enterprise-grade features",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 7: Quality Assurance & Testing": {
                "story_points": 35,
                "team_size": 3,
                "risk_level": "Low",
                "focus": "Quality and reliability",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 8: User Experience & Authentication": {
                "story_points": 38,
                "team_size": 4,
                "risk_level": "Medium",
                "focus": "User-facing features",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 9: API & Integration Platform": {
                "story_points": 42,
                "team_size": 4,
                "risk_level": "Medium",
                "focus": "API development and integrations",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 10: Monetization & Business Model": {
                "story_points": 36,
                "team_size": 3,
                "risk_level": "Medium",
                "focus": "Revenue generation",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 11: Advanced Analytics & AI": {
                "story_points": 44,
                "team_size": 5,
                "risk_level": "High",
                "focus": "Cutting-edge AI features",
                "max_tickets": 8,
                "tickets": []
            },
            "Sprint 12: Market Expansion & Scale": {
                "story_points": 40,
                "team_size": 4,
                "risk_level": "High",
                "focus": "Business growth and scaling",
                "max_tickets": 8,
                "tickets": []
            }
        }
        
        # Ticket priority mapping
        self.priority_mapping = {
            "critical": ["Sprint 1: Critical Foundation"],
            "high": ["Sprint 2: Infrastructure Hardening", "Sprint 3: Data Foundation"],
            "medium": ["Sprint 4: Plugin Architecture Migration", "Sprint 5: Advanced Data Analytics", "Sprint 6: Enterprise Integration"],
            "low": ["Sprint 7: Quality Assurance & Testing", "Sprint 8: User Experience & Authentication", "Sprint 9: API & Integration Platform"],
            "future": ["Sprint 10: Monetization & Business Model", "Sprint 11: Advanced Analytics & AI", "Sprint 12: Market Expansion & Scale"]
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
    
    def determine_priority_for_ticket(self, issue_data: Dict[str, Any]) -> str:
        """Determine ticket priority based on content"""
        try:
            summary = issue_data.get("fields", {}).get("summary", "").lower()
            labels = issue_data.get("fields", {}).get("labels", [])
            
            # Check for critical keywords
            if any(keyword in summary for keyword in ["fix", "broken", "critical", "urgent", "emergency"]):
                return "critical"
            elif any(keyword in summary for keyword in ["infrastructure", "performance", "monitoring", "security"]):
                return "high"
            elif any(keyword in summary for keyword in ["snowflake", "data", "analytics", "ai"]):
                return "medium"
            elif any(keyword in summary for keyword in ["user", "auth", "api", "integration"]):
                return "low"
            elif any(keyword in summary for keyword in ["premium", "monetization", "revenue", "market"]):
                return "future"
            else:
                return "medium"  # Default to medium priority
                
        except Exception as e:
            logger.error(f"❌ Error determining priority: {e}")
            return "medium"
    
    def assign_ticket_to_sprint(self, issue_key: str, sprint_name: str) -> bool:
        """Assign ticket to specific sprint"""
        try:
            # Get current labels
            issue_data = self.get_issue(issue_key)
            current_labels = issue_data.get("fields", {}).get("labels", [])
            
            # Remove old sprint labels
            sprint_labels_to_remove = []
            for label in current_labels:
                if label.startswith("sprint-") or "sprint" in label.lower():
                    sprint_labels_to_remove.append(label)
            
            # Add new sprint label
            sprint_label = sprint_name.lower().replace(" ", "-").replace(":", "")
            new_labels = [label for label in current_labels if label not in sprint_labels_to_remove]
            new_labels.append(sprint_label)
            
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
                logger.info(f"✅ Assigned {issue_key} to {sprint_name}")
                return True
            else:
                logger.error(f"❌ Failed to assign {issue_key}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error assigning {issue_key}: {e}")
            return False
    
    def rebalance_all_tickets(self) -> bool:
        """Rebalance all tickets across sprints"""
        try:
            logger.info("🚀 Starting sprint rebalancing for all tickets")
            
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
            logger.info(f"📋 Found {len(issues)} issues to rebalance")
            
            # Process each issue
            assigned_count = 0
            sprint_counts = {}
            
            for i, issue in enumerate(issues):
                issue_key = issue.get("key")
                priority = self.determine_priority_for_ticket(issue)
                
                # Get available sprints for this priority
                available_sprints = self.priority_mapping.get(priority, ["Sprint 7: Quality Assurance & Testing"])
                
                # Find a sprint with available capacity
                assigned_sprint = None
                for sprint_name in available_sprints:
                    if len(self.balanced_sprints[sprint_name]["tickets"]) < self.balanced_sprints[sprint_name]["max_tickets"]:
                        assigned_sprint = sprint_name
                        break
                
                # If no sprint available, assign to the first one
                if not assigned_sprint:
                    assigned_sprint = available_sprints[0]
                
                # Assign ticket to sprint
                if self.assign_ticket_to_sprint(issue_key, assigned_sprint):
                    assigned_count += 1
                    sprint_counts[assigned_sprint] = sprint_counts.get(assigned_sprint, 0) + 1
                    self.balanced_sprints[assigned_sprint]["tickets"].append(issue_key)
            
            logger.info(f"✅ Sprint rebalancing completed!")
            logger.info(f"📊 Rebalanced {assigned_count} tickets")
            
            # Log sprint breakdown
            logger.info("📊 Balanced Sprint Breakdown:")
            for sprint_name, count in sprint_counts.items():
                logger.info(f"  {sprint_name}: {count} tickets")
            
            # Save summary
            summary = {
                "total_tickets": len(issues),
                "rebalanced_tickets": assigned_count,
                "sprint_counts": sprint_counts,
                "balanced_sprint_structure": self.balanced_sprints
            }
            
            with open("balanced_sprint_assignment_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Rebalancing summary saved to balanced_sprint_assignment_summary.json")
            logger.info(f"🎉 Sprint rebalancing completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sprint rebalancing failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create sprint rebalancer
    rebalancer = SprintRebalancer(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Rebalance sprints
    success = rebalancer.rebalance_all_tickets()
    
    if success:
        logger.info("🎉 All tickets rebalanced across sprints successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Sprint rebalancing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
