"""
evaluate.py - Model Evaluation Module for GlicoSaliva ML Pipeline

Evaluates trained SVM model performance using standard regression metrics
(RMSE, MAE, R²) and classification metrics (accuracy, F1-score) for
non-invasive blood glucose monitoring.

Target: Generate comprehensive evaluation metrics for model validation
"""

import json
import logging
import os
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelEvaluationWarning(UserWarning):
    """Custom warning for model evaluation issues."""
    pass


# Default evaluation thresholds
DEFAULT_THRESHOLDS = {
    "accuracy_min": 0.70,
    "f1_macro_min": 0.60,
    "r2_min": 0.50,
    "rmse_max_percentile": 80.0,  # Max acceptable RMSE as % of mean target
    "mae_max_percentile": 60.0    # Max acceptable MAE as % of mean target
}

# Blood glucose clinical categories (mg/dL)
BGL_CATEGORIES = {
    0: {"name": "Normal", "range": (70, 100)},
    1: {"name": "Pre-Diabetes", "range": (100, 125)},
    2: {"name": "Diabetes", "range": (126, 500)}
}


def _calculate_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> dict:
    """Calculate regression metrics.
    
    Args:
        y_true: Ground truth values
        y_pred: Predicted values
        
    Returns:
        Dictionary with regression metrics
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    # Calculate percentage errors relative to mean target
    mean_target = np.mean(y_true)
    rmse_percent = (rmse / mean_target) * 100 if mean_target > 0 else float('inf')
    mae_percent = (mae / mean_target) * 100 if mean_target > 0 else float('inf')
    
    return {
        "rmse": float(rmse),
        "rmse_percent_of_mean": float(rmse_percent),
        "mae": float(mae),
        "mae_percent_of_mean": float(mae_percent),
        "r2": float(r2),
        "mean_target": float(mean_target)
    }


def _calculate_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> dict:
    """Calculate classification metrics.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        
    Returns:
        Dictionary with classification metrics
    """
    accuracy = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    conf_matrix = confusion_matrix(y_true, y_pred)
    
    # Per-class F1 scores
    unique_classes = np.unique(np.concatenate([y_true, y_pred]))
    f1_per_class = {}
    for cls in unique_classes:
        f1_cls = f1_score(y_true, y_pred, labels=[cls], average="macro", zero_division=0)
        f1_per_class[str(int(cls))] = float(f1_cls)
    
    return {
        "accuracy": float(accuracy),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "f1_per_class": f1_per_class,
        "confusion_matrix": conf_matrix.tolist(),
        "num_samples": int(len(y_true))
    }


def _evaluate_model_clinical_significance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    thresholds: dict
) -> dict:
    """Evaluate if model meets clinical significance thresholds.
    
    Args:
        y_true: Ground truth values
        y_pred: Predicted values
        thresholds: Threshold dictionary for evaluation
        
    Returns:
        Dictionary with clinical significance assessment
    """
    metrics = _calculate_regression_metrics(y_true, y_pred)
    
    # Check against thresholds
    meets_accuracy = metrics["r2"] >= thresholds.get("r2_min", 0.50)
    meets_rmse = metrics["rmse_percent_of_mean"] <= thresholds.get("rmse_max_percentile", 80.0)
    meets_mae = metrics["mae_percent_of_mean"] <= thresholds.get("mae_max_percentile", 60.0)
    
    # Clinical interpretation
    clinical_status = "PASS" if (meets_accuracy and meets_rmse and meets_mae) else "NEEDS_IMPROVEMENT"
    
    issues = []
    if not meets_accuracy:
        issues.append(f"R² ({metrics['r2']:.4f}) below threshold ({thresholds.get('r2_min', 0.50)})")
    if not meets_rmse:
        issues.append(f"RMSE ({metrics['rmse_percent_of_mean']:.2f}%) exceeds threshold ({thresholds.get('rmse_max_percentile', 80.0)}%)")
    if not meets_mae:
        issues.append(f"MAE ({metrics['mae_percent_of_mean']:.2f}%) exceeds threshold ({thresholds.get('mae_max_percentile', 60.0)}%)")
    
    return {
        "clinical_status": clinical_status,
        "meets_thresholds": {
            "r2": meets_accuracy,
            "rmse": meets_rmse,
            "mae": meets_mae
        },
        "issues": issues,
        "recommendations": []
    }


def _generate_evaluation_report(
    model_type: str,
    regression_metrics: dict,
    classification_metrics: dict,
    clinical_assessment: dict,
    timestamp: str
) -> dict:
    """Generate comprehensive evaluation report.
    
    Args:
        model_type: Type of model evaluated (e.g., "SVC", "SVR")
        regression_metrics: Regression metrics dictionary
        classification_metrics: Classification metrics dictionary
        clinical_assessment: Clinical significance assessment
        timestamp: ISO format timestamp
        
    Returns:
        Complete evaluation report dictionary
    """
    return {
        "model_type": model_type,
        "evaluation_timestamp": timestamp,
        "regression_metrics": regression_metrics,
        "classification_metrics": classification_metrics,
        "clinical_assessment": clinical_assessment,
        "overall_status": clinical_assessment["clinical_status"]
    }


def evaluate(
    model_path: str,
    X_test_path: str,
    y_test_path: str,
    scaler_params_path: Optional[str] = None,
    output_dir: str = "evaluation",
    thresholds: dict = None,
    random_state: int = 42
) -> dict:
    """Evaluate trained model on test set.
    
    Args:
        model_path: Path to trained model (.pkl file)
        X_test_path: Path to test features (.npy file)
        y_test_path: Path to test labels (.npy file)
        scaler_params_path: Path to scaler parameters (optional, for reconstruction)
        output_dir: Directory for output files (default: "evaluation")
        thresholds: Evaluation thresholds. If None, uses DEFAULT_THRESHOLDS.
        random_state: Random state for reproducibility
        
    Returns:
        Dictionary with evaluation results including paths to output files
        
    Raises:
        FileNotFoundError: If any required input file not found
        ValueError: If model or data loading fails
        
    Examples:
        >>> result = evaluate(
        ...     model_path="models/best_model.pkl",
        ...     X_test_path="data/processed/X_test.npy",
        ...     y_test_path="data/processed/y_test.npy",
        ...     output_dir="evaluation/"
        ... )
        >>> print(result['evaluation_report_path'])
        'evaluation/evaluation_report.json'
    """
    # Initialize thresholds
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS.copy()
    
    # Validate input files exist
    required_files = [model_path, X_test_path, y_test_path]
    for filepath in required_files:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Required file not found: {filepath}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load model
    logger.info(f"Loading model from {model_path}")
    try:
        with open(model_path, 'rb') as f:
            import pickle
            model = pickle.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load model from {model_path}: {e}")
    
    # Load test data
    logger.info(f"Loading test data from {X_test_path}, {y_test_path}")
    X_test = np.load(X_test_path)
    y_test = np.load(y_test_path)
    
    logger.info(f"Test data shape: X={X_test.shape}, y={y_test.shape}")
    
    # Make predictions
    logger.info("Making predictions on test set")
    try:
        y_pred = model.predict(X_test)
    except Exception as e:
        raise ValueError(f"Model prediction failed: {e}")
    
    # Determine if regression or classification based on label type
    is_regression = np.issubdtype(y_test.dtype, np.floating) or len(np.unique(y_test)) > 10
    
    # Calculate metrics
    if is_regression:
        logger.info("Calculating regression metrics")
        regression_metrics = _calculate_regression_metrics(y_test, y_pred)
        classification_metrics = {}
    else:
        logger.info("Calculating classification metrics")
        regression_metrics = {}
        classification_metrics = _calculate_classification_metrics(y_test, y_pred)
    
    # Clinical significance evaluation
    logger.info("Evaluating clinical significance")
    clinical_assessment = _evaluate_model_clinical_significance(y_test, y_pred, thresholds)
    
    # Generate timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Determine model type
    model_type = type(model).__name__
    
    # Generate evaluation report
    report = _generate_evaluation_report(
        model_type=model_type,
        regression_metrics=regression_metrics,
        classification_metrics=classification_metrics,
        clinical_assessment=clinical_assessment,
        timestamp=timestamp
    )
    
    # Save evaluation report
    report_path = output_path / "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Saved evaluation report to {report_path}")
    
    # Save predictions for further analysis
    pred_path = output_path / "predictions.npy"
    np.save(pred_path, y_pred)
    
    # Save confusion matrix if classification
    if not is_regression:
        conf_matrix_path = output_path / "confusion_matrix.npy"
        np.save(conf_matrix_path, classification_metrics["confusion_matrix"])
    
    logger.info(f"Saved predictions to {pred_path}")
    
    # Return results
    return {
        "evaluation_report_path": str(report_path),
        "predictions_path": str(pred_path),
        "model_type": model_type,
        "regression_metrics": regression_metrics,
        "classification_metrics": classification_metrics,
        "clinical_assessment": clinical_assessment,
        "y_test_path": str(y_test_path),
        "y_pred_path": str(pred_path)
    }


def compare_models(
    model_results: list,
    output_dir: str = "model_comparison"
) -> dict:
    """Compare multiple trained models.
    
    Args:
        model_results: List of dictionaries from evaluate() calls
        output_dir: Directory for comparison output
        
    Returns:
        Dictionary with model comparison results
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extract metrics from each model
    comparison_data = []
    for i, result in enumerate(model_results):
        entry = {
            "model_index": i,
            "model_type": result.get("model_type", "Unknown"),
            "timestamp": result.get("evaluation_timestamp", "N/A"),
            "regression_metrics": result.get("regression_metrics", {}),
            "classification_metrics": result.get("classification_metrics", {}),
            "clinical_status": result.get("clinical_assessment", {}).get("overall_status", "N/A")
        }
        comparison_data.append(entry)
    
    # Find best model based on primary metrics
    best_model = None
    best_score = float('-inf')
    
    for entry in comparison_data:
        # Primary metric: F1-macro for classification, R² for regression
        if entry.get("classification_metrics"):
            score = entry["classification_metrics"].get("f1_macro", 0)
        elif entry.get("regression_metrics"):
            score = entry["regression_metrics"].get("r2", 0)
        else:
            score = 0
        
        if score > best_score:
            best_score = score
            best_model = entry
    
    comparison_report = {
        "models_compared": len(comparison_data),
        "best_model": best_model,
        "best_score": float(best_score),
        "all_models": comparison_data
    }
    
    # Save comparison report
    comparison_path = output_path / "model_comparison.json"
    with open(comparison_path, "w") as f:
        json.dump(comparison_report, f, indent=2)
    
    logger.info(f"Saved model comparison to {comparison_path}")
    
    return comparison_report


if __name__ == "__main__":
    # Example usage
    print("Running model evaluation...")
    
    result = evaluate(
        model_path="models/best_model.pkl",
        X_test_path="data/processed/X_test.npy",
        y_test_path="data/processed/y_test.npy",
        output_dir="evaluation/"
    )
    
    print(f"\nEvaluation complete!")
    print(f"Report: {result['evaluation_report_path']}")
    print(f"Clinical status: {result['clinical_assessment']['clinical_status']}")
    
    if result.get("regression_metrics"):
        print(f"\nRegression Metrics:")
        for key, value in result["regression_metrics"].items():
            print(f"  {key}: {value}")
    
    if result.get("classification_metrics"):
        print(f"\nClassification Metrics:")
        for key, value in result["classification_metrics"].items():
            if key not in ["confusion_matrix", "f1_per_class"]:
                print(f"  {key}: {value}")
