class TestAuthLogin:
    def test_login_success(self, client, admin_user):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "password123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@test.com"
        assert data["user"]["role"] == "admin"

    def test_login_invalid_password(self, client, admin_user):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid email or password"

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@test.com", "password": "password123"},
        )
        assert resp.status_code == 401

    def test_refresh_token(self, client, auth_headers):
        resp = client.post("/api/v1/auth/refresh", headers=auth_headers)
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_logout(self, client, auth_headers):
        resp = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert resp.status_code == 204

    def test_unauthorized_access(self, client):
        resp = client.get("/api/v1/gateways/")
        assert resp.status_code in (401, 403)

    def test_invalid_token(self, client):
        resp = client.get(
            "/api/v1/gateways/",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert resp.status_code in (401, 403)
