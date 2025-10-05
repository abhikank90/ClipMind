# Deployment Guide

## Prerequisites
- AWS Account
- Docker
- kubectl (for Kubernetes deployment)

## Steps

### 1. Deploy Infrastructure
```bash
cd infrastructure
npm install
npm run deploy
```

### 2. Build Images
```bash
docker-compose -f docker-compose.prod.yml build
```

### 3. Push to Registry
```bash
docker tag clipmind-api:latest ECR_URL/clipmind-api:latest
docker push ECR_URL/clipmind-api:latest
```

### 4. Deploy Application
```bash
kubectl apply -f k8s/
```

## Verification
```bash
curl https://api.clipmind.com/health
```
