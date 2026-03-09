def test_metrics_state_year(client):
    response = client.get("/api/metrics/state-year", params={"state": "Kansas"})
    assert response.status_code == 200
    payload = response.json()
    assert "rows" in payload
    assert len(payload["rows"]) >= 1


def test_metrics_invalid_year(client):
    response = client.get("/api/metrics/state-year", params={"state": "Kansas", "year": 1200})
    assert response.status_code == 422
    payload = response.json()
    assert payload["error_code"] == "validation_error"
