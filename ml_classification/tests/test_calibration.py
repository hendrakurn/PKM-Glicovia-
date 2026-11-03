import pandas as pd
import pytest

from cls.calibration import PH_C, PH_M, fructosamine_from_v, glucose_from_i, ph_from_v, with_calibrated


def test_ph_roundtrip_and_clip():
    assert ph_from_v(PH_M * 7.0 + PH_C) == pytest.approx(7.0)
    assert ph_from_v(-10.0) == 9.0 and ph_from_v(10.0) == 4.0     # di luar rentang -> dipotong


def test_glucose_and_fructosamine():
    assert glucose_from_i(7175.0) == pytest.approx(7.175)
    assert glucose_from_i(0.0) == 0.1
    assert fructosamine_from_v(0.91, 0.0) == pytest.approx((9100 + 4000) / 35)   # I = 9100 nA


def test_with_calibrated_keeps_existing_columns():
    df = pd.DataFrame({"v_ph": [PH_M * 6 + PH_C], "i_nA": [5000.0], "v_mid": [0.91], "v_fru": [0.0]})
    out = with_calibrated(df)
    assert out["ph_value"].iloc[0] == pytest.approx(6.0)
    kept = with_calibrated(out.assign(ph_value=7.5))
    assert kept["ph_value"].iloc[0] == 7.5
