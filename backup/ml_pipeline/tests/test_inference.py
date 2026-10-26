from __future__ import annotations

import pandas as pd
import pytest

from src.inference import FEATURE_ORDER, preprocess_sample, predict_batch, predict_single


def test_inference_single_and_batch_uses_fructosamine(trained_model_bundle):
    model_path = trained_model_bundle["model_path"]
    scaler_path = trained_model_bundle["scaler_path"]
    sample = {
        "id": "sample-1",
        "glucose_saliva": 1.3,
        "ph_value": 6.4,
        "fructosamine_umol_l": 285.0,
    }
    result = predict_single(sample=sample, model_path=model_path, scaler_path=scaler_path)
    assert set(FEATURE_ORDER) == {"glucose_saliva", "ph_value", "fructosamine_umol_l"}
    assert result["sample_id"] == "sample-1"
    assert isinstance(result["prediction"], float)
    assert result["category"]["name"] in {"Normal", "Pre-Diabetes", "Diabetes"}
    assert 0.0 <= result["confidence"] <= 1.0

    batch = pd.DataFrame([
        sample,
        {"id": "sample-2", "glucose_saliva": 3.1, "ph_value": 6.1, "fructosamine_umol_l": 390.0},
    ])
    batch_results = predict_batch(batch, model_path=model_path, scaler_path=scaler_path)
    assert len(batch_results) == 2
    assert batch_results[1]["sample_id"] == "sample-2"


def test_preprocess_sample_requires_new_feature(trained_model_bundle):
    scaler_path = trained_model_bundle["scaler_path"]
    with pytest.raises(Exception):
        preprocess_sample({"glucose_saliva": 1.0, "ph_value": 6.5}, scaler_params={"feature_names": FEATURE_ORDER})
