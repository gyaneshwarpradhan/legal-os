"""Automated tests for document pipeline, classification, chunking, and isolated hybrid search."""
import io


def test_document_upload_extraction_and_search(client, seed_org_and_users):
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

    # 3. Attorney 1 creates Matter 1
    matter1_resp = client.post(
        "/api/v1/matters",
        json={
            "title": "Johnson v. Metro Properties",
            "matter_type": "personal_injury",
            "date_opened": "2024-03-15",
        },
        headers=headers1,
    )
    matter1_id = matter1_resp.json()["id"]

    # 4. Attorney 2 creates Matter 2 (completely separate case)
    matter2_resp = client.post(
        "/api/v1/matters",
        json={
            "title": "Davis v. TechCorp International",
            "matter_type": "employment",
            "date_opened": "2024-04-01",
        },
        headers=headers2,
    )
    matter2_id = matter2_resp.json()["id"]

    # 5. Attorney 1 uploads a formal Complaint into Matter 1
    sample_complaint_content = (
        "SUPERIOR COURT OF CALIFORNIA, COUNTY OF ALAMEDA\n\n"
        "MARCUS JOHNSON, Plaintiff,\n"
        "v.\n"
        "METRO PROPERTIES, LLC, Defendant.\n\n"
        "COMPLAINT FOR DAMAGES AND PREMISES LIABILITY\n"
        "JURY TRIAL DEMANDED\n\n"
        "FIRST CAUSE OF ACTION - NEGLIGENCE\n"
        "1. Plaintiff alleges that Defendant failed to maintain the commercial second-story deck.\n"
        "2. As a proximate result of the deck collapse on February 10, 2024, Plaintiff suffered spinal trauma.\n"
        "PRAYER FOR RELIEF\n"
        "Wherefore, Plaintiff prays for judgment against Defendant for general and special damages."
    )

    file_payload = {
        "file": (
            "Verified_Complaint_Johnson.txt",
            io.BytesIO(sample_complaint_content.encode("utf-8")),
            "text/plain",
        )
    }

    upload_resp = client.post(
        f"/api/v1/matters/{matter1_id}/documents",
        files=file_payload,
        headers=headers1,
    )
    assert upload_resp.status_code == 201
    doc_data = upload_resp.json()
    doc_id = doc_data["id"]
    assert doc_data["status"] == "ready"
    assert doc_data["document_type"] == "complaint"  # Auto-classified!
    assert doc_data["processing_status"]["chunks_generated"] > 0

    # 6. Retrieve document chunks
    chunks_resp = client.get(
        f"/api/v1/matters/{matter1_id}/documents/{doc_id}/chunks",
        headers=headers1,
    )
    assert chunks_resp.status_code == 200
    chunks = chunks_resp.json()
    assert len(chunks) > 0
    assert chunks[0]["page_number"] == 1
    assert "negligence" in chunks[0]["content"].lower()

    # 7. Hybrid Search in Matter 1
    search_resp = client.post(
        f"/api/v1/matters/{matter1_id}/search",
        json={"query": "deck collapse spinal trauma damages"},
        headers=headers1,
    )
    assert search_resp.status_code == 200
    search_results = search_resp.json()
    assert len(search_results) > 0
    assert search_results[0]["score"] > 0.3
    assert search_results[0]["document_id"] == doc_id

    # 8. STRICT MATTER ISOLATION TEST:
    # Attorney 2 searches within Matter 2 for the exact same query
    # -> Must return ZERO results because Matter 2 contains no such documents!
    search2_resp = client.post(
        f"/api/v1/matters/{matter2_id}/search",
        json={"query": "deck collapse spinal trauma damages"},
        headers=headers2,
    )
    assert search2_resp.status_code == 200
    assert len(search2_resp.json()) == 0  # No cross-case leakage!

    # 9. PERMISSION BOUNDARY TEST:
    # Attorney 2 attempts to query Matter 1's search endpoint directly
    # -> Must be REJECTED WITH 403 Forbidden!
    unauth_search = client.post(
        f"/api/v1/matters/{matter1_id}/search",
        json={"query": "deck collapse"},
        headers=headers2,
    )
    assert unauth_search.status_code == 403

    # Attorney 2 attempts to read Matter 1's documents
    unauth_docs = client.get(
        f"/api/v1/matters/{matter1_id}/documents",
        headers=headers2,
    )
    assert unauth_docs.status_code == 403

    # 10. Reclassify document
    reclass_resp = client.put(
        f"/api/v1/matters/{matter1_id}/documents/{doc_id}/reclassify",
        json={"document_type": "pleading"},
        headers=headers1,
    )
    assert reclass_resp.status_code == 200
    assert reclass_resp.json()["document_type"] == "pleading"
