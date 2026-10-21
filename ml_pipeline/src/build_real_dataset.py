"""Ringkas log serial alat (hardware/DATA/*.csv) menjadi satu baris per sesi.

Nama file: glicovia_<glukosa_darah>_<KELAS>_....csv  (label diambil dari nama file).
Satu baris keluaran = median separuh akhir sesi (lewati transien pembasahan).
Aman dijalankan ulang: menulis ulang seluruh train.csv dari isi folder DATA.

    python -m src.build_real_dataset [--data-dir ../hardware/DATA] [--out data/real/train.csv]
"""

from __future__ import annotations

import argparse
import re
import statistics
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^glicovia_(\d+)_([A-Za-z]+)_")
CHANNELS = {"v_fru": "Vfru_V", "v_glu": "Vglu_V", "v_ph": "VpH_V", "v_mid": "Vmid_V", "i_nA": "I_nA"}


def summarize(path: Path) -> dict:
    m = NAME_RE.match(path.name)
    if not m:
        raise ValueError(f"Nama file tidak dikenali (butuh glicovia_<mgdl>_<KELAS>_...): {path.name}")
    df = pd.read_csv(path)
    tail = df.iloc[len(df) // 2:]
    row = {
        "session_id": path.stem,
        # ponytail: 1 orang per label (asumsi, PRD D3 belum dijawab). Ganti kolom ini bila ada subjek lain.
        "subject_code": f"S{int(m.group(1)):03d}",
        "label_mgdl": int(m.group(1)),
        "label_class": m.group(2).upper(),
        "n_rows": len(df),
        "n_ok": int((df["status"] == "OK").sum()),
    }
    for out, col in CHANNELS.items():
        row[out] = statistics.median(tail[col].astype(float))
    row[f"sd_v_fru"] = float(tail["Vfru_V"].astype(float).std())
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT.parent / "hardware" / "DATA"))
    ap.add_argument("--out", default=str(ROOT / "data" / "real" / "train.csv"))
    args = ap.parse_args()

    files = sorted(Path(args.data_dir).glob("glicovia_*.csv"))
    if not files:
        raise SystemExit(f"Tidak ada glicovia_*.csv di {args.data_dir}")
    out = pd.DataFrame([summarize(f) for f in files])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(out.round(4).to_string(index=False))
    print(f"\n{len(out)} sesi, {out['subject_code'].nunique()} subjek -> {args.out}")


if __name__ == "__main__":
    main()
