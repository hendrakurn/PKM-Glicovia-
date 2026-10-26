"""Proses RBF dengan 3 fitur (glukosa saliva, pH, fruktosamin): saliva -> mg/dL.

Model dilatih ulang di memori (grid + GroupKFold sama dengan src/train_real_svr.py), TIDAK disimpan,
jadi model_svr_units_v1.pkl (2 fitur) tidak berubah. Data nyata: 2 orang / 2 label (88, 148).

    .venv/bin/python diagrams/rbf_proses_3fitur.py   ->  diagrams/rbf_proses_3fitur.png (+ .pdf)
"""
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.train_real_svr import INPUT_COLS, search  # noqa: E402

GREEN, GOLD, RED, DARK = "#2E7D32", "#F9A825", "#C62828", "#1B5E20"
NAMA = ["Glukosa saliva", "pH", "Fruktosamin (µmol/L)"]

d = pd.read_csv(ROOT / "data/real/generated_data_real.csv")
X, y, grp = d[INPUT_COLS].to_numpy(float), d["bg_mgdl_reference"].to_numpy(float), d["session_id"]
gs = search(INPUT_COLS).fit(X, y, groups=grp)
m = gs.best_estimator_
svr, scaler = m.named_steps["svr"], m.named_steps["prep"].named_transformers_["scale"]
gamma, coef, b = svr._gamma, svr.dual_coef_[0], float(svr.intercept_[0])
sv = svr.support_vectors_
sv_label = y[svr.support_]

x = X[y == 88][:1]                                     # satu sampel Normal sebagai contoh
z = m.named_steps["prep"].transform(x)[0]
K = np.exp(-gamma * ((sv - z) ** 2).sum(1))
kontrib = coef * K
pred = float(kontrib.sum() + b)
col_sv = [GREEN if v < 100 else RED for v in sv_label]
print(f"params {gs.best_params_}  n_SV={len(sv)}  Σ={kontrib.sum():.1f} b={b:.1f} -> {pred:.1f} mg/dL")

fig = plt.figure(figsize=(15, 4.8))
a1 = fig.add_subplot(1, 3, 1, projection="3d")
a1.scatter(*sv.T, c=col_sv, s=50 + 250 * K, edgecolor="k", depthshade=False)
a1.plot([z[0]], [z[1]], [z[2]], marker="*", ms=24, mfc=GOLD, mec="k", ls="", zorder=20, label="Sampel baru")
a1.scatter([], [], c=GREEN, edgecolor="k", label="SV label 88"); a1.scatter([], [], c=RED, edgecolor="k", label="SV label 148")
a1.legend(fontsize=8, loc="upper left")
a1.set_xlabel("Glukosa (terskala)", labelpad=8); a1.set_ylabel("pH (terskala)", labelpad=8)
a1.set_zlabel("Fruktosamin (terskala)", labelpad=4)
a1.set_title("① Sampel vs support vector (3D)\nukuran titik = kemiripan K")

a2 = fig.add_subplot(1, 3, 2)
idx = np.arange(1, len(K) + 1)
a2.bar(idx, kontrib, color=col_sv, edgecolor="k")
a2.axhline(0, color="k", lw=0.8)
a2.set(xlabel=f"{len(K)} support vector", ylabel="bobot × K  (mg/dL)", xticks=[],
       title=f"② Kontribusi tiap pola\nΣ = {kontrib.sum():+.0f},  b = {b:+.0f}  →  {pred:.0f} mg/dL")

a3 = fig.add_subplot(1, 3, 3)
fru = np.linspace(190, 400, 300)
grid = np.c_[np.full_like(fru, X[:, 0].mean()), np.full_like(fru, X[:, 1].mean()), fru]
a3.axhspan(0, 100, color=GREEN, alpha=0.15)
a3.axhspan(100, 126, color=GOLD, alpha=0.25)
a3.axhspan(126, 200, color=RED, alpha=0.15)
a3.plot(fru, m.predict(grid), color=DARK, lw=2.4, label="Prediksi (glukosa, pH tetap)")
for lab, c in [(88, GREEN), (148, RED)]:
    s = d[d.bg_mgdl_reference == lab]
    a3.scatter(s.fructosamine_umol_l, s.bg_mgdl_reference, c=c, s=18, alpha=0.7, label=f"Data nyata {lab}")
a3.scatter(x[0, 2], pred, marker="*", s=400, c=GOLD, edgecolor="k", zorder=4)
for y0, t in [(60, "Normal"), (113, "Prediabetes"), (170, "Diabetes")]:
    a3.text(395, y0, t, ha="right", va="center", fontsize=9, color="#333")
a3.set(xlabel=NAMA[2], ylabel="Glukosa darah (mg/dL)", title="③ Angka → kategori (ambang ADA)",
       ylim=(40, 190), xlim=(190, 400))
a3.legend(fontsize=8, loc="upper left")

fig.tight_layout(w_pad=3)
for ext in ("png", "pdf"):
    fig.savefig(Path(__file__).resolve().parent / f"rbf_proses_3fitur.{ext}", dpi=300, facecolor="white")
