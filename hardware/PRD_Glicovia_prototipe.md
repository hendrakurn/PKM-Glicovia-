# PRD — Glicovia Prototipe End-to-End (data terbatas)

| | |
|---|---|
| Versi | 0.1 (draft, menunggu persetujuan tim) |
| Tanggal | 2026-10-22 |
| Induk | `hardware/PRD_Glicovia.md` (§14–17: progres Opsi B, keputusan K1–K7) |
| Status | Alur lokal terbukti jalan. Kalibrasi masih **sementara**. Akurasi prediksi **belum terbukti**. |

---

## 1. Ringkasan

Dokumen ini merinci rancangan prototipe end-to-end yang dibangun dari data yang sudah direkam di `hardware/data_log/` dan `hardware/DATA/`:

```
ESP32 (main.cpp) --MQTT--> Backend --> Postgres (sensor_readings)
                              |  konversi volt -> satuan riil (bila perlu)
                              +--HTTP /predict--> ML service (SVR) --> Postgres (prediction_results)
                              +--MQTT publish--> topik predictions --> OLED alat
Website <-- Backend <-- Postgres
```

Tujuan: membuktikan **alur** (tetes sampel → prediksi tampil di alat dan di website) memakai data nyata yang ada. Bukan membuktikan alat memprediksi glukosa darah dengan akurat. Lihat §7.

## 2. Keputusan desain

Melanjutkan K1–K7 di PRD induk.

| ID | Keputusan | Alasan |
|---|---|---|
| K8 | Firmware **selalu** mengirim volt mentah di `raw` (`v_ph`, `v_fru`, `v_glu`, `v_mid`, `i_glu_nA`). Kolom `ph`, `fructosamine`, `salivary_glucose` berisi volt atau `null` sebelum kalibrasi, ditandai lewat `units`. | Tidak ada konversi sah di alat. Volt mentah memungkinkan hitung ulang bila kalibrasi berubah. |
| K9 | **Backend** yang mengonversi volt ke satuan riil, dan keputusannya lewat `units.<param>`, **bukan lewat `null`**. | `main.cpp` mengirim fruktosamin sebagai volt yang bukan `null`. Aturan "konversi bila null" akan memperlakukan 0,53 sebagai µmol/L. |
| K10 | Model SVR dilatih dari fitur **satuan riil** (`glucose_saliva`, `ph_value`, `fructosamine_umol_l`) memakai kalibrasi sementara §4.3. Skema sama dengan `ml_pipeline/data/dummy/generated_data.csv`. | Memakai kontrak fitur ML service yang sudah ada tanpa mengubah `FEATURE_ORDER`. |
| K11 | Validasi **per sesi** (leave-one-session-out, grid search dengan GroupKFold). Skor per baris tidak dilaporkan. | Baris satu sesi hampir identik, jadi pembagian per baris bocor (MAE 0,1 palsu). |
| K12 | Fitur model = `ph_value` + `fructosamine_umol_l`. `glucose_saliva` tetap dikirim tetapi **tidak dipakai** model. | Kanal glukosa jenuh (≈7160 nA konstan), tidak membawa informasi. |
| K13 | Label glukosa darah: angka dari nama file (88, 148). Sesi tanpa angka (`DIABETES_1`, `DIABETES_1_1`) diberi nilai default kelas 148 dan ditandai `label_source = assumed`. | Label perkiraan, sesuai arahan tim. Ganti dengan angka glukometer bila ada. |
| K14 | Model baru **tidak menimpa** `best_model.pkl`. Dipilih lewat env `GLICO_MODEL_PATH`. | Sama dengan K6. |
| K15 | Koefisien kalibrasi sementara hidup di **dua tempat** dan harus diubah bersamaan: `PROVISIONAL_CAL` di `inference.service.ts` dan `CAL` di `convert_data_log.py`. Keduanya saling merujuk lewat komentar. | Pelatihan dan inferensi wajib memakai fitur yang sama. |

## 3. Kontrak data

### 3.1 Payload alat → backend (format `main.cpp` v0.3.0)

Sebelum kalibrasi:

```json
{
  "device_code": "GLICO-01",
  "ph": null,
  "fructosamine": 0.5262,
  "salivary_glucose": 0.0050,
  "units": {"ph": "none", "fructosamine": "V", "salivary_glucose": "V"},
  "raw": {"v_ph": 0.0548, "v_fru": 0.5262, "v_glu": 0.0050, "v_mid": 0.913, "i_glu_nA": 7158},
  "quality": {"n": 40, "n_sat": 40, "saturated": true, "cv_pct": 1.2},
  "fw_version": "0.3.0"
}
```

Satu payload per pengukuran (sekali setelah `m` + trigger + tunggu 60 s + 40 sampel). Monitor kontinu tiap 250 ms hanya ke Serial.

### 3.2 Aturan keputusan di backend

`mapSensorReadingToMlPayload` (`app/backend/src/modules/inference/inference.service.ts`), per parameter:

| Kondisi | Nilai yang dipakai |
|---|---|
| `units.<param>` = satuan riil (`pH`, `mg/dL`, `umol/L` / `µmol/L`) | Nilai kolom, apa adanya |
| `units.<param>` ada tetapi bukan satuan riil (`V`, `none`) | Hitung dari `raw` (rumus §3.3) |
| Tidak ada `units` (firmware lama) | Nilai kolom bila bukan `null`, selain itu hitung dari `raw` |
| Volt yang dibutuhkan tidak ada | Error 422, prediksi dicatat `failed` |

Setiap pemakaian jalur hitung dari `raw` dicatat sebagai peringatan `provisional` di log backend.

### 3.3 Rumus konversi sementara

`Rf` = 100 kΩ. Hasil dipotong ke batas model.

| Parameter | Rumus | Koefisien | Batas |
|---|---|---|---|
| pH | `pH = (V − c) / m` | `m = −0,05916` V/pH, `c = 0,3226` V | 4–9 |
| Glukosa saliva | `C = (I − b) / a`, `I = i_glu_nA` | `a = 1000` nA per mg/dL, `b = 0` | 0,1–10 |
| Fruktosamin | `C = (I − b) / a`, `I = (v_mid − v_fru)/Rf × 10⁹` nA | `a = 35` nA per µmol/L, `b = −4000` nA | 150–500 |

### 3.4 Asal koefisien (semuanya sementara, **bukan hasil fit**)

| Koefisien | Asal | Seberapa sah |
|---|---|---|
| pH `m` | Slope Nernst ideal 59,16 mV/pH pada 25 °C | Asumsi |
| pH `c` | Jangkar: buffer 4,01 → 85,4 mV (satu-satunya titik stabil, PRD §15.9) | Satu titik |
| Glukosa `a`, `b` | Tebakan | Arbitrer. Kanal jenuh, hasil ≈ 7,16 untuk semua sampel |
| Fruktosamin `a`, `b` | Dua jangkar yang dipilih: 3700 nA → 220 dan 9100 nA → 374 (rata-rata kelas Normal dan Diabetes pada data dummy) | Dipasang pada dua kelas yang sedang dilatih. Memisahkan kelas **menurut rancangan**, bukan bukti |

Konversi fruktosamin ini setara Opsi A di PRD §14.4 (penskalaan ke rentang dummy). Hasilnya **bukan µmol/L sungguhan** dan tidak boleh dilaporkan sebagai itu.

### 3.5 Respons ML service → backend → alat

`/predict` mengembalikan `prediction`, `category`, `confidence`. Backend memetakan ke `glucose_estimate`, `clinical_category`, `confidence_score`, menyimpannya di `prediction_results`, lalu mem-publish ke `glicovia/devices/<code>/predictions`. Kategori: Normal < 100, Pre-Diabetes 100–125, Diabetes ≥ 126 mg/dL.

## 4. Data dan pelatihan

### 4.1 Pembuatan dataset

`ml_pipeline/src/convert_data_log.py` → `ml_pipeline/data/real/generated_data_real.csv` (+ `.meta.json` berisi koefisien dan status `PROVISIONAL`).

- **Sumber:** `hardware/data_log/` dan `hardware/DATA/`. Hanya `glicovia_[<mgdl>_]<KELAS>_..._<tanggal>_<jam>.csv`.
- **Dilewati:** file kalibrasi tanpa header (`6.86`, `9.18`, `pH_4.01`), `saliva_*` (skema lain, tanpa label), dan sesi pendek < 40 baris (`126_PRE-DIABETES`, `TEST`, `glu*`).
- **Duplikat:** `glicovia_DIABETES_<ts>` sama dengan `glicovia_148_DIABETES_<ts>`. Dihitung sekali, nama yang memuat angka diutamakan.
- **Jendela:** separuh akhir tiap sesi dipecah jadi jendela 20 sampel (~5 s), median per jendela.
- **Keluaran:** 63 baris, 9 sesi. Kolom wajib (`id`, `glucose_saliva`, `ph_value`, `fructosamine_umol_l`, `bg_class`, `bg_mgdl_reference`) diikuti kolom audit (`session_id`, `subject_code`, `label_source`, volt mentah, `sat_frac`, `flags`).

```bash
cd ml_pipeline
venv/bin/python -m src.convert_data_log
venv/bin/python -m src.train_real_svr            # menyimpan src/models/real/model_svr_units_v1.{pkl,json}
```

### 4.2 Pelatihan (`ml_pipeline/src/train_real_svr.py`)

`StandardScaler → SVR(rbf)`, grid `C`, `gamma`, `epsilon` dengan `GroupKFold(3)`, evaluasi luar `LeaveOneGroupOut` per `session_id`.

| Fitur | MAE (mg/dL) | Akurasi kategori |
|---|---|---|
| pH + fruktosamin | 2,8–3,0 (bergantung versi scikit-learn) | 100% |
| pH saja | 22,3 | 54% |
| Tebak rata-rata (pembanding) | 30,0 | — |
| Pembagian per baris (bocor) | 0,1 | jangan dilaporkan |

### 4.3 Cara membaca hasil (wajib dibaca)

- MAE rendah berasal dari fruktosamin. Konversi fruktosamin dirancang memisahkan dua kelas, jadi ini bukti **pipeline berjalan**, bukan bukti alat memprediksi glukosa.
- Hanya dua nilai label (88, 148) dari sekitar dua orang. SVR di sini setara klasifikasi dua kelas. Nilai di antara kedua kelas (mis. fruktosamin 295 → ≈108) adalah interpolasi, bukan prediksi nyata.
- Dua sesi `DIABETES_1` terklasifikasi benar, tetapi lemah sebagai bukti: fruktosamin ≈ 354 dekat dengan kelas 148 (≈375), dan label 148 untuk keduanya asumsi. Volt mereka jauh beda dari tiga sesi 148 lainnya (`v_fru` 0,07 V vs 0,0003 V), tanda beda strip atau hari.
- pH hasil konversi (4,5–5,4) tidak masuk akal untuk saliva. 9 baris dari 2 sesi `DIABETES_1` terpotong di batas 4,0 (`ph_value_clip` di `flags`). Penyebabnya kalibrasi pH lama tidak lulus (PRD §15.9).

## 5. Hasil uji (2026-10-22)

Lingkungan lokal: Postgres (Docker, port 5433), backend (5000), ML service (8001, model `real-v1`), HiveMQ publik. Hasil dibaca dari tabel `prediction_results` lokal.

| Jalur | Masukan | Prediksi | Status |
|---|---|---|---|
| `simulate_device.js` (satuan riil, tanpa `units`) | pH 4,65 / fruktosamin 220 | 88,0 Normal | success |
| `simulate_device.js` | pH 5,05 / fruktosamin 375 | 146,2 Diabetes | success |
| Payload gaya `main.cpp` (volt, `units:"V"`), sesi 88 | `v_fru` 0,5262 | 89,4 Normal | success |
| Payload gaya `main.cpp`, sesi 148 | `v_fru` 0,0003 | 146,3 Diabetes | success |

Pengujian tambahan:
- Fungsi pemetaan, empat kasus (belum terkalibrasi, terkalibrasi, tanpa `units`, `v_mid` hilang → 422): lolos. Skrip sekali pakai, belum jadi tes tersimpan (backend tidak punya framework tes).
- `tsc --noEmit` backend: bersih.
- `pytest` ml_pipeline: 23 lulus, 1 gagal (`test_visualization.py::test_visualization_functions_work_with_fructosamine`). Gagal juga sebelum perubahan ini.

**Perbaikan yang ditemukan saat uji:** `_bootstrap_confidence` di `ml_pipeline/src/inference.py` menambah derau acak dengan satu skala (≈1,5) ke semua fitur, sehingga pH bergeser ±1,5 satuan dan prediksi Normal menjadi 120. Sekarang derau 2% per fitur dengan batas bawah 1.

## 6. Temuan dan risiko

| # | Temuan | Dampak | Status |
|---|---|---|---|
| T1 | Broker HiveMQ publik dipakai bersama. Satu pembacaan mendapat **dua balasan**: 176,0 (+1140 ms, model dummy, pengirim belum teridentifikasi, dugaan: backend lain yang ikut berlangganan, mis. deployment Railway) dan 88,0 (+1269 ms, lokal). `simulate_device.js` berhenti pada balasan pertama, sehingga menampilkan angka salah. | Tampilan alat atau simulator bisa salah. Data uji juga bocor ke pihak lain. | **Terbuka**, lihat D8 |
| T2 | Baris dari firmware prototipe menyimpan **volt** di kolom `fructosamine` dan `salivary_glucose`, `ph` kosong. Website membaca kolom itu apa adanya. | Website menampilkan volt seolah satuan riil. | **Terbuka** |
| T3 | Kalibrasi sementara = Opsi A (penskalaan). | Angka µmol/L dan pH tidak sahih. | Diterima untuk prototipe, wajib diberi label |
| T4 | Koefisien ada di dua tempat (K15). | Fitur pelatihan dan inferensi bisa tidak sama bila salah satu diubah. | Dimitigasi komentar silang |
| T5 | Kanal glukosa jenuh. | `glucose_saliva` tidak informatif (K12). | Menunggu perbaikan hardware (PRD §6.1) |
| T6 | Hanya sekitar 2 orang, 2 nilai label. | Model tidak bermakna secara ilmiah. | Menunggu data ≥ 30 subjek (PRD §8) |
| T7 | Railway: build ditunda akibat insiden keamanan. Railway menyarankan mencabut semua variabel lingkungan dan merotasi kredensial. Connection string Postgres Railway ada di `PANDUAN_SIMULASI_END_TO_END.md` (terlacak git). | Deploy ke Railway tertunda. Kredensial dianggap bocor. | Rotasi password, lihat PRD §14.7 |
| T8 | ML service Railway masih berjalan dengan model dummy. | Tidak dipakai sampai `GLICO_MODEL_PATH` diset dan artefak model disertakan di image. | Menunggu Railway pulih |

## 7. Batas klaim

- Setiap tampilan (OLED, website, laporan) bertanda **PROTOTIPE**.
- Angka glukosa darah **tidak diklaim akurat**. Laporan menyebut jumlah sampel (2 orang, 9 sesi, label perkiraan) dan kalibrasi sementara.
- Skor per baris tidak boleh dilaporkan.
- pH dan fruktosamin hasil konversi sementara tidak boleh disebut pengukuran terkalibrasi.

## 8. Pertanyaan terbuka

| ID | Pertanyaan | Opsi |
|---|---|---|
| D8 | Cara menghindari balasan ganda dari broker publik (T1). | **A.** Mosquitto lokal di Docker untuk dev (isolasi penuh; `MQTT_URL` di `.env` backend diubah, `MQTT_HOST` di `secrets.h` ke IP laptop; simulator membaca `MQTT_URL` dari env). **B.** Tetap di HiveMQ publik, ganti prefix topik unik (mengubah konstanta di simulator dan firmware, dan `MQTT_TOPIC_PREFIX` backend). **C.** Tetap seperti sekarang dan matikan backend lain yang ikut berlangganan (bergantung pada akses yang belum dipastikan). Usulan sementara: **A** untuk dev. Produksi: broker privat + TLS + autentikasi. |
| D9 | Angka glukosa darah sesi `DIABETES_1` dan `DIABETES_1_1` (K13) dan status puasa/sewaktu (D3 PRD induk). | Isi dari glukometer bila ada. |
| D10 | Tampilan website untuk baris volt (T2). | Sembunyikan kolom volt, tampilkan nilai konversi + badge `provisional`, atau tampilkan keduanya. |
| D11 | Kanal ke-3: tetap enzim glukosa atau enzim fruktosamin (D1 PRD induk). | Menentukan arti fruktosamin ke depan. |

## 9. Langkah berikut

1. Putuskan D8, lalu terapkan (broker lokal atau prefix unik). Ulangi uji end-to-end sampai hanya satu balasan.
2. Website: penanganan baris volt dan badge **PROTOTIPE** (T2, PRD §14.6). Tampilkan `model_version`.
3. Tandai hasil `provisional` di data yang tersimpan (saat ini hanya log backend).
4. Rotasi kredensial Postgres Railway, ganti isi `PANDUAN_SIMULASI_END_TO_END.md` dengan `$DATABASE_URL` (T7).
5. Setelah Railway pulih: set `GLICO_MODEL_PATH` dan sertakan `model_svr_units_v1.pkl` + `.json` di image ML service.
6. Hardware dan kalibrasi sebenarnya (PRD §6.1, §15): VMID 1,65 V, kanal tidak jenuh, kalibrasi pH 3 buffer, kurva glukosa. Lalu ganti `CAL`/`PROVISIONAL_CAL`, latih ulang, dan firmware mengisi `ph` serta `fructosamine` sendiri (backend otomatis memakai nilai itu lewat `units`).
7. Pengambilan data subjek sesuai PRD §8.

## 10. Kriteria selesai (prototipe)

- Tetes sampel → ≤ 90 s → OLED menampilkan kategori + angka, dan baris yang sama muncul di website.
- Satu pembacaan menghasilkan **satu** prediksi (T1 selesai).
- Setiap tampilan bertanda PROTOTIPE; tidak ada angka diklaim akurat.
- Laporan menyebut 2 orang, 9 sesi, label perkiraan, kalibrasi sementara.
- Kredensial yang bocor sudah dirotasi (T7).

## 11. Perubahan berkas

| Berkas | Perubahan |
|---|---|
| `app/backend/src/modules/inference/inference.service.ts` | Keputusan konversi lewat `units`, `PROVISIONAL_CAL`, batas model. |
| `ml_pipeline/src/convert_data_log.py` (baru) | Konversi log volt → dataset satuan riil. |
| `ml_pipeline/src/train_real_svr.py` (baru) | SVR dengan validasi per sesi. |
| `ml_pipeline/src/inference.py` | Derau bootstrap per fitur (baris 142). |
| `ml_pipeline/data/real/generated_data_real.csv` + `.meta.json` (baru) | Dataset latih dan metadata kalibrasi. |
| `ml_pipeline/src/models/real/model_svr_units_v1.{pkl,json}` (baru) | Model SVR satuan riil. |
| `run_all.sh` | ML service dijalankan dengan `GLICO_MODEL_PATH`. |
