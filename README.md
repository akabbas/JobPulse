# Job Market Analytics Platform

A job market analytics platform I built to solve real problems with job searching and data collection. This project tackles the common issues of 403 errors and limited job data by using a multi-source approach with proper error handling.

## Why I Built This
I was tired of job scrapers that break after a few requests or only scrape one source. I wanted something that actually works without getting blocked and provides real insights, not just basic job listings.

## Key Features
- **Multi-source scraping** - APIs, Reddit, Indeed, LinkedIn
- **403 error prevention** - Smart source prioritization and rate limiting
- **Real analytics** - Skills analysis, salary insights, market trends
- **Production deployment** - Docker, Kubernetes, monitoring

## Quick Start
```bash
git clone https://github.com/akabbas/job-market-analytics.git
cd job-market-analytics
chmod +x deploy.sh
./deploy.sh
```

Then visit http://localhost:5001

## Tech Stack
- **Backend**: Python, Flask, SQLAlchemy
- **Databases**: PostgreSQL, Redis, Snowflake
- **Deployment**: Docker, Kubernetes, Nginx
- **Monitoring**: Prometheus, Grafana

## What Makes This Different
Most job scrapers are simple scripts that break when sites change. This is a complete platform with robust error handling, real analytics, and production-ready deployment.

## License
MIT License

---
Built with ❤️ and lots of debugging
