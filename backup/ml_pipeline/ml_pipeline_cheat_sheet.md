# ML Pipeline Cheat Sheet Command

Ringkasan command cepat untuk menjalankan semua modul `ml_pipeline` dalam satu halaman.

## Prerequisites
```bash
cd ml_pipeline
```

Gunakan Python dari virtual environment project:
```bash
./venv/bin/python
```

## 1) Run All Modules One by One
Jalankan dari folder `ml_pipeline/src`:
```bash
cd src
../venv/bin/python generate_dummy.py
../venv/bin/python data_loader.py
../venv/bin/python preprocessing.py
../venv/bin/python train_svm.py
../venv/bin/python evaluate.py
../venv/bin/python visualization.py
../venv/bin/python inference.py
../venv/bin/python api_connector.py
../venv/bin/python pipeline.py
```

## 2) End-to-End Pipeline
```bash
cd src
../venv/bin/python pipeline.py
```

## 3) Training Only
```bash
cd src
../venv/bin/python generate_dummy.py
../venv/bin/python preprocessing.py
../venv/bin/python train_svm.py
```

## 4) Evaluation Only
```bash
cd src
../venv/bin/python evaluate.py
```

## 5) Inference Only
```bash
cd src
../venv/bin/python inference.py
```

## 6) API Connector / Hardware Endpoint
```bash
cd src
../venv/bin/python api_connector.py
```

## 7) Visualization Only
```bash
cd src
../venv/bin/python visualization.py
```

## 8) Run Tests
Dari folder `ml_pipeline`:
```bash
PYTHONPATH=. ./venv/bin/python -m pytest -q
```

Single test file:
```bash
PYTHONPATH=. ./venv/bin/python -m pytest tests/test_train_svm.py -q
PYTHONPATH=. ./venv/bin/python -m pytest tests/test_visualization.py -q
PYTHONPATH=. ./venv/bin/python -m pytest tests/test_api_connector.py -q
```

## 9) Quick Notes
- `SVM/SVR` sensitif terhadap scaling, jadi pastikan `preprocessing.py` dijalankan sebelum training/inference.
- Jika import error, cek working directory dan gunakan `PYTHONPATH=.` saat menjalankan pytest.
- Artefak umum: `src/models/`, `src/data/processed/`, `src/evaluation/`, `src/pipeline_results/`.

## 10) Modul Map
- `generate_dummy.py` → synthetic data
- `data_loader.py` → load dataset
- `preprocessing.py` → clean + scale features
- `train_svm.py` → train SVR model
- `evaluate.py` → metrics report
- `visualization.py` → plots and figures
- `inference.py` → predict new sample
- `api_connector.py` → API endpoint for hardware/dashboard
- `pipeline.py` → orchestrate end-to-end flow
