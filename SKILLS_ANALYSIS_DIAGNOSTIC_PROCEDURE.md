# 🔍 Skills Analysis & Skills Network Diagnostic Procedure

## Overview
This document provides a comprehensive two-phase diagnostic procedure to isolate failure points in the Skills Analysis service and Skills Network visualization components of JobPulse.

---

## 📋 Phase 1: Skills Analysis API Diagnosis

### Step 1.1: Test the AI Service
**Objective**: Verify the `ai_analyzer.py` module can be imported and its methods run without errors.

**Terminal Commands**:
```bash
# Navigate to project directory
cd /Users/ammrabbasher/Documents/JobPulse

# Test AI analyzer import and basic functionality
python3 -c "
import sys
sys.path.append('.')
from ai_services.ai_analyzer import AIJobAnalyzer
import os

# Check if OpenAI API key is available
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print('❌ FAIL: OPENAI_API_KEY environment variable not set')
    sys.exit(1)
else:
    print('✅ PASS: OpenAI API key found')

# Test AI analyzer initialization
try:
    analyzer = AIJobAnalyzer()
    print('✅ PASS: AIJobAnalyzer initialized successfully')
    
    # Test with sample job data
    sample_job = {
        'title': 'Software Engineer',
        'description': 'Looking for a Python developer with React and AWS experience. Must have experience with JavaScript, Docker, and modern web development practices.',
        'company': 'Tech Corp',
        'location': 'San Francisco, CA'
    }
    
    # Test job description analysis
    result = analyzer.analyze_job_description(sample_job['description'], sample_job)
    if result.get('success'):
        print('✅ PASS: analyze_job_description() method works correctly')
        print(f'   Analysis result keys: {list(result.get(\"analysis\", {}).keys())}')
    else:
        print(f'❌ FAIL: analyze_job_description() failed: {result.get(\"error\")}')
        
except Exception as e:
    print(f'❌ FAIL: AI analyzer initialization failed: {e}')
    sys.exit(1)
"
```

**Expected Outcome**: 
- ✅ PASS: All components work correctly
- ❌ FAIL: Skills Analysis failed at Step 1.1

---

### Step 1.2: Test the API Endpoint
**Objective**: Call the `/api/skills-network` endpoint directly and validate response structure.

**Terminal Commands**:
```bash
# Start the Flask application in background
cd /Users/ammrabbasher/Documents/JobPulse
python3 web_dashboard/app.py &
FLASK_PID=$!

# Wait for server to start
sleep 5

# Test the API endpoint
echo "Testing /api/skills-network endpoint..."
curl -s -w "\nHTTP Status: %{http_code}\n" \
  "http://localhost:5002/api/skills-network?min_frequency=1&min_co_occurrence=1" \
  -H "Accept: application/json" | jq '.'

# Test with additional parameters
echo -e "\nTesting with keyword filter..."
curl -s -w "\nHTTP Status: %{http_code}\n" \
  "http://localhost:5002/api/skills-network?keyword=python&min_frequency=1" \
  -H "Accept: application/json" | jq '.'

# Clean up - kill the Flask process
kill $FLASK_PID 2>/dev/null || true
```

**Validation Checklist**:
- [ ] HTTP Status Code: 200 (not 500)
- [ ] Response contains `"success": true`
- [ ] Response contains `"data"` object
- [ ] `data.skills` is an object with skill names as keys
- [ ] `data.co_occurrences` is an object with skill pairs as keys
- [ ] Response contains `"nodes"` and `"edges"` arrays for vis-network compatibility

**Expected Outcome**:
- ✅ PASS: API returns valid JSON with required structure
- ❌ FAIL: Skills Analysis failed at Step 1.2

---

### Step 1.3: Validate Data Source
**Objective**: Confirm the API is querying the correct database table and that jobs contain valid description text.

**Terminal Commands**:
```bash
# Test database connectivity and data availability
python3 -c "
import sys
sys.path.append('.')
from web_dashboard.app import app, db, Job, Search
from datetime import datetime, timedelta

with app.app_context():
    # Check if database tables exist
    try:
        job_count = Job.query.count()
        search_count = Search.query.count()
        print(f'✅ PASS: Database connected - {job_count} jobs, {search_count} searches')
    except Exception as e:
        print(f'❌ FAIL: Database connection failed: {e}')
        sys.exit(1)
    
    # Check for recent jobs with descriptions
    recent_jobs = Job.query.filter(
        Job.created_at >= datetime.utcnow() - timedelta(days=7)
    ).limit(5).all()
    
    if not recent_jobs:
        print('⚠️  WARNING: No recent jobs found in database')
        print('   This will cause the API to fall back to sample data')
    else:
        print(f'✅ PASS: Found {len(recent_jobs)} recent jobs')
        
        # Check if jobs have descriptions
        jobs_with_descriptions = [job for job in recent_jobs if job.description and len(job.description.strip()) > 50]
        if jobs_with_descriptions:
            print(f'✅ PASS: {len(jobs_with_descriptions)} jobs have valid descriptions')
            print(f'   Sample description length: {len(jobs_with_descriptions[0].description)} characters')
        else:
            print('❌ FAIL: No jobs have valid descriptions for AI analysis')
    
    # Check for skills data
    jobs_with_skills = Job.query.filter(Job.skills.isnot(None), Job.skills != '').limit(5).all()
    if jobs_with_skills:
        print(f'✅ PASS: Found {len(jobs_with_skills)} jobs with predefined skills')
    else:
        print('⚠️  WARNING: No jobs with predefined skills - will rely on AI extraction')
"
```

**Expected Outcome**:
- ✅ PASS: Database has recent jobs with valid descriptions
- ❌ FAIL: Skills Analysis failed at Step 1.3

---

## 📋 Phase 2: Skills Network Frontend Diagnosis

### Step 2.1: Check Library Dependencies
**Objective**: Verify the `vis-network` library is loaded in the browser without CDN errors.

**Browser Console Commands**:
```javascript
// Open browser DevTools (F12) and run these commands in the Console tab

// Check if vis-network library is loaded
console.log('Testing vis-network library...');
if (typeof vis !== 'undefined') {
    console.log('✅ PASS: vis-network library loaded successfully');
    console.log('   vis.Network available:', typeof vis.Network);
    console.log('   vis.DataSet available:', typeof vis.DataSet);
} else {
    console.log('❌ FAIL: vis-network library not found');
    console.log('   Check network tab for CDN loading errors');
}

// Check for other required libraries
console.log('Checking Chart.js...');
if (typeof Chart !== 'undefined') {
    console.log('✅ PASS: Chart.js library loaded');
} else {
    console.log('❌ FAIL: Chart.js library not found');
}

// Check for jQuery/Bootstrap if used
console.log('Checking jQuery...');
if (typeof $ !== 'undefined') {
    console.log('✅ PASS: jQuery loaded');
} else {
    console.log('⚠️  WARNING: jQuery not found (may not be required)');
}
```

**Network Tab Check**:
1. Open DevTools → Network tab
2. Refresh the page
3. Look for failed requests (red entries) to:
   - `vis-network.min.js`
   - `chart.js`
   - Any other CDN resources

**Expected Outcome**:
- ✅ PASS: All required libraries load without errors
- ❌ FAIL: Skills Network failed at Step 2.1

---

### Step 2.2: Test JavaScript Execution
**Objective**: Check for uncaught JavaScript exceptions when clicking the "Skills Network" tab.

**Browser Console Commands**:
```javascript
// Clear console and monitor for errors
console.clear();
console.log('Monitoring for JavaScript errors...');

// Check if SkillsNetworkVisualizer class is available
if (typeof SkillsNetworkVisualizer !== 'undefined') {
    console.log('✅ PASS: SkillsNetworkVisualizer class loaded');
} else {
    console.log('❌ FAIL: SkillsNetworkVisualizer class not found');
}

// Check if initializeSkillsNetwork function is available
if (typeof initializeSkillsNetwork !== 'undefined') {
    console.log('✅ PASS: initializeSkillsNetwork function available');
} else {
    console.log('❌ FAIL: initializeSkillsNetwork function not found');
}

// Check if skills-network container exists
const container = document.getElementById('skills-network');
if (container) {
    console.log('✅ PASS: skills-network container found');
    console.log('   Container dimensions:', container.offsetWidth, 'x', container.offsetHeight);
} else {
    console.log('❌ FAIL: skills-network container not found');
}

// Monitor for errors during tab switching
console.log('Now click the Skills Network tab and watch for errors...');
```

**Manual Test Steps**:
1. Navigate to the JobPulse application
2. Open DevTools → Console tab
3. Clear the console
4. Click on the "Skills Network" tab
5. Watch for any red error messages

**Expected Outcome**:
- ✅ PASS: No JavaScript errors when switching to Skills Network tab
- ❌ FAIL: Skills Network failed at Step 2.2

---

### Step 2.3: Inspect API Response Handling
**Objective**: Add console logging to the `fetchData()` method to confirm it receives and processes API responses.

**Browser Console Commands**:
```javascript
// Temporarily modify the fetchSkillsData method to add detailed logging
if (window.skillsNetwork) {
    // Store original method
    const originalFetchData = window.skillsNetwork.fetchSkillsData;
    
    // Override with logging version
    window.skillsNetwork.fetchSkillsData = async function() {
        console.log('🔍 DEBUG: fetchSkillsData() called');
        console.log('   API URL:', this.apiUrl);
        console.log('   Use current search:', this.useCurrentSearch);
        console.log('   Search ID:', this.searchId);
        
        try {
            const result = await originalFetchData.call(this);
            console.log('✅ DEBUG: fetchSkillsData() completed successfully');
            console.log('   Response structure:', Object.keys(this.skillsData || {}));
            if (this.skillsData && this.skillsData.data) {
                console.log('   Data structure:', Object.keys(this.skillsData.data));
                console.log('   Skills count:', Object.keys(this.skillsData.data.skills || {}).length);
                console.log('   Co-occurrences count:', Object.keys(this.skillsData.data.co_occurrences || {}).length);
            }
            return result;
        } catch (error) {
            console.log('❌ DEBUG: fetchSkillsData() failed:', error);
            throw error;
        }
    };
    
    console.log('✅ DEBUG: Added logging to fetchSkillsData method');
    console.log('Now refresh the Skills Network tab to see detailed logs...');
} else {
    console.log('❌ FAIL: skillsNetwork instance not found');
}
```

**Manual Test Steps**:
1. Run the above console commands
2. Refresh the Skills Network tab or click it again
3. Watch the console for detailed API call logs
4. Check if the API response is received and parsed correctly

**Expected Outcome**:
- ✅ PASS: API response received and parsed successfully
- ❌ FAIL: Skills Network failed at Step 2.3

---

### Step 2.4: Validate Data Structure
**Objective**: Ensure the frontend `SkillsNetworkVisualizer` class expects the exact JSON structure returned by the API.

**Browser Console Commands**:
```javascript
// Check the expected vs actual data structure
if (window.skillsNetwork && window.skillsNetwork.skillsData) {
    const data = window.skillsNetwork.skillsData;
    console.log('🔍 DEBUG: Validating data structure...');
    
    // Check top-level structure
    const requiredTopLevel = ['success', 'data'];
    const hasRequiredTopLevel = requiredTopLevel.every(key => key in data);
    console.log('✅ Top-level structure:', hasRequiredTopLevel ? 'PASS' : 'FAIL');
    
    if (data.data) {
        // Check data-level structure
        const requiredDataLevel = ['skills', 'co_occurrences'];
        const hasRequiredDataLevel = requiredDataLevel.every(key => key in data.data);
        console.log('✅ Data-level structure:', hasRequiredDataLevel ? 'PASS' : 'FAIL');
        
        // Check skills structure
        if (data.data.skills) {
            const skillsType = typeof data.data.skills;
            const skillsIsObject = skillsType === 'object' && !Array.isArray(data.data.skills);
            console.log('✅ Skills structure:', skillsIsObject ? 'PASS' : 'FAIL');
            console.log('   Skills type:', skillsType);
            console.log('   Skills count:', Object.keys(data.data.skills).length);
        }
        
        // Check co_occurrences structure
        if (data.data.co_occurrences) {
            const coOccType = typeof data.data.co_occurrences;
            const coOccIsObject = coOccType === 'object' && !Array.isArray(data.data.co_occurrences);
            console.log('✅ Co-occurrences structure:', coOccIsObject ? 'PASS' : 'FAIL');
            console.log('   Co-occurrences type:', coOccType);
            console.log('   Co-occurrences count:', Object.keys(data.data.co_occurrences).length);
        }
        
        // Check vis-network compatibility
        const hasNodes = 'nodes' in data;
        const hasEdges = 'edges' in data;
        console.log('✅ Vis-network compatibility:', (hasNodes && hasEdges) ? 'PASS' : 'FAIL');
        console.log('   Has nodes array:', hasNodes);
        console.log('   Has edges array:', hasEdges);
        
        if (hasNodes && hasEdges) {
            console.log('   Nodes count:', data.nodes.length);
            console.log('   Edges count:', data.edges.length);
        }
    }
} else {
    console.log('❌ FAIL: No skills data available for validation');
}
```

**Expected Data Structure**:
```json
{
  "success": true,
  "data": {
    "skills": {
      "Python": 8,
      "React": 6,
      "AWS": 5
    },
    "co_occurrences": {
      "Python|React": 3,
      "Python|AWS": 2
    },
    "total_jobs_analyzed": 10,
    "data_source": "database"
  },
  "nodes": [
    {"id": "Python", "label": "Python", "value": 8},
    {"id": "React", "label": "React", "value": 6}
  ],
  "edges": [
    {"from": "Python", "to": "React", "value": 3}
  ]
}
```

**Expected Outcome**:
- ✅ PASS: Data structure matches frontend expectations
- ❌ FAIL: Skills Network failed at Step 2.4

---

## 🎯 Diagnostic Summary

After completing both phases, you should have a clear understanding of where the failure occurs:

### Phase 1 Results:
- **Step 1.1**: AI Service functionality
- **Step 1.2**: API endpoint response
- **Step 1.3**: Database data availability

### Phase 2 Results:
- **Step 2.1**: Library dependencies
- **Step 2.2**: JavaScript execution
- **Step 2.3**: API response handling
- **Step 2.4**: Data structure validation

### Final Diagnosis:
Based on the results, you can determine:
- **"Skills Analysis failed at Step X"** - If Phase 1 fails
- **"Skills Network failed at Step Y"** - If Phase 2 fails
- **"Both systems working correctly"** - If all steps pass

---

## 🛠️ Quick Fixes

### Common Issues and Solutions:

1. **Missing OpenAI API Key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **Database Connection Issues**:
   ```bash
   # Check if database file exists
   ls -la jobpulse.db
   
   # Recreate database if needed
   python3 -c "from web_dashboard.app import create_tables; create_tables()"
   ```

3. **CDN Loading Issues**:
   - Check internet connection
   - Try alternative CDN URLs
   - Consider hosting libraries locally

4. **JavaScript Errors**:
   - Clear browser cache
   - Check for conflicting scripts
   - Verify container element exists

---

## 📞 Support

If all diagnostic steps pass but the system still doesn't work, the issue may be:
- Environment-specific configuration
- Browser compatibility
- Network/firewall restrictions
- Race conditions in initialization

In such cases, provide the complete diagnostic output for further analysis.
