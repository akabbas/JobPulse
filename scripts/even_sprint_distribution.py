#!/usr/bin/env python3
"""
Even Sprint Distribution for JobPulse
Distributes tickets evenly across all 12 sprints (8-9 tickets per sprint)
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

class EvenSprintDistributor:
    """Distribute tickets evenly across all 12 sprints"""
    
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
        
        # Even sprint distribution (8-9 tickets per sprint)
        self.sprint_names = [
            "Sprint 1: Critical Foundation",
            "Sprint 2: Infrastructure Hardening", 
            "Sprint 3: Data Foundation",
            "Sprint 4: Plugin Architecture Migration",
            "Sprint 5: Advanced Data Analytics",
            "Sprint 6: Enterprise Integration",
            "Sprint 7: Quality Assurance & Testing",
            "Sprint 8: User Experience & Authentication",
            "Sprint 9: API & Integration Platform",
            "Sprint 10: Monetization & Business Model",
            "Sprint 11: Advanced Analytics & AI",
            "Sprint 12: Market Expansion & Scale"
        ]
        
        self.sprint_assignments = {}
        for i, sprint_name in enumerate(self.sprint_names):
            self.sprint_assignments[sprint_name] = []
        
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
    
    def distribute_tickets_evenly(self) -> bool:
        """Distribute all tickets evenly across sprints"""
        try:
            logger.info("🚀 Starting even ticket distribution across all sprints")
            
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
            logger.info(f"📋 Found {len(issues)} issues to distribute")
            
            # Calculate tickets per sprint
            total_tickets = len(issues)
            tickets_per_sprint = total_tickets // len(self.sprint_names)
            extra_tickets = total_tickets % len(self.sprint_names)
            
            logger.info(f"📊 Distributing {total_tickets} tickets across {len(self.sprint_names)} sprints")
            logger.info(f"📊 Base: {tickets_per_sprint} tickets per sprint")
            logger.info(f"📊 Extra: {extra_tickets} sprints will get 1 additional ticket")
            
            # Process each issue
            assigned_count = 0
            sprint_index = 0
            tickets_in_current_sprint = 0
            current_sprint_limit = tickets_per_sprint + (1 if sprint_index < extra_tickets else 0)
            
            for i, issue in enumerate(issues):
                issue_key = issue.get("key")
                sprint_name = self.sprint_names[sprint_index]
                
                # Assign ticket to current sprint
                if self.assign_ticket_to_sprint(issue_key, sprint_name):
                    assigned_count += 1
                    self.sprint_assignments[sprint_name].append(issue_key)
                    tickets_in_current_sprint += 1
                    
                    # Move to next sprint if current sprint is full
                    if tickets_in_current_sprint >= current_sprint_limit:
                        sprint_index += 1
                        tickets_in_current_sprint = 0
                        if sprint_index < len(self.sprint_names):
                            current_sprint_limit = tickets_per_sprint + (1 if sprint_index < extra_tickets else 0)
            
            logger.info(f"✅ Even distribution completed!")
            logger.info(f"📊 Distributed {assigned_count} tickets")
            
            # Log sprint breakdown
            logger.info("📊 Even Sprint Distribution:")
            for sprint_name, tickets in self.sprint_assignments.items():
                logger.info(f"  {sprint_name}: {len(tickets)} tickets")
            
            # Save summary
            summary = {
                "total_tickets": total_tickets,
                "distributed_tickets": assigned_count,
                "tickets_per_sprint": tickets_per_sprint,
                "extra_tickets": extra_tickets,
                "sprint_assignments": self.sprint_assignments
            }
            
            with open("even_sprint_distribution_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Distribution summary saved to even_sprint_distribution_summary.json")
            logger.info(f"🎉 Even ticket distribution completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ticket distribution failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create distributor
    distributor = EvenSprintDistributor(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Distribute tickets
    success = distributor.distribute_tickets_evenly()
    
    if success:
        logger.info("🎉 All tickets distributed evenly across sprints successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Ticket distribution failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
