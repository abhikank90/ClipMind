# ClipMind API Reference

Complete API documentation with request/response examples.

**Base URL:** `http://localhost:8000` (development) or `https://api.clipmind.com` (production)

**Interactive Documentation:** `/docs` (Swagger UI) or `/redoc` (ReDoc)

---

## Table of Contents

- [Authentication](#authentication)
- [Video Management](#video-management)
- [Search](#search)
- [Compilations](#compilations)
- [Analytics](#analytics)
- [Error Handling](#error-handling)

---

## Authentication

All API requests require JWT authentication.

### Obtain Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Use Token

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGc...
```

### Refresh Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

## Video Management

### Upload Video

```http
POST /api/v1/videos/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Parameters:
- file: video file (required)
- title: string (optional, default: "Untitled")
- project_id: string (optional)

Response 200:
{
  "video_id": "video_1704234567_abcd1234",
  "workflow_id": "workflow_video_1704234567_abcd1234",
  "filename": "my_video.mp4",
  "s3_url": "s3://clipmind-raw/users/user_123/videos/video_1704234567.mp4",
  "status": "processing"
}

Response 400:
{
  "detail": "File must be a video"
}
```

**Example with cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/videos/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/video.mp4" \
  -F "title=My Awesome Video"
```

### Get Video Details

```http
GET /api/v1/videos/{video_id}
Authorization: Bearer <token>

Response 200:
{
  "id": "video_1704234567_abcd1234",
  "title": "My Awesome Video",
  "filename": "my_video.mp4",
  "duration": 120.5,
  "width": 1920,
  "height": 1080,
  "fps": 30.0,
  "codec": "h264",
  "status": "processed",
  "thumbnail_url": "https://clipmind-thumbnails.s3.amazonaws.com/...",
  "video_url": "https://clipmind-raw.s3.amazonaws.com/...",
  "created_at": "2024-01-02T10:30:00Z",
  "processed_at": "2024-01-02T10:37:00Z"
}

Response 404:
{
  "detail": "Video not found"
}
```

### List Videos

```http
GET /api/v1/videos/?skip=0&limit=50
Authorization: Bearer <token>

Query Parameters:
- skip: integer (default: 0)
- limit: integer (default: 50, max: 100)
- status: string (optional: "pending", "processing", "processed", "failed")
- project_id: string (optional)

Response 200:
{
  "total": 100,
  "videos": [
    {
      "id": "video_123",
      "title": "Video 1",
      "duration": 120.5,
      "status": "processed",
      "thumbnail_url": "https://...",
      "created_at": "2024-01-01T10:00:00Z"
    },
    ...
  ]
}
```

### Delete Video

```http
DELETE /api/v1/videos/{video_id}
Authorization: Bearer <token>

Response 200:
{
  "message": "Video video_123 deleted"
}

Response 404:
{
  "detail": "Video not found"
}
```

---

## Search

### Search Videos

```http
POST /api/v1/search/
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "happy person dancing",
  "limit": 20,
  "video_ids": ["video_123", "video_456"]
}

Parameters:
- query: string (required) - Natural language search query
- limit: integer (default: 20, max: 100)
- video_ids: array of strings (optional) - Filter by specific videos

Response 200:
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
    },
    ...
  ]
}
```

**Example with cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/search/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sunset beach scene",
    "limit": 10
  }'
```

### Get Search History

```http
GET /api/v1/search/history?limit=50
Authorization: Bearer <token>

Query Parameters:
- limit: integer (default: 50, max: 100)

Response 200:
[
  {
    "search_id": "search_123",
    "query": "happy person dancing",
    "results_count": 15,
    "processing_time_ms": 234.5,
    "created_at": "2024-01-02T10:30:00Z"
  },
  ...
]
```

### Track Clip View

```http
POST /api/v1/search/track-view
Authorization: Bearer <token>
Content-Type: application/json

{
  "clip_id": "video_123_clip_5",
  "search_query_id": "search_1704234567_abcd1234",
  "duration_seconds": 15.3
}

Parameters:
- clip_id: string (required)
- search_query_id: string (optional)
- duration_seconds: float (optional) - How long user watched

Response 200:
{
  "status": "tracked",
  "clip_id": "video_123_clip_5"
}
```

### Get Popular Clips

```http
GET /api/v1/search/analytics/popular-clips?days=7&limit=10
Authorization: Bearer <token>

Query Parameters:
- days: integer (default: 7) - Time window
- limit: integer (default: 10)

Response 200:
{
  "popular_clips": [
    {
      "clip_id": "video_123_clip_5",
      "view_count": 23
    },
    ...
  ]
}
```

---

## Compilations

### Create Compilation

```http
POST /api/v1/compilations/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Best Moments",
  "description": "Compilation of best moments from Q4",
  "clip_ids": [
    "video_123_clip_5",
    "video_456_clip_2",
    "video_789_clip_8"
  ]
}

Response 200:
{
  "compilation_id": "comp_1704234567",
  "title": "Best Moments",
  "description": "Compilation of best moments from Q4",
  "status": "draft",
  "clips_count": 3,
  "created_at": "2024-01-02T10:30:00Z"
}
```

### Get Compilation

```http
GET /api/v1/compilations/{compilation_id}
Authorization: Bearer <token>

Response 200:
{
  "id": "comp_123",
  "title": "Best Moments",
  "description": "...",
  "status": "rendered",
  "clips_count": 3,
  "duration": 45.2,
  "output_url": "https://clipmind-processed.s3.amazonaws.com/compilations/comp_123.mp4",
  "thumbnail_url": "https://...",
  "created_at": "2024-01-02T10:30:00Z",
  "rendered_at": "2024-01-02T10:35:00Z"
}
```

### List Compilations

```http
GET /api/v1/compilations/?skip=0&limit=50
Authorization: Bearer <token>

Query Parameters:
- skip: integer (default: 0)
- limit: integer (default: 50)
- status: string (optional: "draft", "rendering", "rendered", "failed")

Response 200:
{
  "total": 10,
  "compilations": [...]
}
```

### Render Compilation

```http
POST /api/v1/compilations/{compilation_id}/render
Authorization: Bearer <token>

Response 200:
{
  "compilation_id": "comp_123",
  "job_id": "job_1704234567",
  "status": "rendering"
}
```

---

## Analytics

### Get Overall Statistics

```http
GET /api/v1/analytics/stats
Authorization: Bearer <token>

Response 200:
{
  "total_videos": 1234,
  "total_hours": 456.7,
  "searches_today": 89,
  "compilations": 23,
  "storage_used_gb": 567.8
}
```

### Get Recent Activity

```http
GET /api/v1/analytics/activity?limit=10
Authorization: Bearer <token>

Query Parameters:
- limit: integer (default: 10)

Response 200:
[
  {
    "type": "video_upload",
    "description": "New video uploaded: project_demo.mp4",
    "timestamp": "2024-01-02T10:30:00Z"
  },
  {
    "type": "search",
    "description": "Search: 'product demo highlights'",
    "timestamp": "2024-01-02T10:25:00Z"
  },
  ...
]
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Request data validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Examples

**Invalid Authentication:**
```json
Status: 401
{
  "detail": "Invalid authentication credentials"
}
```

**Validation Error:**
```json
Status: 422
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Rate Limit Exceeded:**
```json
Status: 429
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| Search | 100 requests/minute |
| Upload | 10 uploads/hour |
| All other endpoints | 1000 requests/hour |

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704234600
```

---

## Webhooks

Configure webhooks to receive notifications about video processing events.

### Webhook Events

- `video.processing.started`
- `video.processing.completed`
- `video.processing.failed`
- `compilation.rendering.completed`

### Webhook Payload Example

```json
{
  "event": "video.processing.completed",
  "video_id": "video_123",
  "timestamp": "2024-01-02T10:37:00Z",
  "data": {
    "duration": 120.5,
    "clips_generated": 15,
    "processing_time_seconds": 420
  }
}
```

---

## SDKs and Client Libraries

Official SDKs:
- Python: `pip install clipmind-sdk`
- JavaScript/TypeScript: `npm install clipmind-sdk`

Coming soon:
- Ruby
- Go
- PHP
