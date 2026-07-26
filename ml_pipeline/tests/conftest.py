from __future__ import annotations

from pathlib import Path
import pickle

import numpy as np
import pytest
from sklearn.svm import SVR

from src.generate_dummy import generate_dummy
from src.preprocessing import preprocess


@pytest.fixture()
def dummy_dataset(tmp_path: Path):
    output_dir = tmp_path / "dummy"
    df, metadata = generate_dummy(n_samples=120, random_state=7, output_dir=str(output_dir))
    return df, metadata, output_dir


@pytest.fixture()
def preprocessed_bundle(tmp_path: Path, dummy_dataset):
    _, _, dummy_dir = dummy_dataset
    processed_dir = tmp_path / "processed"
    result = preprocess(raw_csv_path=str(dummy_dir / "generated_data.csv"), output_dir=str(processed_dir))
    return result, processed_dir


@pytest.fixture()
def trained_model_bundle(tmp_path: Path, preprocessed_bundle):
    result, processed_dir = preprocessed_bundle
    X_train = np.load(processed_dir / "X_train.npy")
    y_train = np.load(processed_dir / "y_train.npy")

    model = SVR(kernel="rbf", C=5.0, gamma="scale", epsilon=0.1)
    model.fit(X_train, y_train)

    model_path = tmp_path / "best_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    scaler_path = processed_dir / "scaler_params.json"
    return {
        "model_path": str(model_path),
        "scaler_path": str(scaler_path),
        "processed_dir": processed_dir,
        "preprocess_result": result,
    }
