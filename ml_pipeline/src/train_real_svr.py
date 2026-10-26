"""Latih SVR glukosa darah (mg/dL) dari data/real/generated_data_real.csv (hasil convert_data_log.py).

Beda dengan train_svm.py: validasi PER SESI (leave-one-group-out, grid search di dalamnya juga
GroupKFold), karena preprocess() + KFold membagi per baris dan baris satu sesi hampir identik
(bocor -> metrik palsu bagus). Hasil per-baris ikut dicetak hanya sebagai pembanding kebocoran.
Model disimpan ke src/models/real/ TANPA menimpa best_model.pkl.

    python -m src.train_real_svr [--features ph_value fructosamine_umol_l] [--version v1]
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
from sklearn.model_selection import GridSearchCV, GroupKFold, KFold, LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

ROOT = Path(__file__).resolve().parents[1]
INPUT_COLS = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]   # = FEATURE_ORDER inference.py
GRID = {"svr__C": [1, 10, 100], "svr__gamma": [0.01, 0.1, 0.5, 1.0], "svr__epsilon": [0.1, 0.5, 2.0]}


def search(features: list[str], cv=None) -> GridSearchCV:
    idx = [INPUT_COLS.index(f) for f in features]
    pipe = Pipeline([("prep", ColumnTransformer([("scale", StandardScaler(), idx)], remainder="drop")),
                     ("svr", SVR(kernel="rbf"))])
    return GridSearchCV(pipe, GRID, scoring="neg_mean_absolute_error", cv=cv or GroupKFold(3))


def klass(v):  # ambang ADA, sama dengan train_svm._mgdl_to_class
    return np.digitize(v, [100, 126])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "data" / "real" / "generated_data_real.csv"))
    ap.add_argument("--features", nargs="+", default=["ph_value", "fructosamine_umol_l"], choices=INPUT_COLS)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--out-dir", default=str(ROOT / "src" / "models" / "real"))
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    X, y, g = df[INPUT_COLS].to_numpy(float), df["bg_mgdl_reference"].to_numpy(float), df["session_id"]

    # Evaluasi jujur: tiap sesi diuji oleh model yang tidak pernah melihat sesi itu.
    pred = np.empty_like(y)
    for tr, te in LeaveOneGroupOut().split(X, y, g):
        pred[te] = search(args.features).fit(X[tr], y[tr], groups=g.iloc[tr]).predict(X[te])
    df["pred"] = pred
    print(df.groupby("session_id").agg(label=("bg_mgdl_reference", "first"), pred=("pred", "mean"),
                                       src=("label_source", "first")).round(1).to_string())
    mae = float(np.abs(pred - y).mean())
    rmse = float(np.sqrt(((pred - y) ** 2).mean()))
    acc = float((klass(pred) == klass(y)).mean())
    base = float(np.abs(y - y.mean()).mean())
    print(f"\nPer-sesi (leave-one-session-out): MAE={mae:.1f}  RMSE={rmse:.1f}  akurasi kategori={acc:.0%}"
          f"  | tebak rata-rata: MAE={base:.1f}")

    # Pembanding: pembagian per baris (cara train_svm/preprocess) -> bocor.
    row = cross_val_predict(search(args.features, KFold(3, shuffle=True, random_state=0)), X, y, cv=KFold(5, shuffle=True, random_state=42))
    print(f"Per-baris (bocor, JANGAN dilaporkan): MAE={np.abs(row - y).mean():.1f}")

    final = search(args.features).fit(X, y, groups=g)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"model_svr_units_{args.version}"
    with open(out / f"{stem}.pkl", "wb") as f:
        pickle.dump(final.best_estimator_, f)
    meta = {
        "model_name": "GlicoSaliva SVR (satuan riil, kalibrasi SEMENTARA)",
        "version": args.version,
        "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "features": args.features, "input_order": INPUT_COLS,
        "best_params": final.best_params_,
        "n_rows": len(df), "n_sessions": int(g.nunique()),
        "loso": {"mae": mae, "rmse": rmse, "category_accuracy": acc, "baseline_mae": base},
        "note": "Label 88/148 (2 nilai), kalibrasi sementara, <= 2 orang. Bukan bukti akurasi prediksi glukosa.",
    }
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=2))
    print(f"\nModel -> {out / (stem + '.pkl')}  params={final.best_params_}")


if __name__ == "__main__":
    main()
