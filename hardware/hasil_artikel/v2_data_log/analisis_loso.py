"""Klasifikasi SVM-RBF 2 kelas dengan leave-one-session-out (LOSO) pada 174 pengambilan data (jendela 5 s,
setelah transien 30 s). Menghasilkan Gambar 11 (ablasi + confusion matrix) dan angka untuk Tabel 1-2.
Jalankan: ../../../ml_pipeline/.venv/bin/python analisis_loso.py
"""
import os
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "..", "..", "data_log")
SESI = [("Normal", f) for f in ["glicovia_88_NORMAL_20261021_045627.csv", "glicovia_88_NORMAL_backup_20261021_050022.csv",
                                "glicovia_88_NORMAL_backup_2_20261021_050247.csv", "glicovia_88_NORMAL_backup_3_20261021_050732.csv"]] + \
       [("Diabetes", f) for f in ["glicovia_DIABETES_20261021_030626.csv", "glicovia_DIABETES_backup_20261021_032137.csv",
                                  "glicovia_148_DIABETES_backup_2_20261021_043540.csv", "glicovia_DIABETES_1_20261022_090334.csv",
                                  "glicovia_DIABETES_1_1_20261022_090602.csv"]]
FEAT = {"Vfru_V": "Fruktosamin", "Vglu_V": "Glukosa", "VpH_V": "pH"}
T0, WIN = 30.0, 5.0

# Sama dengan buat_grafik_ringkas.py
rows = []
for i, (kelas, fn) in enumerate(SESI):
    s = pd.read_csv(os.path.join(LOG, fn)); s = s[s.t_detik >= T0].copy()
    s["w"] = ((s.t_detik - T0) // WIN).astype(int)
    g = s.groupby("w").agg({**{c: "mean" for c in FEAT}, "t_detik": ["count", "mean"]}); g.columns = list(FEAT) + ["n", "t"]
    rows.append(g[g.n >= 0.8 * WIN / 0.423].assign(kelas=kelas, sesi=i))
W = pd.concat(rows, ignore_index=True)
for c in FEAT: W[c] *= 1e3  # mV
y = (W.kelas == "Diabetes").astype(int).to_numpy()
print("n =", len(W), W.kelas.value_counts().to_dict(), "| sesi:", W.groupby("kelas").sesi.nunique().to_dict())

print("\nTabel 1: median [Q1-Q3] (mV) per kelas")
for k in ("Normal", "Diabetes"):
    print(k, {FEAT[c]: "%.2f [%.2f-%.2f]" % tuple(np.percentile(W.loc[W.kelas == k, c], p) for p in (50, 25, 75)) for c in FEAT})


def loso(cols, log=True):
    X = W[cols].to_numpy()
    if log:  # rentang fruktosamin lintas 3 dekade -> log10 supaya standardisasi tidak didominasi satu kanal
        X = np.log10(np.clip(X, 1e-3, None))
    pred = np.empty(len(W), int)
    for s in W.sesi.unique():
        te = (W.sesi == s).to_numpy()
        m = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1, gamma="scale")).fit(X[~te], y[~te])
        pred[te] = m.predict(X[te])
    return pred


combos = [list(c) for r in (1, 2, 3) for c in itertools.combinations(FEAT, r)]
res = []
for cols in combos:
    p = loso(cols)
    per = [accuracy_score(y[(W.sesi == s).to_numpy()], p[(W.sesi == s).to_numpy()]) for s in W.sesi.unique()]
    res.append({"fitur": " + ".join(FEAT[c] for c in cols), "acc": accuracy_score(y, p), "f1": f1_score(y, p, average="macro"),
                "min_sesi": min(per), "sesi_gagal": sum(a < 0.5 for a in per)})
R = pd.DataFrame(res)
print("\nTabel 2: LOSO"); print(R.round(3).to_string(index=False))

p3 = loso(list(FEAT))
cm = confusion_matrix(y, p3)
print("\nConfusion matrix (baris=benar Normal,Diabetes; kolom=prediksi):\n", cm)
print("akurasi per sesi (3 fitur):", {SESI[s][1][9:-4][:22]: round(accuracy_score(y[(W.sesi == s).to_numpy()], p3[(W.sesi == s).to_numpy()]), 2) for s in W.sesi.unique()})

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                     "font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300, "savefig.bbox": "tight"})
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [2.3, 1]})
a = ax[0]
Rs = R.sort_values("acc")
a.barh(Rs.fitur, Rs.acc * 100, color="#0072B2", alpha=.75)
for i, v in enumerate(Rs.acc * 100): a.text(v + 1, i, "%.1f" % v, va="center", fontsize=8)
a.set_xlim(0, 112); a.set_xlabel("Akurasi LOSO (%)"); a.tick_params(axis="y", labelsize=8)
a.text(-0.02, 1.02, "(a)", transform=a.transAxes, fontweight="bold")
b = ax[1]
b.imshow(cm, cmap="Blues")
for i, j in itertools.product(range(2), range(2)):
    b.text(j, i, cm[i, j], ha="center", va="center", color="w" if cm[i, j] > cm.max() / 2 else "k")
b.set_xticks([0, 1], ["Normal", "Diabetes"]); b.set_yticks([0, 1], ["Normal", "Diabetes"])
b.set_xlabel("Prediksi"); b.set_ylabel("Sebenarnya"); b.spines[["top", "right"]].set_visible(True)
b.text(-0.35, 1.02, "(b)", transform=b.transAxes, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(BASE, "final_gambar11_ablasi_cm.png"))
