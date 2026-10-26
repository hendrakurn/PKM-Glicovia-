"""Data loading and validation utilities for the GlicoSaliva ML pipeline."""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from src.generate_dummy import generate_dummy

REQUIRED_COLUMNS = [
    "id",
    "glucose_saliva",
    "ph_value",
    "fructosamine_umol_l",
    "bg_class",
    "bg_mgdl_reference",
]

FEATURE_COLUMNS = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]
TARGET_COLUMNS = ["bg_class", "bg_mgdl_reference"]

DEFAULT_VALIDATION_THRESHOLDS = {
    "min_samples": 10,
    "max_missing_ratio": 0.10,
    "max_outlier_ratio": 0.05,
    "max_zero_variance_features": 0,
}


class DataLoaderError(ValueError):
    pass


def _validate_required_columns(df: pd.DataFrame) -> List[str]:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise DataLoaderError(f"Missing required columns: {missing}")
    return []


def _check_missing_values(df: pd.DataFrame, cols: Optional[Sequence[str]] = None) -> Dict[str, float]:
    cols = list(cols or FEATURE_COLUMNS)
    return {col: float(df[col].isna().mean()) if col in df.columns else 1.0 for col in cols}


def _check_zero_variance(df: pd.DataFrame, feature_cols: Sequence[str]) -> List[str]:
    zero_variance = []
    for col in feature_cols:
        if col in df.columns and df[col].nunique(dropna=True) <= 1:
            zero_variance.append(col)
    return zero_variance


def _detect_outliers_iqr(df: pd.DataFrame, feature_cols: Sequence[str], multiplier: float = 1.5) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for col in feature_cols:
        if col not in df.columns or df[col].dropna().empty:
            counts[col] = 0
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low = q1 - multiplier * iqr
        high = q3 + multiplier * iqr
        counts[col] = int(((df[col] < low) | (df[col] > high)).sum())
    return counts


def _assess_quality_status(
    total_samples: int,
    missing_ratio: float,
    outlier_ratio: float,
    zero_variance_features: Sequence[str],
    thresholds: Optional[Dict[str, float]] = None,
) -> str:
    thresholds = {**DEFAULT_VALIDATION_THRESHOLDS, **(thresholds or {})}
    if total_samples < thresholds["min_samples"]:
        return "ERROR"
    if len(zero_variance_features) > thresholds["max_zero_variance_features"]:
        return "WARNING"
    if missing_ratio > thresholds["max_missing_ratio"] or outlier_ratio > thresholds["max_outlier_ratio"]:
        return "WARNING"
    return "PASS"


def _build_report(df: pd.DataFrame, thresholds: Dict[str, float], source: str) -> Dict[str, Any]:
    missing = _check_missing_values(df, FEATURE_COLUMNS)
    zero_variance = _check_zero_variance(df, FEATURE_COLUMNS)
    outlier_counts = _detect_outliers_iqr(df, FEATURE_COLUMNS, thresholds.get("outlier_iqr_multiplier", 1.5))
    total_outliers = sum(outlier_counts.values())
    outlier_ratio = total_outliers / (len(df) * len(FEATURE_COLUMNS)) if len(df) and FEATURE_COLUMNS else 0.0
    missing_ratio = float(np.mean(list(missing.values()))) if missing else 0.0
    quality_status = _assess_quality_status(len(df), missing_ratio, outlier_ratio, zero_variance, thresholds)
    return {
        "source": source,
        "total_samples": int(len(df)),
        "feature_columns": FEATURE_COLUMNS.copy(),
        "missing_values": missing,
        "zero_variance_features": zero_variance,
        "outlier_counts": outlier_counts,
        "quality_status": quality_status,
    }


def load_data(
    file_path: Optional[str] = None,
    data: Optional[pd.DataFrame] = None,
    validate: bool = True,
    thresholds: Optional[Dict[str, float]] = None,
    auto_fallback: bool = False,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load a CSV or DataFrame and return a report."""
    thresholds = {**DEFAULT_VALIDATION_THRESHOLDS, **(thresholds or {})}

    if data is not None:
        df = data.copy()
        source = "dataframe"
    elif file_path:
        path = Path(file_path)
        if not path.exists():
            if auto_fallback:
                df, _ = generate_dummy(random_state=random_state)
                source = "auto_fallback"
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        else:
            df = pd.read_csv(path)
            source = str(path)
    else:
        if auto_fallback:
            df, _ = generate_dummy(random_state=random_state)
            source = "auto_fallback"
        else:
            raise DataLoaderError("Either file_path or data must be provided")

    if validate:
        _validate_required_columns(df)
        df = df.copy()
        for col in FEATURE_COLUMNS:
            if df[col].isna().any():
                median = df[col].median()
                df[col] = df[col].fillna(0.0 if pd.isna(median) else median)
        report = _build_report(df, thresholds, source)
    else:
        report = {
            "source": source,
            "total_samples": int(len(df)),
            "feature_columns": FEATURE_COLUMNS.copy(),
            "quality_status": "UNVALIDATED",
        }
    return df, report


def load_batch(
    file_paths: Sequence[str],
    validate: bool = True,
    auto_fallback: bool = False,
    random_state: int = 42,
) -> List[Tuple[pd.DataFrame, Dict[str, Any]]]:
    results: List[Tuple[pd.DataFrame, Dict[str, Any]]] = []
    for file_path in file_paths:
        try:
            results.append(load_data(file_path=file_path, validate=validate, auto_fallback=auto_fallback, random_state=random_state))
        except Exception as exc:
            results.append((pd.DataFrame(), {"source": file_path, "quality_status": "ERROR", "error": str(exc)}))
    return results


def export_to_json(df: pd.DataFrame, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(df.to_json(orient="records", indent=2), encoding="utf-8")
    return str(path)


def export_to_csv(df: pd.DataFrame, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return str(path)


__all__ = [
    "REQUIRED_COLUMNS",
    "FEATURE_COLUMNS",
    "TARGET_COLUMNS",
    "DEFAULT_VALIDATION_THRESHOLDS",
    "DataLoaderError",
    "_validate_required_columns",
    "_check_missing_values",
    "_check_zero_variance",
    "_detect_outliers_iqr",
    "_assess_quality_status",
    "load_data",
    "load_batch",
    "export_to_json",
    "export_to_csv",
]
