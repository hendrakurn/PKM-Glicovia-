"""Latih klasifikasi glukosa darah (label dari glukometer) dari data alat nyata.

Membaca data/real/train.csv (hasil build_real_dataset.py), validasi leave-one-session-out,
lalu menyimpan model baru ke src/models/real/ TANPA menimpa best_model.pkl.

Model menerima 3 kolom sesuai FEATURE_ORDER inference.py
[glucose_saliva, ph_value, fructosamine_umol_l] = [v_glu, v_ph, v_fru], lalu memilih
kolom yang dipakai (--features) di dalam pipeline. Prediksi = label mg/dL langsung
(88 atau 148), jadi _prediction_value_to_mgdl tidak memetakan ulang.

    python -m src.train_real [--features v_fru] [--version v1]
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
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[1]
INPUT_COLS = ["v_glu", "v_ph", "v_fru"]   # urutan = FEATURE_ORDER di inference.py


def build_model(features: list[str]) -> Pipeline:
    idx = [INPUT_COLS.index(f) for f in features]
    prep = ColumnTransformer([("scale", StandardScaler(), idx)], remainder="drop")
    return Pipeline([("prep", prep), ("clf", SVC(kernel="rbf", C=1.0, gamma="scale"))])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "data" / "real" / "train.csv"))
    ap.add_argument("--features", nargs="+", default=["v_fru"], choices=INPUT_COLS)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--out-dir", default=str(ROOT / "src" / "models" / "real"))
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    X = df[INPUT_COLS].to_numpy(float)
    y = df["label_mgdl"].to_numpy(int)
    if len(set(y)) < 2:
        raise SystemExit("Butuh >= 2 kelas label.")

    # Leave-one-session-out. Catatan: sesi lain dari orang yang sama tetap ada di data latih,
    # jadi ini TIDAK mengukur generalisasi ke orang baru (hanya 2 orang tersedia).
    hits = []
    for i in range(len(df)):
        train = np.arange(len(df)) != i
        if len(set(y[train])) < 2:
            continue
        pred = build_model(args.features).fit(X[train], y[train]).predict(X[i:i + 1])[0]
        hits.append(pred == y[i])
        print(f"  uji {df['session_id'][i]:<48} label={y[i]:>3} prediksi={pred:>3} {'OK' if hits[-1] else 'SALAH'}")
    acc = float(np.mean(hits))
    print(f"\nLeave-one-session-out: {sum(hits)}/{len(hits)} benar ({acc:.0%}), fitur={args.features}")

    model = build_model(args.features).fit(X, y)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"model_real_{args.version}"
    with open(out / f"{stem}.pkl", "wb") as f:
        pickle.dump(model, f)
    meta = {
        "model_name": "GlicoSaliva SVC (data nyata)",
        "version": args.version,
        "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "features": args.features,
        "input_order": INPUT_COLS,
        "classes_mgdl": sorted(set(int(v) for v in y)),
        "n_sessions": len(df),
        "n_subjects": int(df["subject_code"].nunique()),
        "loso_accuracy": acc,
        "caveat": "Tiap kelas dari 1 orang; LOSO tidak menguji orang baru. Bukan bukti akurasi prediksi.",
        "train_csv": str(Path(args.csv).name),
    }
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"Disimpan: {out / (stem + '.pkl')}")


if __name__ == "__main__":
    main()
