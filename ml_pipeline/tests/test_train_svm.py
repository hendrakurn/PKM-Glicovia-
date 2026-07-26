from __future__ import annotations

import numpy as np

from src.train_svm import _clinical_metrics, _regression_metrics, train_svm


def test_train_svm_metrics_helpers_work():
    y_true = np.array([80.0, 120.0, 250.0])
    y_pred = np.array([82.0, 118.0, 240.0])
    reg = _regression_metrics(y_true, y_pred)
    clinical = _clinical_metrics(y_true, y_pred)

    assert "rmse" in reg and reg["rmse"] >= 0
    assert "accuracy" in clinical
    assert clinical["accuracy"] >= 0


def test_train_svm_function_exists():
    assert callable(train_svm)
