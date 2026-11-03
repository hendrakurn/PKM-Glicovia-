"""Buat model SINTETIS hanya untuk menguji jalur integrasi (alat -> MQTT -> backend -> OLED/web).

Data dibangkitkan acak (4 subjek per kelas) supaya model_not_ready=false. Hasilnya BUKAN bukti akurasi
dan sengaja ditulis ke models_test/, bukan models/.

    python scripts/make_test_model.py
    GLICO_CLS_MODEL=models_test/model_cls_test.pkl uvicorn cls.api:app --port 8002
"""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cls.train import CLASSES, train  # noqa: E402

# Pusat (glucose_saliva mg/dL, ph_value, fructosamine_umol_l) per kelas, satuan terkalibrasi.
# Hanya agar kelas terpisah; tidak mewakili data nyata.
CENTERS = {"NORMAL": (1.5, 7.0, 250.0), "PREDIABETES": (4.5, 6.2, 300.0), "DIABETES": (8.0, 5.4, 380.0)}
SPREAD = (0.5, 0.25, 15.0)


def synthetic() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for cls_name, c in CENTERS.items():
        for s in range(4):
            for _ in range(3):
                glu, ph, fru = rng.normal(c, SPREAD)
                rows.append({"subject_code": f"{cls_name[:1]}{s}", "label_class": cls_name,
                             "glucose_saliva": glu, "ph_value": ph, "fructosamine_umol_l": fru, "batch": "synthetic"})
    return pd.DataFrame(rows)


def main() -> None:
    model, meta = train(synthetic(), ["glucose_saliva", "ph_value"])
    meta.update(version="test-synthetic", synthetic=True,
                caveat="Data sintetis untuk uji integrasi. BUKAN klaim akurasi.")
    out = ROOT / "models_test"
    out.mkdir(exist_ok=True)
    with open(out / "model_cls_test.pkl", "wb") as f:
        pickle.dump(model, f)
    (out / "model_cls_test.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"model_not_ready={meta['model_not_ready']} -> {out / 'model_cls_test.pkl'}")


if __name__ == "__main__":
    main()
