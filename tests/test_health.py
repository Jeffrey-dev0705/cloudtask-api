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

def test_ready_unavailable():
    from redis.exceptions import ConnectionError as RedisConnectionError
    from sqlalchemy.exc import OperationalError

    mock_db = MagicMock()
    mock_db.execute.side_effect = OperationalError("SELECT 1", {}, Exception("db down"))
    with (
        patch("app.main.SessionLocal", return_value=mock_db),
        patch("app.main.redis_client") as mock_redis,
    ):
        mock_redis.ping = AsyncMock(side_effect=RedisConnectionError("redis down"))
        response = client.get("/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["database"] is False
    assert body["checks"]["redis"] is False
