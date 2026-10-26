"""Gambar 12: tegangan log asli vs contoh kondisi optimal (SIMULASI), gaya sama dengan Gambar 9-11.
Sumber: ../../data_optimal/ringkasan_sesi.csv. Jalankan: ../../../ml_pipeline/.venv/bin/python buat_gambar12.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(os.path.join(BASE, "..", "..", "data_optimal", "ringkasan_sesi.csv"))
# urutan dan kode sesi sama dengan analisis_loso.py (N1-N4, D1-D5)
KODE = {"glicovia_88_NORMAL_20261021_045627": "N1", "glicovia_88_NORMAL_backup_20261021_050022": "N2",
        "glicovia_88_NORMAL_backup_2_20261021_050247": "N3", "glicovia_88_NORMAL_backup_3_20261021_050732": "N4",
        "glicovia_DIABETES_20261021_030626": "D1", "glicovia_DIABETES_backup_20261021_032137": "D2",
        "glicovia_148_DIABETES_backup_2_20261021_043540": "D3", "glicovia_DIABETES_1_20261022_090334": "D4",
        "glicovia_DIABETES_1_1_20261022_090602": "D5"}
COLOR = {"NORMAL": "#0072B2", "DIABETES": "#D55E00"}
KAN = [("Vfru_V", "Fruktosamin"), ("Vglu_V", "Glukosa"), ("VpH_V", "pH")]
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                     "font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300, "savefig.bbox": "tight"})
A = R[(R.versi == "asli")].set_index("sesi"); O = R[(R.versi == "optimal")].set_index("sesi")
fig, ax = plt.subplots(1, 3, figsize=(7.2, 3.0), sharey=True)
for a, (c, n) in zip(ax, KAN):
    for i, (s, kode) in enumerate(KODE.items()):
        k = O.loc[s, "kelas"]
        va, vo = A.loc[s, c] * 1e3, O.loc[s, c] * 1e3
        a.plot([va, vo], [i, i], color="#bbb", lw=1, zorder=1)
        a.scatter(va, i, color="k", marker="x", s=22, zorder=2)
        a.scatter(vo, i, color=COLOR[k], s=26, zorder=3)
    a.set_xlabel("%s (mV)" % n); a.grid(axis="x", alpha=.25, lw=.4)
ax[0].set_yticks(range(len(KODE)), list(KODE.values())); ax[0].invert_yaxis()
ax[0].scatter([], [], color="k", marker="x", label="Data log"); ax[0].scatter([], [], color="#777", label="Optimal (simulasi)")
ax[0].legend(frameon=False, fontsize=8, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
for a, s in zip(ax, "abc"): a.text(-0.04, 1.02, "(%s)" % s, transform=a.transAxes, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(BASE, "final_gambar12_asli_vs_optimal.png"))
