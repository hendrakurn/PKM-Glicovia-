"""Grafik kecil "Input biomarker saliva" untuk slide: sinyal sensor nyata, Normal vs Diabetes.

Sumber: sesi alat nyata (hardware/DATA). Satu sesi per kelas, masing-masing dari 1 orang, jadi
ini menunjukkan bentuk sinyal, BUKAN bukti akurasi. Tiga PNG transparan, satu per kotak slide.

    .venv/bin/python diagrams/input_biomarker.py   ->  diagrams/input_{glukosa,fruktosamin,ph}.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

OUT = Path(__file__).resolve().parent
DATA = OUT.parents[1] / "hardware" / "DATA"
SESI = {"Normal (88 mg/dL)": ("glicovia_88_NORMAL_backup_3_20261021_050732.csv", "#2E7D32"),
        "Diabetes (148 mg/dL)": ("glicovia_148_DIABETES_backup_2_20261021_043540.csv", "#C62828")}
# kolom, berkas, skala ke satuan tampil, satuan
PANEL = [("Vglu_V", "glukosa", 1e3, "mV"), ("Vfru_V", "fruktosamin", 1.0, "V"), ("VpH_V", "ph", 1e3, "mV")]

df = {k: pd.read_csv(DATA / f) for k, (f, _) in SESI.items()}

for kol, nama, skala, unit in PANEL:
    fig, ax = plt.subplots(figsize=(3.6, 1.7))
    for label, d in df.items():
        t = d["t_detik"] - d["t_detik"].min()
        ax.plot(t, d[kol].rolling(12, center=True, min_periods=1).mean() * skala,
                color=SESI[label][1], lw=1.8, label=label)
    ax.set(xlabel="waktu (detik)", ylabel=f"sinyal ({unit})")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    ax.xaxis.label.set_size(8)
    ax.yaxis.label.set_size(8)
    if nama == "glukosa":
        ax.legend(fontsize=7, frameon=False, loc="center right")
    fig.tight_layout()
    fig.savefig(OUT / f"input_{nama}.png", dpi=300, transparent=True)
    plt.close(fig)
print("Disimpan: input_glukosa.png, input_fruktosamin.png, input_ph.png di", OUT)
