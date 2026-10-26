#!/usr/bin/env python3
"""
Kalibrasi pH dari CSV hasil log_sensor.py.

Penggunaan:
    python3 calibrate.py data_log/pH_4.01.csv:4.01 data_log/pH_7.00.csv:7.00 data_log/pH_10.01.csv:10.01
    python3 calibrate.py -w 10 -s 0.0015 ...   # jendela 10 detik, std maks 1.5 mV

Tiap argumen = file.csv:pH_buffer. Per file dicari jendela stabil terakhir,
lalu dirata-ratakan. Hasil fit dicetak sebagai konstanta C++ untuk firmware.
"""

import argparse
import csv
import sys

import numpy as np

SAMPLE_S = 0.25   # sampleInterval firmware (250 ms)
V_MAX = 1.0       # di atas ini = elektroda kering / mengambang, bukan sinyal pH


def read_volts(path):
    """Ambil kolom tegangan pH. Baris rusak (bukan 7 kolom / bukan angka) dibuang."""
    with open(path, encoding="utf-8", errors="ignore") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    # header baru punya pH_Volt; header lama: pH ada di A2 = kolom tegangan terakhir
    col = header.index("pH_Volt") if "pH_Volt" in header else 6
    volts = []
    for r in rows[1:]:
        if len(r) != 7:
            continue
        try:
            v = float(r[col])
        except ValueError:
            continue
        if 0.0 < v < V_MAX:
            volts.append(v)
    return np.array(volts)


def stable_mean(volts, window_s, max_std):
    """Rata-rata jendela terakhir yang std-nya < max_std dan tidak drift."""
    n = int(window_s / SAMPLE_S)
    for end in range(len(volts), n - 1, -1):
        w = volts[end - n:end]
        drift = abs(w[n // 2:].mean() - w[:n // 2].mean())
        if w.std() < max_std and drift < max_std:
            return w.mean(), w.std(), end - n
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("points", nargs="+", help="file.csv:pH")
    ap.add_argument("-w", "--window", type=float, default=15.0, help="lebar jendela stabil (detik)")
    ap.add_argument("-s", "--std", type=float, default=0.002, help="std maks jendela stabil (V)")
    args = ap.parse_args()

    ph, volt = [], []
    print(f"{'file':40s} {'pH':>6s} {'V_mean(mV)':>11s} {'std(mV)':>8s} {'mulai(idx)':>10s}")
    for p in args.points:
        path, _, buf = p.rpartition(":")
        v = read_volts(path)
        res = stable_mean(v, args.window, args.std)
        if res is None:
            sys.exit(f"{path}: tidak ada jendela stabil {args.window}s (std<{args.std*1000:.1f} mV). "
                     "Perpanjang rekaman atau longgarkan -s.")
        mean, std, start = res
        print(f"{path[-40:]:40s} {float(buf):6.2f} {mean*1000:11.2f} {std*1000:8.2f} {start:10d}")
        ph.append(float(buf))
        volt.append(mean)

    if len(set(ph)) < 2:
        sys.exit("Butuh minimal 2 buffer pH berbeda.")

    m, c = np.polyfit(ph, volt, 1)
    pred = m * np.array(ph) + c
    ss_tot = ((np.array(volt) - np.mean(volt)) ** 2).sum()
    r2 = 1 - ((np.array(volt) - pred) ** 2).sum() / ss_tot if len(ph) > 2 else float("nan")

    print(f"\nSlope m  = {m*1000:.2f} mV/pH  (ideal Nernst -59.16 mV/pH, {abs(m)/0.05916*100:.0f}%)")
    print(f"Offset c = {c*1000:.2f} mV")
    print(f"R^2      = {r2:.4f}" if len(ph) > 2 else "R^2      = n/a (2 titik)")
    if m >= 0:
        print("PERINGATAN: slope positif/nol -> sensor tidak merespons pH atau kabel salah.")
    elif not 0.040 <= abs(m) <= 0.065:
        print("PERINGATAN: slope di luar 40-65 mV/pH -> cek elektroda/referensi.")

    print("\n// --- tempel ke firmware ---")
    print(f"const float PH_SLOPE  = {m:.6f}f;  // V/pH")
    print(f"const float PH_OFFSET = {c:.6f}f;  // V")


if __name__ == "__main__":
    main()
