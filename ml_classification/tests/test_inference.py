from cls.inference import predict_class

SAMPLE_DIABETES = {"glucose_saliva": 7.0, "ph_value": 8.0, "fructosamine_umol_l": 1.0}


def _no_mgdl(res):
    return not any("mgdl" in k or "glucose_estimate" in k for k in res)


def test_ok(ready_model):
    res = predict_class(SAMPLE_DIABETES, ready_model)
    assert res["status"] == "ok"
    assert res["class_name"] == "DIABETES" and res["class_index"] == 2
    assert abs(sum(res["probabilities"].values()) - 1) < 1e-3
    assert _no_mgdl(res)


def test_uncertain(ready_model):
    res = predict_class(SAMPLE_DIABETES, ready_model, threshold=1.01)
    assert res["status"] == "uncertain" and res["class_name"] == "UNCERTAIN" and res["class_index"] is None
    assert _no_mgdl(res)


def test_out_of_range(ready_model):
    res = predict_class({**SAMPLE_DIABETES, "ph_value": 99.0}, ready_model)
    assert res["status"] == "out_of_range" and res["class_name"] is None and res["probabilities"] is None


def test_model_not_ready(not_ready_model):
    res = predict_class(SAMPLE_DIABETES, not_ready_model)
    assert res["status"] == "model_not_ready" and res["class_name"] is None
    assert _no_mgdl(res)
