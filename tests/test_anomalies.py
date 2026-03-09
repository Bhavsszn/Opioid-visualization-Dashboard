def test_anomalies_ok(client):
    response = client.get("/api/anomalies", params={"state": "Kansas", "window": 3, "z_threshold": 1.5})
    assert response.status_code == 200
    payload = response.json()
    assert "rows" in payload
    assert payload["window"] == 3


def test_anomalies_invalid_window(client):
    response = client.get("/api/anomalies", params={"state": "Kansas", "window": 1})
    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"
