# PRD SENSOR — Panduan Pengetahuan Sensor Glicovia

> Dokumen hidup (*living document*). Dipakai sebagai **konteks acuan untuk AI** dan anggota tim saat menjelaskan, menganalisis, atau memodifikasi sensor, rangkaian, data, dan model Glicovia.
> Bahasa: Indonesia. Satuan SI kecuali disebut lain.

## 0. Aturan Pakai (untuk AI)

1. Baca dokumen ini sebelum menjawab pertanyaan tentang sensor, AFE, data tegangan/arus, atau model SVM.
2. Bedakan tiga status klaim. Jangan menyatakan klaim bertanda `[BELUM TERVERIFIKASI]` atau `[SIMULASI]` sebagai fakta pengukuran.
   - `[KODE]`: diverifikasi dari kode atau dokumen proyek (sebut file sumbernya).
   - `[TEORI]`: pengetahuan elektrokimia umum, belum tentu persis seperti strip kalian.
   - `[BELUM TERVERIFIKASI]`: asumsi atau pertanyaan terbuka (lihat §10).
3. Jangan mengklaim kanal fruktosamin sebagai pengukuran fruktosamin sungguhan (lihat §6).
4. Data di `hardware/data_optimal/` adalah **simulasi**. Beri label "simulasi/ilustrasi target" bila dikutip.
5. Gaya jawaban ke pengguna: sederhana, bertahap, pakai contoh angka dari proyek.

### Cara memperbarui dokumen
- Pengetahuan baru masuk ke bagian yang relevan, bukan ditumpuk di akhir.
- Setiap perubahan dicatat di **§12 Catatan Perubahan** (tanggal, apa yang berubah, sumbernya).
- Bila fakta baru menggugurkan klaim lama, ubah klaim lamanya dan catat alasannya. Jangan biarkan dua versi bertentangan.
- Bila `[BELUM TERVERIFIKASI]` sudah terjawab, pindahkan jawabannya ke bagian terkait dan hapus dari §10.

---

## 1. Ringkasan Sistem

Glicovia adalah alat genggam yang membaca tiga parameter **saliva** memakai *Screen-Printed Carbon Electrode* (SPCE): **pH**, **glukosa saliva**, dan **fruktosamin**. Hasil dikonversi ke satuan riil, dikirim ke cloud, lalu model **SVM/SVR** memperkirakan kadar glukosa darah (mg/dL) dan kategori klinis (Normal / Prediabetes / Diabetes). `[KODE: PRD_Glicovia.md:14]`

**Rantai sinyal (inti):**

```
Saliva → reaksi di elektroda → ARUS (nA) / POTENSIAL → rangkaian AFE → TEGANGAN (V)
      → ADS1115 (ADC 16-bit) → rumus konversi → satuan riil (pH, µmol/L, mg/dL) → SVM
```

Dasar klinis alat: glukosa darah naik → glukosa saliva ikut naik. Hubungan ini punya variasi besar antar orang (laju saliva, makan/minum, kebersihan mulut), dan ini batas utama akurasi. `[TEORI]`

---

## 2. Prinsip Dasar: Arus vs Tegangan

| Pertanyaan | Jawaban |
|---|---|
| Output utama sensor glukosa/fruktosamin | **Arus** (nA–µA), sebanding dengan jumlah zat yang bereaksi |
| Output utama sensor pH | **Tegangan** (potensiometrik, Nernst) |
| Kenapa arus diubah ke tegangan | ADS1115 (dan ADC umumnya) **hanya membaca tegangan**. Arus harus dialirkan lewat resistor dulu |
| Kenapa tidak pakai sensor arus siap pakai (ACS712, INA219, resistor shunt) | Arus sensor hanya ~0,7–8 µA. Modul itu beresolusi mA. Shunt 1 Ω × 5 µA = 5 µV, di bawah resolusi ADS1115 |
| Solusi | **TIA** (transimpedance amplifier) dengan Rf besar (100 kΩ) |

Di firmware, tegangan dikonversi **kembali ke arus** (`I = (Vmid − Vout) / Rf`) sebelum dihitung jadi kadar.

Kalimat siap pakai untuk laporan: *"Arus sensor dikonversi menjadi tegangan oleh rangkaian TIA (Vout = Vmid − I·Rf), dibaca ADS1115, lalu dikonversi kembali menjadi arus melalui perhitungan."*

### 2.1 Kenapa harus lewat tegangan

ADC bekerja dengan membandingkan tegangan (pembanding dan kapasitor di dalamnya). Arus tetap bisa didigitalkan, tetapi **selalu diubah dulu ke tegangan**. Yang berbeda hanya tempatnya: di luar chip (rancangan Glicovia: OPA2333 + Rf) atau di dalam chip (lihat §2.3). `[TEORI]`

Analogi: timbangan hanya membaca berat. Mengukur air yang mengalir berarti menampungnya dulu di wadah (Rf), baru ditimbang (ADC).

### 2.2 Penurunan rumus `Vout = Vmid − I × Rf`

Rangkaian: masukan (+) OPA2333 diikat ke Vmid, masukan (−) menerima arus sensor, Rf dipasang dari keluaran ke masukan (−). `[TEORI]`

1. **Virtual short.** Umpan balik negatif membuat masukan (−) ikut berpotensial sama dengan (+), yaitu Vmid.
2. **Op-amp tidak menarik arus** (arus bias OPA2333 sangat kecil), jadi seluruh arus sensor `I` mengalir lewat Rf.
3. **Hukum Ohm pada Rf:** `I = (Vmid − Vout) / Rf`.
4. **Susun ulang:** `Vout = Vmid − I × Rf`.

Saat `I = 0`, `Vout = Vmid`. Vmid adalah **titik nol sinyal**. Arus menurunkan Vout dari titik itu, dan besar penurunannya = `I × Rf`.

**Analogi sederhana:** tangki air setinggi Vmid mengalir lewat pipa sempit (Rf). Makin banyak air mengalir (I), makin turun tinggi air di ujung pipa (Vout).

**Kenapa acuan Vmid, bukan 0 V:** suplai hanya 0–3,3 V. Dengan acuan 0 V, tegangan yang turun langsung menabrak rel bawah. Dengan acuan di tengah, sinyal bisa bergerak ke dua arah dan tetap terbaca ADC.

**Catatan polaritas:** tanda minus berlaku bila `I` positif didefinisikan sebagai arus yang mengalir **masuk** ke masukan (−). Bila arahnya terbalik, rumus menjadi `Vout = Vmid + I × Rf`. Polaritas nyata pada alat belum dibuktikan (lihat §10).

### 2.3 Alternatif komponen konversi arus → digital

`[TEORI]` — dari pengetahuan umum, **belum dievaluasi tim**. Cek datasheet sebelum memutuskan.

| Komponen | Fungsi | Catatan untuk Glicovia |
|---|---|---|
| LMP91000 (TI) | AFE potensiostat terprogram (TIA, bias WE–RE, pilihan Rf lewat I2C). Keluaran tegangan, tetap perlu ADC | Paling dekat dengan desain sekarang. Menggantikan OPA2333 + Rf + trimpot. Rf maksimum internal ≈ 350 kΩ. Alamat I2C setahu penulis 0x48, sama dengan ADS1115 (ADDR ke VDD → 0x49). **Cek datasheet** |
| AD5940 / AD5941 (Analog Devices) | AFE elektrokimia lengkap dengan ADC 16-bit terintegrasi, keluaran SPI | Menggantikan OPA2333 + ADS1115. Perubahan desain besar |
| ADuCM355 (Analog Devices) | MCU + potensiostat + ADC | Alat mandiri |
| DDC112 / DDC114 (TI) | ADC masukan arus (integrasi di kapasitor) | Untuk arus sangat kecil (pA–nA) |
| INA219 / INA226 | Pengukur arus dengan shunt | Hanya untuk arus besar (mA–A), tidak cocok untuk µA |

Mengganti komponen **tidak otomatis menyelesaikan** masalah Vmid dan kanal menempel ~0 V (§9). Perbaiki H-1 dan H-2 lebih dulu.

---

## 3. Perangkat Keras Terkait (AFE)

`[KODE: PRD_Glicovia.md §4.1]`

| Komponen | Spesifikasi |
|---|---|
| MCU | ESP32-DevKitC V4 (WROOM-32U). I2C: SDA=IO21, SCL=IO22 |
| ADC | ADS1115 (0x48), 16-bit. Firmware memakai GAIN_ONE ±4,096 V. Mode diferensial A1−A3 memakai GAIN_FOUR (±1,024 V, LSB = 1,024/32768 V) |
| Op-amp | **OPA2333** (3 buah). Op-amp presisi berderau rendah |
| Rf, Cf | Rf = 100 kΩ, Cf = 1,3 nF (TIA) |
| Bias WE–RE | Diatur trimpot RV1/RV2 dari VMID |
| VMID | Pembagi 10k/10k, nominal 1,65 V. **Terukur ≈ 0,913 V** (masalah, lihat §9) |
| Pin ADC | A0 = fruktosamin, A1 = glukosa, A2 = pH, A3 = VMID |
| Konektor sensor | JST 3-pin (WE, RE, CE) per kanal |

**TIA bukan satu chip.** TIA = rangkaian dari **OPA2333 + Rf + Cf**:
- OPA2333: menjaga potensial elektroda tetap (Vmid) dan menyerap arus sensor.
- Rf: mengubah arus jadi tegangan.
- Cf: penstabil dan penyaring noise.

Kanal:
- **CH1 glukosa** dan **CH3 fruktosamin**: potensiostat + TIA amperometrik.
- **CH2 pH**: buffer impedansi tinggi di WE + RE ditahan di VMID (potensiometrik, bukan TIA).

### 3.1 OPA2333 — dua peran

`[TEORI, KODE: PRD_Glicovia.md:46-47]`

1. **Potensiostat:** masukan (+) diikat ke Vmid, sehingga WE (terhubung ke masukan −) tertahan di Vmid. Dengan RE dan bias trimpot, beda potensial WE–RE tetap stabil agar oksidasi H₂O₂ berjalan. Tanpa ini, potensial WE bergeser saat arus berubah.
2. **TIA:** menyerap arus sensor dan memaksanya lewat Rf, sehingga `Vout = Vmid − I × Rf`.

Dipilih karena arus bias dan offset sangat kecil, derau rendah, dan cocok untuk sinyal nA–µA.

### 3.2 Rf (resistor umpan balik) dan Cf

`[KODE: hardware/kicad_tanpa_tp4056/generate_schematic.py:610-650, 749]`

- Rf = **resistor fisik 100 kΩ**: R5 (kanal glukosa) dan R11 (kanal fruktosamin). Cf = kapasitor 1,3 nF paralel dengan Rf: C8 dan C12.
- **Fungsi Rf:** mengubah arus jadi tegangan (gain = Rf volt per ampere).

| Arus sensor | Penurunan tegangan (I × 100 kΩ) |
|---|---|
| 1 nA | 0,1 mV |
| 1 µA | 0,1 V |
| 5 µA | 0,5 V |

- **Fungsi Cf:** menstabilkan op-amp dan meredam noise. Bukan penentu gain.
- **Alasan 100 kΩ (menurut catatan desain skematik):** bandwidth TIA ≈ 1,2 kHz, `fc = 1/(2π × Rf × Cf) = 1/(2π × 100 kΩ × 1,3 nF)`, sesuai simulasi di laporan PKM. Ini meredam noise di atas 1,2 kHz (jala-jala, derau elektronik) tetapi cukup cepat untuk sinyal sensor yang lambat.
- **Batas jenuh:** `Vmid / Rf`. Pada Vmid nominal 1,65 V ≈ **16 µA**. Pada Vmid terukur 0,913 V ≈ **9 µA**.
- **Trade-off:** Rf terlalu kecil → sinyal tenggelam di noise dan resolusi ADC. Rf terlalu besar → cepat jenuh.
- **Status:** skematik sendiri menyebut nilai R/C sebagai *rancangan awal, wajib diverifikasi bench*. Arus sensor sebenarnya belum diketahui (keputusan D5 di PRD). PRD (H-4) menyarankan Rf alternatif lewat jumper (mis. 1 MΩ) bila arus < 100 nA, dan Rf diganti bila arus > 16 µA.

**Cara memilih Rf yang benar:** ukur arus sensor nyata dengan larutan standar atau dummy cell, tentukan `Imax`, pilih `Rf ≈ (Vmid − margin) / Imax`, lalu cek arus minimum masih di atas derau dan resolusi ADC.

### 3.3 VMID — sumber dan peran

`[KODE: generate_schematic.py:591-600, 797]`

```
+3V3 ──[R1 10kΩ]──┬──[R2 10kΩ]── GND
                  ├──[C7 10µF]── GND      (penyaring noise)
                  └── VMID → pin 5 (+) U3, U4, U5 (OPA2333) + jumper ke ADS1115 A3
```

`Vmid = 3,3 V × R2/(R1+R2) = 1,65 V` (nominal). Alat hanya punya suplai 0–3,3 V, sehingga titik tengah buatan ini diperlukan agar sinyal bisa bergerak naik **dan** turun.

| Peran | Penjelasan |
|---|---|
| Acuan op-amp | Masukan (+) OPA2333 diikat ke Vmid, WE tertahan di Vmid |
| Titik nol sinyal | `Vout = Vmid` saat `I = 0` |
| Penahan RE (kanal pH) | U4B menahan RE di Vmid |
| Acuan pembacaan | Dibaca di ADS1115 A3 untuk pembacaan diferensial A1−A3 |

**Masalah:** Vmid terukur ≈ 0,913 V (lihat §9).

### 3.4 Jalur pembacaan: Vout → nilai

`[KODE: hardware/firmware_offline/firmware_offline.ino:56-110, 154]`

```
Vout → ADS1115 (raw) → I2C → ESP32 → I = −vDiff/Rf → trimmed mean 40 sampel → satuan riil
```

| Mode | Gain | Rentang | 1 LSB |
|---|---|---|---|
| Single-ended (A0 fruktosamin, A1 glukosa, A2 pH, A3 VMID) | GAIN_ONE | ±4,096 V | 0,125 mV |
| Diferensial A1−A3 (Vglu − Vmid) | GAIN_FOUR | ±1,024 V | 31,25 µV ≈ 0,31 nA pada Rf 100 kΩ |

- Laju sampel 32 SPS, alamat I2C 0x48.
- Mode diferensial langsung menghasilkan `vDiff = Vout − Vmid = −I × Rf`, tidak terpengaruh Vmid yang melenceng, dan resolusinya lebih halus.
- Mode diferensial hanya aktif bila `USE_A3_VMID = 1` (VMID dijumper ke A3). Bila 0, firmware memakai `VMID_NOMINAL = 1,65 V` sehingga arus yang dihitung **salah** karena Vmid nyata ≈ 0,913 V.
- Status JENUH: `|raw| > 32000` (≈ ±1 V, ≈ 10 µA pada Rf 100 kΩ). Status ARUS ~0: `|I| < 1 nA`.
- `measure()`: tunggu stabil (lewati arus *charging* awal), ambil 40 sampel terakhir, **trimmed mean** (buang 25% terendah dan tertinggi) agar tahan outlier.
- Contoh: glukosa 3,51 mg/dL → I = 3510 nA → vDiff = −0,351 V → raw ≈ −11232.

---

## 4. Strip SPCE

Tiga elektroda per strip: `[TEORI]`

| Elektroda | Fungsi |
|---|---|
| WE (working) | Tempat enzim dan reaksi. Arus yang diukur mengalir di sini |
| RE (reference, Ag/AgCl semu) | Patokan potensial agar WE tetap pada potensial yang tepat |
| CE (counter) | Menutup rangkaian, memberi/menerima elektron pengimbang |

Saliva diteteskan hingga menutupi ketiga elektroda. Ion di saliva membuat larutan menghantar. Saat strip kering, input mengambang (bisa ±3 V acak), jadi perlu deteksi sampel. `[KODE: analisis_uji_ph_saliva.md, PRD_Glicovia.md H-5]`

**Realisasi sensor saat ini (keputusan tim):** 1 SPCE polos (pH) + **2 SPCE ber-enzim glukosa** (kanal "glukosa" dan kanal "fruktosamin"). `[KODE: PRD_Glicovia.md §4.2]`

---

## 5. Parameter 1 — Glukosa Saliva

### 5.1 Alur dari saliva sampai tegangan

1. **Saliva membawa glukosa kecil.** Glukosa darah merembes ke saliva lewat kelenjar ludah. Kadar saliva jauh lebih rendah dari darah: data proyek 0,73 (normal) sampai 3,51 mg/dL (diabetes). Saliva juga membawa **O₂ terlarut**. `[TEORI]`
2. **Tetes saliva menutupi SPCE.** Glukosa berdifusi ke WE yang dilapisi enzim **glukosa oksidase (GOx)**.
3. **Reaksi enzim di WE** `[TEORI]`:
   ```
   Glukosa + O₂ ──(GOx)──→ Glukonolakton + H₂O₂
   ```
4. **H₂O₂ dioksidasi di WE** pada potensial tetap yang dijaga OPA2333 `[TEORI]`:
   ```
   H₂O₂ ──→ O₂ + 2H⁺ + 2e⁻
   ```
   Dua elektron yang ditangkap WE adalah **arus**.
5. **TIA** mengubah arus jadi tegangan: `Vglu = Vmid − I × Rf`.
6. **ADS1115** membaca Vglu, firmware menghitung balik arus, lalu kadar glukosa saliva.

Inti reaksi: **saliva (glukosa + O₂) + GOx → H₂O₂ → (oksidasi di WE) → elektron → arus.** Tanpa GOx, glukosa tidak bereaksi pada potensial itu dan arus hampir nol.

### 5.2 Glukonolakton

- Hasil oksidasi glukosa: GOx mengambil 2H (2e⁻ + 2H⁺) dari gugus aldehida (−CHO) glukosa, yang berubah menjadi gugus **lakton** (ester siklik). Namanya: D-glukono-δ-lakton. `[TEORI]`
- 2H itu diterima O₂ sehingga menjadi H₂O₂ (glukosa teroksidasi, O₂ tereduksi).
- Glukonolakton tidak stabil di air dan terhidrolisis spontan menjadi **asam glukonat**.
- Glukonolakton **tidak ikut diukur**. Yang menghasilkan arus adalah H₂O₂.
- Efek samping: asam glukonat bisa sedikit menurunkan pH lokal di WE. Kemungkinan kecil memengaruhi kanal pH karena strip pH terpisah. `[BELUM TERVERIFIKASI]`

### 5.3 Rumus di firmware `[KODE: hardware/data_optimal/buat_data_optimal.py]`

```
I (nA)         = 1000 × glukosa (mg/dL)        # GLU_A = 1000, GLU_B = 0
glukosa        = clamp(I_nA / 1000, 0.1, 10.0)
Vglu           = Vmid − I × Rf                 # Vdiff = Vout − Vmid = −I·Rf
raw (ADS1115)  = −I × Rf / LSB_G4
```

- Status JENUH bila `|raw| > 32000` atau `Vout < 0,05 V` atau `Vout > 3,25 V` (≈ glukosa 10 mg/dL).
- Status ARUS ~0 bila `|I| < 1 nA` (strip putus/belum ada sampel).

### 5.4 Kenapa tegangan turun saat glukosa naik

Rantai sebab-akibat:

```
Glukosa ↑ → H₂O₂ ↑ → elektron ↑ → arus ↑ → I×Rf ↑ → Vglu ↓
```

TIA bersifat **inverting**: arus yang masuk mengurangi tegangan keluaran dari level awal Vmid. Tanda minus ini sifat rangkaian dan polaritas bias, bukan berarti kadar glukosa turun. Kolom glukosa saliva di tabel tetap naik.

| Kelas | Glukosa | Arus | I × Rf | Vglu |
|---|---|---|---|---|
| Normal | 0,73 mg/dL | 730 nA | 0,073 V | ≈ 840 mV |
| Diabetes | 3,51 mg/dL | 3510 nA | 0,351 V | ≈ 562 mV |

### 5.5 Keterbatasan

- O₂ terlarut terbatas. Pada glukosa tinggi, reaksi bisa dibatasi O₂ (bukan glukosa). Sensor sering memakai mediator. `[TEORI]`
- Apakah strip kalian memakai mediator atau lapisan khusus tidak tercatat. `[BELUM TERVERIFIKASI]`

---

## 6. Parameter 2 — Fruktosamin

> **Peringatan:** saat ini kanal fruktosamin adalah **kanal glukosa kedua** (strip GOx), bukan pengukuran fruktosamin sungguhan. Jangan diklaim sebagai fruktosamin di laporan/PRD publik sebelum enzim yang benar dipakai (mis. fruktosamin oksidase/FAOX). `[KODE: PRD_Glicovia.md §4.2, keputusan D1]`

### 6.0 Apa itu fruktosamin dan alur desain idealnya

**Fruktosamin** = protein (terutama albumin) yang terglikasi: glukosa menempel ke gugus amino protein tanpa enzim, lalu menjadi ikatan stabil (ketoamina). Menggambarkan **rata-rata gula 2–3 minggu terakhir**, berbeda dengan glukosa yang menggambarkan kadar saat ini. `[TEORI]`

| | Glukosa | Fruktosamin |
|---|---|---|
| Menggambarkan | Kadar saat ini (cepat berubah) | Rata-rata 2–3 minggu (stabil) |
| Zat target | Molekul kecil | Protein terglikasi |
| Enzim | GOx | FAOX (desain ideal) |
| Satuan | mg/dL | µmol/L |

**Alur (desain ideal dengan FAOX):**

```
Saliva → FAOX di WE → H₂O₂ → elektron (arus) → TIA (R11, Cf C12) → tegangan Vfru → ADS1115 A0 → ESP32 → µmol/L → SVR
```

1. **Saliva** membawa fruktosamin dan O₂ terlarut. Nilai proyek (216–341 µmol/L) mirip rentang fruktosamin **darah**. Kadar fruktosamin saliva sungguhan perlu dicek ke literatur. `[BELUM TERVERIFIKASI]`
2. **Strip SPCE kanal 3** (konektor J4, TIA R11 dan C12) ditetesi saliva. `[KODE: generate_schematic.py:613]`
3. **Reaksi enzim** `[TEORI]`:
   ```
   Fruktosamin (fruktosil-asam amino) + O₂ ──(FAOX)──→ Glukoson + asam amino + H₂O₂
   ```
   Polanya sama dengan glukosa (enzim + O₂ → H₂O₂). FAOX umumnya bekerja pada fruktosil-asam amino atau peptida kecil, sehingga protein besar biasanya perlu dipotong dulu oleh protease. Apakah strip kalian mengatur ini belum diketahui. `[BELUM TERVERIFIKASI]`
4. **Oksidasi H₂O₂ di WE** (potensial ditahan OPA2333): `H₂O₂ → O₂ + 2H⁺ + 2e⁻`. Elektron = arus.
5. **TIA:** `Vfru = Vmid − I × Rf`. Fruktosamin naik → arus naik → tegangan turun. Alasan Vmid dan tanda minus sama dengan kanal glukosa (lihat §2.2, §3.3).
6. **ADS1115 A0**, single-ended, GAIN_ONE (±4,096 V, 1 LSB = 0,125 mV). `[KODE: firmware_offline.ino]`
7. **ESP32:** `I = (Vmid − Vfru)/Rf`, lalu `fruktosamin = (I + 4000)/35` (dibatasi 150–500), setelah tunggu stabil dan trimmed mean 40 sampel. Hasilnya menjadi fitur `fructosamine_umol_l` untuk SVR.

**Yang sama dengan glukosa:** sampel saliva, enzim oksidase penghasil H₂O₂, oksidasi H₂O₂ di WE, TIA OPA2333 + Rf 100 kΩ + Cf 1,3 nF, acuan Vmid, arah sinyal (zat naik → arus naik → tegangan turun), jalur ADS1115 → ESP32, dan terdampak masalah Vmid 0,913 V.

**Yang beda:** zat target dan enzim, pin ADC (A0 single-ended, bukan diferensial A1−A3), rumus kalibrasi, rentang arus dan tegangan (tabel di §6.2).

### 6.1 Rumus di firmware `[KODE: buat_data_optimal.py]`

```
I (nA)      = 35 × fruktosamin (µmol/L) − 4000      # FRU_A = 35, FRU_B = −4000
fruktosamin = clamp(((Vmid − Vfru)/Rf × 1e9 + 4000) / 35, 150, 500)
Vfru        = Vmid − I × Rf
```

Koefisien 35 dan −4000 adalah **kalibrasi sementara**. Mekanisme kimia di balik hubungan ini tidak terdokumentasi di repo. `[BELUM TERVERIFIKASI]`

### 6.2 Arah sinyal

Fruktosamin naik → arus naik → tegangan turun (sama dengan glukosa, karena TIA inverting).

| Kelas | Fruktosamin | Arus | Vfru |
|---|---|---|---|
| Normal | 216,6 µmol/L | 3581 nA | ≈ 555 mV |
| Diabetes | 340,8 µmol/L | 7928 nA | ≈ 119 mV |

### 6.3 Batas baca rumus

Dengan VMID ≈ 0,913 V, nilai maksimum yang bisa dibaca = **375 µmol/L** (saat Vfru = 0). Itu sebabnya target fruktosamin Diabetes pada simulasi diturunkan dari 386 menjadi 350. Dengan VMID 1,65 V, batas naik ke ≈ 586. `[KODE: data_optimal/README.md]`

Turunan batas: Vfru = 0 → `I = 0,913 V / 100 kΩ = 9130 nA` → `fru = (9130 + 4000)/35 = 375`. Kelas diabetes (Vfru ≈ 0,12 V) sudah dekat dasar rentang, sehingga fruktosamin di atas 375 terpotong.

### 6.4 Contoh perhitungan

Vmid = 0,913 V, Rf = 100 kΩ, ADS1115 A0 GAIN_ONE (1 LSB = 0,125 mV).

| Kelas | Fruktosamin | Arus `35·fru − 4000` | I × Rf | Vfru | raw A0 |
|---|---|---|---|---|---|
| Normal | 216,6 µmol/L | 3581 nA | 0,358 V | 0,555 V | ≈ 4440 |
| Diabetes | 340,8 µmol/L | 7928 nA | 0,793 V | 0,120 V | ≈ 960 |

Arah balik (normal): `I = (0,913 − 0,555)/100.000 = 3580 nA` → `fru = (3580 + 4000)/35 = 216,6` ✓. Resolusi: 1 LSB = 0,125 mV ÷ 100 kΩ = 1,25 nA ≈ 0,036 µmol/L.

### 6.5 Catatan kritis

- **Offset −4000 nA tidak dijelaskan:** pada fruktosamin 0 rumus menuntut arus negatif 4000 nA (tidak masuk akal secara fisik); arus nol terjadi pada fruktosamin ≈ 114 µmol/L. Asal koefisien 35 dan −4000 tidak tercatat di repo, kemungkinan hasil penyesuaian ke data dummy, bukan kalibrasi nyata. `[BELUM TERVERIFIKASI]`
- **Kanal belum mengukur fruktosamin** (strip GOx), jadi alur di §6.0 belum terbukti pada alat nyata.

---

## 7. Parameter 3 — pH Saliva

- Sensor **potensiometrik**: elektroda menghasilkan tegangan, bukan arus. Mengikuti persamaan Nernst (≈ −59,16 mV per satuan pH pada kondisi ideal). `[TEORI, KODE: catatan/nerst_pH.tex]`
- SPCE + RE semu Ag/AgCl bersifat **sub-Nernstian**, jadi slope (m) dan offset (c) harus dikalibrasi empiris (dua titik). `[KODE: nerst_pH.tex]`
- Rumus sementara: `VpH = −0,05916 × pH + 0,3226`, sehingga `pH = (VpH − 0,3226) / −0,05916`, di-clamp 4,0–9,0. `[KODE]`
- Arah: saliva diabetes lebih asam (pH turun) → VpH **naik** secara angka (−89 → −23,5 mV), magnitudonya mengecil.
- **Batas fisik:** `VpH = 0 V` ↔ pH 5,45. Semua pH saliva fisiologis (≈ 5,7–7,0) butuh VpH negatif, padahal ADS1115 single-ended tidak bisa membaca < 0 V. Solusi: ukur diferensial relatif VMID (A2−A3) atau ganti offset kalibrasi. `[KODE: data_optimal/README.md]`

---

## 8. Nilai Acuan per Kelas

> **[SIMULASI]** Dihitung mundur dari rumus `main.cpp` dengan noise kecil. **Bukan hasil pengukuran.** Sumber: `hardware/Hasil_dan_Pembahasan_Glicovia_DataOptimal_v4.docx`, `hardware/data_optimal/`. Nilai = rerata ± SD.

| Kelas | VpH (mV) | Vfru (mV) | Vglu (mV) | pH | Fruktosamin (µmol/L) | Glukosa saliva (mg/dL) |
|---|---|---|---|---|---|---|
| Normal | −89,0 ± 2,0 | 555,2 ± 17,5 | 840,7 ± 6,0 | 6,96 ± 0,03 | 216,6 ± 5,0 | 0,73 ± 0,06 |
| Prediabetes | −59,8 ± 4,4 | 308,8 ± 52,9 | 793,6 ± 11,0 | 6,46 ± 0,07 | 286,3 ± 15,1 | 1,17 ± 0,11 |
| Diabetes | −23,5 ± 5,9 | 119,3 ± 29,8 | 561,4 ± 12,7 | 5,85 ± 0,10 | 340,8 ± 8,5 | 3,51 ± 0,13 |

Target pembuatan simulasi (`buat_data_optimal.py`): pH 6,94 / 6,49 / 5,88; fruktosamin 224 / 285 / 350; glukosa 0,67 / 1,16 / 3,31.

**Pola arah:**

| Parameter | Normal → Diabetes |
|---|---|
| pH saliva | turun (lebih asam) |
| Fruktosamin, glukosa saliva | naik |
| Vfru, Vglu | turun (efek TIA inverting) |
| VpH | naik secara angka (mendekati 0) |

Range ± SD antar kelas tidak tumpang tindih pada data simulasi. Range ini adalah sebaran data eksperimen, **bukan batas diagnosis klinis**.

**Karakter simulasi:** garis hampir datar per sesi, ada lonjakan awal (tau 5 s) yang meniru *charging* sensor, 40 sampel terakhir dipakai `measure()`. Regresi linear sudah sempurna dan tiap kanal tunggal memisahkan kelas, jadi **F1 tinggi di data ini bukan bukti kinerja alat**.

---

## 9. Masalah Perangkat Keras yang Diketahui

`[KODE: PRD_Glicovia.md §6, data_optimal/README.md]`

1. **VMID ≈ 0,913 V**, bukan 1,65 V. Periksa R1/R2, beban, OPA2333 U3/U4/U5 pin 5. (H-1)
   - Dampak: rumus `I = (Vmid − Vout)/Rf` salah bila Vmid tidak dibaca (A3 harus dijumper), batas jenuh turun 16 → ~9 µA, fruktosamin maksimum terbaca 375 µmol/L.
   - Hipotesis penyebab `[BELUM TERVERIFIKASI]`: pembagi 10k/10k langsung menahan tiga pin op-amp (U3, U4, U5) tanpa *buffer*, sehingga arus bias atau kebocoran dapat menggeser Vmid. Biasanya Vmid disangga satu op-amp. Langkah verifikasi: ukur Vmid di titik pembagi, lepas beban satu per satu.
2. **Kanal glukosa menempel ~0 V** pada data asli (output TIA mentok rel bawah, kanal tidak merespons konsentrasi). Verifikasi AFE dengan resistor/dummy cell, arus uji diketahui → `Vout = Vmid − I·Rf` (galat < 5%). (H-2)
3. **Strip kering = input mengambang** (±3 V acak). Perlu pull-down atau mode deteksi sampel. (H-5)
4. **Kontak konektor strip** adalah sumber varians utama. Perlu slot strip yang repeatable. (H-8)
5. **Log Pre-Diabetes asli hanya 5 baris** (~2 s). Perlu pengambilan ulang ≥ 60 s + 40 sampel.
6. **Label 126 mg/dL** pada sesi "Pre-Diabetes" termasuk kriteria diabetes (GDP ≥ 126). Prediabetes = 100–125 mg/dL.
7. Data asli hanya dari **2 pasien**; pola "148 lebih rendah dari 88" berlawanan dengan logika biologis. Data cukup membuktikan alur sistem, bukan akurasi prediksi.

---

## 10. Pertanyaan Terbuka `[BELUM TERVERIFIKASI]`

- Apakah strip glukosa memakai mediator (mis. ferrisianida, Prussian blue)? Potensial kerja WE sebenarnya berapa?
- Mekanisme kimia di balik `I = 35·fru − 4000`. Dari mana koefisien itu diperoleh?
- Polaritas arus nyata pada alat (anodik/katodik) dan apakah sesuai tanda `Vout = Vmid − I·Rf`.
- Pengaruh asam glukonat terhadap pH lokal di strip glukosa.
- Kapan enzim fruktosamin yang benar (FAOX) akan dipakai pada kanal fruktosamin.
- Alasan resmi memilih Rf = 100 kΩ selain bandwidth 1,2 kHz dan simulasi laporan PKM. Rentang arus sampel saliva sebenarnya (keputusan D5) belum diukur.
- Apakah Vmid perlu di-*buffer* dengan op-amp tersendiri (lihat hipotesis §9 butir 1).
- Asal koefisien `I = 35·fru − 4000` (offset negatif) dan apakah dari kalibrasi nyata atau dummy (§6.5).
- Kadar fruktosamin saliva sungguhan (µmol/L) menurut literatur, dan apakah rentang 216–341 realistis untuk saliva.
- Apakah strip FAOX memerlukan protease untuk memotong protein terglikasi.
- Apakah tim mempertimbangkan AFE terintegrasi (LMP91000, AD5940) untuk versi berikutnya (§2.3).

---

## 11. Model AI

`[KODE: ml_pipeline/src/train_svm.py, inference.py]`

- Model estimasi glukosa darah: **SVR kernel RBF**. Output mg/dL. SVC dipakai terpisah untuk klasifikasi kelas.
- Fitur (urutan tetap, `FEATURE_ORDER`): `glucose_saliva`, `ph_value`, `fructosamine_umol_l`. Tegangan dikonversi dulu ke tiga nilai ini.
- Fitur distandarkan (`StandardScaler`) karena skala beda jauh (pH ≈ 6, fruktosamin ≈ 300). Scaler yang sama dipakai saat inferensi.
- **Cara SVR menebak:** mencari permukaan halus yang paling pas dengan data. Kernel RBF membuat permukaan bisa melengkung. Ada pita toleransi ε: titik di dalam pita tidak dihitung salah. Titik penentu = *support vectors*.
- **Hyperparameter** dicari dengan GridSearchCV, 5-fold, skor R²:

| Parameter | Grid | Arti |
|---|---|---|
| `C` | 0,1 / 1 / 10 / 100 | Ketegasan menghukum kesalahan. Kecil = kasar (underfit), besar = hafalan (overfit) |
| `gamma` | 0,01 / 0,1 / 0,5 / 1,0 | Jangkauan pengaruh satu titik. Kecil = halus, besar = bergelombang |
| `epsilon` | 0,1 / 0,2 / 0,5 | Lebar pita toleransi (dalam satuan terstandar) |

  4 × 4 × 3 = 48 kombinasi × 5 fold = 240 kali training. Mode cepat memakai 2 nilai pertama tiap parameter (8 kombinasi). Gamma dibatasi maksimal 1,0.
- **Evaluasi:** regresi (R², MAE, RMSE) dan klinis (Clarke Error Grid). Target v1: MAE ≤ 20 mg/dL dan ≥ 90% titik di zona A+B Clarke pada subjek yang tidak pernah dilihat model. `[KODE: PRD_Glicovia.md]`
- **F1 score** dipakai untuk klasifikasi kelas (rata-rata harmonik precision dan recall, macro-F1 untuk multikelas). Akurasi biasa menipu pada kelas tak seimbang. Pada data simulasi, F1 tinggi tidak menjadi bukti kinerja alat.

---

## 12. Catatan Perubahan

| Tanggal | Perubahan | Sumber |
|---|---|---|
| 2026-10-24 | Dokumen dibuat dari sesi brainstorm: arus vs tegangan, TIA/OPA2333, rantai saliva→GOx→H₂O₂→arus→tegangan, glukonolakton, nilai acuan per kelas (simulasi), model SVR, F1 score | Sesi tanya jawab, `PRD_Glicovia.md`, `data_optimal/` |
| 2026-10-24 | Tambah §2.1–2.3 (kenapa lewat tegangan, penurunan rumus TIA, alternatif komponen AFE), §3.1–3.4 (peran OPA2333, Rf/Cf dan alasan 100 kΩ, sumber VMID, jalur pembacaan ADS1115). Tambah hipotesis penyebab VMID 0,913 V di §9 dan 3 pertanyaan terbuka di §10 | Sesi tanya jawab, `generate_schematic.py`, `firmware_offline.ino` |
| 2026-10-24 | Perluas §6 fruktosamin: definisi, alur desain ideal (saliva → FAOX → H₂O₂ → arus → TIA → ADS1115 A0 → µmol/L), perbandingan dengan glukosa, turunan batas 375, contoh hitung (§6.4), catatan kritis offset −4000 nA (§6.5). Tambah 3 pertanyaan terbuka di §10 | Sesi tanya jawab, `PRD_Glicovia.md §4.2`, `buat_data_optimal.py` |

---

## 13. Rujukan File Proyek

| File | Isi |
|---|---|
| `hardware/PRD_Glicovia.md` | PRD utama: hardware, firmware, backend, pengujian |
| `hardware/PRD_Glicovia_prototipe.md` | PRD prototipe |
| `hardware/data_optimal/README.md` | Penjelasan data simulasi dan batas fisik rumus |
| `hardware/data_optimal/buat_data_optimal.py` | Rumus dan generator data simulasi |
| `hardware/Hasil_dan_Pembahasan_Glicovia_DataOptimal_v4.docx` | Draf Hasil dan Pembahasan (Tabel 1, Gambar 8) |
| `hardware/kicad_tanpa_tp4056/generate_schematic.py` | Skematik: nilai Rf, Cf, pembagi VMID, netlist, catatan desain |
| `hardware/firmware_offline/firmware_offline.ino` | Pembacaan ADS1115, mode diferensial, `measure()` |
| `hardware/catatan/nerst_pH.tex` | Landasan Nernst dan kalibrasi pH |
| `hardware/catatan/analisis_uji_ph_saliva.md` | Analisis uji pH saliva |
| `ml_pipeline/src/train_svm.py`, `inference.py` | Pelatihan SVR dan inferensi |
