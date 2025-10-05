from celery import Task
from app.tasks.celery_app import celery_app
from app.orchestration.orchestrator import Orchestrator, WorkflowType
import logging

# Import AI models and processors
from app.workers.video_processor import VideoProcessor
from app.workers.scene_detector import SceneDetector
from app.ai.clip_model import CLIPEmbedder
from app.ai.whisper_model import WhisperTranscriber
from app.ai.sentence_bert import SentenceBERTEmbedder
from app.search.pinecone_client import PineconeClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")


@celery_app.task(base=CallbackTask, bind=True, max_retries=3)
def process_video_task(self, video_id: str, video_url: str):
    """
    Complete video processing pipeline with AI integration
    
    Steps:
    1. Extract metadata (FFmpeg)
    2. Generate thumbnail
    3. Extract audio
    4. Detect scenes (PySceneDetect)
    5. Transcribe audio (Whisper)
    6. Generate visual embeddings (CLIP)
    7. Generate text embeddings (Sentence-BERT)
    8. Index in Pinecone
    """
    try:
        logger.info(f"Starting video processing: {video_id}")
        
        # Initialize processors
        video_processor = VideoProcessor()
        scene_detector = SceneDetector()
        
        # Step 1: Extract metadata
        logger.info(f"Extracting metadata for {video_id}")
        metadata = video_processor.extract_metadata(video_url)
        
        # Step 2: Generate thumbnail
        logger.info(f"Generating thumbnail for {video_id}")
        thumbnail_path = f"/tmp/{video_id}_thumb.jpg"
        video_processor.generate_thumbnail(video_url, thumbnail_path)
        
        # Step 3: Extract audio
        logger.info(f"Extracting audio for {video_id}")
        audio_path = f"/tmp/{video_id}_audio.wav"
        video_processor.extract_audio(video_url, audio_path)
        
        # Step 4: Detect scenes
        logger.info(f"Detecting scenes for {video_id}")
        scenes = scene_detector.detect_scenes_adaptive(video_url)
        
        # Step 5: Transcribe audio (Whisper)
        logger.info(f"Transcribing audio for {video_id}")
        transcriber = WhisperTranscriber(model_size="base")
        transcription = transcriber.transcribe(audio_path)
        
        # Step 6: Extract frames for each scene
        logger.info(f"Extracting frames for {video_id}")
        frames_dir = f"/tmp/{video_id}_frames"
        frames = video_processor.extract_frames(
            video_url,
            frames_dir,
            fps=1  # 1 frame per second
        )
        
        # Step 7: Generate visual embeddings (CLIP)
        logger.info(f"Generating visual embeddings for {video_id}")
        clip_model = CLIPEmbedder()
        visual_embeddings = clip_model.encode_images_batch(frames, batch_size=8)
        
        # Step 8: Generate text embeddings (Sentence-BERT)
        logger.info(f"Generating text embeddings for {video_id}")
        text_embedder = SentenceBERTEmbedder()
        
        # Embed full transcript
        full_text_embedding = text_embedder.encode(transcription["text"])
        
        # Embed each segment
        segment_embeddings = []
        for segment in transcription["segments"]:
            seg_embedding = text_embedder.encode(segment["text"])
            segment_embeddings.append({
                "text": segment["text"],
                "start": segment["start"],
                "end": segment["end"],
                "embedding": seg_embedding
            })
        
        # Step 9: Index in Pinecone
        logger.info(f"Indexing embeddings in Pinecone for {video_id}")
        pinecone_client = PineconeClient(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
            index_name=settings.PINECONE_INDEX_NAME
        )
        
        # Prepare vectors for Pinecone
        vectors = []
        
        # Add visual embeddings (one per frame/scene)
        for i, (embedding, scene) in enumerate(zip(visual_embeddings, scenes)):
            vectors.append({
                'id': f"{video_id}_scene_{i}",
                'values': embedding.tolist(),
                'metadata': {
                    'video_id': video_id,
                    'type': 'visual',
                    'start_time': scene['start_time'],
                    'end_time': scene['end_time'],
                    'scene_number': scene['scene_number']
                }
            })
        
        # Add text embeddings (one per transcript segment)
        for i, seg_data in enumerate(segment_embeddings):
            vectors.append({
                'id': f"{video_id}_text_{i}",
                'values': seg_data['embedding'].tolist(),
                'metadata': {
                    'video_id': video_id,
                    'type': 'text',
                    'start_time': seg_data['start'],
                    'end_time': seg_data['end'],
                    'text': seg_data['text'][:500]  # Limit text length
                }
            })
        
        # Upsert to Pinecone
        pinecone_client.upsert_vectors(vectors)
        
        # Step 10: Save to database
        # TODO: Update database with metadata, scenes, transcription, etc.
        
        logger.info(f"Video processing completed: {video_id}")
        
        return {
            "video_id": video_id,
            "status": "completed",
            "scenes_count": len(scenes),
            "frames_count": len(frames),
            "transcript_length": len(transcription["text"]),
            "embeddings_indexed": len(vectors)
        }
        
    except Exception as e:
        logger.error(f"Video processing error: {str(e)}", exc_info=True)
        self.retry(exc=e, countdown=60)


@celery_app.task
def generate_clip_embeddings_task(clip_id: str, frame_path: str):
    """Generate embeddings for a single clip"""
    try:
        clip_model = CLIPEmbedder()
        embedding = clip_model.encode_image(frame_path)
        
        # Index in Pinecone
        pinecone_client = PineconeClient(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
            index_name=settings.PINECONE_INDEX_NAME
        )
        
        pinecone_client.upsert_vectors([{
            'id': clip_id,
            'values': embedding.tolist(),
            'metadata': {'clip_id': clip_id}
        }])
        
        return {"clip_id": clip_id, "status": "indexed"}
        
    except Exception as e:
        logger.error(f"Clip embedding error: {str(e)}")
        raise
