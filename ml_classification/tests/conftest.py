import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cls.train import CLASSES, train  # noqa: E402


def make_df(subjects_per_class: int = 3, sessions: int = 2, seed: int = 0) -> pd.DataFrame:
    """Data sintetis terpisah jelas per kelas (satuan riil). fructosamine_umol_l = nomor subjek (tes kebocoran)."""
    rng = np.random.default_rng(seed)
    rows, sid = [], 0
    for c, name in enumerate(CLASSES):
        for _ in range(subjects_per_class):
            sid += 1
            for s in range(sessions):
                rows.append({"session_id": f"s{sid}_{s}", "subject_code": f"P{sid:02d}", "label_class": name,
                             "glucose_saliva": 1.0 + 3 * c + rng.normal(0, 0.1),
                             "ph_value": 5.0 + 1.5 * c + rng.normal(0, 0.1),
                             "fructosamine_umol_l": float(sid), "batch": "20261026"})
    return pd.DataFrame(rows)


def save_model(tmp_path: Path, df: pd.DataFrame, version: str) -> str:
    model, meta = train(df, ["glucose_saliva", "ph_value"])
    path = tmp_path / f"model_cls_{version}.pkl"
    path.write_bytes(pickle.dumps(model))
    path.with_suffix(".json").write_text(json.dumps({"version": version, **meta}))
    return str(path)


@pytest.fixture
def ready_model(tmp_path):
    return save_model(tmp_path, make_df(subjects_per_class=3), "ready")


@pytest.fixture
def not_ready_model(tmp_path):
    return save_model(tmp_path, make_df(subjects_per_class=1, sessions=3), "notready")
