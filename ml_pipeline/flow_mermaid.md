# Diagram Flow ML Pipeline (Mermaid)

```mermaid
flowchart TD
    A[Data mentah / Hardware] --> B[data_loader.py]
    B --> C[preprocessing.py]
    C --> D[train_svm.py]
    D --> E[evaluate.py]
    E --> F[visualization.py]
    F --> G[inference.py]
    G --> H[api_connector.py]
    H --> I[pipeline.py]

    A2[Input CSV / Dataset] --> B
    A3[Sensor / Hardware Device] --> H

    B --> B1[Dataset terbaca]
    C --> C1[Data bersih & terstandarisasi]
    D --> D1[Model SVR terlatih]
    E --> E1[Metode evaluasi: R², RMSE, MAE]
    F --> F1[Grafik / visualisasi]
    G --> G1[Prediksi kadar glukosa darah]
    H --> H1[Response JSON ke dashboard / client]
    I --> I1[Eksekusi end-to-end]
```

## Keterangan Diagram

- `data_loader.py`: membaca dataset dari file atau sumber data.
- `preprocessing.py`: membersihkan data dan menyiapkan fitur.
- `train_svm.py`: melatih model Support Vector Regression.
- `evaluate.py`: menghitung metrik evaluasi model.
- `visualization.py`: menghasilkan visualisasi untuk analisis.
- `inference.py`: melakukan prediksi terhadap data baru.
- `api_connector.py`: menerima data dari hardware dan mengirim hasil prediksi.
- `pipeline.py`: menjalankan seluruh proses secara terintegrasi.

## Alur Singkat

Data mentah atau data dari hardware diproses oleh `data_loader.py`, kemudian melalui tahap prapemrosesan di `preprocessing.py`. Setelah itu model dilatih menggunakan `train_svm.py`, dievaluasi dengan `evaluate.py`, dan hasilnya divisualisasikan melalui `visualization.py`. Pada tahap operasional, data baru diprediksi melalui `inference.py` dan dihubungkan ke sistem melalui `api_connector.py`. Seluruh proses dapat dijalankan secara end-to-end melalui `pipeline.py`.
