#!/usr/bin/env python3
"""
Glicovia Sensor Serial Logger
Merekam data streaming dari ESP32 langsung ke file .csv.

Penggunaan:
    python3 log_sensor.py
    python3 log_sensor.py -l "uji_pH_4.01"
    python3 log_sensor.py -p /dev/ttyUSB0 -l "uji_saliva_01"
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


DEFAULT_HEADER = "timestamp_ms,Glukosa_Raw,Glukosa_Volt,pH_Raw,pH_Volt,Fruktosamin_Raw,Fruktosamin_Volt"


def find_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = p.description or ""
        dev = p.device or ""
        if any(keyword in dev or keyword in desc for keyword in ["USB", "ACM", "CP210", "CH340"]):
            return p.device
    if os.path.exists("/dev/ttyUSB0"):
        return "/dev/ttyUSB0"
    if os.path.exists("/dev/ttyUSB1"):
        return "/dev/ttyUSB1"
    return None


def main():
    parser = argparse.ArgumentParser(description="Glicovia Sensor CSV Logger")
    parser.add_argument("-p", "--port", type=str, default=None, help="Serial port (contoh: /dev/ttyUSB0, COM3)")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("-l", "--label", type=str, default="sample", help="Label pengujian (contoh: buffer_pH4.01, saliva_01)")
    parser.add_argument("-d", "--duration", type=int, default=0, help="Durasi logging dalam detik (0 = manual via Ctrl+C)")
    parser.add_argument("-o", "--outdir", type=str, default="data_log", help="Folder penyimpanan file CSV")

    args = parser.parse_args()

    port = args.port or find_esp32_port()
    if not port:
        print("ERROR: Port ESP32 tidak terdeteksi secara otomatis. Gunakan argumen -p untuk menentukan port secara manual.")
        sys.exit(1)

    os.makedirs(args.outdir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_label = args.label.replace(" ", "_")
    filename = os.path.join(args.outdir, f"glicovia_{clean_label}_{timestamp}.csv")

    print("\n" + "=" * 50)
    print("        GLICOVIA SERIAL DATA LOGGER")
    print("=" * 50)
    print(f"Port Serial  : {port} @ {args.baud} baud")
    print(f"Label Sampel : {args.label}")
    print(f"File Output  : {filename}")
    if args.duration > 0:
        print(f"Durasi Maks  : {args.duration} detik")
    else:
        print("Durasi       : Kontinu (Tekan Ctrl+C untuk berhenti)")
    print("=" * 50 + "\n")

    try:
        ser = serial.Serial(port, args.baud, timeout=1.0)
    except serial.SerialException as e:
        print(f"Gagal membuka port {port}: {e}")
        print("Tips: Pastikan Serial Monitor di Arduino IDE atau aplikasi lain sudah ditutup!")
        sys.exit(1)

    # Bersihkan buffer awal
    ser.reset_input_buffer()

    header_written = False
    row_count = 0
    start_time = time.time()

    with open(filename, "w", encoding="utf-8") as f:
        try:
            print("Merekam data streaming... (menunggu data dari ESP32)\n")
            while True:
                if args.duration > 0 and (time.time() - start_time) >= args.duration:
                    print(f"\nDurasi {args.duration} detik tercapai.")
                    break

                line_raw = ser.readline()
                if not line_raw:
                    continue

                line = line_raw.decode("utf-8", errors="ignore").strip()

                # Lewati baris kosong atau pesan teks inisialisasi
                if not line or line.startswith("---") or line.startswith("#") or "ADS1115" in line or "Peringatan" in line:
                    continue

                # Cek jika baris adalah header dari ESP32
                if "timestamp_ms" in line or "Glukosa" in line or "Volt" in line:
                    if not header_written:
                        f.write(line + "\n")
                        f.flush()
                        header_written = True
                        print(f"[HEADER DITERIMA] {line}")
                    continue

                parts = line.split(",")
                # Pastikan baris data memiliki 7 kolom (waktu, 3x ADC raw, 3x Volt)
                if len(parts) == 7:
                    if not header_written:
                        f.write(DEFAULT_HEADER + "\n")
                        f.flush()
                        header_written = True
                        print(f"[DEFAULT HEADER DITULIS] {DEFAULT_HEADER}")

                    f.write(line + "\n")
                    f.flush()
                    row_count += 1

                    elapsed = time.time() - start_time
                    print(f"\r[DATA #{row_count:04d} | {elapsed:5.1f}s] {line}    ", end="", flush=True)

        except KeyboardInterrupt:
            print("\n\nLogging dihentikan oleh pengguna (Ctrl+C).")

    ser.close()
    print(f"\nSelesai! {row_count} baris data berhasil disimpan ke:\n  --> {os.path.abspath(filename)}\n")


if __name__ == "__main__":
    main()
