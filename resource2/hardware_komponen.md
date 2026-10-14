# Spesifikasi Perancangan Perangkat Keras (Glicovia)

## 1. Sistem

**Permasalahan Saat Ini:**
Alat sebelumnya gagal dalam tahap pengujian/testing. Vendor diminta untuk membuat dan memastikan rangkaian elektronik (terutama bagian *Analog Front-End* dan *I2C Communication*) berjalan dengan stabil, presisi tinggi, dan minim *noise*.

---

## 2. Daftar Komponen Utama

Berdasarkan *source code* dan dokumentasi rancangan, komponen-komponen yang digunakan adalah:

1. **Mikrokontroler:** **ESP32** (mengelola WiFi, MQTT, I2C, dan logika utama).
2. **Sensor & Elektroda:** **SPCE (Screen-Printed Carbon Electrode)**.
3. **Analog Front-End (AFE):** **OPA2333** (Op-Amp presisi tinggi untuk *signal conditioning* / pengkondisian sinyal dari elektroda SPCE). *Catatan: Sebelumnya menggunakan LMP91000 namun direvisi ke OPA2333.*
4. **Analog-to-Digital Converter (ADC):** **ADS1115** (16-bit ADC, sangat sensitif untuk mengonversi sinyal analog presisi dari OPA2333 ke digital).
5. **Layar / Display:** **OLED SH1106G (128x64)** (antarmuka pengguna lokal).

---

## 3. Konfigurasi Pin dan Komunikasi (Firmware)

Semua perangkat periferal berkomunikasi ke ESP32 melalui protokol **I2C**. Firmware menggunakan pin default I2C ESP32 (SDA = GPIO 21, SCL = GPIO 22).

* **OLED SH1106G:**
  - I2C Address: `0x3C`
  - Resolusi: 128x64
  - Reset Pin: Tidak menggunakan pin khusus (menggunakan `-1` di code).
* **ADC ADS1115:**
  - I2C Address: Default (umumnya `0x48` jika pin ADDR dihubungkan ke GND).
  - Mode Pembacaan: *Single-Ended* (Pin A0, A1, A2 digunakan terpisah).
  - Gain: `GAIN_ONE` (Batas tegangan ±4.096V).
* **Pemetaan Sinyal ADC (ADS1115):**
  - **A0:** Salivary Glucose (Glukosa Saliva)
  - **A1:** pH
  - **A2:** Fructosamine (Fruktosamin)

---

## 4. Referensi File dan Sumber Daya Tersedia

Vendor dapat diberikan akses ke file-file berikut untuk keperluan referensi dan dimensi fisik:

- `main.cpp`: Kode sumber firmware ESP32 lengkap (termasuk inisialisasi I2C, pembacaan ADC, dan pengiriman MQTT).
- `pkm_handheld_casing_v2.blend`: File desain 3D untuk *casing handheld* (menentukan dimensi PCB atau penempatan layar OLED dan sensor).
- `diagrams/pkm-komponen.png`: Diagram komponen alat.
- `diagrams/cara_kerja_singkat_alat_flowchart.excalidraw`: Flowchart cara kerja.
