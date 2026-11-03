"""Ringkas log serial alat (glicovia_*.csv) menjadi satu baris per sesi.

Nama file yang dikenali:
  lama  glicovia_<mgdl>_<KELAS>[_backup..]_<YYYYMMDD>_<HHMMSS>.csv  -> subjek S<mgdl>
  baru  glicovia_<subjek>[_<n>]_<mgdl>[mgdl]_<YYYYMMDD>_<HHMMSS>.csv -> subjek P<subjek>
Satu baris keluaran = median separuh akhir sesi (lewati transien pembasahan).
Kelas diturunkan dari mg/dL, bukan dari nama kelas di file.

    python -m cls.dataset [--data-dir ../hardware/DATA ../ml_pipeline/sampling] [--min-ok 0]
"""

from __future__ import annotations

import argparse
import re
import statistics
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
STAMP_RE = re.compile(r"_(\d{8})_\d{6}$")
CHANNELS = {"v_fru": "Vfru_V", "v_glu": "Vglu_V", "v_ph": "VpH_V", "v_mid": "Vmid_V", "i_nA": "I_nA"}


def mgdl_to_class(v: int) -> str:
    return "NORMAL" if v < 100 else "PREDIABETES" if v < 126 else "DIABETES"


def parse_name(stem: str) -> tuple[str, int, str]:
    """(subject_code, mgdl, batch). ASUMSI format baru: angka pertama = subjek, terakhir = mg/dL."""
    m = STAMP_RE.search(stem)
    if not stem.startswith("glicovia_") or not m:
        raise ValueError(f"Nama file tidak dikenali: {stem}")
    toks = stem[: m.start()].split("_")[1:]
    if len(toks) > 1 and toks[0].isdigit() and toks[1].isalpha():
        return f"S{int(toks[0]):03d}", int(toks[0]), m.group(1)
    nums = [re.sub(r"\D", "", t) for t in toks]
    nums = [n for n in nums if n]
    if len(nums) < 2:
        raise ValueError(f"Nama file tidak dikenali: {stem}")
    return f"P{int(nums[0]):02d}", int(nums[-1]), m.group(1)


def summarize(path: Path) -> dict:
    subject, mgdl, batch = parse_name(path.stem)
    df = pd.read_csv(path)
    tail = df.iloc[len(df) // 2:]
    row = {
        "session_id": path.stem,
        "subject_code": subject,
        "label_mgdl": mgdl,
        "label_class": mgdl_to_class(mgdl),
        "n_rows": len(df),
        "n_ok": int((df["status"] == "OK").sum()),
    }
    for out, col in CHANNELS.items():
        row[out] = statistics.median(tail[col].astype(float))
    row["sd_v_fru"] = float(tail["Vfru_V"].astype(float).std())
    row["batch"] = batch
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", nargs="+", default=[str(REPO / "hardware" / "DATA"), str(REPO / "ml_pipeline" / "sampling")])
    ap.add_argument("--out", default=str(ROOT / "data" / "train.csv"))
    ap.add_argument("--min-ok", type=int, default=0, help="buang sesi dengan baris status OK lebih sedikit dari ini")
    args = ap.parse_args()

    # Folder berbeda bisa memuat salinan file yang sama; ambil sekali per nama.
    files = sorted({f.name: f for d in args.data_dir for f in Path(d).glob("glicovia_*.csv")}.values(), key=lambda f: f.name)
    if not files:
        raise SystemExit(f"Tidak ada glicovia_*.csv di {args.data_dir}")
    out = pd.DataFrame([summarize(f) for f in files])

    dropped = out[out["n_ok"] < args.min_ok]
    for _, r in dropped.iterrows():
        print(f"  buang {r['session_id']}: n_ok={r['n_ok']} < --min-ok {args.min_ok}")
    out = out[out["n_ok"] >= args.min_ok].reset_index(drop=True)
    if out.empty:
        raise SystemExit("Semua sesi terbuang oleh --min-ok.")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(out.drop(columns=["session_id"]).round(4).to_string(index=False))
    per_class = out.groupby("label_class")["subject_code"].nunique().to_dict()
    print(f"\n{len(out)} sesi, {out['subject_code'].nunique()} subjek, subjek/kelas={per_class} -> {args.out}")


if __name__ == "__main__":
    main()
