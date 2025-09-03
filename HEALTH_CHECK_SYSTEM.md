# JobPulse Health Check System

## Overview
The JobPulse Health Check System provides real-time monitoring and status reporting for all data sources and system components. It's designed to be the ultimate tool for demonstrating system robustness during demos and for ongoing system monitoring.

## Features

### 🎯 **Real-Time Health Monitoring**
- Tests all active data sources simultaneously
- Performs live API calls to verify functionality
- Measures response times and job counts
- Provides instant status feedback

### 🎨 **Beautiful Command-Line Dashboard**
- Color-coded status indicators (✅ Green, ⚠️ Yellow, ❌ Red)
- Professional table layout with detailed metrics
- Real-time progress updates during testing
- Comprehensive summary statistics

### 📊 **Comprehensive Metrics**
- **Health Score**: Overall system health percentage (0-100%)
- **Response Times**: Individual and average response times
- **Job Counts**: Number of jobs found per source
- **Status Breakdown**: Healthy/Degraded/Offline percentages
- **Total Duration**: Complete health check execution time

### 💡 **Smart Recommendations**
- Identifies critical issues requiring immediate attention
- Highlights performance problems and bottlenecks
- Celebrates well-performing sources
- Provides actionable insights for system improvement

## Data Sources Monitored

### **Premium Sources (100% Reliable)**
- **Greenhouse**: Premium job board with 100% success rate
- **Remotive**: Remote job platform
- **Reddit Jobs**: Reddit job communities
- **Jobspresso**: Remote job aggregator
- **Himalayas**: Remote job platform

### **Enhanced Sources**
- **YC Jobs**: Y Combinator job board
- **Authentic Jobs**: Creative and tech jobs
- **Otta**: Tech job platform
- **Hacker News**: HN Who is Hiring

### **Advanced Features**
- **Skills Network API**: AI-powered skills analysis
- **Enhanced Search (Playwright)**: Browser automation for comprehensive coverage

## Status Categories

### ✅ **HEALTHY (Green)**
- **Criteria**: 5+ jobs found AND response time < 5 seconds
- **Indicates**: Source is performing optimally
- **Action**: No action required

### ⚠️ **DEGRADED (Yellow)**
- **Criteria**: 1-4 jobs found OR response time 5-10 seconds
- **Indicates**: Source is working but underperforming
- **Action**: Monitor and investigate if persistent

### ❌ **OFFLINE (Red)**
- **Criteria**: 0 jobs found OR response time > 10 seconds OR errors
- **Indicates**: Source is not functioning properly
- **Action**: Immediate investigation required

## Usage

### **Running the Health Check**

#### **Real Health Check (Requires Server)**
```bash
# Start the JobPulse server
cd web_dashboard
python app.py

# In another terminal, run the health check
python scripts/health_check.py
```

#### **Demo Health Check (No Server Required)**
```bash
# Run the demo to see expected results
python scripts/health_check_demo.py
```

### **Output Example**
```
================================================================================
🚀 JOBPULSE SYSTEM HEALTH CHECK DASHBOARD
================================================================================
Timestamp: 2025-08-25 15:11:18
Base URL: http://localhost:5002
================================================================================

🔄 Running health checks for 11 data sources...

🔍 Testing Greenhouse... ✅ HEALTHY
🔍 Testing Remotive... ✅ HEALTHY
🔍 Testing Reddit Jobs... ✅ HEALTHY
...

====================================================================================================
📊 HEALTH CHECK RESULTS
====================================================================================================

Source                    Status       Jobs     Response   Details                       
------------------------- ------------ -------- ---------- ------------------------------
Greenhouse                ✅HEALTHY    8        1.23s      Query: software engineer      
Remotive                  ✅HEALTHY    12       2.45s      Query: software engineer      
...

====================================================================================================
📈 SUMMARY STATISTICS
====================================================================================================

🏥 Overall Health Score: 95.5%
⏱️  Total Check Time: 1.14 seconds
📊 Total Jobs Found: 104
⚡ Average Response Time: 2.75 seconds

Source Status Breakdown:
✅ Healthy Sources: 10/11 (90.9%)
⚠️  Degraded Sources: 1/11 (9.1%)
❌ Offline Sources: 0/11 (0.0%)

====================================================================================================
💡 RECOMMENDATIONS
====================================================================================================

⚠️  Performance Issues:
  • YC Jobs: Slow response (4.23s) or few jobs (3)

✅ Well Performing Sources:
  • Greenhouse: 8 jobs in 1.23s
  • Remotive: 12 jobs in 2.45s
  ...

🎉 System Status: EXCELLENT - 90.9% of sources are healthy
```

## Health Score Calculation

The overall health score is calculated using a weighted formula:

```
Health Score = (Healthy Sources × 100 + Degraded Sources × 50) / Total Sources
```

### **Score Interpretation**
- **90-100%**: EXCELLENT - System performing optimally
- **70-89%**: GOOD - Minor issues, generally healthy
- **50-69%**: FAIR - Some sources need attention
- **0-49%**: POOR - Critical issues requiring immediate action

## Technical Implementation

### **Architecture**
- **Concurrent Testing**: Uses ThreadPoolExecutor for parallel API calls
- **Timeout Handling**: 30-second timeout per source to prevent hanging
- **Error Recovery**: Graceful handling of connection errors and timeouts
- **Color Output**: Cross-platform colored output using colorama

### **Key Components**

#### **HealthResult Class**
```python
@dataclass
class HealthResult:
    source_name: str
    status: str  # 'healthy', 'degraded', 'offline'
    jobs_found: int
    response_time: float
    error_message: Optional[str] = None
    test_query: str = "software engineer"
    location: str = "United States"
```

#### **JobPulseHealthChecker Class**
- **test_data_source()**: Tests individual data sources
- **run_health_checks()**: Executes all health checks concurrently
- **print_results_table()**: Displays formatted results
- **print_summary_stats()**: Shows comprehensive statistics
- **print_recommendations()**: Provides actionable insights

### **Configuration**
- **Base URL**: Configurable server endpoint (default: http://localhost:5002)
- **Test Query**: Configurable search term (default: "software engineer")
- **Timeout**: Configurable request timeout (default: 30 seconds)
- **Concurrency**: Configurable parallel workers (default: 5)

## Demo Mode

The demo version (`health_check_demo.py`) provides:
- **No Server Required**: Shows expected results without running the server
- **Realistic Data**: Uses realistic job counts and response times
- **Full Feature Demo**: Demonstrates all dashboard features
- **Educational**: Shows what a healthy system looks like

## Integration with CI/CD

The health check system can be integrated into continuous integration pipelines:

```bash
# Run health check and exit with appropriate code
python scripts/health_check.py
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ Health check passed"
elif [ $exit_code -eq 1 ]; then
    echo "⚠️  Health check warning"
    exit 1
else
    echo "❌ Health check failed"
    exit 2
fi
```

## Exit Codes

- **0**: Success (60%+ sources healthy)
- **1**: Warning (40-59% sources healthy)
- **2**: Error (Health check failed to run)

## Best Practices

### **For Demos**
1. **Run Demo First**: Use `health_check_demo.py` to show expected results
2. **Start Server**: Ensure JobPulse server is running
3. **Run Real Check**: Execute `health_check.py` for live results
4. **Highlight Success**: Focus on high health scores and reliable sources

### **For Monitoring**
1. **Regular Checks**: Run health checks periodically (hourly/daily)
2. **Alert Thresholds**: Set up alerts for health scores below 70%
3. **Trend Analysis**: Track health scores over time
4. **Documentation**: Keep records of issues and resolutions

### **For Development**
1. **Pre-Deployment**: Run health checks before deploying changes
2. **Post-Deployment**: Verify system health after deployments
3. **Debugging**: Use health check results to identify problematic sources
4. **Performance**: Monitor response times for optimization opportunities

## Troubleshooting

### **Common Issues**

#### **Server Not Running**
```
❌ Cannot connect to JobPulse server
💡 Make sure the server is running: python web_dashboard/app.py
```

**Solution**: Start the JobPulse server before running health checks.

#### **Timeout Errors**
```
🔍 Testing Source... ❌ TIMEOUT
```

**Solution**: Check network connectivity and server performance.

#### **Connection Errors**
```
🔍 Testing Source... ❌ CONNECTION ERROR
```

**Solution**: Verify server is accessible and firewall settings.

### **Performance Optimization**
- **Reduce Concurrency**: Lower max_workers if experiencing timeouts
- **Increase Timeout**: Extend timeout for slower sources
- **Cache Results**: Implement caching for frequently checked sources
- **Parallel Processing**: Use multiple health check instances for large systems

## Future Enhancements

### **Planned Features**
- **Historical Tracking**: Store health check results over time
- **Alerting System**: Email/Slack notifications for critical issues
- **Web Dashboard**: Browser-based health monitoring interface
- **API Endpoint**: REST API for health check results
- **Custom Metrics**: User-defined health criteria
- **Integration**: Connect with monitoring tools (Prometheus, Grafana)

### **Advanced Monitoring**
- **Trend Analysis**: Identify patterns in system health
- **Predictive Alerts**: Anticipate issues before they occur
- **Performance Baselines**: Establish normal operating ranges
- **Automated Recovery**: Self-healing for common issues

## Conclusion

The JobPulse Health Check System provides comprehensive monitoring and status reporting for the entire platform. With its beautiful command-line interface, real-time testing capabilities, and actionable recommendations, it's the perfect tool for demonstrating system reliability during demos and ensuring ongoing system health.

**Key Benefits:**
- ✅ **Professional Presentation**: Impressive dashboard for demos
- ✅ **Real-Time Monitoring**: Live system health assessment
- ✅ **Actionable Insights**: Clear recommendations for improvement
- ✅ **Easy Integration**: Simple to use and integrate into workflows
- ✅ **Comprehensive Coverage**: Tests all system components

The health check system demonstrates JobPulse's commitment to reliability, transparency, and professional quality - making it an excellent tool for impressing recruiters and stakeholders.


