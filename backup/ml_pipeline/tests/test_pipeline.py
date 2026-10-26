from __future__ import annotations

from src.pipeline import MLPipeline, run_pipeline


def test_pipeline_module_exports_entrypoints():
    assert callable(run_pipeline)
    assert MLPipeline is not None
