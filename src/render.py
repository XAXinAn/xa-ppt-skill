#!/usr/bin/env python3
"""
render.py - 使用 Playwright 将 HTML 文件渲染为 PNG 截图
"""

import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_PATH = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_PATH / "output"
HTML_DIR = OUTPUT_DIR / "slides"
IMAGES_DIR = OUTPUT_DIR / "images"


def load_rendering_defaults() -> dict:
    """读取设计系统里定义的渲染约束。"""
    ds_path = BASE_PATH / "design-system" / "design-system.json"
    with open(ds_path, "r", encoding="utf-8") as f:
        main_config = json.load(f)
    return main_config.get("renderingDefaults", {})


def get_html_files():
    """获取 slides 目录下的所有 HTML 文件。"""
    html_files = sorted(HTML_DIR.glob("*.html"))
    return [f for f in html_files if f.name.startswith("slide-")]


def clear_generated_files(directory: Path, pattern: str) -> None:
    """清理旧的生成物，避免历史产物混入本次输出。"""
    if not directory.exists():
        return

    for path in directory.glob(pattern):
        if path.is_file():
            path.unlink()


def render_html_to_image(html_path: Path, output_path: Path, rendering_defaults: dict):
    """使用 Playwright 渲染单个 HTML 文件并截图。"""
    viewport = rendering_defaults.get("viewport", {})
    screenshot_target = rendering_defaults.get("screenshotTarget", ".slide")
    screenshot_width = viewport.get("width", 1920)
    screenshot_height = viewport.get("height", 1080)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": screenshot_width, "height": screenshot_height})
        page.goto(html_path.resolve().as_uri())
        page.wait_for_selector(screenshot_target)
        page.locator(screenshot_target).screenshot(path=str(output_path))
        browser.close()


def main():
    rendering_defaults = load_rendering_defaults()

    # 确保图片输出目录存在
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    if rendering_defaults.get("clearOutputBeforeRun", True):
        clear_generated_files(IMAGES_DIR, "*.png")

    html_files = get_html_files()

    if not html_files:
        print("未找到 HTML 文件，请先运行 AI 生成 HTML。")
        sys.exit(1)

    print(f"找到 {len(html_files)} 个 HTML 文件，开始渲染...")

    for html_file in html_files:
        # 生成图片文件名：slide-01-cover.html -> images/slide-01-cover.png
        image_name = html_file.stem + ".png"
        image_path = IMAGES_DIR / image_name

        print(f"  渲染: {html_file.name} -> {image_path.name}")
        try:
            render_html_to_image(html_file, image_path, rendering_defaults)
            print(f"    OK")
        except Exception as e:
            print(f"    FAIL: {e}")
            sys.exit(1)

    print(f"\n渲染完成！{len(html_files)} 个图片已保存到 {IMAGES_DIR}/")
    print("\n接下来运行: python src/build_pptx.py")


if __name__ == "__main__":
    main()
