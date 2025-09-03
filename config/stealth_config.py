#!/usr/bin/env python3
"""
Configuration file for stealth scraper settings
"""

# Proxy Configuration
PROXY_CONFIG = {
    'enabled': False,  # Set to True to enable proxy rotation
    'proxy_list': [
        # Add your proxy servers here
        # Format: "protocol://user:pass@host:port" or "protocol://host:port"
        # Examples:
        # "http://username:password@proxy1.example.com:8080",
        # "socks5://proxy2.example.com:1080",
        # "https://proxy3.example.com:3128"
    ],
    'rotation_strategy': 'round_robin',  # 'round_robin', 'random', 'failover'
    'max_failures': 3,  # Max consecutive failures before switching proxy
    'timeout': 30,  # Proxy timeout in seconds
}

# Stealth Configuration
STEALTH_CONFIG = {
    'browser': {
        'headless': False,  # Set to True for production
        'slow_mo': 100,  # Slow down operations to appear more human
        'devtools': False,  # Disable dev tools to avoid detection
    },
    'viewport': {
        'min_width': 1200,
        'max_width': 1920,
        'min_height': 800,
        'max_height': 1080,
    },
    'user_agents': {
        'rotation_enabled': True,
        'custom_agents': [
            # Add custom user agents if needed
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
    },
    'human_behavior': {
        'min_delay': 2.0,  # Minimum delay between actions
        'max_delay': 8.0,  # Maximum delay between actions
        'mouse_movement_probability': 0.7,  # Probability of random mouse movements
        'scroll_probability': 0.6,  # Probability of random scrolling
        'typing_variance': 0.3,  # Variance in typing speed
        'page_load_wait': 'networkidle',  # Wait strategy: 'load', 'domcontentloaded', 'networkidle'
    },
    'anti_detection': {
        'webdriver_evasion': True,  # Hide webdriver properties
        'navigator_evasion': True,  # Fake navigator properties
        'permissions_evasion': True,  # Fake permissions
        'chrome_evasion': True,  # Fake Chrome runtime
        'automation_evasion': True,  # Hide automation indicators
    }
}

# Indeed-specific Configuration
INDEED_CONFIG = {
    'search': {
        'max_pages': 10,  # Maximum pages to scrape
        'jobs_per_page': 15,  # Jobs per page (Indeed default)
        'max_retries': 3,  # Max retries for failed requests
        'retry_delay': 5,  # Delay between retries in seconds
    },
    'selectors': {
        'job_cards': 'div.job_seen_beacon',
        'job_title': 'h2.jobTitle',
        'company_name': 'span[data-testid="company-name"]',
        'location': 'div[data-testid="text-location"]',
        'job_link': 'a.jcs-JobTitle',
        'job_snippet': 'div.job-snippet',
        'salary': 'div.metadata.salary-snippet-container',
    },
    'blocking_indicators': [
        '//h1[contains(text(), "Access Denied")]',
        '//h1[contains(text(), "Blocked")]',
        '//h1[contains(text(), "Forbidden")]',
        '//div[contains(text(), "CAPTCHA")]',
        '//div[contains(text(), "verify you are human")]',
        '//iframe[contains(@src, "captcha")]',
        '//div[contains(text(), "unusual traffic")]',
        '//div[contains(text(), "rate limit")]',
    ]
}

# Rate Limiting Configuration
RATE_LIMITING = {
    'enabled': True,
    'requests_per_minute': 10,  # Max requests per minute
    'requests_per_hour': 100,   # Max requests per hour
    'burst_limit': 5,           # Max requests in burst
    'cooldown_period': 60,      # Cooldown period in seconds after burst
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'file': 'logs/stealth_scraper.log',
    'max_file_size': '10MB',
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'max_concurrent_browsers': 2,  # Max concurrent browser instances
    'browser_timeout': 60000,      # Browser timeout in milliseconds
    'page_timeout': 30000,         # Page timeout in milliseconds
    'navigation_timeout': 60000,   # Navigation timeout in milliseconds
    'resource_timeout': 30000,     # Resource loading timeout
}

# Advanced Stealth Techniques
ADVANCED_STEALTH = {
    'canvas_fingerprinting': True,     # Randomize canvas fingerprint
    'webgl_fingerprinting': True,     # Randomize WebGL fingerprint
    'audio_fingerprinting': True,     # Randomize audio fingerprint
    'font_fingerprinting': True,      # Randomize font fingerprint
    'battery_api': True,              # Fake battery API
    'connection_api': True,           # Fake connection API
    'hardware_concurrency': True,     # Fake hardware concurrency
    'device_memory': True,            # Fake device memory
    'platform': True,                 # Fake platform
    'vendor': True,                   # Fake vendor
}

# Browser Arguments for Stealth
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--disable-extensions',
    '--no-first-run',
    '--disable-default-apps',
    '--disable-popup-blocking',
    '--disable-notifications',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-features=TranslateUI',
    '--disable-ipc-flooding-protection',
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--disable-blink-features',
    '--disable-webgl',
    '--disable-canvas-aa',
    '--disable-2d-canvas-clip-aa',
    '--disable-gl-drawing-for-tests',
    '--disable-accelerated-2d-canvas',
    '--no-zygote',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-background-networking',
    '--disable-sync',
    '--disable-translate',
    '--hide-scrollbars',
    '--mute-audio',
    '--no-default-browser-check',
    '--no-pings',
    '--no-validate-ssl',
    '--disable-hang-monitor',
    '--disable-prompt-on-repost',
    '--disable-client-side-phishing-detection',
    '--disable-component-update',
    '--disable-domain-reliability',
    '--disable-features=AudioServiceOutOfProcess',
    '--disable-ipc-flooding-protection',
    '--disable-renderer-backgrounding',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-features=TranslateUI',
    '--disable-features=VizDisplayCompositor',
    '--disable-ipc-flooding-protection',
    '--disable-renderer-backgrounding',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-features=TranslateUI',
    '--disable-features=VizDisplayCompositor'
]

# HTTP Headers for Stealth
STEALTH_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
