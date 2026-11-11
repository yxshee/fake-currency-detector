"""Counterfeit checks for INR 500 and 2000 notes, ported from code/{500,2000}_Testing.ipynb.

Pure functions: no GUI, no plotting, no module-level mutable state, no printing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from os import PathLike
from typing import Optional, Union

import cv2
import numpy as np
from skimage.metrics import structural_similarity

from .config import FEATURE_NAMES, DenominationConfig, get_config

# The report's evaluation rule: "if the currency note passed at least 9 features
# out of 10 then the note is real otherwise it is fake" (report, section on results).
GENUINE_MIN_FEATURES = 9
VERDICT_GENUINE = "likely genuine"
VERDICT_COUNTERFEIT = "likely counterfeit"

ImageInput = Union[str, PathLike, np.ndarray]


@dataclass
class FeatureResult:
    index: int  # 1-based feature number
    name: str
    kind: str  # "ssim" (features 1-7), "bleed_lines" (8-9) or "number_panel" (10)
    passed: bool
    avg_ssim: Optional[float] = None
    max_ssim: Optional[float] = None
    templates_used: Optional[int] = None  # templates that were not discarded
    line_count: Optional[float] = None  # -1 when no valid column was found (as in the notebook)
    characters_found: Optional[bool] = None
    crop: Optional[np.ndarray] = field(default=None, repr=False)  # RGB, or None

    def value_text(self) -> str:
        """The measured value(s), formatted the way gui_2.ipynb showed them."""
        if self.kind == "ssim":
            return f"avg SSIM {self.avg_ssim:.3f}, max SSIM {self.max_ssim:.3f}"
        if self.kind == "bleed_lines":
            return f"avg lines {self.line_count:.3f}"
        return "9 characters detected" if self.characters_found else "fewer than 9 characters detected"

    def to_dict(self) -> dict:
        d = {
            "index": self.index,
            "name": self.name,
            "kind": self.kind,
            "passed": self.passed,
            "value": self.value_text(),
        }
        if self.kind == "ssim":
            d.update(avg_ssim=self.avg_ssim, max_ssim=self.max_ssim, templates_used=self.templates_used)
        elif self.kind == "bleed_lines":
            d.update(line_count=self.line_count)
        else:
            d.update(characters_found=self.characters_found)
        return d


@dataclass
class NoteResult:
    denomination: int
    features: list[FeatureResult]
    features_passed: int
    verdict: str

    def to_dict(self) -> dict:
        return {
            "denomination": self.denomination,
            "features_passed": self.features_passed,
            "verdict": self.verdict,
            "features": [f.to_dict() for f in self.features],
        }


# --------------------------------------------------------------------------- helpers


def load_image(image: ImageInput) -> np.ndarray:
    """Return a BGR uint8 image from a path or an array; raise ValueError if unusable."""
    if isinstance(image, np.ndarray):
        img = image
    else:
        img = cv2.imread(str(image), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"could not read image file {str(image)!r} (missing, unreadable or not an image)")
    if img.ndim != 3 or img.shape[2] != 3 or img.size == 0:
        raise ValueError(f"expected a non-empty BGR image of shape (H, W, 3), got shape {img.shape}")
    if img.dtype != np.uint8:
        raise ValueError(f"expected a uint8 image, got dtype {img.dtype}")
    return img


def preprocess(img: np.ndarray, cfg: DenominationConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Cell [7]: resize, Gaussian blur, grayscale. Returns (resized, blurred, gray)."""
    test_img = cv2.resize(img, cfg.resize_size)
    blur = cv2.GaussianBlur(test_img, cfg.blur_kernel, 0)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    return test_img, blur, gray


def mask_outside(gray: np.ndarray, area: tuple[int, int, int, int]) -> np.ndarray:
    """Zero everything outside the search area (x_start, x_end, y_start, y_end), as in Algorithm 1."""
    x0, x1, y0, y1 = area
    out = gray.copy()
    out[:, :x0] = 0
    out[:, x1:] = 0
    out[:y0, :] = 0
    out[y1:, :] = 0
    return out


def calculate_ssim(template_bgr: np.ndarray, query_bgr: np.ndarray) -> float:
    """Cell [8]: resize both to the smaller width/height, convert to gray, SSIM."""
    min_w = min(template_bgr.shape[1], query_bgr.shape[1])
    min_h = min(template_bgr.shape[0], query_bgr.shape[0])
    img1 = cv2.cvtColor(cv2.resize(template_bgr, (min_w, min_h)), cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(cv2.resize(query_bgr, (min_w, min_h)), cv2.COLOR_BGR2GRAY)
    return float(structural_similarity(img1, img2))


def locate_template(template_gray: np.ndarray, query_gray: np.ndarray, cfg: DenominationConfig):
    """Cell [9] computeORB: ORB + brute-force Hamming matching + RANSAC homography.

    Returns (dst, dst_pts) like the notebook, or None when there is no usable match:
    no descriptors on either side, fewer than 4 matches, or no homography.
    """
    orb = cv2.ORB_create(
        nfeatures=cfg.orb_nfeatures,
        scaleFactor=cfg.orb_scale_factor,
        nlevels=cfg.orb_nlevels,
        edgeThreshold=cfg.orb_edge_threshold,
    )
    kpts1, descs1 = orb.detectAndCompute(template_gray, None)
    kpts2, descs2 = orb.detectAndCompute(query_gray, None)
    if descs1 is None or descs2 is None:
        return None
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    dmatches = sorted(bf.match(descs1, descs2), key=lambda m: m.distance)
    if len(dmatches) < 4:  # findHomography needs at least 4 point pairs
        return None
    src_pts = np.float32([kpts1[m.queryIdx].pt for m in dmatches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kpts2[m.trainIdx].pt for m in dmatches]).reshape(-1, 1, 2)
    M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, cfg.ransac_reproj_threshold)
    if M is None:
        return None
    h, w = template_gray.shape[:2]
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)
    return dst, dst_pts


def select_box(dst: np.ndarray, dst_pts: np.ndarray, limits: tuple[int, int]):
    """Algorithm 1 area check: bounding box of the projected template, falling back to the
    bounding box of all matched keypoints; None (template discarded) if both are out of range."""
    min_area, max_area = limits
    x, y, w, h = cv2.boundingRect(dst)
    if w * h < min_area or w * h > max_area:
        x, y, w, h = cv2.boundingRect(dst_pts)
        if w * h < min_area or w * h > max_area:
            return None
    return x, y, w, h


def crop_box(img: np.ndarray, box: tuple[int, int, int, int]) -> Optional[np.ndarray]:
    """Crop (x, y, w, h) clipped to the image; None if nothing is left.

    The notebook sliced img[y:y+h, x:x+w] directly, where a negative x or y wraps
    around (Python indexing) and gives an empty or wrong crop.
    """
    x, y, w, h = box
    H, W = img.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return None
    return img[y0:y1, x0:x1]


def count_bleed_lines(thresh: np.ndarray, max_regions: int) -> float:
    """Algorithm 2: per column, count white->black transitions going down; keep columns with
    0 < count < max_regions; return their average, or -1 if none are valid (as the notebook)."""
    binary = np.where(thresh != 0, 255, 0)  # notebook: any non-0/255 pixel is treated as white
    counts = np.sum((binary[:-1, :] == 255) & (binary[1:, :] == 0), axis=0)
    valid = counts[(counts > 0) & (counts < max_regions)]
    if valid.size == 0:
        return -1.0
    return float(valid.sum() / valid.size)


def filter_panel_rects(rects: list[list[int]], crop_height: int, cfg: DenominationConfig) -> list[list[int]]:
    """Algorithm 3 rectangle elimination, ported loop for loop from 2000_Testing cell [20].

    `rects` are [x, y, w, h] with x != 0, already sorted.
    """
    res_list = [r for r in rects if r[2] * r[3] > cfg.panel_min_rect_area]

    # Eliminate rectangles that end at or before the right edge of an earlier one.
    i = 0
    while i < len(res_list):
        x, y, w, h = res_list[i]
        j = i + 1
        while j < len(res_list):
            x0, y0, w0, h0 = res_list[j]
            if (x + w) >= x0 + w0:
                res_list.pop(j)
            else:
                break
        i += 1

    # Eliminate rectangles far from the bottom edge or too short.
    i = 0
    while i < len(res_list):
        x, y, w, h = res_list[i]
        if (crop_height - (y + h)) > cfg.panel_max_bottom_gap:
            res_list.pop(i)
        elif h < cfg.panel_min_rect_height:
            res_list.pop(i)
        else:
            i += 1
    return res_list


def _bgr_to_rgb(img: Optional[np.ndarray]) -> Optional[np.ndarray]:
    if img is None:
        return None
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# --------------------------------------------------------------------------- algorithms


def load_templates(cfg: DenominationConfig) -> list[list[np.ndarray]]:
    """Read the 6 BGR templates of each of the 7 features; raise if any is missing."""
    out = []
    for f in range(1, len(cfg.search_areas) + 1):
        row = []
        for t in range(1, cfg.templates_per_feature + 1):
            p = cfg.template_path(f, t)
            img = cv2.imread(str(p), cv2.IMREAD_COLOR)
            if img is None:
                raise FileNotFoundError(f"template image missing or unreadable: {p}")
            row.append(img)
        out.append(row)
    return out


def check_template_features(blur: np.ndarray, gray: np.ndarray, cfg: DenominationConfig) -> list[FeatureResult]:
    """Algorithm 1 (features 1-7), the guarded version from 2000_Testing cell [12]."""
    templates = load_templates(cfg)
    results = []
    for j, area in enumerate(cfg.search_areas):
        masked = mask_outside(gray, area)
        score_set: list[float] = []
        max_score = -1.0
        max_score_img = None
        for template_img in templates[j]:
            template_blur = cv2.GaussianBlur(template_img, cfg.blur_kernel, 0)
            template_gray = cv2.cvtColor(template_blur, cv2.COLOR_BGR2GRAY)
            located = locate_template(template_gray, masked, cfg)
            if located is None:
                continue  # discarded: no usable match
            box = select_box(*located, cfg.area_limits[j])
            if box is None:
                continue  # discarded: area outside permitted range
            crop = crop_box(blur, box)
            if crop is None:
                continue  # discarded: box lies outside the image
            try:
                score = calculate_ssim(template_blur, crop)
            except ValueError:
                continue  # discarded: crop smaller than the 7x7 SSIM window
            score_set.append(score)
            if score > max_score:
                max_score = score
                max_score_img = crop
        avg = sum(score_set) / len(score_set) if score_set else 0.0
        passed = avg >= cfg.min_ssim_scores[j] or max_score >= cfg.max_ssim_override
        results.append(
            FeatureResult(
                index=j + 1,
                name=FEATURE_NAMES[j],
                kind="ssim",
                passed=bool(passed),
                avg_ssim=float(avg),
                max_ssim=float(max_score),
                templates_used=len(score_set),
                crop=_bgr_to_rgb(max_score_img),
            )
        )
    return results


def check_bleed_lines(test_img: np.ndarray, cfg: DenominationConfig, index: int) -> FeatureResult:
    """Algorithm 2 (feature 8 = left, feature 9 = right)."""
    r0, r1, c0, c1 = cfg.left_bleed_crop if index == 8 else cfg.right_bleed_crop
    gray = cv2.cvtColor(test_img[r0:r1, c0:c1], cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, cfg.bleed_threshold, 255, cv2.THRESH_BINARY)
    count = count_bleed_lines(thresh, cfg.bleed_max_regions_per_column)
    lo, hi = cfg.bleed_line_range
    return FeatureResult(
        index=index,
        name=FEATURE_NAMES[index - 1],
        kind="bleed_lines",
        passed=bool(lo <= count <= hi),
        line_count=count,
        crop=_bgr_to_rgb(thresh),
    )


def check_number_panel(test_img: np.ndarray, gray: np.ndarray, cfg: DenominationConfig) -> FeatureResult:
    """Algorithm 3 (feature 10), 2000_Testing cells [19]-[20] structure."""
    r0, r1, c0, c1 = cfg.number_panel_crop
    crop = gray[r0:r1, c0:c1]
    crop_bgr = test_img[r0:r1, c0:c1]
    h_img = crop.shape[0]

    res_img_list = []
    count = 0
    for thresh_value in cfg.panel_thresholds:
        _, thresh = cv2.threshold(crop, thresh_value, 255, cv2.THRESH_BINARY)
        copy = crop_bgr.copy()
        img = cv2.bitwise_and(crop, crop, mask=thresh)
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        rects = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if x != 0:
                rects.append([x, y, w, h])
        rects.sort()
        res_list = filter_panel_rects(rects, h_img, cfg)
        for x, y, w, h in res_list:
            cv2.rectangle(copy, (x, y), (x + w, y + h), (0, 0, 255), 1)
        if len(res_list) == cfg.panel_expected_characters:
            res_img_list.append(copy)
            count += 1
        if count == cfg.panel_stop_after_passes:
            break

    # Best image: the last passing case, up to the third (notebook's count 0/1/2/>=3 branches).
    best_img = res_img_list[min(count, cfg.panel_stop_after_passes) - 1] if count else crop_bgr
    return FeatureResult(
        index=10,
        name=FEATURE_NAMES[9],
        kind="number_panel",
        passed=count > 0,
        characters_found=count > 0,
        crop=_bgr_to_rgb(best_img),
    )


def verdict_for(features_passed: int) -> str:
    return VERDICT_GENUINE if features_passed >= GENUINE_MIN_FEATURES else VERDICT_COUNTERFEIT


def analyze(image: ImageInput, denomination: int) -> NoteResult:
    """Run all 10 checks on a note image (path or BGR array) of the given denomination."""
    cv2.setRNGSeed(0)  # RANSAC reproducibility
    cfg = get_config(denomination)
    img = load_image(image)
    test_img, blur, gray = preprocess(img, cfg)
    features = check_template_features(blur, gray, cfg)
    features.append(check_bleed_lines(test_img, cfg, 8))
    features.append(check_bleed_lines(test_img, cfg, 9))
    features.append(check_number_panel(test_img, gray, cfg))
    passed = sum(f.passed for f in features)
    return NoteResult(denomination=cfg.denomination, features=features, features_passed=passed, verdict=verdict_for(passed))
