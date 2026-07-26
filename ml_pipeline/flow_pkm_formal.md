# Alur Kerja ML Pipeline

Dokumen ini menjelaskan alur kerja machine learning pipeline pada sistem prediksi kadar glukosa darah non-invasif berbasis parameter saliva. Penulisan dibuat dengan gaya formal agar dapat digunakan sebagai bagian dari dokumentasi atau laporan PKM.

## 1. Tujuan Pipeline

Machine learning pipeline disusun untuk menghasilkan alur pemrosesan data yang sistematis, mulai dari penerimaan data mentah hingga prediksi kadar glukosa darah. Pipeline ini bertujuan untuk mendukung proses pengembangan model prediksi, evaluasi performa model, serta integrasi hasil prediksi ke dalam sistem monitoring berbasis web.

## 2. Gambaran Umum Alur

Secara umum, pipeline terdiri atas tahapan berikut:

1. Penerimaan data dari file atau perangkat hardware.
2. Pemuatan data menggunakan modul data loader.
3. Prapemrosesan data untuk memastikan data siap digunakan model.
4. Pelatihan model Support Vector Regression (SVR).
5. Evaluasi performa model menggunakan metrik regresi.
6. Visualisasi hasil analisis dan performa model.
7. Prediksi data baru melalui proses inference.
8. Integrasi hasil prediksi melalui API connector.
9. Orkestrasi seluruh proses melalui pipeline utama.

## 3. Alur Kerja Pipeline

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
   pipeline.py
```

## 4. Penjelasan Setiap Tahap

### 4.1 Data Input

Data input berasal dari file dataset atau dari perangkat hardware yang mengirimkan data melalui API. Data tersebut umumnya memuat informasi identitas sampel, waktu pengambilan, serta parameter saliva seperti pH, viskositas, dan kandungan glukosa saliva.

**Hasil tahap ini:** data mentah yang masih perlu dibersihkan dan disesuaikan formatnya.

### 4.2 `data_loader.py`

Modul ini berfungsi untuk membaca data dari sumber yang tersedia, misalnya file CSV, dan mengubahnya ke dalam format yang siap diproses oleh tahapan berikutnya.

**Hasil tahap ini:** dataset yang telah berhasil dimuat ke dalam struktur data yang konsisten.

### 4.3 `preprocessing.py`

Modul prapemrosesan digunakan untuk membersihkan data, menangani nilai hilang apabila ada, memilih fitur yang relevan, serta melakukan penskalaan data. Tahap ini penting karena model SVM sangat sensitif terhadap perbedaan skala fitur.

**Hasil tahap ini:** dataset yang telah dibersihkan dan distandardisasi.

### 4.4 `train_svm.py`

Modul ini digunakan untuk melatih model Support Vector Regression (SVR) dengan kernel tertentu, seperti linear, radial basis function (RBF), atau polynomial. Pelatihan model dilakukan berdasarkan data yang telah dipraproses.

**Hasil tahap ini:** model terlatih yang dapat digunakan untuk prediksi.

### 4.5 `evaluate.py`

Modul evaluasi berfungsi untuk mengukur kinerja model menggunakan metrik regresi, seperti R², RMSE, dan MAE. Evaluasi dilakukan untuk mengetahui sejauh mana model mampu memprediksi nilai target secara akurat.

**Hasil tahap ini:** nilai metrik evaluasi dan ringkasan performa model.

### 4.6 `visualization.py`

Modul visualisasi digunakan untuk menghasilkan grafik dan plot yang membantu analisis data maupun evaluasi model. Visualisasi dapat berupa distribusi data, korelasi antar fitur, confusion matrix, atau grafik evaluasi lainnya sesuai kebutuhan.

**Hasil tahap ini:** file visualisasi dalam bentuk gambar yang mendukung analisis dan pelaporan.

### 4.7 `inference.py`

Modul inference digunakan untuk melakukan prediksi terhadap data baru menggunakan model yang telah dilatih. Tahap ini menjadi inti penggunaan model pada sistem operasional.

**Hasil tahap ini:** estimasi kadar glukosa darah berdasarkan parameter saliva.

### 4.8 `api_connector.py`

Modul ini berfungsi sebagai penghubung antara hardware, backend, dan model prediksi. API menerima data baru, melakukan validasi dan sanitasi input, menjalankan proses inference, kemudian mengirimkan hasil prediksi kepada client atau dashboard.

**Hasil tahap ini:** respons API dalam format JSON yang berisi status sistem atau hasil prediksi.

### 4.9 `pipeline.py`

Modul pipeline utama berfungsi mengorkestrasi seluruh tahapan secara end-to-end. Dengan demikian, proses mulai dari pemuatan data, prapemrosesan, pelatihan, evaluasi, hingga output akhir dapat dijalankan secara lebih terstruktur.

**Hasil tahap ini:** eksekusi pipeline secara menyeluruh dalam satu alur terintegrasi.

## 5. Cara Penggunaan Pipeline

### 5.1 Untuk Pelatihan Model

Pipeline digunakan ketika model akan dilatih dari dataset yang sudah tersedia. Alur penggunaan secara umum adalah sebagai berikut:

1. Menyediakan dataset dalam format yang sesuai.
2. Menjalankan proses pemuatan data.
3. Melakukan prapemrosesan.
4. Melatih model SVR.
5. Mengevaluasi hasil pelatihan.
6. Menyimpan model terbaik.
7. Menghasilkan visualisasi untuk dokumentasi dan analisis.

### 5.2 Untuk Prediksi Data Baru

Pada tahap operasional, data baru dari perangkat atau pengguna dikirim ke API. Data tersebut kemudian diproses oleh model inference untuk menghasilkan estimasi kadar glukosa darah.

### 5.3 Untuk Integrasi dengan Dashboard

Hasil prediksi dari API dapat diteruskan ke dashboard monitoring agar pengguna dapat memantau hasil pengukuran secara berkala dan terstruktur.

## 6. Arti Hasil yang Dihasilkan

| Modul | Hasil | Makna |
|---|---|---|
| `data_loader.py` | Dataset terbaca | Data berhasil dimuat dan siap diproses |
| `preprocessing.py` | Data bersih dan distandardisasi | Data siap digunakan model |
| `train_svm.py` | Model terlatih | Model siap melakukan prediksi |
| `evaluate.py` | R², RMSE, MAE | Ukuran kualitas model |
| `visualization.py` | Grafik/plot | Mendukung analisis dan dokumentasi |
| `inference.py` | Prediksi nilai glukosa darah | Output utama sistem |
| `api_connector.py` | Respons JSON | Hasil prediksi dapat diakses sistem lain |
| `pipeline.py` | Proses end-to-end | Seluruh tahapan berjalan terintegrasi |

## 7. Kesimpulan

Machine learning pipeline pada proyek ini dirancang untuk mendukung pengembangan sistem prediksi kadar glukosa darah non-invasif berbasis saliva. Setiap modul memiliki fungsi yang saling terhubung, sehingga proses pengolahan data, pelatihan model, evaluasi, visualisasi, hingga prediksi dapat dilakukan secara sistematis, terukur, dan mudah diintegrasikan ke dalam sistem monitoring berbasis web.