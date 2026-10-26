from __future__ import annotations

import numpy as np

from src.evaluate import _calculate_classification_metrics, _calculate_regression_metrics, evaluate


def test_evaluate_metrics_helpers_work():
    y_true = np.array([80.0, 120.0, 250.0])
    y_pred = np.array([79.0, 121.0, 260.0])
    reg = _calculate_regression_metrics(y_true, y_pred)
    clf = _calculate_classification_metrics(y_true, y_pred)

    assert "rmse" in reg and reg["rmse"] >= 0
    assert "accuracy" in clf and 0 <= clf["accuracy"] <= 1


def test_evaluate_function_exists():
    assert callable(evaluate)
