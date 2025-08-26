import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import logging

class SkillTrendsAnalyzer:
    def __init__(self):
        self.setup_logging()
        self.setup_plotting()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/skill_analysis.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_plotting(self):
        plt.style.use('default')
        sns.set_palette("husl")
    
    def analyze_skill_frequency(self, df: pd.DataFrame) -> Dict[str, List[Tuple[str, float]]]:
        """
        Analyze skill frequency across all jobs
        Returns: Dict with category names as keys and list of (skill, percentage) tuples as values
        """
        if df.empty or 'skills' not in df.columns:
            self.logger.warning("No skills data available")
            return {}
        
        # Flatten all skills
        all_skills = []
        for skills in df['skills']:
            if isinstance(skills, list):
                all_skills.extend(skills)
            elif isinstance(skills, str):
                # Handle case where skills might be a string
                skills_list = [s.strip() for s in skills.split(',') if s.strip()]
                all_skills.extend(skills_list)
        
        if not all_skills:
            self.logger.warning("No skills found in job data")
            return {}
        
        # Count skills
        skill_counts = Counter(all_skills)
        
        # Calculate percentages
        total_jobs = len(df)
        skill_percentages = {skill: (count / total_jobs) * 100 for skill, count in skill_counts.items()}
        
        # Group by category
        skill_categories = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud_platforms': [],
            'data_tools': [],
            'testing_tools': [],
            'monitoring_tools': [],
            'version_control': [],
            'ides_editors': [],
            'mobile_development': [],
            'game_development': [],
            'blockchain': [],
            'ai_ml_tools': []
        }
        
        # Map skills to categories
        for skill, percentage in skill_percentages.items():
            skill_lower = skill.lower()
            
            # Check each category
            if skill_lower in [s.lower() for s in self._programming_languages]:
                skill_categories['programming_languages'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._frameworks]:
                skill_categories['frameworks'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._databases]:
                skill_categories['databases'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._cloud_platforms]:
                skill_categories['cloud_platforms'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._data_tools]:
                skill_categories['data_tools'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._testing_tools]:
                skill_categories['testing_tools'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._monitoring_tools]:
                skill_categories['monitoring_tools'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._version_control]:
                skill_categories['version_control'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._ides_editors]:
                skill_categories['ides_editors'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._mobile_development]:
                skill_categories['mobile_development'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._game_development]:
                skill_categories['game_development'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._blockchain]:
                skill_categories['blockchain'].append((skill, percentage))
            elif skill_lower in [s.lower() for s in self._ai_ml_tools]:
                skill_categories['ai_ml_tools'].append((skill, percentage))
        
        # Sort each category by percentage (highest first)
        for category in skill_categories:
            skill_categories[category].sort(key=lambda x: x[1], reverse=True)
        
        # Remove empty categories
        skill_categories = {k: v for k, v in skill_categories.items() if v}
        
        self.logger.info(f"Analyzed {len(all_skills)} skills across {total_jobs} jobs")
        return skill_categories
    
    def analyze_skill_combinations(self, df: pd.DataFrame, top_n: int = 10) -> List[Tuple]:
        """
        Find most common skill combinations
        """
        skill_combinations = []
        
        for skills in df['skills']:
            if len(skills) >= 2:
                # Sort skills to ensure consistent combinations
                sorted_skills = tuple(sorted(skills))
                skill_combinations.append(sorted_skills)
        
        combination_counts = Counter(skill_combinations)
        return combination_counts.most_common(top_n)
    
    def analyze_skills_by_job_type(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Analyze skills distribution by job type
        """
        job_types = df['job_type'].unique()
        skill_analysis = {}
        
        for job_type in job_types:
            job_df = df[df['job_type'] == job_type]
            
            # Get skills for this job type
            all_skills = []
            for skills in job_df['skills']:
                all_skills.extend(skills)
            
            skill_counts = Counter(all_skills)
            total_jobs = len(job_df)
            
            skill_percentages = {skill: (count / total_jobs) * 100 
                               for skill, count in skill_counts.items()}
            
            skill_analysis[job_type] = skill_percentages
        
        return skill_analysis
    
    def create_skill_visualizations(self, df: pd.DataFrame, output_dir: str = 'output'):
        """
        Create comprehensive skill analysis visualizations
        """
        # 1. Top skills overall
        skill_freq = self.analyze_skill_frequency(df)
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Software Engineering Skills Analysis', fontsize=16, fontweight='bold')
        
        # Plot each category
        categories = list(skill_freq.keys())
        for i, category in enumerate(categories):
            if i < 6:  # We have 6 subplot positions
                row = i // 3
                col = i % 3
                
                skills_data = skill_freq[category][:10]  # Top 10
                if skills_data:
                    skills, percentages = zip(*skills_data)
                    axes[row, col].barh(range(len(skills)), percentages)
                    axes[row, col].set_yticks(range(len(skills)))
                    axes[row, col].set_yticklabels(skills)
                    axes[row, col].set_title(f'{category.replace("_", " ").title()}')
                    axes[row, col].set_xlabel('Percentage of Jobs')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/skill_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Skills by job type
        job_type_skills = self.analyze_skills_by_job_type(df)
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Skills by Job Type', fontsize=16, fontweight='bold')
        
        job_types = list(job_type_skills.keys())
        for i, job_type in enumerate(job_types):
            if i < 6:
                row = i // 3
                col = i % 3
                
                skills_data = sorted(job_type_skills[job_type].items(), 
                                   key=lambda x: x[1], reverse=True)[:8]
                if skills_data:
                    skills, percentages = zip(*skills_data)
                    axes[row, col].barh(range(len(skills)), percentages)
                    axes[row, col].set_yticks(range(len(skills)))
                    axes[row, col].set_yticklabels(skills)
                    axes[row, col].set_title(job_type)
                    axes[row, col].set_xlabel('Percentage')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/skills_by_job_type.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info("Skill visualizations created successfully")
    
    # Skill category definitions
    _programming_languages = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
        'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'haskell',
        'clojure', 'elixir', 'dart', 'cobol', 'fortran', 'assembly', 'bash', 'powershell'
    ]
    
    _frameworks = [
        'react', 'angular', 'vue.js', 'node.js', 'express', 'django', 'flask',
        'spring', 'laravel', 'ruby on rails', 'asp.net', 'fastapi', 'gin', 'echo',
        'next.js', 'nuxt.js', 'svelte', 'ember.js', 'backbone.js', 'jquery',
        'bootstrap', 'tailwind css', 'material-ui', 'ant design', 'chakra ui'
    ]
    
    _databases = [
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb',
        'snowflake', 'bigquery', 'redshift', 'cassandra', 'neo4j', 'sqlite',
        'oracle', 'sql server', 'mariadb', 'couchdb', 'influxdb', 'timescaledb'
    ]
    
    _cloud_platforms = [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
        'gitlab', 'github actions', 'circleci', 'travis ci', 'bamboo', 'teamcity',
        'ansible', 'chef', 'puppet', 'salt', 'helm', 'istio', 'linkerd'
    ]
    
    _data_tools = [
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'spark',
        'hadoop', 'kafka', 'airflow', 'dbt', 'tableau', 'powerbi', 'looker',
        'jupyter', 'zeppelin', 'databricks', 'snowflake', 'redshift', 'bigquery',
        'apache beam', 'flink', 'storm', 'hive', 'pig', 'sqoop', 'oozie'
    ]
    
    _testing_tools = [
        'jest', 'mocha', 'jasmine', 'cypress', 'selenium', 'playwright',
        'pytest', 'unittest', 'junit', 'testng', 'mockito', 'wiremock',
        'postman', 'insomnia', 'soapui', 'jmeter', 'gatling', 'artillery'
    ]
    
    _monitoring_tools = [
        'prometheus', 'grafana', 'datadog', 'new relic', 'splunk', 'elk stack',
        'elasticsearch', 'logstash', 'kibana', 'jaeger', 'zipkin', 'opentelemetry',
        'nagios', 'zabbix', 'icinga', 'sensu', 'cloudwatch', 'stackdriver'
    ]
    
    _version_control = [
        'git', 'svn', 'mercurial', 'github', 'gitlab', 'bitbucket', 'azure devops',
        'gerrit', 'gitea', 'gogs', 'gitkraken', 'sourcetree', 'tortoisegit'
    ]
    
    _ides_editors = [
        'vscode', 'intellij', 'eclipse', 'vim', 'emacs', 'sublime text',
        'atom', 'brackets', 'notepad++', 'webstorm', 'pycharm', 'android studio',
        'xcode', 'visual studio', 'rider', 'phpstorm', 'datagrip'
    ]
    
    _mobile_development = [
        'react native', 'flutter', 'xamarin', 'ionic', 'cordova', 'phonegap',
        'swift', 'kotlin', 'java', 'objective-c', 'dart', 'typescript'
    ]
    
    _game_development = [
        'unity', 'unreal engine', 'godot', 'cocos2d', 'phaser', 'three.js',
        'babylon.js', 'playcanvas', 'construct', 'game maker', 'rpg maker'
    ]
    
    _blockchain = [
        'ethereum', 'bitcoin', 'solidity', 'web3.js', 'truffle', 'hardhat',
        'metamask', 'ipfs', 'hyperledger', 'corda', 'polkadot', 'cosmos'
    ]
    
    _ai_ml_tools = [
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'opencv', 'nltk',
        'spacy', 'transformers', 'hugging face', 'fastai', 'xgboost', 'lightgbm',
        'catboost', 'mlflow', 'kubeflow', 'sagemaker', 'vertex ai', 'azure ml'
    ] 