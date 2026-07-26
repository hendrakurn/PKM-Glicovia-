"""GlicoSaliva ML Pipeline modules.

Keep package initialization lightweight: avoid importing pipeline-level
modules here because several modules use top-level imports that are only safe
when the package is executed from the project root or src directory.

Import concrete modules/functions directly, e.g.::

    from src.generate_dummy import generate_dummy
    from src.preprocessing import preprocess
"""

from src.generate_dummy import generate_dummy
from src.preprocessing import preprocess
from src.train_svm import train_svm
from src.evaluate import evaluate, compare_models
from src.data_loader import load_data, load_batch, export_to_json, export_to_csv
from src.inference import predict_single, predict_batch, export_predictions
from src.api_connector import app

__all__ = [
    "generate_dummy",
    "preprocess",
    "train_svm",
    "evaluate",
    "compare_models",
    "load_data",
    "load_batch",
    "export_to_json",
    "export_to_csv",
    "predict_single",
    "predict_batch",
    "export_predictions",
    "app",
]
