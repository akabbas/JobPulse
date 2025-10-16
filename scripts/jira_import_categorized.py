#!/usr/bin/env python3
"""
Categorized Jira Import Script for JobPulse
Handles categories, sprints, and enhanced ticket structure
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

class CategorizedJiraImporter:
    """Categorized Jira ticket importer using REST API v3"""
    
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
        self.category_mapping = {}
        
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
    
    def create_epic(self, epic_data: Dict[str, Any], project_key: str) -> str:
        """Create an epic with category information"""
        try:
            # Map priority names to IDs
            priority_map = {
                "Critical": "1",
                "High": "2", 
                "Medium": "3",
                "Low": "4",
                "Lowest": "5"
            }
            
            # Build description with category info
            description_content = [
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
            
            # Add category information
            if "category" in epic_data:
                description_content.append({
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Category: {epic_data['category']}",
                            "marks": [{"type": "strong"}]
                        }
                    ]
                })
            
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "issuetype": {"id": "10010"},  # Epic ID
                    "summary": epic_data["summary"],
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": description_content
                    },
                    "priority": {"id": priority_map.get(epic_data.get("priority", "Medium"), "3")},
                    "labels": epic_data.get("labels", [])
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
                epic_response = response.json()
                epic_key = epic_response["key"]
                epic_id = epic_response["id"]
                self.created_tickets[epic_key] = epic_id
                logger.info(f"✅ Created epic: {epic_key} - {epic_data['summary']} [{epic_data.get('category', 'No Category')}]")
                return epic_key
            else:
                logger.error(f"❌ Failed to create epic: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logger.error(f"❌ Error creating epic: {e}")
            return ""
    
    def create_task(self, task_data: Dict[str, Any], project_key: str, epic_key: str = None) -> str:
        """Create a task with category information"""
        try:
            # Map priority names to IDs
            priority_map = {
                "Critical": "1",
                "High": "2", 
                "Medium": "3",
                "Low": "4",
                "Lowest": "5"
            }
            
            # Build description with category and acceptance criteria
            description_content = [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": task_data["description"]
                        }
                    ]
                }
            ]
            
            # Add category information
            if "category" in task_data:
                description_content.append({
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Category: {task_data['category']}",
                            "marks": [{"type": "strong"}]
                        }
                    ]
                })
            
            # Add acceptance criteria if available
            if "acceptanceCriteria" in task_data and task_data["acceptanceCriteria"]:
                description_content.append({
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Acceptance Criteria:",
                            "marks": [{"type": "strong"}]
                        }
                    ]
                })
                
                for criteria in task_data["acceptanceCriteria"]:
                    description_content.append({
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": f"• {criteria}"
                            }
                        ]
                    })
            
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "issuetype": {"id": "10011"},  # Task ID
                    "summary": task_data["summary"],
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": description_content
                    },
                    "priority": {"id": priority_map.get(task_data.get("priority", "Medium"), "3")},
                    "labels": task_data.get("labels", [])
                }
            }
            
            # Add epic link if provided
            if epic_key and epic_key in self.created_tickets:
                payload["fields"]["parent"] = {"key": epic_key}
            
            response = requests.post(
                f"{self.base_url}/issue",
                auth=self.auth,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                task_response = response.json()
                task_key = task_response["key"]
                task_id = task_response["id"]
                self.created_tickets[task_key] = task_id
                logger.info(f"✅ Created task: {task_key} - {task_data['summary']} [{task_data.get('category', 'No Category')}]")
                return task_key
            else:
                logger.error(f"❌ Failed to create task: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
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
                "goal": f"Sprint {sprint_data['name']} - {sprint_data.get('storyPoints', 0)} story points"
            }
            
            if "focus" in sprint_data:
                sprint_payload["goal"] += f" - Focus: {sprint_data['focus']}"
            
            response = requests.post(
                f"{self.base_url}/sprint",
                auth=self.auth,
                headers=self.headers,
                json=sprint_payload,
                timeout=30
            )
            
            if response.status_code == 201:
                sprint_response = response.json()
                sprint_id = sprint_response["id"]
                logger.info(f"✅ Created sprint: {sprint_id} - {sprint_data['name']}")
                return sprint_id
            else:
                logger.error(f"❌ Failed to create sprint: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logger.error(f"❌ Error creating sprint: {e}")
            return ""
    
    def import_tickets(self, tickets_file: str) -> bool:
        """Import categorized tickets from JSON file"""
        try:
            with open(tickets_file, 'r') as f:
                data = json.load(f)
            
            project_key = data["project"]["key"]
            logger.info(f"🚀 Starting categorized import of tickets to project {project_key}")
            
            # Test connection
            if not self.test_connection():
                return False
            
            # Get project info
            project_info = self.get_project_info(project_key)
            if project_info:
                logger.info(f"📋 Project: {project_info.get('name', 'Unknown')}")
            
            # Create epics first
            epic_keys = {}
            for epic_data in data.get("epics", []):
                epic_key = self.create_epic(epic_data, project_key)
                if epic_key:
                    epic_keys[epic_data["summary"]] = epic_key
            
            # Create tasks
            task_count = 0
            category_counts = {}
            
            for task_data in data.get("tasks", []):
                epic_name = task_data.get("epic")
                epic_key = epic_keys.get(epic_name) if epic_name else None
                
                task_key = self.create_task(task_data, project_key, epic_key)
                if task_key:
                    task_count += 1
                    category = task_data.get("category", "Uncategorized")
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            # Create sprints
            sprint_count = 0
            for sprint_data in data.get("sprints", []):
                sprint_id = self.create_sprint(sprint_data, project_key)
                if sprint_id:
                    sprint_count += 1
            
            logger.info(f"✅ Import completed!")
            logger.info(f"📊 Created {task_count} tasks")
            logger.info(f"📋 Created {len(epic_keys)} epics")
            logger.info(f"🏃 Created {sprint_count} sprints")
            
            # Log category breakdown
            logger.info("📊 Category Breakdown:")
            for category, count in category_counts.items():
                logger.info(f"  {category}: {count} tasks")
            
            # Save summary
            summary = {
                "project": project_key,
                "epics_created": len(epic_keys),
                "tasks_created": task_count,
                "sprints_created": sprint_count,
                "epic_keys": epic_keys,
                "category_counts": category_counts,
                "created_tickets": self.created_tickets
            }
            
            with open("jira_categorized_import_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Export summary saved to jira_categorized_import_summary.json")
            logger.info(f"🎉 Categorized import completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Import failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    tickets_file = os.getenv("TICKETS_FILE", "JIRA_TICKETS_CATEGORIZED.json")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    if not os.path.exists(tickets_file):
        logger.error(f"❌ Tickets file not found: {tickets_file}")
        sys.exit(1)
    
    # Create importer
    importer = CategorizedJiraImporter(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Import tickets
    success = importer.import_tickets(tickets_file)
    
    if success:
        logger.info("🎉 All categorized tickets imported successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Import failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
