"""Latih SVC 3 kelas (NORMAL / PREDIABETES / DIABETES) dari data/real/train.csv.

Validasi leave-one-subject-out: subjek uji tidak pernah ada di data latih.
Model disimpan ke src/models/real/ TANPA menimpa model lama. Bila subjek per kelas < 3
(PRD T-4), metadata ditandai model_not_ready=true dan angka metrik hanya indikatif.

    python -m src.train_classifier [--features v_glu v_ph] [--version c1]
"""

from __future__ import annotations

import argparse
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[1]
INPUT_COLS = ["v_glu", "v_ph", "v_fru"]   # urutan = FEATURE_ORDER di inference.py
CLASSES = ["NORMAL", "PREDIABETES", "DIABETES"]
MIN_SUBJECTS_PER_CLASS = 3


def build_model(features: list[str], C: float, gamma: str | float) -> Pipeline:
    idx = [INPUT_COLS.index(f) for f in features]
    prep = ColumnTransformer([("scale", StandardScaler(), idx)], remainder="drop")
    clf = SVC(kernel="rbf", C=C, gamma=gamma, class_weight="balanced", probability=True, random_state=0)
    return Pipeline([("prep", prep), ("clf", clf)])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "data" / "real" / "train.csv"))
    ap.add_argument("--features", nargs="+", default=["v_glu", "v_ph"], choices=INPUT_COLS)
    ap.add_argument("--C", type=float, default=1.0)
    ap.add_argument("--gamma", default="scale")
    ap.add_argument("--version", default="c1")
    ap.add_argument("--out-dir", default=str(ROOT / "src" / "models" / "real"))
    args = ap.parse_args()
    gamma = args.gamma if args.gamma == "scale" else float(args.gamma)

    df = pd.read_csv(args.csv)
    X = df[INPUT_COLS].to_numpy(float)
    y = df["label_class"].map({c: i for i, c in enumerate(CLASSES)}).to_numpy(int)
    groups = df["subject_code"].to_numpy()
    if len(set(y)) < 2:
        raise SystemExit("Butuh >= 2 kelas label.")

    subj_per_class = {c: int(df.loc[df["label_class"] == c, "subject_code"].nunique()) for c in CLASSES}
    ready = all(n >= MIN_SUBJECTS_PER_CLASS for n in subj_per_class.values())
    print(f"Sesi={len(df)} subjek={len(set(groups))} subjek/kelas={subj_per_class} fitur={args.features}")
    if not ready:
        print("PERINGATAN: subjek per kelas < 3 -> model_not_ready, metrik di bawah BUKAN klaim akurasi.\n")

    pred = np.full(len(df), -1)
    for tr, te in LeaveOneGroupOut().split(X, y, groups):
        if len(set(y[tr])) < 2:
            continue
        pred[te] = build_model(args.features, args.C, gamma).fit(X[tr], y[tr]).predict(X[te])
    for i in range(len(df)):
        got = CLASSES[pred[i]] if pred[i] >= 0 else "-"
        print(f"  uji {df['subject_code'][i]} {df['session_id'][i]:<48} label={df['label_class'][i]:<11} prediksi={got}")

    m = pred >= 0
    labels = list(range(len(CLASSES)))
    cm = confusion_matrix(y[m], pred[m], labels=labels)
    f1 = float(f1_score(y[m], pred[m], labels=labels, average="macro", zero_division=0))
    print(f"\nConfusion matrix (baris=label, kolom=prediksi; {CLASSES}):\n{cm}")
    print(classification_report(y[m], pred[m], labels=labels, target_names=CLASSES, zero_division=0))
    print(f"F1 macro={f1:.3f}  accuracy={float((pred[m] == y[m]).mean()):.3f}  (n_sesi_uji={int(m.sum())})")
    miss = int(cm[2, 0])
    print(f"False negative DIABETES -> NORMAL: {miss}")

    model = build_model(args.features, args.C, gamma).fit(X, y)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"model_cls_{args.version}"
    with open(out / f"{stem}.pkl", "wb") as f:
        pickle.dump(model, f)
    meta = {
        "model_name": "GlicoSaliva SVC 3 kelas",
        "model_type": "SVC-rbf",
        "version": args.version,
        "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "features": args.features,
        "input_order": INPUT_COLS,
        "classes": CLASSES,
        "params": {"C": args.C, "gamma": args.gamma, "class_weight": "balanced"},
        "n_sessions": len(df),
        "n_subjects": int(len(set(groups))),
        "subjects_per_class": subj_per_class,
        "loso": {"f1_macro": f1, "confusion_matrix": cm.tolist(), "n_eval_sessions": int(m.sum()),
                 "fn_diabetes_to_normal": miss},
        "model_not_ready": not ready,
        "caveat": "Subjek per kelas < 3; PREDIABETES hanya 1 subjek sehingga tidak pernah ada di latih saat diuji. "
                  "Bukan bukti akurasi." if not ready else "",
        "train_csv": Path(args.csv).name,
    }
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"Disimpan: {out / (stem + '.pkl')}")


if __name__ == "__main__":
    main()
