#!/usr/bin/env python3
"""
Rekam output firmware diagnostik (kodeDaffa/diagnostik.cpp) ke CSV + tampil di terminal.
Baris yang diparse:
  raw=-22972  Vfru=0.0000 V  Vglu=0.0000 V  VpH=1.8176 V  Vmid=0.9131 V  I= 7178.75 nA  errI2C=0  | JENUH -> ...
Hanya stdlib, Linux. Baris lain (boot, hasil mode ukur 'm') hanya ditampilkan, tidak masuk CSV.

Penggunaan:
    python3 simpan_diagnostik.py
    python3 simpan_diagnostik.py -l saliva -d 60
    python3 simpan_diagnostik.py -p /dev/ttyUSB1 -o data_log
"""

import argparse
import os
import re
import select
import subprocess
import sys
import time
from datetime import datetime

NUM = r"(-?\d+(?:\.\d+)?)"
PAT = re.compile(
    rf"raw=\s*{NUM}\s+Vfru={NUM}\s*V\s+Vglu={NUM}\s*V\s+VpH={NUM}\s*V\s+Vmid={NUM}\s*V"
    rf"\s+I=\s*{NUM}\s*nA\s+errI2C={NUM}\s*\|\s*(.*)"
)
HEADER = "waktu_iso,t_detik,raw,Vfru_V,Vglu_V,VpH_V,Vmid_V,I_nA,errI2C,status"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", default="/dev/ttyUSB0")
    ap.add_argument("-b", "--baud", default="115200")
    ap.add_argument("-l", "--label", default="diag")
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
        out.write(HEADER + "\n")
        try:
            while not args.duration or time.time() - start < args.duration:
                if not select.select([ser], [], [], 1.0)[0]:
                    continue
                buf += ser.read(4096)
                *lines, buf = buf.split(b"\n")
                for raw in lines:
                    line = raw.decode("utf-8", errors="ignore").strip()
                    m = PAT.search(line)
                    if not m:  # boot, hasil mode ukur, baris partial
                        if line:
                            print(line)
                        continue
                    *nums, status = m.groups()
                    row = (f"{datetime.now().isoformat(timespec='milliseconds')},"
                           f"{time.time() - start:.3f},{','.join(nums)},{status.replace(',', ';')}")
                    out.write(row + "\n")
                    out.flush()
                    print(row)
                    n += 1
        except KeyboardInterrupt:
            pass
    print(f"\nSelesai: {n} baris -> {os.path.abspath(path)}")


if __name__ == "__main__":
    sys.exit(main())
