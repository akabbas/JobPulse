from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class Job(db.Model):
    """Job table to store job postings from various sources"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    description = db.Column(db.Text)
    skills = db.Column(db.Text)  # Comma-separated list of skills
    source = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500))
    date_posted = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'
    
    def to_dict(self):
        """Convert job object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'skills': self.skills,
            'source': self.source,
            'url': self.url,
            'date_posted': self.date_posted.isoformat() if self.date_posted else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Search(db.Model):
    """Search table to track user searches and results"""
    __tablename__ = 'searches'
    
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    result_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Search {self.keyword} in {self.location}>'
    
    def to_dict(self):
        """Convert search object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'keyword': self.keyword,
            'location': self.location,
            'result_count': self.result_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
