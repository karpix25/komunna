# Deployment Guide

## EasyPanel Deployment

1. Create new project in EasyPanel
2. Upload `easypanel.json` configuration
3. Set environment variables
4. Deploy services

### Required Environment Variables
```
POSTGRES_PASSWORD=secure_password_here
SECRET_KEY=your_jwt_secret_key
BOT_TOKEN=your_telegram_bot_token
```

## Manual Server Deployment

### Prerequisites
- Docker and Docker Compose
- SSL certificates (for HTTPS)
- Domain name pointing to server

### Steps

1. Clone repository on server
```bash
git clone <repository_url>
cd myapp
```

2. Configure environment
```bash
cp .env.example .env
# Edit .env with production values
```

3. Setup SSL certificates
```bash
# Copy SSL certificates to nginx/ssl/
cp your_cert.pem nginx/ssl/
cp your_key.key nginx/ssl/
```

4. Deploy
```bash
make deploy
```

### Production Checklist
- [ ] SSL certificates configured
- [ ] Environment variables set
- [ ] Database backups scheduled
- [ ] Monitoring setup
- [ ] Domain DNS configured
- [ ] Firewall rules applied

## Database Backup

### Automatic Backups
Setup cron job for automatic backups:
```bash
# Add to crontab
0 2 * * * /path/to/project/scripts/backup-db.sh
```

### Manual Backup
```bash
make backup
```

### Restore Backup
```bash
make restore FILE=./database/backups/backup_20231201_020000.sql
```

## Monitoring

### Logs Location
- Application logs: `./logs/`
- Nginx logs: `./nginx/logs/`
- Docker logs: `docker-compose logs`

### Health Checks
- Frontend: `http://yourdomain.com`
- Backend API: `http://api.yourdomain.com/health`
- Database: Check container status

## Scaling

### Horizontal Scaling
1. Setup load balancer
2. Deploy multiple backend instances
3. Use shared Redis for sessions
4. Setup database replication

### Performance Optimization
1. Enable Redis caching
2. Optimize database queries
3. Setup CDN for static assets
4. Enable gzip compression
