#!/usr/bin/env python3
"""
Match Jira Tickets to Code Snippets and Features
Analyzes the JobPulse codebase and matches Jira tickets to actual code components
"""

import json
import logging
import os
import sys
import requests
from typing import Dict, List, Any
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeTicketMatcher:
    """Match Jira tickets to actual code components and features"""
    
    def __init__(self, jira_site: str, api_token: str, email: str = None):
        self.jira_site = jira_site
        self.api_token = api_token
        self.email = email or "ammrabbasher@gmail.com"
        self.base_url = f"https://{jira_site}/rest/api/3"
        self.auth = (email, api_token)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Code component mappings
        self.code_components = {
            "scrapers": {
                "indeed": "scrapers/indeed_scraper.py",
                "linkedin": "scrapers/linkedin_scraper.py", 
                "stackoverflow": "scrapers/stackoverflow_scraper.py",
                "dice": "scrapers/dice_scraper.py",
                "remoteok": "scrapers/remoteok_scraper.py",
                "weworkremotely": "scrapers/weworkremotely_scraper.py",
                "reddit": "scrapers/reddit_scraper.py",
                "playwright": "scrapers/enhanced_playwright_scraper.py",
                "api_sources": "scrapers/api_sources_scraper.py",
                "lever": "scrapers/lever_scraper.py",
                "greenhouse": "scrapers/greenhouse_scraper.py",
                "google_jobs": "scrapers/google_jobs_scraper.py",
                "otta": "scrapers/otta_scraper.py",
                "hackernews": "scrapers/hackernews_scraper.py",
                "yc_jobs": "scrapers/yc_jobs_scraper.py",
                "authentic_jobs": "scrapers/authentic_jobs_scraper.py",
                "jobspresso": "scrapers/jobspresso_scraper.py",
                "himalayas": "scrapers/himalayas_scraper.py"
            },
            "ai_services": {
                "ai_analyzer": "ai_services/ai_analyzer.py",
                "ai_matcher": "ai_services/ai_matcher.py", 
                "ai_resume_generator": "ai_services/ai_resume_generator.py"
            },
            "database": {
                "snowflake_manager": "database/snowflake_manager.py",
                "db_manager": "database/db_manager.py"
            },
            "web_dashboard": {
                "main_app": "web_dashboard/app.py",
                "models": "web_dashboard/models.py"
            },
            "data_processing": {
                "data_cleaner": "data_processing/data_cleaner.py"
            },
            "analysis": {
                "skill_trends": "analysis/skill_trends.py"
            },
            "config": {
                "settings": "config/settings.py",
                "production": "config/production.py"
            }
        }
        
        # Feature mappings based on keywords
        self.feature_keywords = {
            "snowflake": ["snowflake", "data warehouse", "analytics", "enterprise"],
            "ai": ["ai", "gpt", "machine learning", "artificial intelligence", "analysis"],
            "scraping": ["scraper", "scraping", "data collection", "web scraping"],
            "api": ["api", "rest", "endpoint", "integration"],
            "database": ["database", "postgresql", "sqlite", "data storage"],
            "authentication": ["auth", "login", "user", "security"],
            "monitoring": ["monitoring", "health check", "prometheus", "metrics"],
            "deployment": ["deployment", "docker", "kubernetes", "railway", "heroku"],
            "ui": ["ui", "interface", "dashboard", "frontend", "user experience"],
            "testing": ["test", "testing", "quality", "validation"]
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
    
    def get_all_tickets(self) -> List[Dict[str, Any]]:
        """Get all Jira tickets"""
        try:
            response = requests.get(
                f"{self.base_url}/search/jql",
                auth=self.auth,
                headers=self.headers,
                params={
                    "jql": "project = JB ORDER BY created ASC",
                    "fields": "summary,description,labels",
                    "maxResults": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("issues", [])
            else:
                logger.error(f"❌ Failed to get tickets: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting tickets: {e}")
            return []
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the codebase to identify components and features"""
        codebase_analysis = {
            "components": {},
            "features": {},
            "file_sizes": {},
            "code_snippets": {}
        }
        
        # Analyze each component category
        for category, components in self.code_components.items():
            codebase_analysis["components"][category] = {}
            
            for component_name, file_path in components.items():
                full_path = Path(file_path)
                if full_path.exists():
                    # Get file size and basic info
                    file_size = full_path.stat().st_size
                    codebase_analysis["file_sizes"][file_path] = file_size
                    
                    # Read file content for analysis
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract key features from code
                        features = self.extract_features_from_code(content, component_name)
                        codebase_analysis["components"][category][component_name] = {
                            "file_path": file_path,
                            "size": file_size,
                            "features": features,
                            "code_snippet": content[:500] + "..." if len(content) > 500 else content
                        }
                        
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
                        codebase_analysis["components"][category][component_name] = {
                            "file_path": file_path,
                            "size": file_size,
                            "features": [],
                            "code_snippet": "File could not be read"
                        }
                else:
                    logger.warning(f"File not found: {file_path}")
        
        return codebase_analysis
    
    def extract_features_from_code(self, content: str, component_name: str) -> List[str]:
        """Extract features from code content"""
        features = []
        
        # Check for specific patterns
        if "class" in content.lower():
            features.append("Object-oriented design")
        if "async" in content or "await" in content:
            features.append("Asynchronous processing")
        if "requests" in content:
            features.append("HTTP requests")
        if "beautifulsoup" in content or "bs4" in content:
            features.append("HTML parsing")
        if "playwright" in content:
            features.append("Browser automation")
        if "selenium" in content:
            features.append("Web driver automation")
        if "pandas" in content:
            features.append("Data analysis")
        if "sqlalchemy" in content:
            features.append("Database ORM")
        if "flask" in content:
            features.append("Web framework")
        if "openai" in content or "gpt" in content:
            features.append("AI integration")
        if "snowflake" in content:
            features.append("Snowflake integration")
        if "redis" in content:
            features.append("Caching")
        if "docker" in content:
            features.append("Containerization")
        if "kubernetes" in content or "k8s" in content:
            features.append("Orchestration")
        if "prometheus" in content:
            features.append("Monitoring")
        if "pytest" in content or "unittest" in content:
            features.append("Testing")
        
        return features
    
    def match_ticket_to_code(self, ticket: Dict[str, Any], codebase_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Match a Jira ticket to relevant code components"""
        summary = ticket.get("fields", {}).get("summary", "").lower()
        description = ticket.get("fields", {}).get("description", {})
        labels = ticket.get("fields", {}).get("labels", [])
        
        # Extract description text
        description_text = ""
        if isinstance(description, dict) and "content" in description:
            for content in description.get("content", []):
                if content.get("type") == "paragraph":
                    for para_content in content.get("content", []):
                        if para_content.get("type") == "text":
                            description_text += para_content.get("text", "")
        
        # Find matching components
        matching_components = []
        matching_features = []
        code_snippets = []
        
        # Match based on keywords in summary and description
        all_text = f"{summary} {description_text} {' '.join(labels)}".lower()
        
        # Check each component category
        for category, components in codebase_analysis["components"].items():
            for component_name, component_info in components.items():
                # Check if component matches ticket
                if self.component_matches_ticket(component_name, all_text, summary, labels):
                    matching_components.append({
                        "category": category,
                        "component": component_name,
                        "file_path": component_info["file_path"],
                        "features": component_info["features"],
                        "code_snippet": component_info["code_snippet"]
                    })
                    code_snippets.append(component_info["code_snippet"])
        
        # Find matching features
        for feature_type, keywords in self.feature_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                matching_features.append(feature_type)
        
        return {
            "ticket_key": ticket.get("key"),
            "ticket_summary": ticket.get("fields", {}).get("summary", ""),
            "matching_components": matching_components,
            "matching_features": matching_features,
            "code_snippets": code_snippets,
            "confidence_score": self.calculate_confidence_score(matching_components, matching_features, all_text)
        }
    
    def component_matches_ticket(self, component_name: str, all_text: str, summary: str, labels: List[str]) -> bool:
        """Check if a component matches a ticket"""
        # Direct name matching
        if component_name in all_text:
            return True
        
        # Keyword matching
        component_keywords = {
            "indeed": ["indeed", "job board"],
            "linkedin": ["linkedin", "professional network"],
            "stackoverflow": ["stackoverflow", "stack overflow", "developer"],
            "dice": ["dice", "tech jobs"],
            "remoteok": ["remoteok", "remote ok", "remote jobs"],
            "weworkremotely": ["weworkremotely", "we work remotely"],
            "reddit": ["reddit", "community"],
            "playwright": ["playwright", "browser automation", "stealth"],
            "api_sources": ["api", "rest", "endpoint"],
            "lever": ["lever", "lever api"],
            "greenhouse": ["greenhouse", "greenhouse api"],
            "google_jobs": ["google jobs", "google"],
            "otta": ["otta", "startup jobs"],
            "hackernews": ["hackernews", "hacker news", "y combinator"],
            "yc_jobs": ["yc jobs", "y combinator"],
            "authentic_jobs": ["authentic jobs"],
            "jobspresso": ["jobspresso"],
            "himalayas": ["himalayas", "remote work"],
            "ai_analyzer": ["ai", "artificial intelligence", "analysis", "gpt"],
            "ai_matcher": ["matching", "recommendation", "ai"],
            "ai_resume_generator": ["resume", "cv", "generator"],
            "snowflake_manager": ["snowflake", "data warehouse", "analytics"],
            "db_manager": ["database", "postgresql", "sqlite"],
            "data_cleaner": ["data cleaning", "processing", "cleanup"],
            "skill_trends": ["skills", "trends", "analysis"]
        }
        
        if component_name in component_keywords:
            keywords = component_keywords[component_name]
            return any(keyword in all_text for keyword in keywords)
        
        return False
    
    def calculate_confidence_score(self, components: List[Dict], features: List[str], all_text: str) -> float:
        """Calculate confidence score for matching"""
        score = 0.0
        
        # Base score for components
        score += len(components) * 0.3
        
        # Base score for features
        score += len(features) * 0.2
        
        # Bonus for exact matches
        if any("snowflake" in all_text for _ in [1]):
            score += 0.2
        if any("ai" in all_text or "gpt" in all_text for _ in [1]):
            score += 0.2
        if any("scraper" in all_text for _ in [1]):
            score += 0.2
        
        return min(score, 1.0)
    
    def create_code_ticket_mapping(self) -> Dict[str, Any]:
        """Create comprehensive mapping between tickets and code"""
        try:
            logger.info("🚀 Starting code-ticket mapping analysis")
            
            # Test connection
            if not self.test_connection():
                return {}
            
            # Get all tickets
            tickets = self.get_all_tickets()
            logger.info(f"📋 Found {len(tickets)} tickets to analyze")
            
            # Analyze codebase
            logger.info("🔍 Analyzing codebase...")
            codebase_analysis = self.analyze_codebase()
            
            # Match tickets to code
            mappings = []
            for ticket in tickets:
                mapping = self.match_ticket_to_code(ticket, codebase_analysis)
                mappings.append(mapping)
            
            # Create summary
            result = {
                "total_tickets": len(tickets),
                "mapped_tickets": len([m for m in mappings if m["matching_components"]]),
                "codebase_analysis": codebase_analysis,
                "ticket_mappings": mappings,
                "summary": self.create_summary(mappings, codebase_analysis)
            }
            
            # Save results
            with open("code_ticket_mapping.json", "w") as f:
                json.dump(result, f, indent=2)
            
            logger.info("📄 Results saved to code_ticket_mapping.json")
            logger.info("🎉 Code-ticket mapping completed successfully!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Code-ticket mapping failed: {e}")
            return {}
    
    def create_summary(self, mappings: List[Dict], codebase_analysis: Dict) -> Dict[str, Any]:
        """Create summary of mappings"""
        summary = {
            "high_confidence_matches": [],
            "component_usage": {},
            "feature_coverage": {},
            "recommendations": []
        }
        
        # High confidence matches
        for mapping in mappings:
            if mapping["confidence_score"] > 0.7:
                summary["high_confidence_matches"].append({
                    "ticket": mapping["ticket_key"],
                    "summary": mapping["ticket_summary"],
                    "components": [c["component"] for c in mapping["matching_components"]],
                    "confidence": mapping["confidence_score"]
                })
        
        # Component usage
        for mapping in mappings:
            for component in mapping["matching_components"]:
                comp_name = component["component"]
                if comp_name not in summary["component_usage"]:
                    summary["component_usage"][comp_name] = 0
                summary["component_usage"][comp_name] += 1
        
        # Feature coverage
        for mapping in mappings:
            for feature in mapping["matching_features"]:
                if feature not in summary["feature_coverage"]:
                    summary["feature_coverage"][feature] = 0
                summary["feature_coverage"][feature] += 1
        
        return summary

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create matcher
    matcher = CodeTicketMatcher(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Create mappings
    result = matcher.create_code_ticket_mapping()
    
    if result:
        logger.info("🎉 Code-ticket mapping completed successfully!")
        logger.info(f"📊 Mapped {result['mapped_tickets']}/{result['total_tickets']} tickets")
        sys.exit(0)
    else:
        logger.error("❌ Code-ticket mapping failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
