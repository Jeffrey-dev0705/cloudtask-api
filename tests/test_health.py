from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ready():
    mock_db = MagicMock()
    with (
        patch("app.main.SessionLocal", return_value=mock_db),
        patch("app.main.redis_client") as mock_redis,
    ):
        mock_redis.ping = AsyncMock(return_value=True)
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"database": True, "redis": True},
    }
    mock_db.execute.assert_called_once()
    mock_db.close.assert_called_once()

