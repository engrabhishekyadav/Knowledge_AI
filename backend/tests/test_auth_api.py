import uuid
import pytest

@pytest.mark.asyncio
async def test_signup_and_login_flow(client):
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    signup_payload = {
        "email": unique_email,
        "password": "SecurePassword123!",
        "fullName": "Test Engineer"
    }

    # 1. Signup
    res = await client.post("/api/v1/auth/signup", json=signup_payload)
    assert res.status_code == 200, f"Signup failed: {res.text}"
    data = res.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    assert data["user"]["email"] == unique_email
    token = data["accessToken"]

    # 2. Prevent duplicate signup
    dup_res = await client.post("/api/v1/auth/signup", json=signup_payload)
    assert dup_res.status_code == 400

    # 3. Valid Login
    login_res = await client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "accessToken" in login_data

    # 4. Invalid Password
    bad_login = await client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 5. Authenticated Profile /auth/me
    me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == unique_email
