"""Ringkas log serial alat (hardware/DATA/*.csv) menjadi satu baris per sesi.

Nama file: glicovia_<glukosa_darah>_<KELAS>_....csv  (label diambil dari nama file).
Satu baris keluaran = median separuh akhir sesi (lewati transien pembasahan).
Aman dijalankan ulang: menulis ulang seluruh train.csv dari isi folder DATA.

    python -m src.build_real_dataset [--data-dir ../hardware/DATA sampling] [--out data/real/train.csv]
"""

from __future__ import annotations

import argparse
import re
import statistics
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STAMP_RE = re.compile(r"_\d{8}_\d{6}$")
CHANNELS = {"v_fru": "Vfru_V", "v_glu": "Vglu_V", "v_ph": "VpH_V", "v_mid": "Vmid_V", "i_nA": "I_nA"}


def mgdl_to_class(v: int) -> str:
    return "NORMAL" if v < 100 else "PREDIABETES" if v < 126 else "DIABETES"


def parse_name(stem: str) -> tuple[str, int]:
    """(subject_code, mgdl). Lama: glicovia_<mgdl>_<KELAS>[_backup..]_<stamp>.
    Baru: glicovia_<subjek>[_<n>]_<mgdl>[mgdl]_<stamp> (asumsi: angka pertama = subjek, terakhir = mg/dL)."""
    toks = STAMP_RE.sub("", stem).split("_")[1:]
    if len(toks) > 1 and toks[1].isalpha():
        return f"S{int(toks[0]):03d}", int(toks[0])
    nums = [re.sub(r"\D", "", t) for t in toks if re.sub(r"\D", "", t)]
    if len(nums) < 2:
        raise ValueError(f"Nama file tidak dikenali: {stem}")
    return f"P{int(nums[0]):02d}", int(nums[-1])


def summarize(path: Path) -> dict:
    subject, mgdl = parse_name(path.stem)
    df = pd.read_csv(path)
    tail = df.iloc[len(df) // 2:]
    row = {
        "session_id": path.stem,
        # ponytail: subjek diturunkan dari nama file (asumsi, PRD D3 belum dijawab).
        "subject_code": subject,
        "label_mgdl": mgdl,
        "label_class": mgdl_to_class(mgdl),
        "n_rows": len(df),
        "n_ok": int((df["status"] == "OK").sum()),
    }
    for out, col in CHANNELS.items():
        row[out] = statistics.median(tail[col].astype(float))
    row[f"sd_v_fru"] = float(tail["Vfru_V"].astype(float).std())
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", nargs="+", default=[str(ROOT.parent / "hardware" / "DATA"), str(ROOT / "sampling")])
    ap.add_argument("--out", default=str(ROOT / "data" / "real" / "train.csv"))
    args = ap.parse_args()

    # Folder yang sama bisa memuat salinan file; ambil sekali per nama.
    files = sorted({f.name: f for d in args.data_dir for f in Path(d).glob("glicovia_*.csv")}.values(), key=lambda f: f.name)
    if not files:
        raise SystemExit(f"Tidak ada glicovia_*.csv di {args.data_dir}")
    out = pd.DataFrame([summarize(f) for f in files])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(out.round(4).to_string(index=False))
    print(f"\n{len(out)} sesi, {out['subject_code'].nunique()} subjek -> {args.out}")


if __name__ == "__main__":
    main()
