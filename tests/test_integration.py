import cv2
import numpy as np
import pytest

from fcd.config import DATASETS_DIR
from fcd.detector import VERDICT_COUNTERFEIT, VERDICT_GENUINE, analyze

NOTES = [
    (DATASETS_DIR / "500_dataset" / "500_s1.jpg", 500),
    (DATASETS_DIR / "Fake Notes" / "500" / "500_f1.jpg", 500),
    (DATASETS_DIR / "2000_dataset" / "2000_s1.jpg", 2000),
    (DATASETS_DIR / "Fake Notes" / "2000" / "2000_f1.jpg", 2000),
]


@pytest.mark.parametrize("path,denomination", NOTES, ids=[p.name for p, _ in NOTES])
def test_analyze_structure(path, denomination):
    r = analyze(path, denomination)
    assert r.denomination == denomination
    assert len(r.features) == 10
    assert [f.index for f in r.features] == list(range(1, 11))
    assert [f.kind for f in r.features] == ["ssim"] * 7 + ["bleed_lines"] * 2 + ["number_panel"]
    assert 0 <= r.features_passed <= 10
    assert r.features_passed == sum(f.passed for f in r.features)
    assert r.verdict in (VERDICT_GENUINE, VERDICT_COUNTERFEIT)
    for f in r.features[:7]:
        assert -1.0 <= f.max_ssim <= 1.0
        assert -1.0 <= f.avg_ssim <= 1.0
        assert 0 <= f.templates_used <= 6
    for f in r.features:
        if f.crop is not None:
            assert f.crop.ndim == 3 and f.crop.shape[2] == 3 and f.crop.dtype == np.uint8
    assert isinstance(r.to_dict()["features"][0]["value"], str)


def test_array_input_matches_path_input():
    path, denom = NOTES[0]
    a = analyze(path, denom)
    b = analyze(cv2.imread(str(path)), denom)
    assert a.to_dict() == b.to_dict()


@pytest.mark.parametrize("path,denomination", [NOTES[1], NOTES[2]], ids=["500_f1", "2000_s1"])
def test_two_runs_are_identical(path, denomination):
    a = analyze(path, denomination)
    b = analyze(path, denomination)
    assert a.to_dict() == b.to_dict()
    for fa, fb in zip(a.features, b.features):
        if fa.crop is None:
            assert fb.crop is None
        else:
            assert np.array_equal(fa.crop, fb.crop)
