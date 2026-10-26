"""Bandingkan Normal vs Diabetes dalam satuan riil (pH, fruktosamin, glukosa saliva).
Sumber: ml_pipeline/data/real/generated_data_real.csv (kalibrasi SEMENTARA, lihat .meta.json).
Satu titik = satu sesi (median jendela); bar = rerata antar-sesi."""
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = Path(__file__).resolve().parents[2] / "ml_pipeline/data/real/generated_data_real.csv"
rows = list(csv.DictReader(open(SRC)))
sess = defaultdict(list)
for r in rows:
    sess[(r["bg_class"], r["session_id"])].append(r)

PANELS = [("ph_value", "pH saliva"), ("fructosamine_umol_l", "Salivary fructosamine (µmol/L)"),
          ("glucose_saliva", "Salivary glucose (mg/dL, kanal jenuh)")]
CLS = {"0": ("Normal", "#2a9d8f"), "2": ("Diabetes", "#e76f51")}

fig, ax = plt.subplots(1, 3, figsize=(11, 3.8))
for a, (col, lab) in zip(ax, PANELS):
    for i, (c, (name, color)) in enumerate(CLS.items()):
        meds = [st.median(float(r[col]) for r in v) for (cc, _), v in sess.items() if cc == c]
        sd = st.stdev(meds) if len(meds) > 1 else 0
        a.bar(i, st.mean(meds), yerr=sd, color=color, alpha=.35, capsize=5, width=.55)
        a.scatter([i + (k - len(meds) / 2) * .04 for k in range(len(meds))], meds, color=color, s=28, zorder=3)
        a.text(i, a.get_ylim()[0], f"n={len(meds)} sesi", ha="center", va="bottom", fontsize=8)
    a.set_xticks(range(2), [v[0] for v in CLS.values()])
    a.set_title(lab, fontsize=10)
    a.spines[["top", "right"]].set_visible(False)
fig.suptitle("Perbandingan Normal vs Diabetes (kalibrasi sementara)", fontsize=11)
fig.tight_layout()
fig.savefig(Path(__file__).with_name("perbandingan_kelas.png"), dpi=200)

for col, lab in PANELS:
    for c, (name, _) in CLS.items():
        m = [st.median(float(r[col]) for r in v) for (cc, _), v in sess.items() if cc == c]
        print(f"{col:22s} {name:9s} {st.mean(m):7.2f} ± {st.stdev(m):5.2f}  (n={len(m)})")
