# 📊 Master Plan: Persiapan Data & Alat Referensi PKM-KC
**Proyek:** Deteksi Gula Darah Non-Invasif Berbasis Saliva (Glukosa, pH, Viskositas)  
**Fase:** Pengumpulan Data Klinis (Ground Truth)  
**Status:** Persiapan Eksekusi  

---

## 1. 🎯 Tujuan Fase Ini
Mendapatkan dataset berkualitas tinggi yang terdiri dari pasangan data:
- **Input:** 3 parameter saliva (Glukosa Saliva, pH, Viskositas) yang diukur dengan alat referensi terkalibrasi.
- **Label/Target:** Gula darah kapiler aktual (mg/dL) + Kategori Klinis (Normal/Pre-Diabetes/Diabetes).

> ⚠️ **PRINSIP UTAMA:** Data ini adalah fondasi AI. Prototipe cartridge PKM **DILARANG** digunakan sebagai alat ukur referensi pada fase ini. Gunakan hanya alat standar lab/medis yang tervalidasi.

---

## 2. 🛒 Daftar Alat Referensi Wajib (Shopping List)

| Parameter | Alat Referensi | Spesifikasi Minimum | Estimasi Harga | Sumber |
| :--- | :--- | :--- | :--- | :--- |
| **Gula Darah** | Glucometer Medis + Strip | Akurasi ±5%, ISO 15197:2013 | Rp 150rb–300rb + strip | Apotek (Accu-Chek, OneTouch, Nesco) |
| **pH Saliva** | pH Meter Digital Pen Type | Resolusi 0.01, ATC (Auto Temp Compensation) | Rp 80rb–250rb | Marketplace (ATC, Hanna clone) |
| **Viskositas** | Ostwald Viscometer / Pipet Kapiler | Volume 1-2 mL, diameter konsisten | Rp 30rb–150rb | Toko alat lab kimia/gelas |
| **Glukosa Saliva** | Glucose Assay Kit (Colorimetric) | Sensitivitas ≤0.1 mg/dL, range 0-10 mg/dL | Rp 600rb–1.5jt | Supplier lab biokimia (Sigma, Abcam, lokal) |
| **Spektrofotometer** | UV-Vis Spectrophotometer | Panjang gelombang 450-540nm | **PINJAM LAB KAMPUS** | Lab Biokimia/Kimia Analitik FK/FMIPA |
| **Sampling** | Tabung Steril Bergradasi + Spatula Lidah | Volume min 2mL, steril, disposable | Rp 2rb–5rb/pcs | Toko alkes/lab |
| **Keamanan** | Safety Box + Sarung Tangan + Alkohol Swab | Standar medis | Rp 50rb–100rb | Apotek / Alkes |

### ⚠️ Catatan Kritis Glukosa Saliva
Kadar glukosa saliva 50-100x lebih rendah dari darah. Strip glucometer biasa **TIDAK AKAN BISA** membacanya. **WAJIB** menggunakan Glucose Assay Kit + Spektrofotometer. Jika kampus tidak memiliki spektrofotometer, cari lab mitra atau sewa jasa uji eksternal.

---

## 3. 🔬 Protokol Validasi & Kalibrasi Alat
Sebelum sampling dimulai, setiap alat harus melewati uji validasi berikut. Dokumentasikan hasilnya untuk lampiran laporan PKM.

### A. Glucometer Medis
- [ ] Cek sertifikat & tanggal kadaluarsa strip.
- [ ] Uji dengan larutan kontrol glukosa. Deviasi harus <5% dari nilai referensi botol.
- [ ] (Opsional tapi disarankan) Cross-check 5-10 sampel dengan hasil lab klinik (venous plasma).

### B. pH Meter Digital
- [ ] Kalibrasi 3 titik (buffer pH 4.01, 7.00, 10.01) sebelum SETIAP sesi sampling.
- [ ] Ukur buffer pH 7.00 sebanyak 5x berturut-turut. Standar deviasi harus <0.05.
- [ ] Elektroda disimpan dalam larutan KCl 3M, **BUKAN air murni**.

### C. Viskometer (Flow Time Method)
- [ ] Ukur waktu alir aquades pada suhu kamar sebanyak 5x sebagai baseline.
- [ ] Ukur larutan gliserol-air (konsentrasi tetap) sebanyak 5x. Coefficient of Variation (CV) harus <5%.
- [ ] Catat suhu ruangan setiap pengukuran. Fluktuasi >2°C wajib gunakan water bath.

### D. Glucose Assay Kit + Spektrofotometer
- [ ] Buat kurva standar (0, 0.5, 1, 2, 5, 10 mg/dL) setiap batch assay baru. R² ≥ 0.99.
- [ ] Jalankan blanko (reagen tanpa sampel) untuk koreksi background.
- [ ] Recovery Test: Tambahkan known glucose ke saliva, recovery rate harus 80-120%.

---

## 4. 📋 SOP Pengambilan Sampel (Ringkasan Eksekutif)
*Versi lengkap SOP sudah tersedia di dokumen terpisah.*

1.  **Pra-Sampling:** Subjek puasa min. 2 jam + berkumur air putih 3x + istirahat duduk 5 menit. Informed consent wajib ditandatangani.
2.  **Gula Darah:** Tusuk jari → buang tetesan pertama → ambil tetesan kedua → catat mg/dL + kategori. Tekan luka hingga berhenti. Buang lancet ke safety box.
3.  **Saliva:** Saliva dikumpulkan pasif di dasar mulut 1-2 menit → dikeluarkan ke tabung steril bergradasi → target min 2 mL. Simpan di cooler box (4°C, maks 2 jam).
4.  **Ukur Parameter:** pH (celup, aduk, baca) → Viskositas (flow time, ulang 2x, rata-rata) → Glukosa (assay kit sesuai protokol).
5.  **Pasca-Sampling:** Input data ke spreadsheet → backup cloud → bersihkan alat → buang limbah medis.

---

## 5. 🗂️ Struktur Database & Manajemen Data

### Template Spreadsheet (`Dataset_Saliva_Glukosa_PKM2026.xlsx`)
| Kolom | Tipe | Validasi |
| :--- | :--- | :--- |
| `subject_id` | Text | Format SUB-001 (anonim) |
| `sampling_date` | Date | YYYY-MM-DD |
| `sampling_time` | Time | HH:MM |
| `fasting_hours` | Number | ≥ 2 |
| `bg_reference_mgdl` | Number | Gula darah kapiler |
| `bg_category` | Text | Normal / Pre-Diabetes / Diabetes |
| `saliva_ph` | Decimal | Range 4.0–9.0 |
| `saliva_viscosity_sec` | Decimal | detik/mL atau cP |
| `saliva_glucose_mgdl` | Decimal | Range 0.1–10.0 |
| `proto_*_raw` | Decimal | Opsional: bacaan mentah prototipe |
| `notes` | Text | Anomali/kondisi khusus |
| `operator_initials` | Text | Traceability |

### Aturan Emas
- **Anonimitas Total:** Mapping ID↔nama di file terpisah yang dipassword.
- **Backup Harian:** Upload ke cloud setiap selesai sesi.
- **Validasi Input:** Gunakan Data Validation di Excel untuk mencegah typo.

---

## 6. 🔄 Strategi Paralel (Agar Tidak Idle)

Sementara menunggu alat tiba & ethical clearance terbit:

| Tim | Aktivitas Paralel | Output |
| :--- | :--- | :--- |
| Hardware | Prototype Reader v1 (breadboard) + uji sensor bare dengan sampel buatan | Firmware dasar baca 3 sensor |
| Software | Setup Next.js + Supabase + Prisma + Auth + Dashboard UI dummy | Website skeleton siap integrasi |
| AI/Data | Literatur review + setup Python env + script EDA pipeline | Environment training siap |
| Admin | Draft laporan kemajuan PKM + dokumentasi persiapan | Bab 1-3 draft laporan |

---

## 7. ⚡ Action Plan Minggu Pertama

- [ ] **Hari 1-2:** Order pH meter, viskometer, tabung steril, safety box. Hubungi lab kampus untuk pinjam spektrofotometer.
- [ ] **Hari 3:** Beli glucometer medis + strip + larutan kontrol di apotek.
- [ ] **Hari 4:** Cari supplier Glucose Assay Kit (distributor Sigma/Merck lokal atau marketplace).
- [ ] **Hari 5:** Kalibrasi awal semua alat yang sudah tiba. Dokumentasikan.
- [ ] **Hari 6-7:** Dry run SOP lengkap dengan tim. Evaluasi & revisi SOP.

---

## 8. ⚠️ Risk Management

| Risiko | Mitigasi |
| :--- | :--- |
| Ethical clearance terlambat >8 minggu | Ajukan ASAP; plan B sampling internal (dosen/staf) sebagai subjek awal |
| Sensor glukosa saliva tidak sensitif | Siapkan 2 metode (assay kit + strip urine modifikasi); konsultasi lab fakultas |
| Cartridge bocor/saluran tersumbat | Buat 3x cadangan; uji cairan berwarna dulu sebelum saliva asli |
| Data tidak cukup untuk training AI | Turunkan kompleksitas model (Ridge Regression); fokus klasifikasi 3 kelas |
| ESP32-S3 stok habis | Beli SEKARANG; backup ESP32-WROOM-32E sebagai plan B |
| Spektrofotometer tidak tersedia | Sewa jasa uji eksternal (Sucofindo/Balai POM ~Rp 50-100rb/sampel) |

---

*Dokumen ini merupakan living document. Perbarui setiap kali ada perubahan spesifikasi alat, revisi SOP, atau penyesuaian timeline.*
*Terakhir diperbarui: Juni 2026*