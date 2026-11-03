from fastapi.testclient import TestClient

from cls.api import app

CONTRACT = {"class_index", "class_name", "probabilities", "confidence", "clinical_category",
            "confidence_score", "model_type", "model_version", "status"}
PAYLOAD = {"glucose_saliva": 7.0, "ph_value": 8.0, "fructosamine_umol_l": 1.0}


def test_predict_contract(ready_model, monkeypatch):
    monkeypatch.setenv("GLICO_CLS_MODEL", ready_model)
    body = TestClient(app).post("/predict", json=PAYLOAD).json()
    assert CONTRACT <= body.keys()
    assert body["status"] == "ok" and body["clinical_category"] == body["class_name"] == "DIABETES"
    assert body["confidence_score"] == body["confidence"]


def test_predict_not_ready_keeps_firmware_fields(not_ready_model, monkeypatch):
    monkeypatch.setenv("GLICO_CLS_MODEL", not_ready_model)
    body = TestClient(app).post("/predict", json=PAYLOAD).json()
    assert CONTRACT <= body.keys()
    assert body["clinical_category"] == "MODEL_NOT_READY" and body["confidence_score"] == 0.0


def test_batch_and_info(ready_model, monkeypatch):
    monkeypatch.setenv("GLICO_CLS_MODEL", ready_model)
    client = TestClient(app)
    assert client.post("/predict-batch", json={"samples": [PAYLOAD, PAYLOAD]}).json()["count"] == 2
    assert client.get("/model-info").json()["model_type"] == "SVC-rbf"
    assert client.get("/health").json() == {"status": "ok"}
