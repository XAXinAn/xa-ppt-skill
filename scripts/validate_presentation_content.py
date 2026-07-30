#!/usr/bin/env python3
"""
Validate deck-spec.json against the design system and slide-level rules.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

BASE_PATH = Path(__file__).resolve().parent.parent
DESIGN_SYSTEM_PATH = BASE_PATH / "design-system" / "design-system.json"
SPEC_CANDIDATES = [
    BASE_PATH / "deck-spec.json",
    BASE_PATH / "presentation-content.json",
    BASE_PATH / "content" / "deck-spec.json",
    BASE_PATH / "content" / "presentation-content.json",
]
VALIDATION_DIR = BASE_PATH / "output" / "validation"
REPORT_PATH = VALIDATION_DIR / "presentation-content-report.json"


def find_spec_path() -> Path | None:
    for candidate in SPEC_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def as_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def list_length(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def record_error(errors: list[str], message: str) -> None:
    errors.append(message)


def record_warning(warnings: list[str], message: str) -> None:
    warnings.append(message)


def validate_card_list(
    errors: list[str],
    slide_index: int,
    field_name: str,
    value: Any,
    *,
    expected: int | None = None,
    minimum: int | None = None,
    maximum: int | None = None,
    allow_strings: bool = False,
    require_title: bool = False,
) -> int:
    if not isinstance(value, list):
        record_error(errors, f"Slide {slide_index}: `{field_name}` must be a list.")
        return 0

    count = len(value)

    if expected is not None and count != expected:
        record_error(errors, f"Slide {slide_index}: `{field_name}` must contain exactly {expected} items, got {count}.")
    if minimum is not None and count < minimum:
        record_error(errors, f"Slide {slide_index}: `{field_name}` must contain at least {minimum} items, got {count}.")
    if maximum is not None and count > maximum:
        record_error(errors, f"Slide {slide_index}: `{field_name}` must contain at most {maximum} items, got {count}.")

    for item_index, item in enumerate(value, start=1):
        if isinstance(item, dict):
            if require_title and not as_nonempty_string(item.get("title")):
                record_error(errors, f"Slide {slide_index}: `{field_name}[{item_index}]` requires a non-empty `title`.")
            continue
        if allow_strings and as_nonempty_string(item):
            continue
        record_error(errors, f"Slide {slide_index}: `{field_name}[{item_index}]` must be an object or non-empty string.")

    return count


def validate_table(errors: list[str], slide_index: int, data: dict[str, Any], layout: dict[str, Any]) -> None:
    headers = data.get("headers")
    rows = data.get("rows")
    if not isinstance(headers, list) or not headers:
        record_error(errors, f"Slide {slide_index}: `headers` must be a non-empty list.")
        return
    if not isinstance(rows, list) or not rows:
        record_error(errors, f"Slide {slide_index}: `rows` must be a non-empty list.")
        return

    constraints = layout.get("constraints", {})
    column_limits = constraints.get("columns", {})
    row_limits = constraints.get("rows", {})
    column_count = len(headers)

    if column_limits:
        minimum = column_limits.get("min")
        maximum = column_limits.get("max")
        if minimum is not None and column_count < minimum:
            record_error(errors, f"Slide {slide_index}: table headers must contain at least {minimum} columns, got {column_count}.")
        if maximum is not None and column_count > maximum:
            record_error(errors, f"Slide {slide_index}: table headers must contain at most {maximum} columns, got {column_count}.")

    if row_limits:
        minimum = row_limits.get("min")
        maximum = row_limits.get("max")
        if minimum is not None and len(rows) < minimum:
            record_error(errors, f"Slide {slide_index}: table must contain at least {minimum} rows, got {len(rows)}.")
        if maximum is not None and len(rows) > maximum:
            record_error(errors, f"Slide {slide_index}: table must contain at most {maximum} rows, got {len(rows)}.")

    for row_index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            record_error(errors, f"Slide {slide_index}: table row {row_index} must be an object.")
            continue
        cells = row.get("cells")
        if not isinstance(cells, list):
            record_error(errors, f"Slide {slide_index}: table row {row_index} must contain a `cells` list.")
            continue
        if len(cells) != column_count:
            record_error(errors, f"Slide {slide_index}: table row {row_index} must contain {column_count} cells, got {len(cells)}.")
        for cell_index, cell in enumerate(cells, start=1):
            if not as_nonempty_string(cell):
                record_error(errors, f"Slide {slide_index}: table row {row_index} cell {cell_index} must be a non-empty string.")


def validate_toc(errors: list[str], slide_index: int, data: dict[str, Any]) -> None:
    items = data.get("items")
    if not isinstance(items, list) or not items:
        record_error(errors, f"Slide {slide_index}: `items` must be a non-empty list.")
        return
    for item_index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            record_error(errors, f"Slide {slide_index}: TOC item {item_index} must be an object.")
            continue
        if not as_nonempty_string(item.get("num")):
            record_error(errors, f"Slide {slide_index}: TOC item {item_index} requires a non-empty `num`.")
        if not as_nonempty_string(item.get("name")):
            record_error(errors, f"Slide {slide_index}: TOC item {item_index} requires a non-empty `name`.")


def validate_timeline(errors: list[str], slide_index: int, data: dict[str, Any], layout: dict[str, Any]) -> None:
    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        record_error(errors, f"Slide {slide_index}: `nodes` must be a non-empty list.")
        return

    constraints = layout.get("constraints", {})
    node_limits = constraints.get("nodeCount", {})
    minimum = node_limits.get("min")
    maximum = node_limits.get("max")
    if minimum is not None and len(nodes) < minimum:
        record_error(errors, f"Slide {slide_index}: timeline must contain at least {minimum} nodes, got {len(nodes)}.")
    if maximum is not None and len(nodes) > maximum:
        record_error(errors, f"Slide {slide_index}: timeline must contain at most {maximum} nodes, got {len(nodes)}.")

    for node_index, node in enumerate(nodes, start=1):
        if not isinstance(node, dict):
            record_error(errors, f"Slide {slide_index}: timeline node {node_index} must be an object.")
            continue
        if not as_nonempty_string(node.get("title")):
            record_error(errors, f"Slide {slide_index}: timeline node {node_index} requires a non-empty `title`.")
        if not as_nonempty_string(node.get("desc")):
            record_error(errors, f"Slide {slide_index}: timeline node {node_index} requires a non-empty `desc`.")


def validate_point_list(errors: list[str], slide_index: int, field_name: str, value: Any) -> None:
    if not isinstance(value, list) or not value:
        record_error(errors, f"Slide {slide_index}: `{field_name}` must be a non-empty list.")
        return

    for item_index, item in enumerate(value, start=1):
        if not as_nonempty_string(item):
            record_error(errors, f"Slide {slide_index}: `{field_name}[{item_index}]` must be a non-empty string.")


def validate_comparison(errors: list[str], slide_index: int, data: dict[str, Any]) -> None:
    for side_name in ("leftCard", "rightCard"):
        side = data.get(side_name)
        if not isinstance(side, dict):
            record_error(errors, f"Slide {slide_index}: `{side_name}` must be an object.")
            continue

        if not as_nonempty_string(side.get("title")):
            record_error(errors, f"Slide {slide_index}: `{side_name}.title` must be non-empty.")

        subtitle = side.get("subtitle")
        points = side.get("points")
        has_detail = False

        if as_nonempty_string(subtitle):
            has_detail = True
        if points is not None:
            validate_point_list(errors, slide_index, f"{side_name}.points", points)
            has_detail = True

        if not has_detail:
            record_error(errors, f"Slide {slide_index}: `{side_name}` requires either `subtitle` or `points`.")


def validate_hero_statement(errors: list[str], slide_index: int, data: dict[str, Any]) -> None:
    if not as_nonempty_string(data.get("statement")):
        record_error(errors, f"Slide {slide_index}: hero statement requires a non-empty `statement`.")

    supporting = data.get("supporting")
    if supporting is not None and not as_nonempty_string(supporting):
        record_error(errors, f"Slide {slide_index}: `supporting` must be a non-empty string when provided.")

    meta = data.get("meta")
    if meta is not None and not as_nonempty_string(meta):
        record_error(errors, f"Slide {slide_index}: `meta` must be a non-empty string when provided.")


def validate_process(errors: list[str], slide_index: int, data: dict[str, Any], layout: dict[str, Any]) -> None:
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        record_error(errors, f"Slide {slide_index}: `steps` must be a non-empty list.")
        return

    constraints = layout.get("constraints", {})
    step_limits = constraints.get("stepCount", {})
    minimum = step_limits.get("min")
    maximum = step_limits.get("max")
    if minimum is not None and len(steps) < minimum:
        record_error(errors, f"Slide {slide_index}: process must contain at least {minimum} steps, got {len(steps)}.")
    if maximum is not None and len(steps) > maximum:
        record_error(errors, f"Slide {slide_index}: process must contain at most {maximum} steps, got {len(steps)}.")

    for step_index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            record_error(errors, f"Slide {slide_index}: process step {step_index} must be an object.")
            continue
        if not as_nonempty_string(step.get("title")):
            record_error(errors, f"Slide {slide_index}: process step {step_index} requires a non-empty `title`.")
        if not as_nonempty_string(step.get("desc")):
            record_error(errors, f"Slide {slide_index}: process step {step_index} requires a non-empty `desc`.")


def validate_cards_layout(
    errors: list[str],
    slide_index: int,
    data: dict[str, Any],
    layout: dict[str, Any],
    layout_id: str,
) -> None:
    structure = layout.get("structure", {})

    if layout_id.startswith("cards-left-"):
        left_expected = structure.get("leftColumn", {}).get("cardCount")
        right_expected = structure.get("rightColumn", {}).get("cardCount")
        validate_card_list(errors, slide_index, "leftCards", data.get("leftCards"), expected=left_expected, require_title=True)
        validate_card_list(errors, slide_index, "rightCards", data.get("rightCards"), expected=right_expected, require_title=True)
        return

    if layout_id.startswith("cards-top-"):
        top_expected = structure.get("topRow", {}).get("cardCount")
        bottom_expected = structure.get("bottomRow", {}).get("cardCount")
        top_card = data.get("topCard")
        top_cards = data.get("topCards")
        if top_card is not None:
            if isinstance(top_card, dict):
                if top_expected not in (None, 1):
                    record_error(errors, f"Slide {slide_index}: `topCard` is a single object but layout expects {top_expected} cards.")
                if not as_nonempty_string(top_card.get("title")):
                    record_error(errors, f"Slide {slide_index}: `topCard.title` must be non-empty.")
            elif isinstance(top_card, list):
                validate_card_list(errors, slide_index, "topCard", top_card, expected=top_expected, require_title=True)
            else:
                record_error(errors, f"Slide {slide_index}: `topCard` must be an object or list.")
        elif top_cards is not None:
            validate_card_list(errors, slide_index, "topCards", top_cards, expected=top_expected, require_title=True)
        else:
            record_error(errors, f"Slide {slide_index}: `topCard` or `topCards` is required.")

        bottom_card = data.get("bottomCard")
        bottom_cards = data.get("bottomCards")
        if bottom_card is not None:
            if isinstance(bottom_card, dict):
                if bottom_expected not in (None, 1):
                    record_error(errors, f"Slide {slide_index}: `bottomCard` is a single object but layout expects {bottom_expected} cards.")
                if not as_nonempty_string(bottom_card.get("title")):
                    record_error(errors, f"Slide {slide_index}: `bottomCard.title` must be non-empty.")
            elif isinstance(bottom_card, list):
                validate_card_list(errors, slide_index, "bottomCard", bottom_card, expected=bottom_expected, require_title=True)
            else:
                record_error(errors, f"Slide {slide_index}: `bottomCard` must be an object or list.")
        elif bottom_cards is not None:
            validate_card_list(errors, slide_index, "bottomCards", bottom_cards, expected=bottom_expected, require_title=True)
        else:
            record_error(errors, f"Slide {slide_index}: `bottomCard` or `bottomCards` is required.")
        return

    if layout_id.startswith("grid-cols-"):
        cards = data.get("cards")
        expected_columns = structure.get("columns")
        expected_rows = structure.get("rows")
        expected_count = expected_columns * expected_rows if isinstance(expected_columns, int) and isinstance(expected_rows, int) else None
        validate_card_list(errors, slide_index, "cards", cards, expected=expected_count, require_title=True)
        return

    if layout_id in {"content-col", "content-row"}:
        constraints = layout.get("constraints", {})
        card_limits = constraints.get("cardCount", {})
        items = data.get("items")
        cards = data.get("cards")
        if isinstance(items, list):
            validate_card_list(errors, slide_index, "items", items, minimum=card_limits.get("min"), maximum=card_limits.get("max"), allow_strings=True)
            return
        if isinstance(cards, list):
            validate_card_list(
                errors,
                slide_index,
                "cards",
                cards,
                minimum=card_limits.get("min"),
                maximum=card_limits.get("max"),
                require_title=True,
            )
            return
        record_error(errors, f"Slide {slide_index}: `{layout_id}` requires either `items` or `cards`.")
        return


def validate_slide(
    errors: list[str],
    warnings: list[str],
    slide: dict[str, Any],
    slide_index: int,
    total_slides: int,
    layouts: dict[str, Any],
    themes: dict[str, Any],
) -> None:
    layout_id = slide.get("layout_id")
    theme_id = slide.get("theme")
    data = slide.get("data")

    if not as_nonempty_string(layout_id):
        record_error(errors, f"Slide {slide_index}: `layout_id` must be a non-empty string.")
        return
    if not as_nonempty_string(theme_id):
        record_error(errors, f"Slide {slide_index}: `theme` must be a non-empty string.")
        return
    if not isinstance(data, dict):
        record_error(errors, f"Slide {slide_index}: `data` must be an object.")
        return

    layout_info = layouts.get(layout_id)
    if not layout_info:
        record_error(errors, f"Slide {slide_index}: unknown layout `{layout_id}`.")
        return
    if theme_id not in themes:
        record_error(errors, f"Slide {slide_index}: unknown theme `{theme_id}`.")
        return

    layout_path = BASE_PATH / "design-system" / layout_info["file"]
    if not layout_path.exists():
        record_error(errors, f"Slide {slide_index}: layout file not found at {layout_path}.")
        return

    layout = load_json(layout_path)
    layout_type = layout.get("type")
    footer_visible = bool(layout.get("footer", {}).get("visible", True))
    page = data.get("page")
    total = data.get("total")

    if footer_visible:
        if not isinstance(page, int) or page < 1:
            record_error(errors, f"Slide {slide_index}: `page` is required when footer is visible.")
        elif page != slide_index:
            record_error(errors, f"Slide {slide_index}: `page` must equal its 1-based position, got {page}.")

        if not isinstance(total, int) or total != total_slides:
            record_error(errors, f"Slide {slide_index}: `total` must equal slide count {total_slides}, got {total!r}.")
    else:
        if isinstance(page, int) and page != slide_index:
            record_warning(warnings, f"Slide {slide_index}: `page` is present but does not match its position ({page}).")
        if isinstance(total, int) and total != total_slides:
            record_warning(warnings, f"Slide {slide_index}: `total` is present but does not match slide count ({total}).")

    if layout_type == "cover":
        if not as_nonempty_string(data.get("title")):
            record_error(errors, f"Slide {slide_index}: cover requires a non-empty `title`.")
        if not as_nonempty_string(data.get("subtitle")):
            record_error(errors, f"Slide {slide_index}: cover requires a non-empty `subtitle`.")
        return

    if layout_type == "ending":
        if not as_nonempty_string(data.get("title")):
            record_error(errors, f"Slide {slide_index}: ending requires a non-empty `title`.")
        return

    if layout_type == "toc":
        if not as_nonempty_string(data.get("title")):
            record_error(errors, f"Slide {slide_index}: toc requires a non-empty `title`.")
        validate_toc(errors, slide_index, data)
        return

    if layout_id == "comparison":
        if not as_nonempty_string(data.get("title")):
            record_error(errors, f"Slide {slide_index}: comparison requires a non-empty `title`.")
        validate_comparison(errors, slide_index, data)
        return

    if layout_id == "hero-statement":
        validate_hero_statement(errors, slide_index, data)
        return

    if layout_id == "process":
        if not as_nonempty_string(data.get("title")):
            record_error(errors, f"Slide {slide_index}: process requires a non-empty `title`.")
        validate_process(errors, slide_index, data, layout)
        return

    if layout_id == "table":
        if not as_nonempty_string(data.get("title")):
            record_error(errors, f"Slide {slide_index}: table requires a non-empty `title`.")
        validate_table(errors, slide_index, data, layout)
        return

    if layout_id == "timeline":
        if not as_nonempty_string(data.get("title")):
            record_error(errors, f"Slide {slide_index}: timeline requires a non-empty `title`.")
        validate_timeline(errors, slide_index, data, layout)
        return

    if layout_id.startswith("cards-") or layout_id.startswith("grid-cols-") or layout_id in {"content-col", "content-row"}:
        if not as_nonempty_string(data.get("title")):
            record_error(errors, f"Slide {slide_index}: `{layout_id}` requires a non-empty `title`.")
        validate_cards_layout(errors, slide_index, data, layout, layout_id)
        return

    record_warning(warnings, f"Slide {slide_index}: no dedicated validation rules for `{layout_id}`.")


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

    try:
        design_system = load_json(DESIGN_SYSTEM_PATH)
    except Exception as exc:
        print(f"Failed to parse {DESIGN_SYSTEM_PATH}: {exc}")
        sys.exit(1)

    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(content, dict):
        record_error(errors, "Top-level content must be an object.")
    else:
        if not isinstance(content.get("version"), int) or content["version"] < 1:
            record_error(errors, "Top-level `version` must be a positive integer.")

        source = content.get("source")
        if source is not None and not as_nonempty_string(source):
            record_error(errors, "Top-level `source` must be a non-empty string when provided.")
        elif not isinstance(source, str):
            record_warning(warnings, "Top-level `source` is missing; manifest traceability will be weaker.")

        slides = content.get("slides")
        if not isinstance(slides, list) or not slides:
            record_error(errors, "Top-level `slides` must be a non-empty list.")
            slides = []

        layouts = design_system.get("layouts", {})
        themes = design_system.get("themes", {})

        if isinstance(slides, list):
            for index, slide in enumerate(slides, start=1):
                if not isinstance(slide, dict):
                    record_error(errors, f"Slide {index}: slide entry must be an object.")
                    continue

                validate_slide(errors, warnings, slide, index, len(slides), layouts, themes)

            layout_counts = Counter(slide.get("layout_id") for slide in slides if isinstance(slide, dict))
            if layout_counts:
                most_common_layout, count = layout_counts.most_common(1)[0]
                if count / len(slides) > 0.6:
                    record_warning(
                        warnings,
                        f"Layout `{most_common_layout}` accounts for {count}/{len(slides)} slides ({count / len(slides):.0%}).",
                    )

    report = {
        "status": "fail" if errors else "warn" if warnings else "pass",
        "content_path": str(content_path),
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "slide_count": len(content.get("slides", [])) if isinstance(content, dict) else 0,
            "layout_counts": dict(Counter(
                slide.get("layout_id") for slide in content.get("slides", []) if isinstance(slide, dict)
            )) if isinstance(content, dict) else {},
        },
    }

    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if errors:
        print(f"[FAIL] Presentation content validation failed. Report: {REPORT_PATH}")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    if warnings:
        print(f"[WARN] Presentation content validation passed with warnings. Report: {REPORT_PATH}")
        for warning in warnings:
            print(f"  - {warning}")
        return

    print(f"[OK] Presentation content validation passed. Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
