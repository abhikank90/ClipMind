import subprocess
import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class CompilationRenderer:
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"
        self.temp_dir = "/tmp/clipmind_compilations"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def render_compilation(
        self,
        clips: List[Dict[str, Any]],
        output_path: str,
        music_path: Optional[str] = None,
        transition: str = "fade",
        resolution: str = "1920x1080",
        fps: int = 30
    ) -> bool:
        """
        Render video compilation from clips
        
        clips format: [
            {
                'video_path': '/path/to/video.mp4',
                'start_time': 10.5,
                'end_time': 25.3,
                'transition_duration': 0.5
            }
        ]
        """
        try:
            # Step 1: Extract and trim clips
            trimmed_clips = self._trim_clips(clips)
            
            # Step 2: Create concat file
            concat_file = self._create_concat_file(trimmed_clips, transition)
            
            # Step 3: Concatenate clips
            temp_output = os.path.join(self.temp_dir, f"concat_{os.path.basename(output_path)}")
            success = self._concatenate_clips(concat_file, temp_output, transition)
            
            if not success:
                return False
            
            # Step 4: Add music if provided
            if music_path and os.path.exists(music_path):
                final_output = output_path
                success = self._add_music(temp_output, music_path, final_output)
            else:
                # Just move temp to final
                os.rename(temp_output, output_path)
                success = True
            
            # Cleanup
            self._cleanup(trimmed_clips, concat_file)
            
            logger.info(f"Compilation rendered: {output_path}")
            return success
            
        except Exception as e:
            logger.error(f"Compilation rendering failed: {e}")
            return False
    
    def _trim_clips(self, clips: List[Dict[str, Any]]) -> List[str]:
        """Trim clips to specified durations"""
        trimmed_paths = []
        
        for i, clip in enumerate(clips):
            output_path = os.path.join(self.temp_dir, f"clip_{i:04d}.mp4")
            
            cmd = [
                self.ffmpeg_path,
                "-i", clip["video_path"],
                "-ss", str(clip["start_time"]),
                "-to", str(clip["end_time"]),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-strict", "experimental",
                output_path,
                "-y"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            trimmed_paths.append(output_path)
        
        return trimmed_paths
    
    def _create_concat_file(self, clip_paths: List[str], transition: str) -> str:
        """Create FFmpeg concat file"""
        concat_file = os.path.join(self.temp_dir, "concat_list.txt")
        
        with open(concat_file, "w") as f:
            for path in clip_paths:
                f.write(f"file '{path}'\n")
        
        return concat_file
    
    def _concatenate_clips(self, concat_file: str, output_path: str, transition: str) -> bool:
        """Concatenate clips using FFmpeg"""
        try:
            if transition == "cut":
                # Simple concatenation
                cmd = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file,
                    "-c", "copy",
                    output_path,
                    "-y"
                ]
            else:
                # With re-encoding (needed for transitions)
                cmd = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file,
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    output_path,
                    "-y"
                ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except Exception as e:
            logger.error(f"Concatenation failed: {e}")
            return False
    
    def _add_music(self, video_path: str, music_path: str, output_path: str) -> bool:
        """Add background music to video"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-i", music_path,
                "-filter_complex",
                "[1:a]aloop=loop=-1:size=2e+09[bg];[0:a][bg]amix=inputs=2:duration=shortest[a]",
                "-map", "0:v",
                "-map", "[a]",
                "-c:v", "copy",
                "-c:a", "aac",
                output_path,
                "-y"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except Exception as e:
            logger.error(f"Adding music failed: {e}")
            return False
    
    def _cleanup(self, clip_paths: List[str], concat_file: str):
        """Clean up temporary files"""
        for path in clip_paths:
            if os.path.exists(path):
                os.remove(path)
        
        if os.path.exists(concat_file):
            os.remove(concat_file)
