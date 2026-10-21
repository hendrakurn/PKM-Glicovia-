"""FastAPI connector for the GlicoSaliva ML pipeline."""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.inference import predict_batch, predict_single

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="GlicoSaliva ML API", version="2.0.0")

MODEL_PATH = os.environ.get("GLICO_MODEL_PATH") or str(Path(__file__).resolve().parent / "models" / "best_model.pkl")
# GLICO_MODEL_PATH menunjuk ke model data nyata (train_real.py): masukan berupa sinyal alat
# (volt bila belum terkalibrasi), jadi batas dilonggarkan menjadi batas kewajaran saja.
# Pipeline model itu menskala sendiri; scaler dummy di bawah harus mati, kalau tidak masukan
# terskala dua kali ("" = tanpa scaler eksternal, lihat predict_single).
USING_REAL_MODEL = bool(os.environ.get("GLICO_MODEL_PATH"))
SCALER_PATH = "" if USING_REAL_MODEL else str(Path(__file__).resolve().parent / "data" / "processed" / "scaler_params.json")

required_fields = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]
features = required_fields.copy()
ranges = (
    {"glucose_saliva": (0.0, 1000.0), "ph_value": (0.0, 14.0), "fructosamine_umol_l": (0.0, 1000.0)}
    if USING_REAL_MODEL
    else {"glucose_saliva": (0.1, 10.0), "ph_value": (4.0, 9.0), "fructosamine_umol_l": (150.0, 500.0)}
)

MODEL_INFO = {
    "model_name": "GlicoSaliva SVR",
    "version": "2.0.0",
    "features": features,
    "target": "bg_mgdl_reference",
    "classes": ["Normal", "Pre-Diabetes", "Diabetes"],
}
if USING_REAL_MODEL:
    _meta_path = Path(MODEL_PATH).with_suffix(".json")
    if _meta_path.exists():
        _meta = json.loads(_meta_path.read_text(encoding="utf-8"))
        MODEL_INFO["model_name"] = _meta["model_name"]
        MODEL_INFO["version"] = f"real-{_meta['version']}"


class PredictionInput(BaseModel):
    glucose_saliva: float = Field(..., ge=ranges["glucose_saliva"][0], le=ranges["glucose_saliva"][1], description="Saliva glucose concentration")
    ph_value: float = Field(..., ge=ranges["ph_value"][0], le=ranges["ph_value"][1], description="Saliva pH value")
    fructosamine_umol_l: float = Field(..., ge=ranges["fructosamine_umol_l"][0], le=ranges["fructosamine_umol_l"][1], description="Fructosamine concentration (umol/L)")
    id: Optional[str] = Field(default=None, description="Optional sample identifier")

    @field_validator("id")
    @classmethod
    def sanitize_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        clean = re.sub(r"[^A-Za-z0-9_-]", "", str(value))
        return clean or None


class BatchPredictionInput(BaseModel):
    samples: List[PredictionInput]


class TrainRequest(BaseModel):
    raw_csv_path: Optional[str] = None
    output_dir: Optional[str] = None


def sanitize_input(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", str(value))


def validate_prediction_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        validated = PredictionInput(**payload).model_dump()
    except Exception as exc:
        raise ValueError(str(exc)) from exc
    return validated


@lru_cache(maxsize=1)
def _get_cached_model_paths() -> tuple[str, str]:
    return MODEL_PATH, SCALER_PATH


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/model-info")
def model_info() -> Dict[str, Any]:
    return MODEL_INFO


@app.post("/predict")
def predict_endpoint(sample: PredictionInput) -> Dict[str, Any]:
    try:
        prediction = predict_single(
            sample=sample.model_dump(),
            model_path=MODEL_PATH,
            scaler_path=SCALER_PATH,
        )
        return prediction
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict-batch")
def predict_batch_endpoint(payload: BatchPredictionInput) -> Dict[str, Any]:
    try:
        results = predict_batch(
            samples=[s.model_dump() for s in payload.samples],
            model_path=MODEL_PATH,
            scaler_path=SCALER_PATH,
        )
        return {"predictions": results, "count": len(results)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/train")
def train_endpoint(payload: TrainRequest) -> Dict[str, Any]:
    """Basic training hook for manual retraining flows.

    The endpoint returns an accepted response instead of spawning a background
    job so that the test suite stays deterministic.
    """
    return {
        "status": "accepted",
        "raw_csv_path": payload.raw_csv_path,
        "output_dir": payload.output_dir,
        "message": "Use the pipeline CLI or run_pipeline() for full retraining.",
    }


@app.get("/model-paths")
def model_paths() -> Dict[str, str]:
    return {"model_path": MODEL_PATH, "scaler_path": SCALER_PATH}


__all__ = [
    "app",
    "PredictionInput",
    "BatchPredictionInput",
    "TrainRequest",
    "required_fields",
    "features",
    "ranges",
    "sanitize_input",
    "validate_prediction_input",
    "MODEL_INFO",
]
