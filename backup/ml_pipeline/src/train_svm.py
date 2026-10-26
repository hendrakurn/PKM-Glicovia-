"""
train_svm.py - Regression Training Pipeline for GlicoSaliva ML Pipeline

Trains an SVR model with GridSearchCV and K-Fold Cross-Validation for
non-invasive blood glucose regression in mg/dL.

Target: Train true SVR regressor with hyperparameter optimization
"""

import copy
import json
import logging
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.svm import SVR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelTrainingWarning(UserWarning):
    """Custom warning for model training issues."""
    pass


# Default configuration
DEFAULT_CONFIG = {
    "kernel": "rbf",
    "scoring": "r2",
    "n_splits": 5,
    "grid_param_space": {
        "C": [0.1, 1, 10, 100],
        "gamma": [0.01, 0.1, 0.5, 1.0],
        "epsilon": [0.1, 0.2, 0.5],
    },
    "overfitting_threshold": 0.10,
    "random_state": 42,
    "n_jobs": -1,
}


def _regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calculate common regression metrics."""
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
    }


def _mgdl_to_class(value: float) -> int:
    """Map mg/dL value to a clinical category class."""
    if value < 100:
        return 0
    if value < 126:
        return 1
    return 2


def _clinical_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Derive clinical classification metrics from regression outputs."""
    y_true_class = np.array([_mgdl_to_class(float(v)) for v in y_true], dtype=int)
    y_pred_class = np.array([_mgdl_to_class(float(v)) for v in y_pred], dtype=int)

    return {
        "accuracy": float(accuracy_score(y_true_class, y_pred_class)),
        "f1_macro": float(f1_score(y_true_class, y_pred_class, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true_class, y_pred_class).tolist(),
    }


def _build_svr(kernel: str, params: dict) -> SVR:
    """Create an SVR estimator using the selected kernel and best params."""
    safe_params = {
        key: value
        for key, value in params.items()
        if key in {"C", "gamma", "epsilon", "degree", "coef0"}
    }
    return SVR(kernel=kernel, **safe_params)


def train_svm(
    processed_data_path: str,
    output_dir: str = "models",
    config: dict = None,
) -> dict:
    """Train SVR model with GridSearchCV and K-Fold cross-validation.

    Args:
        processed_data_path: Path to data/processed/ directory containing
            X_train.npy, X_test.npy, y_train.npy, y_test.npy
        output_dir: Directory for output files (default: "models")
        config: Configuration dictionary. If None, uses DEFAULT_CONFIG.

    Returns:
        Dictionary with training results including paths to output files
    """
    merged_config = copy.deepcopy(DEFAULT_CONFIG)
    if config is not None:
        merged_config.update(copy.deepcopy(config))

    kernel = merged_config.get("kernel", "rbf")
    scoring = merged_config.get("scoring", "r2")
    n_splits = int(merged_config.get("n_splits", 5))
    grid_param_space = copy.deepcopy(
        merged_config.get("grid_param_space", DEFAULT_CONFIG["grid_param_space"])
    )
    overfitting_threshold = float(merged_config.get("overfitting_threshold", 0.10))
    random_state = int(merged_config.get("random_state", 42))
    n_jobs = int(merged_config.get("n_jobs", -1))

    input_path = Path(processed_data_path)
    required_files = ["X_train.npy", "X_test.npy", "y_train.npy", "y_test.npy"]
    for filename in required_files:
        if not (input_path / filename).exists():
            raise FileNotFoundError(f"Input file not found: {input_path / filename}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    fold_results_dir = output_path / "fold_results"
    fold_results_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading data from {processed_data_path}")
    X_train = np.load(input_path / "X_train.npy")
    X_test = np.load(input_path / "X_test.npy")
    y_train = np.load(input_path / "y_train.npy").astype(np.float64)
    y_test = np.load(input_path / "y_test.npy").astype(np.float64)

    logger.info(f"Loaded data - X_train: {X_train.shape}, X_test: {X_test.shape}")
    if len(X_test) == 0:
        raise ValueError("Test set is empty. Cannot proceed with training.")
    if len(X_train) < 2:
        raise ValueError("Training set is too small for cross-validation.")

    logger.info(
        "y_train range: [%.2f, %.2f], y_test range: [%.2f, %.2f]",
        float(np.min(y_train)), float(np.max(y_train)),
        float(np.min(y_test)), float(np.max(y_test)),
    )
    # Clamp overly large numeric gamma values to keep the search stable.
    if "gamma" in grid_param_space:
        clamped_gamma = []
        for gamma in grid_param_space["gamma"]:
            if isinstance(gamma, (int, float)) and gamma > 1.0:
                message = f"Gamma value {gamma} > 1.0, clamping to 1.0"
                logger.warning(message)
                warnings.warn(message)
                clamped_gamma.append(1.0)
            else:
                clamped_gamma.append(gamma)
        grid_param_space["gamma"] = clamped_gamma

    n_splits = min(n_splits, len(X_train))
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2 after validation.")

    logger.info(f"Setting up {n_splits}-fold K-Fold cross-validation")
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    logger.info("Initializing GridSearchCV for SVR")
    start_time = datetime.now(timezone.utc)

    try:
        try:
            grid_search = GridSearchCV(
                estimator=_build_svr(kernel=kernel, params={}),
                param_grid=grid_param_space,
                scoring=scoring,
                cv=cv,
                n_jobs=n_jobs,
                refit=True,
                error_score="raise",
            )
            grid_search.fit(X_train, y_train)
        except MemoryError:
            logger.warning("Memory error during GridSearchCV, reducing grid search space")
            reduced_param_space = {
                "C": list(grid_param_space.get("C", [0.1, 1, 10, 100]))[:2],
                "gamma": list(grid_param_space.get("gamma", ["scale", "auto", 0.01, 0.1]))[:2],
                "epsilon": list(grid_param_space.get("epsilon", [0.1, 0.2, 0.5]))[:2],
            }
            grid_search = GridSearchCV(
                estimator=_build_svr(kernel=kernel, params={}),
                param_grid=reduced_param_space,
                scoring=scoring,
                cv=cv,
                n_jobs=n_jobs,
                refit=True,
                error_score="raise",
            )
            grid_search.fit(X_train, y_train)
            grid_param_space = reduced_param_space
    except Exception as e:
        logger.error(f"GridSearchCV failed: {e}")
        raise

    best_model = grid_search.best_estimator_
    best_params = grid_search.best_params_
    logger.info(f"Best params: {best_params}")

    logger.info("Performing detailed cross-validation")
    cv_results = []
    for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train)):
        fold_start = datetime.now(timezone.utc)
        X_fold_train, X_fold_val = X_train[train_idx], X_train[val_idx]
        y_fold_train, y_fold_val = y_train[train_idx], y_train[val_idx]

        fold_model = _build_svr(kernel=kernel, params=best_params)
        fold_model.fit(X_fold_train, y_fold_train)
        y_fold_pred = fold_model.predict(X_fold_val)

        fold_runtime = (datetime.now(timezone.utc) - fold_start).total_seconds()
        if fold_runtime > 30 * 60:
            warnings.warn(
                f"Fold {fold_idx} runtime {fold_runtime:.2f}s exceeds 30 min threshold"
            )

        metrics = _regression_metrics(y_fold_val, y_fold_pred)
        clinical = _clinical_metrics(y_fold_val, y_fold_pred)
        unique_pred = np.unique(np.round(y_fold_pred, 6))
        if len(unique_pred) == 1:
            warnings.warn(
                f"Fold {fold_idx}: All predictions are identical. Model may be failing to learn properly.",
                ModelTrainingWarning,
            )

        fold_result = {
            "fold": fold_idx,
            "params": best_params.copy(),
            "rmse": metrics["rmse"],
            "mae": metrics["mae"],
            "r2": metrics["r2"],
            "accuracy": clinical["accuracy"],
            "f1_macro": clinical["f1_macro"],
            "confusion_matrix": clinical["confusion_matrix"],
            "runtime_seconds": round(fold_runtime, 3),
        }
        cv_results.append(fold_result)

        fold_file = fold_results_dir / f"fold_{fold_idx}.json"
        with open(fold_file, "w") as f:
            json.dump(fold_result, f, indent=2)

        logger.info(
            "Fold %s: R2=%.4f, RMSE=%.4f, MAE=%.4f, Runtime=%.3fs",
            fold_idx,
            metrics["r2"],
            metrics["rmse"],
            metrics["mae"],
            fold_runtime,
        )

    logger.info("Evaluating on test set")
    y_test_pred = best_model.predict(X_test)
    train_pred = best_model.predict(X_train)

    test_metrics = _regression_metrics(y_test, y_test_pred)
    train_metrics = _regression_metrics(y_train, train_pred)
    test_clinical = _clinical_metrics(y_test, y_test_pred)
    train_clinical = _clinical_metrics(y_train, train_pred)

    gap = train_metrics["r2"] - test_metrics["r2"]
    overfitting_detected = gap > overfitting_threshold
    gap_warning = overfitting_detected

    if overfitting_detected:
        warnings.warn(
            f"Overfitting detected: train_r2 ({train_metrics['r2']:.4f}) - "
            f"test_r2 ({test_metrics['r2']:.4f}) = {gap:.4f} > "
            f"threshold ({overfitting_threshold})"
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    experiment_log = {
        "model_type": "SVR",
        "kernel": kernel,
        "primary_scoring": scoring,
        "best_params": best_params,
        "cv_results": cv_results,
        "overfitting_detected": overfitting_detected,
        "overfitting_threshold": overfitting_threshold,
        "train_r2": train_metrics["r2"],
        "test_r2": test_metrics["r2"],
        "train_rmse": train_metrics["rmse"],
        "test_rmse": test_metrics["rmse"],
        "train_mae": train_metrics["mae"],
        "test_mae": test_metrics["mae"],
        "train_accuracy": train_clinical["accuracy"],
        "test_accuracy": test_clinical["accuracy"],
        "train_f1_macro": train_clinical["f1_macro"],
        "test_f1_macro": test_clinical["f1_macro"],
        "train_confusion_matrix": train_clinical["confusion_matrix"],
        "test_confusion_matrix": test_clinical["confusion_matrix"],
        "gap_warning": gap_warning,
        "timestamp": timestamp,
        "training_duration_seconds": round((datetime.now(timezone.utc) - start_time).total_seconds(), 3),
    }

    log_file = output_path / "experiment_log.json"
    with open(log_file, "w") as f:
        json.dump(experiment_log, f, indent=2)
    logger.info(f"Experiment log saved to {log_file}")

    model_file = output_path / "best_model.pkl"
    import pickle
    with open(model_file, "wb") as f:
        pickle.dump(best_model, f)
    logger.info(f"Best model saved to {model_file}")

    return {
        "best_model_path": str(model_file),
        "experiment_log_path": str(log_file),
        "fold_results_dir": str(fold_results_dir),
        "best_params": best_params,
        "train_r2": train_metrics["r2"],
        "test_r2": test_metrics["r2"],
        "train_rmse": train_metrics["rmse"],
        "test_rmse": test_metrics["rmse"],
        "train_mae": train_metrics["mae"],
        "test_mae": test_metrics["mae"],
        "train_accuracy": train_clinical["accuracy"],
        "test_accuracy": test_clinical["accuracy"],
        "train_f1_macro": train_clinical["f1_macro"],
        "test_f1_macro": test_clinical["f1_macro"],
        "train_confusion_matrix": train_clinical["confusion_matrix"],
        "test_confusion_matrix": test_clinical["confusion_matrix"],
        "train_score": train_metrics["r2"],
        "test_score": test_metrics["r2"],
        "overfitting_detected": overfitting_detected,
        "gap_warning": gap_warning,
        "cv_results": cv_results,
    }


if __name__ == "__main__":
    result = train_svm(
        processed_data_path="data/processed/",
        output_dir="models/",
    )
    print("Training completed successfully!")
    print(f"Best model: {result['best_model_path']}")
    print(f"Train R2: {result['train_r2']:.4f}")
    print(f"Test R2: {result['test_r2']:.4f}")
