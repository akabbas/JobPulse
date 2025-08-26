from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime
import re

app = Flask(__name__)

# Simple in-memory storage for demo purposes
jobs_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('keyword', '')
        location = data.get('location', 'United States')
        
        # Simulate job search results
        mock_jobs = [
            {
                'title': f'Software Engineer - {query}',
                'company': 'Tech Corp',
                'location': location,
                'snippet': f'Looking for a {query} developer with experience in modern web technologies.',
                'salary': '$80,000 - $120,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Mock Data',
                'job_url': '#',
                'skills': ['Python', 'JavaScript', 'React', 'Node.js']
            },
            {
                'title': f'Senior {query} Developer',
                'company': 'Innovation Inc',
                'location': location,
                'snippet': f'Join our team as a senior {query} developer and help build amazing products.',
                'salary': '$120,000 - $180,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Mock Data',
                'job_url': '#',
                'skills': ['Python', 'Django', 'PostgreSQL', 'AWS']
            },
            {
                'title': f'Full Stack {query} Engineer',
                'company': 'Future Tech',
                'location': location,
                'snippet': f'Build scalable applications using {query} and modern cloud technologies.',
                'salary': '$100,000 - $150,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Mock Data',
                'job_url': '#',
                'skills': ['Python', 'Flask', 'MongoDB', 'Docker']
            }
        ]
        
        return jsonify({
            'success': True,
            'jobs': mock_jobs,
            'total_jobs': len(mock_jobs),
            'successful_sources': 1,
            'query': query,
            'location': location
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/enhanced_search', methods=['POST'])
def enhanced_search():
    try:
        data = request.get_json()
        query = data.get('keyword', '')
        
        # Enhanced search with more detailed results
        enhanced_jobs = [
            {
                'title': f'Full Stack {query} Engineer',
                'company': 'Future Tech',
                'location': 'New York, NY',
                'snippet': f'Build scalable applications using {query} and modern cloud technologies.',
                'salary': '$100,000 - $150,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Enhanced Search',
                'job_url': '#',
                'skills': ['Python', 'JavaScript', 'Cloud', 'API Design'],
                'experience': '3-5 years'
            },
            {
                'title': f'Lead {query} Developer',
                'company': 'Digital Solutions',
                'location': 'Austin, TX',
                'snippet': f'Lead a team of developers building innovative {query} solutions.',
                'salary': '$130,000 - $200,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Enhanced Search',
                'job_url': '#',
                'skills': ['Leadership', 'Architecture', 'Team Management'],
                'experience': '5+ years'
            },
            {
                'title': f'AI {query} Engineer',
                'company': 'AI Innovations',
                'location': 'San Francisco, CA',
                'snippet': f'Work on cutting-edge AI projects using {query} and machine learning.',
                'salary': '$150,000 - $250,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Enhanced Search',
                'job_url': '#',
                'skills': ['Python', 'TensorFlow', 'PyTorch', 'ML'],
                'experience': '4+ years'
            }
        ]
        
        return jsonify({
            'success': True,
            'jobs': enhanced_jobs,
            'total_jobs': len(enhanced_jobs),
            'scraping_method': 'Playwright Enhanced Scraper',
            'source_breakdown': {'Enhanced': len(enhanced_jobs)},
            'enhanced': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_skills():
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])
        
        if not jobs:
            return jsonify({
                'success': False,
                'error': 'No jobs provided for analysis'
            }), 400
        
        # Simple skills analysis
        all_skills = []
        for job in jobs:
            if 'skills' in job and job['skills']:
                all_skills.extend(job['skills'])
        
        # Count skill occurrences
        skill_counts = {}
        for skill in all_skills:
            skill_lower = skill.lower().strip()
            if skill_lower:
                skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
        
        # Calculate percentages
        total_jobs = len(jobs)
        skill_percentages = {}
        for skill, count in skill_counts.items():
            percentage = (count / total_jobs) * 100
            skill_percentages[skill] = percentage
        
        # Categorize skills
        skill_categories = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud_platforms': [],
            'tools': []
        }
        
        # Simple categorization logic
        for skill, percentage in skill_percentages.items():
            if any(lang in skill.lower() for lang in ['python', 'javascript', 'java', 'c++', 'go', 'rust']):
                skill_categories['programming_languages'].append([skill, percentage])
            elif any(fw in skill.lower() for fw in ['react', 'angular', 'vue', 'django', 'flask', 'spring']):
                skill_categories['frameworks'].append([skill, percentage])
            elif any(db in skill.lower() for db in ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch']):
                skill_categories['databases'].append([skill, percentage])
            elif any(cloud in skill.lower() for cloud in ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes']):
                skill_categories['cloud_platforms'].append([skill, percentage])
            else:
                skill_categories['tools'].append([skill, percentage])
        
        # Sort each category by percentage
        for category in skill_categories:
            skill_categories[category].sort(key=lambda x: x[1], reverse=True)
        
        return jsonify({
            'success': True,
            'skill_analysis': skill_categories,
            'total_jobs_analyzed': total_jobs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/filter', methods=['POST'])
def filter_jobs():
    try:
        data = request.get_json()
        jobs = data.get('jobs', [])
        criteria = data.get('criteria', {})
        
        if not jobs:
            return jsonify({
                'success': False,
                'error': 'No jobs provided for filtering'
            }), 400
        
        filtered_jobs = jobs.copy()
        
        # Filter by required skills
        required_skills = criteria.get('skills_required', [])
        if required_skills:
            filtered_jobs = [
                job for job in filtered_jobs
                if 'skills' in job and job['skills'] and
                any(skill.lower() in [s.lower() for s in job['skills']] 
                    for skill in required_skills)
            ]
        
        # Filter by minimum salary (if available)
        salary_min = criteria.get('salary_min')
        if salary_min:
            filtered_jobs = [
                job for job in filtered_jobs
                if 'salary' in job and job['salary'] and
                extract_salary(job['salary']) >= salary_min
            ]
        
        return jsonify({
            'success': True,
            'filtered_jobs': filtered_jobs,
            'total_filtered': len(filtered_jobs),
            'original_total': len(jobs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def extract_salary(salary_str):
    """Extract numeric salary from salary string"""
    if not salary_str:
        return 0
    
    # Look for numbers in the salary string
    numbers = re.findall(r'\d+', salary_str)
    if numbers:
        # Return the first number found (usually the minimum)
        return int(numbers[0])
    return 0

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app': 'JobPulse Dashboard'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
