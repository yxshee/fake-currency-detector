"""Per-denomination constants ported from code/500_Testing.ipynb and code/2000_Testing.ipynb.

Every value below is copied from the notebooks unchanged. Cell numbers refer to the
notebook cell indices ("##### CELL [n]") of the respective notebook.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = REPO_ROOT / "datasets"
PLACEHOLDER_IMAGE = REPO_ROOT / "assets" / "Image_not_found.jpg"

# Rectangles are (x_start, x_end, y_start, y_end) for search areas, and
# (row_start, row_end, col_start, col_end) for fixed crops, matching the order in
# which the notebooks write the numbers.
Box = tuple[int, int, int, int]

# Names of the 10 features, in notebook order. Features 1-7 are named from the
# committed template images in datasets/Features/*/Feature N/ (the notebooks only
# number them); 8-10 are named in the notebooks' markdown cells.
FEATURE_NAMES: tuple[str, ...] = (
    "Denomination numeral in Devanagari",
    "Ashoka Pillar emblem",
    "RBI name in Hindi",
    "RBI name in English",
    "Denomination numeral with rupee symbol",
    "RBI seal",
    "Denomination in Hindi words",
    "Left bleed lines",
    "Right bleed lines",
    "Number panel",
)


@dataclass(frozen=True)
class DenominationConfig:
    denomination: int

    # Pre-processing (cell [7] in both notebooks): cv2.resize target (width, height),
    # then GaussianBlur with this kernel and sigma 0.
    resize_size: tuple[int, int]
    blur_kernel: tuple[int, int]

    # Algorithm 1, features 1-7.
    # ORB parameters (cell [9] in both notebooks).
    orb_nfeatures: int
    orb_scale_factor: float
    orb_nlevels: int
    orb_edge_threshold: int
    ransac_reproj_threshold: float
    # Search areas and area limits (500: cell [10]; 2000: cell [11]).
    search_areas: tuple[Box, ...]  # (x_start, x_end, y_start, y_end)
    area_limits: tuple[tuple[int, int], ...]  # (min_area, max_area)
    templates_per_feature: int  # NUMBER_OF_TEMPLATES (500: cell [11]; 2000: cell [12])
    template_dir: Path
    # Pass rule (500: cell [21]; 2000: cell [22]): avg SSIM >= min score, or max SSIM >= override.
    min_ssim_scores: tuple[float, ...]
    max_ssim_override: float

    # Algorithm 2, features 8 and 9 (500: cells [14], [16]; 2000: cells [15], [17]).
    left_bleed_crop: Box  # (row_start, row_end, col_start, col_end) on the resized BGR image
    right_bleed_crop: Box
    bleed_threshold: int  # cv2.threshold value, THRESH_BINARY to 255
    bleed_max_regions_per_column: int  # a column is valid if 0 < count < this
    # Accepted average line count, inclusive (500: cell [21]; 2000: cell [22]).
    bleed_line_range: tuple[float, float]

    # Algorithm 3, feature 10.
    # Crop on the blurred gray image (500: cell [18]; 2000: cell [19]).
    number_panel_crop: Box  # (row_start, row_end, col_start, col_end)
    # Threshold schedule: range(start, stop, step) (500: cell [19]; 2000: cell [20]).
    panel_threshold_start: int
    panel_threshold_stop: int
    panel_threshold_step: int
    panel_min_rect_area: int  # rectangles with w*h <= this are dropped
    panel_max_bottom_gap: int  # rectangles whose bottom edge is more than this above the crop bottom are dropped
    panel_min_rect_height: int  # rectangles with h < this are dropped
    panel_expected_characters: int  # a threshold "passes" when exactly this many rectangles remain
    panel_stop_after_passes: int  # the threshold loop stops after this many passing thresholds

    @property
    def panel_thresholds(self) -> range:
        return range(self.panel_threshold_start, self.panel_threshold_stop, self.panel_threshold_step)

    def template_path(self, feature: int, template: int) -> Path:
        """Path of template `template` (1-based) for feature `feature` (1-based)."""
        return self.template_dir / f"Feature {feature}" / f"{template}.jpg"


# Values shared by both notebooks (identical in both).
_SHARED = dict(
    blur_kernel=(5, 5),
    orb_nfeatures=700,
    orb_scale_factor=1.2,
    orb_nlevels=8,
    orb_edge_threshold=15,
    ransac_reproj_threshold=5.0,
    templates_per_feature=6,
    max_ssim_override=0.79,  # the notebook comment says 0.8; the code uses 0.79
    bleed_threshold=130,
    bleed_max_regions_per_column=10,
    panel_threshold_stop=155,
    panel_threshold_step=5,
    panel_min_rect_area=150,
    panel_max_bottom_gap=40,
    panel_min_rect_height=17,
    panel_expected_characters=9,
    panel_stop_after_passes=3,
)

CONFIG_500 = DenominationConfig(
    denomination=500,
    resize_size=(1167, 519),  # cell [7]
    # cell [10]
    search_areas=(
        (200, 300, 200, 370),
        (1050, 1500, 300, 450),
        (100, 450, 20, 120),
        (690, 1050, 20, 120),
        (820, 1050, 350, 430),
        (700, 810, 330, 430),
        (400, 650, 0, 100),
    ),
    # cell [10]
    area_limits=(
        (12000, 17000),
        (10000, 18000),
        (20000, 30000),
        (24000, 36000),
        (15000, 25000),
        (7000, 13000),
        (11000, 18000),
    ),
    template_dir=DATASETS_DIR / "Features" / "500_Features Dataset",
    min_ssim_scores=(0.4, 0.4, 0.5, 0.4, 0.5, 0.45, 0.5),  # cell [21]
    left_bleed_crop=(120, 240, 12, 35),  # cell [14]
    right_bleed_crop=(120, 260, 1135, 1155),  # cell [16]
    bleed_line_range=(4.7, 5.6),  # cell [21]
    number_panel_crop=(410, 500, 700, 1080),  # cell [18]
    panel_threshold_start=95,  # cell [19]
    **_SHARED,
)

CONFIG_2000 = DenominationConfig(
    denomination=2000,
    resize_size=(1165, 455),  # cell [7]
    # cell [11]
    search_areas=(
        (200, 270, 160, 330),
        (1050, 1500, 250, 400),
        (50, 400, 0, 100),
        (750, 1050, 0, 100),
        (850, 1050, 280, 380),
        (700, 820, 290, 370),
        (400, 650, 0, 100),
    ),
    # cell [11]
    area_limits=(
        (10000, 14000),
        (9000, 15000),
        (17000, 21500),
        (19000, 28000),
        (17500, 23000),
        (6500, 9000),
        (10000, 16000),
    ),
    template_dir=DATASETS_DIR / "Features" / "2000_Features Dataset",
    min_ssim_scores=(0.45, 0.4, 0.45, 0.45, 0.5, 0.4, 0.5),  # cell [22]
    left_bleed_crop=(80, 230, 10, 30),  # cell [15]
    right_bleed_crop=(90, 230, 1140, 1160),  # cell [17]
    bleed_line_range=(6.7, 7.6),  # cell [22]
    number_panel_crop=(360, 440, 760, 1080),  # cell [19]
    panel_threshold_start=90,  # cell [20]
    **_SHARED,
)

CONFIGS: dict[int, DenominationConfig] = {500: CONFIG_500, 2000: CONFIG_2000}


def get_config(denomination: int) -> DenominationConfig:
    try:
        return CONFIGS[int(denomination)]
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"unsupported denomination {denomination!r}; expected 500 or 2000") from None
