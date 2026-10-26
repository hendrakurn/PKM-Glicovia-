"""Eksplorasi 2 kelas (Normal vs Diabetes): tiap pembacaan fase stabil dianggap satu sampel.
SVM RBF + standardisasi, 5-fold stratified CV. Menghasilkan Gambar 12-15 + ringkasan di stdout.
Jalankan: ../../ml_pipeline/.venv/bin/python buat_grafik_klasifikasi.py
"""
import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, roc_auc_score

BASE = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(BASE, "..", "backup")
FILES = {"Normal": "glicovia_88_NORMAL_20261021_045627.csv",
         "Diabetes": "glicovia_148_DIABETES_20261021_030626.csv"}
COLOR = {"Normal": "#0072B2", "Diabetes": "#D55E00"}
FEAT = {"Vfru_V": "Fruktosamin", "Vglu_V": "Glukosa", "VpH_V": "pH"}
T_STABIL = 60.0  # sama dengan buat_grafik.py

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "font.size": 10, "axes.labelsize": 10, "legend.fontsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 300, "savefig.bbox": "tight",
})

df = pd.concat([pd.read_csv(os.path.join(BACKUP, f)).assign(kelas=k) for k, f in FILES.items()])
df = df[df.t_detik >= T_STABIL].reset_index(drop=True)
y = (df.kelas == "Diabetes").astype(int).values  # 1 = Diabetes
X_all = df[list(FEAT)].values
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
model = lambda: make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42))

def evaluate(cols):
    X = df[cols].values
    p = cross_val_predict(model(), X, y, cv=cv, method="predict_proba")[:, 1]
    yp = (p >= 0.5).astype(int)
    return dict(acc=accuracy_score(y, yp), f1=f1_score(y, yp, average="macro"),
                auc=roc_auc_score(y, p), cm=confusion_matrix(y, yp))

print("Jumlah sampel:", df.kelas.value_counts().to_dict())

# --- evaluasi utama (3 fitur) ---
main = evaluate(list(FEAT))
fold_acc = []
for tr, te in cv.split(X_all, y):
    m = model().fit(X_all[tr], y[tr]); fold_acc.append(accuracy_score(y[te], m.predict(X_all[te])))
fit = model().fit(X_all, y)
t0 = time.perf_counter()
for row in X_all[:200]:
    fit.predict(row.reshape(1, -1))
t_inf = (time.perf_counter() - t0) / 200 * 1e3
print("3 fitur: acc %.4f  F1 %.4f  AUC %.4f  per-fold %s  inferensi %.2f ms/sampel"
      % (main["acc"], main["f1"], main["auc"], np.round(fold_acc, 4), t_inf))
print("confusion [Normal, Diabetes]:\n", main["cm"])

# --- ablasi fitur ---
SUBSETS = [("Fruktosamin", ["Vfru_V"]), ("Glukosa", ["Vglu_V"]), ("pH", ["VpH_V"]),
           ("Glukosa + pH", ["Vglu_V", "VpH_V"]), ("Ketiga fitur", list(FEAT))]
abl = []
for name, cols in SUBSETS:
    r = evaluate(cols); abl.append((name, r)); print("  %-14s acc %.4f F1 %.4f AUC %.4f" % (name, r["acc"], r["f1"], r["auc"]))

# --- uji split waktu: latih 60% awal rekaman tiap kelas, uji 40% akhir (cek autokorelasi) ---
df["urut"] = df.groupby("kelas").cumcount() / df.groupby("kelas").kelas.transform("size")
tr, te = df.urut < 0.6, df.urut >= 0.6
for name, cols in [("Glukosa + pH", ["Vglu_V", "VpH_V"]), ("Ketiga fitur", list(FEAT))]:
    m = model().fit(df.loc[tr, cols].values, y[tr]); yp = m.predict(df.loc[te, cols].values)
    print("  split waktu %-14s acc %.4f F1 %.4f" % (name, accuracy_score(y[te], yp), f1_score(y[te], yp, average="macro")))

# Gambar 12: distribusi tiap fitur per kelas (tiap titik = sampel)
fig, ax = plt.subplots(1, 3, figsize=(6.6, 2.8))
rng = np.random.default_rng(0)
for a, (c, n) in zip(ax, FEAT.items()):
    scale = 1 if c == "Vfru_V" else 1e3
    vals = [df.loc[df.kelas == k, c].values * scale for k in FILES]
    bp = a.boxplot(vals, widths=.5, showfliers=False, patch_artist=True, medianprops=dict(color="k"))
    for patch, k in zip(bp["boxes"], FILES):
        patch.set(facecolor=COLOR[k], alpha=.25, edgecolor=COLOR[k])
    for i, (v, k) in enumerate(zip(vals, FILES), 1):
        a.scatter(i + rng.uniform(-.18, .18, len(v)), v, s=3, alpha=.35, color=COLOR[k])
    a.set_xticks([1, 2]); a.set_xticklabels(list(FILES))
    a.set_title(n, fontsize=10); a.set_ylabel("Tegangan (%s)" % ("V" if scale == 1 else "mV"))
    a.grid(axis="y", alpha=.25)
fig.tight_layout(); fig.savefig(os.path.join(BASE, "gambar12_distribusi_sampel.png"))

# Gambar 13: confusion matrix 5-fold CV
fig, ax = plt.subplots(figsize=(3.3, 3.0))
cm = main["cm"]
ax.imshow(cm, cmap="Blues")
for i in range(2):
    for j in range(2):
        ax.text(j, i, "%d\n(%.1f%%)" % (cm[i, j], 100 * cm[i, j] / cm[i].sum()), ha="center", va="center",
                color="white" if cm[i, j] > cm.max() / 2 else "black")
ax.set_xticks([0, 1]); ax.set_xticklabels(list(FILES)); ax.set_yticks([0, 1]); ax.set_yticklabels(list(FILES))
ax.set_xlabel("Prediksi"); ax.set_ylabel("Kelas sebenarnya")
ax.spines[:].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(BASE, "gambar13_confusion_matrix.png"))

# Gambar 14: batas keputusan SVM pada dua pasangan fitur
fig, ax = plt.subplots(1, 2, figsize=(6.6, 3.0))
for a, (cx, cy) in zip(ax, [("Vfru_V", "Vglu_V"), ("Vglu_V", "VpH_V")]):
    X2 = df[[cx, cy]].values; m = model().fit(X2, y)
    pad = lambda v: (v.min() - .1 * np.ptp(v), v.max() + .1 * np.ptp(v))
    gx, gy = np.meshgrid(np.linspace(*pad(X2[:, 0]), 300), np.linspace(*pad(X2[:, 1]), 300))
    z = m.predict_proba(np.c_[gx.ravel(), gy.ravel()])[:, 1].reshape(gx.shape)
    sx = 1 if cx == "Vfru_V" else 1e3
    a.contourf(gx * sx, gy * 1e3, z, levels=[0, .5, 1], colors=[COLOR["Normal"], COLOR["Diabetes"]], alpha=.12)
    a.contour(gx * sx, gy * 1e3, z, levels=[.5], colors="k", linewidths=1)
    for k in FILES:
        s = df.kelas == k
        a.scatter(df.loc[s, cx] * sx, df.loc[s, cy] * 1e3, s=6, alpha=.6, color=COLOR[k], label="Kelas " + k)
    a.set_xlabel("%s (%s)" % (FEAT[cx], "V" if sx == 1 else "mV")); a.set_ylabel("%s (mV)" % FEAT[cy])
    a.grid(alpha=.2)
ax[0].legend(frameon=False, fontsize=8, loc="upper left")
for a, s in zip(ax, "ab"):
    a.text(-0.18, 1.02, "(%s)" % s, transform=a.transAxes, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(BASE, "gambar14_batas_keputusan.png"))

# Gambar 15: ablasi fitur
fig, ax = plt.subplots(figsize=(5.4, 2.9))
xx = np.arange(len(abl)); w = .38
ax.bar(xx - w / 2, [r["acc"] * 100 for _, r in abl], w, label="Akurasi", color="#4C72B0")
ax.bar(xx + w / 2, [r["f1"] * 100 for _, r in abl], w, label="Macro F1", color="#55A868")
for i, (_, r) in enumerate(abl):
    ax.text(i - w / 2, r["acc"] * 100 + 1, "%.1f" % (r["acc"] * 100), ha="center", fontsize=7)
    ax.text(i + w / 2, r["f1"] * 100 + 1, "%.1f" % (r["f1"] * 100), ha="center", fontsize=7)
ax.set_xticks(xx); ax.set_xticklabels([n for n, _ in abl], fontsize=8)
ax.set_ylim(0, 108); ax.set_ylabel("Skor (%)"); ax.grid(axis="y", alpha=.25)
ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(.5, 1.0), ncol=2, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(BASE, "gambar15_ablasi_fitur.png"))
