from __future__ import annotations

import pandas as pd

from src.generate_dummy import FEATURE_BOUNDS, generate_dummy


def test_generate_dummy_uses_fructosamine_feature(tmp_path):
    output_dir = tmp_path / "dummy"
    df, metadata = generate_dummy(n_samples=150, random_state=42, output_dir=str(output_dir))

    assert list(df.columns) == [
        "id",
        "glucose_saliva",
        "ph_value",
        "fructosamine_umol_l",
        "bg_class",
        "bg_mgdl_reference",
    ]
    assert metadata["total_samples"] == 150
    assert set(metadata["feature_ranges"].keys()) == {"glucose_saliva", "ph_value", "fructosamine_umol_l"}
    assert output_dir.joinpath("generated_data.csv").exists()
    assert output_dir.joinpath("metadata.json").exists()

    low, high = FEATURE_BOUNDS["fructosamine_umol_l"]
    assert df["fructosamine_umol_l"].between(low, high).all()
    assert df["bg_mgdl_reference"].between(60, 500).all()


def test_generate_dummy_fructosamine_correlates_positively_with_target(tmp_path):
    df, _ = generate_dummy(n_samples=150, random_state=21, output_dir=str(tmp_path / "dummy2"))
    corr = df[["fructosamine_umol_l", "bg_mgdl_reference"]].corr().iloc[0, 1]
    assert corr > 0.25
    assert df["bg_class"].isin([0, 1, 2]).all()
