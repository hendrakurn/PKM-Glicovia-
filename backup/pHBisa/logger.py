#!/usr/bin/env python3
"""
Glicovia Serial Data Logger
Mencatat data CSV streaming dari ESP32 langsung ke file .csv di PC.
"""

import os
import sys
import time
import argparse
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: pyserial belum terpasang. Jalankan: pip install pyserial")
    sys.exit(1)


def find_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "USB" in p.device or "ACM" in p.device or "CP210" in p.description or "CH340" in p.description:
            return p.device
    if os.path.exists("/dev/ttyUSB0"):
        return "/dev/ttyUSB0"
    if os.path.exists("/dev/ttyUSB1"):
        return "/dev/ttyUSB1"
    return None


def main():
    parser = argparse.ArgumentParser(description="Glicovia Sensor Data Logger")
    parser.add_argument("-p", "--port", type=str, default=None, help="Serial port (contoh: /dev/ttyUSB0)")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("-l", "--label", type=str, default="sample", help="Label pengujian (contoh: pH_4.01, glukosa_5mM)")
    parser.add_argument("-d", "--duration", type=int, default=0, help="Durasi logging dalam detik (0 = tanpa batas, stop pakai Ctrl+C)")
    parser.add_argument("-o", "--outdir", type=str, default="data_log", help="Folder penyimpanan file CSV (default: data_log)")

    args = parser.parse_args()

    port = args.port or find_esp32_port()
    if not port:
        print("ERROR: Port ESP32 tidak ditemukan. Pastikan kabel USB terhubung.")
        sys.exit(1)

    os.makedirs(args.outdir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_label = args.label.replace(" ", "_")
    filename = os.path.join(args.outdir, f"glicovia_{clean_label}_{timestamp}.csv")

    print(f"\n========================================")
    print(f"      GLICOVIA DATA LOGGER (PC)")
    print(f"========================================")
    print(f"Port Serial : {port} @ {args.baud} baud")
    print(f"Label Uji   : {args.label}")
    print(f"Output File : {filename}")
    if args.duration > 0:
        print(f"Durasi      : {args.duration} detik")
    else:
        print(f"Durasi      : Kontinu (Tekan Ctrl+C untuk selesai)")
    print(f"========================================\n")

    try:
        ser = serial.Serial(port, args.baud, timeout=1.0)
    except serial.SerialException as e:
        print(f"Gagal membuka port {port}: {e}")
        print("Tip: Tutup Serial Monitor di Arduino IDE jika sedang terbuka!")
        sys.exit(1)

    # Bersihkan buffer serial awal
    ser.reset_input_buffer()

    header_written = False
    row_count = 0
    start_time = time.time()

    with open(filename, "w", encoding="utf-8") as f:
        try:
            print("Merekam data... (tunggu pembacaan dari ESP32)\n")
            while True:
                if args.duration > 0 and (time.time() - start_time) >= args.duration:
                    print(f"\nTarget durasi {args.duration} detik tercapai.")
                    break

                line_raw = ser.readline()
                if not line_raw:
                    continue

                try:
                    line = line_raw.decode("utf-8", errors="ignore").strip()
                except Exception:
                    continue

                # Filter baris non-data / teks boot
                if not line or line.startswith("---") or line.startswith("ADS") or line.startswith("ERROR") or line.startswith("Peringatan"):
                    continue

                # Cek jika baris adalah header
                if "Time_ms" in line or "Volt" in line:
                    if not header_written:
                        f.write(line + "\n")
                        f.flush()
                        header_written = True
                        print(f"[HEADER] {line}")
                    continue

                # Pastikan baris berisi data angka CSV
                parts = line.split(",")
                if len(parts) >= 6:
                    if not header_written:
                        # Buat default header jika belum lewat header
                        f.write("Time_ms,Raw_A0,Volt_Glukosa,Raw_A1,Volt_pH,Raw_A2,Volt_Fruktosa\n")
                        header_written = True

                    f.write(line + "\n")
                    f.flush()
                    row_count += 1

                    # Tampilkan live progress di terminal
                    elapsed = time.time() - start_time
                    print(f"\r[DATA #{row_count:04d} | {elapsed:5.1f}s] {line}    ", end="", flush=True)

        except KeyboardInterrupt:
            print("\n\nLogging dihentikan oleh user (Ctrl+C).")

    ser.close()
    print(f"\nSukses tersimpan: {row_count} baris data ke {filename}")


if __name__ == "__main__":
    main()
