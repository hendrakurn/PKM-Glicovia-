"""Prediksi kelas glukosa darah dari satu sampel saliva (kontrak PRD §8).

Keluaran berupa kelas + probabilitas, TIDAK pernah angka mg/dL.
Status: ok | uncertain | out_of_range | model_not_ready.
"""

from __future__ import annotations

import json
import pickle
from functools import lru_cache
from pathlib import Path

import numpy as np

from cls.train import CLASSES

FEATURE_ORDER = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]   # mg/dL, pH, umol/L (terkalibrasi)
# Batas kewajaran saja (alat sudah memotong ke rentang kalibrasi, lihat cls/calibration.py).
RANGES = {"glucose_saliva": (0.0, 1000.0), "ph_value": (0.0, 14.0), "fructosamine_umol_l": (0.0, 1000.0)}
DEFAULT_THRESHOLD = 0.60


@lru_cache(maxsize=4)
def load(model_path: str) -> tuple[object, dict]:
    path = Path(model_path)
    with open(path, "rb") as f:
        model = pickle.load(f)
    meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    return model, meta


def predict_class(sample: dict, model_path: str, threshold: float = DEFAULT_THRESHOLD) -> dict:
    missing = [f for f in FEATURE_ORDER if f not in sample]
    if missing:
        raise ValueError(f"Fitur hilang: {missing}. Wajib: {FEATURE_ORDER}")
    model, meta = load(str(model_path))
    result = {
        "class_index": None,
        "class_name": None,
        "probabilities": None,
        "confidence": None,
        "model_type": meta.get("model_type", "SVC-rbf"),
        "model_version": meta.get("version"),
        "status": "ok",
    }

    x = [float(sample[f]) for f in FEATURE_ORDER]
    if any(not (RANGES[f][0] <= v <= RANGES[f][1]) for f, v in zip(FEATURE_ORDER, x)):
        result["status"] = "out_of_range"
        return result
    if meta.get("model_not_ready", True):
        result["status"] = "model_not_ready"
        return result

    proba = model.predict_proba(np.array([x]))[0]
    # Model bisa dilatih tanpa salah satu kelas; kelas yang tak dikenal diberi probabilitas 0.
    probs = {c: 0.0 for c in CLASSES}
    for idx, p in zip(model.classes_, proba):
        probs[CLASSES[int(idx)]] = round(float(p), 4)
    best = max(probs, key=probs.get)
    result.update(probabilities=probs, confidence=probs[best])
    if probs[best] < threshold:
        result.update(class_name="UNCERTAIN", status="uncertain")
    else:
        result.update(class_index=CLASSES.index(best), class_name=best)
    return result


__all__ = ["FEATURE_ORDER", "RANGES", "DEFAULT_THRESHOLD", "load", "predict_class"]
