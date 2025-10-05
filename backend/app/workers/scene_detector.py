import logging
from typing import List, Dict, Any
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

logger = logging.getLogger(__name__)


class SceneDetector:
    def __init__(self, threshold: float = 30.0):
        self.threshold = threshold
    
    def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Detect scene changes in video using PySceneDetect
        
        Returns list of scenes with start/end timestamps
        """
        try:
            video_manager = VideoManager([video_path])
            scene_manager = SceneManager()
            
            # Add ContentDetector algorithm (detects fast cuts)
            scene_manager.add_detector(
                ContentDetector(threshold=self.threshold)
            )
            
            # Start video manager
            video_manager.set_downscale_factor()
            video_manager.start()
            
            # Perform scene detection
            scene_manager.detect_scenes(frame_source=video_manager)
            
            # Get scene list
            scene_list = scene_manager.get_scene_list()
            
            scenes = []
            for i, scene in enumerate(scene_list):
                start_time = scene[0].get_seconds()
                end_time = scene[1].get_seconds()
                
                scenes.append({
                    "scene_number": i + 1,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time,
                })
            
            logger.info(f"Detected {len(scenes)} scenes in {video_path}")
            return scenes
            
        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            return []
    
    def detect_scenes_adaptive(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Adaptive scene detection that adjusts threshold based on content
        """
        # Try with default threshold first
        scenes = self.detect_scenes(video_path)
        
        # If too few or too many scenes, adjust
        if len(scenes) < 5:
            # Content might be static, lower threshold
            detector = SceneDetector(threshold=15.0)
            scenes = detector.detect_scenes(video_path)
        elif len(scenes) > 100:
            # Too many cuts, raise threshold
            detector = SceneDetector(threshold=50.0)
            scenes = detector.detect_scenes(video_path)
        
        return scenes
