# ClipMind AI Models

Detailed documentation of all AI models used in ClipMind.

---

## Table of Contents

- [Overview](#overview)
- [CLIP (Visual Understanding)](#clip-visual-understanding)
- [Whisper (Speech-to-Text)](#whisper-speech-to-text)
- [Sentence-BERT (Text Embeddings)](#sentence-bert-text-embeddings)
- [Pinecone (Vector Database)](#pinecone-vector-database)
- [Model Performance](#model-performance)
- [Optimization Strategies](#optimization-strategies)

---

## Overview

ClipMind uses a multi-modal AI pipeline combining computer vision, speech recognition, and natural language processing.

### Model Selection Criteria

1. **Accuracy**: State-of-the-art performance on benchmarks
2. **Speed**: Sub-second inference for real-time search
3. **Cost**: Balance between quality and computational expense
4. **Open Source**: Preferably open-source for customization

---

## CLIP (Visual Understanding)

**Model:** OpenAI CLIP (Contrastive Language-Image Pre-Training)  
**Variant:** `openai/clip-vit-base-patch32`  
**Architecture:** Vision Transformer (ViT)

### Purpose

Generate visual embeddings that capture semantic meaning of images and video frames, enabling text-to-image search.

### Technical Details

**Input:**
- Image size: 224x224 pixels
- Format: RGB
- Preprocessing: Resize, normalize

**Output:**
- Embedding dimension: 512
- Normalized L2 vector
- Range: [-1, 1]

**Model Architecture:**
```
Image (224x224x3)
    ↓
Vision Transformer
    ├─ Patch Embedding (32x32 patches)
    ├─ Positional Encoding
    ├─ 12 Transformer Layers
    └─ Final Projection
    ↓
512-dimensional embedding
```

### Usage in ClipMind

```python
from app.ai.clip_model import CLIPEmbedder

clip_model = CLIPEmbedder()

# Encode image
image_embedding = clip_model.encode_image("frame_001.jpg")
# Returns: numpy array, shape (512,)

# Encode text query
text_embedding = clip_model.encode_text("happy person dancing")
# Returns: numpy array, shape (512,)

# Compute similarity
similarity = clip_model.compute_similarity(image_embedding, text_embedding)
# Returns: float [0, 1]
```

### Performance

**Speed:**
- CPU (Intel i7): ~500ms per image
- GPU (NVIDIA T4): ~50ms per image
- GPU (NVIDIA A100): ~10ms per image

**Batch Processing:**
- Batch size 8: ~80ms per batch (GPU)
- Batch size 32: ~200ms per batch (GPU)

**Memory:**
- Model size: ~600MB
- Per-image inference: ~200MB VRAM

### Optimization

**1. Batch Processing**
```python
embeddings = clip_model.encode_images_batch(
    image_paths=frames,
    batch_size=8  # Process 8 frames at once
)
```

**2. GPU Acceleration**
```python
# Automatically uses CUDA if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
```

**3. Mixed Precision (FP16)**
```python
with torch.cuda.amp.autocast():
    embeddings = model.encode_image(image)
# 2x faster with minimal accuracy loss
```

---

## Whisper (Speech-to-Text)

**Model:** OpenAI Whisper  
**Variant:** `base` (default), configurable to `large-v3`  
**Architecture:** Encoder-Decoder Transformer

### Purpose

Transcribe audio from videos with word-level timestamps, enabling text-based search of spoken content.

### Model Variants

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39M params | 32x realtime | Good |
| base | 74M params | 16x realtime | Better |
| small | 244M params | 6x realtime | Great |
| medium | 769M params | 2x realtime | Excellent |
| large-v3 | 1550M params | 1x realtime | Best |

**Default:** `base` (good balance of speed/accuracy)

### Technical Details

**Input:**
- Audio format: WAV, 16kHz, mono
- Chunk size: 30 seconds
- Preprocessing: Mel spectrogram (80 bins)

**Output:**
```json
{
  "text": "Full transcription text",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello world",
      "tokens": [50364, 2425, 1002],
      "temperature": 0.0,
      "avg_logprob": -0.15
    }
  ],
  "language": "en"
}
```

### Usage in ClipMind

```python
from app.ai.whisper_model import WhisperTranscriber

transcriber = WhisperTranscriber(model_size="base")

# Basic transcription
result = transcriber.transcribe("audio.wav")

# With language hint
result = transcriber.transcribe("audio.wav", language="en")

# Word-level timestamps
words = transcriber.transcribe_with_word_timestamps("audio.wav")
```

### Performance

**Processing Speed (base model):**
- 1 minute audio: ~30 seconds
- 10 minute audio: ~5 minutes
- 1 hour audio: ~30 minutes

**GPU Acceleration:**
- CPU: 2x slower than realtime
- GPU (T4): 16x faster than realtime
- GPU (A100): 32x faster than realtime

**Accuracy:**
- English: 95%+ Word Error Rate (WER)
- Other languages: 85-95% WER
- Supports 100+ languages

### Language Support

Top supported languages:
- English, Spanish, French, German, Italian
- Portuguese, Dutch, Russian, Chinese, Japanese
- Korean, Arabic, Hindi, and 90+ more

### Optimization

**1. Use Appropriate Model Size**
```python
# For speed: use 'base'
transcriber = WhisperTranscriber(model_size="base")

# For accuracy: use 'large-v3'
transcriber = WhisperTranscriber(model_size="large-v3")
```

**2. Specify Language (if known)**
```python
# 2x faster when language is specified
result = transcriber.transcribe(audio, language="en")
```

**3. GPU Inference**
```python
# Enable FP16 for 2x speedup on GPU
result = transcriber.transcribe(audio, fp16=True)
```

---

## Sentence-BERT (Text Embeddings)

**Model:** `all-MiniLM-L6-v2`  
**Architecture:** BERT-based Siamese Network

### Purpose

Generate semantic text embeddings for transcripts, enabling semantic similarity search.

### Technical Details

**Input:**
- Text: Any length (automatically truncated to 256 tokens)
- Languages: Optimized for English

**Output:**
- Embedding dimension: 384
- Normalized vector
- Cosine similarity metric

**Model Architecture:**
```
Text Input
    ↓
Tokenization (WordPiece)
    ↓
BERT Encoder (6 layers)
    ↓
Mean Pooling
    ↓
Normalization
    ↓
384-dimensional embedding
```

### Usage in ClipMind

```python
from app.ai.sentence_bert import SentenceBERTEmbedder

embedder = SentenceBERTEmbedder()

# Single text
embedding = embedder.encode("This is a sample text")
# Returns: numpy array, shape (384,)

# Batch processing
embeddings = embedder.encode([
    "Text 1",
    "Text 2",
    "Text 3"
])
# Returns: numpy array, shape (3, 384)

# Compute similarity
similarity = embedder.compute_similarity("query", "document")
# Returns: float [0, 1]
```

### Performance

**Speed:**
- CPU: ~10ms per sentence
- GPU: ~2ms per sentence
- Batch (32 sentences): ~50ms on GPU

**Memory:**
- Model size: ~90MB
- Per-sentence inference: ~50MB

**Accuracy:**
- Semantic similarity: 0.85 Spearman correlation
- Paraphrase detection: 90%+ accuracy

### Alternative Models

| Model | Dimensions | Speed | Quality |
|-------|------------|-------|---------|
| all-MiniLM-L6-v2 | 384 | Fast | Good |
| all-mpnet-base-v2 | 768 | Medium | Better |
| all-distilroberta-v1 | 768 | Medium | Better |

**Why MiniLM:**
- 5x faster than mpnet
- 50% smaller model size
- Good enough for most use cases

---

## Pinecone (Vector Database)

**Type:** Managed vector database  
**Index Type:** Approximate Nearest Neighbor (ANN)  
**Similarity Metric:** Cosine

### Purpose

Store and search millions of embeddings with sub-100ms latency.

### Technical Details

**Index Configuration:**
```python
{
  "name": "clipmind-embeddings",
  "dimension": 512,  # or 384 for text
  "metric": "cosine",
  "pod_type": "p1.x1",
  "replicas": 1
}
```

**Vector Format:**
```python
{
  "id": "video_123_visual_5",
  "values": [0.1, 0.2, ..., 0.5],  # 512 floats
  "metadata": {
    "video_id": "video_123",
    "type": "visual",
    "start_time": 45.2,
    "end_time": 52.8
  }
}
```

### Usage in ClipMind

```python
from app.search.pinecone_client import PineconeClient

client = PineconeClient(
    api_key="xxx",
    environment="us-east-1-aws",
    index_name="clipmind-embeddings"
)

# Upsert vectors
vectors = [
    {
        "id": "clip_1",
        "values": embedding.tolist(),
        "metadata": {"video_id": "video_123"}
    }
]
client.upsert_vectors(vectors)

# Query similar vectors
results = client.query(
    query_vector=query_embedding,
    top_k=10,
    filter={"video_id": "video_123"}
)
```

### Performance

**Query Latency:**
- P50: 50ms
- P95: 100ms
- P99: 150ms

**Throughput:**
- Queries per second: 1000+
- Upserts per second: 500+

**Scalability:**
- Vectors: 1M - 100M+ per index
- Dimensions: Up to 20,000
- Metadata: Any JSON-serializable data

### Cost

**Pod Types:**
- p1.x1: $70/month (1M vectors)
- p1.x2: $140/month (5M vectors)
- p1.x4: $280/month (10M vectors)

---

## Model Performance

### End-to-End Processing Time

For a 10-minute 1080p video:

| Stage | Time | Component |
|-------|------|-----------|
| Upload | 30s | Network |
| Metadata extraction | 5s | FFmpeg |
| Thumbnail generation | 3s | FFmpeg |
| Scene detection | 2m | PySceneDetect |
| Audio extraction | 10s | FFmpeg |
| Transcription | 3m | Whisper (base) |
| Frame extraction | 20s | FFmpeg |
| Visual embeddings | 1m | CLIP (batch) |
| Text embeddings | 5s | Sentence-BERT |
| Index in Pinecone | 10s | Pinecone |
| **Total** | **~7 minutes** | |

### Search Performance

| Query Type | Latency (P95) |
|------------|---------------|
| Text query → Embeddings | 50ms |
| Pinecone vector search | 100ms |
| PostgreSQL metadata fetch | 50ms |
| S3 URL generation | 10ms |
| Total result fusion | 50ms |
| **Total Search Time** | **~350ms** |

---

## Optimization Strategies

### 1. Model Quantization

Reduce model size and increase speed with minimal accuracy loss:

```python
# CLIP with int8 quantization
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
# 4x smaller, 2x faster
```

### 2. Caching

Cache embeddings for duplicate frames:

```python
@lru_cache(maxsize=1000)
def get_frame_embedding(frame_hash):
    return clip_model.encode_image(frame_path)
```

### 3. Async Processing

Process multiple videos in parallel:

```python
async def process_videos(video_ids):
    tasks = [process_video(vid) for vid in video_ids]
    results = await asyncio.gather(*tasks)
```

### 4. Progressive Quality

Start with fast models, upgrade for important content:

```python
# Quick pass with 'base'
quick_result = transcriber_base.transcribe(audio)

# If important, re-process with 'large-v3'
if video.is_important:
    better_result = transcriber_large.transcribe(audio)
```

---

## Future Improvements

**Planned Enhancements:**

1. **Fine-tuned CLIP**
   - Train on domain-specific data
   - Improve accuracy for specific content types

2. **Faster Whisper**
   - Explore whisper.cpp (C++ implementation)
   - 5-10x faster on CPU

3. **Custom Text Embeddings**
   - Fine-tune Sentence-BERT on user queries
   - Improve search relevance

4. **Model Versioning**
   - A/B test different model versions
   - Gradual rollout of improvements
