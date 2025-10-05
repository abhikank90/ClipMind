import pytest
import os
from app.workers.video_processor import VideoProcessor
from app.workers.scene_detector import SceneDetector
from app.ai.clip_model import CLIPEmbedder
from app.ai.whisper_model import WhisperTranscriber
from app.workers.compilation_renderer import CompilationRenderer


# Mark all tests as integration tests
pytestmark = pytest.mark.integration


class TestVideoProcessor:
    def test_extract_metadata(self, sample_video_path):
        processor = VideoProcessor()
        metadata = processor.extract_metadata(sample_video_path)
        
        assert 'duration' in metadata
        assert 'width' in metadata
        assert 'height' in metadata
    
    def test_generate_thumbnail(self, sample_video_path, tmp_path):
        processor = VideoProcessor()
        output_path = str(tmp_path / "thumb.jpg")
        
        success = processor.generate_thumbnail(sample_video_path, output_path)
        assert success
        assert os.path.exists(output_path)


class TestSceneDetector:
    def test_detect_scenes(self, sample_video_path):
        detector = SceneDetector()
        scenes = detector.detect_scenes(sample_video_path)
        
        assert isinstance(scenes, list)
        if scenes:
            assert 'start_time' in scenes[0]
            assert 'end_time' in scenes[0]


class TestCLIPModel:
    def test_encode_image(self, sample_image_path):
        model = CLIPEmbedder()
        embedding = model.encode_image(sample_image_path)
        
        assert embedding.shape == (512,)
    
    def test_encode_text(self):
        model = CLIPEmbedder()
        embedding = model.encode_text("a happy person")
        
        assert embedding.shape == (512,)


class TestWhisperModel:
    def test_transcribe(self, sample_audio_path):
        transcriber = WhisperTranscriber(model_size="tiny")
        result = transcriber.transcribe(sample_audio_path)
        
        assert 'text' in result
        assert 'segments' in result


# Fixtures
@pytest.fixture
def sample_video_path():
    # TODO: Add path to test video
    return "tests/fixtures/sample.mp4"

@pytest.fixture
def sample_audio_path():
    return "tests/fixtures/sample.wav"

@pytest.fixture
def sample_image_path():
    return "tests/fixtures/sample.jpg"
