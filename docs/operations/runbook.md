# Operational Runbook

## Common Operations

### Scale Workers
```bash
kubectl scale deployment clipmind-worker --replicas=10
```

### View Logs
```bash
kubectl logs -f deployment/clipmind-api
```

### Database Backup
```bash
pg_dump clipmind > backup.sql
```

## Troubleshooting

### High Queue Depth
1. Check worker count
2. Scale workers up
3. Check for failing tasks

### Database Connection Issues
1. Check security groups
2. Verify connection string
3. Check connection pool settings
