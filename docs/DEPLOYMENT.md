# ClipMind Deployment Guide

Production deployment guide for AWS infrastructure.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Infrastructure Setup](#infrastructure-setup)
- [Application Deployment](#application-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- AWS CLI (v2.x)
- Docker (v20.x+)
- Node.js (v18+)
- Python (3.11+)
- Terraform or AWS CDK

### AWS Account Setup

1. **Create AWS Account**
2. **Configure IAM User** with permissions:
   - S3 (read/write)
   - ECS (full access)
   - RDS (full access)
   - DynamoDB (full access)
   - CloudWatch (read/write)

3. **Configure AWS CLI:**
```bash
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output (json)
```

---

## Infrastructure Setup

### 1. Create S3 Buckets

```bash
# Raw videos
aws s3 mb s3://clipmind-raw-prod --region us-east-1
aws s3api put-bucket-encryption \
  --bucket clipmind-raw-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Processed clips
aws s3 mb s3://clipmind-processed-prod --region us-east-1

# Thumbnails
aws s3 mb s3://clipmind-thumbnails-prod --region us-east-1

# Configure lifecycle policies
aws s3api put-bucket-lifecycle-configuration \
  --bucket clipmind-raw-prod \
  --lifecycle-configuration file://s3-lifecycle.json
```

**s3-lifecycle.json:**
```json
{
  "Rules": [
    {
      "Id": "Move to Glacier after 90 days",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

### 2. Create DynamoDB Table

```bash
aws dynamodb create-table \
  --table-name clipmind-workflow-state-prod \
  --attribute-definitions \
    AttributeName=workflow_id,AttributeType=S \
  --key-schema \
    AttributeName=workflow_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 3. Create RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier clipmind-db-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.3 \
  --master-username clipmind \
  --master-user-password <SECURE_PASSWORD> \
  --allocated-storage 100 \
  --storage-encrypted \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --db-name clipmind \
  --vpc-security-group-ids sg-xxxxx \
  --publicly-accessible false
```

### 4. Create ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id clipmind-redis-prod \
  --cache-node-type cache.t3.medium \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxx
```

### 5. Setup Pinecone Index

```bash
# Using Pinecone CLI or Dashboard
pinecone create-index \
  --name clipmind-embeddings-prod \
  --dimension 512 \
  --metric cosine \
  --pod-type p1.x1 \
  --region us-east-1-aws
```

---

## Application Deployment

### 1. Build Docker Images

**Backend:**
```bash
cd backend

# Build API image
docker build -t clipmind-api:latest -f Dockerfile .

# Build Worker image
docker build -t clipmind-worker:latest -f Dockerfile.worker .

# Tag for ECR
docker tag clipmind-api:latest <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/clipmind-api:latest
docker tag clipmind-worker:latest <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/clipmind-worker:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com

docker push <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/clipmind-api:latest
docker push <AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/clipmind-worker:latest
```

**Frontend:**
```bash
cd frontend

# Build production bundle
npm run build

# Deploy to S3
aws s3 sync dist/ s3://clipmind-frontend-prod --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"
```

### 2. Deploy to ECS

**Create ECS Cluster:**
```bash
aws ecs create-cluster --cluster-name clipmind-prod
```

**Create Task Definition:**

Save as `task-definition-api.json`:
```json
{
  "family": "clipmind-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<AWS_ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/clipmind-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "APP_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:clipmind/database-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/clipmind-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register task:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition-api.json
```

**Create ECS Service:**
```bash
aws ecs create-service \
  --cluster clipmind-prod \
  --service-name clipmind-api \
  --task-definition clipmind-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=api,containerPort=8000"
```

### 3. Setup Load Balancer

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name clipmind-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Create Target Group
aws elbv2 create-target-group \
  --name clipmind-api-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /health

# Create Listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

---

## Configuration

### Environment Variables

Store in AWS Secrets Manager:

```bash
# Database URL
aws secretsmanager create-secret \
  --name clipmind/database-url \
  --secret-string "postgresql://user:pass@host:5432/clipmind"

# Pinecone API Key
aws secretsmanager create-secret \
  --name clipmind/pinecone-api-key \
  --secret-string "your-pinecone-key"

# Application Secret Key
aws secretsmanager create-secret \
  --name clipmind/app-secret-key \
  --secret-string "$(openssl rand -base64 32)"
```

### Production .env Template

```bash
# Application
APP_ENV=production
DEBUG=False
SECRET_KEY=<from_secrets_manager>

# Database
DATABASE_URL=<from_secrets_manager>

# Redis
REDIS_URL=redis://<elasticache-endpoint>:6379/0
CELERY_BROKER_URL=redis://<elasticache-endpoint>:6379/1

# AWS
AWS_REGION=us-east-1
S3_BUCKET_RAW=clipmind-raw-prod
S3_BUCKET_PROCESSED=clipmind-processed-prod
S3_BUCKET_THUMBNAILS=clipmind-thumbnails-prod

# DynamoDB
DYNAMODB_WORKFLOW_TABLE=clipmind-workflow-state-prod

# Pinecone
PINECONE_API_KEY=<from_secrets_manager>
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=clipmind-embeddings-prod

# Monitoring
SENTRY_DSN=<sentry_dsn>
DATADOG_API_KEY=<datadog_key>
```

---

## Monitoring

### CloudWatch Dashboards

Create custom dashboard:

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", {"stat": "Average"}],
          [".", "MemoryUtilization", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "ECS Metrics"
      }
    }
  ]
}
```

### CloudWatch Alarms

```bash
# High CPU
aws cloudwatch put-metric-alarm \
  --alarm-name clipmind-high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:xxx:alerts

# High error rate
aws cloudwatch put-metric-alarm \
  --alarm-name clipmind-high-errors \
  --metric-name 5XXError \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 60 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### Application Monitoring

**Sentry (Error Tracking):**
```python
import sentry_sdk
sentry_sdk.init(dsn="<SENTRY_DSN>", environment="production")
```

**Datadog (APM):**
```python
from ddtrace import tracer
tracer.configure(hostname="datadog-agent", port=8126)
```

---

## Scaling

### Auto-Scaling ECS

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/clipmind-prod/clipmind-api \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/clipmind-prod/clipmind-api \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

### Auto-Scaling Celery Workers

Use custom metric for queue depth:

```bash
# CloudWatch custom metric
aws cloudwatch put-metric-data \
  --namespace ClipMind \
  --metric-name QueueDepth \
  --value 150

# Scale workers based on queue depth
# In your worker deployment, scale when queue > 100
```

---

## Troubleshooting

### Common Issues

**1. ECS Task Fails to Start**
```bash
# Check logs
aws logs tail /ecs/clipmind-api --follow

# Check task definition
aws ecs describe-tasks --cluster clipmind-prod --tasks <task-id>
```

**2. Database Connection Issues**
```bash
# Verify security group allows traffic
aws ec2 describe-security-groups --group-ids sg-xxx

# Test connection from ECS task
aws ecs execute-command \
  --cluster clipmind-prod \
  --task <task-id> \
  --container api \
  --interactive \
  --command "/bin/bash"

# Inside container:
psql $DATABASE_URL
```

**3. S3 Upload Failures**
```bash
# Check IAM permissions
aws iam get-role-policy --role-name ecsTaskExecutionRole --policy-name S3Access

# Verify bucket exists and is accessible
aws s3 ls s3://clipmind-raw-prod/
```

**4. High Memory Usage**
```bash
# Check memory metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average

# Increase task memory in task definition
```

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Rollback ECS service to previous task definition
aws ecs update-service \
  --cluster clipmind-prod \
  --service clipmind-api \
  --task-definition clipmind-api:PREVIOUS_REVISION

# 2. Rollback frontend (S3)
aws s3 sync s3://clipmind-frontend-prod-backup/ s3://clipmind-frontend-prod/ --delete

# 3. Rollback database migrations
cd backend
alembic downgrade -1
```

---

## Security Checklist

- [ ] All S3 buckets have encryption enabled
- [ ] RDS has automated backups (7 days retention)
- [ ] All secrets stored in AWS Secrets Manager
- [ ] IAM roles follow least privilege principle
- [ ] Security groups restrict access to necessary ports
- [ ] CloudTrail logging enabled
- [ ] VPC Flow Logs enabled
- [ ] HTTPS enforced (no HTTP)
- [ ] WAF rules configured for ALB
- [ ] Regular security audits scheduled

---

## Cost Optimization

**Strategies:**
1. Use Spot Instances for Celery workers (70% savings)
2. S3 Lifecycle policies (move to Glacier after 90 days)
3. Reserved Instances for RDS (40% savings)
4. CloudFront caching for static assets
5. Auto-scaling to match demand

**Monthly Cost Estimate (1000 hours of video):**
- Compute: ~$200
- Storage: ~$100
- Database: ~$60
- Monitoring: ~$50
- **Total: ~$410/month**
