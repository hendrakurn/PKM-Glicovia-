# GlicoSaliva ML Pipeline - Module Documentation

## Overview
This document describes the ML pipeline modules for non-invasive blood glucose monitoring system.

## Module Structure

### 1. Data Generation (`generate_dummy.py`)
**Purpose**: Generate synthetic saliva dataset for training and testing

**Key Features**:
- Physiological distributions for Normal/Pre-Diabetes/Diabetes classes
- Class imbalance simulation (40%/35%/25%)
- Outlier injection for robustness testing
- Ground truth blood glucose reference generation

**Usage**:
```python
from src.generate_dummy import generate_dummy

df, metadata = generate_dummy(
n_samples=150,
random_state=42,
output_dir="data/dummy"
)
```

**Output**: 
- `data/dummy/generated_data.csv` - Synthetic data
- `data/dummy/metadata.json` - Generation metadata

---

### 2. Preprocessing (`preprocessing.py`)
**Purpose**: Data cleaning, scaling, and train/test splitting

**Key Features**:
- Missing value imputation (median strategy)
- Outlier detection and removal (IQR method)
- Stratified train/test split (80/20)
- StandardScaler normalization

**Usage**:
```python
from src.preprocessing import preprocess

result = preprocess(
raw_csv_path="data/dummy/generated_data.csv",
output_dir="data/processed",
config={"test_size": 0.2, "outlier_strategy": "remove"}
)
```

**Output**:
- `data/processed/X_train.npy` - Scaled training features
- `data/processed/X_test.npy` - Scaled test features
- `data/processed/y_train.npy` - Training labels
- `data/processed/y_test.npy` - Test labels
- `data/processed/scaler_params.json` - Scaler parameters
- `data/processed/preprocessing_report.json` - Preprocessing report

---

### 3. Model Training (`train_svm.py`)
**Purpose**: Train SVM model with hyperparameter optimization

**Key Features**:
- GridSearchCV with cross-validation
- RBF kernel (default) with C and gamma tuning
- Overfitting detection (train-test accuracy gap)
- Fold-level metric tracking

**Usage**:
```python
from src.train_svm import train_svm

result = train_svm(
processed_data_path="data/processed/",
output_dir="models/",
config={"kernel": "rbf", "n_splits": 5}
)
```

**Output**:
- `models/best_model.pkl` - Trained model
- `models/experiment_log.json` - Training metrics
- `models/fold_results/fold_X.json` - Per-fold results

---

### 4. Model Evaluation (`evaluate.py`)
**Purpose**: Comprehensive model performance evaluation

**Key Features**:
- Regression metrics (RMSE, MAE, R²)
- Classification metrics (accuracy, F1-score, confusion matrix)
- Clinical significance assessment
- Model comparison functionality

**Usage**:
```python
from src.evaluate import evaluate, compare_models

result = evaluate(
model_path="models/best_model.pkl",
X_test_path="data/processed/X_test.npy",
y_test_path="data/processed/y_test.npy",
output_dir="evaluation/",
thresholds={"r2_min": 0.50, "rmse_max_percentile": 80.0}
)

# Compare multiple models
comparison = compare_models(model_results=[result1, result2, result3])
```

**Output**:
- `evaluation/evaluation_report.json` - Complete evaluation report
- `evaluation/predictions.npy` - Model predictions
- `evaluation/confusion_matrix.npy` - Confusion matrix (classification)

---

### 5. Pipeline Orchestrator (`pipeline.py`)
**Purpose**: Orchestrate complete ML pipeline from data to evaluation

**Key Features**:
- Single-command execution
- Automatic directory creation
- Configurable pipeline parameters
- Results persistence

**Usage**:
```python
from src.pipeline import MLPipeline, run_pipeline

# Using convenience function
results = run_pipeline(config={
"n_samples": 150,
"kernel": "rbf",
"random_state": 42
})

# Or use MLPipeline class directly
pipeline = MLPipeline(config={"n_samples": 200})
results = pipeline.run_full_pipeline()
pipeline.save_pipeline_results()
```

**Output**:
- All files from individual modules
- `pipeline_results/pipeline_YYYYMMDD_HHMMSS.json` - Complete pipeline results

---

### 6. Data Loader (`data_loader.py`) ⭐ NEW
**Purpose**: Load and validate real-world CSV data with quality checks

**Key Features**:
- CSV data loading from various sources
- Required column validation (id, glucose_saliva, ph_value, fructosamine_umol_l, bg_class, bg_mgdl_reference)
- Data quality checks (missing values, outliers, zero variance)
- Configurable validation thresholds
- Auto-generate dummy data fallback when no real data available
- Export to JSON/CSV formats

**Usage**:
```python
from src.data_loader import load_data, load_batch, export_to_json

# Load from CSV file
df, quality_report = load_data(
file_path="data/patients.csv",
validate=True,
auto_fallback=True
)

# Load from DataFrame
df, report = load_data(data=custom_df, validate=True)

# Load multiple files
results = load_batch(["data/patient1.csv", "data/patient2.csv"])

# Export to JSON
export_to_json(df, "data/exported_data.json")
```

**Output**:
- DataFrame with validated data
- Quality report with status (PASS/WARNING/FAIL)
- Export files in JSON/CSV formats

**Validation Thresholds** (configurable):
- `max_missing_ratio`: 10% max missing values
- `min_variance_ratio`: Minimum variance as ratio of mean
- `outlier_iqr_multiplier`: 1.5 for IQR method
- `max_outlier_ratio`: 5% max outliers
- `min_samples`: 10 minimum samples

---

### 7. Inference (`inference.py`) ⭐ NEW
**Purpose**: Real-time prediction with confidence intervals

**Key Features**:
- Load trained model and scaler
- Single prediction with uncertainty estimation
- Batch prediction support
- Confidence intervals via bootstrap resampling
- Clinical category classification (Normal/Pre-Diabetes/Diabetes)
- Export predictions to CSV/JSON
- Prediction pipeline object for reuse

**Usage**:
```python
from src.inference import (
predict_single,
predict_batch,
export_predictions,
create_prediction_pipeline
)

# Single prediction with confidence
result = predict_single(
sample={
"glucose_saliva": 1.5,
"ph_value": 6.5,
"fructosamine_umol_l": 285
},
model_path="models/best_model.pkl",
scaler_path="data/processed/scaler_params.json",
confidence_level=0.95
)
print(result)  # {'prediction': 1, 'category': {...}, 'confidence': 0.85, ...}

# Batch prediction
results = predict_batch(
samples=[sample1, sample2, sample3],
model_path="models/best_model.pkl",
scaler_path="data/processed/scaler_params.json"
)

# Create reusable pipeline
pipeline = create_prediction_pipeline(
model_path="models/best_model.pkl",
scaler_path="data/processed/scaler_params.json"
)
single_result = pipeline.predict_single(sample)
batch_results = pipeline.predict_batch(samples)

# Export predictions
export_predictions(results, "data/predictions.json", format="json")

# Generate report
report = generate_prediction_report(results)
```

**Output**:
- Prediction dictionary with class, category, confidence
- Exported CSV/JSON files with predictions
- Summary report with statistics

**Clinical Categories**:
- Class 0: Normal (70-100 mg/dL)
- Class 1: Pre-Diabetes (100-125 mg/dL)
- Class 2: Diabetes (126-500 mg/dL)

---

### 8. Visualization (`visualization.py`) ⭐ NEW
**Purpose**: Create comprehensive data and model visualizations

**Key Features**:
- Feature distributions (histograms, box plots per class)
- Correlation heatmap
- Decision boundary plots (2D projections)
- Confusion matrix visualization
- ROC curve and AUC calculation
- Export as PNG/SVG/PDF

**Usage**:
```python
from src.visualization import (
create_feature_distributions,
create_correlation_heatmap,
create_confusion_matrix,
create_roc_curves,
create_decision_boundaries,
create_comprehensive_dashboard
)

# Feature distributions
plot_paths = create_feature_distributions(
df,
feature_cols=["glucose_saliva", "ph_value", "fructosamine_umol_l"],
target_col="bg_class",
output_dir="figures/feature_distributions",
format="png"
)

# Correlation heatmap
corr_result = create_correlation_heatmap(
df,
output_dir="figures/correlation",
format="png"
)

# Confusion matrix
cm_result = create_confusion_matrix(
y_true=y_test,
y_pred=y_pred,
output_dir="figures/confusion_matrix",
format="png"
)

# ROC curves (requires model with predict_proba)
roc_result = create_roc_curves(
y_true=y_test,
y_score=model.predict_proba(X_test),
output_dir="figures/roc_curves",
format="png"
)

# Decision boundaries
decision_result = create_decision_boundaries(
model, X_test, y_test,
feature_indices=(0, 1),
output_dir="figures/decision_boundaries"
)

# Comprehensive dashboard (all plots in one)
dashboard_plots = create_comprehensive_dashboard(
df, model, X_test, y_test, y_pred,
output_dir="figures/dashboard"
)

# Export all visualizations
export_visualizations(output_dir="figures/export", format="png")
```

**Output**:
- PNG/SVG figures in specified directories
- JSON files with matrix data and AUC scores
- Dashboard summary

---

### 9. API Connector (`api_connector.py`) ⭐ NEW
**Purpose**: FastAPI web API for ML pipeline integration

**Key Features**:
- POST /predict - Single prediction
- POST /predict-batch - Batch predictions
- GET /model-info - Model metadata
- POST /train - Trigger training from web
- CORS support for Next.js frontend
- Input sanitization and security
- Request/response validation with Pydantic models
- Request ID tracking for debugging

**Usage**:
```python
from src.api_connector import run_api, app, create_app

# Run API server
run_api(host="0.0.0.0", port=8000)

# Or use as module
app = create_app()
```

**API Endpoints**:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/model-info` | Model metadata |
| POST | `/predict` | Single prediction |
| POST | `/predict-batch` | Batch predictions |
| POST | `/train` | Trigger training |
| GET | `/training-status/{job_id}` | Training job status |

**Example API Requests**:

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict" \
-H "Content-Type: application/json" \
-d '{
"glucose_saliva": 1.5,
"ph_value": 6.5,
"fructosamine_umol_l": 285,
"id": "sample_001"
}'

# Batch prediction
curl -X POST "http://localhost:8000/predict-batch" \
-H "Content-Type: application/json" \
-d '{
"samples": [
{"glucose_saliva": 1.5, "ph_value": 6.5, "fructosamine_umol_l": 285},
{"glucose_saliva": 0.5, "ph_value": 7.0, "fructosamine_umol_l": 220}
]
}'

# Trigger training
curl -X POST "http://localhost:8000/train" \
-H "Content-Type: application/json" \
-d '{
"n_samples": 150,
"kernel": "rbf",
"n_splits": 5
}'
```

**API Response Example**:
```json
{
"prediction": 1,
"category": {
"name": "Pre-Diabetes",
"range_mgdl": [100, 125],
"range_mmol": [5.6, 6.9]
},
"confidence": 0.85,
"probabilities": [0.05, 0.85, 0.10],
"sample_id": "sample_001",
"timestamp": "2026-07-02T19:51:00Z"
}
```

**Documentation**: http://localhost:8000/docs

---

## Directory Structure

```
ml_pipeline/
├── src/
│   ├── __init__.py                    # Module exports
│   ├── generate_dummy.py              # Data generation
│   ├── preprocessing.py               # Data preprocessing
│   ├── train_svm.py                  # Model training
│   ├── evaluate.py                    # Model evaluation
│   ├── pipeline.py                    # Pipeline orchestrator
│   ├── data_loader.py                 # Real data loading ⭐ NEW
│   ├── inference.py                   # Real-time prediction ⭐ NEW
│   ├── visualization.py               # Data visualization ⭐ NEW
│   └── api_connector.py               # FastAPI web integration ⭐ NEW
├── tests/
│   ├── test_generate_dummy.py
│   ├── test_preprocessing.py
│   ├── test_train_svm.py
│   ├── test_evaluate.py
│   ├── test_pipeline.py
│   ├── test_data_loader.py            ⭐ NEW
│   ├── test_inference.py              ⭐ NEW
│   ├── test_visualization.py          ⭐ NEW
│   └── test_api_connector.py          ⭐ NEW
├── data/
│   ├── dummy/                        # Generated synthetic data
│   ├── processed/                    # Preprocessed data
│   └── exported/                     # Exported data
├── models/                           # Trained models
├── evaluation/                       # Evaluation reports
├── figures/                          # Visualizations
│   ├── feature_distributions/
│   ├── correlation/
│   ├── confusion_matrix/
│   ├── roc_curves/
│   └── decision_boundaries/
├── pipeline_results/                 # Pipeline result summaries
└── docs/
└── MODULE_DOCS.md                # This documentation
```

## Testing

Run all tests:
```bash
cd ml_pipeline
source venv/bin/activate
python -m pytest tests/ -v
```

Expected: All tests should pass (~80-100 total tests)

Run specific test modules:
```bash
# New modules
python -m pytest tests/test_data_loader.py -v
python -m pytest tests/test_inference.py -v
python -m pytest tests/test_visualization.py -v
python -m pytest tests/test_api_connector.py -v

# All modules
python -m pytest tests/ -v --tb=short
```

## PKM-Specific Notes

### Clinical Significance
- Model must meet clinical thresholds:
- R² >= 0.50
- RMSE <= 80% of mean target
- MAE <= 60% of mean target
- Status: `PASS` or `NEEDS_IMPROVEMENT`
- Blood glucose categories:
- Normal: 70-100 mg/dL (3.9-5.6 mmol/L)
- Pre-Diabetes: 100-125 mg/dL (5.6-6.9 mmol/L)
- Diabetes: 126+ mg/dL (7.0+ mmol/L)

### Data Privacy
- Subject IDs are anonymized (integer indices)
- No personal identifiable information (PII) in dataset
- Raw CSV files should be treated as confidential
- API input validation prevents injection attacks
- Request IDs for audit trail

### Sample Size
- Target: ~150 samples for initial model
- Minimum: 10 samples for validation
- More samples = better generalization

### Budget Awareness
- All tools are open-source (Python, scikit-learn, FastAPI)
- No proprietary ML platforms
- Self-hosted API (no cloud costs)
- PNG/SVG exports for documentation (no licensing)

---

## Contributing

When adding new modules:
1. Create module in `src/`
2. Add comprehensive tests in `tests/`
3. Update `__init__.py` exports
4. Document in this file
5. Ensure all tests pass

## API Integration with Next.js

```typescript
// Example Next.js API client
const API_BASE = 'http://localhost:8000';

async function predictGlucose(sample: {
glucose_saliva: number;
ph_value: number;
fructosamine_umol_l: number;
id?: string;
}) {
const response = await fetch(`${API_BASE}/predict`, {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify(sample)
});

if (!response.ok) {
throw new Error('Prediction failed');
}

return response.json();
}

async function predictBatch(samples: typeof sample[]) {
const response = await fetch(`${API_BASE}/predict-batch`, {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ samples })
});

return response.json();
}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-02 | Initial release |
| 1.1.0 | 2026-07-02 | Added data_loader, inference, visualization, api_connector modules |

---

*GlicoSaliva ML Pipeline - Non-invasive blood glucose monitoring system*
*Developed for PKM-KC 2026 - DIKTI Partnership Program*
