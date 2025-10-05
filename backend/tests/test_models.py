from app.models.video import Video

def test_video_model():
    video = Video(
        id="test-1",
        title="Test Video",
        filename="test.mp4",
        duration=120.5,
        status="processed"
    )
    assert video.id == "test-1"
    assert video.title == "Test Video"
