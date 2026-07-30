#!/usr/bin/env python3
"""
validate_design_system.py - 校验设计系统是否仍然包含已修复问题的回归风险。

重点检查：
1. 字号是否继续由设计系统统一控制
2. 渲染是否仍然只截取 .slide
3. 经典案例页是否保持“垂直居中 + 左对齐”
4. 布局文件是否继续存在明显的硬编码字号
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent
DESIGN_SYSTEM_PATH = BASE_PATH / "design-system" / "design-system.json"
LAYOUTS_DIR = BASE_PATH / "design-system" / "layouts"


def load_design_system() -> dict:
    with open(DESIGN_SYSTEM_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def assert_required_typography(defaults: dict) -> None:
    typography = defaults.get("typography", {})
    required_keys = ["coverTitle", "coverSubtitle", "sectionTitle", "cardTitle", "body", "footer", "subtitle"]
    missing = [key for key in required_keys if key not in typography]
    if missing:
        fail(f"presentationDefaults.typography 缺少字段: {', '.join(missing)}")

    for key in required_keys:
        value = typography.get(key)
        if not isinstance(value, int) or value <= 0:
            fail(f"presentationDefaults.typography.{key} 必须是正整数，当前值: {value!r}")


def assert_rendering_defaults(rendering_defaults: dict) -> None:
    if rendering_defaults.get("screenshotTarget") != ".slide":
        fail("renderingDefaults.screenshotTarget 必须保持为 .slide")
    if rendering_defaults.get("clearOutputBeforeRun") is not True:
        fail("renderingDefaults.clearOutputBeforeRun 必须为 true")

    viewport = rendering_defaults.get("viewport", {})
    if viewport.get("width") != 1920 or viewport.get("height") != 1080:
        fail("renderingDefaults.viewport 必须保持为 1920x1080")


def assert_slide_size(defaults: dict) -> None:
    slide_size = defaults.get("slideSize", {})
    if slide_size.get("width") != 1920 or slide_size.get("height") != 1080:
        fail("presentationDefaults.slideSize 必须保持为 1920x1080")

    component_defaults = defaults.get("componentDefaults", {})
    card_defaults = component_defaults.get("card", {})
    content_defaults = component_defaults.get("content", {})
    if card_defaults.get("paddingX") is None or card_defaults.get("paddingY") is None:
        fail("presentationDefaults.componentDefaults.card 缺少 paddingX / paddingY")
    if content_defaults.get("bulletWidth") is None or content_defaults.get("subtitleIndent") is None:
        fail("presentationDefaults.componentDefaults.content 缺少 bulletWidth / subtitleIndent")


def assert_regression_rules(ds: dict) -> None:
    rules = {rule.get("id") for rule in ds.get("regressionRules", [])}
    required = {"font-scale-unified", "crop-boundary", "vertical-center-left", "missing-padding"}
    missing = sorted(required - rules)
    if missing:
        fail(f"regressionRules 缺少: {', '.join(missing)}")


def assert_case_layout(layout: dict) -> None:
    css = layout.get("css", {})

    card_rule = css.get(".slide.cards .card", {})
    if card_rule.get("align-items") != "center":
        fail("cards-left-1-right-2 的卡片容器必须垂直居中")
    if card_rule.get("justify-content") != "flex-start":
        fail("cards-left-1-right-2 的卡片容器必须左对齐")

    line_rule = css.get(".slide.cards .line", {})
    if line_rule.get("justify-content") != "center":
        fail("cards-left-1-right-2 的文字块必须在卡片内垂直居中")
    if line_rule.get("align-items") != "flex-start":
        fail("cards-left-1-right-2 的文字块必须保持左对齐")

    main_rule = css.get(".slide.cards .line .main", {})
    if main_rule.get("align-items") != "center":
        fail("cards-left-1-right-2 的主标题与 bullet 必须垂直居中对齐")

    sub_rule = css.get(".slide.cards .line .sub", {})
    if sub_rule.get("margin-top") != "0":
        fail("cards-left-1-right-2 的副标题必须贴着主标题对齐，margin-top 应为 0")


def assert_no_hardcoded_font_sizes() -> None:
    hardcoded_pattern = re.compile(r'"font-size"\s*:\s*"(?!(?:var\()|(?:inherit)|(?:initial)|(?:unset))[^"]*\d[^"]*"')
    offenders: list[str] = []

    for path in sorted(LAYOUTS_DIR.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if hardcoded_pattern.search(content):
            offenders.append(path.name)

    if offenders:
        fail("仍存在硬编码字号的布局文件: " + ", ".join(offenders))


def main() -> None:
    ds = load_design_system()
    presentation_defaults = ds.get("presentationDefaults", {})
    rendering_defaults = ds.get("renderingDefaults", {})
    layouts = ds.get("layouts", {})

    assert_required_typography(presentation_defaults)
    assert_rendering_defaults(rendering_defaults)
    assert_slide_size(presentation_defaults)
    assert_regression_rules(ds)

    case_layout_info = layouts.get("cards-left-1-right-2")
    if not case_layout_info:
        fail("缺少 cards-left-1-right-2 布局定义")

    case_layout_path = BASE_PATH / "design-system" / case_layout_info["file"]
    with open(case_layout_path, "r", encoding="utf-8") as f:
        case_layout = json.load(f)
    assert_case_layout(case_layout)
    assert_no_hardcoded_font_sizes()

    print("[OK] 设计系统校验通过")


if __name__ == "__main__":
    main()
