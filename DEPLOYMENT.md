# Deployment Guide

This guide covers deploying the Data Analysis AI application to production.

## Prerequisites

- Docker and Docker Compose installed
- Baseten API key
- Server with at least 2GB RAM and 2 CPU cores

## Quick Start with Docker

### 1. Clone and Setup

```bash
git clone <repository-url>
cd data-analysis-ai
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` with your production settings:

```env
ENV=production
DEBUG=False
BASETEN_API_KEY=your_api_key_here
BASETEN_BASE_URL=https://inference.baseten.co/v1
BASETEN_MODEL=openai/gpt-oss-120b
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=100
```

### 3. Build and Run

```bash
docker-compose up -d
```

The application will be available at `http://localhost:8501`

### 4. Check Status

```bash
docker-compose ps
docker-compose logs -f
```

## Manual Deployment

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export ENV=production
export BASETEN_API_KEY=your_api_key_here
# ... other variables
```

### 3. Run Application

```bash
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

## Production Considerations

### Security

1. **API Keys**: Never commit `.env` files to version control
2. **HTTPS**: Use a reverse proxy (nginx) with SSL certificates
3. **Firewall**: Restrict access to necessary ports only
4. **Secrets Management**: Use a secrets manager in production

### Performance

1. **Resource Limits**: Set appropriate CPU and memory limits in Docker
2. **File Size Limits**: Configure `MAX_FILE_SIZE_MB` based on your needs
3. **Caching**: Enable caching for frequently accessed data
4. **Log Rotation**: Logs are automatically rotated (10MB, 5 backups)

### Monitoring

1. **Health Checks**: The application includes health check endpoints
2. **Logging**: Check `logs/app.log` for application logs
3. **Metrics**: Monitor CPU, memory, and disk usage

### Scaling

For high-traffic deployments:

1. Use a load balancer (nginx, HAProxy)
2. Deploy multiple instances behind the load balancer
3. Use a shared session store if needed
4. Consider using a message queue for async processing

## Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

## Troubleshooting

### Application won't start

1. Check logs: `docker-compose logs`
2. Verify environment variables are set correctly
3. Check port availability: `netstat -tulpn | grep 8501`

### LLM API errors

1. Verify API key is correct
2. Check network connectivity to Baseten API
3. Review rate limits and quotas

### High memory usage

1. Reduce `MAX_FILE_SIZE_MB`
2. Limit `MAX_ROWS_PREVIEW`
3. Increase container memory limits

## Health Check

The application includes a health check endpoint. You can test it:

```bash
curl http://localhost:8501/_stcore/health
```

## Backup and Recovery

1. **Logs**: Logs are stored in `logs/` directory
2. **Configuration**: Backup `.env` file securely
3. **Data**: User-uploaded data is not persisted (ephemeral)

## Updates

To update the application:

```bash
git pull
docker-compose build
docker-compose up -d
```

## Support

For issues and questions, check the logs first:
```bash
tail -f logs/app.log
```

