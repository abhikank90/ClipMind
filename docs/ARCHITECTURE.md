# ClipMind Architecture

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Layers](#architecture-layers)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Scalability](#scalability)
- [Security](#security)

---

## System Overview

ClipMind is built as a distributed, event-driven system optimized for video processing and semantic search at scale.

### Design Principles

1. **Separation of Concerns**: Clear boundaries between API, orchestration, processing, and storage
2. **Asynchronous Processing**: Long-running video processing doesn't block API responses
3. **Event-Driven**: State changes trigger downstream processing
4. **Horizontally Scalable**: All components can scale independently
5. **Fault Tolerant**: Retry logic, circuit breakers, and graceful degradation

### High-Level Architecture

```
[User] → [API Gateway] → [Orchestrator] → [Workers] → [Storage]
                ↓              ↓              ↓
            [Auth]        [DynamoDB]     [AI Models]
                              ↓              ↓
                          [Workflow]    [Pinecone]
```

---

## Architecture Layers

### 1. User Interface Layer

**Components:**
- React web application (TypeScript)
- Mobile app (React Native) - planned
- REST API consumers

**Responsibilities:**
- User authentication and session management
- Video upload interface
- Search interface
- Results visualization
- Analytics dashboards

### 2. API Gateway Layer

**Technology:** FastAPI (Python 3.11+)

**Responsibilities:**
- REST API endpoints
- JWT authentication and authorization
- Request validation (Pydantic schemas)
- Rate limiting (Redis-based)
- WebSocket connections for real-time updates
- API documentation (OpenAPI/Swagger)

**Key Features:**
- Async/await for non-blocking I/O
- Automatic data validation
- Built-in OpenAPI schema generation
- CORS middleware

### 3. Orchestration Layer

**Technology:** Celery + Redis

**Responsibilities:**
- Workflow state management
- Task scheduling and distribution
- Retry logic with exponential backoff
- Priority queues
- Dead letter queue handling
- Progress tracking

**Queue Structure:**
```
High Priority Queue    → Paid users, urgent processing
Standard Queue         → Regular processing
Batch Queue           → Overnight bulk processing
```

### 4. Processing Layer

**Components:**

**Video Processor (FFmpeg)**
- Metadata extraction
- Transcoding
- Thumbnail generation
- Audio extraction
- Frame extraction

**Scene Detector (PySceneDetect)**
- Shot boundary detection
- Adaptive threshold detection
- Scene metadata extraction

**AI Pipeline**
- CLIP: Visual embeddings (512-dim)
- Whisper: Audio transcription
- Sentence-BERT: Text embeddings (384-dim)

### 5. Search Layer

**Components:**

**Pinecone (Vector Database)**
- 512-dimensional visual vectors
- 384-dimensional text vectors
- Cosine similarity search
- Metadata filtering

**PostgreSQL (Metadata)**
- Relational data queries
- Complex filtering
- Analytics queries

**Redis (Cache)**
- Query result caching
- Hot data caching
- Session storage

### 6. Storage Layer

**AWS S3:**
- Raw videos: `s3://clipmind-raw/users/{user_id}/videos/{video_id}.mp4`
- Processed clips: `s3://clipmind-processed/videos/{video_id}/clips/{clip_id}.mp4`
- Thumbnails: `s3://clipmind-thumbnails/videos/{video_id}/{type}.jpg`

**PostgreSQL:**
- Users, videos, clips
- Projects, compilations
- Search queries, analytics

**DynamoDB:**
- Workflow state tracking
- Real-time progress updates
- Job metadata

**Redis:**
- Session cache
- Rate limiting counters
- Celery message broker

---

## Component Details

### API Gateway (FastAPI)

**File Structure:**
```
app/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   ├── videos.py
│       │   ├── search.py
│       │   └── analytics.py
│       └── router.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── dependencies.py
└── main.py
```

**Request Flow:**
```
Client Request
    ↓
Middleware (CORS, Auth, Rate Limit)
    ↓
Route Handler
    ↓
Service Layer
    ↓
Repository/External Service
    ↓
Response
```

### Orchestration (Celery)

**Task Types:**

1. **Video Processing Tasks**
   - `process_video_task`: Main video processing workflow
   - `generate_clip_embeddings_task`: Generate embeddings for clips

2. **Compilation Tasks**
   - `render_compilation_task`: Render video compilation
   - `add_music_task`: Add background music

3. **Cleanup Tasks**
   - `cleanup_old_files_task`: Remove temporary files
   - `archive_old_videos_task`: Move old videos to Glacier

**Workflow Example:**
```python
@celery_app.task(bind=True, max_retries=3)
def process_video_task(self, video_id, video_url, workflow_id):
    try:
        # Update DynamoDB: status=processing
        # Extract metadata
        # Generate thumbnail
        # Detect scenes
        # Transcribe audio
        # Generate embeddings
        # Index in Pinecone
        # Update PostgreSQL
        # Update DynamoDB: status=completed
    except Exception as e:
        # Update DynamoDB: error
        # Retry with exponential backoff
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

### AI Pipeline

**CLIP (Visual Understanding)**
```
Video Frame (JPG)
    ↓
Preprocessing (resize, normalize)
    ↓
CLIP Model (ViT-B/32)
    ↓
512-dimensional embedding
    ↓
Normalize (L2 norm)
    ↓
Store in Pinecone
```

**Whisper (Transcription)**
```
Audio File (WAV, 16kHz)
    ↓
Whisper Model (base/large-v3)
    ↓
Transcription with timestamps
    ↓
Segment by sentence
    ↓
Store in PostgreSQL
```

**Sentence-BERT (Text Embeddings)**
```
Transcript Text
    ↓
Tokenization
    ↓
Sentence-BERT Model
    ↓
384-dimensional embedding
    ↓
Store in Pinecone
```

### Search Engine

**Hybrid Search Strategy:**

1. **Vector Search** (Pinecone)
   - Generate query embeddings (CLIP + Sentence-BERT)
   - Search visual vectors (top 40)
   - Search text vectors (top 40)
   - Merge with weighted fusion

2. **Metadata Filtering** (PostgreSQL)
   - Date range
   - Video IDs
   - User ownership
   - Duration constraints

3. **Result Fusion**
   - Weighted combination: visual (60%) + text (40%)
   - Sort by relevance score
   - Enrich with database metadata
   - Generate presigned URLs

---

## Data Flow

### Video Upload Flow

```
1. User uploads video → API
2. API validates file → Save to S3 (raw bucket)
3. Create video record → PostgreSQL (status="pending")
4. Create workflow → DynamoDB (progress=0%)
5. Queue task → Celery
6. Return response → User (video_id, workflow_id)

Background Processing:
7. Worker picks task → Update DynamoDB (processing)
8. Extract metadata → FFmpeg
9. Update PostgreSQL → duration, resolution, etc.
10. Generate thumbnail → FFmpeg → S3 (thumbnails)
11. Detect scenes → PySceneDetect
12. Extract audio → FFmpeg
13. Transcribe → Whisper
14. Extract frames → FFmpeg
15. Generate embeddings → CLIP + Sentence-BERT
16. Index embeddings → Pinecone
17. Save clips → PostgreSQL
18. Update status → PostgreSQL (processed), DynamoDB (completed)
```

### Search Flow

```
1. User enters query → API
2. Generate embeddings → CLIP + Sentence-BERT
3. Search Pinecone → Vector similarity (visual + text)
4. Merge results → Weighted fusion
5. Fetch metadata → PostgreSQL (clips, videos)
6. Generate URLs → S3 presigned URLs
7. Save analytics → PostgreSQL (search_queries, search_results)
8. Return results → User

User clicks clip:
9. Track interaction → PostgreSQL (clip_interactions)
```

---

## Scalability

### Horizontal Scaling

**API Layer:**
- ECS Fargate auto-scaling based on CPU/memory
- Target: CPU > 70% → scale out
- Load balancer distributes requests

**Worker Layer:**
- Celery workers scale based on queue depth
- Target: Queue > 100 → add workers
- Separate worker pools for different task types

**Database Layer:**
- PostgreSQL read replicas for search queries
- Connection pooling (20 connections per instance)
- Prepared statement caching

**Storage Layer:**
- S3 automatically scales
- CloudFront CDN for video delivery
- Multi-region replication for disaster recovery

### Performance Optimization

**Caching Strategy:**
```
L1: Application memory (LRU cache)
L2: Redis (query results, 1 hour TTL)
L3: CloudFront (videos/thumbnails, 24 hour TTL)
L4: S3 (permanent storage)
```

**Database Indexes:**
```sql
-- Videos
CREATE INDEX idx_videos_user_status ON videos(user_id, status);
CREATE INDEX idx_videos_created_at ON videos(created_at DESC);

-- Clips
CREATE INDEX idx_clips_video_id ON clips(video_id);
CREATE INDEX idx_clips_embedding_id ON clips(embedding_id);

-- Search queries
CREATE INDEX idx_search_user_created ON search_queries(user_id, created_at DESC);
CREATE INDEX idx_interactions_clip ON clip_interactions(clip_id, created_at DESC);
```

**Batch Processing:**
- Process frames in batches of 8 for CLIP
- Batch insert clips (100 at a time)
- Batch upsert to Pinecone (100 vectors)

---

## Security

### Authentication & Authorization

**JWT Tokens:**
- Access token: 15 minutes expiry
- Refresh token: 7 days expiry
- Tokens signed with HS256

**Authorization Levels:**
- User: Own videos only
- Admin: All videos
- System: Internal tasks

### Data Security

**Encryption at Rest:**
- S3: SSE-KMS encryption
- RDS: Database encryption enabled
- Secrets: AWS Secrets Manager

**Encryption in Transit:**
- TLS 1.3 for all API calls
- S3 presigned URLs with HTTPS only
- Database connections use SSL

### API Security

**Rate Limiting:**
```python
# Per user limits
100 requests/minute for search
10 uploads/hour
1000 requests/hour overall
```

**Input Validation:**
- Pydantic schemas for all inputs
- File type validation
- Maximum file size: 10GB
- SQL injection prevention (parameterized queries)

**CORS Policy:**
```python
allowed_origins = [
    "https://clipmind.app",
    "https://app.clipmind.com"
]
```

---

## Monitoring & Observability

### Metrics Tracked

**Application Metrics:**
- Request rate (requests/second)
- Response time (P50, P95, P99)
- Error rate (%)
- Active users

**Processing Metrics:**
- Queue depth
- Processing time per video
- Success/failure rate
- Worker utilization

**Business Metrics:**
- Videos uploaded per day
- Searches per day
- Popular search terms
- Click-through rate

### Alerting

**Critical Alerts:**
- Error rate > 1% (5-minute window)
- Queue depth > 1000
- Database connection pool exhausted
- S3 upload failures

**Warning Alerts:**
- Response time P95 > 1s
- Processing time > 30 min per video
- Disk usage > 80%

### Logging

**Log Levels:**
- ERROR: Failures, exceptions
- WARNING: Retry attempts, degraded performance
- INFO: State changes, important events
- DEBUG: Detailed execution flow

**Centralized Logging:**
- CloudWatch Logs
- Structured JSON format
- Request ID tracking across services

---

## Disaster Recovery

### Backup Strategy

**Database Backups:**
- Automated daily snapshots (RDS)
- Point-in-time recovery (35 days)
- Cross-region backup replication

**S3 Backups:**
- Versioning enabled
- Lifecycle policies (90 days → Glacier)
- Cross-region replication

**Recovery Time Objectives:**
- RTO (Recovery Time): 1 hour
- RPO (Recovery Point): 15 minutes

### Failure Scenarios

**API Server Down:**
- Load balancer routes to healthy instances
- Auto-scaling adds new instances
- Impact: None (< 1 second failover)

**Database Failure:**
- Automatic failover to standby replica
- Read replicas serve read traffic
- Impact: 30-60 seconds downtime

**S3 Outage:**
- CloudFront serves cached content
- Cross-region failover
- Impact: Degraded (no new uploads)

**Worker Failure:**
- Task automatically retried
- Moved to dead letter queue after 3 failures
- Manual intervention for DLQ items
