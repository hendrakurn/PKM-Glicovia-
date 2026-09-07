from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.generate_dummy import generate_dummy
from src.model_comparison import (
    _build_candidate_models,
    _mgdl_to_class,
    compare_regression_models,
)


def test_candidate_models_include_required_regressors():
    models = _build_candidate_models(random_state=42)

    assert list(models) == [
        "DummyRegressor",
        "LinearRegression",
        "Ridge",
        "KNeighborsRegressor",
        "SVR_RBF",
        "TunedSVR_RBF",
        "RandomForestRegressor",
        "GradientBoostingRegressor",
    ]


def test_mgdl_to_class_uses_clinical_thresholds():
    classes = _mgdl_to_class(np.array([99.9, 100.0, 125.9, 126.0]))

    assert classes.tolist() == [0, 1, 1, 2]


def test_compare_regression_models_writes_ranked_artifacts(tmp_path):
    dummy_dir = tmp_path / "dummy"
    generate_dummy(n_samples=120, random_state=21, output_dir=str(dummy_dir))
    output_dir = tmp_path / "model_comparison"

    result = compare_regression_models(
        raw_csv_path=str(dummy_dir / "generated_data.csv"),
        output_dir=str(output_dir),
        config={
            "n_splits": 3,
            "random_state": 21,
            "models": ["DummyRegressor", "LinearRegression", "Ridge"],
        },
    )

    assert result["models_compared"] == 3
    assert result["best_model"]["model_name"] in {"DummyRegressor", "LinearRegression", "Ridge"}

    artifact_paths = result["artifact_paths"]
    for key in ["comparison_report", "comparison_table", "predictions", "best_model"]:
        assert Path(artifact_paths[key]).exists()

    report = json.loads(Path(artifact_paths["comparison_report"]).read_text(encoding="utf-8"))
    assert report["best_model"]["model_name"] == result["best_model"]["model_name"]

    ranked = result["model_results"]
    for current, following in zip(ranked, ranked[1:]):
        current_key = (current["test_r2"], -current["test_rmse"])
        following_key = (following["test_r2"], -following["test_rmse"])
        assert current_key >= following_key
