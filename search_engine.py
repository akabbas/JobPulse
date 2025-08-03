from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class SearchCriteria:
    keywords: List[str] = field(default_factory=list)
    location: Optional[str] = None
    job_level: Optional[str] = None
    job_type: Optional[str] = None
    skills_required: Optional[List[str]] = field(default_factory=list)
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None

def filter_jobs(jobs: List[Dict], criteria: SearchCriteria) -> List[Dict]:
    filtered = []
    for job in jobs:
        # Keyword match
        if criteria.keywords and not any(k.lower() in job['title'].lower() for k in criteria.keywords):
            continue
        # Location match
        if criteria.location and criteria.location.lower() not in job['location'].lower():
            continue
        # Skills required
        if criteria.skills_required and not all(s.lower() in [sk.lower() for sk in job['skills']] for s in criteria.skills_required):
            continue
        # Salary min
        if criteria.salary_min and job.get('salary_min') and job['salary_min'] < criteria.salary_min:
            continue
        # Salary max
        if criteria.salary_max and job.get('salary_max') and job['salary_max'] > criteria.salary_max:
            continue
        filtered.append(job)
    return filtered 