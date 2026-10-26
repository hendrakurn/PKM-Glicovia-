"""Ilustrasi SVM kernel RBF untuk slide "Analisis pola".

Data DUMMY dua biomarker (pH, fruktosamin) hanya untuk ilustrasi, bukan data alat.

    .venv/bin/python diagrams/rbf_pola.py   ->  diagrams/rbf_pola.png (+ .pdf)
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

OUT = Path(__file__).resolve().parent
GREEN, GOLD, RED = "#2E7D32", "#F9A825", "#C62828"
NAMA = ["Normal", "Prediabetes", "Diabetes"]
WARNA = [GREEN, GOLD, RED]

rng = np.random.default_rng(7)
pusat = [(0.0, 0.0), (1.6, 0.9), (0.2, 2.4)]          # tiga kelompok pola, tumpang tindih tipis
X = np.vstack([rng.normal(c, 0.55, (40, 2)) for c in pusat])
y = np.repeat([0, 1, 2], 40)

X = StandardScaler().fit_transform(X)                  # RBF berbasis jarak -> wajib diskalakan
clf = SVC(kernel="rbf", C=10, gamma=0.5).fit(X, y)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1.5, 1]})

# (a) batas keputusan melengkung
gx, gy = np.meshgrid(np.linspace(-2.6, 2.6, 400), np.linspace(-2.6, 2.6, 400))
z = clf.predict(np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
a1.contourf(gx, gy, z, levels=[-.5, .5, 1.5, 2.5], colors=WARNA, alpha=0.18)
a1.contour(gx, gy, z, levels=[.5, 1.5], colors="k", linewidths=1.4)
for k in range(3):
    a1.scatter(*X[y == k].T, c=WARNA[k], edgecolor="white", s=38, label=NAMA[k])
a1.scatter(*X[clf.support_].T, facecolor="none", edgecolor="k", s=110, linewidth=1.1,
           label="Support vector")
a1.set(xlabel="Biomarker 1 (pH, terskala)", ylabel="Biomarker 2 (fruktosamin, terskala)",
       title="Batas keputusan RBF: melengkung mengikuti pola")
a1.legend(loc="lower right", fontsize=8, framealpha=0.9)

# (b) fungsi kernel: kemiripan vs jarak, tiga nilai gamma
d = np.linspace(0, 3, 300)
for g, ls in [(0.1, ":"), (0.5, "-"), (2.0, "--")]:
    a2.plot(d, np.exp(-g * d**2), ls, lw=2.2, color="#1B5E20", label=f"γ = {g}")
a2.set(xlabel="Jarak antar sampel  ‖x − x′‖", ylabel="Kemiripan  K(x, x′)",
       title="Kernel RBF: dekat = mirip, jauh = tidak", ylim=(0, 1.05))
a2.text(1.45, 0.78, r"$K=e^{-\gamma\,\|x-x'\|^{2}}$", fontsize=13,
        bbox=dict(boxstyle="round", fc="white", ec="#1B5E20"))
a2.legend(fontsize=9)
a2.grid(alpha=0.3)

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(OUT / f"rbf_pola.{ext}", dpi=300, transparent=False, facecolor="white")
print("Disimpan:", OUT / "rbf_pola.png")
