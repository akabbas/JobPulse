import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///job_market.db')

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}

# Alternative headers for different sites
ALTERNATIVE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Mobile headers for some sites
MOBILE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

# Job Search Parameters
SEARCH_KEYWORDS = [
    'software engineer',
    'software developer',
    'full stack developer',
    'backend developer',
    'frontend developer',
    'data engineer',
    'devops engineer',
    'machine learning engineer'
]

# Skills to Track
TECH_SKILLS = {
    'programming_languages': [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
        'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'haskell',
        'clojure', 'elixir', 'dart', 'cobol', 'fortran', 'assembly', 'bash', 'powershell'
    ],
    'frameworks': [
        'react', 'angular', 'vue.js', 'node.js', 'express', 'django', 'flask',
        'spring', 'laravel', 'ruby on rails', 'asp.net', 'fastapi', 'gin', 'echo',
        'next.js', 'nuxt.js', 'svelte', 'ember.js', 'backbone.js', 'jquery',
        'bootstrap', 'tailwind css', 'material-ui', 'ant design', 'chakra ui'
    ],
    'databases': [
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb',
        'snowflake', 'bigquery', 'redshift', 'cassandra', 'neo4j', 'sqlite',
        'oracle', 'sql server', 'mariadb', 'couchdb', 'influxdb', 'timescaledb'
    ],
    'cloud_platforms': [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
        'gitlab', 'github actions', 'circleci', 'travis ci', 'bamboo', 'teamcity',
        'ansible', 'chef', 'puppet', 'salt', 'helm', 'istio', 'linkerd'
    ],
    'data_tools': [
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'spark',
        'hadoop', 'kafka', 'airflow', 'dbt', 'tableau', 'powerbi', 'looker',
        'jupyter', 'zeppelin', 'databricks', 'snowflake', 'redshift', 'bigquery',
        'apache beam', 'flink', 'storm', 'hive', 'pig', 'sqoop', 'oozie'
    ],
    'testing_tools': [
        'jest', 'mocha', 'jasmine', 'cypress', 'selenium', 'playwright',
        'pytest', 'unittest', 'junit', 'testng', 'mockito', 'wiremock',
        'postman', 'insomnia', 'soapui', 'jmeter', 'gatling', 'artillery'
    ],
    'monitoring_tools': [
        'prometheus', 'grafana', 'datadog', 'new relic', 'splunk', 'elk stack',
        'elasticsearch', 'logstash', 'kibana', 'jaeger', 'zipkin', 'opentelemetry',
        'nagios', 'zabbix', 'icinga', 'sensu', 'cloudwatch', 'stackdriver'
    ],
    'version_control': [
        'git', 'svn', 'mercurial', 'github', 'gitlab', 'bitbucket', 'azure devops',
        'gerrit', 'gitea', 'gogs', 'gitkraken', 'sourcetree', 'tortoisegit'
    ],
    'ides_editors': [
        'vscode', 'intellij', 'eclipse', 'vim', 'emacs', 'sublime text',
        'atom', 'brackets', 'notepad++', 'webstorm', 'pycharm', 'android studio',
        'xcode', 'visual studio', 'rider', 'phpstorm', 'datagrip'
    ],
    'mobile_development': [
        'react native', 'flutter', 'xamarin', 'ionic', 'cordova', 'phonegap',
        'swift', 'kotlin', 'java', 'objective-c', 'dart', 'typescript'
    ],
    'game_development': [
        'unity', 'unreal engine', 'godot', 'cocos2d', 'phaser', 'three.js',
        'babylon.js', 'playcanvas', 'construct', 'game maker', 'rpg maker'
    ],
    'blockchain': [
        'ethereum', 'bitcoin', 'solidity', 'web3.js', 'truffle', 'hardhat',
        'metamask', 'ipfs', 'hyperledger', 'corda', 'polkadot', 'cosmos'
    ],
    'ai_ml_tools': [
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'opencv', 'nltk',
        'spacy', 'transformers', 'hugging face', 'fastai', 'xgboost', 'lightgbm',
        'catboost', 'mlflow', 'kubeflow', 'sagemaker', 'vertex ai', 'azure ml'
    ]
}

# Scraping Delays (in seconds)
DELAY_BETWEEN_REQUESTS = 2
DELAY_BETWEEN_PAGES = 5

# Output Configuration
OUTPUT_DIR = 'output'
LOG_DIR = 'logs' 