#!/usr/bin/env python3
"""
Run the full PPT generation pipeline in one command.

Sequence:
validate -> review -> generate_html -> render -> build -> manifest
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
VALIDATION_DIR = BASE_PATH / "output" / "validation"
VALIDATION_REPORT = VALIDATION_DIR / "presentation-content-report.json"
DECK_REPORT = VALIDATION_DIR / "deck-quality-report.json"


def run_step(label: str, args: list[str]) -> subprocess.CompletedProcess[str]:
    print(f"\n==> {label}", flush=True)
    result = subprocess.run(args, cwd=BASE_PATH)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    return result


def load_report_status(path: Path) -> str | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    status = report.get("status")
    return status if isinstance(status, str) else None


def stop_on_warn(mode: str, label: str, report_path: Path) -> None:
    status = load_report_status(report_path)
    if status == "warn" and mode == "stop-on-warn":
        print(f"\nStopping after {label}: warning status in {report_path}")
        raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full PPT generation pipeline.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--stop-on-warn", action="store_true", help="Stop the pipeline if validation or deck review returns warnings.")
    mode_group.add_argument("--allow-warn", action="store_true", help="Continue the pipeline even if validation or deck review returns warnings.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mode = "stop-on-warn" if args.stop_on_warn else "allow-warn"

    print(f"Pipeline mode: {mode}", flush=True)

    run_step("validate presentation content", [PYTHON, str(BASE_PATH / "scripts" / "validate_presentation_content.py")])
    stop_on_warn(mode, "validate presentation content", VALIDATION_REPORT)

    run_step("review deck quality", [PYTHON, str(BASE_PATH / "scripts" / "review_deck_quality.py")])
    stop_on_warn(mode, "review deck quality", DECK_REPORT)

    run_step("generate html", [PYTHON, str(BASE_PATH / "src" / "generate_html.py")])
    run_step("render images", [PYTHON, str(BASE_PATH / "src" / "render.py")])
    run_step("build pptx + manifest", [PYTHON, str(BASE_PATH / "src" / "build_pptx.py")])

    print("\nPipeline complete.")
    print(f"PPTX: {BASE_PATH / 'output' / 'presentation.pptx'}")
    print(f"Manifest: {BASE_PATH / 'output' / 'manifest.json'}")
    print(f"Mode: {mode}")


if __name__ == "__main__":
    main()
