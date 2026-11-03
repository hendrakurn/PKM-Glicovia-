"""Kalibrasi SEMENTARA: sinyal alat (volt / nA) -> satuan riil masukan model.

Harus sama dengan konstanta di firmware (hardware/f_endtoend_auto/f_endtoend_auto.ino: PH_M, PH_C,
GLU_A/B, FRU_A/B) agar nilai latih = nilai yang dikirim alat. Ubah konstanta di sini -> latih ulang model.
  pH          : V = PH_M * pH + PH_C            (Nernst 59,16 mV/pH; sama dengan ml_pipeline & backend)
  glukosa     : I(nA) = GLU_A * mg/dL + GLU_B   (kanal jenuh, hampir tidak informatif)
  fruktosamin : I(nA) = FRU_A * umol/L + FRU_B,  I = (VMID - Vfru) / RF
Hasil dipotong ke rentang yang sama dengan firmware.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

RF = 100e3
PH_M, PH_C = -0.05916, 0.3226
GLU_A, GLU_B = 1000.0, 0.0
FRU_A, FRU_B = 35.0, -4000.0
BOUNDS = {"glucose_saliva": (0.1, 10.0), "ph_value": (4.0, 9.0), "fructosamine_umol_l": (150.0, 500.0)}
CAL = {"ph": {"m": PH_M, "c": PH_C}, "glu": {"a": GLU_A, "b": GLU_B}, "fru": {"a": FRU_A, "b": FRU_B}, "rf_ohm": RF}


def ph_from_v(v):
    return np.clip((v - PH_C) / PH_M, *BOUNDS["ph_value"])


def glucose_from_i(i_nA):
    return np.clip((i_nA - GLU_B) / GLU_A, *BOUNDS["glucose_saliva"])


def fructosamine_from_v(v_mid, v_fru):
    i_nA = (v_mid - v_fru) / RF * 1e9
    return np.clip((i_nA - FRU_B) / FRU_A, *BOUNDS["fructosamine_umol_l"])


def with_calibrated(df: pd.DataFrame) -> pd.DataFrame:
    """Tambah kolom satuan riil dari v_ph, v_fru, v_mid, i_nA. Kolom yang sudah ada tidak ditimpa."""
    out = df.copy()
    if "ph_value" not in out:
        out["ph_value"] = ph_from_v(out["v_ph"])
    if "glucose_saliva" not in out:
        out["glucose_saliva"] = glucose_from_i(out["i_nA"])
    if "fructosamine_umol_l" not in out:
        out["fructosamine_umol_l"] = fructosamine_from_v(out["v_mid"], out["v_fru"])
    return out
