"""Command line: `python -m fcd detect IMAGE --denomination 500` and `python -m fcd evaluate`."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from .config import DATASETS_DIR, REPO_ROOT
from .detector import VERDICT_COUNTERFEIT, VERDICT_GENUINE, analyze

DENOMINATIONS = (500, 2000)


def _natural_key(p: Path):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.name)]


def sample_notes() -> list[tuple[Path, int, str]]:
    """Every committed note as (path, denomination, label) with label 'real' or 'fake'."""
    notes = []
    for d in DENOMINATIONS:
        for label, folder in (("real", DATASETS_DIR / f"{d}_dataset"), ("fake", DATASETS_DIR / "Fake Notes" / str(d))):
            for p in sorted(folder.glob("*.jpg"), key=_natural_key):
                notes.append((p, d, label))
    return notes


def _print_note(result, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return
    for f in result.features:
        status = "PASS" if f.passed else "FAIL"
        print(f"{f.index:>2}. {f.name:<40} {status}  {f.value_text()}")
    print(f"{result.features_passed} / 10 features passed")
    print(f"Verdict: {result.verdict}")


def cmd_detect(args) -> int:
    try:
        result = analyze(args.image, args.denomination)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    _print_note(result, args.json)
    return 0


def _pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:.1f}%" if d else "n/a"


def summarize(rows: list[dict]) -> list[dict]:
    out = []
    for scope in [*(str(d) for d in DENOMINATIONS), "overall"]:
        sel = rows if scope == "overall" else [r for r in rows if str(r["denomination"]) == scope]
        real = [r for r in sel if r["label"] == "real"]
        fake = [r for r in sel if r["label"] == "fake"]
        real_ok = sum(r["verdict"] == VERDICT_GENUINE for r in real)
        fake_ok = sum(r["verdict"] == VERDICT_COUNTERFEIT for r in fake)
        out.append(
            {
                "scope": scope,
                "real_total": len(real),
                "real_classified_genuine": real_ok,
                "fake_total": len(fake),
                "fake_classified_counterfeit": fake_ok,
                "correct": real_ok + fake_ok,
                "total": len(sel),
            }
        )
    return out


def render_markdown(rows: list[dict], summary: list[dict], mean_seconds: float) -> str:
    lines = ["# Evaluation on the committed sample notes", ""]
    lines.append("Rule: a note is classified genuine when at least 9 of 10 features pass (report's rule).")
    lines.append("")
    lines.append("| Note | Denomination | Label | Features passed | Failed features | Verdict | Correct | Seconds |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        failed = ", ".join(str(i) for i in r["failed_features"]) or "-"
        lines.append(
            f"| {r['note']} | {r['denomination']} | {r['label']} | {r['features_passed']} / 10 | {failed} "
            f"| {r['verdict']} | {'yes' if r['correct'] else 'no'} | {r['seconds']:.2f} |"
        )
    lines += ["", "## Summary", ""]
    lines.append("| Scope | Real classified genuine | Fake classified counterfeit | All correct |")
    lines.append("|---|---|---|---|")
    for s in summary:
        lines.append(
            f"| {s['scope']} | {s['real_classified_genuine']} / {s['real_total']} "
            f"({_pct(s['real_classified_genuine'], s['real_total'])}) "
            f"| {s['fake_classified_counterfeit']} / {s['fake_total']} "
            f"({_pct(s['fake_classified_counterfeit'], s['fake_total'])}) "
            f"| {s['correct']} / {s['total']} ({_pct(s['correct'], s['total'])}) |"
        )
    lines += ["", f"Mean seconds per note: {mean_seconds:.2f}", ""]
    lines.append("Original report: 15 / 19 real notes and 10 / 12 fake notes classified correctly.")
    lines.append("")
    return "\n".join(lines)


def cmd_evaluate(args) -> int:
    rows = []
    for path, denom, label in sample_notes():
        t0 = time.perf_counter()
        result = analyze(path, denom)
        secs = time.perf_counter() - t0
        expected = VERDICT_GENUINE if label == "real" else VERDICT_COUNTERFEIT
        rows.append(
            {
                "note": str(path.relative_to(REPO_ROOT)),
                "denomination": denom,
                "label": label,
                "features_passed": result.features_passed,
                "failed_features": [f.index for f in result.features if not f.passed],
                "verdict": result.verdict,
                "correct": result.verdict == expected,
                "seconds": secs,
                "features": [f.to_dict() for f in result.features],
            }
        )
    summary = summarize(rows)
    mean_seconds = sum(r["seconds"] for r in rows) / len(rows) if rows else 0.0
    md = render_markdown(rows, summary, mean_seconds)
    print(md)
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(
            json.dumps({"notes": rows, "summary": summary, "mean_seconds_per_note": mean_seconds}, indent=2) + "\n"
        )
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(md)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m fcd", description="Fake currency detector for INR 500 and 2000 notes")
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("detect", help="analyse one note image")
    d.add_argument("image")
    d.add_argument("--denomination", type=int, choices=DENOMINATIONS, required=True)
    d.add_argument("--json", action="store_true", help="print the result as JSON")
    d.set_defaults(func=cmd_detect)
    e = sub.add_parser("evaluate", help="run every committed real and fake note")
    e.add_argument("--json", metavar="PATH", help="write per-note results and summary as JSON")
    e.add_argument("--markdown", metavar="PATH", help="write the tables as Markdown")
    e.set_defaults(func=cmd_evaluate)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
