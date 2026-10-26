"""Perbandingan nilai riil (pH, fruktosamin, glukosa saliva) hasil konversi tegangan, tiga kelas, data optimal (SIMULASI).
Kotak = sebaran jendela 5 s; titik besar = median tiap sesi. Sumber: dataset_jendela.csv.
Jalankan: ../../../ml_pipeline/.venv/bin/python buat_gambar_nilai_riil.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
W = pd.read_csv(HERE / "dataset_jendela.csv")
KELAS = ["Normal", "Pre-Diabetes", "Diabetes"]
WARNA = {"Normal": "#0072B2", "Pre-Diabetes": "#009E73", "Diabetes": "#D55E00"}
PARAM = [("pH", "pH saliva", "%.2f"), ("fructosamine_umol_L", "Fruktosamin (µmol/L)", "%.0f"),
         ("salivary_glucose_mgdL", "Glukosa saliva (mg/dL)", "%.2f")]

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                     "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 300, "savefig.bbox": "tight"})
rng = np.random.default_rng(0)
fig, ax = plt.subplots(1, 3, figsize=(7.4, 3.0))
for a, (col, lab, fmt) in zip(ax, PARAM):
    data = [W.loc[W.kelas == k, col].to_numpy() for k in KELAS]
    bp = a.boxplot(data, widths=.5, showfliers=False, patch_artist=True, medianprops=dict(color="k"))
    for p, k in zip(bp["boxes"], KELAS): p.set(facecolor=WARNA[k], alpha=.3, edgecolor=WARNA[k])
    for i, k in enumerate(KELAS, 1):
        med = W[W.kelas == k].groupby("sesi")[col].median().to_numpy()
        a.scatter(i + rng.uniform(-.12, .12, len(med)), med, s=22, color=WARNA[k], zorder=3, edgecolor="w", lw=.5)
        a.text(i, a.get_ylim()[1], fmt % data[i - 1].mean(), ha="center", va="bottom", fontsize=8.5, color=WARNA[k])
    a.set_xticks([1, 2, 3], ["Normal", "Pre-DM", "DM"]); a.set_ylabel(lab, fontsize=9); a.grid(axis="y", alpha=.25, lw=.4)
for a, s in zip(ax, "abc"): a.text(-0.28, 1.12, "(%s)" % s, transform=a.transAxes, fontweight="bold")
fig.text(0.5, -0.03, "Data simulasi kondisi optimal; angka di atas = rerata kelas; titik = median tiap sesi", ha="center", fontsize=8.5, style="italic")
fig.tight_layout(); fig.savefig(HERE / "gambar_nilai_riil_3kelas.png")
print(W.groupby("kelas")[[p[0] for p in PARAM]].agg(["mean", "std"]).round(2).loc[KELAS].to_string())
