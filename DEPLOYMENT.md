# Job Market Analytics - Production Deployment Guide

This guide will help you deploy the Job Market Analytics application to a server to test real job searches and avoid 403 errors.

## 🚀 Quick Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Clone or navigate to your project directory
cd /path/to/job_market_analytics

# Make deployment script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

### Option 2: Manual Docker Compose

```bash
# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 20GB+ free space
- **CPU**: 2+ cores
- **Network**: Stable internet connection

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Install Docker (if not installed)

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**CentOS/RHEL:**
```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

## 🔧 Configuration

### 1. Environment Variables

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` with your configuration:
```bash
nano .env
```

Key settings to configure:
- `SECRET_KEY`: Generate a strong secret key
- `DATABASE_URL`: PostgreSQL connection string
- API keys (optional but recommended)

### 2. SSL Certificate (Optional)

For HTTPS in production:
```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key -out ssl/nginx.crt
```

### 3. Firewall Configuration

```bash
# Allow required ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9090/tcp  # Prometheus
```

## 🌐 Access Points

After deployment, access the application at:

- **Main Dashboard**: http://your-server-ip:80
- **Direct Flask App**: http://your-server-ip:5000
- **Health Check**: http://your-server-ip/health
- **Grafana Monitoring**: http://your-server-ip:3000 (admin/admin)
- **Prometheus**: http://your-server-ip:9090

## 🔍 Testing the Deployment

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

### 3. Database Connection Test
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U jobpulse -d jobpulse -c "SELECT version();"
```

## 📊 Monitoring

### 1. Application Logs
```bash
# View real-time logs
docker-compose logs -f app

# View specific service logs
docker-compose logs -f nginx
docker-compose logs -f db
```

### 2. Performance Monitoring
- **Grafana**: http://your-server-ip:3000
  - Username: `admin`
  - Password: `admin`
- **Prometheus**: http://your-server-ip:9090

### 3. Resource Usage
```bash
# Check container resource usage
docker stats

# Check disk usage
df -h

# Check memory usage
free -h
```

## 🔧 Troubleshooting

### Common Issues

#### 1. 403 Errors
The application is configured to use reliable sources first:
- API sources (most reliable)
- Reddit sources (reliable)
- Web scraping sources (may have 403 errors)

**Solution**: The app automatically falls back to reliable sources.

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose ps db

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

#### 3. Application Not Starting
```bash
# Check application logs
docker-compose logs app

# Rebuild application
docker-compose up --build -d app
```

#### 4. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :80

# Stop conflicting service
sudo systemctl stop apache2  # or nginx
```

### Performance Optimization

#### 1. Increase Resources
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

#### 2. Enable Caching
The application uses Redis for caching. Monitor cache hit rates in Grafana.

#### 3. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

## 🔄 Updates and Maintenance

### 1. Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up --build -d
```

### 2. Backup Database
```bash
# Create backup
docker-compose exec db pg_dump -U jobpulse jobpulse > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U jobpulse jobpulse < backup_file.sql
```

### 3. Update Dependencies
```bash
# Update requirements
pip freeze > requirements.txt

# Rebuild container
docker-compose up --build -d app
```

## 🛡️ Security Considerations

### 1. Change Default Passwords
- Database: Update `POSTGRES_PASSWORD` in docker-compose.yml
- Grafana: Change admin password after first login
- Flask: Update `SECRET_KEY` in .env

### 2. SSL/TLS
For production, use proper SSL certificates:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Firewall Rules
```bash
# Restrict access to monitoring ports
sudo ufw deny 3000/tcp  # Grafana
sudo ufw deny 9090/tcp  # Prometheus
```

## 📈 Scaling

### 1. Horizontal Scaling
```bash
# Scale application instances
docker-compose up --scale app=3 -d
```

### 2. Load Balancer
Add nginx load balancer configuration for multiple app instances.

### 3. Database Scaling
Consider using managed PostgreSQL services for production.

## 🎯 Success Metrics

Monitor these metrics to ensure successful deployment:

1. **Health Check**: Should return 200 OK
2. **Job Search**: Should return job results without 403 errors
3. **Response Time**: < 5 seconds for job searches
4. **Uptime**: > 99% availability
5. **Error Rate**: < 1% for API endpoints

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Test connectivity: `curl http://localhost/health`
4. Check resource usage: `docker stats`

The application is designed to be resilient and automatically handle 403 errors by using reliable data sources first. 