#!/usr/bin/env python3
"""
Review deck-level repetition and layout balance for deck-spec.json.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

BASE_PATH = Path(__file__).resolve().parent.parent
SPEC_CANDIDATES = [
    BASE_PATH / "deck-spec.json",
    BASE_PATH / "presentation-content.json",
    BASE_PATH / "content" / "deck-spec.json",
    BASE_PATH / "content" / "presentation-content.json",
]
VALIDATION_DIR = BASE_PATH / "output" / "validation"
REPORT_PATH = VALIDATION_DIR / "deck-quality-report.json"


def find_spec_path() -> Path | None:
    for candidate in SPEC_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def record_warning(warnings: list[str], message: str) -> None:
    warnings.append(message)


def build_signature(slide: dict[str, Any]) -> str:
    layout_id = str(slide.get("layout_id", "unknown"))
    data = slide.get("data", {})
    if not isinstance(data, dict):
        return f"{layout_id}|bad-data"

    parts: list[str] = []
    for key in ["items", "cards", "leftCards", "rightCards", "topCard", "topCards", "bottomCards", "headers", "rows", "nodes", "bullets", "steps"]:
        value = data.get(key)
        if isinstance(value, list):
            parts.append(f"{key}:{len(value)}")
        elif isinstance(value, dict):
            for nested_key in ("points", "bullets", "items"):
                nested_value = value.get(nested_key)
                if isinstance(nested_value, list):
                    parts.append(f"{key}.{nested_key}:{len(nested_value)}")

    if not parts:
        parts.append("no-list-fields")

    return f"{layout_id}|{'|'.join(parts)}"


def detect_runs(values: list[str]) -> list[dict[str, Any]]:
    if not values:
        return []

    runs: list[dict[str, Any]] = []
    start = 1
    current = values[0]

    for index, value in enumerate(values[1:], start=2):
        if value == current:
            continue

        runs.append({
            "value": current,
            "start": start,
            "end": index - 1,
            "length": index - start,
        })
        current = value
        start = index

    runs.append({
        "value": current,
        "start": start,
        "end": len(values),
        "length": len(values) - start + 1,
    })
    return runs


def main() -> None:
    content_path = find_spec_path()
    if content_path is None:
        print("No deck-spec.json found.")
        sys.exit(1)

    try:
        content = load_json(content_path)
    except Exception as exc:
        print(f"Failed to parse {content_path}: {exc}")
        sys.exit(1)

    if not isinstance(content, dict):
        print("Top-level content must be an object.")
        sys.exit(1)

    slides = content.get("slides", [])
    if not isinstance(slides, list) or not slides:
        print("Top-level `slides` must be a non-empty list.")
        sys.exit(1)

    warnings: list[str] = []
    layout_ids: list[str] = []
    signatures: list[str] = []

    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            record_warning(warnings, f"Slide {index}: slide entry is not an object.")
            continue
        layout_id = str(slide.get("layout_id", "unknown"))
        layout_ids.append(layout_id)
        signatures.append(build_signature(slide))

    layout_counts = Counter(layout_ids)
    signature_counts = Counter(signatures)
    layout_runs = detect_runs(layout_ids)
    signature_runs = detect_runs(signatures)

    slide_count = len(slides)
    dominant_layout = layout_counts.most_common(1)[0] if layout_counts else None
    if dominant_layout:
        layout_id, count = dominant_layout
        ratio = count / slide_count
        if ratio >= 0.6:
            record_warning(warnings, f"Layout `{layout_id}` covers {count}/{slide_count} slides ({ratio:.0%}).")

    content_col_count = layout_counts.get("content-col", 0)
    if content_col_count / slide_count >= 0.5:
        record_warning(warnings, f"`content-col` appears on {content_col_count}/{slide_count} slides ({content_col_count / slide_count:.0%}).")

    long_layout_runs = [run for run in layout_runs if run["length"] >= 3]
    for run in long_layout_runs:
        record_warning(
            warnings,
            f"Layout `{run['value']}` repeats for {run['length']} consecutive slides ({run['start']}-{run['end']}).",
        )

    repeated_signatures = [
        (signature, count)
        for signature, count in signature_counts.items()
        if count >= 3
    ]
    for signature, count in sorted(repeated_signatures, key=lambda item: (-item[1], item[0])):
        record_warning(warnings, f"Structure `{signature}` appears {count} times across the deck.")

    long_signature_runs = [run for run in signature_runs if run["length"] >= 2]
    for run in long_signature_runs:
        record_warning(
            warnings,
            f"Structure `{run['value']}` repeats for {run['length']} consecutive slides ({run['start']}-{run['end']}).",
        )

    report = {
        "status": "warn" if warnings else "pass",
        "content_path": str(content_path),
        "summary": {
            "slide_count": slide_count,
            "layout_counts": dict(layout_counts),
            "signature_counts": dict(signature_counts),
            "layout_runs": layout_runs,
            "signature_runs": signature_runs,
        },
        "warnings": warnings,
    }

    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if warnings:
        print(f"[WARN] Deck quality review found repetition risks. Report: {REPORT_PATH}")
        for warning in warnings:
            print(f"  - {warning}")
        return

    print(f"[OK] Deck quality review passed. Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
