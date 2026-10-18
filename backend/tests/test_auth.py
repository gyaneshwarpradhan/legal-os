def test_login_success(client, seed_org_and_users):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "attorney1@test.local", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, seed_org_and_users):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "attorney1@test.local", "password": "wrong_password"},
    )
    assert response.status_code == 401


def test_me_endpoint_authenticated(client, seed_org_and_users):
    # Log in
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "attorney1@test.local", "password": "password123"},
    )
    token = login_resp.json()["access_token"]

    # Call /me
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    user_data = me_resp.json()
    assert user_data["email"] == "attorney1@test.local"
    assert user_data["role"] == "attorney"


def test_me_endpoint_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
