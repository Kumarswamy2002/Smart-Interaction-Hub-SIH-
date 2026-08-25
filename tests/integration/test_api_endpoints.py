import pytest
from httpx import AsyncClient, ASGITransport
from sih.api.app import app

@pytest.mark.asyncio
async def test_auth_and_health_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Health check
        res = await client.get("/api/v1/system/health")
        assert res.status_code == 200
        assert res.json()["status"] == "HEALTHY"

        # Register
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": "user1@example.com",
            "password": "Password123!",
            "full_name": "User One"
        })
        assert reg_res.status_code == 200
        data = reg_res.json()
        assert "access_token" in data

@pytest.mark.asyncio
async def test_conversation_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post("/api/v1/conversations/send", json={
            "content": "Prepare everything for tomorrow's meeting",
            "user_id": "usr-test",
            "workspace_id": "ws-test"
        })
        assert res.status_code == 200
        body = res.json()
        assert "conversation_id" in body
        assert "message" in body
