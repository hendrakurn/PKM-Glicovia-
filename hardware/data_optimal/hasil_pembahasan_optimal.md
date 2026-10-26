# Draf Hasil dan Pembahasan — Percobaan Data Optimal (SIMULASI)

> **Catatan penempatan.** Data pada bagian ini dibuat dari invers rumus konversi `main.cpp`, bukan hasil
> ukur. Tempatkan sebagai sub-bab **"Validasi Rumus Konversi dan Target Kondisi Optimal Sensor"** setelah
> sub-bab data log asli, dan sebut jelas sebagai simulasi. Jangan dipakai sebagai bukti kinerja alat.
> Semua angka di bawah dihasilkan `analisis_korelasi.py` (kalibrasi masih sementara, `provisional-2026-10-22`).

## 1. Hubungan tegangan dengan nilai biomarka (Gambar: `korelasi_volt_satuan.png`)

Tegangan tiap kanal dikonversi ke satuan riil dengan rumus pada firmware. Regresi linear pada 400 baris
(40 sampel terakhir × 10 sesi) menghasilkan korelasi |r| ≈ 1,00 untuk ketiga parameter, dengan sensitivitas:

| Parameter | Kanal | Sensitivitas (hasil regresi) | Nilai teoritis rumus | Resolusi ADC* |
|---|---|---|---|---|
| pH | VpH (A2) | −59,16 mV/pH | −59,16 mV/pH (Nernst) | ≈ 0,002 pH |
| Fruktosamin | Vfru (A0) | −3,51 mV per µmol/L | −3,5 mV (`FRU_A`·Rf) | ≈ 0,04 µmol/L |
| Glukosa saliva | Vglu (A1−A3) | −100,4 mV per mg/dL | −100 mV (`GLU_A`·Rf) | ≈ 0,0003 mg/dL |

\*LSB ADS1115: 0,125 mV (GAIN_ONE) untuk pH dan fruktosamin, 31,25 µV (GAIN_FOUR) untuk glukosa.

**Pembahasan.** Korelasi sempurna di sini **bukan temuan empiris**: data optimal diturunkan dari rumus yang
sama sehingga hubungannya pasti linear. Yang bernilai adalah (a) bukti bahwa implementasi konversi konsisten
dengan rumus (kemiringan regresi = kemiringan teoretis; juga diverifikasi dengan mengompilasi blok `CALC`
`main.cpp`), dan (b) besaran sensitivitasnya. Kanal pH hanya memberi **66 mV** antara Normal dan Diabetes
(−0,089 vs −0,023 V), sedangkan fruktosamin 439 mV dan glukosa 274 mV. Jadi pH paling rentan terhadap
offset dan drift elektroda: galat offset 0,13 V saja menggeser pH sekitar 2,2 satuan.

## 2. Perbandingan tegangan log asli dan kondisi optimal (Gambar: `volt_asli_vs_optimal.png`)

| Kanal | Kelas | Rerata asli (V) | Rerata optimal (V) | Selisih (V) |
|---|---|---|---|---|
| VpH | Normal | 0,047 | −0,089 | −0,136 |
| VpH | Diabetes | 0,090 | −0,023 | −0,113 |
| Vfru | Normal | 0,557 | 0,549 | −0,007 |
| Vfru | Diabetes | 0,029 | 0,110 | +0,081 |
| Vglu | Normal | 0,004 | 0,840 | +0,836 |
| Vglu | Diabetes | 0,009 | 0,566 | +0,557 |

**Pembahasan.**
- **Vglu** adalah selisih terbesar. Pada log asli Vout glukosa menempel di ≈ 0 V (status `JENUH`, arus ≈ 7160 nA),
  sedangkan kondisi optimal ada di 0,57–0,84 V dengan arus 0,7–3,5 µA. Kanal glukosa masih jenuh dan belum
  bisa dipakai.
- **Vfru** untuk Normal sudah dekat nilai optimal (selisih < 10 mV), sehingga kanal ini paling siap.
  Diabetes asli menempel di ≈ 0 V, tepat di batas atas bacaan rumus (375 µmol/L pada VMID ≈ 0,913 V),
  jadi nilai fruktosamin Diabetes pada data asli terbaca saturasi.
- **VpH** asli bernilai **positif** (0,00–0,19 V), sedangkan rumus menuntut nilai **negatif** untuk pH saliva
  fisiologis (VpH = 0 V ↔ pH 5,45). Konsekuensinya pH asli terbaca 4,0–5,4. Ini menandakan perlunya
  pengukuran pH terhadap VMID (diferensial A2−A3) atau kalibrasi ulang offset.

## 3. Korelasi antar-parameter (Gambar: `korelasi_matriks.png`, Spearman, n = 10 sesi)

- Ketiga biomarka berkorelasi kuat dengan referensi glukosa darah: |ρ| = 0,90 (pH negatif; fruktosamin dan
  glukosa positif).
- Antar-biomarka: pH–fruktosamin ρ = −0,81, pH–glukosa −0,81, fruktosamin–glukosa +0,71. Artinya ketiganya
  searah menunjukkan tingkat metabolik yang sama, tetapi informasinya tumpang-tindih sehingga manfaat
  tambahan tiap parameter terhadap SVM perlu diuji (uji ablasi fitur sudah ada di `gambar15_ablasi_fitur.png`).

**Keterbatasan:** referensi glukosa darah hanya tiga nilai (88/112/148 mg/dL) yang ditetapkan dari kelas, bukan
hasil glukometer per sampel, dan n = 10 sesi. Korelasi ini menggambarkan *arah target*, bukan kekuatan
hubungan sebenarnya.

## 4. Pemisahan kelas Normal vs Diabetes

| Parameter | Normal | Diabetes | Cohen's d |
|---|---|---|---|
| pH | 6,96 ± 0,04 | 5,85 ± 0,12 | 11,8 |
| Fruktosamin (µmol/L) | 218 ± 7 | 343 ± 8 | 16,2 |
| Glukosa saliva (mg/dL) | 0,74 ± 0,07 | 3,46 ± 0,15 | 22,6 |

Nilai d yang sangat besar muncul karena variasi antar-sesi pada simulasi sengaja kecil. Pada data nyata
yang noisier, d akan jauh lebih rendah; gunakan angka ini hanya sebagai batas atas ideal. Pemisahan di
domain volt dan domain satuan setara (d volt 11,7–23,0 vs d satuan 11,8–22,6) karena transformasinya linear;
konversi ke satuan riil tidak menambah daya pembeda, hanya membuat hasil dapat dibaca klinisi.

## 5. Contoh kalimat siap pakai

> Simulasi kondisi optimal menunjukkan bahwa konversi tegangan ke satuan riil bersifat linear dengan
> sensitivitas −59,16 mV/pH, −3,51 mV per µmol/L fruktosamin, dan −100,4 mV per mg/dL glukosa saliva, sesuai
> parameter firmware. Dibandingkan data log asli, kanal fruktosamin Normal sudah mendekati kondisi optimal
> (selisih < 10 mV), sedangkan kanal glukosa masih jenuh (Vout ≈ 0 V dibanding 0,57–0,84 V pada kondisi
> optimal) dan kanal pH menunjukkan offset positif 0,11–0,14 V. Hasil ini menjadi target optimasi
> rangkaian dan kalibrasi pada tahap selanjutnya, bukan bukti kinerja klasifikasi.

## Rekomendasi tindak lanjut (urut prioritas)
1. Perbaiki kanal pH: ukur diferensial terhadap VMID atau fit ulang offset dari buffer 4,01 / 6,86 / 9,18.
2. Atasi saturasi kanal glukosa (turunkan gain/Rf, cek bias WE–RE) hingga status `OK`.
3. Ambil ulang sesi Pre-Diabetes (≥ 60 s + 40 sampel, GDP 100–125 mg/dL).
4. Gantikan referensi kelas dengan glukosa darah per sampel (glukometer) untuk korelasi yang sah.
