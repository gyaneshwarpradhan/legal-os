"""Test matter operations and strict matter isolation security enforcement."""


def test_matter_creation_and_strict_isolation(client, seed_org_and_users):
    # 1. Login as Attorney 1
    resp1 = client.post(
        "/api/v1/auth/login",
        json={"email": "attorney1@test.local", "password": "password123"},
    )
    token1 = resp1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 2. Login as Attorney 2
    resp2 = client.post(
        "/api/v1/auth/login",
        json={"email": "attorney2@test.local", "password": "password123"},
    )
    token2 = resp2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 3. Attorney 1 creates a matter
    matter_payload = {
        "title": "Confidential IP Litigation - Alpha v. Competitor",
        "case_number": "2024-IP-001",
        "description": "Trade secret misappropriation matter.",
        "matter_type": "commercial",
        "date_opened": "2024-05-01",
        "court": "U.S. District Court, N.D. Cal.",
        "jurisdiction": "Federal",
        "judge": "Hon. Sarah Vance",
    }
    create_resp = client.post("/api/v1/matters", json=matter_payload, headers=headers1)
    assert create_resp.status_code == 201
    matter_id = create_resp.json()["id"]

    # 4. Attorney 1 can retrieve the matter
    get_resp1 = client.get(f"/api/v1/matters/{matter_id}", headers=headers1)
    assert get_resp1.status_code == 200
    assert get_resp1.json()["title"] == matter_payload["title"]

    # 5. Attorney 2 attempts to retrieve Matter A -> MUST BE REJECTED WITH 403
    unauthorized_resp = client.get(f"/api/v1/matters/{matter_id}", headers=headers2)
    assert unauthorized_resp.status_code == 403
    assert "not authorized" in unauthorized_resp.json()["detail"].lower()

    # 6. Attorney 2 lists matters -> Matter A should NOT appear in their list
    list_resp2 = client.get("/api/v1/matters", headers=headers2)
    assert list_resp2.status_code == 200
    matter_ids_visible_to_attorney2 = [
        item["id"] for item in list_resp2.json()["items"]
    ]
    assert matter_id not in matter_ids_visible_to_attorney2

    # 7. Admin CAN access the matter due to firm-wide administrative privileges
    resp_admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.local", "password": "password123"},
    )
    token_admin = resp_admin.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    admin_get_resp = client.get(f"/api/v1/matters/{matter_id}", headers=headers_admin)
    assert admin_get_resp.status_code == 200

    # 8. Attorney 1 adds Attorney 2 to the matter team
    attorney2_id = seed_org_and_users["attorney_2"].id
    add_member_resp = client.post(
        f"/api/v1/matters/{matter_id}/members",
        json={"user_id": str(attorney2_id), "role": "attorney"},
        headers=headers1,
    )
    assert add_member_resp.status_code == 200

    # 9. Attorney 2 CAN NOW access the matter
    authorized_resp2 = client.get(f"/api/v1/matters/{matter_id}", headers=headers2)
    assert authorized_resp2.status_code == 200
    assert authorized_resp2.json()["id"] == matter_id


def test_matter_entities_crud(client, seed_org_and_users):
    # Login as Attorney 1
    resp1 = client.post(
        "/api/v1/auth/login",
        json={"email": "attorney1@test.local", "password": "password123"},
    )
    token1 = resp1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Create matter
    create_resp = client.post(
        "/api/v1/matters",
        json={
            "title": "Smith v. Acme Corp",
            "matter_type": "employment",
            "date_opened": "2024-01-15",
        },
        headers=headers1,
    )
    matter_id = create_resp.json()["id"]

    # Add Party
    party_resp = client.post(
        f"/api/v1/matters/{matter_id}/parties",
        json={"name": "Jane Smith", "party_type": "plaintiff", "entity_type": "individual"},
        headers=headers1,
    )
    assert party_resp.status_code == 201
    assert party_resp.json()["name"] == "Jane Smith"

    # Add Event (Timeline)
    event_resp = client.post(
        f"/api/v1/matters/{matter_id}/events",
        json={
            "title": "Initial EEOC Charge Filed",
            "event_date": "2024-01-20T10:00:00Z",
            "event_type": "filing",
        },
        headers=headers1,
    )
    assert event_resp.status_code == 201

    # Add Deadline
    deadline_resp = client.post(
        f"/api/v1/matters/{matter_id}/deadlines",
        json={
            "title": "Response to Interrogatories Due",
            "due_date": "2024-03-01T17:00:00Z",
            "deadline_type": "discovery",
            "is_high_risk": True,
        },
        headers=headers1,
    )
    assert deadline_resp.status_code == 201

    # Verify lists
    parties = client.get(f"/api/v1/matters/{matter_id}/parties", headers=headers1).json()
    assert len(parties) == 1
    events = client.get(f"/api/v1/matters/{matter_id}/events", headers=headers1).json()
    assert len(events) == 1
    deadlines = client.get(f"/api/v1/matters/{matter_id}/deadlines", headers=headers1).json()
    assert len(deadlines) == 1
