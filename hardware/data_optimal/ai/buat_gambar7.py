"""Gambar 7: pembacaan tiap parameter (tegangan dan nilai riil) pada tiga kelas, dari data optimal (SIMULASI).
Sumber: dataset_jendela.csv (hasil latih_ai_optimal.py). Jalankan: ../../../ml_pipeline/.venv/bin/python buat_gambar7.py
"""
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
W = pd.read_csv(HERE / "dataset_jendela.csv")
KELAS = ["Normal", "Pre-Diabetes", "Diabetes"]
WARNA = {"Normal": "#0072B2", "Pre-Diabetes": "#009E73", "Diabetes": "#D55E00"}
BARIS = [[("VpH_V", "Tegangan pH (mV)"), ("Vfru_V", "Tegangan fruktosamin (mV)"), ("Vglu_V", "Tegangan glukosa (mV)")],
         [("pH", "pH saliva"), ("fructosamine_umol_L", "Fruktosamin (µmol/L)"), ("salivary_glucose_mgdL", "Glukosa saliva (mg/dL)")]]

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                     "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 300, "savefig.bbox": "tight"})
fig, ax = plt.subplots(2, 3, figsize=(7.4, 5.0), sharex=True)
for r, baris in enumerate(BARIS):
    for c, (col, lab) in enumerate(baris):
        a = ax[r, c]
        for s, d in W.groupby("sesi"):
            a.plot(d.t, d[col], color=WARNA[d.kelas.iloc[0]], lw=.9, alpha=.8)
        a.set_ylabel(lab, fontsize=9); a.grid(alpha=.25, lw=.4)
        a.text(-0.28, 1.04, "(%s)" % "abcdef"[r * 3 + c], transform=a.transAxes, fontweight="bold")
        if r == 1: a.set_xlabel("Waktu (s)")
for k in KELAS: ax[0, 0].plot([], [], color=WARNA[k], label=k)
h, l = ax[0, 0].get_legend_handles_labels()
fig.legend(h, l, frameon=False, fontsize=9, loc="upper center", ncol=3)
fig.text(0.5, -0.01, "Data simulasi kondisi optimal, bukan hasil pengukuran alat", ha="center", fontsize=8.5, style="italic")
fig.tight_layout(rect=[0, 0.01, 1, 0.94]); fig.savefig(HERE / "gambar7_pembacaan_3kelas.png")
