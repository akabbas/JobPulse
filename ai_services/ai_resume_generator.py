#!/usr/bin/env python3
"""
AI-Powered Resume and Cover Letter Generator for JobPulse
Uses GPT-5 for intelligent document generation and optimization
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

class AIResumeGenerator:
    """AI-powered resume and cover letter generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI resume generator"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # Will be "gpt-5" when available
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the AI resume generator"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai_resume.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def generate_targeted_resume(self, user_profile: Dict[str, Any], job_description: Dict[str, Any], 
                                resume_format: str = "modern") -> Dict[str, Any]:
        """
        Generate a targeted resume for a specific job using AI
        
        Args:
            user_profile: User's experience, skills, and background
            job_description: Target job details and requirements
            resume_format: Resume style (modern, traditional, creative)
        
        Returns:
            Dictionary containing generated resume content
        """
        try:
            prompt = self._create_resume_generation_prompt(user_profile, job_description, resume_format)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=3000
            )
            
            resume_content = self._parse_resume_response(response.choices[0].message.content)
            self.logger.info(f"Generated targeted resume for {job_description.get('title', 'Unknown')}")
            
            return {
                'success': True,
                'resume': resume_content,
                'job_title': job_description.get('title', 'Unknown'),
                'company': job_description.get('company', 'Unknown'),
                'format': resume_format,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Error generating resume: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_cover_letter(self, user_profile: Dict[str, Any], job_description: Dict[str, Any], 
                             company_info: Dict[str, Any] = None, tone: str = "professional") -> Dict[str, Any]:
        """
        Generate a targeted cover letter using AI
        
        Args:
            user_profile: User's background and experience
            job_description: Target job details
            company_info: Company information and culture
            tone: Writing tone (professional, enthusiastic, casual)
        
        Returns:
            Dictionary containing generated cover letter
        """
        try:
            prompt = self._create_cover_letter_prompt(user_profile, job_description, company_info, tone)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2000
            )
            
            cover_letter = self._parse_cover_letter_response(response.choices[0].message.content)
            self.logger.info(f"Generated cover letter for {job_description.get('title', 'Unknown')}")
            
            return {
                'success': True,
                'cover_letter': cover_letter,
                'job_title': job_description.get('title', 'Unknown'),
                'company': job_description.get('company', 'Unknown'),
                'tone': tone,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def optimize_resume_for_ats(self, resume_content: Dict[str, Any], job_description: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize resume for Applicant Tracking Systems (ATS) using AI
        
        Args:
            resume_content: Current resume content
            job_description: Target job requirements
        
        Returns:
            Dictionary containing optimized resume
        """
        try:
            prompt = self._create_ats_optimization_prompt(resume_content, job_description)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2500
            )
            
            optimized_resume = self._parse_resume_response(response.choices[0].message.content)
            self.logger.info("Optimized resume for ATS compatibility")
            
            return {
                'success': True,
                'original_resume': resume_content,
                'optimized_resume': optimized_resume,
                'ats_improvements': self._identify_ats_improvements(resume_content, optimized_resume),
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing resume for ATS: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_resume_variations(self, user_profile: Dict[str, Any], target_roles: List[str], 
                                  formats: List[str] = None) -> Dict[str, Any]:
        """
        Generate multiple resume variations for different roles
        
        Args:
            user_profile: User's background and experience
            target_roles: List of target job roles
            formats: List of resume formats to generate
        
        Returns:
            Dictionary containing multiple resume variations
        """
        if formats is None:
            formats = ["modern", "traditional"]
        
        variations = {}
        
        for role in target_roles:
            for format_style in formats:
                try:
                    # Create a mock job description for the role
                    mock_job = {
                        'title': role,
                        'company': 'Target Company',
                        'description': f'Software engineering role focusing on {role}',
                        'requirements': [f'{role} experience', 'Software development', 'Problem solving']
                    }
                    
                    resume = self.generate_targeted_resume(user_profile, mock_job, format_style)
                    if resume['success']:
                        key = f"{role}_{format_style}"
                        variations[key] = resume
                        
                except Exception as e:
                    self.logger.warning(f"Failed to generate variation for {role} in {format_style}: {e}")
        
        return {
            'success': True,
            'variations': variations,
            'total_generated': len(variations),
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_resume_generation_prompt(self, user_profile: Dict[str, Any], 
                                        job_description: Dict[str, Any], 
                                        resume_format: str) -> str:
        """Create prompt for resume generation"""
        return f"""
        Generate a targeted resume for this specific job opportunity:

        USER PROFILE:
        {json.dumps(user_profile, indent=2)}

        TARGET JOB:
        {json.dumps(job_description, indent=2)}

        RESUME FORMAT: {resume_format}

        Create a professional resume that:
        1. Highlights relevant skills and experience for this specific role
        2. Uses action verbs and quantifiable achievements
        3. Follows the {resume_format} format style
        4. Is optimized for both human readers and ATS systems
        5. Emphasizes transferable skills when direct experience is limited

        Return the resume in this JSON structure:
        {{
            "header": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "phone_number",
                "location": "City, State",
                "linkedin": "linkedin_url",
                "portfolio": "portfolio_url"
            }},
            "summary": "Professional summary tailored to the job",
            "experience": [
                {{
                    "title": "Job Title",
                    "company": "Company Name",
                    "duration": "Duration",
                    "achievements": [
                        "Quantified achievement 1",
                        "Quantified achievement 2"
                    ]
                }}
            ],
            "skills": {{
                "technical_skills": ["skill1", "skill2"],
                "soft_skills": ["skill1", "skill2"],
                "tools": ["tool1", "tool2"]
            }},
            "education": [
                {{
                    "degree": "Degree Name",
                    "institution": "Institution",
                    "graduation_year": "Year",
                    "gpa": "GPA if relevant"
                }}
            ],
            "certifications": ["cert1", "cert2"],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Brief description",
                    "technologies": ["tech1", "tech2"],
                    "url": "project_url"
                }}
            ]
        }}
        """
    
    def _create_cover_letter_prompt(self, user_profile: Dict[str, Any], 
                                   job_description: Dict[str, Any], 
                                   company_info: Dict[str, Any], 
                                   tone: str) -> str:
        """Create prompt for cover letter generation"""
        company_str = ""
        if company_info:
            company_str = f"\nCOMPANY INFORMATION:\n{json.dumps(company_info, indent=2)}"
        
        return f"""
        Generate a compelling cover letter for this job opportunity:

        USER PROFILE:
        {json.dumps(user_profile, indent=2)}

        TARGET JOB:
        {json.dumps(job_description, indent=2)}
        {company_str}

        WRITING TONE: {tone}

        Create a cover letter that:
        1. Opens with a strong hook that shows enthusiasm for the role
        2. Demonstrates understanding of the company and position
        3. Connects the user's experience to the job requirements
        4. Shows cultural fit and alignment with company values
        5. Ends with a clear call to action
        6. Maintains the specified {tone} tone throughout

        Return the cover letter in this JSON structure:
        {{
            "header": {{
                "date": "Current Date",
                "recipient_name": "Hiring Manager Name",
                "recipient_title": "Hiring Manager Title",
                "company_name": "Company Name",
                "company_address": "Company Address"
            }},
            "greeting": "Dear [Name or Hiring Manager]",
            "opening_paragraph": "Engaging opening paragraph",
            "body_paragraphs": [
                "Body paragraph 1 - Experience and skills",
                "Body paragraph 2 - Company fit and enthusiasm"
            ],
            "closing_paragraph": "Strong closing with call to action",
            "signature": "Sincerely,\n[Your Name]",
            "postscript": "Optional P.S. with additional compelling point"
        }}
        """
    
    def _create_ats_optimization_prompt(self, resume_content: Dict[str, Any], 
                                       job_description: Dict[str, Any]) -> str:
        """Create prompt for ATS optimization"""
        return f"""
        Optimize this resume for Applicant Tracking Systems (ATS) compatibility:

        CURRENT RESUME:
        {json.dumps(resume_content, indent=2)}

        TARGET JOB:
        {json.dumps(job_description, indent=2)}

        Optimize the resume to:
        1. Include relevant keywords from the job description
        2. Use standard section headings (Experience, Education, Skills)
        3. Avoid graphics, tables, or complex formatting
        4. Use simple, clean fonts and formatting
        5. Include industry-standard terminology
        6. Ensure proper keyword density without stuffing
        7. Make it scannable for both ATS and human readers

        Return the optimized resume in the same JSON structure as the original.
        """
    
    def _parse_resume_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for resume content"""
        try:
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return self._fallback_resume_content()
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON response, using fallback content")
            return self._fallback_resume_content()
    
    def _parse_cover_letter_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for cover letter content"""
        try:
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return self._fallback_cover_letter_content()
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON response, using fallback content")
            return self._fallback_cover_letter_content()
    
    def _identify_ats_improvements(self, original: Dict[str, Any], optimized: Dict[str, Any]) -> List[str]:
        """Identify improvements made for ATS compatibility"""
        improvements = []
        
        # Check for keyword improvements
        if 'skills' in original and 'skills' in optimized:
            orig_skills = original['skills'].get('technical_skills', [])
            opt_skills = optimized['skills'].get('technical_skills', [])
            
            if len(opt_skills) > len(orig_skills):
                improvements.append("Added relevant keywords for better ATS matching")
        
        # Check for formatting improvements
        if 'summary' in original and 'summary' in optimized:
            if len(optimized['summary']) > len(original['summary']):
                improvements.append("Enhanced summary with job-specific keywords")
        
        # Check for experience improvements
        if 'experience' in original and 'experience' in optimized:
            orig_exp = len(original['experience'])
            opt_exp = len(optimized['experience'])
            
            if opt_exp > orig_exp:
                improvements.append("Expanded experience descriptions with relevant keywords")
        
        return improvements if improvements else ["No significant ATS improvements identified"]
    
    def _fallback_resume_content(self) -> Dict[str, Any]:
        """Fallback resume content when parsing fails"""
        return {
            'header': {
                'name': 'Your Name',
                'email': 'your.email@example.com',
                'phone': 'Your Phone',
                'location': 'Your Location'
            },
            'summary': 'Professional summary could not be generated',
            'experience': [],
            'skills': {'technical_skills': [], 'soft_skills': []},
            'education': [],
            'certifications': [],
            'projects': []
        }
    
    def _fallback_cover_letter_content(self) -> Dict[str, Any]:
        """Fallback cover letter content when parsing fails"""
        return {
            'header': {
                'date': datetime.now().strftime('%B %d, %Y'),
                'recipient_name': 'Hiring Manager',
                'company_name': 'Company Name'
            },
            'greeting': 'Dear Hiring Manager,',
            'opening_paragraph': 'Cover letter content could not be generated',
            'body_paragraphs': [],
            'closing_paragraph': 'Thank you for your consideration.',
            'signature': 'Sincerely,\nYour Name'
        }
    
    def update_model(self, new_model: str):
        """Update the AI model being used"""
        self.model = new_model
        self.logger.info(f"Updated AI model to: {new_model}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for the AI service"""
        try:
            return {
                'model': self.model,
                'api_calls': 'tracked_via_openai',
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting usage stats: {e}")
            return {'error': str(e)}
