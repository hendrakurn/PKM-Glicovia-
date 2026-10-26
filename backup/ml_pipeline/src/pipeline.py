"""
pipeline.py - Main ML Pipeline Orchestrator for GlicoSaliva

Orchestrates the complete ML pipeline:
1. Generate synthetic data (or load real data)
2. Preprocess data (scaling, split, outlier handling)
3. Train SVM model with hyperparameter optimization
4. Evaluate model performance

Target: Single command to run entire ML pipeline from scratch
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add src to path when running as a script from the project root.
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Prefer package imports when available; fall back to local script imports when
# the file is executed directly from ml_pipeline/src.
try:
    from src.generate_dummy import generate_dummy
    from src.preprocessing import preprocess
    from src.train_svm import train_svm
    from src.evaluate import evaluate, compare_models
except ImportError:  # pragma: no cover - script execution fallback
    from generate_dummy import generate_dummy
    from preprocessing import preprocess
    from train_svm import train_svm
    from evaluate import evaluate, compare_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Default pipeline configuration
DEFAULT_PIPELINE_CONFIG = {
    # Data generation settings
    "generate_dummy": True,
    "n_samples": 150,
    "random_state": 42,
    
    # Preprocessing settings
    "test_size": 0.2,
    "outlier_strategy": "remove",
    
    # Training settings
    "kernel": "rbf",
    "n_splits": 5,
    
    # Evaluation settings
    "r2_min": 0.50,
    "rmse_max_percentile": 80.0,
    "mae_max_percentile": 60.0
}


class PipelineConfigError(ValueError):
    """Error in pipeline configuration."""
    pass


class MLPipeline:
    """Orchestrates the complete ML pipeline for blood glucose prediction."""
    
    def __init__(self, config: dict = None):
        """Initialize pipeline with configuration.
        
        Args:
            config: Pipeline configuration dictionary. If None, uses DEFAULT_PIPELINE_CONFIG.
        """
        if config is None:
            self.config = DEFAULT_PIPELINE_CONFIG.copy()
        else:
            self.config = DEFAULT_PIPELINE_CONFIG.copy()
            self.config.update(config)
        
        # Create base directories
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.models_dir = self.base_dir / "models"
        self.evaluation_dir = self.base_dir / "evaluation"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.evaluation_dir.mkdir(parents=True, exist_ok=True)
        
        # Store pipeline results
        self.pipeline_results = {}
    
    def run_full_pipeline(self) -> dict:
        """Run complete ML pipeline from data generation to evaluation.
        
        Returns:
            Dictionary with complete pipeline results and output paths
        
        Raises:
            PipelineConfigError: If any pipeline step fails
        """
        logger.info("=" * 60)
        logger.info("Starting GlicoSaliva ML Pipeline")
        logger.info("=" * 60)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.pipeline_results["pipeline_timestamp"] = timestamp
        
        try:
            # Step 1: Data Generation
            if self.config.get("generate_dummy", True):
                logger.info("\n" + "=" * 60)
                logger.info("STEP 1: DATA GENERATION")
                logger.info("=" * 60)
                
                dummy_result = self._generate_data()
                self.pipeline_results["data_generation"] = dummy_result
                logger.info(f"✓ Data generation completed: {dummy_result['n_samples']} samples")
            else:
                logger.info("\n" + "=" * 60)
                logger.info("STEP 1: DATA GENERATION SKIPPED (loading existing data)")
                logger.info("=" * 60)
                dummy_result = None
            
            # Step 2: Preprocessing
            logger.info("\n" + "=" * 60)
            logger.info("STEP 2: DATA PREPROCESSING")
            logger.info("=" * 60)
            
            preprocess_result = self._preprocess_data()
            self.pipeline_results["preprocessing"] = preprocess_result
            logger.info(f"✓ Preprocessing completed: {preprocess_result['train_samples']} train, "
                       f"{preprocess_result['test_samples']} test")
            
            # Step 3: Model Training
            logger.info("\n" + "=" * 60)
            logger.info("STEP 3: MODEL TRAINING")
            logger.info("=" * 60)
            
            train_result = self._train_model()
            self.pipeline_results["training"] = train_result
            logger.info(f"✓ Training completed: Test R² = {train_result['test_r2']:.4f}")
            
            # Step 4: Model Evaluation
            logger.info("\n" + "=" * 60)
            logger.info("STEP 4: MODEL EVALUATION")
            logger.info("=" * 60)
            
            evaluate_result = self._evaluate_model()
            self.pipeline_results["evaluation"] = evaluate_result
            logger.info(f"✓ Evaluation completed: Clinical status = "
                       f"{evaluate_result['clinical_assessment']['clinical_status']}")
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
            self.pipeline_results["pipeline_status"] = "SUCCESS"
            self.pipeline_results["pipeline_summary"] = self._generate_summary()
            
            return self.pipeline_results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.pipeline_results["pipeline_status"] = "FAILED"
            self.pipeline_results["error"] = str(e)
            raise PipelineConfigError(f"Pipeline failed: {e}")
    
    def _generate_data(self) -> dict:
        """Generate synthetic data or load existing."""
        output_dir = self.data_dir / "dummy"
        
        # Check if data already exists
        existing_csv = output_dir / "generated_data.csv"
        if existing_csv.exists():
            logger.info(f"Loading existing data from {existing_csv}")
            # Load the CSV to get sample count
            import pandas as pd
            df = pd.read_csv(existing_csv)
            return {
                "status": "loaded", 
                "path": str(existing_csv),
                "n_samples": len(df)
            }
        
        # Generate new data
        result = generate_dummy(
            n_samples=self.config.get("n_samples", 150),
            random_state=self.config.get("random_state", 42),
            output_dir=str(output_dir)
        )
        
        return {
            "status": "generated",
            "n_samples": result[1]["total_samples"],
            "class_distribution": result[1]["class_distribution"],
            "output_path": str(output_dir / "generated_data.csv")
        }
    
    def _preprocess_data(self) -> dict:
        """Preprocess data for training."""
        input_csv = self.data_dir / "dummy" / "generated_data.csv"
        output_dir = self.data_dir / "processed"
        
        # Load preprocessing config
        preprocess_config = {
            "test_size": self.config.get("test_size", 0.2),
            "outlier_strategy": self.config.get("outlier_strategy", "remove"),
            "random_state": self.config.get("random_state", 42)
        }
        
        result = preprocess(
            raw_csv_path=str(input_csv),
            output_dir=str(output_dir),
            config=preprocess_config
        )
        
        return {
            "train_samples": result["train_samples"],
            "test_samples": result["test_samples"],
            "feature_names": result["feature_names"],
            "X_train_path": result["X_train_path"],
            "X_test_path": result["X_test_path"],
            "y_train_path": result["y_train_path"],
            "y_test_path": result["y_test_path"],
            "scaler_params_path": result["scaler_params_path"]
        }
    
    def _train_model(self) -> dict:
        """Train SVM model."""
        processed_dir = self.data_dir / "processed"
        
        # Load training config
        train_config = {
            "kernel": self.config.get("kernel", "rbf"),
            "n_splits": self.config.get("n_splits", 5),
            "random_state": self.config.get("random_state", 42)
        }
        
        result = train_svm(
            processed_data_path=str(processed_dir),
            output_dir=str(self.models_dir),
            config=train_config
        )
        
        return {
            "best_model_path": result["best_model_path"],
            "experiment_log_path": result["experiment_log_path"],
            "best_params": result["best_params"],
            "train_r2": result["train_r2"],
            "test_r2": result["test_r2"],
            "train_rmse": result["train_rmse"],
            "test_rmse": result["test_rmse"],
            "train_mae": result["train_mae"],
            "test_mae": result["test_mae"],
            "overfitting_detected": result["overfitting_detected"],
            "cv_results": result["cv_results"]
        }
    
    def _evaluate_model(self) -> dict:
        """Evaluate trained model."""
        # Load evaluation config
        eval_config = {
            "r2_min": self.config.get("r2_min", 0.50),
            "rmse_max_percentile": self.config.get("rmse_max_percentile", 80.0),
            "mae_max_percentile": self.config.get("mae_max_percentile", 60.0)
        }
        
        result = evaluate(
            model_path=self.pipeline_results["training"]["best_model_path"],
            X_test_path=self.pipeline_results["preprocessing"]["X_test_path"],
            y_test_path=self.pipeline_results["preprocessing"]["y_test_path"],
            output_dir=str(self.evaluation_dir),
            thresholds=eval_config
        )
        
        return result
    
    def _generate_summary(self) -> dict:
        """Generate pipeline summary."""
        summary = {
            "total_samples": self.pipeline_results.get("data_generation", {}).get("n_samples", 0),
            "train_samples": self.pipeline_results.get("preprocessing", {}).get("train_samples", 0),
            "test_samples": self.pipeline_results.get("preprocessing", {}).get("test_samples", 0),
            "model_type": f"SVR-{self.config.get('kernel', 'rbf')}",
            "train_r2": self.pipeline_results.get("training", {}).get("train_r2", 0),
            "test_r2": self.pipeline_results.get("training", {}).get("test_r2", 0),
            "clinical_status": self.pipeline_results.get("evaluation", {}).get(
                "clinical_assessment", {}
            ).get("clinical_status", "UNKNOWN")
        }
        
        return summary
    
    def save_pipeline_results(self, output_path: Optional[str] = None) -> str:
        """Save complete pipeline results to JSON file.
        
        Args:
            output_path: Optional custom output path. If None, uses default location.
            
        Returns:
            Path to saved results file
        """
        if output_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = self.base_dir / "pipeline_results" / f"pipeline_{timestamp}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare serializable results
        serializable_results = {
            k: str(v) if isinstance(v, Path) else v 
            for k, v in self.pipeline_results.items()
        }
        
        with open(output_path, "w") as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Pipeline results saved to {output_path}")
        return str(output_path)


def run_pipeline(config: dict = None) -> dict:
    """Convenience function to run ML pipeline.
    
    Args:
        config: Pipeline configuration. If None, uses defaults.
        
    Returns:
        Dictionary with pipeline results
    """
    pipeline = MLPipeline(config=config)
    results = pipeline.run_full_pipeline()
    pipeline.save_pipeline_results()
    return results


if __name__ == "__main__":
    # Run complete ML pipeline
    print("Running GlicoSaliva ML Pipeline...")
    print("=" * 60)
    
    # Example custom config
    custom_config = {
        "n_samples": 150,
        "test_size": 0.2,
        "kernel": "rbf",
        "n_splits": 5,
        "random_state": 42
    }
    
    results = run_pipeline(config=custom_config)
    
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    
    summary = results.get("pipeline_summary", {})
    print(f"Total samples: {summary.get('total_samples', 0)}")
    print(f"Train samples: {summary.get('train_samples', 0)}")
    print(f"Test samples: {summary.get('test_samples', 0)}")
    print(f"Model type: {summary.get('model_type', 'N/A')}")
    print(f"Train R²: {summary.get('train_r2', 0):.4f}")
    print(f"Test R²: {summary.get('test_r2', 0):.4f}")
    print(f"Clinical status: {summary.get('clinical_status', 'UNKNOWN')}")
    
    print("\n" + "=" * 60)
    print("Output files:")
    print(f"  - Model: {results.get('training', {}).get('best_model_path', 'N/A')}")
    print(f"  - Evaluation: {results.get('evaluation', {}).get('evaluation_report_path', 'N/A')}")
    print(f"  - Results JSON: {results.get('results_path', 'N/A')}")
    print("=" * 60)
