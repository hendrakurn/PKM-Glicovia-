#!/usr/bin/env python3
"""
Simpan data realtime firmware (baris "Glu:x<TAB>Fru:y<TAB>pH:z") ke CSV + tampil di terminal.
Hanya stdlib, Linux.

Penggunaan:
    python3 simpan_realtime.py
    python3 simpan_realtime.py -l saliva -d 60
    python3 simpan_realtime.py -p /dev/ttyUSB1 -o data_log
"""

import argparse
import os
import re
import select
import subprocess
import sys
import time
from datetime import datetime

PAT = re.compile(r"Glu:\s*(-?[\d.]+)\s+Fru:\s*(-?[\d.]+)\s+pH:\s*(-?[\d.]+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", default="/dev/ttyUSB0")
    ap.add_argument("-b", "--baud", default="115200")
    ap.add_argument("-l", "--label", default="sample")
    ap.add_argument("-d", "--duration", type=float, default=0, help="detik, 0 = sampai Ctrl+C")
    ap.add_argument("-o", "--outdir", default="data_log")
    args = ap.parse_args()

    subprocess.run(["stty", "-F", args.port, args.baud, "raw", "-echo"], check=True)

    os.makedirs(args.outdir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(args.outdir, f"glicovia_{args.label}_{stamp}.csv")

    start = time.time()
    n = 0
    buf = b""
    print(f"Merekam {args.port} -> {path} (Ctrl+C untuk berhenti)")
    with open(args.port, "rb", buffering=0) as ser, open(path, "w", encoding="utf-8") as out:
        out.write("waktu_iso,t_detik,glukosa_V,fruktosa_V,pH_V\n")
        try:
            while not args.duration or time.time() - start < args.duration:
                if not select.select([ser], [], [], 1.0)[0]:
                    continue
                buf += ser.read(4096)
                *lines, buf = buf.split(b"\n")
                for raw in lines:
                    m = PAT.search(raw.decode("utf-8", errors="ignore"))
                    if not m:  # baris error / partial / boot message
                        continue
                    now = time.time()
                    row = f"{datetime.now().isoformat(timespec='milliseconds')},{now - start:.3f},{m[1]},{m[2]},{m[3]}"
                    out.write(row + "\n")
                    out.flush()
                    print(row)
                    n += 1
        except KeyboardInterrupt:
            pass
    print(f"\nSelesai: {n} baris -> {os.path.abspath(path)}")


if __name__ == "__main__":
    sys.exit(main())
