#!/usr/bin/env python3
"""
Jira Import Script for JobPulse
Automatically imports all tickets from JIRA_TICKETS.json into Jira via REST API
"""

import json
import requests
import os
import sys
from typing import Dict, List, Any
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/jira_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JiraImporter:
    """Jira ticket importer using REST API v3"""
    
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
        self.created_tickets = {}
        
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
    
    def get_project_info(self, project_key: str) -> Dict[str, Any]:
        """Get project information"""
        try:
            response = requests.get(
                f"{self.base_url}/project/{project_key}",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get project info: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error getting project info: {e}")
            return {}
    
    def get_issue_types(self) -> List[Dict[str, Any]]:
        """Get available issue types"""
        try:
            response = requests.get(
                f"{self.base_url}/issuetype",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get issue types: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting issue types: {e}")
            return []
    
    def get_priorities(self) -> List[Dict[str, Any]]:
        """Get available priorities"""
        try:
            response = requests.get(
                f"{self.base_url}/priority",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get priorities: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting priorities: {e}")
            return []
    
    def get_components(self, project_key: str) -> List[Dict[str, Any]]:
        """Get project components"""
        try:
            response = requests.get(
                f"{self.base_url}/project/{project_key}/components",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get components: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting components: {e}")
            return []
    
    def create_epic(self, epic_data: Dict[str, Any], project_key: str) -> str:
        """Create an epic ticket"""
        try:
            # Epic creation payload
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "issuetype": {"name": "Epic"},
                    "summary": epic_data["summary"],
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": epic_data["description"]
                                    }
                                ]
                            }
                        ]
                    },
                    "priority": {"name": epic_data["priority"]},
                    "labels": epic_data["labels"],
                    "components": [{"name": comp} for comp in epic_data["components"]],
                    "customfield_10014": epic_data["summary"]  # Epic Name
                }
            }
            
            response = requests.post(
                f"{self.base_url}/issue",
                auth=self.auth,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_key = issue_data["key"]
                self.created_tickets[epic_data["summary"]] = issue_key
                logger.info(f"✅ Created epic: {issue_key} - {epic_data['summary']}")
                return issue_key
            else:
                logger.error(f"❌ Failed to create epic: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error creating epic: {e}")
            return ""
    
    def create_story(self, story_data: Dict[str, Any], project_key: str, epic_key: str = None) -> str:
        """Create a story ticket"""
        try:
            # Story creation payload
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "issuetype": {"name": "Story"},
                    "summary": story_data["summary"],
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": story_data["description"]
                                    }
                                ]
                            }
                        ]
                    },
                    "priority": {"name": story_data["priority"]},
                    "labels": story_data["labels"],
                    "components": [{"name": comp} for comp in story_data["components"]],
                    "customfield_10016": story_data.get("storyPoints", 0)  # Story Points
                }
            }
            
            # Add epic link if provided
            if epic_key:
                payload["fields"]["parent"] = {"key": epic_key}
            
            response = requests.post(
                f"{self.base_url}/issue",
                auth=self.auth,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_key = issue_data["key"]
                self.created_tickets[story_data["summary"]] = issue_key
                logger.info(f"✅ Created story: {issue_key} - {story_data['summary']}")
                return issue_key
            else:
                logger.error(f"❌ Failed to create story: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error creating story: {e}")
            return ""
    
    def create_bug(self, bug_data: Dict[str, Any], project_key: str, epic_key: str = None) -> str:
        """Create a bug ticket"""
        try:
            # Bug creation payload
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "issuetype": {"name": "Bug"},
                    "summary": bug_data["summary"],
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": bug_data["description"]
                                    }
                                ]
                            }
                        ]
                    },
                    "priority": {"name": bug_data["priority"]},
                    "labels": bug_data["labels"],
                    "components": [{"name": comp} for comp in bug_data["components"]]
                }
            }
            
            # Add epic link if provided
            if epic_key:
                payload["fields"]["parent"] = {"key": epic_key}
            
            response = requests.post(
                f"{self.base_url}/issue",
                auth=self.auth,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_key = issue_data["key"]
                self.created_tickets[bug_data["summary"]] = issue_key
                logger.info(f"✅ Created bug: {issue_key} - {bug_data['summary']}")
                return issue_key
            else:
                logger.error(f"❌ Failed to create bug: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error creating bug: {e}")
            return ""
    
    def create_sprint(self, sprint_data: Dict[str, Any], project_key: str) -> str:
        """Create a sprint"""
        try:
            # Get board ID first
            board_response = requests.get(
                f"{self.base_url}/board",
                auth=self.auth,
                headers=self.headers,
                params={"projectKeyOrId": project_key},
                timeout=30
            )
            
            if board_response.status_code != 200:
                logger.error(f"❌ Failed to get board: {board_response.status_code} - {board_response.text}")
                return ""
            
            boards = board_response.json().get("values", [])
            if not boards:
                logger.error("❌ No boards found for project")
                return ""
            
            board_id = boards[0]["id"]
            
            # Create sprint
            sprint_payload = {
                "name": sprint_data["name"],
                "originBoardId": board_id,
                "goal": f"Sprint {sprint_data['name']} - {sprint_data['storyPoints']} story points"
            }
            
            response = requests.post(
                f"{self.base_url}/sprint",
                auth=self.auth,
                headers=self.headers,
                json=sprint_payload,
                timeout=30
            )
            
            if response.status_code == 201:
                sprint_data = response.json()
                sprint_id = sprint_data["id"]
                logger.info(f"✅ Created sprint: {sprint_id} - {sprint_data['name']}")
                return sprint_id
            else:
                logger.error(f"❌ Failed to create sprint: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error creating sprint: {e}")
            return ""
    
    def import_tickets(self, tickets_file: str) -> bool:
        """Import all tickets from JSON file"""
        try:
            # Load tickets data
            with open(tickets_file, 'r') as f:
                data = json.load(f)
            
            project_key = data["project_key"]
            tickets = data["tickets"]
            sprints = data.get("sprints", [])
            
            logger.info(f"🚀 Starting import of {len(tickets)} tickets to project {project_key}")
            
            # Test connection
            if not self.test_connection():
                return False
            
            # Get project info
            project_info = self.get_project_info(project_key)
            if not project_info:
                logger.error(f"❌ Project {project_key} not found")
                return False
            
            logger.info(f"📋 Project: {project_info.get('name', 'Unknown')}")
            
            # Create epics first
            epics = [t for t in tickets if t["issueType"] == "Epic"]
            epic_keys = {}
            
            for epic in epics:
                epic_key = self.create_epic(epic, project_key)
                if epic_key:
                    epic_keys[epic["summary"]] = epic_key
            
            # Create sprints
            sprint_ids = {}
            for sprint in sprints:
                sprint_id = self.create_sprint(sprint, project_key)
                if sprint_id:
                    sprint_ids[sprint["name"]] = sprint_id
            
            # Create stories and bugs
            stories = [t for t in tickets if t["issueType"] in ["Story", "Bug"]]
            
            for story in stories:
                epic_key = None
                if "epicLink" in story:
                    epic_key = epic_keys.get(story["epicLink"])
                
                if story["issueType"] == "Story":
                    self.create_story(story, project_key, epic_key)
                elif story["issueType"] == "Bug":
                    self.create_bug(story, project_key, epic_key)
            
            # Summary
            logger.info(f"✅ Import completed!")
            logger.info(f"📊 Created {len(self.created_tickets)} tickets")
            logger.info(f"📋 Created {len(epic_keys)} epics")
            logger.info(f"🏃 Created {len(sprint_ids)} sprints")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Import failed: {e}")
            return False
    
    def export_summary(self, output_file: str):
        """Export import summary"""
        try:
            summary = {
                "import_timestamp": datetime.now().isoformat(),
                "created_tickets": self.created_tickets,
                "total_tickets": len(self.created_tickets)
            }
            
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Export summary saved to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to export summary: {e}")

def main():
    """Main function"""
    # Get configuration from environment variables
    jira_site = os.getenv("JIRA_SITE", "ammrabbasher.atlassian.net")
    api_token = os.getenv("JIRA_API_TOKEN")
    tickets_file = os.getenv("TICKETS_FILE", "JIRA_TICKETS.json")
    
    if not api_token:
        logger.error("❌ JIRA_API_TOKEN environment variable not set")
        logger.error("Please set your Jira API token: export JIRA_API_TOKEN='your_token_here'")
        sys.exit(1)
    
    if not os.path.exists(tickets_file):
        logger.error(f"❌ Tickets file not found: {tickets_file}")
        sys.exit(1)
    
    # Create importer
    importer = JiraImporter(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Import tickets
    success = importer.import_tickets(tickets_file)
    
    if success:
        # Export summary
        importer.export_summary("jira_import_summary.json")
        logger.info("🎉 Import completed successfully!")
    else:
        logger.error("❌ Import failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
