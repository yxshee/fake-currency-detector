import pytest

from fcd.config import CONFIG_500, CONFIG_2000, CONFIGS, FEATURE_NAMES, PLACEHOLDER_IMAGE, get_config


@pytest.mark.parametrize("cfg", [CONFIG_500, CONFIG_2000], ids=["500", "2000"])
def test_seven_template_features(cfg):
    assert len(cfg.search_areas) == 7
    assert len(cfg.area_limits) == 7
    assert len(cfg.min_ssim_scores) == 7
    for x0, x1, y0, y1 in cfg.search_areas:
        assert x0 < x1 and y0 < y1
    for lo, hi in cfg.area_limits:
        assert 0 < lo < hi


@pytest.mark.parametrize("cfg", [CONFIG_500, CONFIG_2000], ids=["500", "2000"])
def test_42_template_files_exist(cfg):
    paths = [cfg.template_path(f, t) for f in range(1, 8) for t in range(1, cfg.templates_per_feature + 1)]
    assert len(paths) == 42
    missing = [p for p in paths if not p.is_file()]
    assert missing == []


@pytest.mark.parametrize("cfg", [CONFIG_500, CONFIG_2000], ids=["500", "2000"])
def test_crops_fit_inside_resized_image(cfg):
    w, h = cfg.resize_size
    for r0, r1, c0, c1 in (cfg.left_bleed_crop, cfg.right_bleed_crop, cfg.number_panel_crop):
        assert 0 <= r0 < r1 <= h
        assert 0 <= c0 < c1 <= w


def test_per_denomination_values_from_notebooks():
    assert CONFIG_500.resize_size == (1167, 519)
    assert CONFIG_2000.resize_size == (1165, 455)
    assert CONFIG_500.bleed_line_range == (4.7, 5.6)
    assert CONFIG_2000.bleed_line_range == (6.7, 7.6)
    assert list(CONFIG_500.panel_thresholds) == list(range(95, 155, 5))
    assert list(CONFIG_2000.panel_thresholds) == list(range(90, 155, 5))
    assert CONFIG_500.min_ssim_scores == (0.4, 0.4, 0.5, 0.4, 0.5, 0.45, 0.5)
    assert CONFIG_2000.min_ssim_scores == (0.45, 0.4, 0.45, 0.45, 0.5, 0.4, 0.5)
    assert CONFIG_500.max_ssim_override == CONFIG_2000.max_ssim_override == 0.79


def test_misc():
    assert len(FEATURE_NAMES) == 10
    assert set(CONFIGS) == {500, 2000}
    assert PLACEHOLDER_IMAGE.is_file()
    assert get_config("2000") is CONFIG_2000
    with pytest.raises(ValueError):
        get_config(100)
