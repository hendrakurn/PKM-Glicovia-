from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

from src.generate_dummy import generate_dummy
from src.visualization import create_correlation_heatmap, create_feature_distributions, save_figure


def test_visualization_functions_work_with_fructosamine(tmp_path):
    df, _, _ = generate_dummy(n_samples=60, random_state=19, output_dir=str(tmp_path / "dummy"))
    dist_fig = create_feature_distributions(df, output_dir=str(tmp_path / "figs"))
    heat_fig = create_correlation_heatmap(df, output_dir=str(tmp_path / "figs"))

    dist_path = save_figure(dist_fig, str(tmp_path / "figs" / "dist.png"))
    heat_path = save_figure(heat_fig, str(tmp_path / "figs" / "heat.png"))

    assert Path(dist_path).exists()
    assert Path(heat_path).exists()
