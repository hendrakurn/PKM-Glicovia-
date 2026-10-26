"""Real-time inference utilities for the GlicoSaliva ML pipeline."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class InferenceError(ValueError):
    pass


class PredictionConfidenceWarning(UserWarning):
    pass


BLOOD_GLUCOSE_CATEGORIES = {
    0: {"name": "Normal", "range_mgdl": (70, 100), "range_mmol": (3.9, 5.6)},
    1: {"name": "Pre-Diabetes", "range_mgdl": (100, 125), "range_mmol": (5.6, 6.9)},
    2: {"name": "Diabetes", "range_mgdl": (126, 500), "range_mmol": (7.0, 27.8)},
}

CLASS_TO_MGDL = {
    0: 85.0,
    1: 112.5,
    2: 313.0,
}

FEATURE_ORDER = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]


def _load_model(model_path: str) -> object:
    if not os.path.exists(model_path):
        raise InferenceError(f"Model file not found: {model_path}")
    try:
        import pickle

        with open(model_path, "rb") as f:
            model = pickle.load(f)
        return model
    except Exception as exc:
        raise InferenceError(f"Failed to load model: {exc}") from exc


def _load_scaler(scaler_path: str) -> object:
    if not os.path.exists(scaler_path):
        raise InferenceError(f"Scaler file not found: {scaler_path}")
    try:
        with open(scaler_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise InferenceError(f"Failed to load scaler: {exc}") from exc


def _load_scaler_from_model(model) -> Optional[object]:
    if hasattr(model, "named_steps") and "scaler" in getattr(model, "named_steps", {}):
        return model.named_steps["scaler"]
    if hasattr(model, "scaler_"):
        return model.scaler_
    if hasattr(model, "scaler"):
        return model.scaler
    return None


def preprocess_sample(
    sample: Dict[str, float],
    scaler_params: Optional[Dict] = None,
    scaler_object: Optional[object] = None,
) -> np.ndarray:
    features = []
    for feature in FEATURE_ORDER:
        if feature not in sample:
            raise InferenceError(f"Missing feature '{feature}' in sample. Required: {FEATURE_ORDER}")
        features.append(float(sample[feature]))

    X_sample = np.array(features, dtype=float).reshape(1, -1)

    if scaler_object is not None:
        X_sample = scaler_object.transform(X_sample)
    elif scaler_params is not None:
        means = np.array(scaler_params.get("means", [0, 0, 0]), dtype=float)
        stds = np.array(scaler_params.get("stds", [1, 1, 1]), dtype=float)
        feature_names = scaler_params.get("feature_names", FEATURE_ORDER)
        if list(feature_names) == FEATURE_ORDER and len(means) == X_sample.shape[1]:
            X_sample = (X_sample - means) / (stds + 1e-8)
    return X_sample


def _is_class_label(value: object) -> bool:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return False
    return numeric_value.is_integer() and int(numeric_value) in CLASS_TO_MGDL


def _prediction_value_to_mgdl(prediction_value: object) -> float:
    if _is_class_label(prediction_value):
        return float(CLASS_TO_MGDL[int(float(prediction_value))])
    return float(prediction_value)


def _predict_array(model, X_sample: np.ndarray) -> float:
    raw = model.predict(X_sample)
    if isinstance(raw, (list, tuple, np.ndarray)):
        raw = raw[0]
    return _prediction_value_to_mgdl(raw)


def _category_from_mgdl(value: float) -> dict:
    if value < 100:
        idx = 0
    elif value < 126:
        idx = 1
    else:
        idx = 2
    meta = BLOOD_GLUCOSE_CATEGORIES[idx]
    return {"class": idx, "name": meta["name"], "range_mgdl": meta["range_mgdl"], "range_mmol": meta["range_mmol"]}


def _bootstrap_confidence(
    model,
    X_sample: np.ndarray,
    n_bootstraps: int = 100,
    confidence_level: float = 0.95,
) -> Tuple[float, float, float]:
    base = float(_predict_array(model, X_sample))
    if n_bootstraps <= 1:
        return base, base, confidence_level

    rng = np.random.default_rng(42)
    perturb_scale = np.maximum(np.abs(X_sample).mean(), 1.0) * 0.02
    preds = []
    for _ in range(n_bootstraps):
        jitter = rng.normal(0, perturb_scale, size=X_sample.shape)
        try:
            preds.append(_predict_array(model, X_sample + jitter))
        except Exception:
            preds.append(base)

    pred_mean = float(np.mean(preds))
    pred_std = float(np.std(preds))
    confidence = float(np.clip(1.0 - (pred_std / (abs(pred_mean) + 1e-6)), 0.0, 1.0))
    confidence = float(max(confidence, confidence_level - 0.2))
    return pred_mean, pred_std, confidence


def predict_single(
    sample: Dict[str, float],
    model_path: str,
    scaler_path: Optional[str] = None,
    confidence_level: float = 0.95,
    n_bootstraps: int = 100,
) -> Dict:
    model = _load_model(model_path)
    scaler_object = _load_scaler_from_model(model)
    scaler_params = _load_scaler(scaler_path) if scaler_path else None

    X_sample = preprocess_sample(sample, scaler_params=scaler_params, scaler_object=scaler_object)
    prediction, pred_std, confidence = _bootstrap_confidence(
        model, X_sample, n_bootstraps=n_bootstraps, confidence_level=confidence_level
    )

    if scaler_path is None and scaler_object is None:
        logger.warning("Prediction produced without scaler information; results may be unstable.")

    result = {
        "prediction": float(prediction),
        "category": _category_from_mgdl(float(prediction)),
        "confidence": float(confidence),
        "probabilities": None,
        "sample_id": sample.get("id"),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prediction_std": float(pred_std),
    }
    return result


def predict_batch(
    samples: Union[pd.DataFrame, List[Dict[str, float]]],
    model_path: str,
    scaler_path: Optional[str] = None,
    confidence_level: float = 0.95,
    n_bootstraps: int = 100,
) -> List[Dict]:
    if isinstance(samples, pd.DataFrame):
        records = samples.to_dict(orient="records")
    else:
        records = list(samples)

    results = []
    for sample in records:
        try:
            results.append(
                predict_single(
                    sample=sample,
                    model_path=model_path,
                    scaler_path=scaler_path,
                    confidence_level=confidence_level,
                    n_bootstraps=n_bootstraps,
                )
            )
        except Exception as exc:
            results.append({"sample_id": sample.get("id"), "error": str(exc)})
    return results


def export_predictions(predictions: List[Dict], output_path: str, format: str = "json") -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = format.lower()
    if fmt == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(predictions, f, indent=2, ensure_ascii=False)
    elif fmt == "csv":
        pd.DataFrame(predictions).to_csv(path, index=False)
    else:
        raise ValueError("Format output hanya mendukung json atau csv")
    return str(path)


__all__ = [
    "InferenceError",
    "PredictionConfidenceWarning",
    "BLOOD_GLUCOSE_CATEGORIES",
    "CLASS_TO_MGDL",
    "FEATURE_ORDER",
    "preprocess_sample",
    "predict_single",
    "predict_batch",
    "export_predictions",
]
