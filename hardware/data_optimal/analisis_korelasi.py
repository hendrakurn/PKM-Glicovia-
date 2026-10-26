"""Analisis data_optimal: (1) volt vs satuan riil (sensitivitas, R2), (2) volt asli vs optimal,
(3) korelasi antar-parameter dan terhadap glukosa darah referensi, (4) pemisahan kelas (volt vs satuan).
Semua dari data SIMULASI + log asli; hubungan volt->satuan linear karena memang diturunkan dari rumus main.cpp.

    python3 analisis_korelasi.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
N = 40
WARNA = {"NORMAL": "#2a9d8f", "PRE-DIABETES": "#e9c46a", "DIABETES": "#e76f51"}
# (kolom volt, kolom satuan, label volt, label satuan)
PARAM = [("VpH_V", "pH", "VpH (V)", "pH"),
         ("Vfru_V", "fructosamine_umol_L", "Vfru (V)", "Fruktosamin (µmol/L)"),
         ("Vglu_V", "salivary_glucose_mgdL", "Vglu (V)", "Glukosa saliva (mg/dL)")]

ring = pd.read_csv(HERE / "ringkasan_sesi.csv")
opt = ring[(ring.versi == "optimal") & (ring.n >= N)].reset_index(drop=True)
asli = ring[(ring.versi == "asli") & (ring.n >= N)].set_index("sesi")

# ---- 1. volt vs satuan riil: regresi per baris (40 sampel terakhir tiap sesi) ----
frames = []
for s, k in zip(opt.sesi, opt.kelas):
    d = pd.read_csv(HERE / "sesi" / f"{s}_optimal.csv").tail(N)
    d["kelas"] = k
    frames.append(d)
baris = pd.concat(frames, ignore_index=True)

fig, ax = plt.subplots(1, 3, figsize=(13, 4))
print("== 1. Regresi volt -> satuan riil (per baris, n=%d)" % len(baris))
fit = {}
for a, (cv, cu, lv, lu) in zip(ax, PARAM):
    m, c = np.polyfit(baris[cv], baris[cu], 1)
    r = np.corrcoef(baris[cv], baris[cu])[0, 1]
    fit[cu] = (m, c, r)
    for k, g in baris.groupby("kelas"):
        a.scatter(g[cv], g[cu], s=10, color=WARNA[k], alpha=.7, label=k.title())
    xs = np.linspace(baris[cv].min(), baris[cv].max(), 20)
    a.plot(xs, m * xs + c, "k--", lw=1)
    a.set_xlabel(lv); a.set_ylabel(lu)
    a.set_title(f"r = {r:.3f}   kemiringan = {m:.2f}", fontsize=10)
    a.spines[["top", "right"]].set_visible(False)
    print(f"{cu:24s} slope={m:9.3f} (satuan/V)  = {1000/m if m else float('nan'):8.2f} mV/satuan  r={r:.4f}")
ax[0].legend(fontsize=8, frameon=False)
fig.suptitle("Volt vs satuan riil (data optimal, 40 sampel terakhir per sesi)", fontsize=11)
fig.tight_layout(); fig.savefig(HERE / "korelasi_volt_satuan.png", dpi=200)

# ---- 2. volt asli vs optimal per sesi ----
sesi_asli = [s for s in opt.sesi if s in asli.index]
fig, ax = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
print("\n== 2. Volt asli vs optimal (rerata 40 sampel terakhir)")
rows = []
for a, (cv, cu, lv, lu) in zip(ax, PARAM):
    for i, s in enumerate(sesi_asli):
        k = opt.set_index("sesi").loc[s, "kelas"]
        va, vo = asli.loc[s, cv], opt.set_index("sesi").loc[s, cv]
        a.plot([va, vo], [i, i], color="#bbb", lw=1, zorder=1)
        a.scatter(va, i, color="k", marker="x", s=30, zorder=2)
        a.scatter(vo, i, color=WARNA[k], s=40, zorder=3)
        rows.append((cv, s, k, va, vo))
    a.set_xlabel(lv); a.spines[["top", "right"]].set_visible(False)
ax[0].set_yticks(range(len(sesi_asli)), [s.replace("glicovia_", "")[:-16] for s in sesi_asli], fontsize=7)
ax[0].scatter([], [], color="k", marker="x", label="asli"); ax[0].scatter([], [], color="#888", label="optimal")
ax[0].legend(fontsize=8, frameon=False, loc="lower right")
fig.suptitle("Selisih volt log asli (×) vs contoh optimal (●)", fontsize=11)
fig.tight_layout(); fig.savefig(HERE / "volt_asli_vs_optimal.png", dpi=200)
sel = pd.DataFrame(rows, columns=["kanal", "sesi", "kelas", "asli", "optimal"])
sel["selisih"] = sel.optimal - sel.asli
print(sel.groupby(["kanal", "kelas"])[["asli", "optimal", "selisih"]].mean().round(4).to_string())

# ---- 3. korelasi antar-parameter & dengan glukosa darah referensi (level sesi) ----
ref = {"NORMAL": 88, "PRE-DIABETES": 112, "DIABETES": 148}
opt["bg_ref"] = opt.kelas.map(ref)
cols = ["VpH_V", "Vfru_V", "Vglu_V", "pH", "fructosamine_umol_L", "salivary_glucose_mgdL", "bg_ref"]
corr = opt[cols].corr(method="spearman")
print("\n== 3. Korelasi Spearman level sesi (n=%d)" % len(opt))
print(corr.round(2).to_string())
nama = ["VpH", "Vfru", "Vglu", "pH", "Fru", "Glu", "BG ref"]
fig, a = plt.subplots(figsize=(5.8, 5))
im = a.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
a.set_xticks(range(7), nama, rotation=45, ha="right"); a.set_yticks(range(7), nama)
for i in range(7):
    for j in range(7):
        a.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7,
               color="w" if abs(corr.iloc[i, j]) > .6 else "k")
fig.colorbar(im, shrink=.8); a.set_title("Korelasi Spearman (level sesi)", fontsize=10)
fig.tight_layout(); fig.savefig(HERE / "korelasi_matriks.png", dpi=200)

# ---- 4. pemisahan kelas: Normal vs Diabetes, ukuran efek di domain volt vs satuan ----
print("\n== 4. Pemisahan Normal vs Diabetes (Cohen d, level sesi)")
n_, d_ = opt[opt.kelas == "NORMAL"], opt[opt.kelas == "DIABETES"]
for c in cols[:6]:
    a, b = n_[c].to_numpy(), d_[c].to_numpy()
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    print(f"{c:24s} Normal {a.mean():8.3f}±{a.std(ddof=1):6.3f}  Diabetes {b.mean():8.3f}±{b.std(ddof=1):6.3f}  d={abs(a.mean()-b.mean())/sp:6.1f}")

print("\nSensitivitas teoritis dari rumus main.cpp:")
print("  pH   : dV/dpH   = -59,16 mV/pH")
print("  fru  : dV/dFru  = -(FRU_A·Rf) = -3,5 mV per µmol/L  (Vfru = Vmid - I·Rf)")
print("  glu  : dVout/dG = -(GLU_A·Rf) = -100 mV per mg/dL")
