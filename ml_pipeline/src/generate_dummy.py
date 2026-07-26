"""
generate_dummy.py - Dummy Data Generator for GlicoSaliva ML Pipeline

Generates synthetic saliva datasets with realistic physiological distributions
for SVM-based regression and clinical category reporting.

Target: 150 samples with 3-class imbalance (40% Normal, 35% Pre-Diabetes, 25% Diabetes)
"""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Default physiological distributions for the exploratory biomarker schema.
DEFAULT_CLASS_MEANS = {
    "Normal": {"glucose": 0.5, "ph": 7.0, "fructosamine": 220.0},
    "Pre-Diabetes": {"glucose": 1.2, "ph": 6.5, "fructosamine": 285.0},
    "Diabetes": {"glucose": 3.5, "ph": 6.0, "fructosamine": 375.0},
}

DEFAULT_CLASS_STDS = {
    "Normal": {"glucose": 0.2, "ph": 0.3, "fructosamine": 18.0},
    "Pre-Diabetes": {"glucose": 0.4, "ph": 0.4, "fructosamine": 25.0},
    "Diabetes": {"glucose": 1.0, "ph": 0.5, "fructosamine": 40.0},
}

DEFAULT_CLASS_WEIGHTS = {
    "Normal": 0.4,
    "Pre-Diabetes": 0.35,
    "Diabetes": 0.25,
}

# Physiological feature bounds
FEATURE_BOUNDS = {
    "glucose_saliva": (0.1, 10.0),
    "ph_value": (4.0, 9.0),
    "fructosamine_umol_l": (150.0, 500.0),
}

CLASS_LABELS = {
    0: "Normal",
    1: "Pre-Diabetes",
    2: "Diabetes",
}


def _validate_class_weights(weights: dict) -> dict:
    """Validate and normalize class weights."""
    required_classes = {"Normal", "Pre-Diabetes", "Diabetes"}
    if set(weights.keys()) != required_classes:
        raise ValueError(f"Weights must contain keys: {required_classes}")

    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Class weights must sum to a positive value")
    if not np.isclose(total, 1.0, atol=1e-6):
        warnings.warn(
            f"Class weights sum to {total:.4f}, not 1.0. Auto-normalizing weights.",
            UserWarning,
        )
        weights = {k: v / total for k, v in weights.items()}
    return weights


def _clamp_series(series: pd.Series, lower: float, upper: float) -> tuple[pd.Series, int]:
    """Clamp series values to bounds."""
    mask_low = series < lower
    mask_high = series > upper
    count_clamped = int(mask_low.sum() + mask_high.sum())
    if count_clamped == 0:
        return series, 0

    result = series.copy()
    result = result.where(~mask_low, lower)
    result = result.where(~mask_high, upper)
    return result, count_clamped


def _clamp_df_features(
    df: pd.DataFrame,
    feature_bounds: dict[str, tuple[float, float]],
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Clamp all features in a DataFrame to their physiological bounds."""
    df = df.copy()
    clamped_counts: dict[str, int] = {}

    for feature, (lower, upper) in feature_bounds.items():
        if feature in df.columns:
            df[feature], count = _clamp_series(df[feature], lower, upper)
            clamped_counts[feature] = count

    return df, clamped_counts


def _generate_bg_reference(
    rng: np.random.Generator,
    glucose_saliva: pd.Series,
    fructosamine_umol_l: pd.Series,
    bg_class: pd.Series,
) -> pd.Series:
    """Generate ground truth blood glucose reference (mg/dL).

    The target uses class-aware baselines with moderate contributions from
    saliva glucose and fructosamine so the biomarker remains exploratory and
    does not become a deterministic proxy.
    """
    bg_reference = pd.Series(index=glucose_saliva.index, dtype=float)
    fruct_centered = fructosamine_umol_l - 285.0

    normal_mask = bg_class == 0
    pre_mask = bg_class == 1
    diabetes_mask = bg_class == 2

    if normal_mask.any():
        n = int(normal_mask.sum())
        bg_reference.loc[normal_mask] = (
            78.0
            + glucose_saliva.loc[normal_mask] * 18.0
            + fruct_centered.loc[normal_mask] * 0.12
            + rng.normal(0, 4.0, n)
        )
    if pre_mask.any():
        n = int(pre_mask.sum())
        bg_reference.loc[pre_mask] = (
            108.0
            + glucose_saliva.loc[pre_mask] * 24.0
            + fruct_centered.loc[pre_mask] * 0.15
            + rng.normal(0, 6.0, n)
        )
    if diabetes_mask.any():
        n = int(diabetes_mask.sum())
        bg_reference.loc[diabetes_mask] = (
            145.0
            + glucose_saliva.loc[diabetes_mask] * 35.0
            + fruct_centered.loc[diabetes_mask] * 0.18
            + rng.normal(0, 10.0, n)
        )

    return bg_reference.clip(60, 500)


def _generate_outliers(
    df: pd.DataFrame,
    rng: np.random.Generator,
    outlier_ratio: float,
    clamp: bool = True,
) -> tuple[pd.DataFrame, int]:
    """Insert synthetic outliers into the dataset."""
    if len(df) == 0 or outlier_ratio <= 0:
        return df.copy(), 0

    df = df.copy()
    n_outliers = max(1, int(len(df) * outlier_ratio))
    outlier_indices = rng.choice(len(df), size=n_outliers, replace=False)

    for idx in outlier_indices:
        feature = rng.choice(["glucose_saliva", "ph_value", "fructosamine_umol_l"])
        lower, upper = FEATURE_BOUNDS[feature]
        if rng.random() < 0.5:
            outlier_val = lower - rng.uniform(1, 3) * (upper - lower) * 0.1
        else:
            outlier_val = upper + rng.uniform(1, 3) * (upper - lower) * 0.1
        df.loc[idx, feature] = outlier_val

    if clamp:
        df, _ = _clamp_df_features(df, FEATURE_BOUNDS)
    return df, int(n_outliers)


def _retry_csv_write(filepath: Path, df: pd.DataFrame, max_retries: int = 3) -> None:
    """Write CSV with retry logic."""
    last_exception: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(filepath, index=False)
            return
        except Exception as exc:  # pragma: no cover - best-effort retry path
            last_exception = exc
            if attempt < max_retries:
                warnings.warn(f"CSV write attempt {attempt} failed: {exc}. Retrying...")
            else:
                warnings.warn(f"CSV write failed after {max_retries} attempts: {exc}")
    raise FileNotFoundError(f"Unable to write CSV to {filepath} after {max_retries} retries") from last_exception


def generate_dummy(
    n_samples: int = 150,
    class_weights: dict | None = None,
    class_means: dict | None = None,
    class_stds: dict | None = None,
    noise_sigma: float = 0.1,
    outlier_ratio: float = 0.03,
    random_state: int = 42,
    output_dir: str = "data/dummy",
) -> tuple[pd.DataFrame, dict]:
    """Generate synthetic saliva dataset with physiological distributions."""
    if n_samples < 10:
        raise ValueError(f"n_samples must be at least 10, got {n_samples}")

    rng = np.random.default_rng(random_state)

    class_weights = _validate_class_weights(
        (class_weights or DEFAULT_CLASS_WEIGHTS).copy()
    )
    class_means = {k: v.copy() for k, v in (class_means or DEFAULT_CLASS_MEANS).items()}
    class_stds = {k: v.copy() for k, v in (class_stds or DEFAULT_CLASS_STDS).items()}

    class_names = ["Normal", "Pre-Diabetes", "Diabetes"]
    samples_per_class: dict[str, int] = {}
    remaining = n_samples
    for i, class_name in enumerate(class_names):
        if i == len(class_names) - 1:
            samples_per_class[class_name] = remaining
        else:
            n = int(n_samples * class_weights[class_name])
            samples_per_class[class_name] = n
            remaining -= n

    rows = []
    for class_idx, class_name in enumerate(class_names):
        n = samples_per_class[class_name]
        if n <= 0:
            continue

        glucose = rng.normal(class_means[class_name]["glucose"], class_stds[class_name]["glucose"], size=n)
        ph = rng.normal(class_means[class_name]["ph"], class_stds[class_name]["ph"], size=n)
        fruct = rng.normal(class_means[class_name]["fructosamine"], class_stds[class_name]["fructosamine"], size=n)

        glucose = glucose + rng.normal(0, noise_sigma, size=n)
        ph = ph + rng.normal(0, noise_sigma, size=n)
        fruct = fruct + rng.normal(0, noise_sigma * 10, size=n)

        glucose, _ = _clamp_series(pd.Series(glucose), *FEATURE_BOUNDS["glucose_saliva"])
        ph, _ = _clamp_series(pd.Series(ph), *FEATURE_BOUNDS["ph_value"])
        fruct, _ = _clamp_series(pd.Series(fruct), *FEATURE_BOUNDS["fructosamine_umol_l"])

        for i in range(n):
            rows.append(
                {
                    "id": len(rows),
                    "glucose_saliva": float(glucose.iloc[i]),
                    "ph_value": float(ph.iloc[i]),
                    "fructosamine_umol_l": float(fruct.iloc[i]),
                    "bg_class": class_idx,
                    "bg_mgdl_reference": 0.0,
                }
            )

    df = pd.DataFrame(rows)
    df, n_outliers = _generate_outliers(df, rng, outlier_ratio, clamp=True)
    df["bg_mgdl_reference"] = _generate_bg_reference(
        rng,
        df["glucose_saliva"],
        df["fructosamine_umol_l"],
        df["bg_class"],
    )

    class_distribution = {
        class_name: int((df["bg_class"] == idx).sum())
        for idx, class_name in enumerate(class_names)
    }
    feature_ranges = {
        col: [round(float(df[col].min()), 4), round(float(df[col].max()), 4)]
        for col in ["glucose_saliva", "ph_value", "fructosamine_umol_l"]
    }

    metadata = {
        "total_samples": int(len(df)),
        "class_distribution": class_distribution,
        "feature_ranges": feature_ranges,
        "noise_level": f"Gaussian(sigma={noise_sigma})",
        "outlier_count": int(n_outliers),
        "random_state": int(random_state),
        "generation_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    _retry_csv_write(output_path / "generated_data.csv", df)
    with open(output_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return df, metadata


if __name__ == "__main__":
    print("Generating dummy dataset...")
    df, meta = generate_dummy(n_samples=150, random_state=42)
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Class distribution: {meta['class_distribution']}")
    print(f"Feature ranges: {meta['feature_ranges']}")
    print(f"Outlier count: {meta['outlier_count']}")
    print("Data saved to: data/dummy/generated_data.csv")
    print("Metadata saved to: data/dummy/metadata.json")
    print(df.head(10).to_string(index=False))
