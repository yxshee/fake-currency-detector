"""The committed evaluation must be what the code produces on the platform CI runs on."""
import json
import platform

import pytest

from fcd.cli import sample_notes
from fcd.config import REPO_ROOT
from fcd.detector import analyze

COMMITTED = REPO_ROOT / "results" / "evaluation.json"

# OpenCV's floating-point results differ slightly between CPU architectures, and
# a few notes sit close to a threshold, so the verdict for those notes depends
# on the machine. results/evaluation.json holds the Linux x86-64 results, which
# is the platform of the CI job, and this test pins the README's table to them.
pytestmark = pytest.mark.skipif(
    platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"),
    reason="results/evaluation.json was generated on Linux x86-64",
)


def test_every_note_matches_the_committed_evaluation():
    committed = {row["note"]: row for row in json.loads(COMMITTED.read_text())["notes"]}
    assert len(committed) == 31

    mismatches = []
    for path, denomination, _label in sample_notes():
        note = path.relative_to(REPO_ROOT).as_posix()
        result = analyze(path, denomination)
        expected = committed[note]
        got = (result.features_passed, result.verdict)
        want = (expected["features_passed"], expected["verdict"])
        if got != want:
            mismatches.append(f"{note}: committed {want}, computed {got}")
    assert not mismatches, "\n".join(mismatches)


def test_committed_summary_matches_its_own_rows():
    data = json.loads(COMMITTED.read_text())
    overall = next(row for row in data["summary"] if row["scope"] == "overall")
    real = [row for row in data["notes"] if row["label"] == "real"]
    fake = [row for row in data["notes"] if row["label"] == "fake"]
    assert overall["real_total"] == len(real) == 19
    assert overall["fake_total"] == len(fake) == 12
    assert overall["real_classified_genuine"] == sum(row["correct"] for row in real)
    assert overall["fake_classified_counterfeit"] == sum(row["correct"] for row in fake)
