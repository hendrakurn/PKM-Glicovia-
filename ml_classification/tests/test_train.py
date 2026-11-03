import numpy as np
import pytest
from conftest import make_df

from cls.train import load_xyg, loso_predict, train

FEATURES = ["glucose_saliva", "ph_value"]


class _LeakSpy:
    """Estimator palsu: kolom ke-3 (fructosamine_umol_l) = nomor subjek; gagal bila subjek uji ada di data latih."""

    def fit(self, X, y):
        self.seen = set(X[:, 2])
        self.label = y[0]
        return self

    def predict(self, X):
        assert not (set(X[:, 2]) & self.seen), "subjek uji ikut di data latih"
        return np.full(len(X), self.label)


def test_loso_never_leaks_subject():
    X, y, groups = load_xyg(make_df())
    pred = loso_predict(_LeakSpy, X, y, groups)
    assert (pred >= 0).all()


def test_train_rejects_single_class():
    df = make_df()
    df = df[df["label_class"] == "NORMAL"]
    with pytest.raises(ValueError):
        train(df, FEATURES)


def test_model_not_ready_when_few_subjects():
    _, meta = train(make_df(subjects_per_class=1, sessions=3), FEATURES)
    assert meta["model_not_ready"] is True
    _, meta = train(make_df(subjects_per_class=3), FEATURES)
    assert meta["model_not_ready"] is False
