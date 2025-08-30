# 🚀 JobPulse Plugin Architecture

## Overview

The JobPulse scraper system has been refactored into a modern, extensible plugin architecture that provides:

- **🔌 Plugin-based scraper management**
- **⚡ Parallel execution and better performance**
- **🛡️ Built-in error handling and retry logic**
- **📊 Comprehensive monitoring and statistics**
- **🔧 Easy configuration and customization**
- **🧹 Automatic resource management**

## 🏗️ Architecture Components

### 1. Base Scraper Interface (`base_scraper.py`)

The foundation of the plugin system. All scrapers must inherit from `BaseScraper` and implement:

```python
from scrapers.base_scraper import BaseScraper, ScraperType

class MyCustomScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="My Custom Scraper",
            scraper_type=ScraperType.WEB_SCRAPER,
            priority=2
        )
    
    def _init_resources(self):
        # Initialize scraper-specific resources
        pass
    
    def search_jobs(self, keyword: str, location: str, limit: int, **kwargs):
        # Implement job search logic
        pass
```

**Key Features:**
- Automatic logging setup
- Status tracking and error handling
- Performance metrics
- Resource cleanup

### 2. Scraper Manager (`scraper_manager.py`)

Coordinates all scrapers and provides a unified interface:

```python
from scrapers.scraper_manager import ScraperManager

# Create manager
manager = ScraperManager(max_workers=5)

# Register scrapers
manager.register_scraper(my_scraper)

# Execute search
results = manager.search_jobs(
    keyword="software engineer",
    location="United States",
    limit=50,
    sources=["enhanced", "api_sources"]
)
```

**Key Features:**
- Parallel scraper execution
- Automatic result aggregation
- Duplicate removal
- Experience level filtering
- Performance tracking

### 3. Plugin Configuration (`plugin_config.py`)

Centralized configuration for all scrapers:

```python
from scrapers.plugin_config import create_default_plugin_loader

# Load all configured scrapers
loader = create_default_plugin_loader()
scrapers = loader.load_scrapers()

# Create manager with loaded scrapers
manager = ScraperManagerFactory.create_manager_with_scrapers(
    list(scrapers.values())
)
```

**Key Features:**
- Declarative scraper configuration
- Priority-based execution order
- Easy enabling/disabling of scrapers
- Configuration overrides

## 🔄 Migration from Old System

### Before (Old System)

```python
# Hardcoded scraper instances
indeed_scraper = IndeedScraper()
linkedin_scraper = LinkedInScraper()
enhanced_scraper = EnhancedPlaywrightScraper()

# Manual execution in search function
if 'enhanced' in sources:
    try:
        enhanced_results = enhanced_scraper.scrape_all_sources(keyword, limit)
        all_jobs.extend(enhanced_results.get('all_sources', []))
        successful_sources += 1
    except Exception as e:
        logger.error(f"Error with enhanced scraper: {e}")

# Repeat for each scraper...
```

### After (New Plugin System)

```python
# Centralized scraper management
plugin_loader = create_default_plugin_loader()
scraper_manager = ScraperManagerFactory.create_manager_with_scrapers(
    plugin_loader.load_scrapers()
)

# Single method call handles all scrapers
results = scraper_manager.search_jobs(
    keyword=keyword,
    location=location,
    limit=limit,
    sources=sources,
    experience_level=experience_level
)
```

## 📊 Scraper Types and Priorities

### Scraper Types

- **`WEB_SCRAPER`**: Traditional web scraping (BeautifulSoup, Selenium)
- **`API_SCRAPER`**: API-based scrapers
- **`PLAYWRIGHT_SCRAPER`**: Playwright-based scrapers
- **`ENHANCED_SCRAPER`**: Enhanced scrapers with anti-detection
- **`FALLBACK_SCRAPER`**: Fallback/mock data scrapers

### Priority Levels

- **Priority 1**: High-priority, reliable scrapers (enhanced, API sources)
- **Priority 2**: Medium-priority scrapers (greenhouse, lever, etc.)
- **Priority 3**: Lower-priority scrapers (indeed, linkedin, etc.)
- **Priority 4-5**: Fallback scrapers (only used when others fail)

## 🛠️ Adding New Scrapers

### Step 1: Create Scraper Class

```python
# scrapers/my_new_scraper.py
from scrapers.base_scraper import BaseScraper, ScraperType

class MyNewScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="My New Scraper",
            scraper_type=ScraperType.API_SCRAPER,
            priority=2
        )
    
    def _init_resources(self):
        # Initialize API client, session, etc.
        self.api_client = MyAPIClient()
    
    def search_jobs(self, keyword: str, location: str, limit: int, **kwargs):
        try:
            # Implement job search logic
            jobs = self.api_client.search(keyword, location, limit)
            
            # Record success
            self.record_success(len(jobs))
            
            return jobs
            
        except Exception as e:
            # Record error
            self.record_error(e)
            raise
```

### Step 2: Add Configuration

```python
# In plugin_config.py, add to DEFAULT_SCRAPER_CONFIGS
"my_new_scraper": ScraperConfig(
    name="My New Scraper",
    class_name="MyNewScraper",
    module_path="scrapers.my_new_scraper",
    scraper_type=ScraperType.API_SCRAPER,
    priority=2,
    config={"api_key": "your_api_key"}
)
```

### Step 3: Use the Scraper

```python
# The scraper will be automatically loaded and available
results = scraper_manager.search_jobs(
    keyword="python developer",
    sources=["enhanced", "my_new_scraper"]  # Include your new scraper
)
```

## 🔧 Configuration and Customization

### Custom Plugin Loader

```python
from scrapers.plugin_config import ScraperConfig, create_custom_plugin_loader

# Create custom configurations
custom_configs = {
    "custom_enhanced": ScraperConfig(
        name="Custom Enhanced",
        class_name="EnhancedPlaywrightScraper",
        module_path="scrapers.enhanced_playwright_scraper",
        scraper_type=ScraperType.ENHANCED_SCRAPER,
        priority=1,
        config={"headless": False, "custom_option": "value"}
    )
}

# Create custom loader
loader = create_custom_plugin_loader(custom_configs)
```

### Dynamic Scraper Management

```python
# Enable/disable scrapers at runtime
loader.enable_scraper("indeed")
loader.disable_scraper("simple")

# Update configurations
loader.update_scraper_config("linkedin", priority=2)

# Get scraper information
enabled_scrapers = loader.get_enabled_scrapers()
api_scrapers = loader.get_scrapers_by_type(ScraperType.API_SCRAPER)
```

## 📈 Monitoring and Statistics

### Scraper Status

```python
# Get individual scraper status
scraper_status = scraper.get_status()
print(f"Success rate: {scraper_status['success_rate']:.1%}")
print(f"Total jobs scraped: {scraper_status['total_jobs_scraped']}")

# Get manager status
manager_status = scraper_manager.get_manager_status()
print(f"Total searches: {manager_status['total_searches']}")
print(f"Average response time: {manager_status['average_response_time']:.2f}s")
```

### Registry Status

```python
# Get registry information
registry_status = scraper_manager.registry.get_registry_status()
print(f"Available scrapers: {registry_status['available_scrapers']}")
print(f"Scrapers by type: {registry_status['scrapers_by_type']}")
```

## 🧪 Testing and Development

### Run Migration Example

```bash
cd scrapers
python -m migration_example
```

### Test Individual Scrapers

```python
from scrapers.plugin_config import create_default_plugin_loader

# Load and test a specific scraper
loader = create_default_plugin_loader()
scraper = loader.load_scraper("enhanced")

# Test the scraper
try:
    jobs = scraper.search_jobs("python developer", "United States", 5)
    print(f"Found {len(jobs)} jobs")
except Exception as e:
    print(f"Error: {e}")
```

## 🚀 Performance Benefits

### Parallel Execution

- **Old System**: Sequential scraper execution
- **New System**: Parallel execution with configurable worker pool

### Resource Management

- **Old System**: Manual resource cleanup
- **New System**: Automatic cleanup with context managers

### Error Handling

- **Old System**: Basic try-catch blocks
- **New System**: Comprehensive error tracking and recovery

## 🔒 Security and Rate Limiting

### Built-in Protection

- Automatic retry logic with exponential backoff
- Rate limiting awareness
- Status tracking for blocked scrapers
- Configurable timeouts and limits

### Anti-Detection

- Rotating user agents
- Browser profile rotation
- Request spacing and randomization
- Proxy support (can be extended)

## 📚 Best Practices

### 1. Error Handling

```python
def search_jobs(self, keyword: str, location: str, limit: int, **kwargs):
    try:
        # Your scraping logic
        jobs = self._scrape_jobs(keyword, location, limit)
        
        # Record success
        self.record_success(len(jobs))
        
        return jobs
        
    except Exception as e:
        # Record error
        self.record_error(e)
        raise
```

### 2. Resource Management

```python
def cleanup(self):
    """Always implement cleanup for resources"""
    if hasattr(self, 'session'):
        self.session.close()
    if hasattr(self, 'browser'):
        self.browser.close()
```

### 3. Configuration

```python
def __init__(self):
    super().__init__(
        name="Descriptive Name",
        scraper_type=ScraperType.APPROPRIATE_TYPE,
        priority=REASONABLE_PRIORITY
    )
```

## 🔮 Future Enhancements

### Planned Features

- **Plugin Hot-Reloading**: Update scrapers without restarting
- **Advanced Metrics**: Detailed performance analytics
- **Machine Learning**: Intelligent scraper selection
- **Distributed Execution**: Multi-server scraper coordination
- **Plugin Marketplace**: Community-contributed scrapers

### Extension Points

- **Custom Scraper Types**: Define new scraper categories
- **Advanced Filtering**: Custom job filtering logic
- **Data Transformers**: Custom data processing pipelines
- **Notification Systems**: Alert on scraper failures

## 🤝 Contributing

### Adding New Scrapers

1. Create scraper class implementing `BaseScraper`
2. Add configuration to `plugin_config.py`
3. Test thoroughly with various inputs
4. Update documentation
5. Submit pull request

### Improving Existing Scrapers

1. Identify areas for improvement
2. Implement changes while maintaining interface
3. Add tests for new functionality
4. Update configuration if needed
5. Document changes

## 📞 Support

For questions or issues with the plugin architecture:

1. Check the migration example (`migration_example.py`)
2. Review the base scraper implementation
3. Look at existing scraper examples
4. Create an issue with detailed description

---

**🎉 Welcome to the future of JobPulse scraping!** The new plugin architecture makes it easier than ever to add, configure, and manage scrapers while providing better performance and reliability.
