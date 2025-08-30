#!/usr/bin/env python3
"""
AI-Powered Job Analysis Service for JobPulse
Integrates GPT-5 for intelligent job market insights
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIJobAnalyzer:
    """AI-powered job analysis using GPT-5"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI analyzer with OpenAI API key"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.setup_logging()
        
        # Default model - can be updated to GPT-5 when available
        self.model = "gpt-4-turbo-preview"  # Will be "gpt-5" when released
        
    def setup_logging(self):
        """Setup logging for the AI analyzer"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai_analysis.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_job_description(self, job_text: str, job_metadata: Dict = None) -> Dict[str, Any]:
        """
        Analyze job description using AI to extract insights
        
        Args:
            job_text: The job description text
            job_metadata: Additional job metadata (title, company, etc.)
        
        Returns:
            Dictionary containing extracted insights
        """
        try:
            prompt = self._create_job_analysis_prompt(job_text, job_metadata)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis = self._parse_job_analysis_response(response.choices[0].message.content)
            self.logger.info(f"Successfully analyzed job description")
            
            return {
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing job description: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_skill_recommendations(self, current_skills: List[str], target_role: str, 
                                     experience_level: str = "mid") -> Dict[str, Any]:
        """
        Generate AI-powered skill recommendations for career advancement
        
        Args:
            current_skills: List of current skills
            target_role: Target role to achieve
            experience_level: Current experience level (junior, mid, senior)
        
        Returns:
            Dictionary containing skill recommendations and learning path
        """
        try:
            prompt = self._create_skill_recommendation_prompt(current_skills, target_role, experience_level)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2500
            )
            
            recommendations = self._parse_skill_recommendations(response.choices[0].message.content)
            self.logger.info(f"Generated skill recommendations for {target_role}")
            
            return {
                'success': True,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Error generating skill recommendations: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_market_trends(self, job_data: List[Dict], time_period: str = "6months") -> Dict[str, Any]:
        """
        Analyze job market trends using AI
        
        Args:
            job_data: List of job postings with metadata
            time_period: Time period for analysis
        
        Returns:
            Dictionary containing market insights and trends
        """
        try:
            prompt = self._create_market_analysis_prompt(job_data, time_period)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=3000
            )
            
            trends = self._parse_market_trends(response.choices[0].message.content)
            self.logger.info(f"Analyzed market trends for {time_period}")
            
            return {
                'success': True,
                'trends': trends,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing market trends: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_job_analysis_prompt(self, job_text: str, job_metadata: Dict = None) -> str:
        """Create prompt for job description analysis"""
        metadata_str = ""
        if job_metadata:
            metadata_str = f"\nJob Title: {job_metadata.get('title', 'N/A')}\nCompany: {job_metadata.get('company', 'N/A')}\nLocation: {job_metadata.get('location', 'N/A')}"
        
        return f"""
        Analyze this job description and provide structured insights:

        {metadata_str}
        
        Job Description:
        {job_text}

        Please provide a JSON response with the following structure:
        {{
            "required_skills": {{
                "technical_skills": ["skill1", "skill2"],
                "soft_skills": ["skill1", "skill2"],
                "certifications": ["cert1", "cert2"]
            }},
            "experience_level": "entry|mid|senior|executive",
            "experience_indicators": {{
                "level_confidence": 0.95,
                "supporting_evidence": ["evidence1", "evidence2"],
                "years_experience": "0-2|3-5|6-8|8+",
                "seniority_indicators": ["indicator1", "indicator2"]
            }},
            "skills_by_experience": {{
                "entry_level_skills": ["skill1", "skill2"],
                "mid_level_skills": ["skill1", "skill2"],
                "senior_level_skills": ["skill1", "skill2"],
                "executive_level_skills": ["skill1", "skill2"]
            }},
            "salary_indicators": {{
                "min_experience_years": 0,
                "seniority_level": "entry|mid|senior|executive",
                "salary_range": "low|medium|high|very_high"
            }},
            "company_culture_insights": ["insight1", "insight2"],
            "growth_opportunities": ["opportunity1", "opportunity2"],
            "red_flags": ["flag1", "flag2"],
            "green_flags": ["flag1", "flag2"],
            "key_requirements": ["req1", "req2"],
            "nice_to_have": ["skill1", "skill2"]
        }}
        """
    
    def _create_skill_recommendation_prompt(self, current_skills: List[str], target_role: str, 
                                          experience_level: str) -> str:
        """Create prompt for skill recommendations"""
        return f"""
        Given the current skills and target role, provide skill development recommendations:

        Current Skills: {', '.join(current_skills)}
        Target Role: {target_role}
        Experience Level: {experience_level}

        Please provide a JSON response with the following structure:
        {{
            "skill_gaps": {{
                "critical_skills": ["skill1", "skill2"],
                "important_skills": ["skill1", "skill2"],
                "nice_to_have": ["skill1", "skill2"]
            }},
            "learning_path": [
                {{
                    "phase": "phase_name",
                    "skills": ["skill1", "skill2"],
                    "estimated_time": "X months",
                    "priority": "high|medium|low"
                }}
            ],
            "learning_resources": {{
                "courses": ["resource1", "resource2"],
                "books": ["book1", "book2"],
                "projects": ["project1", "project2"],
                "communities": ["community1", "community2"]
            }},
            "market_demand": {{
                "high_demand_skills": ["skill1", "skill2"],
                "growing_skills": ["skill1", "skill2"],
                "declining_skills": ["skill1", "skill2"]
            }},
            "timeline_estimate": "X-Y months to reach target role"
        }}
        """
    
    def analyze_experience_levels_and_skills(self, job_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze job data to extract experience levels and skills by experience level
        
        Args:
            job_data: List of job postings with metadata
        
        Returns:
            Dictionary containing experience level analysis and skills mapping
        """
        try:
            prompt = self._create_experience_analysis_prompt(job_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4000
            )
            
            analysis = self._parse_experience_analysis(response.choices[0].message.content)
            self.logger.info(f"Successfully analyzed experience levels and skills for {len(job_data)} jobs")
            
            return {
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing experience levels and skills: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_experience_analysis_prompt(self, job_data: List[Dict]) -> str:
        """Create prompt for experience level and skills analysis"""
        # Sample the job data to avoid token limits
        sample_data = job_data[:30] if len(job_data) > 30 else job_data
        
        return f"""
        Analyze this job data to extract experience levels and map skills to different career stages:

        Sample Job Data: {json.dumps(sample_data, indent=2)}

        Please provide a JSON response with the following structure:
        {{
            "experience_level_distribution": {{
                "entry": {{
                    "count": 0,
                    "percentage": 0.0,
                    "common_indicators": ["indicator1", "indicator2"]
                }},
                "mid": {{
                    "count": 0,
                    "percentage": 0.0,
                    "common_indicators": ["indicator1", "indicator2"]
                }},
                "senior": {{
                    "count": 0,
                    "percentage": 0.0,
                    "common_indicators": ["indicator1", "indicator2"]
                }},
                "executive": {{
                    "count": 0,
                    "percentage": 0.0,
                    "common_indicators": ["indicator1", "indicator2"]
                }}
            }},
            "skills_by_experience_level": {{
                "entry_level": {{
                    "core_skills": ["skill1", "skill2"],
                    "nice_to_have": ["skill1", "skill2"],
                    "frequency": {{"skill1": 10, "skill2": 8}}
                }},
                "mid_level": {{
                    "core_skills": ["skill1", "skill2"],
                    "nice_to_have": ["skill1", "skill2"],
                    "frequency": {{"skill1": 15, "skill2": 12}}
                }},
                "senior_level": {{
                    "core_skills": ["skill1", "skill2"],
                    "nice_to_have": ["skill1", "skill2"],
                    "frequency": {{"skill1": 20, "skill2": 18}}
                }},
                "executive_level": {{
                    "core_skills": ["skill1", "skill2"],
                    "nice_to_have": ["skill1", "skill2"],
                    "frequency": {{"skill1": 5, "skill2": 3}}
                }}
            }},
            "experience_level_insights": {{
                "most_common_level": "mid",
                "level_trends": ["trend1", "trend2"],
                "skill_evolution": {{
                    "entry_to_mid": ["skill1", "skill2"],
                    "mid_to_senior": ["skill1", "skill2"],
                    "senior_to_executive": ["skill1", "skill2"]
                }}
            }},
            "market_analysis": {{
                "demand_by_level": {{"entry": "high", "mid": "very_high", "senior": "high", "executive": "medium"}},
                "salary_trends_by_level": {{"entry": "stable", "mid": "increasing", "senior": "increasing", "executive": "stable"}},
                "emerging_requirements": ["req1", "req2"]
            }}
        }}
        """
    
    def _parse_experience_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for experience level analysis"""
        try:
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return self._fallback_parsing(response_text)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON response for experience analysis, using fallback parsing")
            return self._fallback_parsing(response_text)
    
    def _create_market_analysis_prompt(self, job_data: List[Dict], time_period: str) -> str:
        """Create prompt for market trend analysis"""
        # Sample the job data to avoid token limits
        sample_data = job_data[:50] if len(job_data) > 50 else job_data
        
        return f"""
        Analyze this job market data and provide insights for the past {time_period}:

        Sample Job Data: {json.dumps(sample_data, indent=2)}

        Please provide a JSON response with the following structure:
        {{
            "emerging_trends": {{
                "skills": ["skill1", "skill2"],
                "technologies": ["tech1", "tech2"],
                "roles": ["role1", "role2"]
            }},
            "salary_trends": {{
                "by_location": {{"location": "trend"}},
                "by_experience": {{"level": "trend"}}
            }},
            "industry_shifts": ["shift1", "shift2"],
            "future_predictions": {{
                "next_6_months": ["prediction1", "prediction2"],
                "next_year": ["prediction1", "prediction2"]
            }},
            "recommendations": {{
                "for_job_seekers": ["rec1", "rec2"],
                "for_career_advancement": ["rec1", "rec2"],
                "for_skill_development": ["rec1", "rec2"]
            }}
        }}
        """
    
    def _parse_job_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for job analysis"""
        try:
            # Try to extract JSON from response
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._fallback_parsing(response_text)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON response, using fallback parsing")
            return self._fallback_parsing(response_text)
    
    def _parse_skill_recommendations(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for skill recommendations"""
        try:
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return self._fallback_parsing(response_text)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON response, using fallback parsing")
            return self._fallback_parsing(response_text)
    
    def _parse_market_trends(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for market trends"""
        try:
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return self._fallback_parsing(response_text)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON response, using fallback parsing")
            return self._fallback_parsing(response_text)
    
    def _fallback_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        return {
            'raw_response': response_text,
            'parsing_method': 'fallback',
            'note': 'Response could not be parsed as JSON'
        }
    
    def update_model(self, new_model: str):
        """Update the AI model being used"""
        self.model = new_model
        self.logger.info(f"Updated AI model to: {new_model}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for the AI service"""
        try:
            # This would integrate with OpenAI's usage tracking
            return {
                'model': self.model,
                'api_calls': 'tracked_via_openai',
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting usage stats: {e}")
            return {'error': str(e)}
