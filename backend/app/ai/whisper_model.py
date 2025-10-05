import logging
import whisper
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model
        
        model_size: tiny, base, small, medium, large, large-v2, large-v3
        """
        logger.info(f"Loading Whisper {model_size} model")
        self.model = whisper.load_model(model_size)
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio file
        
        Returns:
            {
                'text': full transcription,
                'segments': list of segments with timestamps,
                'language': detected language
            }
        """
        try:
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                fp16=False  # Set to True if using GPU
            )
            
            logger.info(f"Transcribed {audio_path}: {len(result['segments'])} segments")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "text": "",
                "segments": [],
                "language": "unknown"
            }
    
    def transcribe_with_word_timestamps(self, audio_path: str) -> List[Dict[str, Any]]:
        """Transcribe with word-level timestamps"""
        try:
            result = self.model.transcribe(
                audio_path,
                word_timestamps=True
            )
            
            words = []
            for segment in result["segments"]:
                for word_info in segment.get("words", []):
                    words.append({
                        "word": word_info["word"],
                        "start": word_info["start"],
                        "end": word_info["end"],
                        "probability": word_info.get("probability", 0.0)
                    })
            
            return words
            
        except Exception as e:
            logger.error(f"Word-level transcription failed: {e}")
            return []
    
    def detect_language(self, audio_path: str) -> str:
        """Detect the language of the audio"""
        try:
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            _, probs = self.model.detect_language(mel)
            
            detected_language = max(probs, key=probs.get)
            logger.info(f"Detected language: {detected_language}")
            
            return detected_language
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "en"
