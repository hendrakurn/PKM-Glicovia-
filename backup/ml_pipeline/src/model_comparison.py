"""Model comparison workflow for GlicoSaliva regression models."""

from __future__ import annotations

import argparse
import copy
import json
import logging
import pickle
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import GridSearchCV, KFold, cross_validate
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR

try:
    from src.preprocessing import preprocess
except ImportError:  # pragma: no cover - direct script execution fallback
    from preprocessing import preprocess


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


DEFAULT_CONFIG = {
    "test_size": 0.2,
    "n_splits": 5,
    "random_state": 42,
    "outlier_strategy": "remove",
}


def _build_candidate_models(random_state: int) -> dict[str, Any]:
    """Build the default set of regression models to compare."""
    tuned_svr_cv = KFold(n_splits=3, shuffle=True, random_state=random_state)
    return {
        "DummyRegressor": DummyRegressor(strategy="mean"),
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "KNeighborsRegressor": KNeighborsRegressor(n_neighbors=5),
        "SVR_RBF": SVR(kernel="rbf", C=10.0, gamma=0.1, epsilon=0.2),
        "TunedSVR_RBF": GridSearchCV(
            estimator=SVR(kernel="rbf"),
            param_grid={
                "C": [1.0, 10.0, 100.0, 500.0, 1000.0],
                "gamma": ["scale", 0.01, 0.03, 0.1, 0.3],
                "epsilon": [0.01, 0.05, 0.1, 0.2],
            },
            scoring="r2",
            cv=tuned_svr_cv,
            n_jobs=-1,
            refit=True,
            error_score="raise",
        ),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "GradientBoostingRegressor": GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=3,
            random_state=random_state,
        ),
    }


def _load_processed_data(processed_data_path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    input_path = Path(processed_data_path)
    required_files = ["X_train.npy", "X_test.npy", "y_train.npy", "y_test.npy"]
    for filename in required_files:
        filepath = input_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Processed data file not found: {filepath}")

    return (
        np.load(input_path / "X_train.npy"),
        np.load(input_path / "X_test.npy"),
        np.load(input_path / "y_train.npy").astype(np.float64),
        np.load(input_path / "y_test.npy").astype(np.float64),
    )


def _regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def _mgdl_to_class(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    return np.select(
        [values < 100.0, values < 126.0],
        [0, 1],
        default=2,
    ).astype(int)


def _clinical_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true_class = _mgdl_to_class(y_true)
    y_pred_class = _mgdl_to_class(y_pred)
    return {
        "accuracy": float(accuracy_score(y_true_class, y_pred_class)),
        "f1_macro": float(f1_score(y_true_class, y_pred_class, average="macro", zero_division=0)),
    }


def _cross_validation_metrics(
    model: Any,
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_splits: int,
    random_state: int,
) -> dict[str, float]:
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    scores = cross_validate(
        clone(model),
        X_train,
        y_train,
        cv=cv,
        scoring={
            "r2": "r2",
            "rmse": "neg_root_mean_squared_error",
            "mae": "neg_mean_absolute_error",
        },
        n_jobs=-1,
        error_score="raise",
    )

    rmse_scores = -scores["test_rmse"]
    mae_scores = -scores["test_mae"]
    return {
        "cv_r2_mean": float(np.mean(scores["test_r2"])),
        "cv_r2_std": float(np.std(scores["test_r2"])),
        "cv_rmse_mean": float(np.mean(rmse_scores)),
        "cv_rmse_std": float(np.std(rmse_scores)),
        "cv_mae_mean": float(np.mean(mae_scores)),
        "cv_mae_std": float(np.std(mae_scores)),
    }


def _ranking_key(result: dict[str, Any]) -> tuple[float, float]:
    return (float(result["test_r2"]), -float(result["test_rmse"]))


def _json_safe_params(params: dict[str, Any]) -> dict[str, Any]:
    safe_params = {}
    for key, value in params.items():
        if isinstance(value, np.generic):
            safe_params[key] = value.item()
        else:
            safe_params[key] = value
    return safe_params


def _fitted_model_details(fitted_model: Any) -> dict[str, Any]:
    details = {"estimator_type": type(fitted_model).__name__}
    if hasattr(fitted_model, "best_estimator_"):
        details["best_estimator_type"] = type(fitted_model.best_estimator_).__name__
    if hasattr(fitted_model, "best_params_"):
        details["best_params"] = _json_safe_params(fitted_model.best_params_)
    if hasattr(fitted_model, "best_score_"):
        details["best_cv_score"] = float(fitted_model.best_score_)
    return details


def _validate_model_selection(selected_models: list[str] | None, available_models: dict[str, Any]) -> dict[str, Any]:
    if selected_models is None:
        return available_models

    missing = [name for name in selected_models if name not in available_models]
    if missing:
        raise ValueError(f"Unknown model name(s): {missing}")
    return {name: available_models[name] for name in selected_models}


def compare_regression_models(
    raw_csv_path: str = "src/data/dummy/generated_data.csv",
    output_dir: str = "src/models/model_comparison",
    processed_data_path: str | None = None,
    config: dict | None = None,
) -> dict[str, Any]:
    """Compare regression models and save comparison artifacts.

    If ``processed_data_path`` is not provided, this function first calls the
    existing preprocessing pipeline so every candidate model uses the same
    split and scaled feature arrays.
    """
    merged_config = copy.deepcopy(DEFAULT_CONFIG)
    if config is not None:
        merged_config.update(copy.deepcopy(config))

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    random_state = int(merged_config.get("random_state", 42))
    n_splits = int(merged_config.get("n_splits", 5))

    if processed_data_path is None:
        processed_path = output_path / "processed"
        preprocessing_result = preprocess(
            raw_csv_path=raw_csv_path,
            output_dir=str(processed_path),
            config={
                "test_size": merged_config.get("test_size", 0.2),
                "random_state": random_state,
                "outlier_strategy": merged_config.get("outlier_strategy", "remove"),
            },
        )
    else:
        processed_path = Path(processed_data_path)
        preprocessing_result = {
            "processed_data_path": str(processed_path),
            "source": "existing_processed_data",
        }

    X_train, X_test, y_train, y_test = _load_processed_data(str(processed_path))
    if len(X_train) < 2:
        raise ValueError("Training set must contain at least 2 samples.")
    if len(X_test) == 0:
        raise ValueError("Test set is empty.")

    n_splits = min(n_splits, len(X_train))
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2 after validation.")

    candidate_models = _validate_model_selection(
        merged_config.get("models"),
        _build_candidate_models(random_state),
    )
    if not candidate_models:
        raise ValueError("At least one model is required for comparison.")

    model_results: list[dict[str, Any]] = []
    predictions: dict[str, np.ndarray] = {}
    fitted_models: dict[str, Any] = {}

    for model_name, model in candidate_models.items():
        logger.info("Training and evaluating %s", model_name)
        start_time = time.perf_counter()

        cv_metrics = _cross_validation_metrics(model, X_train, y_train, n_splits, random_state)
        fitted_model = clone(model)
        fitted_model.fit(X_train, y_train)

        train_pred = fitted_model.predict(X_train)
        test_pred = fitted_model.predict(X_test)
        train_metrics = _regression_metrics(y_train, train_pred)
        test_metrics = _regression_metrics(y_test, test_pred)
        clinical_metrics = _clinical_metrics(y_test, test_pred)

        result = {
            "model_name": model_name,
            **cv_metrics,
            "train_r2": train_metrics["r2"],
            "test_r2": test_metrics["r2"],
            "r2_gap": train_metrics["r2"] - test_metrics["r2"],
            "test_rmse": test_metrics["rmse"],
            "test_mae": test_metrics["mae"],
            "test_clinical_accuracy": clinical_metrics["accuracy"],
            "test_clinical_f1_macro": clinical_metrics["f1_macro"],
            "model_details": _fitted_model_details(fitted_model),
            "runtime_seconds": round(time.perf_counter() - start_time, 3),
        }
        model_results.append(result)
        predictions[model_name] = test_pred
        fitted_models[model_name] = fitted_model

    ranked_results = sorted(model_results, key=_ranking_key, reverse=True)
    best_model_name = ranked_results[0]["model_name"]

    comparison_table_path = output_path / "comparison_table.csv"
    pd.DataFrame(ranked_results).to_csv(comparison_table_path, index=False)

    predictions_path = output_path / "predictions.npz"
    np.savez(predictions_path, **predictions)

    best_model_path = output_path / "best_model.pkl"
    with open(best_model_path, "wb") as f:
        pickle.dump(fitted_models[best_model_name], f)

    comparison_report_path = output_path / "comparison_report.json"
    report = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "raw_csv_path": raw_csv_path,
        "processed_data_path": str(processed_path),
        "preprocessing": preprocessing_result,
        "ranking": {
            "primary": "highest test_r2",
            "tie_breaker": "lowest test_rmse",
        },
        "best_model": ranked_results[0],
        "models_compared": len(ranked_results),
        "model_results": ranked_results,
        "artifact_paths": {
            "comparison_report": str(comparison_report_path),
            "comparison_table": str(comparison_table_path),
            "predictions": str(predictions_path),
            "best_model": str(best_model_path),
        },
    }
    with open(comparison_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def _print_cli_summary(report: dict[str, Any]) -> None:
    best_model = report["best_model"]
    artifact_paths = report["artifact_paths"]
    print("Model comparison completed")
    print(f"Best model: {best_model['model_name']}")
    print(f"Test R2: {best_model['test_r2']:.4f}")
    print(f"Test RMSE: {best_model['test_rmse']:.4f}")
    print(f"Test MAE: {best_model['test_mae']:.4f}")
    print(f"Comparison report: {artifact_paths['comparison_report']}")
    print(f"Comparison table: {artifact_paths['comparison_table']}")
    print(f"Saved best model: {artifact_paths['best_model']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare regression models for GlicoSaliva data.")
    parser.add_argument("--raw-csv", default="src/data/dummy/generated_data.csv")
    parser.add_argument("--output-dir", default="src/models/model_comparison")
    parser.add_argument("--processed-data-path", default=None)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    report = compare_regression_models(
        raw_csv_path=args.raw_csv,
        output_dir=args.output_dir,
        processed_data_path=args.processed_data_path,
        config={
            "test_size": args.test_size,
            "n_splits": args.n_splits,
            "random_state": args.random_state,
        },
    )
    _print_cli_summary(report)


if __name__ == "__main__":
    main()


__all__ = [
    "DEFAULT_CONFIG",
    "_build_candidate_models",
    "_clinical_metrics",
    "_mgdl_to_class",
    "_ranking_key",
    "compare_regression_models",
]
