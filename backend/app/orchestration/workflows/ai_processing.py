from typing import Dict, Any, List
import logging
import os

# Import AI models and processors
from app.workers.video_processor import VideoProcessor
from app.workers.scene_detector import SceneDetector
from app.ai.clip_model import CLIPEmbedder
from app.ai.whisper_model import WhisperTranscriber
from app.ai.sentence_bert import SentenceBERTEmbedder
from app.search.pinecone_client import PineconeClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProcessingWorkflow:
    """
    Complete AI processing workflow with real integrations
    """
    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.scene_detector = SceneDetector()
        self.clip_model = CLIPEmbedder()
        self.transcriber = WhisperTranscriber(model_size="base")
        self.text_embedder = SentenceBERTEmbedder()
        self.pinecone_client = PineconeClient(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
            index_name=settings.PINECONE_INDEX_NAME
        )
    
    async def execute(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete AI processing pipeline"""
        video_id = context.get("video_id")
        video_url = context.get("video_url")
        
        logger.info(f"AI processing workflow started: {workflow_id}")
        
        try:
            # Step 1: Detect scenes
            scenes = await self._detect_scenes(video_url)
            
            # Step 2: Extract and transcribe audio
            transcript = await self._transcribe_audio(video_url)
            
            # Step 3: Generate visual embeddings
            visual_embeddings = await self._generate_visual_embeddings(video_url, scenes)
            
            # Step 4: Generate text embeddings
            text_embeddings = await self._generate_text_embeddings(transcript)
            
            # Step 5: Index everything in Pinecone
            await self._index_embeddings(video_id, visual_embeddings, text_embeddings)
            
            return {
                "workflow_id": workflow_id,
                "video_id": video_id,
                "status": "completed",
                "scenes_count": len(scenes),
                "transcript_length": len(transcript.get("text", "")),
                "embeddings_indexed": len(visual_embeddings) + len(text_embeddings)
            }
            
        except Exception as e:
            logger.error(f"AI processing failed: {str(e)}", exc_info=True)
            raise
    
    async def _detect_scenes(self, video_url: str) -> List[Dict[str, Any]]:
        """Detect scene boundaries using PySceneDetect"""
        logger.info(f"Detecting scenes: {video_url}")
        scenes = self.scene_detector.detect_scenes_adaptive(video_url)
        return scenes
    
    async def _transcribe_audio(self, video_url: str) -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        logger.info(f"Transcribing audio: {video_url}")
        
        # Extract audio first
        audio_path = f"/tmp/{os.path.basename(video_url)}_audio.wav"
        self.video_processor.extract_audio(video_url, audio_path)
        
        # Transcribe
        transcript = self.transcriber.transcribe(audio_path)
        
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return transcript
    
    async def _generate_visual_embeddings(
        self,
        video_url: str,
        scenes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate CLIP embeddings for video frames"""
        logger.info(f"Generating visual embeddings: {video_url}")
        
        # Extract frames (1 per scene or 1 per second)
        frames_dir = f"/tmp/{os.path.basename(video_url)}_frames"
        frames = self.video_processor.extract_frames(video_url, frames_dir, fps=1)
        
        # Generate embeddings
        embeddings = self.clip_model.encode_images_batch(frames, batch_size=8)
        
        # Combine with scene info
        result = []
        for i, (embedding, scene) in enumerate(zip(embeddings, scenes)):
            result.append({
                "scene_number": i,
                "embedding": embedding,
                "start_time": scene["start_time"],
                "end_time": scene["end_time"]
            })
        
        # Cleanup frames
        if os.path.exists(frames_dir):
            import shutil
            shutil.rmtree(frames_dir)
        
        return result
    
    async def _generate_text_embeddings(
        self,
        transcript: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate Sentence-BERT embeddings for transcript"""
        logger.info(f"Generating text embeddings")
        
        result = []
        
        # Generate embedding for each segment
        for segment in transcript.get("segments", []):
            embedding = self.text_embedder.encode(segment["text"])
            result.append({
                "text": segment["text"],
                "embedding": embedding,
                "start_time": segment["start"],
                "end_time": segment["end"]
            })
        
        return result
    
    async def _index_embeddings(
        self,
        video_id: str,
        visual_embeddings: List[Dict[str, Any]],
        text_embeddings: List[Dict[str, Any]]
    ) -> None:
        """Index all embeddings in Pinecone"""
        logger.info(f"Indexing embeddings in Pinecone: {video_id}")
        
        vectors = []
        
        # Add visual embeddings
        for i, data in enumerate(visual_embeddings):
            vectors.append({
                'id': f"{video_id}_visual_{i}",
                'values': data['embedding'].tolist(),
                'metadata': {
                    'video_id': video_id,
                    'type': 'visual',
                    'start_time': data['start_time'],
                    'end_time': data['end_time'],
                    'scene_number': data['scene_number']
                }
            })
        
        # Add text embeddings
        for i, data in enumerate(text_embeddings):
            vectors.append({
                'id': f"{video_id}_text_{i}",
                'values': data['embedding'].tolist(),
                'metadata': {
                    'video_id': video_id,
                    'type': 'text',
                    'start_time': data['start_time'],
                    'end_time': data['end_time'],
                    'text': data['text'][:500]
                }
            })
        
        # Upsert to Pinecone in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.pinecone_client.upsert_vectors(batch)
        
        logger.info(f"Indexed {len(vectors)} vectors in Pinecone")
