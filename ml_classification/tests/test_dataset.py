import pytest

from cls.dataset import mgdl_to_class, parse_name


@pytest.mark.parametrize("stem, expected", [
    ("glicovia_148_DIABETES_20261021_030626", ("S148", 148, "20261021")),
    ("glicovia_88_NORMAL_backup_2_20261021_050247", ("S088", 88, "20261021")),
    ("glicovia_1_77_20261026_200951", ("P01", 77, "20261026")),
    ("glicovia_2_12_112mgdl_20261026_201820", ("P02", 112, "20261026")),
])
def test_parse_name_both_formats(stem, expected):
    assert parse_name(stem) == expected


@pytest.mark.parametrize("stem", [
    "glicovia_abc_20261026_200951",     # tidak ada angka
    "glicovia_77_20261026_200951",      # hanya satu angka
    "glicovia_1_77",                    # tanpa stamp
    "other_1_77_20261026_200951",       # awalan salah
])
def test_parse_name_rejects_unknown(stem):
    with pytest.raises(ValueError):
        parse_name(stem)


def test_mgdl_to_class_thresholds():
    assert [mgdl_to_class(v) for v in (99, 100, 125, 126)] == ["NORMAL", "PREDIABETES", "PREDIABETES", "DIABETES"]
