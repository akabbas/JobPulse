#!/usr/bin/env python3
"""
Create Problem-Focused Categories for JobPulse
Creates precise categories based on the actual problems JobPulse solves and its architecture
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

class ProblemFocusedCategoryCreator:
    """Create problem-focused categories for JobPulse"""
    
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
        
        # Problem-focused categories based on JobPulse architecture
        self.problem_categories = {
            "🚫 Anti-Bot Detection & Bypass": {
                "description": "Solving 403 errors, IP blocks, and anti-bot measures",
                "keywords": ["403", "blocked", "anti-bot", "stealth", "playwright", "user-agent", "proxy", "rotation", "bypass", "detection"],
                "problems_solved": [
                    "Job scrapers breaking after few requests",
                    "403 errors and IP blocks",
                    "Anti-bot detection bypass",
                    "Stealth scraping capabilities"
                ],
                "tickets": []
            },
            "🔌 Multi-Source Data Collection": {
                "description": "Aggregating jobs from 20+ sources for comprehensive coverage",
                "keywords": ["scraper", "source", "indeed", "linkedin", "dice", "stackoverflow", "greenhouse", "lever", "collection", "aggregation", "multi-source"],
                "problems_solved": [
                    "Limited job coverage from single sources",
                    "Manual job searching across multiple sites",
                    "Inconsistent data formats",
                    "Missing job opportunities"
                ],
                "tickets": []
            },
            "🤖 AI-Powered Job Analysis": {
                "description": "Using GPT-5 and AI for intelligent job matching and insights",
                "keywords": ["ai", "gpt", "analysis", "matching", "intelligence", "insights", "recommendation", "skills", "resume", "cortex"],
                "problems_solved": [
                    "No real insights from job data",
                    "Manual job matching and analysis",
                    "Lack of personalized recommendations",
                    "Missing skill gap analysis"
                ],
                "tickets": []
            },
            "🏗️ Production Infrastructure": {
                "description": "Building reliable, scalable, production-ready systems",
                "keywords": ["production", "deployment", "docker", "kubernetes", "railway", "postgresql", "infrastructure", "scalability", "reliability"],
                "problems_solved": [
                    "Unreliable deployment and hosting",
                    "System failures in production",
                    "Scalability issues",
                    "Poor performance and downtime"
                ],
                "tickets": []
            },
            "📊 Data Analytics & Insights": {
                "description": "Transforming raw job data into actionable business intelligence",
                "keywords": ["analytics", "insights", "trends", "snowflake", "data", "warehouse", "reporting", "dashboard", "metrics", "intelligence"],
                "problems_solved": [
                    "Raw data dumps with no analysis",
                    "No market trend insights",
                    "Missing business intelligence",
                    "Lack of data-driven decisions"
                ],
                "tickets": []
            },
            "🔧 Plugin Architecture & Extensibility": {
                "description": "Modern, maintainable architecture for easy scraper management",
                "keywords": ["plugin", "architecture", "extensibility", "maintainability", "base-scraper", "manager", "modular", "scalable"],
                "problems_solved": [
                    "Difficult to maintain and extend scrapers",
                    "Inconsistent error handling",
                    "Hard to add new data sources",
                    "Poor code organization"
                ],
                "tickets": []
            },
            "⚡ Performance & Optimization": {
                "description": "Optimizing speed, efficiency, and resource usage",
                "keywords": ["performance", "optimization", "speed", "caching", "redis", "concurrent", "parallel", "efficiency", "memory", "cpu"],
                "problems_solved": [
                    "Slow job scraping and processing",
                    "High resource usage",
                    "Poor user experience",
                    "Inefficient data processing"
                ],
                "tickets": []
            },
            "🛡️ Error Handling & Reliability": {
                "description": "Building robust systems that handle failures gracefully",
                "keywords": ["error", "handling", "reliability", "robust", "failure", "retry", "fallback", "graceful", "resilient"],
                "problems_solved": [
                    "System crashes and failures",
                    "Poor error handling",
                    "Data loss during failures",
                    "Unreliable user experience"
                ],
                "tickets": []
            },
            "👤 User Experience & Interface": {
                "description": "Creating intuitive interfaces for job search and analysis",
                "keywords": ["ui", "ux", "interface", "dashboard", "user", "experience", "frontend", "web", "design", "usability"],
                "problems_solved": [
                    "Poor user interfaces",
                    "Difficult job searching experience",
                    "Lack of user-friendly dashboards",
                    "Complex navigation and workflows"
                ],
                "tickets": []
            },
            "🧪 Testing & Quality Assurance": {
                "description": "Ensuring code quality, reliability, and maintainability",
                "keywords": ["test", "testing", "quality", "qa", "coverage", "validation", "reliability", "maintainability", "debugging"],
                "problems_solved": [
                    "Untested code causing failures",
                    "Poor code quality",
                    "Difficult debugging and maintenance",
                    "Unreliable system behavior"
                ],
                "tickets": []
            },
            "📚 Documentation & Knowledge": {
                "description": "Creating comprehensive documentation and knowledge management",
                "keywords": ["documentation", "doc", "knowledge", "guide", "manual", "tutorial", "readme", "wiki", "help"],
                "problems_solved": [
                    "Lack of documentation",
                    "Difficult onboarding for new developers",
                    "Missing user guides",
                    "Poor knowledge management"
                ],
                "tickets": []
            },
            "💰 Business & Monetization": {
                "description": "Building revenue-generating features and business models",
                "keywords": ["business", "revenue", "monetization", "premium", "subscription", "billing", "marketplace", "enterprise", "commercial"],
                "problems_solved": [
                    "No revenue generation",
                    "Lack of business model",
                    "Missing enterprise features",
                    "No monetization strategy"
                ],
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
    
    def analyze_ticket_for_problem_category(self, issue_data: Dict[str, Any]) -> str:
        """Analyze ticket to determine which problem it solves"""
        try:
            full_text = self.extract_text_content(issue_data)
            
            # Score each problem category
            category_scores = {}
            for category_name, category_data in self.problem_categories.items():
                score = 0
                keywords = category_data["keywords"]
                
                # Count keyword matches
                for keyword in keywords:
                    if keyword.lower() in full_text:
                        score += 1
                
                # Bonus points for exact problem matches
                problems_solved = category_data["problems_solved"]
                for problem in problems_solved:
                    problem_words = problem.lower().split()
                    for word in problem_words:
                        if word in full_text:
                            score += 2
                
                category_scores[category_name] = score
            
            # Find the category with highest score
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                if category_scores[best_category] > 0:
                    return best_category
            
            # Default to general development if no clear match
            return "🛠️ General Development"
            
        except Exception as e:
            logger.error(f"❌ Error analyzing ticket: {e}")
            return "🛠️ General Development"
    
    def apply_problem_category_to_ticket(self, issue_key: str, category_name: str) -> bool:
        """Apply problem-focused category to a specific ticket"""
        try:
            # Get current labels
            issue_data = self.get_issue(issue_key)
            current_labels = issue_data.get("fields", {}).get("labels", [])
            
            # Remove old category labels
            old_category_labels = [
                "critical-urgent", "complex-technical", "data-analytics", 
                "ai-machine-learning", "business-revenue", "infrastructure-ops",
                "user-experience", "quality-testing", "documentation-knowledge",
                "general-development", "anti-bot-detection", "multi-source-data",
                "ai-powered-analysis", "production-infrastructure", "data-analytics-insights",
                "plugin-architecture", "performance-optimization", "error-handling-reliability"
            ]
            
            # Clean category name for label
            clean_category = category_name.lower()
            clean_category = clean_category.replace("🚫", "").replace("🔌", "").replace("🤖", "")
            clean_category = clean_category.replace("🏗️", "").replace("📊", "").replace("🔧", "")
            clean_category = clean_category.replace("⚡", "").replace("🛡️", "").replace("👤", "")
            clean_category = clean_category.replace("🧪", "").replace("📚", "").replace("💰", "").replace("🛠️", "")
            clean_category = clean_category.replace(" ", "-").replace("&", "and")
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
            
            response = requests.put(
                f"{self.base_url}/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Applied '{category_name}' to {issue_key}")
                return True
            else:
                logger.error(f"❌ Failed to apply category to {issue_key}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error applying category to {issue_key}: {e}")
            return False
    
    def apply_problem_focused_categories(self) -> bool:
        """Apply problem-focused categories to all tickets"""
        try:
            logger.info("🚀 Starting problem-focused category application")
            
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
            
            # Analyze and categorize each ticket
            total_applied = 0
            category_stats = {}
            
            for issue in issues:
                issue_key = issue.get("key")
                category = self.analyze_ticket_for_problem_category(issue)
                
                if self.apply_problem_category_to_ticket(issue_key, category):
                    total_applied += 1
                    category_stats[category] = category_stats.get(category, 0) + 1
                    self.problem_categories[category]["tickets"].append(issue_key)
            
            # Log results
            logger.info(f"🎉 Problem-focused categorization completed!")
            logger.info(f"📊 Total categories applied: {len(category_stats)}")
            logger.info(f"📊 Total tickets updated: {total_applied}")
            
            # Log category breakdown
            logger.info("📊 Problem-Focused Category Distribution:")
            for category_name, count in category_stats.items():
                problems = self.problem_categories[category_name]["problems_solved"]
                logger.info(f"  📁 {category_name}: {count} tickets")
                logger.info(f"    🎯 Problems solved: {', '.join(problems[:2])}...")
            
            # Save results
            results = {
                "total_tickets": len(issues),
                "categorized_tickets": total_applied,
                "category_stats": category_stats,
                "problem_categories": self.problem_categories,
                "application_timestamp": "2025-10-16T14:40:00Z"
            }
            
            with open("problem_focused_categories_summary.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info("📄 Results saved to problem_focused_categories_summary.json")
            logger.info("🎉 Problem-focused categorization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Problem-focused categorization failed: {e}")
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
    categorizer = ProblemFocusedCategoryCreator(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Apply problem-focused categories
    success = categorizer.apply_problem_focused_categories()
    
    if success:
        logger.info("🎉 All problem-focused categories applied successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Problem-focused categorization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
