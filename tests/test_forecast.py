def test_forecast_ok(client):
    response = client.get("/api/forecast", params={"state": "Kansas", "horizon": 2})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["forecast"]) == 2
    for field in ["model_name", "train_start_year", "train_end_year", "mae", "mape", "interval_coverage"]:
        assert field in payload


def test_forecast_invalid_horizon(client):
    response = client.get("/api/forecast", params={"state": "Kansas", "horizon": 0})
    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"
