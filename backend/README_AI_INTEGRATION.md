# ClipMind AI Integration Guide

## How AI Models Are Integrated

### Architecture Overview

```
Video Upload
    ↓
Celery Task (process_video_task)
    ↓
┌─────────────────────────────────────┐
│   AI Processing Workflow            │
├─────────────────────────────────────┤
│ 1. FFmpeg (metadata/audio)          │
│ 2. PySceneDetect (scenes)           │
│ 3. Whisper (transcription)          │
│ 4. CLIP (visual embeddings)         │
│ 5. Sentence-BERT (text embeddings)  │
│ 6. Pinecone (vector indexing)       │
└─────────────────────────────────────┘
    ↓
Database + Vector Store
    ↓
Search API
    ↓
Results to User
```

### Integration Points

#### 1. Video Processing (app/tasks/video_tasks.py)
- **Entry Point**: `process_video_task(video_id, video_url)`
- **AI Models Used**:
  - VideoProcessor (FFmpeg)
  - SceneDetector (PySceneDetect)
  - WhisperTranscriber (Whisper)
  - CLIPEmbedder (CLIP)
  - SentenceBERTEmbedder (Sentence-BERT)
- **Output**: Embeddings indexed in Pinecone

#### 2. Search (app/services/search_service.py)
- **Entry Point**: `SearchService.search(query, user_id, filters, limit)`
- **AI Models Used**:
  - CLIPEmbedder (query → visual embedding)
  - SentenceBERTEmbedder (query → text embedding)
  - PineconeClient (vector similarity search)
- **Output**: Ranked search results

#### 3. Workflow Orchestration (app/orchestration/workflows/ai_processing.py)
- **Entry Point**: `AIProcessingWorkflow.execute(workflow_id, context)`
- **Coordinates**: All AI models in sequence
- **Output**: Complete video analysis

### File Locations

```
backend/app/
├── ai/
│   ├── clip_model.py           ← CLIP integration
│   ├── whisper_model.py        ← Whisper integration
│   └── sentence_bert.py        ← Sentence-BERT integration
├── search/
│   └── pinecone_client.py      ← Pinecone integration
├── workers/
│   ├── video_processor.py      ← FFmpeg integration
│   └── scene_detector.py       ← PySceneDetect integration
├── tasks/
│   └── video_tasks.py          ← **MAIN ENTRY POINT**
├── services/
│   └── search_service.py       ← **SEARCH ENTRY POINT**
└── orchestration/workflows/
    └── ai_processing.py        ← **WORKFLOW ENTRY POINT**
```

### Example: End-to-End Flow

1. **User uploads video** → API endpoint
2. **API triggers** → `process_video_task.delay(video_id, s3_url)`
3. **Celery worker executes**:
   ```python
   # Extract metadata
   metadata = video_processor.extract_metadata(video_url)
   
   # Detect scenes
   scenes = scene_detector.detect_scenes_adaptive(video_url)
   
   # Transcribe
   transcription = transcriber.transcribe(audio_path)
   
   # Generate embeddings
   visual_embeddings = clip_model.encode_images_batch(frames)
   text_embeddings = text_embedder.encode(transcription["text"])
   
   # Index in Pinecone
   pinecone_client.upsert_vectors(vectors)
   ```

4. **User searches** → API endpoint
5. **Search service executes**:
   ```python
   # Generate query embeddings
   clip_embedding = clip_model.encode_text(query)
   text_embedding = text_embedder.encode(query)
   
   # Search Pinecone
   visual_results = pinecone_client.query(clip_embedding)
   text_results = pinecone_client.query(text_embedding)
   
   # Merge and rank
   return merged_results
   ```

### Configuration

All AI integrations use settings from `app/core/config.py`:

```python
# .env file
PINECONE_API_KEY=your-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=clipmind-embeddings
```

### Testing AI Integration

```bash
# Test video processing
cd backend
poetry run python -c "
from app.tasks.video_tasks import process_video_task
result = process_video_task('test-1', '/path/to/video.mp4')
print(result)
"

# Test search
poetry run python -c "
from app.services.search_service import SearchService
import asyncio

async def test():
    service = SearchService()
    results = await service.search('happy person', 'user-1', None, 10)
    print(results)

asyncio.run(test())
"
```

### Performance Notes

- **CLIP**: ~500ms per image on CPU, ~50ms on GPU
- **Whisper**: ~30s per minute of audio (base model)
- **Sentence-BERT**: ~10ms per sentence
- **Pinecone**: <100ms query latency

### Scaling Considerations

1. **Use GPU** for CLIP and Whisper (10x faster)
2. **Batch processing** for embeddings
3. **Async workers** for parallel processing
4. **Cache embeddings** to avoid recomputation
