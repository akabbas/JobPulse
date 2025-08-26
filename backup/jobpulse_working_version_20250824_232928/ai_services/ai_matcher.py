#!/usr/bin/env python3
"""
AI-Powered Job Matching Service for JobPulse
Uses GPT-5 for intelligent job recommendations and personalization
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
from dotenv import load_dotenv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

class AIJobMatcher:
    """AI-powered job matching using GPT-5 and ML techniques"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI job matcher"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # Will be "gpt-5" when available
        self.setup_logging()
        
        # Initialize TF-IDF vectorizer for text similarity
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def setup_logging(self):
        """Setup logging for the AI matcher"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai_matching.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def match_jobs_to_profile(self, user_profile: Dict[str, Any], available_jobs: List[Dict], 
                             top_k: int = 10) -> Dict[str, Any]:
        """
        Match available jobs to user profile using AI and ML
        
        Args:
            user_profile: User's skills, experience, preferences
            available_jobs: List of available job postings
            top_k: Number of top matches to return
        
        Returns:
            Dictionary containing matched jobs and insights
        """
        try:
            # Step 1: AI-powered profile analysis
            profile_analysis = self._analyze_user_profile(user_profile)
            
            # Step 2: AI-powered job understanding
            enhanced_jobs = self._enhance_job_understandings(available_jobs)
            
            # Step 3: Multi-dimensional matching
            matches = self._calculate_matches(user_profile, enhanced_jobs, profile_analysis)
            
            # Step 4: AI-powered ranking and insights
            ranked_matches = self._ai_rank_matches(matches, user_profile, top_k)
            
            # Step 5: Generate personalized insights
            insights = self._generate_personalized_insights(user_profile, ranked_matches)
            
            return {
                'success': True,
                'matches': ranked_matches[:top_k],
                'insights': insights,
                'total_jobs_analyzed': len(available_jobs),
                'matching_score_distribution': self._get_score_distribution(matches),
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            self.logger.error(f"Error in job matching: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def expand_search_queries(self, base_query: str, user_profile: Dict[str, Any]) -> List[str]:
        """
        Use AI to expand search queries for better job discovery
        
        Args:
            base_query: Base search query
            user_profile: User's profile and preferences
        
        Returns:
            List of expanded search queries
        """
        try:
            prompt = self._create_query_expansion_prompt(base_query, user_profile)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1000
            )
            
            expanded_queries = self._parse_expanded_queries(response.choices[0].message.content)
            self.logger.info(f"Expanded '{base_query}' to {len(expanded_queries)} queries")
            
            return expanded_queries
            
        except Exception as e:
            self.logger.error(f"Error expanding search queries: {e}")
            return [base_query]  # Fallback to original query
    
    def _analyze_user_profile(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user profile using AI to extract insights"""
        try:
            prompt = self._create_profile_analysis_prompt(user_profile)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            analysis = self._parse_profile_analysis(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing user profile: {e}")
            return self._fallback_profile_analysis(user_profile)
    
    def _enhance_job_understandings(self, jobs: List[Dict]) -> List[Dict]:
        """Enhance job postings with AI-generated insights"""
        enhanced_jobs = []
        
        for job in jobs:
            try:
                # Extract key information from job description
                job_text = job.get('description', '') + ' ' + job.get('title', '')
                
                # Use AI to extract structured information
                enhanced_info = self._extract_job_insights(job_text, job)
                
                enhanced_job = {
                    **job,
                    'ai_enhanced': enhanced_info,
                    'skills_extracted': enhanced_info.get('skills', []),
                    'experience_level': enhanced_info.get('experience_level', 'unknown'),
                    'culture_indicators': enhanced_info.get('culture_indicators', []),
                    'growth_potential': enhanced_info.get('growth_potential', 'medium')
                }
                
                enhanced_jobs.append(enhanced_job)
                
            except Exception as e:
                self.logger.warning(f"Failed to enhance job {job.get('id', 'unknown')}: {e}")
                enhanced_jobs.append(job)
        
        return enhanced_jobs
    
    def _calculate_matches(self, user_profile: Dict[str, Any], enhanced_jobs: List[Dict], 
                          profile_analysis: Dict[str, Any]) -> List[Tuple[Dict, float]]:
        """Calculate matching scores using multiple criteria"""
        matches = []
        
        for job in enhanced_jobs:
            try:
                # 1. Skills matching (40% weight)
                skills_score = self._calculate_skills_match(
                    user_profile.get('skills', []),
                    job.get('skills_extracted', [])
                )
                
                # 2. Experience level matching (25% weight)
                experience_score = self._calculate_experience_match(
                    user_profile.get('experience_level', 'mid'),
                    job.get('experience_level', 'unknown')
                )
                
                # 3. Location preference matching (15% weight)
                location_score = self._calculate_location_match(
                    user_profile.get('location_preferences', []),
                    job.get('location', '')
                )
                
                # 4. Company culture fit (10% weight)
                culture_score = self._calculate_culture_match(
                    user_profile.get('culture_preferences', []),
                    job.get('culture_indicators', [])
                )
                
                # 5. Career growth alignment (10% weight)
                growth_score = self._calculate_growth_match(
                    user_profile.get('career_goals', []),
                    job.get('growth_potential', 'medium')
                )
                
                # Calculate weighted total score
                total_score = (
                    skills_score * 0.40 +
                    experience_score * 0.25 +
                    location_score * 0.15 +
                    culture_score * 0.10 +
                    growth_score * 0.10
                )
                
                matches.append((job, total_score))
                
            except Exception as e:
                self.logger.warning(f"Failed to calculate match for job {job.get('id', 'unknown')}: {e}")
                matches.append((job, 0.0))
        
        return matches
    
    def _ai_rank_matches(self, matches: List[Tuple[Dict, float]], user_profile: Dict[str, Any], 
                         top_k: int) -> List[Dict]:
        """Use AI to provide final ranking and insights"""
        try:
            # Sort by score first
            sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)
            
            # Get top matches for AI analysis
            top_matches = sorted_matches[:min(top_k * 2, len(sorted_matches))]
            
            # Use AI to provide final ranking with explanations
            ai_ranking = self._get_ai_ranking(top_matches, user_profile)
            
            # Combine AI insights with original scores
            final_matches = []
            for job, score in top_matches:
                ai_insight = ai_ranking.get(str(job.get('id', 'unknown')), {})
                
                final_match = {
                    **job,
                    'matching_score': score,
                    'ai_ranking': ai_insight.get('rank', 0),
                    'ai_explanation': ai_insight.get('explanation', ''),
                    'ai_recommendations': ai_insight.get('recommendations', [])
                }
                
                final_matches.append(final_match)
            
            # Final sort by AI ranking
            final_matches.sort(key=lambda x: x.get('ai_ranking', 0))
            
            return final_matches[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error in AI ranking: {e}")
            # Fallback to score-based ranking
            return [job for job, score in sorted(matches, key=lambda x: x[1], reverse=True)[:top_k]]
    
    def _calculate_skills_match(self, user_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skills matching score"""
        if not user_skills or not job_skills:
            return 0.0
        
        # Convert to lowercase for comparison
        user_skills_lower = [skill.lower() for skill in user_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Calculate intersection
        matching_skills = set(user_skills_lower) & set(job_skills_lower)
        
        # Calculate score based on matching skills and total required skills
        if len(job_skills_lower) == 0:
            return 0.0
        
        match_ratio = len(matching_skills) / len(job_skills_lower)
        
        # Bonus for having more skills than required
        skill_bonus = min(len(user_skills_lower) / max(len(job_skills_lower), 1), 1.5)
        
        return min(match_ratio * skill_bonus, 1.0)
    
    def _calculate_experience_match(self, user_level: str, job_level: str) -> float:
        """Calculate experience level matching score"""
        level_mapping = {
            'junior': 1, 'entry': 1, 'associate': 1,
            'mid': 2, 'intermediate': 2, 'experienced': 2,
            'senior': 3, 'lead': 4, 'principal': 4, 'staff': 4
        }
        
        user_num = level_mapping.get(user_level.lower(), 2)
        job_num = level_mapping.get(job_level.lower(), 2)
        
        # Perfect match
        if user_num == job_num:
            return 1.0
        
        # User is slightly overqualified (still good)
        if user_num == job_num + 1:
            return 0.8
        
        # User is underqualified
        if user_num < job_num:
            return max(0.1, 1.0 - (job_num - user_num) * 0.3)
        
        # User is overqualified
        return max(0.3, 1.0 - (user_num - job_num) * 0.2)
    
    def _calculate_location_match(self, user_preferences: List[str], job_location: str) -> float:
        """Calculate location preference matching score"""
        if not user_preferences or not job_location:
            return 0.5  # Neutral score
        
        job_location_lower = job_location.lower()
        
        for preference in user_preferences:
            preference_lower = preference.lower()
            
            # Exact match
            if preference_lower == job_location_lower:
                return 1.0
            
            # Partial match (e.g., "San Francisco" matches "SF")
            if preference_lower in job_location_lower or job_location_lower in preference_lower:
                return 0.8
            
            # Country/state match
            if any(region in job_location_lower for region in ['united states', 'us', 'usa']):
                if any(region in preference_lower for region in ['united states', 'us', 'usa']):
                    return 0.6
        
        return 0.3  # Low score for no matches
    
    def _calculate_culture_match(self, user_preferences: List[str], job_indicators: List[str]) -> float:
        """Calculate company culture matching score"""
        if not user_preferences or not job_indicators:
            return 0.5
        
        # Simple keyword matching for now
        user_prefs_lower = [pref.lower() for pref in user_preferences]
        job_indicators_lower = [ind.lower() for ind in job_indicators]
        
        matches = sum(1 for pref in user_prefs_lower 
                     if any(pref in ind or ind in pref for ind in job_indicators_lower))
        
        return min(matches / len(user_preferences), 1.0)
    
    def _calculate_growth_match(self, user_goals: List[str], job_growth: str) -> float:
        """Calculate career growth alignment score"""
        if not user_goals or not job_growth:
            return 0.5
        
        growth_keywords = {
            'high': ['growth', 'advancement', 'career development', 'learning'],
            'medium': ['opportunity', 'development', 'training'],
            'low': ['stable', 'maintenance', 'support']
        }
        
        job_growth_lower = job_growth.lower()
        relevant_keywords = growth_keywords.get(job_growth_lower, [])
        
        # Check if user goals align with job growth potential
        user_goals_lower = [goal.lower() for goal in user_goals]
        
        matches = sum(1 for keyword in relevant_keywords 
                     if any(keyword in goal or goal in keyword for goal in user_goals_lower))
        
        return min(matches / len(relevant_keywords), 1.0)
    
    def _create_profile_analysis_prompt(self, user_profile: Dict[str, Any]) -> str:
        """Create prompt for user profile analysis"""
        return f"""
        Analyze this user profile and provide insights:

        Profile: {json.dumps(user_profile, indent=2)}

        Please provide a JSON response with:
        {{
            "career_stage": "early|mid|late",
            "skill_strengths": ["strength1", "strength2"],
            "skill_gaps": ["gap1", "gap2"],
            "career_aspirations": ["aspiration1", "aspiration2"],
            "preferred_work_environment": ["env1", "env2"],
            "salary_expectations": "low|medium|high|very_high",
            "location_flexibility": "low|medium|high",
            "growth_priorities": ["priority1", "priority2"]
        }}
        """
    
    def _create_query_expansion_prompt(self, base_query: str, user_profile: Dict[str, Any]) -> str:
        """Create prompt for search query expansion"""
        return f"""
        Expand this job search query based on the user profile:

        Base Query: {base_query}
        User Profile: {json.dumps(user_profile, indent=2)}

        Generate 5-8 related search queries that would help find relevant jobs.
        Consider:
        - Alternative job titles
        - Related skills
        - Industry variations
        - Experience level variations

        Return as a JSON array: ["query1", "query2", "query3"]
        """
    
    def _parse_profile_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for profile analysis"""
        try:
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return self._fallback_profile_analysis({})
        except json.JSONDecodeError:
            return self._fallback_profile_analysis({})
    
    def _parse_expanded_queries(self, response_text: str) -> List[str]:
        """Parse AI response for expanded queries"""
        try:
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return []
        except json.JSONDecodeError:
            return []
    
    def _fallback_profile_analysis(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback profile analysis when AI fails"""
        return {
            'career_stage': 'mid',
            'skill_strengths': user_profile.get('skills', [])[:3],
            'skill_gaps': [],
            'career_aspirations': [],
            'preferred_work_environment': [],
            'salary_expectations': 'medium',
            'location_flexibility': 'medium',
            'growth_priorities': []
        }
    
    def _extract_job_insights(self, job_text: str, job_metadata: Dict) -> Dict[str, Any]:
        """Extract insights from job text using AI"""
        try:
            prompt = f"""
            Extract key insights from this job posting:

            Job Title: {job_metadata.get('title', 'N/A')}
            Company: {job_metadata.get('company', 'N/A')}
            Description: {job_text[:1000]}

            Return JSON with:
            {{
                "skills": ["skill1", "skill2"],
                "experience_level": "junior|mid|senior|lead",
                "culture_indicators": ["indicator1", "indicator2"],
                "growth_potential": "low|medium|high"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            return self._parse_job_insights(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.warning(f"Failed to extract job insights: {e}")
            return {
                'skills': [],
                'experience_level': 'unknown',
                'culture_indicators': [],
                'growth_potential': 'medium'
            }
    
    def _parse_job_insights(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for job insights"""
        try:
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return self._fallback_job_insights()
        except json.JSONDecodeError:
            return self._fallback_job_insights()
    
    def _fallback_job_insights(self) -> Dict[str, Any]:
        """Fallback job insights when AI fails"""
        return {
            'skills': [],
            'experience_level': 'unknown',
            'culture_indicators': [],
            'growth_potential': 'medium'
        }
    
    def _get_ai_ranking(self, top_matches: List[Tuple[Dict, float]], 
                        user_profile: Dict[str, Any]) -> Dict[str, Dict]:
        """Get AI-powered ranking for top matches"""
        try:
            # Create a summary of top matches for AI analysis
            matches_summary = []
            for i, (job, score) in enumerate(top_matches):
                summary = {
                    'id': str(job.get('id', i)),
                    'title': job.get('title', 'Unknown'),
                    'company': job.get('company', 'Unknown'),
                    'matching_score': score,
                    'skills': job.get('skills_extracted', [])[:5]
                }
                matches_summary.append(summary)
            
            prompt = f"""
            Rank these job matches for the user profile:

            User Profile: {json.dumps(user_profile, indent=2)}
            Job Matches: {json.dumps(matches_summary, indent=2)}

            Provide ranking with explanations. Return JSON:
            {{
                "job_id": {{
                    "rank": 1,
                    "explanation": "Why this job is ranked here",
                    "recommendations": ["action1", "action2"]
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            return self._parse_ai_ranking(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error getting AI ranking: {e}")
            return {}
    
    def _parse_ai_ranking(self, response_text: str) -> Dict[str, Dict]:
        """Parse AI response for ranking"""
        try:
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return {}
        except json.JSONDecodeError:
            return {}
    
    def _generate_personalized_insights(self, user_profile: Dict[str, Any], 
                                      ranked_matches: List[Dict]) -> Dict[str, Any]:
        """Generate personalized insights for the user"""
        try:
            # Analyze patterns in top matches
            top_skills = []
            top_companies = []
            salary_ranges = []
            
            for job in ranked_matches[:5]:
                top_skills.extend(job.get('skills_extracted', []))
                top_companies.append(job.get('company', ''))
                if 'salary' in job:
                    salary_ranges.append(job['salary'])
            
            # Count occurrences
            skill_counts = {}
            for skill in top_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            company_counts = {}
            for company in top_companies:
                if company:
                    company_counts[company] = company_counts.get(company, 0) + 1
            
            return {
                'top_matching_skills': sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                'top_matching_companies': sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:3],
                'salary_trend': self._analyze_salary_trend(salary_ranges),
                'skill_gap_analysis': self._analyze_skill_gaps(user_profile.get('skills', []), top_skills),
                'career_advice': self._generate_career_advice(user_profile, ranked_matches)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating personalized insights: {e}")
            return {}
    
    def _analyze_salary_trend(self, salary_ranges: List[str]) -> str:
        """Analyze salary trend from job matches"""
        if not salary_ranges:
            return "insufficient_data"
        
        # Simple analysis - could be enhanced with AI
        high_count = sum(1 for s in salary_ranges if 'high' in s.lower())
        medium_count = sum(1 for s in salary_ranges if 'medium' in s.lower())
        low_count = sum(1 for s in salary_ranges if 'low' in s.lower())
        
        if high_count > medium_count and high_count > low_count:
            return "increasing"
        elif low_count > medium_count and low_count > high_count:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_skill_gaps(self, user_skills: List[str], job_skills: List[str]) -> List[str]:
        """Analyze skill gaps between user and job requirements"""
        user_skills_lower = [skill.lower() for skill in user_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        gaps = []
        for skill in job_skills_lower:
            if skill not in user_skills_lower:
                gaps.append(skill)
        
        return gaps[:5]  # Top 5 gaps
    
    def _generate_career_advice(self, user_profile: Dict[str, Any], 
                               ranked_matches: List[Dict]) -> List[str]:
        """Generate career advice based on matches"""
        advice = []
        
        # Analyze top matches for patterns
        if ranked_matches:
            top_job = ranked_matches[0]
            
            # Skills-based advice
            if 'skills_extracted' in top_job:
                missing_skills = [skill for skill in top_job['skills_extracted'] 
                                if skill.lower() not in [s.lower() for s in user_profile.get('skills', [])]]
                if missing_skills:
                    advice.append(f"Consider developing: {', '.join(missing_skills[:3])}")
            
            # Company-based advice
            if 'company' in top_job:
                advice.append(f"Research {top_job['company']} culture and values")
            
            # Location advice
            if 'location' in top_job:
                advice.append(f"Explore opportunities in {top_job['location']}")
        
        return advice[:3]  # Top 3 pieces of advice
    
    def _get_score_distribution(self, matches: List[Tuple[Dict, float]]) -> Dict[str, float]:
        """Get distribution of matching scores"""
        if not matches:
            return {}
        
        scores = [score for _, score in matches]
        
        return {
            'min_score': min(scores),
            'max_score': max(scores),
            'avg_score': sum(scores) / len(scores),
            'median_score': sorted(scores)[len(scores) // 2]
        }
