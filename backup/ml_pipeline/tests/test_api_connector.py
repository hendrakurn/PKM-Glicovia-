from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

import src.api_connector as api_connector


client = TestClient(api_connector.app)


def test_api_schema_uses_fructosamine():
    info = client.get("/model-info").json()
    assert info["features"] == ["glucose_saliva", "ph_value", "fructosamine_umol_l"]
    assert api_connector.required_fields == ["glucose_saliva", "ph_value", "fructosamine_umol_l"]


def test_api_validation_accepts_new_payload_and_rejects_old_payload():
    validated = api_connector.validate_prediction_input(
        {"glucose_saliva": 1.5, "ph_value": 6.5, "fructosamine_umol_l": 285.0, "id": "abc;DROP"}
    )
    assert validated["id"] == "abcDROP"
    assert validated["fructosamine_umol_l"] == 285.0

    with pytest.raises(ValueError):
        api_connector.validate_prediction_input({"glucose_saliva": 1.5, "ph_value": 6.5})


def test_predict_endpoint_with_monkeypatched_inference(monkeypatch):
    def fake_predict_single(sample, model_path, scaler_path, **kwargs):
        return {"prediction": 123.4, "category": {"name": "Normal"}, "confidence": 0.9, "sample_id": sample.get("id")}

    monkeypatch.setattr(api_connector, "predict_single", fake_predict_single)
    response = client.post(
        "/predict",
        json={"glucose_saliva": 1.5, "ph_value": 6.5, "fructosamine_umol_l": 285.0, "id": "sample-1"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["prediction"] == 123.4
    assert payload["sample_id"] == "sample-1"


def test_predict_batch_endpoint_with_monkeypatched_inference(monkeypatch):
    def fake_predict_batch(samples, model_path, scaler_path, **kwargs):
        return [{"sample_id": sample.get("id"), "prediction": 1.0} for sample in samples]

    monkeypatch.setattr(api_connector, "predict_batch", fake_predict_batch)
    response = client.post(
        "/predict-batch",
        json={
            "samples": [
                {"glucose_saliva": 1.5, "ph_value": 6.5, "fructosamine_umol_l": 285.0, "id": "s1"},
                {"glucose_saliva": 3.0, "ph_value": 6.0, "fructosamine_umol_l": 380.0, "id": "s2"},
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["predictions"][0]["sample_id"] == "s1"
