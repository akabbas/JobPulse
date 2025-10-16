#!/usr/bin/env python3
"""
Analyze Tickets and Create Smart Categories for JobPulse
Analyzes all ticket content to create meaningful categories based on actual content
"""

import json
import logging
import os
import sys
import requests
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartCategoryAnalyzer:
    """Analyze ticket content and create intelligent categories"""
    
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
        
        # Analysis results
        self.ticket_analysis = []
        self.content_patterns = defaultdict(list)
        self.keyword_frequency = Counter()
        self.suggested_categories = {}
        
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
    
    def extract_all_text_content(self, issue_data: Dict[str, Any]) -> str:
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
    
    def analyze_ticket_content(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual ticket content"""
        try:
            issue_key = issue_data.get("key")
            summary = issue_data.get("fields", {}).get("summary", "")
            full_text = self.extract_all_text_content(issue_data)
            
            # Extract key information
            analysis = {
                "issue_key": issue_key,
                "summary": summary,
                "full_text": full_text,
                "word_count": len(full_text.split()),
                "keywords": [],
                "themes": [],
                "priority_indicators": [],
                "technical_indicators": [],
                "business_indicators": []
            }
            
            # Analyze for different types of content
            technical_keywords = ["api", "database", "server", "code", "function", "class", "method", "endpoint", "integration", "migration", "refactor", "optimize", "performance", "security", "monitoring", "logging", "testing", "deployment", "infrastructure", "architecture", "framework", "library", "dependency", "configuration", "environment", "docker", "kubernetes", "redis", "postgresql", "snowflake", "caching", "rate-limiting", "health-check"]
            
            business_keywords = ["user", "customer", "revenue", "business", "premium", "subscription", "billing", "payment", "monetization", "market", "sales", "growth", "conversion", "retention", "engagement", "analytics", "reporting", "dashboard", "insights", "metrics", "kpi", "roi", "profit", "cost", "pricing", "plan", "strategy"]
            
            priority_keywords = ["critical", "urgent", "emergency", "broken", "fix", "hotfix", "patch", "immediate", "asap", "priority", "high", "low", "medium", "blocking", "dependency", "deadline", "milestone", "release", "production", "live", "deploy"]
            
            data_keywords = ["data", "analytics", "snowflake", "database", "query", "sql", "etl", "pipeline", "warehouse", "lake", "streaming", "real-time", "batch", "processing", "transformation", "cleaning", "validation", "quality", "governance", "privacy", "compliance", "audit", "backup", "recovery", "sync", "replication"]
            
            ai_keywords = ["ai", "machine learning", "ml", "artificial intelligence", "neural", "model", "prediction", "classification", "clustering", "recommendation", "nlp", "natural language", "text analysis", "sentiment", "cortex", "intelligence", "automation", "algorithm", "pattern", "insight", "forecast", "trend", "anomaly", "detection"]
            
            # Categorize keywords
            for keyword in technical_keywords:
                if keyword in full_text:
                    analysis["technical_indicators"].append(keyword)
                    analysis["keywords"].append(keyword)
            
            for keyword in business_keywords:
                if keyword in full_text:
                    analysis["business_indicators"].append(keyword)
                    analysis["keywords"].append(keyword)
            
            for keyword in priority_keywords:
                if keyword in full_text:
                    analysis["priority_indicators"].append(keyword)
                    analysis["keywords"].append(keyword)
            
            for keyword in data_keywords:
                if keyword in full_text:
                    analysis["themes"].append("data")
                    analysis["keywords"].append(keyword)
            
            for keyword in ai_keywords:
                if keyword in full_text:
                    analysis["themes"].append("ai")
                    analysis["keywords"].append(keyword)
            
            # Determine primary theme
            if analysis["themes"]:
                analysis["primary_theme"] = max(set(analysis["themes"]), key=analysis["themes"].count)
            else:
                analysis["primary_theme"] = "general"
            
            # Determine complexity level
            complexity_score = len(analysis["technical_indicators"]) + len(analysis["keywords"])
            if complexity_score > 10:
                analysis["complexity"] = "high"
            elif complexity_score > 5:
                analysis["complexity"] = "medium"
            else:
                analysis["complexity"] = "low"
            
            # Determine urgency
            if analysis["priority_indicators"]:
                analysis["urgency"] = "high"
            else:
                analysis["urgency"] = "normal"
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing ticket content: {e}")
            return {}
    
    def analyze_all_tickets(self) -> bool:
        """Analyze all tickets to understand content patterns"""
        try:
            logger.info("🚀 Starting comprehensive ticket content analysis")
            
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
            logger.info(f"📋 Found {len(issues)} issues to analyze")
            
            # Analyze each ticket
            for i, issue in enumerate(issues):
                logger.info(f"📊 Analyzing ticket {i+1}/{len(issues)}: {issue.get('key')}")
                analysis = self.analyze_ticket_content(issue)
                if analysis:
                    self.ticket_analysis.append(analysis)
                    
                    # Update keyword frequency
                    for keyword in analysis["keywords"]:
                        self.keyword_frequency[keyword] += 1
                    
                    # Group by themes
                    theme = analysis["primary_theme"]
                    self.content_patterns[theme].append(analysis)
            
            logger.info(f"✅ Analysis completed for {len(self.ticket_analysis)} tickets")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ticket analysis failed: {e}")
            return False
    
    def generate_smart_categories(self) -> Dict[str, Any]:
        """Generate smart categories based on analysis"""
        try:
            logger.info("🧠 Generating smart categories based on content analysis")
            
            # Analyze patterns
            theme_counts = {theme: len(tickets) for theme, tickets in self.content_patterns.items()}
            top_keywords = self.keyword_frequency.most_common(20)
            
            # Create category suggestions
            categories = {}
            
            # 1. Priority-based categories
            urgent_tickets = [t for t in self.ticket_analysis if t["urgency"] == "high"]
            if urgent_tickets:
                categories["🚨 Critical & Urgent"] = {
                    "description": "Critical issues requiring immediate attention",
                    "tickets": urgent_tickets,
                    "count": len(urgent_tickets),
                    "keywords": ["critical", "urgent", "broken", "fix", "emergency"]
                }
            
            # 2. Technical complexity categories
            high_complexity = [t for t in self.ticket_analysis if t["complexity"] == "high"]
            if high_complexity:
                categories["🔧 Complex Technical Work"] = {
                    "description": "High-complexity technical tasks requiring expertise",
                    "tickets": high_complexity,
                    "count": len(high_complexity),
                    "keywords": ["architecture", "migration", "integration", "performance"]
                }
            
            # 3. Data and analytics
            data_tickets = [t for t in self.ticket_analysis if "data" in t["themes"]]
            if data_tickets:
                categories["📊 Data & Analytics"] = {
                    "description": "Data processing, analytics, and business intelligence",
                    "tickets": data_tickets,
                    "count": len(data_tickets),
                    "keywords": ["data", "analytics", "snowflake", "database", "reporting"]
                }
            
            # 4. AI and machine learning
            ai_tickets = [t for t in self.ticket_analysis if "ai" in t["themes"]]
            if ai_tickets:
                categories["🤖 AI & Machine Learning"] = {
                    "description": "Artificial intelligence and machine learning features",
                    "tickets": ai_tickets,
                    "count": len(ai_tickets),
                    "keywords": ["ai", "ml", "machine learning", "cortex", "intelligence"]
                }
            
            # 5. Business and revenue
            business_tickets = [t for t in self.ticket_analysis if t["business_indicators"]]
            if business_tickets:
                categories["💰 Business & Revenue"] = {
                    "description": "Business features, monetization, and revenue generation",
                    "tickets": business_tickets,
                    "count": len(business_tickets),
                    "keywords": ["business", "revenue", "premium", "monetization", "user"]
                }
            
            # 6. Infrastructure and operations
            infra_tickets = [t for t in self.ticket_analysis if len(t["technical_indicators"]) > 3]
            if infra_tickets:
                categories["🏗️ Infrastructure & Ops"] = {
                    "description": "Infrastructure, operations, and system maintenance",
                    "tickets": infra_tickets,
                    "count": len(infra_tickets),
                    "keywords": ["infrastructure", "monitoring", "deployment", "security", "performance"]
                }
            
            # 7. User experience
            ux_tickets = [t for t in self.ticket_analysis if "user" in t["full_text"] or "interface" in t["full_text"]]
            if ux_tickets:
                categories["👤 User Experience"] = {
                    "description": "User interface, experience, and interaction improvements",
                    "tickets": ux_tickets,
                    "count": len(ux_tickets),
                    "keywords": ["user", "interface", "experience", "ui", "ux", "dashboard"]
                }
            
            # 8. Quality and testing
            quality_tickets = [t for t in self.ticket_analysis if "test" in t["full_text"] or "quality" in t["full_text"]]
            if quality_tickets:
                categories["🧪 Quality & Testing"] = {
                    "description": "Testing, quality assurance, and code quality",
                    "tickets": quality_tickets,
                    "count": len(quality_tickets),
                    "keywords": ["test", "testing", "quality", "qa", "coverage", "validation"]
                }
            
            # 9. Documentation and knowledge
            doc_tickets = [t for t in self.ticket_analysis if "documentation" in t["full_text"] or "doc" in t["full_text"]]
            if doc_tickets:
                categories["📚 Documentation & Knowledge"] = {
                    "description": "Documentation, knowledge management, and information",
                    "tickets": doc_tickets,
                    "count": len(doc_tickets),
                    "keywords": ["documentation", "doc", "knowledge", "guide", "manual"]
                }
            
            # 10. General development
            general_tickets = [t for t in self.ticket_analysis if t["primary_theme"] == "general"]
            if general_tickets:
                categories["🛠️ General Development"] = {
                    "description": "General development tasks and improvements",
                    "tickets": general_tickets,
                    "count": len(general_tickets),
                    "keywords": ["development", "feature", "improvement", "enhancement"]
                }
            
            self.suggested_categories = categories
            return categories
            
        except Exception as e:
            logger.error(f"❌ Error generating smart categories: {e}")
            return {}
    
    def save_analysis_results(self) -> bool:
        """Save analysis results to files"""
        try:
            # Save detailed analysis
            analysis_results = {
                "total_tickets": len(self.ticket_analysis),
                "analysis_timestamp": "2025-10-16T14:30:00Z",
                "ticket_analysis": self.ticket_analysis,
                "keyword_frequency": dict(self.keyword_frequency.most_common(50)),
                "content_patterns": {theme: len(tickets) for theme, tickets in self.content_patterns.items()},
                "suggested_categories": self.suggested_categories
            }
            
            with open("smart_category_analysis.json", "w") as f:
                json.dump(analysis_results, f, indent=2)
            
            # Save category summary
            category_summary = {
                "total_categories": len(self.suggested_categories),
                "categories": {}
            }
            
            for category_name, category_data in self.suggested_categories.items():
                category_summary["categories"][category_name] = {
                    "description": category_data["description"],
                    "ticket_count": category_data["count"],
                    "keywords": category_data["keywords"],
                    "ticket_keys": [t["issue_key"] for t in category_data["tickets"]]
                }
            
            with open("smart_categories_summary.json", "w") as f:
                json.dump(category_summary, f, indent=2)
            
            logger.info("📄 Analysis results saved to smart_category_analysis.json")
            logger.info("📄 Category summary saved to smart_categories_summary.json")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis results: {e}")
            return False
    
    def run_complete_analysis(self) -> bool:
        """Run complete ticket analysis and category generation"""
        try:
            logger.info("🚀 Starting complete ticket analysis and smart categorization")
            
            # Analyze all tickets
            if not self.analyze_all_tickets():
                return False
            
            # Generate smart categories
            categories = self.generate_smart_categories()
            
            # Save results
            if not self.save_analysis_results():
                return False
            
            # Log results
            logger.info("📊 Smart Category Analysis Results:")
            logger.info(f"📋 Total tickets analyzed: {len(self.ticket_analysis)}")
            logger.info(f"📊 Suggested categories: {len(categories)}")
            
            for category_name, category_data in categories.items():
                logger.info(f"  📁 {category_name}: {category_data['count']} tickets")
                logger.info(f"    📝 {category_data['description']}")
            
            logger.info("🎉 Complete analysis and smart categorization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete analysis failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create analyzer
    analyzer = SmartCategoryAnalyzer(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Run complete analysis
    success = analyzer.run_complete_analysis()
    
    if success:
        logger.info("🎉 Smart category analysis completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Smart category analysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
