"""Grafik Hasil dan Pembahasan artikel Glicovia (Gambar 9-11) dari rekaman sensor dua kelas."""
import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(BASE, "..", "backup")
FILES = {
    "Normal": "glicovia_88_NORMAL_20261021_045627.csv",
    "Diabetes": "glicovia_148_DIABETES_20261021_030626.csv",
}
COLOR = {"Normal": "#0072B2", "Diabetes": "#D55E00"}
CH = [("Vfru_V", "Fruktosamin"), ("Vglu_V", "Glukosa"), ("VpH_V", "pH")]
T_STABIL = 60.0  # detik; sebelum ini = fase transien/pembasahan elektroda

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "font.size": 10, "axes.labelsize": 10, "legend.fontsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 300, "savefig.bbox": "tight",
})

def load(fn):
    with open(os.path.join(BACKUP, fn)) as f:
        r = list(csv.DictReader(f))
    return {k: np.array([float(x[k]) for x in r]) for k in r[0] if k not in ("waktu_iso", "status")}

D = {k: load(v) for k, v in FILES.items()}

def settle(t, v, frac=0.95):
    """Waktu pertama sinyal masuk dan bertahan dalam +-(1-frac)*|final-awal| dari nilai akhir."""
    fin = v[t >= T_STABIL].mean()
    band = (1 - frac) * abs(fin - v[0]) if abs(fin - v[0]) > 0 else 1e-9
    out = np.abs(v - fin) > band
    idx = np.where(out)[0]
    return t[min(idx[-1] + 1, len(t) - 1)] if len(idx) else t[0]

print("Statistik fase stabil (t >= %.0f s)" % T_STABIL)
for k, d in D.items():
    m = d["t_detik"] >= T_STABIL
    print(k, "n=%d" % m.sum())
    for c, n in CH:
        v = d[c][m]
        print("  %-11s mean %.4f sd %.4f cv %.2f%%  settle95 %.1f s" % (
            n, v.mean(), v.std(ddof=1), 100 * v.std(ddof=1) / abs(v.mean()) if v.mean() else 0,
            settle(d["t_detik"], d[c])))

# Gambar 9: respons waktu
fig, ax = plt.subplots(3, 1, figsize=(6.3, 6.2), sharex=True)
for a, (c, n) in zip(ax, CH):
    for k, d in D.items():
        a.plot(d["t_detik"], d[c], color=COLOR[k], lw=1.3, label="Kelas " + k)
    a.axvline(T_STABIL, color="grey", ls=":", lw=1)
    a.set_ylabel("%s (V)" % n)
    a.grid(alpha=.25)
ax[0].legend(frameon=False, loc="center left")
ax[0].text(T_STABIL + 2, ax[0].get_ylim()[1] * 0.08, "fase stabil", color="grey", fontsize=8)
ax[-1].set_xlabel("Waktu (s)")
for a, s in zip(ax, "abc"):
    a.text(-0.1, 1.0, "(%s)" % s, transform=a.transAxes, fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(BASE, "gambar9_respons_waktu.png"))

# Gambar 10: rata-rata +- SD fase stabil
fig, ax = plt.subplots(1, 3, figsize=(6.5, 2.7))
for a, (c, n) in zip(ax, CH):
    for i, (k, d) in enumerate(D.items()):
        v = d[c][d["t_detik"] >= T_STABIL]
        a.bar(i, v.mean(), yerr=v.std(ddof=1), color=COLOR[k], capsize=4, width=.6)
    a.set_xticks([0, 1]); a.set_xticklabels(list(D))
    a.set_title(n, fontsize=10); a.set_ylabel("Tegangan (V)")
    a.grid(axis="y", alpha=.25)
fig.tight_layout()
fig.savefig(os.path.join(BASE, "gambar10_rerata_fase_stabil.png"))

# Gambar 11: ruang fitur fruktosamin vs glukosa (fase stabil)
fig, ax = plt.subplots(figsize=(4.2, 3.6))
for k, d in D.items():
    m = d["t_detik"] >= T_STABIL
    ax.scatter(d["Vfru_V"][m], d["Vglu_V"][m] * 1e3, s=9, alpha=.6, color=COLOR[k], label="Kelas " + k)
ax.set_xlabel("Tegangan fruktosamin (V)"); ax.set_ylabel("Tegangan glukosa (mV)")
ax.grid(alpha=.25); ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(BASE, "gambar11_ruang_fitur.png"))
