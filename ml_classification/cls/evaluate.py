"""Laporan evaluasi leave-one-subject-out: SVC vs baseline, ditulis ke reports/.

Baseline (PRD T-6) memakai protokol LOSO dan fitur yang sama: tebak mayoritas,
regresi logistik, k-NN. SVC layak dipertahankan hanya bila mengalahkan baseline.

    python -m cls.evaluate [--features glucose_saliva ph_value]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier

from cls.train import (CLASSES, INPUT_COLS, MIN_SUBJECTS_PER_CLASS, build_model, load_xyg, loso_predict, scaled,
                       score, subjects_per_class)

ROOT = Path(__file__).resolve().parents[1]


def evaluate(df: pd.DataFrame, features: list[str]) -> dict:
    X, y, groups = load_xyg(df)
    makers = {
        "SVC-rbf": lambda: build_model(features),
        "majority": lambda: scaled(features, DummyClassifier(strategy="most_frequent")),
        "logreg": lambda: scaled(features, LogisticRegression(class_weight="balanced", max_iter=1000)),
        "knn3": lambda: scaled(features, KNeighborsClassifier(n_neighbors=3)),
    }
    spc = subjects_per_class(df)
    return {
        "evaluated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "protocol": "leave-one-subject-out",
        "features": features,
        "n_sessions": len(df),
        "n_subjects": int(df["subject_code"].nunique()),
        "subjects_per_class": spc,
        "claim_allowed": all(n >= MIN_SUBJECTS_PER_CLASS for n in spc.values()),
        "models": {name: score(y, loso_predict(make, X, y, groups)) for name, make in makers.items()},
    }


def to_text(rep: dict) -> str:
    n = f"n_subjek={rep['n_subjects']}, n_sesi={rep['n_sessions']}"
    lines = [f"Evaluasi {rep['protocol']} | fitur={rep['features']} | {n}",
             f"Subjek per kelas: {rep['subjects_per_class']}"]
    if not rep["claim_allowed"]:
        lines.append(f"PERINGATAN: ada kelas dengan subjek < {MIN_SUBJECTS_PER_CLASS}. "
                     "Angka di bawah BUKAN klaim akurasi.")
    lines += ["", f"{'model':<10} {'acc':>6} {'F1mac':>6} " + " ".join(f"rec_{c[:4]:<5}" for c in CLASSES) + "  FN_D->N"]
    for name, s in rep["models"].items():
        rec = " ".join(f"{s['per_class'][c]['recall']:>9.2f}" for c in CLASSES)
        lines.append(f"{name:<10} {s['accuracy']:>6.2f} {s['f1_macro']:>6.2f} {rec}  {s['fn_diabetes_to_normal']:>7}")
    svc = rep["models"]["SVC-rbf"]
    lines += ["", f"Confusion matrix SVC-rbf (baris=label, kolom=prediksi; {CLASSES}; {n}):"]
    lines += [f"  {c:<11} {row}" for c, row in zip(CLASSES, svc["confusion_matrix"])]
    lines.append(f"False negative DIABETES -> NORMAL (SVC): {svc['fn_diabetes_to_normal']}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "data" / "train.csv"))
    ap.add_argument("--features", nargs="+", default=["glucose_saliva", "ph_value"], choices=INPUT_COLS)
    ap.add_argument("--out-dir", default=str(ROOT / "reports"))
    args = ap.parse_args()

    rep = evaluate(pd.read_csv(args.csv), args.features)
    text = to_text(rep)
    print(text)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "loso_report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "loso_report.txt").write_text(text + "\n", encoding="utf-8")
    print(f"\nDisimpan: {out / 'loso_report.json'}, {out / 'loso_report.txt'}")


if __name__ == "__main__":
    main()
