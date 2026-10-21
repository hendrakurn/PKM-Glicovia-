# PRD — Glicovia: Alat Skrining Diabetes Berbasis Saliva

| | |
|---|---|
| Versi | 0.1 (draft) |
| Tanggal | 2026-10-21 |
| Tim | PKM-KC Glicovia |
| Status hardware | Skematik rev 1.0 `kicad_tanpa_tp4056/` (AFE masih rancangan awal, belum terverifikasi bench) |

---

## 1. Ringkasan

Glicovia adalah alat genggam (*handheld*) yang membaca tiga parameter saliva memakai *Screen-Printed Carbon Electrode* (SPCE): **pH**, **glukosa saliva**, dan **fruktosamin**. Hasil pembacaan dikonversi ke **satuan riil** (bukan volt), dikirim ke cloud (Railway), lalu model **SVM** memperkirakan **kadar glukosa darah (mg/dL)** dan kategori klinis. Hasil ditampilkan balik di OLED alat.

Alat ini **skrining awal non-invasif**, bukan alat diagnosis. Lihat §10.

## 2. Masalah & tujuan

**Masalah.** Pemeriksaan gula darah memerlukan tusuk jari/vena; tidak nyaman dan menghambat skrining massal.

**Tujuan produk**
1. Mengukur pH, glukosa, fruktosamin saliva dalam satu kali tetes sampel.
2. Mengeluarkan nilai riil per parameter (pH, mg/dL, µmol/L atau satuan setara) dari alat, bukan tegangan.
3. Menaksir glukosa darah (mg/dL) lewat inferensi SVM di cloud, tampil di alat < 10 detik setelah pengukuran selesai.
4. Menyimpan semua pembacaan + label glukometer di database untuk pelatihan ulang model.

**Bukan tujuan (v1)**: diagnosis medis, sertifikasi regulator, aplikasi mobile, multi-pengguna/akun, pengisian baterai di dalam alat.

## 3. Pengguna & skenario

| Persona | Kebutuhan |
|---|---|
| Operator/peneliti tim | Mengambil data uji, kalibrasi, melihat data di DB, melatih ulang model |
| Pengguna uji (relawan) | Meneteskan saliva, menunggu, membaca hasil di OLED |

Alur pakai: nyalakan → (opsional) kalibrasi → teteskan saliva ke strip SPCE → alat deteksi sampel masuk → tunggu stabil → baca 3 kanal → konversi satuan riil → kirim ke cloud → terima prediksi → tampil OLED.

## 4. Kondisi saat ini (as-is)

### 4.1 Hardware (`kicad_tanpa_tp4056/`)
- **MCU**: ESP32-DevKitC V4 (WROOM-32U, antena eksternal RP-SMA). I2C: SDA=IO21, SCL=IO22.
- **ADC**: ADS1115 (0x48, ADDR=GND), 16-bit, GAIN_ONE ±4,096 V.
- **Tampilan**: OLED **1,3"** I2C (0x3C), 128x64. Firmware memakai driver SH1106G (`Adafruit_SH110X`). Modul 1,3" umumnya SH1106; jika ternyata SSD1306, ganti driver. Skematik masih berlabel 0,96" (hanya label, pinout sama).
- **Daya**: Li-Po 1S 3,7 V 1200 mAh (PCM internal) → saklar KCD11 → MT3608 boost 5,0 V → ESP32 5V. **Tanpa TP4056**; baterai diisi di luar alat.
- **AFE** (3× OPA2333, tiap IC dual/quad dipakai untuk satu kanal):
  - CH1 glukosa & CH3 fruktosamin: potensiostat + TIA amperometrik. Rf 100 kΩ, Cf 1,3 nF, bias WE–RE diatur trimpot (RV1/RV2) dari VMID.
  - CH2 pH: buffer impedansi tinggi WE + penahan RE di VMID (potensiometrik).
  - VMID = pembagi 10k/10k (nominal 1,65 V), referensi WE/RE.
  - Konektor sensor JST 3-pin (WE, RE, CE) per kanal.
- Skematik digenerate oleh `generate_schematic.py`, netlist diverifikasi `verify_netlist.py`. Catatan desain di skematik sendiri menyebut AFE "rancangan awal, wajib diverifikasi bench".

### 4.2 Sensor (keputusan tim karena keterbatasan waktu)
Idealnya: pH = SPCE polos; glukosa = SPCE + enzim glukosa oksidase; fruktosamin = SPCE + enzim fruktosamin (mis. fruktosamin oksidase/FAOX). **Realisasi**: 1 SPCE polos (pH) + **2 SPCE ber-enzim glukosa** (kanal glukosa dan kanal "fruktosamin").

> **Konsekuensi**: kanal fruktosamin saat ini tidak spesifik fruktosamin. Ia merupakan kanal glukosa kedua. Jangan diklaim sebagai pengukuran fruktosamin di laporan/PRD publik sebelum enzim yang benar dipakai. Lihat §11 (keputusan D1).

### 4.3 Firmware (tiga varian, belum konsisten)
| Folder | Fungsi | Peta kanal ADS |
|---|---|---|
| `firmware/firmware.ino` | Online: WiFi + MQTT (HiveMQ publik) + OLED + terima prediksi | A0=glukosa, A1=pH, A2=fruktosamin; rumus konversi **dummy** (×200, 7−5V, ×500) |
| `firmware_offline/firmware_offline.ino` | Diagnostik serial, TIA diferensial A1−A3, hitung arus nA | A0=fruktosa, A1=glukosa, A2=pH, A3=VMID |
| `pHBisa/` | Uji pH + kalibrasi (`calibrate.py`, catatan Nernst) | A2=pH |

Peta kanal **berbeda** antar firmware dan juga berbeda dari catatan skematik (A0 glukosa, A1 pH, A2 fruktosamin). Harus disatukan (§6.1 H-3).

Firmware online sudah punya kontrak prediksi: subscribe `glicovia/devices/GLICO-01/predictions`, mem-parse `glucose_estimate`, `clinical_category`, `confidence_score`.

### 4.4 Data (`DATA/`)
Tujuh file CSV, kolom `waktu_iso, t_detik, raw, Vfru_V, Vglu_V, VpH_V, Vmid_V, I_nA, errI2C, status`, ±4 sampel/detik.

| Sampel | File | Baris | Baris status `OK` |
|---|---|---|---|
| Glukosa darah **148 mg/dL** (diabetes) | 3 file | 430 / 316 / 221 | 2 / 0 / 57 |
| Glukosa darah **88 mg/dL** (normal) | 4 file | 512 / 199 / 307 / 332 | 0 / 0 / 0 / 0 |

Rata-rata separuh akhir tiap sesi (V): 

| Sesi | Vfru | Vglu | VpH | Vmid | I (nA) |
|---|---|---|---|---|---|
| 148 #1 | 0,0002 | 0,0024 | 0,0214 | 0,912 | 7165 |
| 148 #2 | 0,0002 | 0,0032 | 0,0043 | 0,912 | 7161 |
| 148 #3 | 0,0027 | 0,0401 | 0,0507 | 0,915 | 6949 |
| 88 #1 | 0,513 | 0,0041 | 0,0546 | 0,914 | 7161 |
| 88 #2 | 0,541 | 0,0041 | 0,0490 | 0,914 | 7160 |
| 88 #3 | 0,568 | 0,0041 | 0,0413 | 0,913 | 7160 |
| 88 #4 | 0,583 | 0,0044 | 0,0448 | 0,913 | 7157 |

## 5. Temuan kritis (harus diselesaikan sebelum AI bermakna)

1. **Data hampir seluruhnya tidak valid.** Hanya 59 dari 2.317 baris (≈2,5%) berstatus `OK`; sisanya `JENUH`. Arus terbaca ≈7.160 nA konstan di hampir semua sesi → nilai itu *clamp*, bukan sinyal sampel.
2. **Kanal glukosa menempel di ~0 V** (Vglu 0,002–0,04 V) pada semua sesi: output TIA mentok rel bawah. Kanal tidak merespons konsentrasi.
3. **VMID terukur 0,91 V, rancangan 1,65 V.** Selisih besar menandakan masalah bias/beban/pembagi; semua perhitungan arus `I = (VMID − Vout)/Rf` ikut salah. Penyebab belum diketahui; perlu diukur multimeter di bench.
4. **Kanal fruktosamin berbeda drastis antar kelas** (≈0,0002 V pada 148 vs 0,51–0,58 V pada 88, dan nilainya naik di dalam sesi 88 dengan SD 0,12–0,14 V). Pola ini lebih mirip kontak/pembasahan/*floating* daripada analit; kelas "terbalik" terhadap ekspektasi biologis. Jangan dipakai sebagai fitur model sebelum dipastikan.
5. **Hanya 2 pasien (2 label) tersedia.** Model SVM tidak bisa dilatih/divalidasi dari 2 titik; pemisahan 148 vs 88 oleh model mungkin hanya menangkap artefak sesi (kontak strip, hari, kelembapan), bukan glukosa.
6. **Peta kanal ADS tidak konsisten** antar firmware dan skematik (§4.3). Data lama bisa salah label kanal.
7. **Kanal fruktosamin bukan fruktosamin** (§4.2).
8. **Keamanan data:** SSID/password WiFi dan broker HiveMQ publik tanpa autentikasi/TLS di firmware. Data kesehatan tidak boleh lewat broker publik.

Implikasi: bagian AI (§8) dapat dibangun pipeline-nya sekarang, tetapi **angka prediksi tidak boleh dilaporkan sebagai hasil ilmiah** sampai kriteria data §9 terpenuhi.

## 6. Persyaratan

Prioritas: **P0** wajib sebelum demo, **P1** sangat diinginkan, **P2** nanti.

### 6.1 Hardware (H)
| ID | Persyaratan | P |
|---|---|---|
| H-1 | Ukur & perbaiki VMID hingga 1,65 V ±2% pada bench (cek R1/R2, beban, OPA2333 U3/U4/U5 pin 5). Buktikan dengan foto multimeter. | P0 |
| H-2 | Verifikasi tiap AFE dengan resistor/dummy cell: arus uji diketahui → Vout sesuai `Vmid − I·Rf` (galat < 5%). Kanal glukosa tidak boleh menempel di rel. | P0 |
| H-3 | Tetapkan **satu** peta kanal ADS dan tulis di skematik: A0=glukosa, A1=pH, A2=fruktosamin(sementara), A3=VMID *atau* sesuai firmware offline; pilih salah satu dan samakan semua firmware + skematik. | P0 |
| H-4 | Pastikan rentang arus: Rf 100 kΩ jenuh pada ≈16 µA. Pilih Rf atau bias VSET agar arus sampel saliva (puluhan nA–µA) terbaca tanpa jenuh. Sediakan Rf alternatif (mis. 1 MΩ via jumper) bila arus < 100 nA. | P1 |
| H-5 | Pelindung derau: kondisi kering = input *floating* (3 V acak, lihat `analisis_uji_ph_saliva.md`). Tambah pull-down/mode deteksi sampel agar alat tidak membaca saat strip kering. | P1 |
| H-6 | Selesaikan PCB (`.kicad_pcb`), DRC bersih, ekspor Gerber. | P1 |
| H-7 | Daya: bertahan ≥ 4 jam pengukuran kontinu pada 1200 mAh; MT3608 diset 5,0 V sebelum disambung ke ESP32. | P1 |
| H-8 | Casing + slot strip SPCE dengan kontak konektor yang repeatable (kontak buruk = sumber varians utama). | P1 |

### 6.2 Firmware (F)
| ID | Persyaratan | P |
|---|---|---|
| F-1 | **Keluaran satuan riil**: `pH` (unit pH), `glucose_saliva` (mg/dL), `fructosamine` (µmol/L bila enzim benar; sementara `fructosamine_index` = arus setara nA). Volt/arus mentah ikut dikirim sebagai field terpisah untuk audit. | P0 |
| F-2 | **pH**: kalibrasi 2–3 titik buffer (4,01 / 6,86 / 9,18) → `pH = (V − c) / m` dengan `m` (V/pH) dan `c` disimpan di NVS ESP32. Kompensasi suhu Nernst (59,16 mV/pH @25 °C) bila ada sensor suhu (P2). Hasil `calibrate.py` dipindah ke firmware. | P0 |
| F-3 | **Glukosa**: `I(nA) = (VMID − Vout)/Rf × 1e9`; konsentrasi `mg/dL = (I − intercept)/slope` dari regresi larutan standar (≥ 5 konsentrasi, replikat ≥ 3), koefisien di NVS. Hapus konstanta dummy di `firmware.ino`. | P0 |
| F-4 | Mode ukur terstruktur: deteksi sampel masuk (Δarus > ambang) → tunggu stabil (lewati arus *charging*; tetapkan waktu dari data, saat ini 60 s) → ambil N sampel → *trimmed mean* + SD + CV. Kirim **satu ringkasan per pengukuran**, bukan stream tiap 5 s. | P0 |
| F-5 | Tolak hasil bila `status != OK`, CV > 10%, jenuh, atau error I2C; tampilkan penyebab di OLED. Tidak boleh mengirim nilai jenuh sebagai data valid. | P0 |
| F-6 | Konfigurasi WiFi/endpoint/token tidak di-*hardcode* di repo (file `secrets.h` di-gitignore atau portal WiFiManager). | P0 |
| F-7 | Kirim ke cloud lewat HTTPS (disarankan, §7) dengan retry + buffer lokal bila offline (min. 20 pengukuran di flash). | P1 |
| F-8 | OLED: layar hasil (3 parameter riil + prediksi glukosa darah + kategori), layar kalibrasi, layar error. | P1 |
| F-9 | Mode kalibrasi dari tombol/serial tanpa re-flash. | P1 |
| F-10 | `device_code`, versi firmware, versi kalibrasi di setiap payload. | P1 |

### 6.3 Cloud & database (C) — Railway
> **DIGANTIKAN oleh §14.2.** Setelah audit repo ternyata backend, ML service, database, dan website sudah ada dan berjalan di `app/` dan `ml_pipeline/`. Jangan membangun FastAPI baru; pakai yang ada. Bagian di bawah dipertahankan sebagai referensi persyaratan C-1…C-7 saja.

Arsitektur awal yang diusulkan (tidak jadi dipakai):

```
ESP32 --HTTPS POST /v1/readings--> API (FastAPI, Railway)
                                      |-- simpan ke Postgres (Railway)
                                      |-- load model SVM (joblib)  -> prediksi
ESP32 <-- JSON {glucose_estimate, clinical_category, confidence} (response sama)
```

Alasan: satu service + satu DB, tanpa broker, tanpa subscriber terpisah, prediksi dikembalikan di *response*. MQTT yang sekarang (HiveMQ publik) boleh dipertahankan hanya bila perlu *push*; bila dipakai, wajib broker privat + TLS + auth.

| ID | Persyaratan | P |
|---|---|---|
| C-1 | `POST /v1/readings` (auth token per device), validasi skema, simpan raw + terkonversi, balas prediksi. | P0 |
| C-2 | Postgres, skema §7.2. | P0 |
| C-3 | Model SVM dimuat saat start; versi model dicatat di tiap prediksi. Bila belum ada model valid → balas `glucose_estimate: null`, `status: "model_not_ready"` (tidak ada angka palsu). | P0 |
| C-4 | `POST /v1/labels` untuk mengisi glukosa darah glukometer (ground truth) ke sebuah pengukuran/sesi. | P0 |
| C-5 | `GET /v1/readings?device=&from=&to=` + ekspor CSV untuk pelatihan. | P1 |
| C-6 | Endpoint `POST /v1/train` atau skrip offline di repo untuk melatih ulang dari DB, menyimpan artefak model + metrik. | P1 |
| C-7 | HTTPS, token per device di env var Railway, rate limit, tanpa data identitas pribadi di DB (pakai `subject_code`). | P0 |

### 6.4 Model AI (M)
Lihat §8.

## 7. Kontrak data

### 7.1 Payload alat → cloud (JSON)
```json
{
  "device_code": "GLICO-01",
  "fw_version": "0.2.0",
  "cal_version": "2026-10-21-a",
  "measured_at": "2026-10-21T05:07:33Z",
  "subject_code": "S001",
  "ph": 6.82,
  "glucose_saliva_mgdl": 1.9,
  "fructosamine": null,
  "fructosamine_index_nA": 41.2,
  "raw": {
    "v_glu": 0.0412, "v_ph": 0.0450, "v_fru": 0.5100, "v_mid": 1.650,
    "i_glu_nA": 42.3, "i_fru_nA": 41.2
  },
  "quality": {
    "n_samples": 40, "cv_pct": 4.2, "saturated": false, "i2c_errors": 0,
    "wait_ms": 60000, "ok": true
  }
}
```
Nama field `ph`, `fructosamine`, `salivary_glucose` pada firmware lama boleh dipertahankan untuk kompatibilitas; yang baru ditambahkan, tidak mengubah arti yang lama.

### 7.2 Respons cloud → alat (kompatibel dengan parser firmware sekarang)
```json
{
  "glucose_estimate": 112.4,
  "clinical_category": "PREDIABETES",
  "confidence_score": 0.74,
  "model_version": "svr-2026-11-01",
  "status": "ok"
}
```
Kategori (acuan puasa ADA): `NORMAL` < 100, `PREDIABETES` 100–125, `DIABETES` ≥ 126 mg/dL. Tim wajib menetapkan apakah label uji berasal dari kondisi puasa/sewaktu (§11 D3).

### 7.3 Skema DB
- `devices(id, device_code, token_hash, created_at)`
- `subjects(id, subject_code, age, sex, diabetes_status, notes)` — tanpa nama.
- `measurements(id, device_id, subject_id, measured_at, ph, glucose_saliva_mgdl, fructosamine, fructosamine_index_nA, raw jsonb, quality jsonb, fw_version, cal_version)`
- `labels(id, measurement_id|subject_id+session, blood_glucose_mgdl, method, fasting bool, taken_at)`
- `predictions(id, measurement_id, model_version, glucose_estimate, category, confidence, created_at)`
- `calibrations(id, device_id, kind, params jsonb, created_at)`

## 8. Model SVM

**Tugas.** Regresi (**SVR**) glukosa darah (mg/dL) dari fitur saliva; kategori klinis diturunkan dari angka regresi (bukan model terpisah) agar konsisten. Klasifikasi SVC hanya sebagai pembanding.

**Fitur v1**: `ph`, `glucose_saliva_mgdl` (atau `i_glu_nA`), `fructosamine_index_nA`. Opsional: `cv_pct`, jeda pembasahan. `fructosamine` riil hanya masuk bila kanal benar-benar spesifik (D1).

**Pipeline**: `StandardScaler → SVR(kernel=rbf)`, `GridSearchCV` (C, epsilon, gamma). Versi dan artefak model (`joblib`) + metrik disimpan.

**Persyaratan data (syarat sebelum angka dilaporkan)**
| Item | Minimum |
|---|---|
| Subjek berbeda | ≥ 30 (target 50), tersebar di 70–250 mg/dL; tidak hanya dua klaster 88 dan 148 |
| Pengukuran per subjek | ≥ 3, hanya baris `quality.ok = true` |
| Label | glukosa darah glukometer, waktu ≤ 10 menit dari saliva, status puasa tercatat |
| Pengambilan saliva | Prosedur seragam (puasa/waktu sejak makan, bilas mulut, volume tetes) |
| Strip | Lot SPCE dan enzim dicatat |

**Validasi**: *leave-one-subject-out* atau *GroupKFold* per `subject_code`. Dilarang membagi per baris (baris satu sesi hampir identik → *leakage*, akurasi palsu tinggi). Laporkan MAE, RMSE, R², dan Clarke Error Grid (zona A+B).

**Target v1 (realistis)**: MAE ≤ 20 mg/dL dan ≥ 90% titik di zona A+B Clarke pada subjek yang tidak pernah dilihat model. Bila tidak tercapai, laporkan jujur sebagai penelitian awal.

**Kondisi sekarang**: dengan 2 subjek dan data jenuh, yang dapat dikerjakan hanya (a) pipeline pelatihan/inferensi dan (b) uji *smoke* model dummy yang ditandai `model_not_ready`.

## 9. Kriteria penerimaan

1. Bench: VMID 1,65 V ±2%; arus uji resistor terbaca dengan galat < 5% di ketiga kanal; tanpa jenuh.
2. Kalibrasi pH: buffer 4,01/6,86/9,18 terbaca ±0,1 pH (R² ≥ 0,99).
3. Kalibrasi glukosa: kurva standar R² ≥ 0,98; LOD dan rentang linear terdokumentasi.
4. Repeatability: CV ≤ 10% pada 3 replikat sampel yang sama.
5. Alat menampilkan pH, glukosa saliva (satuan riil), dan prediksi glukosa darah di OLED; end-to-end (tetes → tampil) ≤ 90 s termasuk waktu tunggu stabil, jaringan ≤ 5 s.
6. Setiap pengukuran valid tercatat di Postgres dengan raw + label.
7. Tidak ada kredensial atau data pasien di repo/di broker publik.

## 10. Non-fungsional, etika, regulasi

- **Klinis**: korelasi glukosa saliva–darah lemah dan bervariasi (konsentrasi saliva sangat rendah, dipengaruhi makanan, kebersihan mulut, laju alir saliva, pH, dan kesehatan gigi). Alat ditampilkan sebagai "indikasi skrining", dengan pernyataan: *bukan alat diagnosis; hasil tidak menggantikan pemeriksaan laboratorium*.
- **Etika**: uji pada manusia butuh *informed consent* (dan *ethical clearance* bila hasil dipublikasikan); data subjek hanya berupa kode.
- **Keamanan**: HTTPS/TLS, token per device, secret di env, tanpa data identitas.
- **Keselamatan listrik**: baterai Li-Po dengan PCM; arus ke elektroda < µA dan tegangan bias < 1 V; saklar mematikan semua rel.
- **Performa**: boot < 10 s, konsumsi rata-rata ≤ 250 mA saat WiFi aktif.

## 11. Risiko

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Data valid terlalu sedikit untuk SVM | Model tidak bermakna | Prioritaskan perbaikan AFE + pengumpulan ≥ 30 subjek; laporan jujur sebagai studi awal |
| VMID 0,91 V / TIA jenuh tidak teratasi | Kanal glukosa tak berfungsi | Debug bench §6.1 (H-1, H-2) hari pertama |
| Kanal fruktosamin bukan spesifik | Klaim parameter ke-3 tidak sah | D1: ganti enzim bila memungkinkan, atau ganti klaim menjadi "kanal glukosa ganda/replikat" |
| Waktu mepet | Fitur tidak selesai | Kerjakan urut P0; MQTT→HTTP mengurangi komponen |
| Varian strip/kontak | Varians antar sesi | Casing + slot strip repeatable; catat lot |
| Kebocoran data via broker publik | Pelanggaran privasi | Hapus HiveMQ publik, HTTPS saja |

## 12. Rencana kerja (urut, waktu mepet)

1. **Hari 1–2 (hardware)**: H-1, H-2, H-3. Tanpa ini, langkah lain sia-sia.
2. **Hari 2–3 (kalibrasi)**: F-2 pH (buffer), F-3 glukosa (standar), simpan koefisien NVS. Hasil: output riil pH dan mg/dL.
3. **Hari 3–4 (firmware)**: F-1, F-4, F-5, F-6; satukan satu firmware.
4. **Hari 4–5 (cloud)**: C-1…C-4, C-7 di Railway; model dummy `model_not_ready`.
5. **Hari 5+ (data & model)**: ambil data subjek sebanyak mungkin dengan prosedur §8, latih SVR, laporkan metrik dengan validasi per subjek.
6. Demo end-to-end + dokumen.

## 13. Pertanyaan terbuka (butuh keputusan tim)

| ID | Pertanyaan |
|---|---|
| D1 | Kanal ke-3: tetap enzim glukosa (jadi replikat) atau pakai enzim fruktosamin? Apa klaim di laporan? |
| D2 | Satuan glukosa saliva: mg/dL atau µM/mM? (rentang saliva jauh di bawah darah; tetapkan dari kurva standar) |
| D3 | Sampel 148 dan 88 mg/dL diambil puasa atau sewaktu? Dari berapa orang (1 per kelas?) dan berapa kali ambil? |
| D4 | Peta kanal ADS final: skematik atau firmware offline yang jadi acuan? |
| D5 | Arus sampel saliva diperkirakan berapa (nA)? Menentukan Rf (H-4). |
| D6 | Kirim via HTTPS ke Railway (disarankan) atau tetap MQTT? Bila MQTT, broker privat apa? |
| D7 | Perlu sensor suhu untuk kompensasi Nernst? |

---

## 14. Temuan lanjutan & jalur prototipe (data terbatas)

Bagian ini untuk tahap berikutnya: menghubungkan data alat ke SVM, menghasilkan prediksi glukosa darah, menampilkannya di OLED 1,3" dan di website, dengan keputusan **melanjutkan memakai data yang ada** (waktu mepet).

### 14.1 Uji cepat: apakah data yang ada "terbaca" oleh model?

Metode: satu file CSV = satu sampel (median separuh akhir sesi), lalu *leave-one-session-out* dengan nearest-centroid (sklearn tidak terpasang di mesin uji). 7 sesi: 3 untuk 148 mg/dL, 4 untuk 88 mg/dL.

| Sesi | Label | VpH (V) | Vfru (V) |
|---|---|---|---|
| 148 #1 | 148 | 0,0216 | 0,0003 |
| 148 #2 | 148 | 0,0044 | 0,0001 |
| 148 #3 | 148 | 0,0509 | 0,0029 |
| 88 #1 | 88 | 0,0548 | 0,5262 |
| 88 #2 | 88 | 0,0496 | 0,5440 |
| 88 #3 | 88 | 0,0411 | 0,5615 |
| 88 #4 | 88 | 0,0449 | 0,5918 |

| Fitur | Tebakan benar (7 sesi) |
|---|---|
| VpH saja | 6 / 7 |
| Vfru saja | **7 / 7** |

**Cara membaca hasil ini:** `Vfru` memisahkan dua kelas dengan sempurna, tetapi tiap kelas hanya berasal dari **satu orang**. Perbedaan orang, hari, strip, dan kontak konektor tidak bisa dipisahkan dari efek glukosa. Pola "148 lebih rendah dari 88" juga berlawanan dengan logika biologis. Kesimpulan: **data cukup untuk membuktikan alur sistem, bukan untuk membuktikan akurasi prediksi.**

Kanal glukosa (`Vglu`, `I_nA`) konstan karena jenuh (§5) dan tidak membawa informasi; jangan dipakai sebagai fitur.

### 14.2 Hasil audit: sistem end-to-end sudah ada

Sumber: `PANDUAN_SIMULASI_END_TO_END.md`, `app/backend/src`, `ml_pipeline/src`. 

```
ESP32 --MQTT publish--> HiveMQ --> Backend Express (Railway) --> Postgres: sensor_readings
  ^   glicovia/devices/<code>/readings        |
  |                                           +--HTTP POST /predict--> ML service FastAPI (SVR)
  +-----MQTT subscribe <------ publish <------+          |
  glicovia/devices/<code>/predictions                    v
                                              Postgres: prediction_results --> Website Next.js (Vercel)
```

| Komponen | Lokasi | Keterangan |
|---|---|---|
| Backend | `app/backend/src` | Modul auth, devices, pairing, readings, inference, predictions, models, MQTT handler. Setelah inferensi, hasil dipublish balik ke topik prediksi (`inference.service.ts` memanggil `publishMqttMessage`). |
| ML service | `ml_pipeline/src/api_connector.py` | FastAPI: `/health`, `/model-info`, `/predict`, `/predict-batch`, `/train`. |
| Fitur model | `ml_pipeline/src/inference.py:39` | `FEATURE_ORDER = [glucose_saliva, ph_value, fructosamine_umol_l]` |
| Website | `app/web/src/app/` | Halaman `overview`, `readings`, `predictions`, `devices`, `operator`. Produksi: Vercel. |
| Firmware | `firmware/firmware.ino` | Sudah publish ke `.../readings` dan subscribe `.../predictions`, parse `glucose_estimate`, `clinical_category`, `confidence_score`. |

Implikasi: yang kurang bukan infrastruktur, melainkan **jembatan hardware → model** (§14.3).

### 14.3 Celah integrasi (terverifikasi dari kode)

1. **Model dilatih dari data dummy**, bukan data alat: 150 sampel sintetis dari `generate_dummy.py` (rata-rata kelas: fruktosamin 220/285/375 µmol/L, pH 7,0/6,5/6,0, glukosa saliva 0,5/1,2/3,5).
2. **ML service menolak input di luar rentang.** `api_connector.py:44-46` memakai `Field(ge=..., le=...)`. Rentang pelatihan: `glucose_saliva` 0,1–10; `ph_value` 4–9; `fructosamine_umol_l` 150–500. Volt mentah (mis. `Vfru` = 0,5) akan ditolak (HTTP 422), jadi tidak ada prediksi.
3. **Hardware tidak menghasilkan satuan itu.** Tidak ada µmol/L (kanal ke-3 bukan fruktosamin), dan glukosa saliva belum terkalibrasi.
4. **Firmware online mengirim tiap 5 detik terus-menerus**, termasuk saat strip kering (nilai acak). Setiap kiriman memicu inferensi dan menyimpan baris.
5. **Layar prediksi di OLED hanya tampil 15 detik** (`firmware.ino`: `millis() - lastPredReceivedTime < 15000`).
6. **Format pesan sudah cocok:** firmware kirim `ph`, `fructosamine`, `salivary_glucose`; backend memetakan ke fitur ML (`inference.service.ts:167-169`); respons ke alat memakai `glucose_estimate`, `clinical_category`, `confidence_score`. Tidak perlu mengubah nama field.

### 14.4 Dua opsi jalur prototipe

| | Opsi A: demo cepat | Opsi B: jujur (disarankan) |
|---|---|---|
| Model | Tetap model dummy | Latih ulang dari 7 sesi nyata (`POST /train` atau `train_svm.py`) sebagai klasifikasi 2 kelas |
| Isi tiga field | Skala linear dari volt ke rentang dummy (mis. `Vfru` → 150–500) | Tetap tiga nama field, isi dengan sinyal alat apa adanya (pH terkalibrasi, `Vfru`, glukosa konstan/dibuang) |
| Perubahan kode | Hanya firmware (fungsi skala) | Firmware + ubah `FEATURE_BOUNDS` / rentang validasi di ML service + latih ulang |
| Ketahanan | Angka terlihat realistis tetapi **karangan**; mudah ketahuan bila diuji sampel lain | Angka hanya 88 atau 148 (dua kelas); jujur soal batas |
| Risiko saat ditanya penguji | Tinggi | Rendah |

Rekomendasi: **Opsi B**. Bila memilih A, label di layar dan laporan wajib "SIMULASI/DEMO" dan skala wajib dicatat tertulis.

### 14.5 Langkah kerja (urutan)

1. **Perbaiki firmware kirim data**: gunakan mode ukur (deteksi sampel → tunggu stabil → ambil N sampel → trimmed mean) dari `masHaikalKeren.cpp`, kirim **satu** payload per pengukuran. Tolak kirim bila jenuh atau CV > 10% (khusus prototipe ini jenuh diterima, tapi harus ditandai di payload: `"saturated": true`).
2. **pH ke satuan riil**: kalibrasi buffer 4,01 / 6,86 / 9,18 (`calibrate.py`), simpan `m` dan `c` di NVS. Kanal ini tidak butuh kanal glukosa, tetapi satuan riil baru sah bila kalibrasi lulus kriteria §15.3. **Data kalibrasi lama belum memenuhi (lihat §15.9), jadi harus diulang.**
3. **Siapkan data latih** dari `DATA/*.csv`: ringkas per file, buang `Vglu` dan `I_nA`, beri label 88 / 148. Simpan sebagai CSV baru; **jangan menimpa** `ml_pipeline/data/dummy/generated_data.csv`.
4. **Latih model baru** (versi baru, bukan menimpa `best_model.pkl` dummy tanpa cadangan), validasi *leave-one-session-out*, catat akurasi apa adanya.
5. **Longgarkan validasi rentang** di ML service sesuai fitur baru, atau skala di firmware (Opsi A).
6. **Pairing device**: `GLICO-01` harus berstatus `paired` dan punya `device_assignments` aktif ke akun, kalau tidak hasil tidak muncul di website (`PANDUAN_SIMULASI_END_TO_END.md` §2).
7. **Uji dengan simulator dulu**: `scripts/simulate_device.js` (`NODE_PATH=app/backend/node_modules node scripts/simulate_device.js ...`) sebelum alat fisik.
8. **Uji alat fisik**: tetes sampel → OLED menampilkan hasil → cek halaman `predictions` di website.

### 14.6 Tampilan hasil

**OLED 1,3" (128x64)** — tiga layar:
- Ukur: `Teteskan sampel…` → `Menunggu stabil 60s…` (hitung mundur).
- Hasil: baris 1 `Glukosa darah ~ 148 mg/dL`, baris 2 kategori (`Normal` / `Pre-Diabetes` / `Diabetes`), baris 3 `pH 6.8`, baris 4 `PROTOTIPE`.
- Error: `Sensor jenuh` / `Kontak strip` / `WiFi putus`.
Perubahan firmware: tahan layar hasil sampai pengukuran berikutnya (hapus batas 15 detik), tambah penanda `PROTOTIPE`.

**Website** — sudah ada (`readings`, `predictions`, `overview`). Syarat: device terpasang ke akun (langkah 6). Tambahkan di tampilan: badge **"Prototipe — model dilatih dari 2 sampel"** dan tampilkan `model_version` bila tersedia, supaya hasil tidak disalahartikan.

### 14.7 Keamanan: perlu tindakan sekarang

`PANDUAN_SIMULASI_END_TO_END.md` (file **terlacak git**) berisi connection string Postgres Railway lengkap dengan password. Jika repo pernah di-push ke remote, anggap kredensial itu bocor:
1. Rotasi password database di Railway.
2. Ganti isi panduan dengan `$DATABASE_URL` dari `.env`.
3. Periksa riwayat git bila repo publik.

Juga: broker `broker.hivemq.com` bersifat publik tanpa autentikasi; topik `glicovia/devices/GLICO-01/*` dapat dibaca atau dikirimi pesan siapa pun. Untuk data kesehatan, pindah ke broker privat + TLS sebelum uji pada manusia.

### 14.8 Definisi selesai (prototipe)

- Tetes sampel → ≤ 90 detik → OLED menampilkan kategori + angka, dan baris yang sama muncul di website.
- Setiap tampilan bertanda **PROTOTIPE**.
- Tidak ada angka glukosa darah yang diklaim sebagai akurat; laporan menyebut jumlah sampel (2 orang, 7 sesi).
- Kredensial bocor sudah dirotasi.

### 14.9 Belum diverifikasi

- Kode halaman website (`app/web`) belum dibaca; asumsi fitur berasal dari `PANDUAN_SIMULASI_END_TO_END.md`.
- Status deployment Railway/Vercel saat ini belum dicek (apakah model yang berjalan = `best_model.pkl` di repo).
- Isi `ranges` di `api_connector.py` belum dibaca baris per baris; angka rentang diambil dari `generate_dummy.py` (`FEATURE_BOUNDS`).
- Jenis controller OLED 1,3" milik tim (SH1106 vs SSD1306) belum dikonfirmasi.

---

## 15. Prosedur kalibrasi

Tujuan: mengubah sinyal alat menjadi satuan riil lewat fungsi linear yang dicari dari larutan standar, lalu menyimpannya di firmware (NVS ESP32).

| Parameter | Fungsi | Cari dari |
|---|---|---|
| pH | `V = m·pH + c`, dipakai `pH = (V − c)/m` | Buffer 4,01 / 6,86 / 9,18 |
| Glukosa saliva | `I = a·C + b`, dipakai `C = (I − b)/a`, dengan `I = (VMID − Vout)/Rf` | Larutan glukosa standar |
| Fruktosamin | Sama seperti glukosa | Hanya sah dengan enzim spesifik + kalibrator fruktosamin (lihat 15.6) |

### 15.1 Urutan wajib
1. Perbaiki hardware (VMID 1,65 V, kanal tidak jenuh) — kalibrasi **berlaku hanya untuk kondisi hardware yang sama**.
2. Kalibrasi pH → kalibrasi glukosa.
3. Kunci hardware (jangan ubah VMID, Rf, bias) lalu ambil data subjek.
4. Ulangi kalibrasi bila: hardware diubah, lot strip berganti, uji harian gagal (15.7).

### 15.2 Prasyarat (cek sebelum mulai)
- VMID terukur 1,65 V ±2% (multimeter).
- Peta kanal tetap: A0 fruktosa, A1 glukosa, A2 pH, A3 VMID.
- Strip kering terbaca: `Vglu` tidak menempel di ~0 V dan tidak mengambang liar (3 V acak). Gunakan perintah `live`.
- Suhu larutan sekitar 25 °C dan sama untuk semua titik (catat). Nernst bergantung suhu (59,16 mV/pH pada 25 °C).
- Radio WiFi mati selama pengukuran (firmware prototipe sudah mematikannya).
- Strip dari lot yang sama dengan yang dipakai pada subjek. Catat kode lot.

### 15.3 Kalibrasi pH
**Bahan:** buffer 4,01; 6,86; 9,18 (segar, tidak kedaluwarsa); air DI; tisu; strip SPCE. Opsional buffer 7,00 sebagai titik uji (tidak ikut fit).

**Langkah** (strip terbatas, lihat §16: satu strip polos dipakai ulang untuk ketiga buffer, satu strip lain untuk verifikasi):
1. Strip baru, sambung ke konektor. Jalankan `live` dan pastikan tidak mengambang.
2. Teteskan buffer **dari pH rendah ke tinggi** (4,01 → 6,86 → 9,18), tutup ketiga elektroda.
3. Tunggu stabil: pantau `VpH` dengan `live`. Stabil bila perubahan < 0,5 mV dalam 15 detik. Minimal tunggu 60 detik.
4. Ketik `cal ph 4.01` (isi sesuai buffer). Firmware mengambil 40 pembacaan, mencatat rata-rata terpangkas dan SD.
5. Antar buffer: bilas air DI, blot, **pakai strip yang sama**. Setelah 9,18, ukur ulang 4,01 pada strip itu: selisih terhadap pembacaan awal ≤ 3 mV (usulan awal, untuk mendeteksi drift/histeresis). Bila lebih besar, kalibrasi diragukan.
6. Setelah ≥3 titik: `fit ph`.

**Kriteria lulus (otomatis dicek firmware):**
- R² ≥ 0,99.
- |kemiringan| ≥ 40 mV/pH (≥ ~70% Nernst). Di bawah itu resolusi pH tidak memadai: ADS1115 GAIN_ONE = 0,125 mV/bit, jadi 0,1 pH butuh ≥ 4 mV agar tidak tenggelam di derau.
- SD pada tiap titik ≤ 1 mV.
- Tanda kemiringan **negatif** (tegangan turun saat pH naik) bila rangkaian sama seperti catatan Nernst proyek ini.

Bila tidak lulus firmware tidak menyimpan (kecuali `fit ph force`). Jangan memakai `force` untuk data laporan.

**Verifikasi:** ukur buffer 7,00 (tidak dipakai fit) dengan mode ukur. Galat ≤ 0,1 pH.

### 15.4 Kalibrasi glukosa saliva
**Syarat awal:** kanal tidak jenuh pada strip basah tanpa glukosa (Vout jauh dari 0 V dan 3,3 V). Bila jenuh, firmware menolak titik (`DITOLAK: kanal glukosa jenuh`).

**Bahan:** glukosa stok 100 mg/dL dalam PBS atau saliva buatan pH 6,8–7,4 (bukan air DI: matriks ion mempengaruhi arus); strip SPCE ber-enzim glukosa; pipet.

**Konsentrasi (mg/dL):** 0 (blanko), 0,5, 1, 2, 5, 10. Rentang ini sama dengan rentang masukan model (`glucose_saliva` 0,1–10). Buat dari pengenceran bertingkat, **segar** (≤ 4 jam).

**Langkah:**
1. Untuk tiap konsentrasi, **3 strip berbeda** (replikat).
2. Teteskan, tunggu 60 detik (lewati arus pengisian), `cal glu <konsentrasi>`.
3. Setelah semua titik: `fit glu`.

**Kriteria lulus:** R² ≥ 0,98; kemiringan positif; tidak ada titik dengan jenuh > 10%; CV replikat titik tengah ≤ 10%.
**Dilaporkan:** LOD = 3·SD(blanko)/a, LOQ = 10·SD(blanko)/a, dan rentang linear. Konsentrasi di luar rentang linear tidak boleh diekstrapolasi.

### 15.5 Pencatatan (lembar tiap sesi kalibrasi)
| Tanggal | Parameter | Lot strip | Suhu | Titik (x → y) | m/c atau a/b | R² | SD | cal_version | Lulus? |
|---|---|---|---|---|---|---|---|---|---|
Simpan juga CSV Serial. `cal_version` ikut di setiap payload sehingga data bisa dihitung ulang bila kalibrasi diperbaiki.

### 15.6 Fruktosamin
Tidak dikalibrasi pada prototipe. Alasan: kanal ketiga memakai enzim glukosa, bukan enzim fruktosamin, jadi tidak ada hubungan terhadap fruktosamin. Prosedur bila enzim yang benar tersedia: sama dengan 15.4, tetapi dengan kalibrator fruktosamin (mis. 1-deoxy-1-morpholino-D-fructose, umum dipakai sebagai kalibrator uji fruktosamin) pada rentang 100–500 µmol/L, dan **rentang itu perlu dipastikan dari literatur untuk saliva** (rentang 150–500 µmol/L di model berasal dari data dummy, mirip rentang serum). Sampai itu tersedia, payload mengisi `fructosamine` dengan volt dan `units.fructosamine = "V"`.

### 15.7 Uji harian (pemeriksaan drift)
Sebelum sesi pengambilan data: ukur buffer 6,86 dengan strip baru. Bila |pH terukur − 6,86| > 0,1, ulangi kalibrasi pH. Catat hasilnya di lembar 15.5.

### 15.8 Pemakaian di firmware
`firmware_prototipe/firmware_prototipe.ino` menyediakan perintah Serial `cal ph <pH>`, `cal glu <mg/dL>`, `fit ph|glu [force]`, `show`, `clear`, `live`, dan `m` (atau tombol BOOT) untuk pengukuran. Koefisien disimpan di NVS (bertahan setelah mati). Koefisien yang dihitung di luar (mis. dari log `masHaikalKeren.cpp` + `calibrate.py`) dimasukkan dengan `set ph <m> <c>` / `set glu <a> <b>`. Sebelum pH terkalibrasi, firmware **tidak mengirim ke cloud** (`REQUIRE_PH_CAL`), supaya kolom `ph` database tidak berisi volt.

### 15.9 Temuan: data kalibrasi pH yang ada belum bisa dipakai
File di `data_log/` (buffer 4,01; 6,86; 9,18) sudah dibaca (stabilitas per seperempat durasi):

| Buffer | Kanal di file | Hasil |
|---|---|---|
| 4,01 | A2 | **Stabil** ≈ 85,4 mV (SD 0,2 mV). Catatan analisis lama mencatat 76,8 mV untuk buffer yang sama → selisih ±9 mV ≈ 0,15 pH antar sesi/strip. |
| 6,86 | A1 | **Tidak stabil**: mulai mengambang sampai 2,98 V, lalu meluruh 0,56 → 0,024 → 0,007 → ~0,001 V dan belum mendatar. |
| 9,18 | A1 | **Mengambang liar** 0–3,36 V, lalu menempel di 0 V. |

Kesimpulan: tiga titik itu **tidak bisa di-fit**. Kanal pH berbeda antar file (A2 untuk 4,01; A1 untuk dua lainnya), dua titik terakhir tidak mencapai kondisi mantap, dan nilai ~0 V mengarah ke rel bawah yang sama seperti masalah di §5. Dua titik yang tersedia (4,01 → ~1 mV pada 6,86) memberi kemiringan ≈ −30 mV/pH, tetapi itu tidak boleh dipakai karena titik kedua belum mantap. **"pH sudah bisa" belum terbukti**; kalibrasi pH harus diulang dengan prosedur 15.3 setelah hardware dibenahi.

---

## 16. Anggaran strip

Sisa strip: **24 = 22 polos + 2 ber-enzim glukosa**. Satu pengukuran = 3 strip (pH, glukosa, fruktosa), jadi hanya **satu** pengukuran berenzim yang masih mungkin.

| Penggunaan | Polos | Enzim | Catatan |
|---|---|---|---|
| Diagnosis saturasi (strip dipakai ulang, bilas) | 2 | 0 | Buffer/air garam pada strip polos: bila `Vglu` tetap terjepit, penyebabnya bias/korslet, bukan enzim |
| Kalibrasi pH (1 strip lintas 3 buffer + 1 verifikasi) | 2 | 0 | §15.3 |
| Uji go/no-go kanal glukosa: blanko vs 5 mg/dL | 0 | 2 | Hanya setelah kanal terbukti tidak jenuh |
| 5 orang × 1 sampel × 3 strip polos | 15 | 0 | Sinyal non-spesifik (lihat bawah) |
| Cadangan | 3 | 0 | Strip cacat / ulang |
| **Total** | **22** | **2** | |

Konsekuensi:
1. **Kalibrasi glukosa penuh (§15.4) tidak mungkin**: butuh ≥ 5 konsentrasi × 3 replikat = 15 strip enzim, tersedia 2. Uji go/no-go (blanko vs satu konsentrasi) hanya menunjukkan apakah kanal merespons, bukan memberi kurva kalibrasi. Satuan mg/dL untuk glukosa saliva tidak akan tercapai dengan strip yang ada.
2. **Pengukuran subjek memakai strip polos di ketiga kanal.** Sinyalnya non-spesifik (pH, kekuatan ion, redoks latar), bukan glukosa-enzimatik. Ini sejalan dengan pendekatan ML pada pola sinyal (§14), tetapi **tidak sebanding** dengan 7 sesi lama bila sesi itu memakai strip berenzim. Catat `strip_type` (polos/enzim) per kanal di setiap data, dan jangan campur tanpa dicek.
3. Urutan keputusan: diagnosis saturasi (strip polos) → bila `Vglu` bebas jenuh, pakai 2 strip enzim untuk go/no-go → pengambilan data subjek.

---

## 17. Progres & keputusan (2026-10-22): Opsi B dijalankan

### 17.1 Keputusan

| ID | Keputusan | Alasan |
|---|---|---|
| K1 | Pakai **Opsi B** (§14.4): latih ulang dari data alat nyata, bukan skala ke rentang dummy. | Jujur soal batas data; risiko rendah saat ditanya penguji. |
| K2 | Model = **klasifikasi 2 kelas** (SVC), keluaran langsung **88** atau **148** mg/dL. Bukan regresi. | Hanya 2 nilai label; regresi mg/dL tidak bermakna. |
| K3 | Fitur awal **`v_fru` saja** (volt). `v_glu` dan `v_ph` ikut dikirim tapi **tidak dipakai model**. | `v_glu` jenuh (§5). `v_ph` saja hanya 4/7. `v_fru` ditambah `v_ph` tidak lebih baik (7/7, sama). |
| K4 | Fitur **volt mentah**, bukan nilai konversi. Nilai terkonversi (pH) menyusul setelah kalibrasi lulus (§15.3). | Tidak ada konversi sah untuk fruktosamin/glukosa. Volt dari `raw` bisa dihitung ulang bila kalibrasi berubah. |
| K5 | Data bertambah → **latih ulang dari seluruh CSV**, bukan menambah ke model lama. | SVM scikit-learn tidak punya `partial_fit`. Pelatihan hitungan detik. |
| K6 | Model baru **tidak menimpa** `best_model.pkl` dummy. Dipilih lewat env `GLICO_MODEL_PATH`. | Cadangan dan bisa kembali ke model lama. |
| K7 | `subject_code` = `S148` / `S088` (1 orang per kelas). | **Asumsi**, D3 (§13) belum dijawab. Ganti bila ternyata bukan itu. |

### 17.2 Yang sudah dikerjakan

| Berkas | Perubahan |
|---|---|
| `hardware/kodeMasHaikal/main.cpp` | Ditambah WiFi + MQTT. `measure()` kirim **satu** payload JSON per pengukuran (`ph`, `fructosamine`, `salivary_glucose`, `units`, `raw`, `quality`, `fw_version`) ke `glicovia/devices/GLICO-01/readings`. `PH_M`/`PH_C` = 0 → `ph: null`. Balasan prediksi hanya dicetak ke Serial (tanpa OLED). **Belum dikompilasi** (tidak ada PlatformIO/arduino-cli di mesin). Tambahan: `secrets.example.h`, `.gitignore`. |
| `ml_pipeline/src/build_real_dataset.py` (baru) | `hardware/DATA/*.csv` → `ml_pipeline/data/real/train.csv`. 1 baris per sesi = median separuh akhir. Label dari nama file. Idempoten. |
| `ml_pipeline/src/train_real.py` (baru) | Latih SVC, validasi leave-one-session-out, simpan `src/models/real/model_real_<versi>.pkl` + `.json`. |
| `ml_pipeline/src/api_connector.py` | Bila `GLICO_MODEL_PATH` diset: model dari path itu, batas masukan dilonggarkan ke batas kewajaran (0–1000 / pH 0–14), scaler eksternal dummy **dimatikan**, `/model-info` melaporkan `real-<versi>`. Tanpa env, perilaku lama tidak berubah. |
| `app/backend/.../inference.service.ts` | Bila kolom `ph`/`salivary_glucose`/`fructosamine` bernilai `null`, pakai volt dari `raw_payload.raw` (`v_ph`, `v_glu`, `v_fru`). Sebelumnya `ph: null` membuat inferensi gagal 422. |

### 17.3 Hasil

Data latih (`train.csv`): 7 sesi, 2 subjek (cocok dengan tabel §14.1).

| Fitur | Leave-one-session-out |
|---|---|
| `v_fru` (dipakai, K3) | 7/7 |
| `v_ph` | 4/7 |
| `v_fru` + `v_ph` | 7/7 |

Uji lewat `/predict` (model nyata, `GLICO_MODEL_PATH`): `v_fru` 0,0003 dan 0,0029 → **148** (Diabetes); 0,5262 dan 0,5918 → **88** (Normal). `tsc --noEmit` backend bersih. `pytest` ml_pipeline: 23 lulus, 1 gagal (`test_visualization.py::test_visualization_functions_work_with_fructosamine`), **gagal juga sebelum perubahan ini**.

**Cara membaca (penting):** 7/7 **tidak membuktikan** model memprediksi glukosa. Tiap kelas berasal dari satu orang, jadi LOSO tetap melatih dengan sesi lain dari orang yang sama. Perbedaan `v_fru` bisa berasal dari orang, hari, atau kontak strip (§5.4, §14.1). Model baru layak dilaporkan setelah syarat data §8 terpenuhi. Nilai di antara kedua kelas (mis. `v_fru` ≈ 0,27 memberi ~120 mg/dL) adalah artefak rata-rata dari estimasi kepercayaan di `inference.py`, **bukan prediksi nyata**.

### 17.4 Cara pakai

```bash
cd ml_pipeline
.venv/bin/python -m src.build_real_dataset          # setelah menambah CSV ke hardware/DATA/
.venv/bin/python -m src.train_real --version v2     # latih ulang, versi baru
GLICO_MODEL_PATH=src/models/real/model_real_v2.pkl uvicorn src.api_connector:app --port 8080
```
Nama file CSV baru harus `glicovia_<glukosa_darah>_<KELAS>_<tanggal>.csv`. Kalau ada orang baru, ubah kolom `subject_code` di `train.csv` atau di `build_real_dataset.py` agar validasi per orang bisa dipakai.

### 17.5 Belum dikerjakan

1. **Deploy ke Railway**: set `GLICO_MODEL_PATH` pada ML service dan sertakan `src/models/real/model_real_v1.pkl` + `.json` di image. Pada deploy lama model dummy tetap berjalan.
2. **Uji `scripts/simulate_device.js`** terhadap ML service + backend lokal (butuh Postgres/MQTT).
3. **Pairing `GLICO-01`** ke akun agar hasil muncul di website (§14.5 langkah 6).
4. **Kompilasi dan uji `main.cpp`** di alat; isi `PH_M`/`PH_C` setelah kalibrasi pH lulus.
5. **Badge "Prototipe — model dilatih dari 2 sampel"** di website (§14.6).
6. **Rotasi kredensial Postgres** dan pindah dari broker MQTT publik (§14.7). Masih terbuka.
7. Pengambilan data subjek baru (target §8). Ini yang menentukan apakah model bermakna.
