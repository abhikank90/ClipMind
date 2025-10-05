def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_list_videos(client):
    response = client.get("/api/v1/videos/")
    assert response.status_code == 200
    assert "videos" in response.json()
