import numpy as np
import pytest

from fcd.config import CONFIG_500
from fcd.detector import (
    GENUINE_MIN_FEATURES,
    VERDICT_COUNTERFEIT,
    VERDICT_GENUINE,
    analyze,
    calculate_ssim,
    count_bleed_lines,
    crop_box,
    filter_panel_rects,
    load_image,
    mask_outside,
    select_box,
    verdict_for,
)


def test_count_bleed_lines_counts_white_to_black_transitions():
    col = np.array([255, 0, 0, 255, 0, 255, 255, 0], dtype=np.uint8)  # 3 white->black transitions
    thresh = np.stack([col] * 4, axis=1)
    assert count_bleed_lines(thresh, 10) == 3.0


def test_count_bleed_lines_drops_noisy_and_empty_columns():
    good = np.array([255, 0] * 3, dtype=np.uint8)  # 3 transitions
    empty = np.full(6, 255, dtype=np.uint8)  # 0 transitions -> discarded
    thresh = np.stack([good, empty], axis=1)
    assert count_bleed_lines(thresh, 10) == 3.0
    noisy = np.array([255, 0] * 10, dtype=np.uint8)  # 10 transitions -> discarded (count < 10 required)
    assert count_bleed_lines(noisy[:, None], 10) == -1.0


def test_count_bleed_lines_treats_grey_as_white():
    col = np.array([128, 0, 128, 0], dtype=np.uint8)
    assert count_bleed_lines(col[:, None], 10) == 2.0


def test_mask_outside_keeps_only_search_area():
    gray = np.full((10, 10), 7, dtype=np.uint8)
    out = mask_outside(gray, (2, 5, 3, 6))
    assert out[3:6, 2:5].min() == 7
    assert out.sum() == 7 * 9
    assert gray.min() == 7  # input untouched


def test_crop_box_clips_and_rejects_outside_boxes():
    img = np.zeros((20, 30, 3), dtype=np.uint8)
    assert crop_box(img, (5, 5, 10, 10)).shape == (10, 10, 3)
    assert crop_box(img, (-5, -5, 10, 10)).shape == (5, 5, 3)
    assert crop_box(img, (25, 15, 10, 10)).shape == (5, 5, 3)
    assert crop_box(img, (40, 0, 10, 10)) is None
    assert crop_box(img, (0, -30, 10, 10)) is None


def test_select_box_falls_back_to_keypoints_then_discards():
    big = np.float32([[0, 0], [0, 99], [99, 99], [99, 0]]).reshape(-1, 1, 2)  # 100x100 -> area 10000
    small = np.float32([[0, 0], [0, 9], [9, 9], [9, 0]]).reshape(-1, 1, 2)  # area 100
    assert select_box(big, small, (5000, 20000)) == (0, 0, 100, 100)
    assert select_box(small, big, (5000, 20000)) == (0, 0, 100, 100)
    assert select_box(small, small, (5000, 20000)) is None


def test_calculate_ssim_identical_images_is_one():
    rng = np.random.default_rng(0)
    img = rng.integers(0, 255, (40, 60, 3), dtype=np.uint8)
    assert calculate_ssim(img, img) == pytest.approx(1.0)


def test_filter_panel_rects():
    h_img = 90
    rects = sorted(
        [
            [10, 60, 10, 25],  # kept
            [12, 62, 6, 30],  # ends at x=18, inside the previous one (ends at x=20) -> dropped
            [30, 10, 10, 20],  # bottom edge 60 px above crop bottom -> dropped
            [50, 70, 20, 10],  # height < 17 -> dropped
            [80, 60, 4, 30],  # area 120 <= 150 -> dropped
            [100, 55, 12, 30],  # kept
        ]
    )
    assert filter_panel_rects(rects, h_img, CONFIG_500) == [[10, 60, 10, 25], [100, 55, 12, 30]]


def test_verdict_threshold():
    assert GENUINE_MIN_FEATURES == 9
    assert verdict_for(9) == VERDICT_GENUINE
    assert verdict_for(10) == VERDICT_GENUINE
    assert verdict_for(8) == VERDICT_COUNTERFEIT


def test_unreadable_image_raises_value_error(tmp_path):
    bad = tmp_path / "not_an_image.jpg"
    bad.write_bytes(b"this is not a jpeg")
    with pytest.raises(ValueError, match="could not read image"):
        analyze(bad, 500)
    with pytest.raises(ValueError, match="could not read image"):
        analyze(tmp_path / "missing.jpg", 2000)


def test_bad_array_and_denomination_raise_value_error():
    with pytest.raises(ValueError):
        load_image(np.zeros((10, 10), dtype=np.uint8))
    with pytest.raises(ValueError):
        analyze(np.zeros((10, 10, 3), dtype=np.uint8), 100)
