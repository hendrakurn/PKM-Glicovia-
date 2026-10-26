"""Pelatihan AI pada data optimal (SIMULASI): tegangan (Vfru, Vglu, VpH) -> pH, fruktosamin, glukosa saliva (SVR),
lalu tegangan -> kelas Normal / Pre-Diabetes / Diabetes (SVM). Evaluasi leave-one-session-out (LOSO).

Pre-Diabetes hanya punya 1 sesi lengkap, jadi 3 sesi simulasi tambahan dibuat dengan generator yang sama
(sesi_prediabetes_ekstra/). Semua hasil mencerminkan desain data simulasi, BUKAN kinerja pada alat.

Jalankan: ../../../ml_pipeline/.venv/bin/python latih_ai_optimal.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import confusion_matrix, f1_score, mean_absolute_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR

HERE = Path(__file__).resolve().parent
OPT = HERE.parent
sys.path.insert(0, str(OPT))
import buat_data_optimal as bdo  # noqa: E402  (generator data optimal + rumus main.cpp)

T0, WIN = 15.0, 5.0          # buang transien awal 15 s (tau 5 s), jendela 5 s
KELAS = ["Normal", "Pre-Diabetes", "Diabetes"]
WARNA = {"Normal": "#0072B2", "Pre-Diabetes": "#009E73", "Diabetes": "#D55E00"}
FITUR = [("VpH_V", "pH"), ("Vfru_V", "Fruktosamin"), ("Vglu_V", "Glukosa")]
TARGET = [("pH", "pH", ""), ("fructosamine_umol_L", "Fruktosamin", "µmol/L"), ("salivary_glucose_mgdL", "Glukosa saliva", "mg/dL")]

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                    "savefig.dpi": 300, "savefig.bbox": "tight"})

# ---------- 1. kumpulkan sesi ----------
sesi = {}
for p in sorted((OPT / "sesi").glob("*_optimal.csv")):
    d = pd.read_csv(p)
    if len(d) < 40:
        continue
    k = "Pre-Diabetes" if "PRE-DIABETES" in p.name else "Diabetes" if "DIABETES" in p.name else "Normal"
    sesi[p.name.replace("_optimal.csv", "")] = (k, d)

extra_dir = HERE / "sesi_prediabetes_ekstra"
extra_dir.mkdir(exist_ok=True)
for i, dur in enumerate([100.0, 120.0, 140.0], 1):          # 3 sesi simulasi tambahan
    rng = np.random.default_rng(1000 + i)
    t = np.arange(0.194, dur, 0.423)
    asli = pd.DataFrame({"waktu_iso": pd.date_range("2026-10-22T09:00:00", periods=len(t), freq="423ms").strftime("%Y-%m-%dT%H:%M:%S.%f").str[:-3],
                         "t_detik": t.round(3), "Vmid_V": (0.9110 + rng.normal(0, 0.0009, len(t))).round(4)})
    nama = f"contoh_PRE-DIABETES_ekstra_{i}"
    d = bdo.optimal_session(asli, "PRE-DIABETES", nama)
    d.to_csv(extra_dir / f"{nama}_optimal.csv", index=False)
    sesi[nama] = ("Pre-Diabetes", d)

rows = []
for sid, (k, d) in sesi.items():
    d = d[d.t_detik >= T0].copy()
    d["w"] = ((d.t_detik - T0) // WIN).astype(int)
    g = d.groupby("w").agg(VpH_V=("VpH_V", "mean"), Vfru_V=("Vfru_V", "mean"), Vglu_V=("Vglu_V", "mean"),
                           pH=("pH", "mean"), fructosamine_umol_L=("fructosamine_umol_L", "mean"),
                           salivary_glucose_mgdL=("salivary_glucose_mgdL", "mean"), n=("t_detik", "size"), t=("t_detik", "mean"))
    rows.append(g[g.n >= 9].assign(sesi=sid, kelas=k))
W = pd.concat(rows, ignore_index=True)
for c, _ in FITUR:
    W[c] *= 1e3                                            # mV
W.to_csv(HERE / "dataset_jendela.csv", index=False)
print("sesi:", W.groupby("kelas").sesi.nunique().to_dict(), "| jendela:", W.kelas.value_counts().to_dict(), "| total", len(W))

# ---------- Tabel: tegangan dan nilai per kelas ----------
print("\nTabel 1: tegangan (mV) dan nilai riil per kelas, rerata ± SD antar-jendela")
tab = []
for k in KELAS:
    s = W[W.kelas == k]
    row = {"kelas": k, "sesi": s.sesi.nunique()}
    for c, n in FITUR + [(t[0], t[1]) for t in TARGET]:
        row[c] = "%.1f ± %.1f" % (s[c].mean(), s[c].std()) if c.startswith("V") else "%.2f ± %.2f" % (s[c].mean(), s[c].std())
    tab.append(row)
T1 = pd.DataFrame(tab); print(T1.to_string(index=False)); T1.to_csv(HERE / "tabel1_per_kelas.csv", index=False)

# ---------- 2. AI tahap 1: tegangan -> pH, fruktosamin, glukosa (SVR vs regresi linear) ----------
X = W[[c for c, _ in FITUR]].to_numpy()
g = W.sesi.to_numpy()
y_cls = W.kelas.map({k: i for i, k in enumerate(KELAS)}).to_numpy()


def svr():
    return TransformedTargetRegressor(make_pipeline(StandardScaler(), SVR(kernel="rbf", C=100, gamma="scale", epsilon=0.01)),
                                      transformer=StandardScaler())


def lin():
    return make_pipeline(StandardScaler(), LinearRegression())


pred = {}
print("\nTabel 2: regresi tegangan -> nilai riil (LOSO)")
res = []
for col, nama, sat in TARGET:
    y = W[col].to_numpy()
    for mk, mf in (("SVR-RBF", svr), ("Regresi linear", lin)):
        p = np.empty(len(W))
        for s in np.unique(g):
            te = g == s
            p[te] = mf().fit(X[~te], y[~te]).predict(X[te])
        if mk == "SVR-RBF":
            pred[col] = p
        res.append({"parameter": f"{nama} {('('+sat+')') if sat else ''}".strip(), "model": mk,
                    "MAE": mean_absolute_error(y, p), "R2": r2_score(y, p), "rentang": y.max() - y.min()})
R = pd.DataFrame(res); print(R.round(4).to_string(index=False)); R.to_csv(HERE / "tabel2_regresi_loso.csv", index=False)

# ---------- 3. AI tahap 2: tegangan -> kelas (SVM, 3 kelas) ----------
pc = np.empty(len(W), int)
for s in np.unique(g):
    te = g == s
    pc[te] = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1, gamma="scale")).fit(X[~te], y_cls[~te]).predict(X[te])
acc = (pc == y_cls).mean(); f1 = f1_score(y_cls, pc, average="macro"); cm = confusion_matrix(y_cls, pc)
print(f"\nSVM 3 kelas LOSO: akurasi {acc:.3f}  macro-F1 {f1:.3f}\n{cm}")
per = {s: round((pc[g == s] == y_cls[g == s]).mean(), 2) for s in np.unique(g)}
print("akurasi per sesi (terendah):", min(per.values()))
# ablasi: fitur tunggal
for c, n in FITUR:
    i = [x[0] for x in FITUR].index(c); p = np.empty(len(W), int)
    for s in np.unique(g):
        te = g == s
        p[te] = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1, gamma="scale")).fit(X[~te][:, [i]], y_cls[~te]).predict(X[te][:, [i]])
    print(f"  hanya {n}: akurasi {(p == y_cls).mean():.3f}")

# ---------- Gambar A: tegangan per kelas terhadap waktu ----------
fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.8))
for a, (c, n) in zip(ax, FITUR):
    for s, d in W.groupby("sesi"):
        a.plot(d.t, d[c], color=WARNA[d.kelas.iloc[0]], lw=.9, alpha=.8)
    a.set_xlabel("Waktu (s)"); a.set_ylabel(f"Tegangan {n} (mV)"); a.grid(alpha=.25, lw=.4)
for k in KELAS: ax[0].plot([], [], color=WARNA[k], label=k)
h, l = ax[0].get_legend_handles_labels(); fig.legend(h, l, frameon=False, fontsize=8, loc="upper center", ncol=3)
for a, s in zip(ax, "abc"): a.text(-0.2, 1.02, "(%s)" % s, transform=a.transAxes, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93]); fig.savefig(HERE / "ai_gambar_A_volt_per_kelas.png"); plt.close(fig)

# ---------- Gambar B: alur pelatihan ----------
fig, a = plt.subplots(figsize=(7.4, 2.2)); a.axis("off"); a.set_xlim(0, 100); a.set_ylim(0, 30)
kotak = [(1, "Tegangan sensor\n(VpH, Vfru, Vglu)"), (21, "Standardisasi\nfitur"), (41, "SVR-RBF\n(tahap 1)"),
         (61, "pH, fruktosamin,\nglukosa saliva"), (81, "SVM-RBF\n(tahap 2)")]
for x, tx in kotak:
    a.add_patch(FancyBboxPatch((x, 12), 16, 10, boxstyle="round,pad=0.3", fc="#eef3f8", ec="#355070"))
    a.text(x + 8, 17, tx, ha="center", va="center", fontsize=7.5)
for x in (17.6, 37.6, 57.6, 77.6):
    a.add_patch(FancyArrowPatch((x, 17), (x + 2.8, 17), arrowstyle="-|>", mutation_scale=9, color="#355070"))
a.add_patch(FancyArrowPatch((89, 11.4), (89, 7.6), arrowstyle="-|>", mutation_scale=9, color="#355070"))
a.text(89, 4.6, "Kelas: Normal / Pre-Diabetes / Diabetes", ha="center", va="center", fontsize=7.5)
a.text(50, 27, "Validasi: leave-one-session-out (satu sesi diuji, sesi lain melatih)", ha="center", fontsize=8.5, style="italic")
fig.savefig(HERE / "ai_gambar_B_alur_pelatihan.png"); plt.close(fig)

# ---------- Gambar C: prediksi AI vs nilai rumus ----------
fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.7))
for a, (col, n, sat) in zip(ax, TARGET):
    y = W[col].to_numpy(); r = R[(R.model == "SVR-RBF")].reset_index(drop=True)
    for k in KELAS:
        m = (W.kelas == k).to_numpy()
        a.scatter(y[m], pred[col][m], s=8, color=WARNA[k], alpha=.7, lw=0)
    lo, hi = y.min(), y.max(); a.plot([lo, hi], [lo, hi], "k--", lw=.8)
    row = R[(R.model == "SVR-RBF") & R.parameter.str.startswith(n)].iloc[0]
    a.set_xlabel(f"{n} rumus {('('+sat+')') if sat else ''}".strip()); a.set_ylabel("Prediksi AI")
    a.text(.05, .93, f"MAE {row.MAE:.3g}\nR² {row.R2:.3f}", transform=a.transAxes, va="top", fontsize=8)
for k in KELAS: ax[0].scatter([], [], s=12, color=WARNA[k], label=k)
h, l = ax[0].get_legend_handles_labels(); fig.legend(h, l, frameon=False, fontsize=8, loc="upper center", ncol=3)
for a, s in zip(ax, "abc"): a.text(-0.25, 1.02, "(%s)" % s, transform=a.transAxes, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93]); fig.savefig(HERE / "ai_gambar_C_prediksi_vs_rumus.png"); plt.close(fig)

# ---------- Gambar D: confusion matrix ----------
fig, a = plt.subplots(figsize=(3.4, 3.0))
a.imshow(cm, cmap="Blues")
for i in range(3):
    for j in range(3):
        a.text(j, i, cm[i, j], ha="center", va="center", color="w" if cm[i, j] > cm.max() / 2 else "k")
a.set_xticks(range(3), KELAS, rotation=20); a.set_yticks(range(3), KELAS)
a.set_xlabel("Prediksi"); a.set_ylabel("Sebenarnya"); a.spines[["top", "right"]].set_visible(True)
fig.tight_layout(); fig.savefig(HERE / "ai_gambar_D_confusion.png"); plt.close(fig)
