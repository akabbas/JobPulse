# 🚀 Railway Deployment Guide for JobPulse

## Overview

This guide will walk you through deploying your enhanced JobPulse application to Railway, a modern platform for deploying applications with built-in PostgreSQL databases.

## ✨ Why Railway?

- **🚀 Simple Deployment**: Git-based deployments with automatic builds
- **🗄️ Built-in PostgreSQL**: No need to manage external databases
- **🌍 Global CDN**: Fast loading times worldwide
- **📊 Built-in Monitoring**: Health checks and performance metrics
- **💰 Generous Free Tier**: Perfect for development and small projects

## 📋 Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Python 3.8+**: Your application should be Python 3.8+ compatible
4. **Playwright**: Ensure Playwright browsers are installed

## 🚀 Quick Deployment Steps

### Step 1: Prepare Your Repository

Ensure your repository has these files:
```
JobPulse/
├── web_dashboard/
│   ├── app.py                 # Main Flask app
│   ├── models.py              # Database models
│   └── templates/             # HTML templates
├── scrapers/                  # All scraper modules
├── requirements-railway.txt   # Railway requirements
├── Procfile.railway          # Railway process file
├── railway.json              # Railway configuration
└── .gitignore                # Git ignore file
```

### Step 2: Connect to Railway

1. **Login to Railway**: `railway login`
2. **Initialize Project**: `railway init`
3. **Link Repository**: `railway link`

### Step 3: Deploy

```bash
# Make the deployment script executable
chmod +x deploy_railway.sh

# Run the deployment script
./deploy_railway.sh
```

## 🔧 Manual Deployment

If you prefer manual deployment:

### 1. Install Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 -useb | iex
```

### 2. Login and Initialize

```bash
railway login
railway init
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements-railway.txt

# Install Playwright browsers
cd web_dashboard
playwright install --with-deps chromium
cd ..
```

### 4. Deploy

```bash
railway up
```

## 🌐 Environment Variables

Set these in your Railway dashboard:

### Required Variables
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-random-key-here
```

### Optional Variables
```bash
FLASK_DEBUG=false
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
MAX_CONCURRENT_SCRAPERS=10
```

### Database (Auto-configured)
Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Application port

## 🗄️ Database Setup

Railway automatically provides a PostgreSQL database:

1. **Database Creation**: Happens automatically on first deployment
2. **Table Creation**: Tables are created on first request
3. **Connection**: Flask-SQLAlchemy automatically connects

### Database Schema
Your `models.py` defines:
- **Job Table**: Stores all scraped job data
- **Search Table**: Tracks user search history

## 🚀 Application Configuration

### Port Configuration
```python
# Automatically uses Railway's PORT environment variable
port = int(os.environ.get('PORT', 5002))
app.run(host='0.0.0.0', port=port)
```

### Database Configuration
```python
# Automatically handles Railway's DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///jobpulse.db'
```

## 📊 Monitoring and Health Checks

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'environment': app.config['FLASK_ENV'],
        'database': 'connected' if db.engine.pool.checkedin() > 0 else 'disconnected'
    })
```

### Railway Dashboard
- **Deployments**: View deployment history and status
- **Logs**: Real-time application logs
- **Metrics**: Performance and resource usage
- **Variables**: Manage environment variables

## 🔍 Troubleshooting

### Common Issues

#### 1. **Playwright Browser Issues**
```bash
# Install browsers in Railway build
playwright install --with-deps chromium
```

#### 2. **Database Connection Issues**
- Check `DATABASE_URL` in Railway variables
- Ensure PostgreSQL service is running
- Verify database credentials

#### 3. **Port Binding Issues**
- Railway automatically provides `PORT` environment variable
- Ensure app binds to `0.0.0.0` and uses `os.environ.get('PORT')`

#### 4. **Import Errors**
- Check all required packages are in `requirements-railway.txt`
- Ensure relative imports are correct

### Debug Commands

```bash
# Check deployment status
railway status

# View logs
railway logs

# Check environment variables
railway variables

# Open application
railway open

# Get application URL
railway domain
```

## 🚀 Advanced Configuration

### Custom Domain
```bash
# Add custom domain
railway domain add yourdomain.com
```

### Environment-Specific Deployments
```bash
# Deploy to specific environment
railway up --environment production
```

### Scaling
```bash
# Scale to multiple replicas
railway scale 2
```

## 📈 Performance Optimization

### 1. **Database Optimization**
- Use database indexes for frequently queried fields
- Implement connection pooling
- Regular database maintenance

### 2. **Caching Strategy**
- Redis for session storage (optional)
- Database caching for job results
- Browser caching for static assets

### 3. **Scraping Optimization**
- Concurrent scraping with rate limiting
- Intelligent retry mechanisms
- Source health monitoring

## 🔒 Security Considerations

### 1. **Environment Variables**
- Never commit secrets to Git
- Use Railway's encrypted variables
- Rotate secrets regularly

### 2. **Database Security**
- Use Railway's managed PostgreSQL
- Implement proper input validation
- SQL injection prevention

### 3. **API Security**
- Rate limiting
- Input sanitization
- CORS configuration

## 🧪 Testing Deployment

### 1. **Health Check**
```bash
curl https://your-app.railway.app/health
```

### 2. **Basic Functionality**
- Test homepage loading
- Test job search functionality
- Test enhanced search
- Verify database operations

### 3. **Performance Testing**
- Response time under load
- Database query performance
- Scraping speed and reliability

## 📚 Useful Commands

### Railway CLI
```bash
railway login          # Login to Railway
railway init           # Initialize project
railway up             # Deploy application
railway status         # Check status
railway logs           # View logs
railway open           # Open in browser
railway variables      # Manage environment variables
railway domain         # Get app URL
```

### Application Management
```bash
# Check application health
curl https://your-app.railway.app/health

# Test job search
curl -X POST https://your-app.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{"keyword":"python developer","location":"United States"}'
```

## 🎉 Success Checklist

- [ ] Application deploys successfully
- [ ] Health check endpoint responds
- [ ] Database tables are created
- [ ] Job search functionality works
- [ ] Enhanced search works
- [ ] Database operations succeed
- [ ] Environment variables are set
- [ ] Custom domain configured (optional)
- [ ] Monitoring and logging working
- [ ] Performance meets expectations

## 🆘 Getting Help

### Railway Support
- **Documentation**: [railway.app/docs](https://railway.app/docs)
- **Discord**: [railway.app/discord](https://railway.app/discord)
- **GitHub**: [github.com/railwayapp](https://github.com/railwayapp)

### JobPulse Support
- Check logs: `railway logs`
- Review deployment status: `railway status`
- Verify environment variables: `railway variables`

## 🚀 Next Steps

After successful deployment:

1. **Monitor Performance**: Use Railway dashboard metrics
2. **Set Up Alerts**: Configure notifications for issues
3. **Optimize**: Implement performance improvements
4. **Scale**: Add more resources as needed
5. **Backup**: Set up database backups
6. **CI/CD**: Automate deployments with GitHub Actions

---

**🎉 Congratulations! Your enhanced JobPulse application is now running on Railway with comprehensive Playwright scraping capabilities!**
