"""Hasil & Pembahasan v2: 9 rekaman firmware terbaru di hardware/data_log (4 Normal, 5 Diabetes).
Pra-proses: buang 30 s awal (transien), rata-rata jendela 5 s (redam osilasi alias ~2,5 s) -> 1 jendela = 1 sampel.
Evaluasi SVM RBF: (a) 5-fold stratified acak, (b) leave-one-session-out (LOSO).
Jalankan: ../../../ml_pipeline/.venv/bin/python buat_grafik_v2.py
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
from sklearn.model_selection import StratifiedKFold, LeaveOneGroupOut, cross_val_predict
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, roc_auc_score

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "..", "..", "data_log")
# (kode sesi, kelas, file) — urut waktu
SESI = [
    ("N1", "Normal", "glicovia_88_NORMAL_20261021_045627.csv"),
    ("N2", "Normal", "glicovia_88_NORMAL_backup_20261021_050022.csv"),
    ("N3", "Normal", "glicovia_88_NORMAL_backup_2_20261021_050247.csv"),
    ("N4", "Normal", "glicovia_88_NORMAL_backup_3_20261021_050732.csv"),
    ("D1", "Diabetes", "glicovia_DIABETES_20261021_030626.csv"),
    ("D2", "Diabetes", "glicovia_DIABETES_backup_20261021_032137.csv"),
    ("D3", "Diabetes", "glicovia_148_DIABETES_backup_2_20261021_043540.csv"),
    ("D4", "Diabetes", "glicovia_DIABETES_1_20261022_090334.csv"),
    ("D5", "Diabetes", "glicovia_DIABETES_1_1_20261022_090602.csv"),
]
KELAS = ["Normal", "Diabetes"]
COLOR = {"Normal": "#0072B2", "Diabetes": "#D55E00"}
FEAT = {"Vfru_V": "Fruktosamin", "Vglu_V": "Glukosa", "VpH_V": "pH"}
T_TRANSIEN, WIN = 30.0, 5.0

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "font.size": 10, "axes.labelsize": 10, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 300, "savefig.bbox": "tight",
})
save = lambda fig, n: fig.savefig(os.path.join(BASE, n))

raw, win = {}, []
for kode, kelas, fn in SESI:
    d = pd.read_csv(os.path.join(LOG, fn))
    raw[kode] = d
    s = d[d.t_detik >= T_TRANSIEN].copy()
    s["w"] = ((s.t_detik - T_TRANSIEN) // WIN).astype(int)
    g = s.groupby("w").agg({**{c: "mean" for c in FEAT}, "t_detik": ["count", "mean"]})
    g.columns = list(FEAT) + ["n", "t"]
    g = g[g.n >= 0.8 * WIN / 0.423]  # buang jendela terakhir yang terpotong
    win.append(g.assign(sesi=kode, kelas=kelas, jenuh=(s.status.str.startswith("JENUH")).mean()))
W = pd.concat(win, ignore_index=True)
y = (W.kelas == "Diabetes").astype(int).values
groups = W.sesi.values

# --- Tabel sesi ---
print("Tabel sesi (median fase stabil, mV):")
tab = W.groupby("sesi", sort=False).agg(kelas=("kelas", "first"), jendela=("n", "size"),
                                         **{FEAT[c]: (c, "median") for c in FEAT}, jenuh=("jenuh", "first"))
tab["durasi_s"] = [raw[k].t_detik.iloc[-1] - raw[k].t_detik.iloc[0] for k in tab.index]
for c in FEAT.values():
    tab[c] = (tab[c] * 1e3).round(1)
tab["jenuh"] = (tab.jenuh * 100).round(0)
print(tab.to_string())
print("Total jendela:", W.kelas.value_counts().to_dict())

model = lambda: make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1.0, gamma="scale"))
SKF = StratifiedKFold(5, shuffle=True, random_state=42)
LOSO = LeaveOneGroupOut()

def evaluate(cols, cv):
    X = W[cols].values
    kw = dict(groups=groups) if cv is LOSO else {}
    s = cross_val_predict(model(), X, y, cv=cv, method="decision_function", **kw)
    yp = (s > 0).astype(int)
    return dict(acc=accuracy_score(y, yp), f1=f1_score(y, yp, average="macro"),
                auc=roc_auc_score(y, s), cm=confusion_matrix(y, yp), yp=yp)

SUBSETS = [("Fruktosamin", ["Vfru_V"]), ("Glukosa", ["Vglu_V"]), ("pH", ["VpH_V"]),
           ("Glukosa + pH", ["Vglu_V", "VpH_V"]), ("Ketiga fitur", list(FEAT))]
hasil = {}
print("\n%-17s | %-24s | %-24s" % ("Fitur", "5-fold acak acc/F1/AUC", "LOSO acc/F1/AUC"))
for name, cols in SUBSETS:
    a, b = evaluate(cols, SKF), evaluate(cols, LOSO)
    hasil[name] = (a, b)
    print("%-17s | %.3f %.3f %.3f        | %.3f %.3f %.3f" % (name, a["acc"], a["f1"], a["auc"], b["acc"], b["f1"], b["auc"]))
main_skf, main_loso = hasil["Ketiga fitur"]
print("\nAkurasi LOSO per sesi (ketiga fitur):")
for k in tab.index:
    m = groups == k
    print("  %s (%s): %.0f%%" % (k, tab.kelas[k], 100 * (main_loso["yp"][m] == y[m]).mean()))
fit = model().fit(W[list(FEAT)].values, y)
x1 = W[list(FEAT)].values[:1]
t0 = time.perf_counter()
for _ in range(500):
    fit.predict(x1)
print("Inferensi: %.2f ms/sampel (PC)" % ((time.perf_counter() - t0) / 500 * 1e3))

# Gambar 9: respons waktu sesi representatif (mentah + rata-rata jendela)
fig, ax = plt.subplots(3, 1, figsize=(6.3, 6.4), sharex=True)
for a, (c, n) in zip(ax, FEAT.items()):
    for kode in ["N1", "D1"]:
        d, k = raw[kode], ("Normal" if kode[0] == "N" else "Diabetes")
        a.plot(d.t_detik, d[c] * 1e3, color=COLOR[k], lw=.5, alpha=.35)
        w = W[W.sesi == kode]
        a.plot(w.t, w[c] * 1e3, "o-", color=COLOR[k], ms=2.5, lw=1.2, label="%s (sesi %s)" % (k, kode))
    a.axvspan(0, T_TRANSIEN, color="grey", alpha=.1, lw=0)
    a.set_ylabel("%s (mV)" % n); a.grid(alpha=.25)
ax[2].set_ylim(0, 120); ax[1].set_ylim(0, 8)
ax[0].legend(frameon=False, loc="center right")
ax[0].text(2, ax[0].get_ylim()[1] * .9, "transien", color="grey", fontsize=8)
ax[-1].set_xlabel("Waktu (s)")
for a, s in zip(ax, "abc"):
    a.text(-0.12, 1.0, "(%s)" % s, transform=a.transAxes, fontweight="bold")
fig.tight_layout(); save(fig, "gambar9_respons_waktu.png")

# Gambar 10: sebaran per sesi (boxplot jendela) tiap kanal
fig, ax = plt.subplots(1, 3, figsize=(6.8, 2.9))
kodes = list(tab.index)
for a, (c, n) in zip(ax, FEAT.items()):
    vals = [W.loc[W.sesi == k, c].values * 1e3 for k in kodes]
    bp = a.boxplot(vals, widths=.6, showfliers=False, patch_artist=True, medianprops=dict(color="k", lw=1))
    for p, k in zip(bp["boxes"], kodes):
        kl = tab.kelas[k]; p.set(facecolor=COLOR[kl], alpha=.55, edgecolor=COLOR[kl])
    a.set_xticks(range(1, len(kodes) + 1)); a.set_xticklabels(kodes, fontsize=7, rotation=90)
    a.set_title(n, fontsize=10); a.set_ylabel("Tegangan (mV)"); a.grid(axis="y", alpha=.25)
    if c != "VpH_V":
        a.set_yscale("log")
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=COLOR[k], alpha=.55, label=k) for k in KELAS], frameon=False,
           ncol=2, loc="upper center", bbox_to_anchor=(.5, 1.06))
fig.tight_layout(); save(fig, "gambar10_sebaran_per_sesi.png")

# Gambar 11: ruang fitur fruktosamin vs pH, marker per sesi
fig, ax = plt.subplots(figsize=(4.6, 3.6))
MK = "osD^v"
for k in kodes:
    w, kl = W[W.sesi == k], tab.kelas[k]
    ax.scatter(w.Vfru_V * 1e3, w.VpH_V * 1e3, s=16, marker=MK[int(k[1]) - 1], facecolor="none",
               edgecolor=COLOR[kl], lw=.9, label=k)
ax.set_xscale("log"); ax.set_xlabel("Tegangan fruktosamin (mV, log)"); ax.set_ylabel("Tegangan pH (mV)")
ax.grid(alpha=.25); ax.legend(frameon=False, ncol=3, fontsize=7, loc="upper left")
fig.tight_layout(); save(fig, "gambar11_ruang_fitur.png")

# Gambar 12: confusion matrix 5-fold acak vs LOSO
fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.9))
gp_loso = hasil["Glukosa + pH"][1]
for a, (r, judul) in zip(ax, [(main_skf, "(a) Ketiga fitur, 5-fold acak"), (main_loso, "(b) Ketiga fitur, LOSO"),
                              (gp_loso, "(c) Glukosa + pH, LOSO")]):
    cm = r["cm"]; a.imshow(cm, cmap="Blues", vmin=0, vmax=cm.sum(1).max())
    for i in range(2):
        for j in range(2):
            a.text(j, i, "%d\n(%.1f%%)" % (cm[i, j], 100 * cm[i, j] / cm[i].sum()), ha="center", va="center",
                   fontsize=9, color="white" if cm[i, j] > cm.sum(1).max() / 2 else "black")
    a.set_xticks([0, 1]); a.set_xticklabels(KELAS); a.set_yticks([0, 1]); a.set_yticklabels(KELAS)
    a.set_xlabel("Prediksi"); a.set_title("%s\nakurasi %.1f%%" % (judul, r["acc"] * 100), fontsize=9)
    a.spines[:].set_visible(False)
ax[0].set_ylabel("Kelas sebenarnya")
fig.tight_layout(); save(fig, "gambar12_confusion_matrix.png")

# Gambar 13: akurasi tiap kombinasi fitur, 5-fold acak vs LOSO
fig, ax = plt.subplots(figsize=(6.0, 3.0))
xx, wd = np.arange(len(SUBSETS)), .38
for off, idx, lab, col in [(-wd / 2, 0, "5-fold stratified acak", "#9DB4D3"), (wd / 2, 1, "Leave-one-session-out", "#2F5D8A")]:
    v = [hasil[n][idx]["acc"] * 100 for n, _ in SUBSETS]
    ax.bar(xx + off, v, wd, color=col, label=lab)
    for x, vv in zip(xx + off, v):
        ax.text(x, vv + 1, "%.1f" % vv, ha="center", fontsize=7)
ax.axhline(50, color="grey", ls=":", lw=1); ax.text(-.6, 51.5, "tebakan acak", fontsize=7, color="grey", ha="left")
ax.set_xticks(xx); ax.set_xticklabels([n for n, _ in SUBSETS], fontsize=8)
ax.set_ylim(0, 110); ax.set_ylabel("Akurasi (%)"); ax.grid(axis="y", alpha=.25)
ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(.5, 1.0))
fig.tight_layout(); save(fig, "gambar13_akurasi_fitur.png")
