# ClipMind Infrastructure

AWS CDK infrastructure for ClipMind.

## Setup

```bash
npm install
npm run build
```

## Deploy

```bash
npm run deploy
```

This deploys:
- VPC with public/private subnets
- PostgreSQL RDS database
- S3 buckets for video storage
- ECS cluster for containers
