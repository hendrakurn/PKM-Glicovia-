# ML Pipeline Flow dan Cara Penggunaan

Dokumen ini menjelaskan alur kerja ML pipeline untuk proyek non-invasive blood glucose monitoring via saliva, cara menjalankannya, dan arti dari hasil yang dihasilkan oleh tiap modul.

## 1. Gambaran Umum Alur

Alur utama pipeline:

```text
Data mentah / Hardware
        ↓
   data_loader.py
        ↓
 preprocessing.py
        ↓
   train_svm.py
        ↓
    evaluate.py
        ↓
 visualization.py
        ↓
    inference.py
        ↓
   api_connector.py
        ↓
   pipeline.py (orkestrasi end-to-end)
```

### Penjelasan singkat flow
- `data_loader.py`: membaca data dari CSV / sumber data lain.
- `preprocessing.py`: membersihkan data dan menyiapkan fitur.
- `train_svm.py`: melatih model SVR/SVM regression.
- `evaluate.py`: menghitung metrik performa model.
- `visualization.py`: membuat grafik analisis dan laporan.
- `inference.py`: melakukan prediksi pada data baru.
- `api_connector.py`: menerima data dari hardware dan mengirim hasil prediksi.
- `pipeline.py`: menjalankan semua langkah di atas secara terintegrasi.

## 2. Cara Menggunakan Pipeline

### A. Untuk Training Model
Gunakan alur ini saat ingin melatih model dari data yang sudah ada.

Langkah umum:
1. Siapkan file data, biasanya CSV.
2. Jalankan data loading.
3. Lakukan preprocessing.
4. Latih model SVR.
5. Evaluasi hasil model.
6. Simpan model terbaik.
7. Generate visualisasi hasil.

Contoh penggunaan konsep:
```bash
python src/pipeline.py
```

Atau jika dijalankan per modul:
```bash
python src/data_loader.py
python src/preprocessing.py
python src/train_svm.py
python src/evaluate.py
python src/visualization.py
```

> Catatan: nama fungsi spesifik bisa berbeda tergantung implementasi file, tetapi urutan logisnya tetap sama.

### B. Untuk Prediksi Data Baru (Inference)
Gunakan ini saat ada data baru dari hardware atau input user.

Langkah umum:
1. Data baru dikirim ke API.
2. Data divalidasi dan disanitasi.
3. Data diproses oleh model inference.
4. Sistem mengembalikan nilai prediksi gula darah.

### C. Untuk Integrasi Hardware → Web/API
Alur penggunaan saat sistem berjalan:
1. Hardware membaca parameter saliva.
2. Hardware mengirim JSON ke API.
3. API menerima data di `api_connector.py`.
4. Data diteruskan ke inference model.
5. Hasil dikirim kembali ke dashboard/web.

Contoh payload JSON:
```json
{
  "subject_id": "SUBJ001",
  "sampling_date": "2026-07-03",
  "sampling_time": "08:30:00",
  "fasting_hours": 8,
  "saliva_ph": 6.8,
  "saliva_viscosity_sec": 12.4,
  "saliva_glucose_mgdl": 15.2,
  "proto_glucose_raw": 321
}
```

## 3. Fungsi Tiap Modul dan Hasil yang Dihasilkan

### 3.1 `generate_dummy.py`
**Fungsi:**
- Membuat data sintetis/dummy untuk testing pipeline.

**Kapan dipakai:**
- Saat data asli masih terbatas.
- Saat ingin menguji alur training tanpa menunggu data hardware.

**Hasil yang dihasilkan:**
- File data dummy dalam format tabel/CSV.

**Arti hasil:**
- Data ini bukan data klinis asli, tetapi dipakai untuk simulasi dan debugging.

---

### 3.2 `data_loader.py`
**Fungsi:**
- Membaca dataset dari CSV atau sumber data lain.

**Kapan dipakai:**
- Di awal pipeline sebelum preprocessing.

**Hasil yang dihasilkan:**
- DataFrame / objek data yang siap diproses.

**Arti hasil:**
- Dataset sudah terbaca dengan format yang konsisten dan bisa masuk ke tahap berikutnya.

---

### 3.3 `preprocessing.py`
**Fungsi:**
- Membersihkan data.
- Menangani missing value jika ada.
- Memilih fitur yang dipakai.
- Melakukan scaling/normalization untuk SVM.

**Kapan dipakai:**
- Sebelum training dan inference.

**Hasil yang dihasilkan:**
- Dataset yang sudah bersih dan terstandarisasi.

**Arti hasil:**
- Fitur siap dipakai model. Ini penting karena SVM sensitif terhadap skala data.

---

### 3.4 `train_svm.py`
**Fungsi:**
- Melatih model Support Vector Regression (SVR).
- Menguji kernel seperti `linear`, `rbf`, dan `poly`.

**Kapan dipakai:**
- Saat model baru akan dibuat atau di-train ulang.

**Hasil yang dihasilkan:**
- Model terlatih (`.pkl`, `.joblib`, atau format lain sesuai implementasi).
- Ringkasan training.

**Arti hasil:**
- Model siap digunakan untuk prediksi data baru.
- Jika hasil training buruk, berarti perlu tuning hyperparameter atau perbaikan data.

---

### 3.5 `evaluate.py`
**Fungsi:**
- Mengukur performa model menggunakan metrik evaluasi.

**Metrik yang umum dipakai:**
- `R²`
- `RMSE`
- `MAE`

**Hasil yang dihasilkan:**
- Nilai metrik evaluasi.
- Kadang juga file report atau summary hasil evaluasi.

**Arti hasil:**
- `R²` tinggi berarti model lebih baik menjelaskan variasi data.
- `RMSE` rendah berarti error prediksi kecil dalam satuan mg/dL.
- `MAE` rendah berarti rata-rata selisih prediksi dengan nilai asli kecil.

**Interpretasi umum:**
- `R²` mendekati 1 = sangat baik.
- `RMSE` makin kecil = makin baik.
- `MAE` makin kecil = makin baik.

---

### 3.6 `visualization.py`
**Fungsi:**
- Membuat grafik untuk analisis data dan performa model.

**Contoh output:**
- Distribusi fitur
- Heatmap korelasi
- Confusion matrix
- ROC curve
- Dashboard plot lain

**Hasil yang dihasilkan:**
- File gambar visualisasi, misalnya `.png`.

**Arti hasil:**
- Membantu melihat pola data.
- Membantu mengecek kualitas model.
- Berguna untuk laporan PKM dan presentasi.

---

### 3.7 `inference.py`
**Fungsi:**
- Menggunakan model terlatih untuk memprediksi input baru.

**Kapan dipakai:**
- Saat data baru masuk dari hardware atau user.

**Hasil yang dihasilkan:**
- Prediksi kadar gula darah (`bg_reference_mgdl` atau nilai estimasinya).

**Arti hasil:**
- Ini adalah output utama sistem, yaitu estimasi kadar gula darah dari parameter saliva.

---

### 3.8 `api_connector.py`
**Fungsi:**
- Menyediakan endpoint API untuk menerima data sensor.
- Menjalankan inference.
- Mengembalikan hasil ke client/dashboard.

**Contoh endpoint yang umum:**
- `/health`
- `/model-info`
- `/predict`

**Hasil yang dihasilkan:**
- Response JSON dari server.

**Arti hasil:**
- Menunjukkan status sistem.
- Memberikan info model.
- Menghasilkan prediksi dari input yang dikirim.

---

### 3.9 `pipeline.py`
**Fungsi:**
- Menggabungkan seluruh tahap pipeline menjadi satu alur.

**Kapan dipakai:**
- Saat ingin menjalankan pipeline end-to-end.

**Hasil yang dihasilkan:**
- Training + evaluasi + output pipeline dalam satu proses.

**Arti hasil:**
- Memudahkan eksekusi tanpa menjalankan modul satu per satu.

## 4. Ringkasan Output dan Artinya

| Modul | Output | Arti Output |
|---|---|---|
| `generate_dummy.py` | Data dummy | Data simulasi untuk testing |
| `data_loader.py` | Dataset terbaca | Data siap diproses |
| `preprocessing.py` | Data bersih & scaled | Siap untuk training/inference |
| `train_svm.py` | Model terlatih | Bisa dipakai prediksi |
| `evaluate.py` | R², RMSE, MAE | Ukuran performa model |
| `visualization.py` | Grafik/plot | Analisis & pelaporan |
| `inference.py` | Prediksi gula darah | Output utama sistem |
| `api_connector.py` | Response JSON | Output untuk hardware/dashboard |
| `pipeline.py` | Proses end-to-end | Menjalankan semua tahap |

## 5. Contoh Alur Pemakaian Sederhana

### Skenario 1: Training dari data CSV
1. Dataset dibaca oleh `data_loader.py`
2. Dataset dibersihkan di `preprocessing.py`
3. Model dilatih di `train_svm.py`
4. Hasil dievaluasi di `evaluate.py`
5. Grafik dibuat oleh `visualization.py`
6. Model terbaik disimpan untuk inference

### Skenario 2: Prediksi dari hardware
1. Hardware mengirim data saliva ke API
2. `api_connector.py` menerima request
3. Data dicek dan dibersihkan
4. `inference.py` menghasilkan prediksi
5. Hasil dikirim ke dashboard

## 6. Catatan Penting

- Dataset proyek masih relatif kecil, jadi cross-validation tetap penting.
- SVM sensitif terhadap skala fitur, jadi preprocessing wajib dilakukan dengan benar.
- Hasil evaluasi harus dilihat bersama konteks data medis, bukan hanya satu metrik.
- Jika model belum memenuhi target, lakukan tuning kernel, C, gamma, atau fitur input.

## 7. Kesimpulan

ML pipeline ini sudah dibangun untuk mendukung prediksi kadar gula darah non-invasive berbasis saliva. Setiap modul punya peran spesifik: dari membaca data, membersihkan data, melatih model, mengevaluasi performa, membuat visualisasi, sampai menerima data dari hardware melalui API.

Dengan pipeline ini, sistem bisa dipakai untuk:
- eksperimen model,
- prediksi data baru,
- integrasi ke dashboard monitoring,
- dan dokumentasi hasil untuk laporan PKM.
