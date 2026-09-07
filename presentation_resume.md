# Glicovia — 3-Minute Project Resume

**Project type:** Non-invasive blood-glucose monitoring prototype  
**Core idea:** Use saliva biomarkers and machine learning to estimate blood-glucose status, then present the result through a usable web application.

## One-line summary

I built an end-to-end health-tech prototype that connects a validated machine-learning pipeline with a web dashboard for data ingestion, glucose prediction, monitoring, and operator management.

## What I built

### 1. Machine-learning pipeline

- Generated realistic synthetic saliva data for Normal, Pre-Diabetes, and Diabetes classes, including class imbalance, outliers, and blood-glucose reference values.
- Added reusable data loading and quality validation for real CSV data, including required-column checks, missing values, outliers, variance, and minimum sample size.
- Implemented preprocessing with median imputation, IQR outlier handling, stratified 80/20 train-test splitting, and `StandardScaler` normalization.
- Trained an SVM model with an RBF kernel and `GridSearchCV` hyperparameter optimization.
- Added five-fold validation, fold-level result tracking, experiment logs, overfitting checks, and model comparison reports.
- Implemented evaluation for regression and classification: RMSE, MAE, R², accuracy, F1-score, confusion matrix, and clinical-threshold checks.
- Built reusable inference for single and batch predictions, confidence intervals through bootstrap resampling, clinical categories, and CSV/JSON export.

### 2. Glicovia application

- Built a web dashboard for health-data workflows around the model.
- Added pages and components for overview, readings, predictions, analytics, ingestion, devices, and operator activities.
- Added charts and tables for glucose trends, recent readings, subject records, and prediction results.
- Added a backend API with separated routes, controllers, services, and repositories.
- Added authentication middleware, request IDs, error handling, not-found handling, and Prisma-based database modeling.
- Designed a user-device pairing flow to connect subjects, operators, and measurement devices.

## Technical stack

**Machine learning:** Python, NumPy, pandas, scikit-learn, joblib, pytest  
**Web:** Next.js, React, TypeScript, CSS  
**Backend:** Node.js, TypeScript, Fastify-style modular API structure  
**Data:** PostgreSQL/Prisma-oriented schema, CSV/JSON interchange, persisted model artifacts  
**Engineering practices:** modular architecture, reproducible experiments, validation reports, automated tests, diagrams, and documented pipeline stages

## Project impact

The main achievement was integrating research-oriented machine learning into a product-shaped workflow. Instead of stopping at model training, the project carries data from ingestion through preprocessing, prediction, storage, visualization, and operator review.

## 3-minute presentation script

“My project is called Glicovia, a prototype for non-invasive blood-glucose monitoring using saliva biomarkers.

The problem I focused on is that glucose monitoring is usually invasive and inconvenient. My approach was to build both sides of the solution: the machine-learning pipeline that produces a prediction, and the application that makes the prediction usable.

On the machine-learning side, I created a complete pipeline. It can generate controlled synthetic saliva data for three clinical categories: Normal, Pre-Diabetes, and Diabetes. It can also load real CSV data and check its quality. Before training, the pipeline handles missing values, detects outliers, scales the features, and creates a stratified train-test split.

For modeling, I used an SVM with an RBF kernel and hyperparameter optimization through cross-validation. I also added fold-level tracking, experiment logs, model comparison, and overfitting checks. The evaluation stage reports both regression and classification metrics, including RMSE, MAE, R-squared, accuracy, F1-score, and a confusion matrix. For inference, the system supports single and batch predictions, confidence intervals, clinical categories, and exportable results.

On the application side, I built Glicovia as a dashboard around that pipeline. It includes data ingestion, readings, predictions, analytics, device management, subject records, and operator workflows. The backend is organized into routes, controllers, services, and repositories, with authentication, request tracking, error handling, and database models for user-device pairing.

The most important result is the end-to-end integration. This is not only a model experiment and not only a dashboard. It is a product-shaped prototype that moves from biomarker data to a validated prediction and then to a clear interface for monitoring and decision support.

In the next stage, I would replace the synthetic data with a larger clinically validated dataset, improve calibration and uncertainty analysis, and conduct formal clinical and usability validation.”

## Suggested closing sentence

“Glicovia demonstrates my ability to connect machine learning, backend engineering, data quality, and frontend product design into one coherent system.”

