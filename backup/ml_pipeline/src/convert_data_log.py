"""Ubah log serial alat (hardware/data_log/*.csv, volt) jadi dataset berstruktur
data/dummy/generated_data.csv (satuan riil) yang siap dilatih SVM.

Konversi memakai KALIBRASI SEMENTARA (CAL di bawah), BUKAN hasil fit buffer/larutan standar:
    pH            = (V - c) / m          V = m*pH + c   (Nernst 59,16 mV/pH, titik 4,01 -> 85,4 mV)
    glucose_saliva = (I_nA - b) / a      I = (VMID - Vout)/Rf   (kanal jenuh, tidak informatif)
    fructosamine   = (I_nA - b) / a      a,b = dua titik jangkar: 3700 nA -> 220, 9100 nA -> 374
Ganti CAL setelah kalibrasi sebenarnya lulus (PRD §15) lalu jalankan ulang.

Label glukosa darah diambil dari nama file (glicovia_<mgdl>_<KELAS>_...). Bila nama file tidak
memuat angka, dipakai nilai default kelas (kolom label_source = "assumed"). Satu sesi dipecah jadi
beberapa jendela dari separuh akhir; JANGAN validasi per baris, pakai GroupKFold per session_id.

    python -m src.convert_data_log [--data-dir ../hardware/data_log ../hardware/DATA] [--out data/real/generated_data_real.csv]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RF = 100e3  # ohm, feedback TIA
WIN = 20    # sampel per jendela (~5 s pada 4 Hz)

CAL = {
    "ph": {"m": -0.05916, "c": 0.3226},
    "glu": {"a": 1000.0, "b": 0.0},
    "fru": {"a": 35.0, "b": -4000.0},
}
BOUNDS = {"glucose_saliva": (0.1, 10.0), "ph_value": (4.0, 9.0), "fructosamine_umol_l": (150.0, 500.0)}
CLASS_DEFAULT_MGDL = {"NORMAL": 88, "PRE-DIABETES": 112, "DIABETES": 148}

NAME_RE = re.compile(r"^glicovia_(?:(\d+)_)?(NORMAL|PRE-DIABETES|DIABETES)(?:_[A-Za-z0-9]+)*_(\d{8}_\d{6})\.csv$")
COLS = ["id", "glucose_saliva", "ph_value", "fructosamine_umol_l", "bg_class", "bg_mgdl_reference"]


def mgdl_to_class(v: float) -> int:  # sama dengan train_svm._mgdl_to_class
    return 0 if v < 100 else 1 if v < 126 else 2


def clip(x: float, key: str, flags: list[str]) -> float:
    lo, hi = BOUNDS[key]
    if x < lo or x > hi:
        flags.append(f"{key}_clip")
    return min(max(x, lo), hi)


def session_rows(path: Path, m: re.Match) -> list[dict]:
    df = pd.read_csv(path)
    tail = df.iloc[len(df) // 2:]
    if len(df) < 2 * WIN:
        print(f"  lewati (terlalu pendek, {len(df)} baris): {path.name}")
        return []
    mgdl = int(m.group(1)) if m.group(1) else CLASS_DEFAULT_MGDL[m.group(2)]
    rows = []
    for k in range(0, len(tail) - WIN + 1, WIN):
        w = tail.iloc[k:k + WIN]
        v_mid, v_fru, v_glu, v_ph = (float(w[c].median()) for c in ("Vmid_V", "Vfru_V", "Vglu_V", "VpH_V"))
        i_glu = float(w["I_nA"].median())
        i_fru = (v_mid - v_fru) / RF * 1e9
        flags: list[str] = []
        sat = float((w["status"] != "OK").mean())
        if sat > 0.5:
            flags.append("jenuh")
        rows.append({
            "glucose_saliva": clip((i_glu - CAL["glu"]["b"]) / CAL["glu"]["a"], "glucose_saliva", flags),
            "ph_value": clip((v_ph - CAL["ph"]["c"]) / CAL["ph"]["m"], "ph_value", flags),
            "fructosamine_umol_l": clip((i_fru - CAL["fru"]["b"]) / CAL["fru"]["a"], "fructosamine_umol_l", flags),
            "bg_class": mgdl_to_class(mgdl),
            "bg_mgdl_reference": mgdl,
            "session_id": path.stem,
            "subject_code": f"S{mgdl:03d}",
            "label_source": "filename" if m.group(1) else "assumed",
            "v_fru": v_fru, "v_glu": v_glu, "v_ph": v_ph, "v_mid": v_mid,
            "i_glu_nA": i_glu, "i_fru_nA": i_fru,
            "sat_frac": sat,
            "flags": ";".join(flags),
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", nargs="+", default=[str(ROOT.parent / "hardware" / "data_log"),
                                                     str(ROOT.parent / "hardware" / "DATA")])
    ap.add_argument("--out", default=str(ROOT / "data" / "real" / "generated_data_real.csv"))
    args = ap.parse_args()

    # Salinan sesi sama bernama beda (mis. glicovia_DIABETES_<ts>.csv vs glicovia_148_DIABETES_<ts>.csv):
    # satu per timestamp, utamakan yang namanya memuat angka glukosa.
    picked: dict[str, tuple[Path, re.Match]] = {}
    for p in sorted(f for d in args.data_dir for f in Path(d).glob("glicovia_*.csv")):
        m = NAME_RE.match(p.name)
        if m and (m.group(3) not in picked or (m.group(1) and not picked[m.group(3)][1].group(1))):
            picked[m.group(3)] = (p, m)
    if not picked:
        raise SystemExit(f"Tidak ada sesi berlabel di {args.data_dir}")

    rows: list[dict] = []
    for p, m in sorted(picked.values()):
        rows += session_rows(p, m)
    out = pd.DataFrame(rows)
    out.insert(0, "id", range(len(out)))
    out = out[COLS + [c for c in out.columns if c not in COLS]]

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.round(4).to_csv(args.out, index=False)
    Path(args.out).with_suffix(".meta.json").write_text(json.dumps(
        {"calibration": CAL, "rf_ohm": RF, "window": WIN, "bounds": BOUNDS, "status": "PROVISIONAL"}, indent=2))

    g = out.groupby("session_id")
    print(g.agg(n=("id", "size"), mgdl=("bg_mgdl_reference", "first"), src=("label_source", "first"),
                glu=("glucose_saliva", "median"), ph=("ph_value", "median"),
                fru=("fructosamine_umol_l", "median"), sat=("sat_frac", "mean")).round(2).to_string())
    print(f"\n{len(out)} baris, {out['session_id'].nunique()} sesi -> {args.out}")


if __name__ == "__main__":
    main()
