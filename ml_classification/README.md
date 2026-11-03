# ml_classification — SVC 3 kelas Glicovia

Klasifikasi glukosa darah dari sinyal saliva ke `NORMAL` (<100 mg/dL), `PREDIABETES` (100–125),
`DIABETES` (≥126). Acuan: `ml_pipeline/PRD_ML_Glicovia.md`. Terpisah dari jalur regresi `ml_pipeline/`.

Alat ini **skrining awal, bukan diagnosis**.

## Jalankan

Dari folder `ml_classification/`:

```bash
python -m cls.dataset && python -m cls.train && python -m cls.evaluate
uvicorn cls.api:app --port 8000          # API, model: env GLICO_CLS_MODEL atau models/ terbaru
pytest tests
```

Docker (API saja; port dari env `PORT`, default 8080):

```bash
docker build -t glicovia-cls .
docker run -p 8000:8080 glicovia-cls      # backend: ML_CLS_SERVICE_URL=http://localhost:8000
```

Image memakai `requirements-api.txt` (versi dikunci = versi saat model dilatih, scikit-learn 1.9.0) dan model
`GLICO_CLS_MODEL=/app/models/model_cls_kal_20261029.pkl`. Model baru -> ganti `GLICO_CLS_MODEL` di `Dockerfile`
(atau set env di Railway). Naikkan scikit-learn -> latih ulang model.

| Langkah | Masukan | Keluaran |
|---|---|---|
| `cls.dataset` | `hardware/DATA`, `ml_pipeline/sampling` (`--data-dir`) | `data/train.csv` (1 baris/sesi) |
| `cls.train` | `data/train.csv` | `models/model_cls_<versi>.pkl` + `.json` (tidak menimpa) |
| `cls.evaluate` | `data/train.csv` | `reports/loso_report.json` + `.txt` (SVC vs baseline) |

Opsi penting: `--min-ok N` (buang sesi dengan baris `OK` < N, default 0),
`--features glucose_saliva ph_value fructosamine_umol_l` (default dua yang pertama), `--C`, `--gamma`, `--version`.

## Kalibrasi

Fitur = satuan riil hasil kalibrasi sementara di `cls/calibration.py`, dihitung dari kolom volt/arus
`train.csv` (`v_ph`, `i_nA`, `v_mid`, `v_fru`) saat `cls.train` / `cls.evaluate`. Konstanta harus sama dengan
firmware `hardware/f_endtoend_auto/f_endtoend_auto.ino`; ubah konstanta -> **latih ulang model**.
pH: `V = -0,05916 * pH + 0,3226` (Nernst; sama dengan `ml_pipeline/src/convert_data_log.py`, `PROVISIONAL_CAL` di
backend, dan firmware). Hasil regresi 3 buffer (`m = -0,014552`, `c = 0,28292`, lihat `hardware/data_log/pH/`)
sengaja BELUM dipakai: ganti serentak di keempat tempat lalu latih ulang model regresi dan klasifikasi.
Dengan nilai ini pH hampir selalu terpotong ke 4,0 (V ≈ 0,14–1,3 V), jadi fitur pH belum informatif.
Model lama (`model_cls_20261027_042201`, `model_cls_c1`) dilatih dari volt dan tidak cocok dengan masukan baru.

## Kontrak `/predict`

Masukan: `{"glucose_saliva": .., "ph_value": .., "fructosamine_umol_l": ..}` (mg/dL, pH, umol/L; kalibrasi sementara,
sama dengan yang dikirim firmware/backend ke jalur regresi).
Keluaran: `class_index`, `class_name`, `probabilities`, `confidence`, `model_type`, `model_version`, `status`,
plus `clinical_category` dan `confidence_score` untuk firmware lama.
`status`: `ok` | `uncertain` (max proba < 0,60) | `out_of_range` | `model_not_ready`. Tidak ada angka mg/dL.

## Asumsi & keterbatasan

- **Nama file format baru** (`glicovia_<subjek>[_<n>]_<mgdl>[mgdl]_<stamp>`): angka pertama = subjek, angka
  terakhir = mg/dL. Arti angka tengah (mis. `12` di `glicovia_2_12_112mgdl`) belum dikonfirmasi.
- **Format lama** (`glicovia_<mgdl>_<KELAS>_...`): subjek diasumsikan 1 orang per nilai mg/dL.
- **Data (2026-10-27):** 11 sesi, 6 subjek; NORMAL 4, PREDIABETES 1, DIABETES 1 subjek. Semua model
  bertanda `model_not_ready` (PRD T-4: butuh ≥ 3 subjek per kelas) dan API tidak mengeluarkan kelas.
- **Pergeseran sinyal:** `v_ph` batch 20261021 ≈ 0,05 V, batch 20261026 ≈ 1,3 V. Fitur `ph_value` bisa
  memisahkan batch, bukan glukosa. Kolom `batch` di `train.csv` untuk memeriksa ini.
- Fitur `glucose_saliva` berasal dari **arus** (`i_nA`), bukan `v_glu` seperti model lama. Kanal glukosa sering jenuh.
- Pemotongan kalibrasi (pH 4–9, glukosa 0,1–10, fruktosamin 150–500) membuang informasi di luar rentang.
- Sebagian besar sesi berstatus `JENUH`; default tidak disaring (`--min-ok 0`).
- Kanal ke-3 (`fructosamine_umol_l`) **bukan fruktosamin sungguhan** saat ini.
- Metrik LOSO saat ini **tidak boleh** dilaporkan sebagai akurasi.
- `models/model_cls_c1.*` berasal dari percobaan awal (dipindah dari `ml_pipeline/`).
