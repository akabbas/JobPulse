#!/usr/bin/env python3
"""
Remove Duplicate Jira Tickets
Identifies and removes duplicate tickets from the Jira backlog
"""

import json
import logging
import os
import sys
import requests
from typing import Dict, List, Any, Set, Tuple
import re
from datetime import datetime
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DuplicateTicketRemover:
    """Remove duplicate tickets from Jira backlog"""
    
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
        
        # Known duplicate patterns
        self.duplicate_patterns = {
            "snowflake_integration": [
                "Snowflake Enterprise Integration",
                "Integrate Snowflake",
                "Snowflake Manager",
                "Snowflake Data"
            ],
            "plugin_architecture": [
                "Plugin Architecture Migration",
                "Migrate Core Scrapers",
                "BaseScraper",
                "ScraperManager"
            ],
            "production_stability": [
                "Production Stability",
                "Monitoring",
                "Health Check",
                "Site Reliability"
            ],
            "database_infrastructure": [
                "Database & Infrastructure",
                "Database Managers",
                "Database Migration",
                "Unify Database"
            ],
            "testing_quality": [
                "Testing & Quality Assurance",
                "Unit Tests",
                "Integration Test",
                "Quality Assurance"
            ],
            "documentation": [
                "Documentation",
                "API Documentation",
                "Technical Documentation",
                "Architecture Decision"
            ],
            "recruiter_api": [
                "Recruiter API Access",
                "Recruiter API"
            ]
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
    
    def get_all_issues(self) -> List[Dict[str, Any]]:
        """Get all issues from Jira"""
        try:
            issues = []
            start_at = 0
            max_results = 50
            
            while True:
                response = requests.get(
                    f"{self.base_url}/search/jql",
                    auth=self.auth,
                    headers=self.headers,
                    params={
                        "jql": "project = JB ORDER BY created ASC",
                        "fields": "summary,description,issuetype,status,labels,created",
                        "startAt": start_at,
                        "maxResults": max_results
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Failed to get issues: {response.status_code} - {response.text}")
                    return []
                
                data = response.json()
                issues.extend(data.get('issues', []))
                
                if len(issues) >= data.get('total', 0):
                    break
                start_at += max_results
            
            logger.info(f"📋 Retrieved {len(issues)} issues")
            return issues
            
        except Exception as e:
            logger.error(f"❌ Error getting issues: {e}")
            return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        try:
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        except Exception:
            return 0.0
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s]', '', str(text).lower())
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def find_duplicate_groups(self, issues: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Find groups of duplicate tickets"""
        try:
            duplicate_groups = []
            processed_issues = set()
            
            for i, issue1 in enumerate(issues):
                if i in processed_issues:
                    continue
                
                issue1_key = issue1.get('key')
                issue1_summary = issue1.get('fields', {}).get('summary', '')
                issue1_normalized = self.normalize_text(issue1_summary)
                
                if not issue1_normalized:
                    continue
                
                current_group = [issue1]
                processed_issues.add(i)
                
                # Check against remaining issues
                for j, issue2 in enumerate(issues[i+1:], i+1):
                    if j in processed_issues:
                        continue
                    
                    issue2_key = issue2.get('key')
                    issue2_summary = issue2.get('fields', {}).get('summary', '')
                    issue2_normalized = self.normalize_text(issue2_summary)
                    
                    if not issue2_normalized:
                        continue
                    
                    # Calculate similarity
                    similarity = self.calculate_similarity(issue1_normalized, issue2_normalized)
                    
                    # Check for pattern-based duplicates
                    pattern_match = self.check_pattern_duplicates(issue1_summary, issue2_summary)
                    
                    # Consider duplicates if similarity > 0.8 or pattern match
                    if similarity > 0.8 or pattern_match:
                        current_group.append(issue2)
                        processed_issues.add(j)
                        logger.info(f"🔍 Found potential duplicate: {issue1_key} <-> {issue2_key} (similarity: {similarity:.2f})")
                
                # Only add groups with more than one ticket
                if len(current_group) > 1:
                    duplicate_groups.append(current_group)
                    logger.info(f"📋 Duplicate group found with {len(current_group)} tickets")
            
            return duplicate_groups
            
        except Exception as e:
            logger.error(f"❌ Error finding duplicate groups: {e}")
            return []
    
    def check_pattern_duplicates(self, summary1: str, summary2: str) -> bool:
        """Check if tickets match known duplicate patterns"""
        try:
            summary1_lower = summary1.lower()
            summary2_lower = summary2.lower()
            
            for pattern_name, patterns in self.duplicate_patterns.items():
                match1 = any(pattern.lower() in summary1_lower for pattern in patterns)
                match2 = any(pattern.lower() in summary2_lower for pattern in patterns)
                
                if match1 and match2:
                    logger.info(f"🎯 Pattern match found: {pattern_name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking pattern duplicates: {e}")
            return False
    
    def select_keep_ticket(self, duplicate_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select which ticket to keep from duplicate group"""
        try:
            if len(duplicate_group) <= 1:
                return duplicate_group[0] if duplicate_group else None
            
            # Scoring criteria
            best_ticket = None
            best_score = -1
            
            for ticket in duplicate_group:
                score = 0
                fields = ticket.get('fields', {})
                
                # Prefer tickets with more complete information
                if fields.get('description'):
                    score += 2
                
                # Prefer tickets with labels
                if fields.get('labels'):
                    score += 1
                
                # Prefer tickets with specific status
                status = fields.get('status', {}).get('name', '').lower()
                if status in ['in progress', 'done', 'closed']:
                    score += 3
                elif status in ['to do', 'open']:
                    score += 1
                
                # Prefer tickets with more detailed summaries
                summary = fields.get('summary', '')
                if len(summary) > 50:
                    score += 1
                
                # Prefer tickets created earlier (original)
                created = fields.get('created', '')
                if created:
                    score += 1
                
                if score > best_score:
                    best_score = score
                    best_ticket = ticket
            
            return best_ticket or duplicate_group[0]
            
        except Exception as e:
            logger.error(f"❌ Error selecting keep ticket: {e}")
            return duplicate_group[0] if duplicate_group else None
    
    def delete_ticket(self, issue_key: str) -> bool:
        """Delete a ticket from Jira"""
        try:
            # First, try to transition to "Done" status
            transition_response = requests.post(
                f"{self.base_url}/issue/{issue_key}/transitions",
                auth=self.auth,
                headers=self.headers,
                json={
                    "transition": {
                        "name": "Done"
                    }
                },
                timeout=30
            )
            
            if transition_response.status_code == 204:
                logger.info(f"✅ Transitioned {issue_key} to Done status")
            else:
                logger.warning(f"⚠️ Could not transition {issue_key} to Done: {transition_response.status_code}")
            
            # Note: Jira doesn't allow direct deletion of issues via API
            # Instead, we'll mark them as duplicates and suggest manual deletion
            logger.info(f"📝 Ticket {issue_key} marked for deletion (manual action required)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting ticket {issue_key}: {e}")
            return False
    
    def update_duplicate_ticket(self, issue_key: str, original_ticket_key: str) -> bool:
        """Update duplicate ticket with reference to original"""
        try:
            payload = {
                "fields": {
                    "summary": f"DUPLICATE - {issue_key} (Original: {original_ticket_key})",
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"❌ DUPLICATE TICKET - This ticket is a duplicate of {original_ticket_key} and should be deleted."
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
                logger.info(f"✅ Updated duplicate ticket {issue_key}")
                return True
            else:
                logger.error(f"❌ Failed to update {issue_key}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating duplicate ticket {issue_key}: {e}")
            return False
    
    def remove_duplicates(self) -> bool:
        """Remove duplicate tickets from Jira"""
        try:
            logger.info("🚀 Starting duplicate ticket removal")
            
            # Test connection
            if not self.test_connection():
                return False
            
            # Get all issues
            issues = self.get_all_issues()
            if not issues:
                logger.warning("No issues found to analyze")
                return False
            
            # Find duplicate groups
            duplicate_groups = self.find_duplicate_groups(issues)
            
            if not duplicate_groups:
                logger.info("✅ No duplicate tickets found")
                return True
            
            logger.info(f"🔍 Found {len(duplicate_groups)} duplicate groups")
            
            # Process each duplicate group
            removal_results = []
            total_duplicates = 0
            
            for group in duplicate_groups:
                logger.info(f"📋 Processing duplicate group with {len(group)} tickets")
                
                # Select ticket to keep
                keep_ticket = self.select_keep_ticket(group)
                if not keep_ticket:
                    continue
                
                keep_key = keep_ticket.get('key')
                logger.info(f"✅ Keeping ticket: {keep_key}")
                
                # Mark others as duplicates
                for ticket in group:
                    ticket_key = ticket.get('key')
                    if ticket_key == keep_key:
                        continue
                    
                    logger.info(f"🗑️ Marking as duplicate: {ticket_key}")
                    
                    # Update duplicate ticket
                    if self.update_duplicate_ticket(ticket_key, keep_key):
                        total_duplicates += 1
                        removal_results.append({
                            "duplicate_key": ticket_key,
                            "original_key": keep_key,
                            "status": "marked_duplicate"
                        })
                    else:
                        removal_results.append({
                            "duplicate_key": ticket_key,
                            "original_key": keep_key,
                            "status": "failed"
                        })
            
            # Log results
            logger.info(f"🎉 Duplicate removal completed!")
            logger.info(f"📊 Processed {len(duplicate_groups)} duplicate groups")
            logger.info(f"📊 Marked {total_duplicates} tickets as duplicates")
            
            # Save results
            results = {
                "total_duplicate_groups": len(duplicate_groups),
                "total_duplicates_marked": total_duplicates,
                "removal_results": removal_results,
                "removal_timestamp": datetime.now().isoformat()
            }
            
            with open("duplicate_removal_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info("📄 Results saved to duplicate_removal_results.json")
            logger.info("🎉 Duplicate ticket removal completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Duplicate removal failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create duplicate remover
    remover = DuplicateTicketRemover(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Remove duplicates
    success = remover.remove_duplicates()
    
    if success:
        logger.info("🎉 Duplicate ticket removal completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Duplicate ticket removal failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
