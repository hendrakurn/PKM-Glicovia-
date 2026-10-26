#!/usr/bin/env python3
"""
Simpan output serial ke file, setara: stty -F /dev/ttyUSB0 115200 raw && cat /dev/ttyUSB0
Tanpa pyserial (hanya stdlib).

Penggunaan:
    python3 simpan_serial.py
    python3 simpan_serial.py -l pH_7.00 -d 60
    python3 simpan_serial.py -p /dev/ttyUSB1 -o data_log
"""

import argparse
import os
import select
import subprocess
import sys
import time
from datetime import datetime


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", default="/dev/ttyUSB0")
    ap.add_argument("-b", "--baud", default="115200")
    ap.add_argument("-l", "--label", default="serial")
    ap.add_argument("-d", "--duration", type=float, default=0, help="detik, 0 = sampai Ctrl+C")
    ap.add_argument("-o", "--outdir", default="data_log")
    args = ap.parse_args()

    subprocess.run(["stty", "-F", args.port, args.baud, "raw"], check=True)

    os.makedirs(args.outdir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(args.outdir, f"glicovia_{args.label}_{stamp}.csv")

    start = time.time()
    n = 0
    buf = b""
    print(f"Merekam {args.port} -> {path} (Ctrl+C untuk berhenti)")
    with open(args.port, "rb", buffering=0) as ser, open(path, "w", encoding="utf-8") as out:
        try:
            while not args.duration or time.time() - start < args.duration:
                if not select.select([ser], [], [], 1.0)[0]:
                    continue
                buf += ser.read(4096)
                *lines, buf = buf.split(b"\n")
                for raw in lines:
                    line = raw.decode("utf-8", errors="ignore").strip()
                    if line:
                        print(line)
                        out.write(line + "\n")
                        out.flush()
                        n += 1
        except KeyboardInterrupt:
            pass
    print(f"\nSelesai: {n} baris -> {os.path.abspath(path)}")


if __name__ == "__main__":
    sys.exit(main())
