def test_quality_status(client):
    response = client.get("/api/quality/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"pass", "fail"}
    assert "checks" in payload
    assert "summary" in payload
