#!/usr/bin/env python3
"""
Enhanced Jira Tickets with Professional User Stories - FIXED VERSION
Creates detailed, professional documentation for each ticket using proper user story format
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

class ProfessionalTicketEnhancer:
    """Enhance Jira tickets with professional user stories and detailed documentation"""
    
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
            category = "General Development"
            for label in labels:
                if "anti-bot-detection" in label:
                    category = "Anti-Bot Detection & Bypass"
                elif "multi-source-data" in label:
                    category = "Multi-Source Data Collection"
                elif "ai-powered-analysis" in label:
                    category = "AI-Powered Job Analysis"
                elif "production-infrastructure" in label:
                    category = "Production Infrastructure"
                elif "data-analytics-insights" in label:
                    category = "Data Analytics & Insights"
                elif "plugin-architecture" in label:
                    category = "Plugin Architecture & Extensibility"
                elif "performance-optimization" in label:
                    category = "Performance & Optimization"
                elif "error-handling-reliability" in label:
                    category = "Error Handling & Reliability"
                elif "user-experience" in label:
                    category = "User Experience & Interface"
                elif "quality-testing" in label:
                    category = "Testing & Quality Assurance"
                elif "documentation-knowledge" in label:
                    category = "Documentation & Knowledge"
                elif "business-monetization" in label:
                    category = "Business & Monetization"
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
    
    def generate_professional_user_story(self, ticket_content: Dict[str, str]) -> str:
        """Generate professional user story documentation"""
        try:
            summary = ticket_content.get("summary", "")
            description = ticket_content.get("description", "")
            category = ticket_content.get("category", "General Development")
            
            # Determine user type and goal based on category and summary
            user_type, goal, benefit = self.determine_user_story_elements(summary, category)
            
            # Generate task description
            task = self.generate_task_description(summary)
            
            # Create professional documentation
            professional_story = f"""# {summary}

## 📋 User Story
**As a** {user_type}, **I want to** {task} **so that I can** {goal}.

## 🎯 Acceptance Criteria
{self.generate_acceptance_criteria(summary, category)}

## ⚡ Nonfunctional Requirements
{self.generate_nonfunctional_requirements(category, summary)}

## 💡 Benefit Hypothesis
{self.generate_benefit_hypothesis(category, summary, benefit)}

## 🔧 Technical Implementation
{self.generate_technical_implementation(summary, category)}

## 📊 Success Metrics
{self.generate_success_metrics(category, summary)}

## 🚀 Dependencies
{self.generate_dependencies(summary, category)}

## 📝 Notes
{self.generate_notes(summary, category)}

---
*Category: {category}*
*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            return professional_story
            
        except Exception as e:
            logger.error(f"❌ Error generating professional story: {e}")
            return f"# {ticket_content.get('summary', 'Unknown')}\n\nError generating story: {e}"
    
    def determine_user_story_elements(self, summary: str, category: str) -> tuple:
        """Determine user type, goal, and benefit based on summary and category"""
        summary_lower = summary.lower()
        
        # User types based on category
        if "Anti-Bot Detection" in category:
            return ("scraper engineer", "prevent 403 errors and IP blocks", "maintain reliable data collection")
        elif "Multi-Source Data Collection" in category:
            return ("data engineer", "aggregate jobs from multiple sources", "provide comprehensive market coverage")
        elif "AI-Powered Job Analysis" in category:
            return ("job seeker", "get intelligent job recommendations", "find better career opportunities")
        elif "Production Infrastructure" in category:
            return ("system administrator", "ensure system reliability and scalability", "maintain high uptime")
        elif "Data Analytics & Insights" in category:
            return ("business analyst", "analyze market trends and patterns", "make data-driven decisions")
        elif "Plugin Architecture" in category:
            return ("developer", "maintain and extend the system easily", "reduce technical debt")
        elif "Performance & Optimization" in category:
            return ("end user", "experience faster response times", "have a better user experience")
        elif "Error Handling & Reliability" in category:
            return ("end user", "have a stable and reliable system", "avoid system failures")
        elif "User Experience & Interface" in category:
            return ("job seeker", "navigate the system easily", "complete tasks efficiently")
        elif "Testing & Quality Assurance" in category:
            return ("developer", "ensure code quality and reliability", "deliver stable features")
        elif "Documentation & Knowledge" in category:
            return ("new team member", "understand the system quickly", "onboard efficiently")
        elif "Business & Monetization" in category:
            return ("business owner", "generate revenue and grow the business", "achieve financial sustainability")
        else:
            return ("user", "improve the system", "achieve better results")
    
    def generate_task_description(self, summary: str) -> str:
        """Generate task description from summary"""
        summary_lower = summary.lower()
        
        if "implement" in summary_lower:
            return f"implement {summary.lower()}"
        elif "add" in summary_lower:
            return f"add {summary.lower()}"
        elif "create" in summary_lower:
            return f"create {summary.lower()}"
        elif "fix" in summary_lower or "repair" in summary_lower:
            return f"fix {summary.lower()}"
        elif "update" in summary_lower or "upgrade" in summary_lower:
            return f"update {summary.lower()}"
        elif "optimize" in summary_lower or "improve" in summary_lower:
            return f"optimize {summary.lower()}"
        elif "integrate" in summary_lower:
            return f"integrate {summary.lower()}"
        elif "enhance" in summary_lower:
            return f"enhance {summary.lower()}"
        else:
            return f"complete {summary.lower()}"
    
    def generate_acceptance_criteria(self, summary: str, category: str) -> str:
        """Generate acceptance criteria"""
        criteria = []
        
        # Generic criteria based on common patterns
        if "test" in summary.lower():
            criteria.extend([
                "✅ All tests pass with 100% success rate",
                "✅ Test coverage meets minimum requirements (80%+)",
                "✅ Performance tests validate expected behavior",
                "✅ Integration tests verify system compatibility"
            ])
        
        if "api" in summary.lower() or "integration" in summary.lower():
            criteria.extend([
                "✅ API endpoints return expected responses",
                "✅ Error handling works correctly for all scenarios",
                "✅ Authentication and authorization work properly",
                "✅ API documentation is complete and accurate"
            ])
        
        if "ui" in summary.lower() or "interface" in summary.lower() or "dashboard" in summary.lower():
            criteria.extend([
                "✅ User interface is responsive and accessible",
                "✅ All user interactions work as expected",
                "✅ Design matches specifications and brand guidelines",
                "✅ Cross-browser compatibility is verified"
            ])
        
        if "data" in summary.lower() or "database" in summary.lower():
            criteria.extend([
                "✅ Data is stored and retrieved correctly",
                "✅ Data integrity is maintained",
                "✅ Performance meets requirements (<2s response time)",
                "✅ Backup and recovery procedures work"
            ])
        
        if "auth" in summary.lower() or "security" in summary.lower():
            criteria.extend([
                "✅ Authentication works for all user types",
                "✅ Authorization is properly enforced",
                "✅ Security best practices are followed",
                "✅ No security vulnerabilities are introduced"
            ])
        
        # Default criteria
        if not criteria:
            criteria.extend([
                "✅ Feature works as specified in requirements",
                "✅ No errors or exceptions occur during normal operation",
                "✅ Performance meets specified requirements",
                "✅ Code follows project standards and best practices",
                "✅ Documentation is updated and accurate"
            ])
        
        return "\n".join(criteria)
    
    def generate_nonfunctional_requirements(self, category: str, summary: str) -> str:
        """Generate nonfunctional requirements"""
        requirements = []
        
        if "Anti-Bot Detection" in category:
            requirements.extend([
                "🛡️ **Security**: Implement anti-detection measures without compromising system security",
                "⚡ **Performance**: Maintain response times under 2 seconds",
                "🔄 **Reliability**: 99.9% uptime for scraping operations",
                "🔒 **Privacy**: Ensure user data privacy and compliance"
            ])
        elif "Production Infrastructure" in category:
            requirements.extend([
                "🚀 **Scalability**: Support 1000+ concurrent users",
                "⚡ **Performance**: Response times under 500ms",
                "🛡️ **Security**: Implement proper authentication and authorization",
                "🔄 **Reliability**: 99.9% system uptime"
            ])
        elif "AI-Powered" in category:
            requirements.extend([
                "🧠 **Accuracy**: AI predictions with 90%+ accuracy",
                "⚡ **Performance**: AI processing under 5 seconds",
                "🔒 **Privacy**: Ensure data privacy and compliance",
                "📊 **Usability**: Intuitive AI-powered interface"
            ])
        elif "Data Analytics" in category:
            requirements.extend([
                "📈 **Performance**: Handle large datasets efficiently",
                "🔍 **Accuracy**: Analytics results within 95% confidence",
                "📊 **Usability**: Intuitive dashboard interface",
                "🔄 **Reliability**: Consistent data processing"
            ])
        else:
            requirements.extend([
                "⚡ **Performance**: Meet specified response time requirements",
                "🛡️ **Security**: Follow security best practices",
                "🔄 **Reliability**: Maintain system stability",
                "📱 **Usability**: Ensure good user experience"
            ])
        
        return "\n".join(requirements)
    
    def generate_benefit_hypothesis(self, category: str, summary: str, benefit: str) -> str:
        """Generate benefit hypothesis"""
        hypotheses = []
        
        if "Anti-Bot Detection" in category:
            hypotheses.append("We believe that implementing robust anti-bot detection will reduce scraping failures by 80% and improve data collection reliability, leading to better user experience and reduced maintenance overhead.")
        elif "Production Infrastructure" in category:
            hypotheses.append("We believe that improving infrastructure will increase system reliability by 95% and reduce downtime by 90%, resulting in higher user satisfaction and reduced support burden.")
        elif "AI-Powered" in category:
            hypotheses.append("We believe that AI-powered features will improve user satisfaction by 60% and increase engagement by 40%, leading to better user retention and competitive advantage.")
        elif "Data Analytics" in category:
            hypotheses.append("We believe that enhanced analytics will provide actionable insights that drive 30% better decision-making and improve business outcomes.")
        elif "Plugin Architecture" in category:
            hypotheses.append("We believe that plugin architecture will reduce development time by 50% and improve maintainability by 70%, leading to faster feature delivery and lower technical debt.")
        else:
            hypotheses.append(f"We believe that implementing this feature will {benefit.lower()} and improve overall system performance, leading to better user satisfaction and business value.")
        
        return "\n".join(hypotheses)
    
    def generate_technical_implementation(self, summary: str, category: str) -> str:
        """Generate technical implementation details"""
        implementation = []
        
        if "api" in summary.lower():
            implementation.extend([
                "🔌 **API Integration**: Implement RESTful API endpoints with proper HTTP methods",
                "🔐 **Authentication**: Add JWT-based authentication mechanisms",
                "📝 **Documentation**: Create comprehensive API documentation with examples",
                "🧪 **Testing**: Implement unit and integration tests for all endpoints"
            ])
        elif "database" in summary.lower() or "data" in summary.lower():
            implementation.extend([
                "🗄️ **Database Design**: Design efficient database schema with proper indexing",
                "🔍 **Query Optimization**: Optimize database queries for performance",
                "🔄 **Data Migration**: Implement safe data migration strategies",
                "📊 **Monitoring**: Add database performance monitoring"
            ])
        elif "ui" in summary.lower() or "interface" in summary.lower():
            implementation.extend([
                "🎨 **Frontend Development**: Create responsive user interface using modern frameworks",
                "📱 **Mobile Support**: Ensure mobile compatibility and responsive design",
                "♿ **Accessibility**: Implement WCAG 2.1 accessibility standards",
                "🧪 **Testing**: Add automated UI testing and cross-browser testing"
            ])
        else:
            implementation.extend([
                "🏗️ **Architecture**: Design scalable system architecture with proper separation of concerns",
                "🧪 **Testing**: Implement comprehensive testing strategy (unit, integration, e2e)",
                "📚 **Documentation**: Create technical documentation and code comments",
                "🔧 **DevOps**: Set up CI/CD pipeline and deployment automation"
            ])
        
        return "\n".join(implementation)
    
    def generate_success_metrics(self, category: str, summary: str) -> str:
        """Generate success metrics"""
        metrics = []
        
        if "Anti-Bot Detection" in category:
            metrics.extend([
                "📊 **Success Rate**: 95%+ successful scraping attempts",
                "⏱️ **Response Time**: <2 seconds average response time",
                "🔄 **Uptime**: 99.9% system availability",
                "🛡️ **Error Rate**: <1% error rate for scraping operations"
            ])
        elif "Production Infrastructure" in category:
            metrics.extend([
                "🚀 **Performance**: <500ms average response time",
                "📈 **Scalability**: Support 1000+ concurrent users",
                "🛡️ **Reliability**: 99.9% uptime",
                "⚡ **Throughput**: Handle 10,000+ requests per minute"
            ])
        elif "AI-Powered" in category:
            metrics.extend([
                "🎯 **Accuracy**: 90%+ prediction accuracy",
                "⚡ **Speed**: <5 seconds processing time",
                "👥 **User Satisfaction**: 4.5+ star rating",
                "📈 **Engagement**: 40% increase in user engagement"
            ])
        else:
            metrics.extend([
                "📊 **Completion Rate**: 100% feature completion",
                "⚡ **Performance**: Meet specified performance targets",
                "👥 **User Feedback**: Positive user feedback (4+ stars)",
                "🔄 **Reliability**: Zero critical bugs in production"
            ])
        
        return "\n".join(metrics)
    
    def generate_dependencies(self, summary: str, category: str) -> str:
        """Generate dependencies"""
        dependencies = []
        
        if "integration" in summary.lower():
            dependencies.append("🔗 **External APIs**: Ensure third-party API availability and documentation")
        if "database" in summary.lower():
            dependencies.append("🗄️ **Database**: Database schema updates and migration scripts required")
        if "ui" in summary.lower():
            dependencies.append("🎨 **Design System**: UI/UX design specifications and component library")
        if "auth" in summary.lower():
            dependencies.append("🔐 **Security**: Security review and authentication system setup")
        if "ai" in summary.lower():
            dependencies.append("🧠 **AI Services**: AI model training and API integration")
        
        if not dependencies:
            dependencies.append("📋 **Requirements**: Clear requirements and technical specifications")
        
        dependencies.append("👥 **Team**: Development team availability and expertise")
        dependencies.append("🛠️ **Tools**: Required development tools and environments")
        
        return "\n".join(dependencies)
    
    def generate_notes(self, summary: str, category: str) -> str:
        """Generate additional notes"""
        notes = []
        
        notes.append(f"📝 **Category**: {category}")
        notes.append(f"📅 **Created**: {time.strftime('%Y-%m-%d')}")
        
        if "critical" in summary.lower() or "urgent" in summary.lower():
            notes.append("🚨 **Priority**: High - Critical for system functionality")
        
        if "security" in summary.lower() or "auth" in summary.lower():
            notes.append("🔒 **Security**: Security review required before implementation")
        
        if "performance" in summary.lower() or "optimization" in summary.lower():
            notes.append("⚡ **Performance**: Performance testing and optimization required")
        
        if "ai" in summary.lower() or "ml" in summary.lower():
            notes.append("🧠 **AI/ML**: Machine learning model training and validation required")
        
        notes.append("📋 **Review**: Code review and testing required before deployment")
        notes.append("📚 **Documentation**: Update technical documentation and user guides")
        
        return "\n".join(notes)
    
    def update_issue_description(self, issue_key: str, professional_story: str) -> bool:
        """Update issue with professional story"""
        try:
            # Convert markdown to Jira format
            jira_content = self.convert_markdown_to_jira(professional_story)
            
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
                logger.info(f"✅ Updated {issue_key} with professional story")
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
                elif line.startswith('✅') or line.startswith('📊') or line.startswith('⚡') or line.startswith('💡') or line.startswith('🔧') or line.startswith('🚀') or line.startswith('📝') or line.startswith('🔒') or line.startswith('🛡️') or line.startswith('🎯') or line.startswith('📋') or line.startswith('🔗') or line.startswith('📅') or line.startswith('🚨') or line.startswith('🧠') or line.startswith('🎨') or line.startswith('🗄️') or line.startswith('🔍') or line.startswith('🔄') or line.startswith('📈') or line.startswith('👥') or line.startswith('🛠️') or line.startswith('🏗️') or line.startswith('🧪') or line.startswith('📱') or line.startswith('♿') or line.startswith('🔐') or line.startswith('🔌') or line.startswith('📚') or line.startswith('⏱️') or line.startswith('🎯'):
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
        """Enhance all tickets with professional user stories"""
        try:
            logger.info("🚀 Starting professional ticket enhancement")
            
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
                
                # Generate professional story
                professional_story = self.generate_professional_user_story(ticket_content)
                
                # Update issue with professional story
                if self.update_issue_description(issue_key, professional_story):
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
            logger.info(f"🎉 Professional ticket enhancement completed!")
            logger.info(f"📊 Enhanced {enhanced_count}/{len(issues)} tickets")
            
            # Save results
            results = {
                "total_tickets": len(issues),
                "enhanced_tickets": enhanced_count,
                "enhancement_results": enhancement_results,
                "enhancement_timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open("professional_ticket_enhancement_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info("📄 Enhancement results saved to professional_ticket_enhancement_results.json")
            logger.info("🎉 Professional ticket enhancement completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Professional ticket enhancement failed: {e}")
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
    enhancer = ProfessionalTicketEnhancer(jira_site, api_token, "ammrabbasher@gmail.com")
    
    # Enhance all tickets
    success = enhancer.enhance_all_tickets()
    
    if success:
        logger.info("🎉 All tickets enhanced with professional user stories!")
        sys.exit(0)
    else:
        logger.error("❌ Professional ticket enhancement failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
