# PRD — Machine Learning Glicovia: Klasifikasi Kelas Glukosa Darah dari Saliva

| | |
|---|---|
| Versi | 0.1 (draft) |
| Tanggal | 2026-10-26 |
| Tim | PKM-KC Glicovia |
| Lingkup | Folder `ml_pipeline/` (data → latih → evaluasi → inferensi → API) |
| Dokumen induk | `hardware/PRD_Glicovia.md` (§8 Model SVM, §9 Kriteria penerimaan) |

---

## 1. Ringkasan

Modul ML Glicovia menerima pembacaan sensor saliva (pH, glukosa, kanal ke-3) dari alat, lalu mengeluarkan **kelas kategori glukosa darah** sebagai **output utama**: `NORMAL`, `PREDIABETES`, atau `DIABETES`, beserta skor keyakinan.

**Perubahan arah dari PRD hardware §8.** PRD hardware menetapkan SVR (regresi mg/dL) sebagai model utama dan SVC hanya pembanding. Dokumen ini membalik itu:

| | PRD hardware §8 | PRD ini |
|---|---|---|
| Model utama | SVR → angka mg/dL, kelas diturunkan | **SVC → kelas langsung** |
| SVR | Utama | Pembanding / jalur riset |
| Output ke alat | `glucose_estimate` + kategori | **Kategori + probabilitas**; `glucose_estimate` opsional |

Alasan: data nyata masih sedikit dan berkelompok pada kelas diskret (88 dan 148 mg/dL). Klasifikasi lebih jujur terhadap bentuk data itu daripada regresi yang mengklaim presisi angka. Skrining juga butuh kategori, bukan angka persis.

Alat ini **skrining awal, bukan diagnosis**.

## 2. Masalah & tujuan

**Masalah.** Cek gula darah memerlukan tusuk jari. Tim ingin skrining non-invasif lewat saliva.

**Tujuan ML**
1. Mengklasifikasi sampel saliva ke kelas glukosa darah (3 kelas, §5).
2. Memberi skor keyakinan per prediksi, dan menolak (`uncertain`) bila ragu atau input di luar jangkauan.
3. Melayani prediksi lewat API (FastAPI, Railway) dengan latensi ≤ 2 detik.
4. Menjadikan seluruh pelatihan **dapat diulang**: satu perintah dari data log mentah sampai artefak model + metrik.
5. Mengevaluasi hanya pada **subjek yang tidak pernah dilihat model**.

**Bukan tujuan (v1):** diagnosis medis, prediksi angka mg/dL yang diklaim akurat, deep learning, pelatihan online, sertifikasi regulator.

## 3. Kondisi saat ini (as-is)

### 3.1 Kode yang sudah ada

| Komponen | File | Jenis | Status |
|---|---|---|---|
| Data dummy | `src/generate_dummy.py` | Sintetis | Ada |
| Loader, preprocessing | `src/data_loader.py`, `src/preprocessing.py` | — | Ada, ber-tes |
| SVR + GridSearchCV + K-Fold | `src/train_svm.py` | Regresi | Ada, jalur lama |
| Perbandingan model | `src/model_comparison.py` | Regresi | Ada, ber-tes |
| Evaluasi, visualisasi | `src/evaluate.py`, `src/visualization.py` | Metrik regresi + kelas turunan | Ada |
| Data log → dataset | `src/build_real_dataset.py`, `src/convert_data_log.py` | — | Ada |
| **SVC data nyata** | `src/train_real.py` | **Klasifikasi** | Ada, **kerangka awal fitur ini** |
| SVR data nyata | `src/train_real_svr.py` | Regresi | Ada |
| Inferensi, API | `src/inference.py`, `src/api_connector.py` | Regresi dulu | Ada, perlu adaptasi |

`train_real.py` sudah memuat `Pipeline(StandardScaler → SVC(kernel="rbf", C=1.0, gamma="scale"))` dan validasi leave-one-session-out. Fitur klasifikasi baru **dibangun dari sini**, bukan dari nol.

### 3.2 Data nyata

`data/real/train.csv`: 7 sesi, dua kelas, **2 orang** (satu per kelas).

| Kelas | Glukosa darah | Sesi | Subjek |
|---|---|---|---|
| NORMAL | 88 mg/dL | 4 | S088 |
| DIABETES | 148 mg/dL | 3 | S148 |
| PREDIABETES | — | **0** | — |

Model nyata terbaru (`models/real/model_real_v1`): SVC, hanya fitur `v_fru`, LOSO accuracy 100%. Angka itu **tidak boleh dilaporkan sebagai akurasi** karena:
- Sesi lain dari orang yang sama ikut di data latih, jadi tidak menguji orang baru.
- Satu orang = satu kelas, sehingga model bisa belajar "siapa orangnya / strip hari itu", bukan glukosa.
- Menurut `hardware/PRD_Glicovia.md` §5, sinyal `v_fru` kedua kelas berbeda drastis dengan pola yang mirip artefak kontak, bukan analit. Hanya 59 dari 2.317 baris berstatus `OK`; sisanya jenuh.

### 3.3 Celah yang harus ditutup

- Tidak ada kelas `PREDIABETES` di data nyata.
- Tidak ada jalur klasifikasi 3 kelas di `train_svm.py`, `evaluate.py`, `inference.py`.
- `inference.py` memetakan label kelas ke angka lewat `CLASS_TO_MGDL`, bukan menyajikan kelas sebagai keluaran utama.
- Tidak ada probabilitas / penolakan `uncertain`.
- Validasi belum per-subjek (butuh `GroupKFold`).

## 4. Pengguna & kebutuhan

| Persona | Kebutuhan dari ML |
|---|---|
| Alat Glicovia (ESP32) | Kirim fitur, terima `{kelas, probabilitas, status}` cepat |
| Operator/peneliti | Latih ulang dari data baru, lihat metrik per kelas, bandingkan versi model |
| Penulis laporan PKM | Angka evaluasi jujur, confusion matrix, F1, keterbatasan tertulis |

## 5. Definisi kelas (label)

Acuan puasa ADA, selaras dengan `_mgdl_to_class` di kode:

| Kelas | Indeks | Glukosa darah (mg/dL) |
|---|---|---|
| `NORMAL` | 0 | < 100 |
| `PREDIABETES` | 1 | 100 – 125 |
| `DIABETES` | 2 | ≥ 126 |

Aturan label:
- Label = hasil **glukometer** pada orang yang sama, selisih waktu ≤ 10 menit dari pengambilan saliva.
- Status puasa/sewaktu **wajib dicatat** (keputusan D3 di PRD hardware belum dijawab). Ambang di atas hanya valid untuk puasa.
- Label ditentukan dari angka glukometer lalu dipetakan ke kelas. Jangan memberi nama kelas berdasarkan dugaan.

**Opsi v1 bila PREDIABETES belum punya data:** latih 2 kelas (`NORMAL` vs `DIABETES`) dan nyatakan jelas bahwa kelas tengah belum didukung. Jangan memaksa 3 kelas tanpa data.

## 6. Fitur (input)

Urutan tetap sesuai `FEATURE_ORDER` di `inference.py`:

| # | Fitur | Sumber | Catatan |
|---|---|---|---|
| 1 | `glucose_saliva` | Kanal glukosa (enzim GOx) | Satuan riil setelah kalibrasi; sebelum itu volt |
| 2 | `ph_value` | Kanal pH (potensiometrik) | Nernst, kalibrasi 2–3 titik buffer |
| 3 | `fructosamine_umol_l` | Kanal ke-3 | **Bukan fruktosamin sungguhan** saat ini (SPCE enzim glukosa kedua, keputusan D1) |

Aturan:
- Jangan menyebut fitur 3 sebagai fruktosamin di laporan sebelum enzim yang benar dipakai. Pakai nama netral (mis. "kanal ke-3") atau tandai replikat glukosa.
- Fitur dipilih lewat argumen `--features`; pemilihan harus berdasar validasi per-subjek, bukan karena akurasi tertinggi pada data kecil.
- Baris `status != OK` / jenuh **tidak boleh** masuk data latih.
- Satu sesi → satu baris (median separuh akhir sesi, sudah dilakukan `build_real_dataset.py`).

## 7. Persyaratan fungsional

Prioritas: **P0** wajib sebelum demo, **P1** sangat diinginkan, **P2** nanti.

### 7.1 Data (D)

| ID | Persyaratan | P |
|---|---|---|
| D-1 | `build_real_dataset.py` membuang sesi tanpa baris `OK` memadai dan melaporkan alasannya. Ambang minimum baris `OK` ditetapkan dan dicatat. | P0 |
| D-2 | `train.csv` memuat `subject_code` yang benar (bukan diasumsikan dari label), `fasting`, `session_date`, `strip_lot`. | P0 |
| D-3 | Data dummy diberi penanda jelas dan **tidak pernah dicampur** dengan data nyata di evaluasi. | P0 |
| D-4 | Cek keseimbangan kelas dan cetak peringatan bila satu kelas < 20% sampel. | P1 |

### 7.2 Pelatihan klasifikasi (T)

| ID | Persyaratan | P |
|---|---|---|
| T-1 | Skrip latih klasifikasi (`train_classifier.py`, turunan `train_real.py`) memakai `Pipeline(StandardScaler → SVC(kernel="rbf", probability=True))`. | P0 |
| T-2 | Tuning `C` dan `gamma` dengan `GridSearchCV` memakai **`GroupKFold` per `subject_code`**. Dilarang `KFold` per baris. | P0 |
| T-3 | `class_weight="balanced"` agar kelas minoritas tidak diabaikan. | P0 |
| T-4 | Skrip menolak melatih bila < 2 kelas, dan **menolak mengeluarkan klaim akurasi** bila subjek per kelas < 3. Ia boleh tetap menyimpan model bertanda `model_not_ready`. | P0 |
| T-5 | Artefak per versi di `src/models/real/`: `.pkl` (pipeline lengkap), `.json` (metadata: fitur, kelas, versi, tanggal, jumlah subjek, metrik, caveat). Tidak menimpa model lama. | P0 |
| T-6 | Perbandingan dengan baseline: regresi logistik, k-NN, dan "tebak kelas mayoritas". SVC dipertahankan hanya bila mengalahkan baseline pada validasi per-subjek. | P1 |
| T-7 | Kernel pembanding `linear` vs `rbf` untuk menunjukkan apakah RBF memang perlu. | P2 |

### 7.3 Evaluasi (E)

| ID | Persyaratan | P |
|---|---|---|
| E-1 | Validasi **leave-one-subject-out** atau `GroupKFold`. Satu subjek tidak boleh muncul di latih dan uji sekaligus. | P0 |
| E-2 | Metrik: accuracy, **F1 macro**, precision/recall **per kelas**, confusion matrix. Accuracy saja tidak cukup. | P0 |
| E-3 | Laporkan **jumlah subjek** dan **jumlah sesi** di samping setiap angka. | P0 |
| E-4 | Perhatian khusus **recall `DIABETES`**: skrining lebih buruk melewatkan penderita daripada salah menandai orang sehat. Laporkan false negative `DIABETES → NORMAL` terpisah. | P0 |
| E-5 | Confidence interval via bootstrap per subjek. | P1 |
| E-6 | Uji sensitivitas derau (F1 vs derau) dan variasi antar individu, sebagai analisis tambahan laporan. | P2 |

### 7.4 Inferensi & API (I)

| ID | Persyaratan | P |
|---|---|---|
| I-1 | `predict_single` mengembalikan `class_index`, `class_name`, `probabilities` (per kelas), `confidence`, `model_version`, `status`. | P0 |
| I-2 | Bila `max(probabilities) < ambang` (default 0,60, bisa diatur), `class_name = "UNCERTAIN"` dan alat menampilkan "ukur ulang". | P0 |
| I-3 | Validasi rentang input (sudah ada di `api_connector.py`); input di luar jangkauan → `status = "out_of_range"`, tanpa prediksi. | P0 |
| I-4 | Bila `model_not_ready`, respons membawa `status = "model_not_ready"` dan alat tidak menampilkan kelas sebagai hasil. | P0 |
| I-5 | Endpoint tetap `/predict`, `/predict-batch`, `/model-info`, `/health`; **kompatibel mundur** dengan parser firmware (`clinical_category`, `confidence_score`) sambil menambah field baru. | P0 |
| I-6 | `glucose_estimate` (mg/dL) menjadi **opsional**, hanya terisi bila model SVR pembanding aktif. Tidak ada angka mg/dL yang dipetakan dari kelas (hindari presisi palsu). | P1 |
| I-7 | Pemilihan model via env `GLICO_MODEL_PATH` (sudah ada); `/model-info` menampilkan jenis model (SVC/SVR) dan caveat. | P1 |

### 7.5 Operasional (O)

| ID | Persyaratan | P |
|---|---|---|
| O-1 | Satu perintah untuk jalur nyata: `build_real_dataset → train_classifier → evaluate`. | P0 |
| O-2 | Tes `pytest` untuk: pembagian per-subjek tidak bocor, penolakan < 2 kelas, bentuk respons API, penolakan `UNCERTAIN`. | P0 |
| O-3 | `Dockerfile` tetap jalan; model versi aktif ikut di image atau dimuat dari volume. | P1 |
| O-4 | Log setiap prediksi (input, kelas, probabilitas, versi model) untuk audit dan pelatihan ulang. | P1 |

## 8. Kontrak API (target)

Permintaan (tidak berubah):

```json
{ "glucose_saliva": 1.8, "ph_value": 6.7, "fructosamine_umol_l": 210 }
```

Respons:

```json
{
  "class_index": 2,
  "class_name": "DIABETES",
  "probabilities": { "NORMAL": 0.08, "PREDIABETES": 0.17, "DIABETES": 0.75 },
  "confidence": 0.75,
  "clinical_category": "DIABETES",
  "confidence_score": 0.75,
  "model_type": "SVC-rbf",
  "model_version": "svc-2026-11-01",
  "status": "ok"
}
```

`clinical_category` dan `confidence_score` dipertahankan agar firmware lama tetap bekerja. Nilai `status`: `ok`, `uncertain`, `out_of_range`, `model_not_ready`.

## 9. Kriteria penerimaan

**Tahap A — pipeline benar (bisa dicapai sekarang):**
1. Satu perintah menghasilkan model + metadata + laporan evaluasi dari `hardware/DATA/*.csv`.
2. Tes membuktikan tidak ada kebocoran subjek antara latih dan uji.
3. API mengembalikan kontrak §8; model dengan data tidak cukup bertanda `model_not_ready`.
4. Semua `pytest` lulus.

**Tahap B — klaim ilmiah (butuh data):**

| Item | Minimum |
|---|---|
| Subjek berbeda | ≥ 30 (target 50), mencakup ketiga kelas |
| Subjek per kelas | ≥ 8 (kelas minoritas tidak boleh kosong) |
| Pengukuran per subjek | ≥ 3 sesi valid (`status = OK`) |
| Label | Glukometer, ≤ 10 menit, status puasa tercatat |
| Validasi | LOSO / GroupKFold per subjek |

Target v1 (realistis, pada subjek yang belum pernah dilihat): **F1 macro ≥ 0,70** dan **recall DIABETES ≥ 0,80**. Bila tidak tercapai, laporkan jujur sebagai studi awal. Jangan menyetel ulang model sampai angka bagus pada data uji yang sama.

## 10. Risiko & keterbatasan

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Hanya 2 subjek, tiap kelas 1 orang | Model belajar identitas / strip, bukan glukosa | Kumpulkan ≥ 30 subjek; T-4 menolak klaim akurasi |
| Sinyal `v_fru` mirip artefak kontak | Akurasi tinggi palsu | Uji fitur lewat validasi per-subjek; jangan jadikan fitur tunggal tanpa bukti |
| Data hampir semua jenuh (≈2,5% `OK`) | Fitur tidak mewakili sampel | Perbaiki AFE dulu (PRD hardware §6.1); D-1 membuang sesi jenuh |
| Kelas `PREDIABETES` kosong | Tidak bisa 3 kelas | Mulai 2 kelas; kumpulkan data kelas tengah |
| Korelasi glukosa saliva–darah lemah dan bervariasi | Batas atas akurasi rendah | Pernyataan "skrining awal"; laporkan keterbatasan |
| Kelas ambang (100/126) rawan pada nilai dekat batas | Salah kelas di tepi | Probabilitas + `UNCERTAIN`; laporkan error di dekat batas |
| Dummy dianggap data nyata | Klaim palsu di laporan | D-3: penanda jelas, evaluasi terpisah |
| False negative `DIABETES` | Penderita lolos skrining | E-4, ambang `UNCERTAIN`, penekanan "bukan diagnosis" |
| Perubahan kontrak merusak firmware | Alat tidak menampilkan hasil | I-5: kompatibel mundur |

## 11. Keputusan terbuka

| # | Pertanyaan | Pemilik |
|---|---|---|
| M1 | 2 kelas dulu atau langsung 3 kelas? (bergantung ketersediaan data prediabetes) | Tim |
| M2 | Sampel 88 dan 148 diambil puasa atau sewaktu, dari berapa orang? (D3 PRD hardware) | Tim data |
| M3 | Ambang `UNCERTAIN` (0,60?) dan biaya salah kelas: apakah false negative diberi bobot lebih? | Tim + pembimbing |
| M4 | Kanal ke-3 dipakai sebagai fitur atau ditunda sampai enzim benar? (D1) | Tim hardware |
| M5 | SVR dipertahankan sebagai pembanding di laporan atau dihentikan? | Tim |
| M6 | Prosedur pengambilan saliva (puasa, bilas mulut, volume tetes) baku apa? | Tim data |

## 12. Fase kerja

| Fase | Isi | Keluaran |
|---|---|---|
| 1 | Rapikan data: D-1, D-2, D-3; sesi jenuh dibuang | `train.csv` bersih + laporan sesi |
| 2 | Bangun `train_classifier.py` (T-1…T-5) + tes O-2 | Model SVC + metadata |
| 3 | Evaluasi per-subjek (E-1…E-4) + baseline (T-6) | Laporan metrik, confusion matrix |
| 4 | Adaptasi `inference.py` + `api_connector.py` (I-1…I-5) | API kontrak §8 |
| 5 | Pengumpulan data subjek (Tahap B) → latih ulang | Angka yang boleh dilaporkan |

Fase 1–4 bisa dikerjakan sekarang. Fase 5 bergantung pada hardware yang sudah lolos bench dan relawan.

## 13. Glosarium singkat

- **SVM**: keluarga metode pemisah data berbasis margin. **SVC** = untuk kelas, **SVR** = untuk angka.
- **Kernel RBF**: ukuran kemiripan `exp(-γ‖x−x'‖²)` yang membuat batas keputusan melengkung.
- **C**: penalti salah klasifikasi. **γ (gamma)**: lebar pengaruh tiap sampel.
- **LOSO / GroupKFold**: validasi yang mengelompokkan data per subjek agar uji selalu orang baru.
- **F1 macro**: rata-rata F1 antar kelas, adil terhadap kelas kecil.
- **Kebocoran data (leakage)**: informasi uji ikut masuk latih sehingga akurasi tampak palsu tinggi.
