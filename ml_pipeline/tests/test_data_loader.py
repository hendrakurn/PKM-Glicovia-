from __future__ import annotations

import pandas as pd
import pytest

from src.data_loader import (
    DataLoaderError,
    FEATURE_COLUMNS,
    REQUIRED_COLUMNS,
    _assess_quality_status,
    _check_missing_values,
    _detect_outliers_iqr,
    _validate_required_columns,
    load_batch,
    load_data,
)
from src.generate_dummy import generate_dummy


def test_data_loader_requires_fructosamine_column(tmp_path):
    out_dir = tmp_path / "dummy"
    df, _ = generate_dummy(n_samples=50, random_state=3, output_dir=str(out_dir))
    loaded, report = load_data(file_path=str(out_dir / "generated_data.csv"), validate=True)

    assert list(loaded.columns) == REQUIRED_COLUMNS
    assert report["quality_status"] in {"PASS", "WARNING"}
    assert FEATURE_COLUMNS == ["glucose_saliva", "ph_value", "fructosamine_umol_l"]


def test_data_loader_missing_required_column_raises():
    df = pd.DataFrame({"id": [1], "glucose_saliva": [1.2], "ph_value": [6.5], "bg_class": [0], "bg_mgdl_reference": [90.0]})
    with pytest.raises(DataLoaderError):
        _validate_required_columns(df)


def test_data_loader_quality_helpers():
    df = pd.DataFrame(
        {
            "glucose_saliva": [1.0, 1.0, 1.0, 1.0],
            "ph_value": [6.5, 6.5, 6.5, 6.5],
            "fructosamine_umol_l": [200.0, 210.0, 220.0, 230.0],
        }
    )
    missing = _check_missing_values(df)
    outliers = _detect_outliers_iqr(df, FEATURE_COLUMNS)
    status = _assess_quality_status(total_samples=100, missing_ratio=max(missing.values()), outlier_ratio=0.0, zero_variance_features=[])

    assert missing["fructosamine_umol_l"] == 0.0
    assert "fructosamine_umol_l" in outliers
    assert status == "PASS"


def test_data_loader_batch_and_fallback(tmp_path):
    df, _ = generate_dummy(n_samples=40, random_state=5, output_dir=str(tmp_path / "dummy"))
    out_dir = tmp_path / "dummy"
    results = load_batch([str(out_dir / "generated_data.csv"), str(tmp_path / "missing.csv")], validate=False, auto_fallback=True)

    assert len(results) == 2
    assert results[0][1]["quality_status"] == "UNVALIDATED"
    assert results[1][1]["quality_status"] in {"UNVALIDATED", "ERROR", "PASS", "WARNING"}
