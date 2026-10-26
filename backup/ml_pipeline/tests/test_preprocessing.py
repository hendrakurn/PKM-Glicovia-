from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.preprocessing import (
    FEATURE_COLUMNS,
    REQUIRED_COLUMNS,
    _calculate_stratification_ratios,
    _handle_missing_values,
    _handle_zero_variance,
    _validate_input_csv,
    preprocess,
)
from src.generate_dummy import generate_dummy


def test_preprocessing_pipeline_saves_three_feature_scaler(tmp_path):
    dummy_dir = tmp_path / "dummy"
    _, _ = generate_dummy(n_samples=120, random_state=11, output_dir=str(dummy_dir))
    result = preprocess(raw_csv_path=str(dummy_dir / "generated_data.csv"), output_dir=str(tmp_path / "processed"))

    X_train = np.load(result["X_train_path"])
    X_test = np.load(result["X_test_path"])
    scaler_params = json.loads(Path(result["scaler_params_path"]).read_text())
    report = json.loads(Path(result["preprocessing_report_path"]).read_text())

    assert X_train.shape[1] == 3
    assert X_test.shape[1] == 3
    assert scaler_params["feature_names"] == FEATURE_COLUMNS
    assert report["feature_names"] == FEATURE_COLUMNS
    assert report["target_label"] == "bg_mgdl_reference"
    assert list(REQUIRED_COLUMNS) == ["id", "glucose_saliva", "ph_value", "fructosamine_umol_l", "bg_class", "bg_mgdl_reference"]


def test_preprocessing_helper_validation_and_zero_variance():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "glucose_saliva": [1.0, 1.1, 1.2],
            "ph_value": [6.5, 6.6, 6.7],
            "fructosamine_umol_l": [200.0, 200.0, 200.0],
            "bg_class": [0, 0, 1],
            "bg_mgdl_reference": [90.0, 91.0, 120.0],
        }
    )
    df2, active_features = _handle_zero_variance(df, FEATURE_COLUMNS)
    assert "fructosamine_umol_l" not in active_features
    assert "fructosamine_umol_l" not in df2.columns


def test_preprocessing_stratification_ratios():
    ratios = _calculate_stratification_ratios(np.array([0, 0, 1, 2]), np.array([0, 1]))
    assert ratios["0"] == [0.5, 0.5]
    assert ratios["1"] == [0.25, 0.5]
    assert ratios["2"] == [0.25, 0.0]
