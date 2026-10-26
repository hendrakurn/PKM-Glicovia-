"""Grafik proses RBF pada model SVR nyata (model_svr_units_v1.pkl): saliva -> mg/dL.

Tiga panel: (1) kemiripan sampel dengan support vector di ruang fitur terskala,
(2) kontribusi tiap support vector + bias = kadar, (3) kurva keluaran mg/dL dan ambang ADA.
Model dilatih dari 2 orang / 2 label (88, 148): menggambarkan mekanisme, bukan akurasi.

    .venv/bin/python diagrams/rbf_proses.py   ->  diagrams/rbf_proses.png (+ .pdf)
"""
import pickle
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")                      # pickle dibuat di sklearn 1.9, lokal 1.7
ROOT = Path(__file__).resolve().parents[1]
GREEN, GOLD, RED, DARK = "#2E7D32", "#F9A825", "#C62828", "#1B5E20"
COLS = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]

m = pickle.load(open(ROOT / "src/models/real/model_svr_units_v1.pkl", "rb"))
svr, scaler = m.named_steps["svr"], m.named_steps["prep"].named_transformers_["scale"]
gamma, coef, b = svr._gamma, svr.dual_coef_[0], float(svr.intercept_[0])
sv, mu, sd = svr.support_vectors_, scaler.mean_, scaler.scale_

d = pd.read_csv(ROOT / "data/real/generated_data_real.csv")
sv_label = d["bg_mgdl_reference"].to_numpy()[svr.support_]
row = d[d.bg_mgdl_reference == 88].iloc[0]             # satu sampel Normal sebagai contoh
x = row[COLS].to_numpy(float)[None]
z = m.named_steps["prep"].transform(x)[0]
K = np.exp(-gamma * ((sv - z) ** 2).sum(1))
kontrib = coef * K
pred = float(kontrib.sum() + b)
col_sv = [GREEN if v < 100 else RED for v in sv_label]

fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(15, 4.6), gridspec_kw={"width_ratios": [1.1, 1, 1.1]})

# (1) ruang fitur + kontur kemiripan sampel
g = np.linspace(-2.2, 2.2, 300)
gx, gy = np.meshgrid(g, g)
a1.contourf(gx, gy, np.exp(-gamma * ((gx - z[0]) ** 2 + (gy - z[1]) ** 2)), levels=12, cmap="Greens", alpha=0.55)
a1.scatter(*sv.T, c=col_sv, s=70 + 260 * K, edgecolor="k", zorder=3)
for i, (p, k) in enumerate(zip(sv, K), 1):
    a1.annotate(f"{i}", p, textcoords="offset points", xytext=(7, 6), fontsize=8)
a1.scatter(*z, marker="*", s=380, c=GOLD, edgecolor="k", zorder=4, label="Sampel baru")
a1.set(xlabel="pH (terskala)", ylabel="Fruktosamin (terskala)", title="① Kemiripan dengan tiap support vector",
       xlim=(-2.2, 2.2), ylim=(-2.2, 2.2))
a1.scatter([], [], c=GREEN, edgecolor="k", label="SV label 88 mg/dL")
a1.scatter([], [], c=RED, edgecolor="k", label="SV label 148 mg/dL")
a1.legend(fontsize=8, loc="upper left")

# (2) kontribusi
idx = np.arange(1, len(K) + 1)
a2.bar(idx, kontrib, color=col_sv, edgecolor="k")
a2.axhline(0, color="k", lw=0.8)
a2.set(xlabel="Support vector ke-", ylabel="bobot × K  (mg/dL)", title="② Kontribusi tiap pola", ylim=(-120, 175),
       xticks=idx)
a2.text(0.5, 0.97, f"Σ = {kontrib.sum():+.0f}\nbias b = {b:+.0f}\nkadar = {pred:.0f} mg/dL",
        transform=a2.transAxes, va="top", ha="center", fontsize=11,
        bbox=dict(boxstyle="round", fc="white", ec=DARK))

# (3) kurva keluaran terhadap fruktosamin (pH dikunci di rata-rata) + ambang ADA
fru = np.linspace(150, 450, 300)
grid = np.c_[np.full_like(fru, row.glucose_saliva), np.full_like(fru, mu[0]), fru]
a3.axhspan(0, 100, color=GREEN, alpha=0.15)
a3.axhspan(100, 126, color=GOLD, alpha=0.25)
a3.axhspan(126, 200, color=RED, alpha=0.15)
a3.plot(fru, m.predict(grid), color=DARK, lw=2.4, label="Prediksi model (pH tetap)")
for lab, c in [(88, GREEN), (148, RED)]:
    s = d[d.bg_mgdl_reference == lab]
    a3.scatter(s.fructosamine_umol_l, s.bg_mgdl_reference, c=c, s=18, alpha=0.7, label=f"Data nyata {lab}")
a3.scatter(row.fructosamine_umol_l, pred, marker="*", s=380, c=GOLD, edgecolor="k", zorder=4)
for y0, t in [(60, "Normal"), (113, "Prediabetes"), (170, "Diabetes")]:
    a3.text(445, y0, t, ha="right", va="center", fontsize=9, color="#333")
a3.set(xlabel="Fruktosamin (µmol/L)", ylabel="Glukosa darah (mg/dL)", title="③ Angka → kategori (ambang ADA)",
       ylim=(40, 190), xlim=(150, 450))
a3.legend(fontsize=8, loc="upper left")

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(Path(__file__).resolve().parent / f"rbf_proses.{ext}", dpi=300, facecolor="white")
print(f"kadar = {pred:.1f} mg/dL; Disimpan rbf_proses.png")
