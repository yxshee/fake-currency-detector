"""Streamlit front end: `streamlit run app.py`."""

from __future__ import annotations

import cv2
import numpy as np
import streamlit as st

from fcd.cli import sample_notes
from fcd.config import PLACEHOLDER_IMAGE, REPO_ROOT
from fcd.detector import VERDICT_GENUINE, analyze

st.set_page_config(page_title="Fake Currency Detector", layout="wide")
st.title("Fake Currency Detector")
st.caption("Checks 10 security features of an INR 500 or 2000 note. A note is called likely genuine when at least 9 pass.")

SAMPLES = {f"{p.relative_to(REPO_ROOT)} ({label})": (p, d) for p, d, label in sample_notes()}


TILE_SIZE = (300, 200)  # width, height of each feature-crop tile


@st.cache_data
def placeholder_rgb() -> np.ndarray:
    return cv2.cvtColor(cv2.imread(str(PLACEHOLDER_IMAGE)), cv2.COLOR_BGR2RGB)


def tile(crop: np.ndarray) -> np.ndarray:
    """Scale a crop to fit a white tile of TILE_SIZE, keeping its aspect ratio."""
    tile_w, tile_h = TILE_SIZE
    h, w = crop.shape[:2]
    scale = min(tile_w / w, tile_h / h)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    resized = cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    canvas = np.full((tile_h, tile_w, 3), 255, dtype=np.uint8)
    top, left = (tile_h - new_h) // 2, (tile_w - new_w) // 2
    canvas[top:top + new_h, left:left + new_w] = resized
    return canvas


source = st.radio("Image source", ["Committed sample", "Upload"], horizontal=True)
image = None
default_denom = 500
if source == "Committed sample":
    choice = st.selectbox("Sample note", list(SAMPLES))
    path, default_denom = SAMPLES[choice]
    image = cv2.imread(str(path))
else:
    upload = st.file_uploader("Note image", type=["jpg", "jpeg", "png"])
    if upload is not None:
        image = cv2.imdecode(np.frombuffer(upload.getvalue(), dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            st.error("Could not decode the uploaded file as an image.")

denomination = st.radio("Denomination", [500, 2000], index=0 if default_denom == 500 else 1, horizontal=True)

if image is not None:
    try:
        result = analyze(image, denomination)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    note_column, table_column = st.columns([2, 3])
    with note_column:
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Input note", width="stretch")
        if result.verdict == VERDICT_GENUINE:
            st.success(f"Verdict: {result.verdict}")
        else:
            st.error(f"Verdict: {result.verdict}")
        st.subheader(f"{result.features_passed} / 10 features passed")
    with table_column:
        st.table(
            [
                {"#": f.index, "Feature": f.name, "Measured value": f.value_text(), "Status": "PASS" if f.passed else "FAIL"}
                for f in result.features
            ]
        )

    st.subheader("Feature crops")
    cols = st.columns(5)
    for i, f in enumerate(result.features):
        with cols[i % 5]:
            crop = f.crop if f.crop is not None else placeholder_rgb()
            st.image(tile(crop), caption=f"{f.index}. {f.name}: {'PASS' if f.passed else 'FAIL'}", width="stretch")
