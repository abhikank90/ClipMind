# ClipMind AI Setup Guide

## Prerequisites

1. **FFmpeg** - Install system-wide:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

2. **Python 3.11+**

## Installation

### 1. Install AI Dependencies
```bash
cd backend
pip install -r requirements_ai.txt
```

### 2. Download Models (First Run)

Models will be downloaded automatically on first use:
- **CLIP**: ~600MB
- **Whisper**: 140MB (base) to 3GB (large-v3)
- **Sentence-BERT**: ~90MB (all-MiniLM-L6-v2)

### 3. Set Up Pinecone

1. Create account at https://www.pinecone.io
2. Create an index:
   - Dimensions: 512
   - Metric: cosine
3. Add API key to `.env`:
```bash
PINECONE_API_KEY=your-key-here
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=clipmind-embeddings
```

## Usage Examples

### Process a Video
```python
from app.workers.video_processor import VideoProcessor
from app.workers.scene_detector import SceneDetector
from app.ai.clip_model import CLIPEmbedder
from app.ai.whisper_model import WhisperTranscriber

# Extract metadata
processor = VideoProcessor()
metadata = processor.extract_metadata("video.mp4")

# Detect scenes
detector = SceneDetector()
scenes = detector.detect_scenes("video.mp4")

# Generate thumbnail
processor.generate_thumbnail("video.mp4", "thumbnail.jpg", timestamp=5.0)

# Extract audio
processor.extract_audio("video.mp4", "audio.wav")

# Transcribe
transcriber = WhisperTranscriber(model_size="base")
transcription = transcriber.transcribe("audio.wav")

# Generate embeddings
clip_model = CLIPEmbedder()
frames = processor.extract_frames("video.mp4", "frames/", fps=1)
embeddings = clip_model.encode_images_batch(frames)
```

### Search with Vector Similarity
```python
from app.search.pinecone_client import PineconeClient
from app.ai.clip_model import CLIPEmbedder

# Initialize
pinecone = PineconeClient(api_key="xxx", environment="xxx", index_name="clipmind")
clip_model = CLIPEmbedder()

# Index embeddings
vectors = [
    {
        'id': f'clip_{i}',
        'values': embedding.tolist(),
        'metadata': {'video_id': 'video_1', 'timestamp': i}
    }
    for i, embedding in enumerate(embeddings)
]
pinecone.upsert_vectors(vectors)

# Search
query_embedding = clip_model.encode_text("person smiling")
results = pinecone.query(query_embedding, top_k=10)
```

### Render Compilation
```python
from app.workers.compilation_renderer import CompilationRenderer

renderer = CompilationRenderer()

clips = [
    {'video_path': 'video1.mp4', 'start_time': 10, 'end_time': 20},
    {'video_path': 'video2.mp4', 'start_time': 5, 'end_time': 15},
]

success = renderer.render_compilation(
    clips=clips,
    output_path='compilation.mp4',
    music_path='background.mp3',
    transition='fade'
)
```

## GPU Support (Optional)

For faster processing with CUDA:

```bash
# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Check GPU availability:
```python
import torch
print(torch.cuda.is_available())  # Should print True
```

## Troubleshooting

### FFmpeg Not Found
```bash
# Verify FFmpeg is installed
ffmpeg -version
```

### Out of Memory
- Use smaller Whisper model (tiny/base instead of large)
- Reduce batch size for CLIP embeddings
- Process videos in chunks

### Slow Processing
- Use GPU if available
- Reduce video resolution
- Use faster Whisper model
