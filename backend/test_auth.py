import httpx
import uuid

def test_auth_system():
    print("=== 1. Testing User Signup API ===")
    unique_email = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
    signup_payload = {
        "email": unique_email,
        "password": "SecurePassword123!",
        "fullName": "Dev Engineer"
    }

    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=10.0) as client:
        # Signup
        signup_res = client.post("/auth/signup", json=signup_payload)
        print("Signup Status:", signup_res.status_code)
        assert signup_res.status_code == 200, f"Signup failed: {signup_res.text}"
        signup_data = signup_res.json()
        token = signup_data["accessToken"]
        user = signup_data["user"]
        print(f"Created User: {user['id']} ({user['email']}) - Token: {token[:20]}...")

        # Duplicate email check
        dup_res = client.post("/auth/signup", json=signup_payload)
        print("Duplicate Email Status:", dup_res.status_code)
        assert dup_res.status_code == 400

        print("\n=== 2. Testing User Login API ===")
        # Valid Login
        login_res = client.post("/auth/login", json={
            "email": unique_email,
            "password": "SecurePassword123!"
        })
        print("Valid Login Status:", login_res.status_code)
        assert login_res.status_code == 200

        # Invalid Password Login
        invalid_res = client.post("/auth/login", json={
            "email": unique_email,
            "password": "WrongPassword!"
        })
        print("Invalid Password Status:", invalid_res.status_code)
        assert invalid_res.status_code == 401

        print("\n=== 3. Testing Authenticated /auth/me Profile Endpoint ===")
        me_res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        print("Auth Me Status:", me_res.status_code)
        assert me_res.status_code == 200
        me_data = me_res.json()
        print(f"Authenticated as: {me_data['fullName']} ({me_data['email']})")

    print("\n[SUCCESS] ALL AUTHENTICATION BACKEND TESTS PASSED WITH 0 ERRORS!")

if __name__ == "__main__":
    test_auth_system()
