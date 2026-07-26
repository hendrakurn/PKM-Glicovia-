"""CLI wrapper for single-sample inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.inference import predict_single

DEFAULT_MODEL_PATH = str(Path(__file__).resolve().parent / "src" / "models" / "best_model.pkl")
DEFAULT_SCALER_PATH = str(Path(__file__).resolve().parent / "src" / "data" / "processed" / "scaler_params.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GlicoSaliva prediction from the command line")
    parser.add_argument("--glucose-saliva", type=float, required=True, dest="glucose_saliva")
    parser.add_argument("--ph-value", type=float, required=True, dest="ph_value")
    parser.add_argument("--fructosamine-umol-l", type=float, required=True, dest="fructosamine_umol_l")
    parser.add_argument("--sample-id", type=str, default=None, dest="id")
    parser.add_argument("--model-path", type=str, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--scaler-path", type=str, default=DEFAULT_SCALER_PATH)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sample = {
        "id": args.id,
        "glucose_saliva": args.glucose_saliva,
        "ph_value": args.ph_value,
        "fructosamine_umol_l": args.fructosamine_umol_l,
    }
    result = predict_single(sample=sample, model_path=args.model_path, scaler_path=args.scaler_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
