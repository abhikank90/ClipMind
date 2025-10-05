import subprocess
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"  # Assumes ffmpeg is in PATH
        self.ffprobe_path = "ffprobe"
    
    def extract_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata using ffprobe"""
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            metadata = json.loads(result.stdout)
            
            video_stream = next(
                (s for s in metadata.get("streams", []) if s["codec_type"] == "video"),
                {}
            )
            
            return {
                "duration": float(metadata.get("format", {}).get("duration", 0)),
                "size_bytes": int(metadata.get("format", {}).get("size", 0)),
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                "codec": video_stream.get("codec_name", "unknown"),
            }
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    def generate_thumbnail(self, video_path: str, output_path: str, timestamp: float = 1.0) -> bool:
        """Generate thumbnail at specified timestamp"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-ss", str(timestamp),
                "-vframes", "1",
                "-q:v", "2",
                output_path,
                "-y"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return False
    
    def extract_audio(self, video_path: str, output_path: str) -> bool:
        """Extract audio track from video"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # WAV format for Whisper
                "-ar", "16000",  # 16kHz sample rate
                "-ac", "1",  # Mono
                output_path,
                "-y"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            return False
    
    def extract_frames(self, video_path: str, output_dir: str, fps: float = 1.0) -> list[str]:
        """Extract frames at specified FPS"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-vf", f"fps={fps}",
                os.path.join(output_dir, "frame_%04d.jpg"),
                "-y"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Get list of generated frames
            frames = sorted([
                os.path.join(output_dir, f)
                for f in os.listdir(output_dir)
                if f.startswith("frame_") and f.endswith(".jpg")
            ])
            
            return frames
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return []
    
    def transcode_video(
        self,
        input_path: str,
        output_path: str,
        codec: str = "libx264",
        quality: str = "medium"
    ) -> bool:
        """Transcode video to standard format"""
        try:
            preset_map = {
                "fast": "ultrafast",
                "medium": "medium",
                "high": "slow"
            }
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-c:v", codec,
                "-preset", preset_map.get(quality, "medium"),
                "-c:a", "aac",
                "-b:a", "128k",
                output_path,
                "-y"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Transcoding failed: {e}")
            return False
