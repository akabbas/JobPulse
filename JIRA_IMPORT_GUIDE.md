# Jira Import Guide for JobPulse

## Overview

This guide provides step-by-step instructions for importing the JobPulse product backlog into Jira using the automated import script.

## Prerequisites

### 1. Jira Setup
- Jira site: `ammrabbasher.atlassian.net`
- Project key: `JB`
- Board: https://ammrabbasher.atlassian.net/jira/software/projects/JB/boards/2

### 2. API Token
- Generate API token from Jira account settings
- Token: `YOUR_API_TOKEN_HERE`

### 3. Python Environment
- Python 3.8+
- Required packages: `requests`

## Quick Start

### 1. Set Environment Variables
```bash
export JIRA_SITE="ammrabbasher.atlassian.net"
export JIRA_API_TOKEN="YOUR_API_TOKEN_HERE"
export TICKETS_FILE="JIRA_TICKETS.json"
```

### 2. Install Dependencies
```bash
pip install requests
```

### 3. Run Import Script
```bash
python scripts/jira_import.py
```

## Detailed Instructions

### Step 1: Generate Jira API Token
1. Go to Jira account settings
2. Navigate to Security → API tokens
3. Create new token with appropriate permissions
4. Copy the token for use in environment variables

### Step 2: Configure Environment
Create a `.env` file or set environment variables:
```bash
JIRA_SITE=ammrabbasher.atlassian.net
JIRA_API_TOKEN=your_actual_token_here
TICKETS_FILE=JIRA_TICKETS.json
```

### Step 3: Prepare Ticket Data
Ensure your ticket data is in the correct JSON format:
- Epics with proper structure
- Tasks with appropriate fields
- Categories and labels
- Sprint assignments

### Step 4: Run Import
Execute the import script:
```bash
python scripts/jira_import.py
```

## Script Options

### Basic Import
```bash
python scripts/jira_import.py
```

### Categorized Import
```bash
python scripts/jira_import_categorized.py
```

### Sprint Assignment
```bash
python scripts/assign_sprints_corporate.py
```

## Troubleshooting

### Common Issues
1. **Authentication Error**: Check API token and permissions
2. **Rate Limiting**: Wait and retry, or implement delays
3. **Field Errors**: Verify issue types and custom fields
4. **Network Issues**: Check internet connection and Jira availability

### Error Messages
- `403 Forbidden`: Invalid API token or insufficient permissions
- `400 Bad Request`: Invalid data format or missing required fields
- `429 Too Many Requests`: Rate limiting, implement delays

## Best Practices

### 1. Test First
- Start with a small subset of tickets
- Verify data format and structure
- Test authentication and permissions

### 2. Batch Processing
- Process tickets in batches to avoid rate limits
- Implement proper error handling
- Use retry logic for failed requests

### 3. Data Validation
- Validate ticket data before import
- Check for required fields
- Ensure proper formatting

### 4. Monitoring
- Monitor import progress
- Log errors and issues
- Track success rates

## Advanced Configuration

### Custom Fields
If your Jira instance has custom fields, update the script to include them:
```python
custom_fields = {
    "customfield_10001": "value",
    "customfield_10002": "value"
}
```

### Issue Types
Verify available issue types in your Jira project:
- Epic
- Story
- Task
- Bug
- Sub-task

### Components
Add components if your project uses them:
```python
components = [
    {"name": "Frontend"},
    {"name": "Backend"},
    {"name": "Database"}
]
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Jira API documentation
3. Contact the development team
4. Check project documentation

## Security Notes

- Never commit API tokens to version control
- Use environment variables for sensitive data
- Rotate API tokens regularly
- Follow security best practices

## Conclusion

This guide provides comprehensive instructions for importing JobPulse tickets into Jira. Follow the steps carefully and refer to troubleshooting for common issues.
