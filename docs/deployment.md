# Deployment Guide

## Production Deployment

### Docker Deployment

#### 1. Build Image

```bash
docker build -t emotional-tts:latest .
```

#### 2. Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e MODEL_NAME=coqui \
  -e DEVICE=cpu \
  --name emotional-tts \
  emotional-tts:latest
```

#### 3. With GPU Support

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DEVICE=cuda \
  --gpus all \
  --name emotional-tts \
  emotional-tts:latest
```

---

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

### AWS Deployment

#### ECS Fargate

1. **Build and push image:**
```bash
aws ecr create-repository --repository-name emotional-tts
docker tag emotional-tts:latest <account>.dkr.ecr.<region>.amazonaws.com/emotional-tts:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/emotional-tts:latest
```

2. **Create task definition:**
```json
{
  "family": "emotional-tts",
  "cpu": "2048",
  "memory": "8192",
  "requiresCompatibilities": ["FARGATE"],
  "containerDefinitions": [{
    "name": "api",
    "image": "<account>.dkr.ecr.<region>.amazonaws.com/emotional-tts:latest",
    "portMappings": [{"containerPort": 8000}]
  }]
}
```

3. **Create service:**
```bash
aws ecs create-service \
  --cluster emotional-tts-cluster \
  --service-name emotional-tts-api \
  --task-definition emotional-tts \
  --desired-count 2 \
  --launch-type FARGATE
```

---

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: emotional-tts
spec:
  replicas: 3
  selector:
    matchLabels:
      app: emotional-tts
  template:
    metadata:
      labels:
        app: emotional-tts
    spec:
      containers:
      - name: api
        image: emotional-tts:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "1"
          limits:
            memory: "8Gi"
            cpu: "2"
```

---

### systemd Service

```ini
[Unit]
Description=Emotional TTS API
After=network.target

[Service]
Type=simple
User=tts
WorkingDirectory=/opt/emotional-tts
Environment="PATH=/opt/emotional-tts/venv/bin"
ExecStart=/opt/emotional-tts/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/v1/health
```

### Prometheus Metrics

Add to `src/api/main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Access at: `http://localhost:8000/metrics`

---

## Security

### HTTPS/SSL

Use Nginx as reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name tts.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### API Key Authentication

Implement in `src/api/dependencies.py`:
```python
def verify_api_key(api_key: str = Header(...)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

---

## Scaling

### Horizontal Scaling

- Use load balancer (AWS ALB, Nginx)
- Session-less API (stateless)
- Shared storage (S3, NFS)

### Vertical Scaling

- Increase CPU/RAM for faster processing
- Add GPU for real-time synthesis

---

## Backup & Recovery

### Database Backup

```bash
# If using PostgreSQL
pg_dump emotional_tts > backup.sql
```

### Model Backup

```bash
# Backup models
tar -czf models-backup.tar.gz data/models/

# Upload to S3
aws s3 cp models-backup.tar.gz s3://backups/
```

---

## Troubleshooting

### Model not loading

```bash
# Check VRAM
nvidia-smi

# Download models manually
python scripts/setup_models.py
```

### High latency

- Enable GPU
- Reduce model size (quantization)
- Add caching layer (Redis)

---

## Cost Optimization

1. **Use spot instances** for non-critical workloads
2. **Auto-scaling** based on queue length
3. **Caching** for common phrases
4. **Batch processing** for multiple requests

