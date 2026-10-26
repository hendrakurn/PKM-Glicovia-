# Real Data to Model Guide

This guide explains the exact steps to take new real data and produce a trained model file in this repository.

Repository root:

```text
/home/hendra/projects/pkmGlico/ml_pipeline
```

All commands below assume you are running from the project root:

```bash
cd /home/hendra/projects/pkmGlico/ml_pipeline
```

## Goal

Starting from a real CSV dataset, you will:

1. validate the required schema
2. preprocess the dataset
3. train the SVR model
4. evaluate the trained model
5. use the saved model for inference

Main output files:

- `src/models/best_model.pkl`
- `src/data/processed/scaler_params.json`

## Important Constraint

The current [src/pipeline.py](/home/hendra/projects/pkmGlico/ml_pipeline/src/pipeline.py:1) is still oriented around dummy-data generation by default.

For real data, the correct path today is to run preprocessing, training, and evaluation directly with Python commands. Do not rely on `src/pipeline.py` for real CSV input unless it is extended to accept a custom `raw_csv_path`.

## Step 1: Prepare the Real CSV

Your real training CSV must contain these columns:

```text
id
glucose_saliva
ph_value
fructosamine_umol_l
bg_class
bg_mgdl_reference
```

Column meaning:

- `id`: sample identifier
- `glucose_saliva`: saliva glucose feature
- `ph_value`: saliva pH feature
- `fructosamine_umol_l`: fructosamine feature in `umol/L`
- `bg_class`: class label used for stratified split
- `bg_mgdl_reference`: regression target in `mg/dL`

Example CSV:

```csv
id,glucose_saliva,ph_value,fructosamine_umol_l,bg_class,bg_mgdl_reference
S001,1.2,6.7,240,0,92
S002,1.9,6.4,290,1,113
S003,3.1,6.1,380,2,168
```

Recommended location:

```text
data/raw/real_data.csv
```

## Step 2: Preprocess the Real Data

This step:

- checks required columns
- handles missing values
- removes outliers
- performs train/test split
- fits the scaler from the training set
- writes processed arrays and scaler metadata

Run:

```bash
./venv/bin/python -c "from src.preprocessing import preprocess; result = preprocess(raw_csv_path='data/raw/real_data.csv', output_dir='src/data/processed'); print(result)"
```

Expected outputs:

- `src/data/processed/X_train.npy`
- `src/data/processed/X_test.npy`
- `src/data/processed/y_train.npy`
- `src/data/processed/y_test.npy`
- `src/data/processed/scaler_params.json`
- `src/data/processed/preprocessing_report.json`

What the scaler file is for:

- inference must use the same feature scaling that was used during training
- `run_inference.py` reads this scaler metadata by default

## Step 3: Train the Model

This repository trains an `SVR` regression model, not a pure classifier.

The model predicts blood glucose in `mg/dL`, then inference maps that numeric value into:

- `Normal`
- `Pre-Diabetes`
- `Diabetes`

Run training:

```bash
./venv/bin/python -c "from src.train_svm import train_svm; result = train_svm(processed_data_path='src/data/processed', output_dir='src/models'); print(result)"
```

Expected outputs:

- `src/models/best_model.pkl`
- `src/models/experiment_log.json`
- `src/models/fold_results/`

The main model artifact is:

```text
src/models/best_model.pkl
```

That is the file later used by inference.

## Step 4: Evaluate the Trained Model

This step measures model quality on the held-out test set.

Run:

```bash
./venv/bin/python -c "from src.evaluate import evaluate; result = evaluate(model_path='src/models/best_model.pkl', X_test_path='src/data/processed/X_test.npy', y_test_path='src/data/processed/y_test.npy', output_dir='src/evaluation'); print(result)"
```

Expected outputs:

- `src/evaluation/evaluation_report.json`
- `src/evaluation/predictions.npy`
- `src/evaluation/confusion_matrix.npy`

Key metrics to inspect:

- `r2`
- `rmse`
- `mae`
- clinical classification metrics derived from the regression output

## Step 5: Run Inference on a New Single Sample

After training is complete, run inference with the saved model and scaler.

Command:

```bash
./venv/bin/python run_inference.py \
  --glucose-saliva 1.3 \
  --ph-value 6.4 \
  --fructosamine-umol-l 285 \
  --sample-id sample-1
```

This prints JSON to the terminal.

It uses these default files automatically:

- `src/models/best_model.pkl`
- `src/data/processed/scaler_params.json`

## Step 6: Run Batch Inference on a CSV

If you have many new unlabeled samples, prepare a CSV like this:

```csv
id,glucose_saliva,ph_value,fructosamine_umol_l
N001,1.3,6.4,285
N002,2.8,6.2,360
```

Recommended location:

```text
data/new_samples.csv
```

Run batch inference:

```bash
./venv/bin/python -c "import pandas as pd; from src.inference import predict_batch; df = pd.read_csv('data/new_samples.csv'); results = predict_batch(df, model_path='src/models/best_model.pkl', scaler_path='src/data/processed/scaler_params.json'); print(results)"
```

If you want to export the results:

```bash
./venv/bin/python -c "import pandas as pd; from src.inference import predict_batch, export_predictions; df = pd.read_csv('data/new_samples.csv'); results = predict_batch(df, model_path='src/models/best_model.pkl', scaler_path='src/data/processed/scaler_params.json'); export_predictions(results, 'src/evaluation/batch_predictions.json', format='json'); print(results)"
```

## End-to-End Command Sequence

If your real data is already in `data/raw/real_data.csv`, run these commands in order:

```bash
./venv/bin/python -c "from src.preprocessing import preprocess; result = preprocess(raw_csv_path='data/raw/real_data.csv', output_dir='src/data/processed'); print(result)"
./venv/bin/python -c "from src.train_svm import train_svm; result = train_svm(processed_data_path='src/data/processed', output_dir='src/models'); print(result)"
./venv/bin/python -c "from src.evaluate import evaluate; result = evaluate(model_path='src/models/best_model.pkl', X_test_path='src/data/processed/X_test.npy', y_test_path='src/data/processed/y_test.npy', output_dir='src/evaluation'); print(result)"
./venv/bin/python run_inference.py --glucose-saliva 1.3 --ph-value 6.4 --fructosamine-umol-l 285 --sample-id sample-1
```

## Common Failure Cases

### Missing Columns

If preprocessing fails with missing columns, verify your CSV includes:

```text
id,glucose_saliva,ph_value,fructosamine_umol_l,bg_class,bg_mgdl_reference
```

### Only One Class Present

Preprocessing uses stratified train/test split. If all rows have the same `bg_class`, preprocessing will fail.

Your training CSV must include enough samples across at least two classes.

### Wrong Working Directory

Run commands from the project root:

```bash
cd /home/hendra/projects/pkmGlico/ml_pipeline
```

If you run commands from `src/`, relative paths like `./venv/bin/python` and `run_inference.py` will fail.

### Trying to Train on Unlabeled New Samples

If your new dataset only has:

```text
id,glucose_saliva,ph_value,fructosamine_umol_l
```

that file is only suitable for inference, not training.

To train a new model, you need labels:

- `bg_class`
- `bg_mgdl_reference`

## File Map

Relevant source files:

- [src/preprocessing.py](/home/hendra/projects/pkmGlico/ml_pipeline/src/preprocessing.py:1)
- [src/train_svm.py](/home/hendra/projects/pkmGlico/ml_pipeline/src/train_svm.py:1)
- [src/evaluate.py](/home/hendra/projects/pkmGlico/ml_pipeline/src/evaluate.py:1)
- [src/inference.py](/home/hendra/projects/pkmGlico/ml_pipeline/src/inference.py:1)
- [run_inference.py](/home/hendra/projects/pkmGlico/ml_pipeline/run_inference.py:1)

Primary artifact locations:

- `src/data/processed/`
- `src/models/`
- `src/evaluation/`

## Result Summary

Training path:

```text
real labeled CSV
-> preprocess
-> train SVR model
-> evaluate
-> save best_model.pkl + scaler_params.json
```

Inference path:

```text
new sample
-> load best_model.pkl
-> apply scaler_params.json
-> predict blood glucose value
-> map to clinical category
-> return JSON result
```

```
uvicorn src.api_connector:app --host 0.0.0.0 --port 8001 --reload
```
