"""CONTOH data optimal (SIMULASI, bukan hasil ukur) untuk tiap sesi berlabel di hardware/data_log.

Per sesi asli: waktu, t_detik, jumlah baris, dan Vmid diambil dari file asli. Kanal Vfru, Vglu (Vout TIA),
VpH, raw, dan I_nA dibuat ulang supaya sesuai target satuan riil kelasnya, lalu dihitung balik ke satuan
riil dengan rumus CALC di hardware/f_endtoend/main.cpp (phFromV, fruFromV, gluFromI + clamp).

Target kelas = rerata data dummy tempat model SVM dilatih (ml_pipeline/data/dummy/generated_data.csv),
kecuali fruktosamin Diabetes: 386 -> 350 umol/L karena dengan VMID ~0,913 V batas baca rumus = 375.

    python3 buat_data_optimal.py
"""
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
LOG = HERE.parent / "data_log"

# === Konstanta main.cpp (CALC + readOnce) ===
RF = 100e3
PH_M, PH_C = -0.05916, 0.3226
GLU_A, GLU_B = 1000.0, 0.0
FRU_A, FRU_B = 35.0, -4000.0
LSB_G4 = 1.024 / 32768          # GAIN_FOUR, V per LSB (diferensial A1-A3)
N_SAMPLES = 40                  # measure(): 40 sampel terakhir
LOD_NA = 1.0

# Target per kelas: (pH, fruktosamin umol/L, glukosa saliva mg/dL), sebaran antar-sesi (SD)
TARGET = {
    "NORMAL":       ((6.94, 224.0, 0.67), (0.08, 8.0, 0.08)),
    "PRE-DIABETES": ((6.49, 285.0, 1.16), (0.10, 8.0, 0.12)),
    "DIABETES":     ((5.88, 350.0, 3.31), (0.12, 8.0, 0.25)),
}
MGDL_DEFAULT = {"NORMAL": 88, "PRE-DIABETES": 126, "DIABETES": 148}


def clamp(v, lo, hi):
    return min(max(v, lo), hi), (v < lo or v > hi)


def ph_from_v(v):            return clamp((v - PH_C) / PH_M, 4.0, 9.0)
def glu_from_i(i_na):        return clamp((i_na - GLU_B) / GLU_A, 0.1, 10.0)
def fru_from_v(vmid, vfru):  return clamp(((vmid - vfru) / RF * 1e9 - FRU_B) / FRU_A, 150.0, 500.0)


def label(raw, vout, i_na):  # sama dengan label() + kondisi sat di readOnce()
    if abs(raw) > 32000 or vout < 0.05 or vout > 3.25:
        return "JENUH -> arus > rentang / short / lonjakan awal"
    if abs(i_na) < LOD_NA:
        return "ARUS ~0 -> kontak strip putus / belum ada sampel"
    return "OK"


def parse(name):
    parts = name.split("_")
    kelas = next(k for k in ("PRE-DIABETES", "DIABETES", "NORMAL") if k in parts)
    mgdl = int(parts[1]) if parts[1].isdigit() else MGDL_DEFAULT[kelas]
    return kelas, mgdl


def contoh_prediabetes():
    """Sesi Pre-Diabetes lengkap (log asli hanya 5 baris): 150 s, interval & VMID seperti log asli."""
    asli = pd.read_csv(LOG / "glicovia_126_PRE-DIABETES_20261022_085847.csv")
    dt = asli["t_detik"].diff().median()
    t = np.arange(asli["t_detik"].iloc[0], 150.0, dt)
    t0 = pd.Timestamp(asli["waktu_iso"].iloc[0])
    rng = np.random.default_rng(126)
    return pd.DataFrame({
        "waktu_iso": [(t0 + pd.Timedelta(seconds=s - t[0])).isoformat(timespec="milliseconds") for s in t],
        "t_detik": t.round(3),
        "Vmid_V": (asli["Vmid_V"].mean() + rng.normal(0, 0.0009, len(t))).round(4),
    })


def optimal_session(asli, kelas, seed_name):
    rng = np.random.default_rng(zlib.crc32(seed_name.encode()))
    (ph_t, fru_t, glu_t), sd = TARGET[kelas]
    ph_t, fru_t, glu_t = (t + rng.normal(0, s) for t, s in zip((ph_t, fru_t, glu_t), sd))

    t = asli["t_detik"].to_numpy()
    n = len(t)
    vmid = asli["Vmid_V"].to_numpy()
    settle = 1 + 0.5 * np.exp(-(t - t[0]) / 5.0)          # lonjakan charging awal, tau 5 s

    # Volt ideal dari invers rumus CALC + noise kecil
    vph = PH_M * ph_t + PH_C + (settle - 1) * 0.02 + rng.normal(0, 0.0005, n)
    i_fru = (FRU_A * fru_t + FRU_B) * (1 + rng.normal(0, 0.003, n))
    vfru = vmid - i_fru * 1e-9 * RF
    i_glu = (GLU_A * glu_t + GLU_B) * settle * (1 + rng.normal(0, 0.015, n))
    raw = np.round(-i_glu * 1e-9 * RF / LSB_G4).astype(int)  # vDiff = Vout - Vmid = -I*Rf
    i_na = -raw * LSB_G4 / RF * 1e9
    vout = vmid + raw * LSB_G4

    df = pd.DataFrame({
        "waktu_iso": asli["waktu_iso"], "t_detik": t, "raw": raw,
        "Vfru_V": vfru.round(4), "Vglu_V": vout.round(4), "VpH_V": vph.round(4), "Vmid_V": vmid,
        "I_nA": i_na.round(2), "errI2C": 0,
        "status": [label(r, vo, i) for r, vo, i in zip(raw, vout, i_na)],
    })
    df["pH"] = [round(ph_from_v(v)[0], 2) for v in df.VpH_V]
    df["fructosamine_umol_L"] = [round(fru_from_v(m, f)[0], 1) for m, f in zip(df.Vmid_V, df.Vfru_V)]
    df["salivary_glucose_mgdL"] = [round(glu_from_i(i)[0], 2) for i in df.I_nA]
    return df


def measure_summary(d, i_col="I_nA"):
    """Ringkasan ala measure(): rerata volt + trimmed mean arus pada 40 sampel terakhir."""
    w = d.tail(N_SAMPLES)
    i = np.sort(w[i_col].to_numpy())
    k = len(i)
    tmean = i[k // 4: k - k // 4].mean()
    cv = i.std(ddof=1) / abs(tmean) * 100 if k > 1 and abs(tmean) > 1e-6 else float("nan")
    vph, vfru, vglu, vmid = (w[c].mean() for c in ("VpH_V", "Vfru_V", "Vglu_V", "Vmid_V"))
    ph, c1 = ph_from_v(vph)
    fru, c2 = fru_from_v(vmid, vfru)
    glu, c3 = glu_from_i(tmean)
    n_sat = int((~w["status"].str.startswith("OK")).sum())
    return dict(n=k, n_sat=n_sat, VpH_V=vph, Vfru_V=vfru, Vglu_V=vglu, Vmid_V=vmid, I_trim_nA=tmean,
                cv_pct=cv, pH=ph, fructosamine_umol_L=fru, salivary_glucose_mgdL=glu, clipped=c1 or c2 or c3)


def main():
    out_dir = HERE / "sesi"
    out_dir.mkdir(exist_ok=True)
    files = sorted(p for p in LOG.glob("glicovia_*.csv")
                   if any(k in p.stem.split("_") for k in ("NORMAL", "DIABETES", "PRE-DIABETES")))
    rows, deret = [], {}
    for p in files:
        asli = pd.read_csv(p)
        kelas, mgdl = parse(p.stem)
        opt = optimal_session(asli, kelas, p.name)
        opt.to_csv(out_dir / f"{p.stem}_optimal.csv", index=False)
        deret[p.stem] = opt
        for versi, d in (("asli", asli), ("optimal", opt)):
            rows.append({"sesi": p.stem, "kelas": kelas, "bg_mgdl_ref": mgdl, "versi": versi,
                         **measure_summary(d)})
    pre = optimal_session(contoh_prediabetes(), "PRE-DIABETES", "contoh_PRE-DIABETES")
    pre.to_csv(out_dir / "contoh_PRE-DIABETES_lengkap_optimal.csv", index=False)
    deret["contoh_PRE-DIABETES_lengkap"] = pre
    rows.append({"sesi": "contoh_PRE-DIABETES_lengkap", "kelas": "PRE-DIABETES", "bg_mgdl_ref": 112,
                 "versi": "optimal", **measure_summary(pre)})
    ring = pd.DataFrame(rows).round(4)
    ring.to_csv(HERE / "ringkasan_sesi.csv", index=False)

    # Grafik: optimal per kelas (titik = sesi); sesi < 40 sampel tidak lolos measure(), jadi tidak ikut
    opt = ring[(ring.versi == "optimal") & (ring.n >= N_SAMPLES)]
    kelas_urut = [k for k in ("NORMAL", "PRE-DIABETES", "DIABETES") if k in set(opt.kelas)]
    warna = {"NORMAL": "#2a9d8f", "PRE-DIABETES": "#e9c46a", "DIABETES": "#e76f51"}
    panel = [("pH", "pH saliva"), ("fructosamine_umol_L", "Salivary fructosamine (µmol/L)"),
             ("salivary_glucose_mgdL", "Salivary glucose (mg/dL)")]
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    for a, (col, judul) in zip(ax, panel):
        for i, k in enumerate(kelas_urut):
            v = opt.loc[opt.kelas == k, col].to_numpy()
            a.bar(i, v.mean(), yerr=v.std(ddof=1) if len(v) > 1 else 0, color=warna[k], alpha=.35,
                  capsize=5, width=.55)
            a.scatter(i + np.linspace(-.12, .12, len(v)), v, color=warna[k], s=28, zorder=3)
            a.annotate(f"n={len(v)}", (i, 0), xytext=(0, 3), textcoords="offset points",
                       ha="center", fontsize=8)
        a.set_xticks(range(len(kelas_urut)), [k.title() for k in kelas_urut])
        a.set_title(judul, fontsize=10)
        a.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Contoh data optimal (SIMULASI) per kelas — rumus main.cpp", fontsize=11)
    fig.tight_layout()
    fig.savefig(HERE / "perbandingan_optimal.png", dpi=200)

    # Grafik deret waktu: satu sesi per kelas, garis tebal = 40 sampel yang dipakai measure()
    contoh = {"NORMAL": "glicovia_88_NORMAL_20261021_045627", "PRE-DIABETES": "contoh_PRE-DIABETES_lengkap",
              "DIABETES": "glicovia_DIABETES_20261021_030626"}
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    for a, (col, judul) in zip(ax, panel):
        for k, s in contoh.items():
            d = deret[s]
            a.plot(d.t_detik, d[col], color=warna[k], lw=1, label=k.title())
            w = d.tail(N_SAMPLES)
            a.plot(w.t_detik, w[col], color=warna[k], lw=3, alpha=.5)
        a.set_title(judul, fontsize=10)
        a.set_xlabel("waktu (s)")
        a.spines[["top", "right"]].set_visible(False)
    ax[0].legend(fontsize=8, frameon=False)
    fig.suptitle("Contoh deret waktu optimal (SIMULASI): Normal vs Pre-Diabetes vs Diabetes", fontsize=11)
    fig.tight_layout()
    fig.savefig(HERE / "deret_waktu_3kelas.png", dpi=200)

    cols = ["kelas", "versi", "n", "n_sat", "VpH_V", "Vfru_V", "Vglu_V", "I_trim_nA",
            "pH", "fructosamine_umol_L", "salivary_glucose_mgdL", "clipped"]
    print(ring.set_index("sesi")[cols].to_string())


if __name__ == "__main__":
    main()
