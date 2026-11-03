"""FastAPI klasifikasi Glicovia (kontrak PRD §8).

Model dipilih lewat env GLICO_CLS_MODEL; bila kosong, dipakai models/model_cls_*.pkl terbaru.

    uvicorn cls.api:app --port 8000
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from cls.inference import DEFAULT_THRESHOLD, load, predict_class

ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(title="Glicovia Classification API", version="1.0.0")


class PredictionInput(BaseModel):
    # Rentang tidak divalidasi di sini: di luar rentang dijawab status "out_of_range", bukan 422.
    glucose_saliva: float = Field(..., description="Glukosa saliva (mg/dL, kalibrasi sementara)")
    ph_value: float = Field(..., description="pH saliva (kalibrasi sementara)")
    fructosamine_umol_l: float = Field(..., description="Fruktosamin (umol/L, kalibrasi sementara; belum tervalidasi)")
    id: Optional[str] = Field(default=None, description="Optional sample identifier")

    @field_validator("id")
    @classmethod
    def sanitize_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return re.sub(r"[^A-Za-z0-9_-]", "", str(value)) or None


class BatchPredictionInput(BaseModel):
    samples: List[PredictionInput]


def model_path() -> str:
    env = os.environ.get("GLICO_CLS_MODEL")
    if env:
        return env
    found = sorted((ROOT / "models").glob("model_cls_*.pkl"), key=lambda p: p.stat().st_mtime)
    if not found:
        raise HTTPException(status_code=503, detail="Belum ada model; jalankan python -m cls.train")
    return str(found[-1])


def _respond(sample: PredictionInput) -> Dict[str, Any]:
    res = predict_class(sample.model_dump(), model_path(), threshold=DEFAULT_THRESHOLD)
    # Field lama untuk parser firmware: kelas bila ada, selain itu status (UNCERTAIN / MODEL_NOT_READY / OUT_OF_RANGE).
    res["clinical_category"] = res["class_name"] or res["status"].upper()
    res["confidence_score"] = res["confidence"] if res["confidence"] is not None else 0.0
    res["sample_id"] = sample.id
    return res


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/model-info")
def model_info() -> Dict[str, Any]:
    path = model_path()
    _, meta = load(path)
    return {"model_path": Path(path).name, "threshold": DEFAULT_THRESHOLD, **meta}


@app.post("/predict")
def predict_endpoint(sample: PredictionInput) -> Dict[str, Any]:
    try:
        return _respond(sample)
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict-batch")
def predict_batch_endpoint(payload: BatchPredictionInput) -> Dict[str, Any]:
    try:
        results = [_respond(s) for s in payload.samples]
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"predictions": results, "count": len(results)}
