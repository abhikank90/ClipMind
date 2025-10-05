# ClipMind System Design

## Overview
ClipMind is an AI-powered video search platform built on event-driven architecture.

## Architecture Layers

### 1. API Layer (FastAPI)
- RESTful endpoints
- WebSocket for real-time updates
- JWT authentication
- Rate limiting

### 2. Processing Pipeline (Celery)
- Asynchronous video processing
- Scene detection with PySceneDetect
- AI model inference (CLIP, Whisper)
- Embedding generation

### 3. Storage Layer
- **S3**: Video files with lifecycle policies
- **PostgreSQL**: Relational metadata
- **Pinecone**: Vector embeddings (512-dim)
- **Elasticsearch**: Full-text search

### 4. AI Models
- **CLIP**: Visual understanding and embeddings
- **Whisper**: Audio transcription
- **Sentence-BERT**: Text embeddings

## Data Flow

1. User uploads video → S3
2. Celery worker triggered
3. Video processed (scenes, transcription, embeddings)
4. Embeddings indexed in Pinecone
5. Metadata stored in PostgreSQL
6. User searches → Vector + text search → Results

## Scalability

- API: Auto-scaling ECS tasks
- Workers: Scale based on queue depth
- Database: Read replicas
- Storage: S3 with CloudFront CDN
