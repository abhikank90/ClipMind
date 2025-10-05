# ClipMind Search Documentation

## Complete Search Flow

### 1. User Searches

```
User enters query: "happy person dancing"
    ↓
POST /api/v1/search/
    ↓
SearchService.search()
    │
    ├─→ [1] Generate Embeddings
    │   ├─→ CLIP: text → 512-dim visual embedding
    │   └─→ Sentence-BERT: text → 384-dim text embedding
    │
    ├─→ [2] Search Pinecone
    │   ├─→ Query with visual embedding (top 40 results)
    │   ├─→ Query with text embedding (top 40 results)
    │   └─→ Merge with weighted fusion (visual*0.6 + text*0.4)
    │
    ├─→ [3] Enrich from PostgreSQL
    │   ├─→ Fetch clip details (start/end times, transcript)
    │   ├─→ Fetch video details (title, metadata)
    │   └─→ Verify user ownership
    │
    ├─→ [4] Generate S3 URLs
    │   ├─→ Presigned thumbnail URLs (1 hour expiry)
    │   └─→ Presigned clip playback URLs (1 hour expiry)
    │
    ├─→ [5] Save Analytics
    │   ├─→ INSERT INTO search_queries (query, user, results_count)
    │   └─→ INSERT INTO search_results (clip_id, rank, score)
    │
    └─→ [6] Return Complete Results
        └─→ JSON with all data + presigned URLs
```

### 2. User Clicks Result

```
User clicks clip in search results
    ↓
Frontend calls: POST /api/v1/search/track-view
    {
      "clip_id": "video_123_clip_5",
      "search_query_id": "search_456",
      "duration_seconds": 15.3
    }
    ↓
INSERT INTO clip_interactions
    (user_id, clip_id, action="viewed", duration_seconds)
```

## What Gets Saved

### Search Query
```sql
search_queries table:
- id: "search_1704234567_abcd1234"
- user_id: "user_123"
- query_text: "happy person dancing"
- results_count: 15
- processing_time_ms: 234.5
- created_at: "2024-01-02T10:30:00Z"
```

### Search Results
```sql
search_results table:
- id: "search_1704234567_abcd1234_result_1"
- search_query_id: "search_1704234567_abcd1234"
- clip_id: "video_123_clip_5"
- rank: 1
- relevance_score: 0.92
```

### Clip Interactions
```sql
clip_interactions table:
- id: "interaction_1704234590_abcd1234"
- user_id: "user_123"
- clip_id: "video_123_clip_5"
- search_query_id: "search_1704234567_abcd1234"
- action: "viewed"
- duration_seconds: 15.3
- created_at: "2024-01-02T10:30:30Z"
```

## API Endpoints

### Search Videos
```http
POST /api/v1/search/
Content-Type: application/json

{
  "query": "happy person dancing",
  "limit": 20,
  "video_ids": ["video_123", "video_456"]  // Optional filter
}

Response:
{
  "query": "happy person dancing",
  "search_id": "search_1704234567_abcd1234",
  "total_results": 15,
  "processing_time_ms": 234.5,
  "clips": [
    {
      "clip_id": "video_123_clip_5",
      "video_id": "video_123",
      "video_title": "Summer Party 2024",
      "start_time": 45.2,
      "end_time": 52.8,
      "duration": 7.6,
      "relevance_score": 0.92,
      "thumbnail_url": "https://clipmind-thumbnails.s3.amazonaws.com/...",
      "clip_url": "https://clipmind-raw.s3.amazonaws.com/...#t=45.2,52.8",
      "transcript": "Everyone was so happy dancing together...",
      "created_at": "2024-01-01T15:30:00Z"
    }
  ]
}
```

### Get Search History
```http
GET /api/v1/search/history?limit=50

Response:
[
  {
    "search_id": "search_1704234567_abcd1234",
    "query": "happy person dancing",
    "results_count": 15,
    "processing_time_ms": 234.5,
    "created_at": "2024-01-02T10:30:00Z"
  }
]
```

### Track Clip View
```http
POST /api/v1/search/track-view
Content-Type: application/json

{
  "clip_id": "video_123_clip_5",
  "search_query_id": "search_1704234567_abcd1234",
  "duration_seconds": 15.3
}

Response:
{
  "status": "tracked",
  "clip_id": "video_123_clip_5"
}
```

### Get Popular Clips
```http
GET /api/v1/search/analytics/popular-clips?days=7&limit=10

Response:
{
  "popular_clips": [
    {
      "clip_id": "video_123_clip_5",
      "view_count": 23
    }
  ]
}
```

## Frontend Integration

### Search Component
```typescript
// Search for clips
const searchClips = async (query: string) => {
  const response = await fetch('/api/v1/search/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit: 20 })
  });
  
  const data = await response.json();
  setSearchResults(data.clips);
  setSearchId(data.search_id);
};

// Track when user clicks a result
const handleClipClick = async (clipId: string) => {
  await fetch('/api/v1/search/track-view', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      clip_id: clipId,
      search_query_id: searchId
    })
  });
  
  // Play the clip
  playClip(clipId);
};

// Track viewing duration
const trackViewDuration = async (clipId: string, duration: number) => {
  await fetch('/api/v1/search/track-view', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      clip_id: clipId,
      search_query_id: searchId,
      duration_seconds: duration
    })
  });
};
```

## Analytics Queries

### Most Popular Search Terms
```sql
SELECT 
  query_text,
  COUNT(*) as search_count,
  AVG(results_count) as avg_results,
  AVG(processing_time_ms) as avg_time_ms
FROM search_queries
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY query_text
ORDER BY search_count DESC
LIMIT 20;
```

### Click-Through Rate
```sql
SELECT 
  sq.query_text,
  COUNT(DISTINCT sq.id) as total_searches,
  COUNT(DISTINCT ci.id) as total_clicks,
  ROUND(COUNT(DISTINCT ci.id)::numeric / COUNT(DISTINCT sq.id) * 100, 2) as ctr_percentage
FROM search_queries sq
LEFT JOIN clip_interactions ci ON sq.id = ci.search_query_id
WHERE sq.created_at > NOW() - INTERVAL '7 days'
GROUP BY sq.query_text
HAVING COUNT(DISTINCT sq.id) > 5
ORDER BY ctr_percentage DESC;
```

### Average Watch Time by Clip
```sql
SELECT 
  c.id,
  c.video_id,
  c.start_time,
  c.end_time,
  COUNT(ci.id) as view_count,
  AVG(ci.duration_seconds) as avg_watch_time,
  c.end_time - c.start_time as clip_duration
FROM clips c
JOIN clip_interactions ci ON c.id = ci.clip_id
WHERE ci.action = 'viewed'
GROUP BY c.id
ORDER BY view_count DESC
LIMIT 20;
```

## Performance Optimization

### Caching Popular Searches
```python
# Cache search results for common queries
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_search(query_hash: str):
    # Return cached results if available
    pass
```

### Database Indexes
```sql
-- Already created in migration
CREATE INDEX ix_search_queries_user_id ON search_queries(user_id);
CREATE INDEX ix_search_queries_created_at ON search_queries(created_at);
CREATE INDEX ix_clip_interactions_clip_id ON clip_interactions(clip_id);
CREATE INDEX ix_clip_interactions_created_at ON clip_interactions(created_at);
```
