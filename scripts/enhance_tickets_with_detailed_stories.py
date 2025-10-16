#!/usr/bin/env python3
"""
Enhance Jira Tickets with Detailed User Stories
Creates professional, detailed documentation for each ticket using proper user story format
"""

import json
import logging
import os
import sys
import requests
from typing import Dict, List, Any
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TicketEnhancer:
    """Enhance Jira tickets with detailed user stories and professional documentation"""
    
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
        
        # User story templates based on problem categories
        self.story_templates = {
            "🚫 Anti-Bot Detection & Bypass": {
                "user_types": ["developer", "data engineer", "scraper engineer", "system administrator"],
                "goals": ["prevent 403 errors", "avoid IP blocks", "maintain data collection", "ensure scraper reliability"],
                "benefits": ["Improved data collection reliability", "Reduced maintenance overhead", "Better user experience", "Cost savings from reduced downtime"]
            },
            "🔌 Multi-Source Data Collection": {
                "user_types": ["data engineer", "product manager", "business analyst", "job seeker"],
                "goals": ["aggregate comprehensive job data", "provide complete market coverage", "reduce manual searching", "improve data quality"],
                "benefits": ["Complete market visibility", "Better job matching", "Reduced manual effort", "Competitive advantage"]
            },
            "🤖 AI-Powered Job Analysis": {
                "user_types": ["job seeker", "recruiter", "business analyst", "product manager"],
                "goals": ["get intelligent job recommendations", "analyze market trends", "match skills to opportunities", "gain career insights"],
                "benefits": ["Personalized job matching", "Market intelligence", "Career guidance", "Competitive differentiation"]
            },
            "🏗️ Production Infrastructure": {
                "user_types": ["system administrator", "devops engineer", "product manager", "end user"],
                "goals": ["ensure system reliability", "scale the application", "maintain uptime", "provide consistent service"],
                "benefits": ["High availability", "Scalable architecture", "Reduced downtime", "Better user experience"]
            },
            "📊 Data Analytics & Insights": {
                "user_types": ["business analyst", "product manager", "executive", "data scientist"],
                "goals": ["analyze market trends", "make data-driven decisions", "identify opportunities", "track performance"],
                "benefits": ["Market intelligence", "Strategic insights", "Competitive analysis", "Business growth"]
            },
            "🔧 Plugin Architecture & Extensibility": {
                "user_types": ["developer", "system architect", "product manager", "maintenance engineer"],
                "goals": ["maintain code quality", "add new features easily", "reduce technical debt", "improve system reliability"],
                "benefits": ["Easier maintenance", "Faster development", "Better code quality", "Reduced technical debt"]
            },
            "⚡ Performance & Optimization": {
                "user_types": ["end user", "system administrator", "product manager", "developer"],
                "goals": ["improve response times", "reduce resource usage", "enhance user experience", "optimize system efficiency"],
                "benefits": ["Better user experience", "Reduced infrastructure costs", "Improved scalability", "Higher user satisfaction"]
            },
            "🛡️ Error Handling & Reliability": {
                "user_types": ["end user", "system administrator", "developer", "product manager"],
                "goals": ["prevent system failures", "handle errors gracefully", "maintain data integrity", "ensure system stability"],
                "benefits": ["Improved reliability", "Better user experience", "Reduced support burden", "Higher system uptime"]
            },
            "👤 User Experience & Interface": {
                "user_types": ["job seeker", "recruiter", "business user", "administrator"],
                "goals": ["navigate the system easily", "find information quickly", "complete tasks efficiently", "have an intuitive experience"],
                "benefits": ["Improved user adoption", "Reduced training time", "Higher user satisfaction", "Better task completion rates"]
            },
            "🧪 Testing & Quality Assurance": {
                "user_types": ["developer", "quality engineer", "product manager", "end user"],
                "goals": ["ensure code quality", "prevent bugs", "maintain system reliability", "deliver stable features"],
                "benefits": ["Higher code quality", "Reduced bugs", "Better user experience", "Lower maintenance costs"]
            },
            "📚 Documentation & Knowledge": {
                "user_types": ["developer", "new team member", "stakeholder", "end user"],
                "goals": ["understand the system", "onboard quickly", "maintain knowledge", "reduce support burden"],
                "benefits": ["Faster onboarding", "Reduced support costs", "Better knowledge sharing", "Improved team productivity"]
            },
            "💰 Business & Monetization": {
                "user_types": ["business owner", "product manager", "sales team", "customer"],
                "goals": ["generate revenue", "attract customers", "scale the business", "create value"],
                "benefits": ["Revenue growth", "Market expansion", "Customer acquisition", "Business sustainability"]
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
    
    def extract_ticket_content(self, issue_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract and analyze ticket content"""
        try:
            summary = issue_data.get("fields", {}).get("summary", "")
            description = issue_data.get("fields", {}).get("description", {})
            labels = issue_data.get("fields", {}).get("labels", [])
            
            # Extract text from description
            description_text = ""
            if isinstance(description, dict) and "content" in description:
                for content in description.get("content", []):
                    if content.get("type") == "paragraph":
                        for para_content in content.get("content", []):
                            if para_content.get("type") == "text":
                                description_text += para_content.get("text", "")
            
            # Determine category from labels
            category = "🛠️ General Development"
            for label in labels:
                if "anti-bot-detection" in label:
                    category = "🚫 Anti-Bot Detection & Bypass"
                elif "multi-source-data" in label:
                    category = "🔌 Multi-Source Data Collection"
                elif "ai-powered-analysis" in label:
                    category = "🤖 AI-Powered Job Analysis"
                elif "production-infrastructure" in label:
                    category = "🏗️ Production Infrastructure"
                elif "data-analytics-insights" in label:
                    category = "📊 Data Analytics & Insights"
                elif "plugin-architecture" in label:
                    category = "🔧 Plugin Architecture & Extensibility"
                elif "performance-optimization" in label:
                    category = "⚡ Performance & Optimization"
                elif "error-handling-reliability" in label:
                    category = "🛡️ Error Handling & Reliability"
                elif "user-experience" in label:
                    category = "👤 User Experience & Interface"
                elif "quality-testing" in label:
                    category = "🧪 Testing & Quality Assurance"
                elif "documentation-knowledge" in label:
                    category = "📚 Documentation & Knowledge"
                elif "business-monetization" in label:
                    category = "💰 Business & Monetization"
                break
            
            return {
                "summary": summary,
                "description": description_text,
                "category": category,
                "labels": labels
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting ticket content: {e}")
            return {}
    
    def generate_detailed_story(self, ticket_content: Dict[str, str]) -> str:
        """Generate detailed user story documentation"""
        try:
            summary = ticket_content.get("summary", "")
            description = ticket_content.get("description", "")
            category = ticket_content.get("category", "🛠️ General Development")
            
            # Get template for category
            template = self.story_templates.get(category, self.story_templates["🛠️ General Development"])
            user_types = template["user_types"]
            goals = template["goals"]
            benefits = template["benefits"]
            
            # Generate user story
            user_type = user_types[0] if user_types else "user"
            goal = goals[0] if goals else "improve the system"
            benefit = benefits[0] if benefits else "achieve better results"
            
            # Create detailed documentation
            detailed_story = f"""# {summary}

## 📋 User Story
**As a** {user_type}, **I want to** {self.generate_task_from_summary(summary)} **so that I can** {goal}.

## 🎯 Acceptance Criteria
{self.generate_acceptance_criteria(summary, description)}

## ⚡ Nonfunctional Requirements
{self.generate_nonfunctional_requirements(category, summary)}

## 💡 Benefit Hypothesis
{self.generate_benefit_hypothesis(category, summary, benefit)}

## 🔧 Technical Implementation
{self.generate_technical_implementation(summary, description)}

## 📊 Success Metrics
{self.generate_success_metrics(category, summary)}

## 🚀 Dependencies
{self.generate_dependencies(summary, description)}

## 📝 Notes
{self.generate_notes(summary, description, category)}

---
*Category: {category}*
*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            return detailed_story
            
        except Exception as e:
            logger.error(f"❌ Error generating detailed story: {e}")
            return f"# {ticket_content.get('summary', 'Unknown')}\n\nError generating detailed story: {e}"
    
    def generate_task_from_summary(self, summary: str) -> str:
        """Generate task description from summary"""
        summary_lower = summary.lower()
        
        if "implement" in summary_lower or "create" in summary_lower:
            return f"implement {summary.lower()}"
        elif "fix" in summary_lower or "repair" in summary_lower:
            return f"fix {summary.lower()}"
        elif "add" in summary_lower or "integrate" in summary_lower:
            return f"add {summary.lower()}"
        elif "update" in summary_lower or "upgrade" in summary_lower:
            return f"update {summary.lower()}"
        elif "optimize" in summary_lower or "improve" in summary_lower:
            return f"optimize {summary.lower()}"
        else:
            return f"complete {summary.lower()}"
    
    def generate_acceptance_criteria(self, summary: str, description: str) -> str:
        """Generate acceptance criteria"""
        criteria = []
        
        # Generic criteria based on common patterns
        if "test" in summary.lower():
            criteria.extend([
                "✅ All tests pass with 100% success rate",
                "✅ Test coverage meets minimum requirements",
                "✅ Performance tests validate expected behavior"
            ])
        
        if "api" in summary.lower() or "integration" in summary.lower():
            criteria.extend([
                "✅ API endpoints return expected responses",
                "✅ Error handling works correctly",
                "✅ Authentication and authorization work properly"
            ])
        
        if "ui" in summary.lower() or "interface" in summary.lower():
            criteria.extend([
                "✅ User interface is responsive and accessible",
                "✅ All user interactions work as expected",
                "✅ Design matches specifications"
            ])
        
        if "data" in summary.lower() or "database" in summary.lower():
            criteria.extend([
                "✅ Data is stored and retrieved correctly",
                "✅ Data integrity is maintained",
                "✅ Performance meets requirements"
            ])
        
        # Default criteria
        if not criteria:
            criteria.extend([
                "✅ Feature works as specified",
                "✅ No errors or exceptions occur",
                "✅ Performance meets requirements",
                "✅ Code follows project standards"
            ])
        
        return "\n".join(criteria)
    
    def generate_nonfunctional_requirements(self, category: str, summary: str) -> str:
        """Generate nonfunctional requirements"""
        requirements = []
        
        if "🚫 Anti-Bot Detection" in category:
            requirements.extend([
                "🛡️ **Security**: Implement anti-detection measures without compromising system security",
                "⚡ **Performance**: Maintain response times under 2 seconds",
                "🔄 **Reliability**: 99.9% uptime for scraping operations"
            ])
        elif "🏗️ Production Infrastructure" in category:
            requirements.extend([
                "🚀 **Scalability**: Support 1000+ concurrent users",
                "⚡ **Performance**: Response times under 500ms",
                "🛡️ **Security**: Implement proper authentication and authorization"
            ])
        elif "🤖 AI-Powered" in category:
            requirements.extend([
                "🧠 **Accuracy**: AI predictions with 90%+ accuracy",
                "⚡ **Performance**: AI processing under 5 seconds",
                "🔒 **Privacy**: Ensure data privacy and compliance"
            ])
        elif "📊 Data Analytics" in category:
            requirements.extend([
                "📈 **Performance**: Handle large datasets efficiently",
                "🔍 **Accuracy**: Analytics results within 95% confidence",
                "📊 **Usability**: Intuitive dashboard interface"
            ])
        else:
            requirements.extend([
                "⚡ **Performance**: Meet specified response time requirements",
                "🛡️ **Security**: Follow security best practices",
                "🔄 **Reliability**: Maintain system stability"
            ])
        
        return "\n".join(requirements)
    
    def generate_benefit_hypothesis(self, category: str, summary: str, benefit: str) -> str:
        """Generate benefit hypothesis"""
        hypotheses = []
        
        if "🚫 Anti-Bot Detection" in category:
            hypotheses.append("We believe that implementing robust anti-bot detection will reduce scraping failures by 80% and improve data collection reliability.")
        elif "🏗️ Production Infrastructure" in category:
            hypotheses.append("We believe that improving infrastructure will increase system reliability by 95% and reduce downtime by 90%.")
        elif "🤖 AI-Powered" in category:
            hypotheses.append("We believe that AI-powered features will improve user satisfaction by 60% and increase engagement by 40%.")
        elif "📊 Data Analytics" in category:
            hypotheses.append("We believe that enhanced analytics will provide actionable insights that drive 30% better decision-making.")
        elif "🔧 Plugin Architecture" in category:
            hypotheses.append("We believe that plugin architecture will reduce development time by 50% and improve maintainability by 70%.")
        else:
            hypotheses.append(f"We believe that implementing this feature will {benefit.lower()} and improve overall system performance.")
        
        return "\n".join(hypotheses)
    
    def generate_technical_implementation(self, summary: str, description: str) -> str:
        """Generate technical implementation details"""
        implementation = []
        
        if "api" in summary.lower():
            implementation.extend([
                "🔌 **API Integration**: Implement RESTful API endpoints",
                "🔐 **Authentication**: Add proper authentication mechanisms",
                "📝 **Documentation**: Create comprehensive API documentation"
            ])
        elif "database" in summary.lower() or "data" in summary.lower():
            implementation.extend([
                "🗄️ **Database Design**: Design efficient database schema",
                "🔍 **Query Optimization**: Optimize database queries for performance",
                "🔄 **Data Migration**: Implement safe data migration strategies"
            ])
        elif "ui" in summary.lower() or "interface" in summary.lower():
            implementation.extend([
                "🎨 **Frontend Development**: Create responsive user interface",
                "📱 **Mobile Support**: Ensure mobile compatibility",
                "♿ **Accessibility**: Implement accessibility standards"
            ])
        else:
            implementation.extend([
                "🏗️ **Architecture**: Design scalable system architecture",
                "🧪 **Testing**: Implement comprehensive testing strategy",
                "📚 **Documentation**: Create technical documentation"
            ])
        
        return "\n".join(implementation)
    
    def generate_success_metrics(self, category: str, summary: str) -> str:
        """Generate success metrics"""
        metrics = []
        
        if "🚫 Anti-Bot Detection" in category:
            metrics.extend([
                "📊 **Success Rate**: 95%+ successful scraping attempts",
                "⏱️ **Response Time**: <2 seconds average response time",
                "🔄 **Uptime**: 99.9% system availability"
            ])
        elif "🏗️ Production Infrastructure" in category:
            metrics.extend([
                "🚀 **Performance**: <500ms average response time",
                "📈 **Scalability**: Support 1000+ concurrent users",
                "🛡️ **Reliability**: 99.9% uptime"
            ])
        elif "🤖 AI-Powered" in category:
            metrics.extend([
                "🎯 **Accuracy**: 90%+ prediction accuracy",
                "⚡ **Speed**: <5 seconds processing time",
                "👥 **User Satisfaction**: 4.5+ star rating"
            ])
        else:
            metrics.extend([
                "📊 **Completion Rate**: 100% feature completion",
                "⚡ **Performance**: Meet specified performance targets",
                "👥 **User Feedback**: Positive user feedback"
            ])
        
        return "\n".join(metrics)
    
    def generate_dependencies(self, summary: str, description: str) -> str:
        """Generate dependencies"""
        dependencies = []
        
        if "integration" in summary.lower():
            dependencies.append("🔗 **External APIs**: Ensure third-party API availability")
        if "database" in summary.lower():
            dependencies.append("🗄️ **Database**: Database schema updates required")
        if "ui" in summary.lower():
            dependencies.append("🎨 **Design System**: UI/UX design specifications")
        
        if not dependencies:
            dependencies.append("📋 **Requirements**: Clear requirements and specifications")
        
        return "\n".join(dependencies)
    
    def generate_notes(self, summary: str, description: str, category: str) -> str:
        """Generate additional notes"""
        notes = []
        
        notes.append(f"📝 **Category**: {category}")
        notes.append(f"📅 **Created**: {time.strftime('%Y-%m-%d')}")
        
        if "critical" in summary.lower() or "urgent" in summary.lower():
            notes.append("🚨 **Priority**: High - Critical for system functionality")
        
        if "security" in summary.lower() or "auth" in summary.lower():
            notes.append("🔒 **Security**: Security review required before implementation")
        
        if "performance" in summary.lower() or "optimization" in summary.lower():
            notes.append("⚡ **Performance**: Performance testing required")
        
        return "\n".join(notes)
    
    def update_issue_description(self, issue_key: str, detailed_story: str) -> bool:
        """Update issue with detailed story"""
        try:
            # Convert markdown to Jira format
            jira_content = self.convert_markdown_to_jira(detailed_story)
            
            payload = {
                "fields": {
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": jira_content
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
                logger.info(f"✅ Updated {issue_key} with detailed story")
                return True
            else:
                logger.error(f"❌ Failed to update {issue_key}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating {issue_key}: {e}")
            return False
    
    def convert_markdown_to_jira(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Convert markdown content to Jira format"""
        try:
            content = []
            lines = markdown_content.split('\n')
            
            for line in lines:
                if line.startswith('# '):
                    # Main heading
                    content.append({
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": line[2:]}]
                    })
                elif line.startswith('## '):
                    # Subheading
                    content.append({
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": line[3:]}]
                    })
                elif line.startswith('### '):
                    # Sub-subheading
                    content.append({
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": line[4:]}]
                    })
                elif line.startswith('✅') or line.startswith('📊') or line.startswith('⚡') or line.startswith('💡') or line.startswith('🔧') or line.startswith('🚀') or line.startswith('📝') or line.startswith('🔒') or line.startswith('🛡️') or line.startswith('🎯') or line.startswith('📋') or line.startswith('🔗') or line.startswith('📅') or line.startswith('🚨'):
                    # Bullet point with emoji
                    content.append({
                        "type": "paragraph",
                        "content": [{"type": "text", "text": line}]
                    })
                elif line.startswith('- '):
                    # Bullet point
                    content.append({
                        "type": "paragraph",
                        "content": [{"type": "text", "text": line[2:]}]
                    })
                elif line.strip():
                    # Regular paragraph
                    content.append({
                        "type": "paragraph",
                        "content": [{"type": "text", "text": line}]
                    })
                else:
                    # Empty line
                    content.append({
                        "type": "paragraph",
                        "content": []
                    })
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Error converting markdown to Jira: {e}")
            return [{"type": "paragraph", "content": [{"type": "text", "text": markdown_content}]}]
    
    def enhance_all_tickets(self) -> bool:
        """Enhance all tickets with detailed stories"""
        try:
            logger.info("🚀 Starting ticket enhancement with detailed user stories")
            
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
            logger.info(f"📋 Found {len(issues)} issues to enhance")
            
            # Enhance each ticket
            enhanced_count = 0
            enhancement_results = []
            
            for i, issue in enumerate(issues):
                issue_key = issue.get("key")
                logger.info(f"📝 Enhancing ticket {i+1}/{len(issues)}: {issue_key}")
                
                # Get current issue data
                issue_data = self.get_issue(issue_key)
                if not issue_data:
                    continue
                
                # Extract ticket content
                ticket_content = self.extract_ticket_content(issue_data)
                if not ticket_content:
                    continue
                
                # Generate detailed story
                detailed_story = self.generate_detailed_story(ticket_content)
                
                # Update issue with detailed story
                if self.update_issue_description(issue_key, detailed_story):
                    enhanced_count += 1
                    enhancement_results.append({
                        "issue_key": issue_key,
                        "summary": ticket_content.get("summary", ""),
                        "category": ticket_content.get("category", ""),
                        "enhanced": True
                    })
                else:
                    enhancement_results.append({
                        "issue_key": issue_key,
                        "summary": ticket_content.get("summary", ""),
                        "category": ticket_content.get("category", ""),
                        "enhanced": False
                    })
                
                # Add delay to avoid rate limiting
                time.sleep(0.5)
            
            # Log results
            logger.info(f"🎉 Ticket enhancement completed!")
            logger.info(f"📊 Enhanced {enhanced_count}/{len(issues)} tickets")
            
            # Save results
            results = {
                "total_tickets": len(issues),
                "enhanced_tickets": enhanced_count,
                "enhancement_results": enhancement_results,
                "enhancement_timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open("ticket_enhancement_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info("📄 Enhancement results saved to ticket_enhancement_results.json")
            logger.info("🎉 Ticket enhancement completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ticket enhancement failed: {e}")
            return False

def main():
    """Main function"""
    # Get environment variables
    jira_site = os.getenv("JIRA_SITE")
    api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_site or not api_token:
        logger.error("❌ Missing required environment variables: JIRA_SITE, JIRA_API_TOKEN")
        sys.exit(1)
    
    # Create enhancer
    enhancer = TicketEnhancer(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Enhance all tickets
    success = enhancer.enhance_all_tickets()
    
    if success:
        logger.info("🎉 All tickets enhanced with detailed user stories!")
        sys.exit(0)
    else:
        logger.error("❌ Ticket enhancement failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
