"""Grafik ringkas 2 kelas: tiap titik = satu pengambilan data (rata-rata jendela 5 s, setelah 30 s transien).
Jalankan: ../../../ml_pipeline/.venv/bin/python buat_grafik_ringkas.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "..", "..", "data_log")
SESI = [("Normal", f) for f in ["glicovia_88_NORMAL_20261021_045627.csv", "glicovia_88_NORMAL_backup_20261021_050022.csv",
                                "glicovia_88_NORMAL_backup_2_20261021_050247.csv", "glicovia_88_NORMAL_backup_3_20261021_050732.csv"]] + \
       [("Diabetes", f) for f in ["glicovia_DIABETES_20261021_030626.csv", "glicovia_DIABETES_backup_20261021_032137.csv",
                                  "glicovia_148_DIABETES_backup_2_20261021_043540.csv", "glicovia_DIABETES_1_20261022_090334.csv",
                                  "glicovia_DIABETES_1_1_20261022_090602.csv"]]
COLOR = {"Normal": "#0072B2", "Diabetes": "#D55E00"}
FEAT = {"Vfru_V": "Fruktosamin", "Vglu_V": "Glukosa", "VpH_V": "pH"}
T0, WIN = 30.0, 5.0

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "font.size": 10, "axes.labelsize": 10, "legend.fontsize": 9, "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 300, "savefig.bbox": "tight"})

rows = []
for kelas, fn in SESI:
    s = pd.read_csv(os.path.join(LOG, fn)); s = s[s.t_detik >= T0].copy()
    s["w"] = ((s.t_detik - T0) // WIN).astype(int)
    g = s.groupby("w").agg({**{c: "mean" for c in FEAT}, "t_detik": ["count", "mean"]}); g.columns = list(FEAT) + ["n", "t"]
    rows.append(g[g.n >= 0.8 * WIN / 0.423].assign(kelas=kelas))
W = pd.concat(rows, ignore_index=True)
for c in FEAT: W[c] *= 1e3  # mV

print(W.kelas.value_counts().to_dict())
for k in COLOR:
    print(k, {FEAT[c]: "med %.2f  IQR %.2f-%.2f  min-max %.2f-%.2f" % tuple(np.percentile(W.loc[W.kelas == k, c], p) for p in (50, 25, 75, 0, 100)) for c in FEAT})
# rasio median Normal/Diabetes
for c in FEAT: print(FEAT[c], "median Normal/Diabetes = %.1f" % (W.loc[W.kelas == "Normal", c].median() / W.loc[W.kelas == "Diabetes", c].median()))

# Gambar 9: titik terhadap waktu
fig, ax = plt.subplots(3, 1, figsize=(6.3, 6.2), sharex=True)
for a, (c, n) in zip(ax, FEAT.items()):
    for k in COLOR:
        w = W[W.kelas == k]
        a.scatter(w.t, w[c], s=9, alpha=.65, color=COLOR[k], label="Kelas " + k, lw=0)
    a.set_yscale("log"); a.set_ylabel("%s (mV)" % n); a.grid(alpha=.25, which="both", lw=.4)
ax[0].legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(.5, 1.0))
ax[-1].set_xlabel("Waktu pengukuran (s)")
for a, s in zip(ax, "abc"): a.text(-0.12, 1.0, "(%s)" % s, transform=a.transAxes, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(BASE, "ringkas_gambar9_titik_waktu.png"))

# Gambar 10: sebaran tegangan per parameter
fig, ax = plt.subplots(1, 3, figsize=(6.8, 2.9)); rng = np.random.default_rng(0)
for a, (c, n) in zip(ax, FEAT.items()):
    vals = [W.loc[W.kelas == k, c].values for k in COLOR]
    bp = a.boxplot(vals, widths=.5, showfliers=False, patch_artist=True, medianprops=dict(color="k"))
    for p, k in zip(bp["boxes"], COLOR): p.set(facecolor=COLOR[k], alpha=.25, edgecolor=COLOR[k])
    for i, (v, k) in enumerate(zip(vals, COLOR), 1):
        a.scatter(i + rng.uniform(-.17, .17, len(v)), v, s=4, alpha=.5, color=COLOR[k], lw=0)
    a.set_yscale("log"); a.set_xticks([1, 2]); a.set_xticklabels(list(COLOR)); a.set_title(n, fontsize=10)
    a.set_ylabel("Tegangan (mV)"); a.grid(axis="y", alpha=.25, which="both", lw=.4)
fig.tight_layout(); fig.savefig(os.path.join(BASE, "ringkas_gambar10_sebaran.png"))

# Gambar 11: ruang fitur
fig, ax = plt.subplots(figsize=(4.4, 3.5))
for k in COLOR:
    w = W[W.kelas == k]; ax.scatter(w.Vfru_V, w.VpH_V, s=12, alpha=.65, color=COLOR[k], label="Kelas " + k, lw=0)
ax.set_xscale("log"); ax.set_xlabel("Tegangan fruktosamin (mV)"); ax.set_ylabel("Tegangan pH (mV)")
ax.grid(alpha=.25); ax.legend(frameon=False, loc="upper left")
fig.tight_layout(); fig.savefig(os.path.join(BASE, "ringkas_gambar11_ruang_fitur.png"))
