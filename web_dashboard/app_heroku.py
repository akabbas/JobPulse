from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

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
        query = data.get('query', '')
        location = data.get('location', '')
        
        # Simulate job search results
        mock_jobs = [
            {
                'title': f'Software Engineer - {query}',
                'company': 'Tech Corp',
                'location': location or 'Remote',
                'description': f'Looking for a {query} developer with experience in modern web technologies.',
                'salary': '$80,000 - $120,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Mock Data'
            },
            {
                'title': f'Senior {query} Developer',
                'company': 'Innovation Inc',
                'location': location or 'San Francisco, CA',
                'description': f'Join our team as a senior {query} developer and help build amazing products.',
                'salary': '$120,000 - $180,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Mock Data'
            }
        ]
        
        return jsonify({
            'success': True,
            'jobs': mock_jobs,
            'total': len(mock_jobs),
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
        query = data.get('query', '')
        location = data.get('location', '')
        
        # Enhanced search with more detailed results
        enhanced_jobs = [
            {
                'title': f'Full Stack {query} Engineer',
                'company': 'Future Tech',
                'location': location or 'New York, NY',
                'description': f'Build scalable applications using {query} and modern cloud technologies.',
                'salary': '$100,000 - $150,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Enhanced Search',
                'skills': ['Python', 'JavaScript', 'Cloud', 'API Design'],
                'experience': '3-5 years'
            },
            {
                'title': f'Lead {query} Developer',
                'company': 'Digital Solutions',
                'location': location or 'Austin, TX',
                'description': f'Lead a team of developers building innovative {query} solutions.',
                'salary': '$130,000 - $200,000',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Enhanced Search',
                'skills': ['Leadership', 'Architecture', 'Team Management'],
                'experience': '5+ years'
            }
        ]
        
        return jsonify({
            'success': True,
            'jobs': enhanced_jobs,
            'total': len(enhanced_jobs),
            'query': query,
            'location': location,
            'enhanced': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
