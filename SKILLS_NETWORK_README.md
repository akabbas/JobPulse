# 🚀 JobPulse Skills Network Visualization

A powerful interactive visualization that shows relationships between skills in the job market. This feature demonstrates advanced data analysis and visualization capabilities using the vis-network library.

## ✨ Features

- **Interactive Network Graph**: Visual representation of skill relationships
- **AI-Powered Skill Extraction**: Uses your existing AI analyzer to extract skills from job descriptions
- **Real-time Filtering**: Filter skills by frequency and co-occurrence thresholds
- **Professional UI**: Clean, responsive design with dark mode support
- **API Integration**: RESTful endpoints for programmatic access
- **Statistics Dashboard**: Real-time metrics and insights

## 🛠️ Setup Instructions

### 1. Install Dependencies

The skills network visualization uses the `vis-network` library. Make sure it's included in your HTML:

```html
<!-- Include vis-network library -->
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>

<!-- Include custom styles and scripts -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/skillsNetwork.css') }}">
<script src="{{ url_for('static', filename='js/skillsNetwork.js') }}"></script>
```

### 2. Add the Container

Add this HTML element where you want the visualization to appear:

```html
<div id="skills-network"></div>
```

### 3. Initialize the Visualization

The visualization will automatically initialize when the page loads, or you can manually initialize it:

```javascript
// Auto-initialization (already included)
// The visualization will start automatically when the DOM is ready

// Manual initialization
const skillsNetwork = initializeSkillsNetwork('skills-network');
```

## 🌐 API Endpoints

### GET `/api/skills-network`

Returns skills and their co-occurrences formatted for the vis-network library.

**Query Parameters:**
- `min_frequency` (int): Minimum skill frequency (default: 2)
- `min_co_occurrence` (int): Minimum co-occurrence count (default: 1)
- `keyword` (string): Filter by job keyword (optional)
- `location` (string): Filter by location (optional)

**Response Format:**
```json
{
  "success": true,
  "data": {
    "skills": {
      "Python": 8,
      "React": 6,
      "AWS": 5,
      "Docker": 4
    },
    "co_occurrences": {
      "Python|React": 3,
      "Python|AWS": 2,
      "React|Docker": 2
    },
    "total_jobs_analyzed": 8,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### GET `/api/skills-network/stats`

Returns metadata about the skills network API.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_endpoints": 2,
    "available_filters": ["keyword", "location", "min_frequency", "min_co_occurrence"],
    "data_sources": ["sample_data", "ai_analysis"],
    "last_updated": "2024-01-15T10:30:00",
    "version": "1.0.0"
  }
}
```

## 🎯 Demo Page

Visit `/skills-network` to see the complete demo with:
- Interactive controls for filtering
- Real-time statistics
- User instructions
- Sample data visualization

## 🔧 Integration with Your Existing Code

### 1. Replace Sample Data

The current implementation uses sample data. To integrate with your real job data:

```python
# In your Flask app, replace the sample_jobs list with:
@app.route('/api/skills-network')
def get_skills_network():
    try:
        # Get real job data from your scrapers or database
        real_jobs = get_jobs_from_database()  # Your function here
        
        # Or use recent search results
        real_jobs = get_recent_job_searches()  # Your function here
        
        # Process the real jobs...
        
    except Exception as e:
        # Error handling...
```

### 2. Use Your Existing Skill Extraction

The API already integrates with your `AIJobAnalyzer`:

```python
# AI skill extraction is automatically used when available
if ai_analyzer and job.get('description'):
    ai_analysis = ai_analyzer.analyze_job_description(
        job['description'], 
        {'title': job.get('title', '')}
    )
    
    if ai_analysis.get('success') and 'skills' in ai_analysis.get('analysis', {}):
        extracted_skills = ai_analysis['analysis']['skills']
        # Use AI-extracted skills...
```

### 3. Database Integration

To use a database instead of in-memory data:

```python
# Example with SQLAlchemy
from your_database import Job, db

@app.route('/api/skills-network')
def get_skills_network():
    try:
        # Query your database
        jobs = Job.query.filter(
            Job.created_at >= datetime.now() - timedelta(days=30)
        ).limit(1000).all()
        
        # Convert to the expected format
        job_data = []
        for job in jobs:
            job_data.append({
                'title': job.title,
                'description': job.description,
                'skills': job.skills.split(',') if job.skills else []
            })
        
        # Process the job data...
        
    except Exception as e:
        # Error handling...
```

## 🎨 Customization

### 1. Styling

Modify `web_dashboard/static/css/skillsNetwork.css` to customize:
- Colors and themes
- Node and edge appearance
- Layout and spacing
- Responsive breakpoints

### 2. Behavior

Modify `web_dashboard/static/js/skillsNetwork.js` to customize:
- Network physics settings
- Interaction behaviors
- Data processing logic
- Event handling

### 3. Data Processing

Modify the Flask endpoint to customize:
- Skill extraction algorithms
- Filtering logic
- Data aggregation methods
- Response format

## 🧪 Testing

Use the included test script to verify everything works:

```bash
# Make sure your Flask app is running
python web_dashboard/app.py

# In another terminal, run the test
python test_skills_network_api.py
```

## 🚀 Production Considerations

### 1. Performance

- **Caching**: Cache skills network data to avoid recalculating
- **Database Indexing**: Index job skills and descriptions for faster queries
- **Background Processing**: Use Celery or similar for heavy skill analysis

### 2. Scalability

- **Data Limits**: Limit the number of jobs analyzed per request
- **Pagination**: Implement pagination for large skill networks
- **CDN**: Serve static assets from a CDN

### 3. Security

- **Rate Limiting**: Implement API rate limiting
- **Input Validation**: Validate all query parameters
- **Error Handling**: Don't expose internal errors to users

## 🔍 Troubleshooting

### Common Issues

1. **Visualization Not Loading**
   - Check browser console for JavaScript errors
   - Verify vis-network library is loaded
   - Check that the container element exists

2. **No Data Displayed**
   - Verify the API endpoint returns data
   - Check network tab for API errors
   - Ensure skills data is properly formatted

3. **Performance Issues**
   - Reduce the number of skills/connections
   - Increase minimum frequency thresholds
   - Implement data caching

### Debug Mode

Enable debug logging in your Flask app:

```python
app.logger.setLevel(logging.DEBUG)
```

## 📚 API Documentation

### JavaScript API

```javascript
// Get the network instance
const network = window.skillsNetwork;

// Refresh data
network.refreshData();

// Apply custom filters
network.applyFilters({
    minFrequency: 5,
    coOccurrenceThreshold: 3
});

// Get current data
const currentData = network.skillsData;
```

### Event Handling

```javascript
// Listen for network events
network.network.on('click', (params) => {
    if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        console.log('Clicked skill:', nodeId);
    }
});
```

## 🌟 What This Demonstrates

This skills network visualization showcases:

1. **Advanced Data Visualization**: Professional network graphs
2. **AI Integration**: Smart skill extraction and analysis
3. **Real-time Analytics**: Live data processing and filtering
4. **Modern Web Development**: ES6, responsive design, accessibility
5. **API Design**: RESTful endpoints with proper error handling
6. **User Experience**: Intuitive controls and interactive features

## 🤝 Contributing

To enhance the skills network visualization:

1. **Add New Data Sources**: Integrate with more job platforms
2. **Improve Skill Extraction**: Enhance AI analysis algorithms
3. **Add More Visualizations**: Charts, graphs, and analytics
4. **Performance Optimization**: Caching, lazy loading, etc.
5. **Mobile Enhancement**: Touch gestures and mobile-specific features

---

**Built with ❤️ for the JobPulse project**

This feature demonstrates advanced technical skills that will impress recruiters by showing:
- Full-stack development capabilities
- Data science and visualization expertise
- API design and integration skills
- Modern web development practices
- User experience design thinking


