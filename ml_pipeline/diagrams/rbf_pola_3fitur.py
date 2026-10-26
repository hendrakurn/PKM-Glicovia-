"""Ilustrasi SVM RBF dengan 3 fitur (glukosa saliva, pH, fruktosamin) = FEATURE_ORDER inference.py.

Data DUMMY hanya untuk ilustrasi, bukan data alat. Batas 3D tak bisa digambar jelas, jadi
tiap panel 2D adalah irisan: fitur ketiga dikunci di rata-rata (0 setelah diskala).

    .venv/bin/python diagrams/rbf_pola_3fitur.py   ->  diagrams/rbf_pola_3fitur.png (+ .pdf)
"""
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

OUT = Path(__file__).resolve().parent
FITUR = ["Glukosa saliva", "pH", "Fruktosamin"]
NAMA = ["Normal", "Prediabetes", "Diabetes"]
WARNA = ["#2E7D32", "#F9A825", "#C62828"]

rng = np.random.default_rng(7)
pusat = [(0.0, 0.0, 0.0), (1.4, 0.9, 1.2), (2.6, 2.2, 0.3)]
X = StandardScaler().fit_transform(np.vstack([rng.normal(c, 0.6, (40, 3)) for c in pusat]))
y = np.repeat([0, 1, 2], 40)
clf = SVC(kernel="rbf", C=10, gamma=0.5).fit(X, y)

fig = plt.figure(figsize=(11, 9))

a3 = fig.add_subplot(2, 2, 1, projection="3d")
for k in range(3):
    a3.scatter(*X[y == k].T, c=WARNA[k], edgecolor="white", s=30, label=NAMA[k])
a3.scatter(*X[clf.support_].T, facecolor="none", edgecolor="k", s=90, label="Support vector")
a3.set(xlabel=FITUR[0], ylabel=FITUR[1], zlabel=FITUR[2], title="3 fitur = 1 titik di ruang 3D")
a3.legend(fontsize=7, loc="upper left")

g = np.linspace(-2.6, 2.6, 300)
gx, gy = np.meshgrid(g, g)
for ax, (i, j) in zip([fig.add_subplot(2, 2, p) for p in (2, 3, 4)], combinations(range(3), 2)):
    grid = np.zeros((gx.size, 3))
    grid[:, i], grid[:, j] = gx.ravel(), gy.ravel()        # fitur ketiga = 0 (rata-rata)
    z = clf.predict(grid).reshape(gx.shape)
    ax.contourf(gx, gy, z, levels=[-.5, .5, 1.5, 2.5], colors=WARNA, alpha=0.18)
    ax.contour(gx, gy, z, levels=[.5, 1.5], colors="k", linewidths=1.3)
    for k in range(3):
        ax.scatter(X[y == k, i], X[y == k, j], c=WARNA[k], edgecolor="white", s=30)
    ax.scatter(X[clf.support_, i], X[clf.support_, j], facecolor="none", edgecolor="k", s=90)
    ax.set(xlabel=f"{FITUR[i]} (terskala)", ylabel=f"{FITUR[j]} (terskala)", xlim=(-2.6, 2.6),
           ylim=(-2.6, 2.6), title=f"Irisan: {FITUR[i]} vs {FITUR[j]}")

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(OUT / f"rbf_pola_3fitur.{ext}", dpi=300, facecolor="white")
print("Disimpan:", OUT / "rbf_pola_3fitur.png")
