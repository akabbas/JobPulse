# 🚀 Job Market Analytics - Server Deployment Guide

This guide will help you deploy the Job Market Analytics application to a server to test real job searches and avoid 403 errors.

## 🎯 Why Deploy to a Server?

- **Avoid 403 Errors**: Server deployment provides better IP reputation and avoids rate limiting
- **Real Job Data**: Access to actual job postings from multiple sources
- **Production Testing**: Test the application in a real-world environment
- **Better Performance**: Dedicated resources for faster scraping and processing
- **Reliable Access**: 24/7 availability for continuous job market monitoring

## 📋 Deployment Options

### Option 1: Docker Deployment (Recommended)
- **Pros**: Isolated environment, easy scaling, consistent deployment
- **Cons**: Requires Docker knowledge
- **Best for**: Production environments, cloud deployments

### Option 2: Direct Server Deployment
- **Pros**: Simple setup, no Docker required
- **Cons**: More manual configuration
- **Best for**: Simple deployments, learning environments

## 🐳 Option 1: Docker Deployment

### Prerequisites
- Server with Docker support
- 4GB+ RAM, 20GB+ storage
- Stable internet connection

### Quick Start

1. **Install Docker** (if not installed):
```bash
chmod +x install_docker.sh
./install_docker.sh
```

2. **Deploy the application**:
```bash
chmod +x deploy.sh
./deploy.sh
```

3. **Access the application**:
- Main Dashboard: `http://your-server-ip:80`
- Health Check: `http://your-server-ip/health`
- Grafana Monitoring: `http://your-server-ip:3000`

### Docker Services Included

- **App**: Flask web application
- **Nginx**: Reverse proxy and load balancer
- **PostgreSQL**: Database for job data
- **Redis**: Caching and session storage
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboard

## 🖥️ Option 2: Direct Server Deployment

### Prerequisites
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Python 3.8+
- 4GB+ RAM, 20GB+ storage

### Quick Start

1. **Deploy directly on server**:
```bash
chmod +x deploy_simple.sh
./deploy_simple.sh
```

2. **Access the application**:
- Web Dashboard: `http://your-server-ip:5000`
- Health Check: `http://your-server-ip:5000/health`

## 🔧 Configuration

### Environment Variables

Copy and configure the environment file:
```bash
cp env.example .env
nano .env
```

Key settings:
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database Configuration
DATABASE_URL=postgresql://jobpulse:jobpulse123@localhost:5432/jobpulse
REDIS_URL=redis://localhost:6379

# API Keys (Optional but recommended)
INDEED_API_KEY=your_indeed_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
```

### Firewall Configuration

```bash
# Allow required ports
sudo ufw allow 80/tcp    # Nginx
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 5000/tcp  # Flask app
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9090/tcp  # Prometheus
```

## 🛡️ Avoiding 403 Errors

The application is specifically designed to avoid 403 errors through:

### 1. **Reliable Data Sources**
- **API Sources**: Uses official APIs (most reliable)
- **Reddit Sources**: Community job postings (reliable)
- **Web Scraping**: Fallback with rate limiting

### 2. **Smart Source Prioritization**
```python
# Priority order (most reliable first)
sources = {
    'primary': ['api_sources', 'reddit', 'simple_jobs'],
    'secondary': ['indeed', 'linkedin', 'stackoverflow'],
    'fallback': ['dice', 'remoteok', 'weworkremotely']
}
```

### 3. **Rate Limiting & Delays**
- 2-second delays between requests
- Maximum 5 concurrent requests
- Automatic retry with exponential backoff

### 4. **User Agent Rotation**
- Multiple realistic user agents
- Automatic rotation to avoid detection

### 5. **Error Handling**
- Automatic fallback to reliable sources
- Graceful degradation when sources fail
- Sample data fallback for testing

## 🧪 Testing the Deployment

### 1. Health Check
```bash
curl http://your-server-ip/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

### 2. Job Search Test
```bash
curl -X POST http://your-server-ip/search \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "software engineer",
    "location": "United States",
    "sources": ["api_sources", "reddit"],
    "limit": 10
  }'
```

### 3. Database Test
```bash
# Docker deployment
docker-compose exec db psql -U jobpulse -d jobpulse -c "SELECT COUNT(*) FROM jobs;"

# Direct deployment
sudo -u postgres psql -d jobpulse -c "SELECT COUNT(*) FROM jobs;"
```

## 📊 Monitoring & Logs

### Docker Deployment
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f nginx
docker-compose logs -f db

# Check resource usage
docker stats
```

### Direct Deployment
```bash
# View application logs
sudo journalctl -u job-analytics -f

# Check service status
sudo systemctl status job-analytics

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Monitoring Dashboards
- **Grafana**: `http://your-server-ip:3000` (admin/admin)
- **Prometheus**: `http://your-server-ip:9090`

## 🔧 Troubleshooting

### Common Issues

#### 1. **403 Errors Still Occurring**
```bash
# Check which sources are working
curl -X POST http://your-server-ip/search \
  -H "Content-Type: application/json" \
  -d '{"sources": ["api_sources", "reddit"]}'
```

**Solution**: The app automatically uses reliable sources first.

#### 2. **Application Not Starting**
```bash
# Check logs
docker-compose logs app
# or
sudo journalctl -u job-analytics -f

# Check if ports are in use
sudo netstat -tulpn | grep :5000
```

#### 3. **Database Connection Issues**
```bash
# Docker
docker-compose restart db

# Direct deployment
sudo systemctl restart postgresql
```

#### 4. **Memory Issues**
```bash
# Check memory usage
free -h

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🔄 Updates & Maintenance

### Update Application
```bash
# Docker deployment
git pull origin main
docker-compose up --build -d

# Direct deployment
git pull origin main
sudo systemctl restart job-analytics
```

### Backup Database
```bash
# Docker deployment
docker-compose exec db pg_dump -U jobpulse jobpulse > backup_$(date +%Y%m%d_%H%M%S).sql

# Direct deployment
sudo -u postgres pg_dump jobpulse > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Monitor Performance
```bash
# Check resource usage
htop
df -h
free -h

# Monitor application metrics
curl http://your-server-ip:5000/health
```

## 🛡️ Security Best Practices

### 1. **Change Default Passwords**
- Database password in docker-compose.yml
- Grafana admin password
- Flask secret key

### 2. **SSL/TLS Configuration**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. **Firewall Rules**
```bash
# Restrict access to monitoring ports
sudo ufw deny 3000/tcp  # Grafana
sudo ufw deny 9090/tcp  # Prometheus
```

### 4. **Regular Updates**
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Docker images
docker-compose pull
docker-compose up -d
```

## 📈 Performance Optimization

### 1. **Resource Allocation**
Edit `docker-compose.yml`:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### 2. **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

### 3. **Caching Strategy**
- Redis caching for job data
- Nginx caching for static files
- Application-level caching

## 🎯 Success Metrics

Monitor these metrics to ensure successful deployment:

1. **Health Check**: Should return 200 OK
2. **Job Search**: Should return job results without 403 errors
3. **Response Time**: < 5 seconds for job searches
4. **Uptime**: > 99% availability
5. **Error Rate**: < 1% for API endpoints
6. **Data Quality**: > 80% job data completeness

## 📞 Support & Resources

### Useful Commands
```bash
# Check all services
docker-compose ps

# View real-time logs
docker-compose logs -f

# Restart specific service
docker-compose restart app

# Check resource usage
docker stats

# Access database
docker-compose exec db psql -U jobpulse -d jobpulse
```

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)

### Getting Help
1. Check the logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Test connectivity: `curl http://localhost/health`
4. Check resource usage: `docker stats`

The application is designed to be resilient and automatically handle 403 errors by using reliable data sources first. If you encounter issues, the logs will provide detailed information about what's happening. 