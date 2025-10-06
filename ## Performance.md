## Performance

### Processing Benchmarks

- **Video ingestion** (1080p, 10 min): 45 seconds
- **Scene detection**: 2 minutes
- **Transcription** (Whisper base): 3 minutes
- **Embedding generation**: 1 minute
- **End-to-end processing**: ~7 minutes
- **Concurrent processing**: 50+ videos

### Search Performance

- **Semantic search** (P50): 120ms
- **Semantic search** (P95): 350ms
- **Pinecone query**: <100ms

### Cost Estimate

Monthly cost for 1,000 hours of video:

| Service | Cost |
|---------|------|
| S3 Storage | $23 |
| PostgreSQL RDS | $60 |
| ECS Fargate | $120 |
| Pinecone | $70 |
| Data Transfer | $30 |
| **Total** | **~$303/month** |