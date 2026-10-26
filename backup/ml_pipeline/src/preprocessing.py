"""Data preprocessing pipeline for the GlicoSaliva ML project."""

from __future__ import annotations

import json
import logging
import os
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DataQualityWarning(UserWarning):
    pass


REQUIRED_COLUMNS = [
    "id",
    "glucose_saliva",
    "ph_value",
    "fructosamine_umol_l",
    "bg_class",
    "bg_mgdl_reference",
]

FEATURE_COLUMNS = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]

DEFAULT_CONFIG = {
    "test_size": 0.2,
    "target_label": "bg_mgdl_reference",
    "stratify_label": "bg_class",
    "missing_value_strategy": "median",
    "outlier_detection_method": "IQR",
    "outlier_multiplier": 1.5,
    "outlier_strategy": "remove",
    "scaler_type": "StandardScaler",
    "random_state": 42,
}


def _validate_input_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input CSV not found: {path}")
    df = pd.read_csv(path)
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    return df


def _detect_outliers_iqr(df: pd.DataFrame, feature: str, multiplier: float):
    q1 = df[feature].quantile(0.25)
    q3 = df[feature].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    outliers = df[(df[feature] < lower_bound) | (df[feature] > upper_bound)].index
    return outliers, q1, q3, iqr


def _handle_missing_values(
    df: pd.DataFrame,
    feature_columns: list,
    config: dict,
    original_counts: dict,
) -> pd.DataFrame:
    df = df.copy()
    strategy = config.get("missing_value_strategy", "median")
    for feature in feature_columns:
        missing_ratio = df[feature].isna().sum() / len(df)
        if missing_ratio > 0.10:
            warnings.warn(
                f"Feature '{feature}' has {missing_ratio:.1%} missing values (>10%). Auto-removing rows with missing values.",
                DataQualityWarning,
            )
            df = df.dropna(subset=[feature])

    if strategy != "median":
        strategy = "median"

    for feature in feature_columns:
        if df[feature].isna().any():
            median_val = df[feature].median()
            if pd.isna(median_val):
                median_val = 0.0
            df[feature] = df[feature].fillna(median_val)
            logger.info(
                "Imputed %s missing values in '%s' with median: %.4f",
                original_counts[feature],
                feature,
                median_val,
            )
    return df


def _remove_outliers(df: pd.DataFrame, feature_columns: list, config: dict):
    df = df.copy()
    multiplier = float(config.get("outlier_multiplier", 1.5))
    if multiplier <= 0:
        warnings.warn(f"IQR multiplier {multiplier} is invalid, clamping to 1.5")
        multiplier = 1.5

    outlier_strategy = config.get("outlier_strategy", "remove")
    outlier_counts = {}
    if outlier_strategy == "remove":
        for feature in feature_columns:
            outliers, q1, q3, iqr = _detect_outliers_iqr(df, feature, multiplier)
            outlier_counts[feature] = len(outliers)
            if len(outliers) > 0:
                df = df.drop(outliers)
                logger.info(
                    "Removed %d outliers from '%s' (bounds: [%.4f, %.4f])",
                    len(outliers),
                    feature,
                    q1 - multiplier * iqr,
                    q3 + multiplier * iqr,
                )
    return df, outlier_counts


def _handle_zero_variance(df: pd.DataFrame, feature_columns: list):
    df = df.copy()
    dropped_features = []
    remaining_features = list(feature_columns)

    for feature in feature_columns:
        if feature in df.columns and df[feature].std() == 0:
            warnings.warn(
                f"Feature '{feature}' has zero variance (all values identical). Removing feature.",
                DataQualityWarning,
            )
            dropped_features.append(feature)

    for feature in dropped_features:
        if feature in df.columns:
            df = df.drop(columns=[feature])
        if feature in remaining_features:
            remaining_features.remove(feature)
    return df, remaining_features


def _fit_scaler(X_train: np.ndarray, scaler_type: str, random_state: int):
    scaler = StandardScaler()
    scaler.fit(X_train)
    return scaler, scaler.mean_, scaler.scale_


def _save_scaler_params(
    output_dir: str,
    feature_names: list,
    means: np.ndarray,
    stds: np.ndarray,
    n_train_samples: int,
    n_test_samples: int,
    max_retries: int = 3,
) -> None:
    scaler_params = {
        "feature_names": feature_names,
        "means": means.tolist(),
        "stds": stds.tolist(),
        "n_train_samples": n_train_samples,
        "n_test_samples": n_test_samples,
    }
    filepath = Path(output_dir) / "scaler_params.json"
    for attempt in range(1, max_retries + 1):
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(scaler_params, f, indent=2)
            return
        except Exception as exc:
            if attempt == max_retries:
                raise FileNotFoundError(f"Unable to save scaler parameters to {filepath} after {max_retries} retries") from exc
            warnings.warn(f"Scaler params save attempt {attempt} failed: {exc}. Retrying...")


def _generate_preprocessing_report(
    original_n_samples: int,
    missing_counts_before: dict,
    imputation_strategy: str,
    outlier_counts: dict,
    outlier_strategy: str,
    final_train_samples: int,
    final_test_samples: int,
    stratification_ratios: dict,
    timestamp: str,
) -> dict:
    return {
        "original_n_samples": original_n_samples,
        "missing_values_before": missing_counts_before,
        "imputation_strategy": imputation_strategy,
        "outliers_detected": outlier_counts,
        "outlier_strategy": outlier_strategy,
        "final_train_samples": final_train_samples,
        "final_test_samples": final_test_samples,
        "stratification_ratios": stratification_ratios,
        "timestamp": timestamp,
    }


def _calculate_stratification_ratios(y_train: np.ndarray, y_test: np.ndarray) -> dict:
    unique_classes = np.unique(np.concatenate([y_train, y_test]))
    ratios = {}
    for class_id in unique_classes:
        train_count = int((y_train == class_id).sum())
        test_count = int((y_test == class_id).sum())
        train_total = len(y_train)
        test_total = len(y_test)
        ratios[str(int(class_id))] = [
            round(train_count / train_total, 2) if train_total else 0.0,
            round(test_count / test_total, 2) if test_total else 0.0,
        ]
    return ratios


def preprocess(
    raw_csv_path: str,
    output_dir: str = "data/processed",
    config: dict | None = None,
) -> dict:
    if config is None:
        config = DEFAULT_CONFIG.copy()
    else:
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)
        config = merged

    test_size = float(config.get("test_size", 0.2))
    target_label = config.get("target_label", "bg_mgdl_reference")
    stratify_label = config.get("stratify_label", "bg_class")
    outlier_multiplier = float(config.get("outlier_multiplier", 1.5))
    outlier_strategy = config.get("outlier_strategy", "remove")
    scaler_type = config.get("scaler_type", "StandardScaler")
    random_state = int(config.get("random_state", 42))

    if outlier_multiplier <= 0:
        warnings.warn(f"IQR multiplier {outlier_multiplier} is invalid, clamping to 1.5")
        outlier_multiplier = 1.5

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info("Loading data from %s", raw_csv_path)
    df = _validate_input_csv(raw_csv_path)
    original_n_samples = len(df)

    missing_counts_before = {feature: int(df[feature].isna().sum()) for feature in FEATURE_COLUMNS}
    df = _handle_missing_values(df, FEATURE_COLUMNS, config, missing_counts_before)

    active_features = FEATURE_COLUMNS.copy()
    df, active_features = _handle_zero_variance(df, active_features)
    df, outlier_counts = _remove_outliers(df, active_features, {**config, "outlier_multiplier": outlier_multiplier, "outlier_strategy": outlier_strategy})

    X = df[active_features].values.astype(np.float64)
    y = df[target_label].values.astype(np.float64)
    stratify_y = df[stratify_label].values.astype(np.int64)

    if len(np.unique(stratify_y)) < 2:
        raise ValueError("Cannot perform stratified split: only one class label present")

    X_train, X_test, y_train, y_test, stratify_train, stratify_test = train_test_split(
        X,
        y,
        stratify_y,
        test_size=test_size,
        stratify=stratify_y,
        random_state=random_state,
    )

    if len(X_test) == 0:
        raise ValueError(
            "Test set is empty after split. Consider reducing test_size or increasing sample size."
        )

    scaler, mean, std = _fit_scaler(X_train, scaler_type, random_state)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    np.save(output_path / "X_train.npy", X_train_scaled)
    np.save(output_path / "X_test.npy", X_test_scaled)
    np.save(output_path / "y_train.npy", y_train)
    np.save(output_path / "y_test.npy", y_test)

    _save_scaler_params(
        output_dir=str(output_path),
        feature_names=active_features,
        means=mean,
        stds=std,
        n_train_samples=len(X_train_scaled),
        n_test_samples=len(X_test_scaled),
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = _generate_preprocessing_report(
        original_n_samples=original_n_samples,
        missing_counts_before=missing_counts_before,
        imputation_strategy=config.get("missing_value_strategy", "median"),
        outlier_counts=outlier_counts,
        outlier_strategy=outlier_strategy,
        final_train_samples=len(X_train_scaled),
        final_test_samples=len(X_test_scaled),
        stratification_ratios=_calculate_stratification_ratios(stratify_train, stratify_test),
        timestamp=timestamp,
    )
    report["feature_names"] = active_features
    report["target_label"] = target_label
    report["stratify_label"] = stratify_label

    with open(output_path / "preprocessing_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return {
        "X_train_path": str(output_path / "X_train.npy"),
        "X_test_path": str(output_path / "X_test.npy"),
        "y_train_path": str(output_path / "y_train.npy"),
        "y_test_path": str(output_path / "y_test.npy"),
        "scaler_params_path": str(output_path / "scaler_params.json"),
        "preprocessing_report_path": str(output_path / "preprocessing_report.json"),
        "train_samples": len(X_train_scaled),
        "test_samples": len(X_test_scaled),
        "feature_names": active_features,
        "target_label": target_label,
        "stratify_label": stratify_label,
        "scaler_type": scaler_type,
    }


__all__ = [
    "DataQualityWarning",
    "REQUIRED_COLUMNS",
    "FEATURE_COLUMNS",
    "DEFAULT_CONFIG",
    "_validate_input_csv",
    "_detect_outliers_iqr",
    "_handle_missing_values",
    "_remove_outliers",
    "_handle_zero_variance",
    "_fit_scaler",
    "_save_scaler_params",
    "_generate_preprocessing_report",
    "_calculate_stratification_ratios",
    "preprocess",
]
