"""Latih SVC 3 kelas (NORMAL / PREDIABETES / DIABETES) dari data/train.csv.

Validasi leave-one-subject-out: subjek uji tidak pernah ada di data latih.
Model disimpan ke models/model_cls_<versi>.pkl/.json dan tidak menimpa versi lama.
Bila subjek per kelas < 3 (PRD T-4), metadata bertanda model_not_ready=true.

    python -m cls.train [--features glucose_saliva ph_value] [--C 1.0] [--gamma scale] [--version c2]

Fitur = satuan riil hasil kalibrasi sementara (cls/calibration.py), dihitung dari kolom volt/arus train.csv.
"""

from __future__ import annotations

import argparse
import json
import pickle
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from cls.calibration import CAL, with_calibrated

# ponytail: SVC(probability=True) deprecated sejak sklearn 1.9 (hilang di 1.11).
# Migrasi ke CalibratedClassifierCV(SVC(), ensemble=False) bila venv naik ke 1.11.
warnings.filterwarnings("ignore", message="The `probability` parameter", category=FutureWarning)

ROOT = Path(__file__).resolve().parents[1]
INPUT_COLS = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]   # mg/dL, pH, umol/L (terkalibrasi)
CLASSES = ["NORMAL", "PREDIABETES", "DIABETES"]
MIN_SUBJECTS_PER_CLASS = 3


def scaled(features: list[str], clf) -> Pipeline:
    """Pipeline yang menerima 3 kolom INPUT_COLS lalu memakai & menskala `features` saja."""
    idx = [INPUT_COLS.index(f) for f in features]
    prep = ColumnTransformer([("scale", StandardScaler(), idx)], remainder="drop")
    return Pipeline([("prep", prep), ("clf", clf)])


def build_model(features: list[str], C: float = 1.0, gamma: str | float = "scale") -> Pipeline:
    clf = SVC(kernel="rbf", C=C, gamma=gamma, class_weight="balanced", probability=True, random_state=0)
    return scaled(features, clf)


def load_xyg(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    df = with_calibrated(df)
    X = df[INPUT_COLS].to_numpy(float)
    y = df["label_class"].map({c: i for i, c in enumerate(CLASSES)}).to_numpy(int)
    return X, y, df["subject_code"].to_numpy()


def loso_predict(make: Callable[[], Pipeline], X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> np.ndarray:
    """Prediksi leave-one-subject-out. -1 = fold dilewati (data latih < 2 kelas)."""
    pred = np.full(len(y), -1)
    for tr, te in LeaveOneGroupOut().split(X, y, groups):
        if len(set(y[tr])) < 2:
            continue
        pred[te] = make().fit(X[tr], y[tr]).predict(X[te])
    return pred


def score(y: np.ndarray, pred: np.ndarray) -> dict:
    m = pred >= 0
    labels = list(range(len(CLASSES)))
    cm = confusion_matrix(y[m], pred[m], labels=labels)
    p, r, f, s = precision_recall_fscore_support(y[m], pred[m], labels=labels, zero_division=0)
    return {
        "n_eval_sessions": int(m.sum()),
        "accuracy": float((pred[m] == y[m]).mean()) if m.any() else 0.0,
        "f1_macro": float(f1_score(y[m], pred[m], labels=labels, average="macro", zero_division=0)),
        "per_class": {c: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]), "support": int(s[i])}
                      for i, c in enumerate(CLASSES)},
        "confusion_matrix": cm.tolist(),
        "fn_diabetes_to_normal": int(cm[2, 0]),
    }


def subjects_per_class(df: pd.DataFrame) -> dict:
    return {c: int(df.loc[df["label_class"] == c, "subject_code"].nunique()) for c in CLASSES}


def train(df: pd.DataFrame, features: list[str], C: float = 1.0, gamma: str | float = "scale") -> tuple[Pipeline, dict]:
    """Latih model final + metadata (termasuk metrik LOSO). Tolak bila < 2 kelas."""
    X, y, groups = load_xyg(df)
    if len(set(y)) < 2:
        raise ValueError("Butuh >= 2 kelas label.")
    spc = subjects_per_class(df)
    ready = all(n >= MIN_SUBJECTS_PER_CLASS for n in spc.values())
    loso = score(y, loso_predict(lambda: build_model(features, C, gamma), X, y, groups))
    model = build_model(features, C, gamma).fit(X, y)
    meta = {
        "model_name": "GlicoSaliva SVC 3 kelas",
        "model_type": "SVC-rbf",
        "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "features": features,
        "input_order": INPUT_COLS,
        "calibration": CAL,
        "classes": CLASSES,
        "params": {"C": C, "gamma": gamma, "class_weight": "balanced"},
        "n_sessions": len(df),
        "n_subjects": int(len(set(groups))),
        "subjects_per_class": spc,
        "batches": sorted(df["batch"].astype(str).unique().tolist()) if "batch" in df else [],
        "loso": loso,
        "model_not_ready": not ready,
        "caveat": "" if ready else (
            f"Subjek per kelas < {MIN_SUBJECTS_PER_CLASS} ({spc}). Kelas dengan 1 subjek tidak pernah ada di data "
            "latih saat subjeknya diuji. Metrik LOSO bukan klaim akurasi."),
    }
    return model, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "data" / "train.csv"))
    ap.add_argument("--features", nargs="+", default=["glucose_saliva", "ph_value"], choices=INPUT_COLS)
    ap.add_argument("--C", type=float, default=1.0)
    ap.add_argument("--gamma", default="scale")
    ap.add_argument("--version", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    ap.add_argument("--out-dir", default=str(ROOT / "models"))
    args = ap.parse_args()
    gamma = args.gamma if args.gamma == "scale" else float(args.gamma)

    out = Path(args.out_dir)
    stem = f"model_cls_{args.version}"
    if (out / f"{stem}.pkl").exists():
        raise SystemExit(f"{stem}.pkl sudah ada; pakai --version lain (versi lama tidak ditimpa).")

    df = pd.read_csv(args.csv)
    try:
        model, meta = train(df, args.features, args.C, gamma)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    meta = {"version": args.version, **meta, "train_csv": Path(args.csv).name}

    loso = meta["loso"]
    print(f"Sesi={meta['n_sessions']} subjek={meta['n_subjects']} subjek/kelas={meta['subjects_per_class']} fitur={args.features}")
    print(f"LOSO: F1 macro={loso['f1_macro']:.3f} accuracy={loso['accuracy']:.3f} (n_sesi_uji={loso['n_eval_sessions']}), "
          f"FN DIABETES->NORMAL={loso['fn_diabetes_to_normal']}")
    if meta["model_not_ready"]:
        print(f"PERINGATAN: model_not_ready. {meta['caveat']}")

    out.mkdir(parents=True, exist_ok=True)
    with open(out / f"{stem}.pkl", "wb") as f:
        pickle.dump(model, f)
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Disimpan: {out / (stem + '.pkl')}")


if __name__ == "__main__":
    main()
