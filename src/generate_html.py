#!/usr/bin/env python3
"""
generate_html.py - 从 design-system.json 读取布局配置，生成 HTML 幻灯片
"""

import json
import re
from pathlib import Path
from typing import Any, Dict

BASE_PATH = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_PATH / "output"
SLIDES_DIR = OUTPUT_DIR / "slides"
OUTLINE_PATHS = [
    Path.home() / "Desktop" / "AI经验分享PPT大纲.md",
    BASE_PATH / "AI经验分享PPT大纲.md",
]
SPEC_JSON_PATHS = [
    BASE_PATH / "deck-spec.json",
    BASE_PATH / "presentation-content.json",
    BASE_PATH / "content" / "deck-spec.json",
    BASE_PATH / "content" / "presentation-content.json",
]
SECTION_RE = re.compile(r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}", re.DOTALL)
VAR_RE = re.compile(r"\{\{(\w+|\.)\}\}")
SLIDE_HEADING_RE = re.compile(r"^##\s+Slide\s+(\d+)：(.+)$")
SUBTITLE_RE = re.compile(r"^###\s+(.+)$")
BULLET_RE = re.compile(r"^-\s+(.+)$")
NUMBERED_RE = re.compile(r"^(\d+)\.\s+(.+)$")
TABLE_ROW_RE = re.compile(r"^\|.*\|$")
TABLE_SEPARATOR_RE = re.compile(r"^\|(?:\s*:?-+:?\s*\|)+\s*$")


def clear_generated_files(directory: Path, pattern: str) -> None:
    """删除目录下匹配的生成物，避免旧产物污染当前输出。"""
    if not directory.exists():
        return

    for path in directory.glob(pattern):
        if path.is_file():
            path.unlink()


def find_outline_path() -> Path | None:
    """查找用户提供的大纲文件。"""
    for path in OUTLINE_PATHS:
        if path.exists():
            return path
    return None


def find_spec_json_path() -> Path | None:
    """查找预生成的 PPT 规格 JSON。"""
    for path in SPEC_JSON_PATHS:
        if path.exists():
            return path
    return None


def load_content_json(content_path: Path) -> list[dict]:
    """读取内容 JSON 里的幻灯片定义。"""
    with open(content_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    slides = content.get("slides", [])
    if not isinstance(slides, list):
        return []
    return slides


def split_slide_blocks(markdown_text: str) -> list[dict]:
    """把大纲拆成按 Slide 编号分组的块。"""
    lines = markdown_text.splitlines()
    blocks = []
    current = None

    for line in lines:
        match = SLIDE_HEADING_RE.match(line.strip())
        if match:
            if current:
                blocks.append(current)
            current = {
                "number": int(match.group(1)),
                "title": match.group(2).strip(),
                "lines": [],
            }
            continue

        if current is not None:
            current["lines"].append(line)

    if current:
        blocks.append(current)

    return blocks


def first_section_heading(lines: list[str]) -> str:
    """提取每页第一个三级标题作为副标题。"""
    for line in lines:
        match = SUBTITLE_RE.match(line.strip())
        if match:
            return match.group(1).strip()
    return ""


def extract_bullet_texts(lines: list[str]) -> list[str]:
    """提取普通项目符号内容。"""
    bullets = []
    for line in lines:
        match = BULLET_RE.match(line.strip())
        if match:
            bullets.append(match.group(1).strip())
    return bullets


def extract_numbered_items(lines: list[str]) -> list[str]:
    """提取有序列表内容。"""
    items = []
    for line in lines:
        match = NUMBERED_RE.match(line.strip())
        if match:
            items.append(match.group(2).strip())
    return items


def parse_table(lines: list[str]) -> dict[str, Any]:
    """提取 Markdown 表格。"""
    table_lines = [line.strip() for line in lines if TABLE_ROW_RE.match(line.strip())]
    if not table_lines:
        return {"headers": [], "rows": []}

    rows = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and all(re.fullmatch(r"[:\-\s]+", cell or "") for cell in cells):
            continue
        rows.append(cells)

    if not rows:
        return {"headers": [], "rows": []}

    headers = rows[0]
    body_rows = rows[1:]
    return {
        "headers": headers,
        "rows": [{"cells": row} for row in body_rows],
    }


def parse_outline_slides(markdown_path: Path) -> list[dict]:
    """从 Markdown 大纲生成当前 PPT 的幻灯片定义。"""
    with open(markdown_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    slide_blocks = split_slide_blocks(markdown_text)
    total_slides = len(slide_blocks)
    slides = []

    for block in slide_blocks:
        number = block["number"]
        title = block["title"]
        lines = block["lines"]
        subtitle = first_section_heading(lines)
        bullets = extract_bullet_texts(lines)
        numbered = extract_numbered_items(lines)

        slide_data: dict[str, Any] = {
            "page": number,
            "total": total_slides,
        }

        if number == 1:
            for bullet in bullets:
                if bullet.startswith("标题："):
                    slide_data["title"] = bullet.split("：", 1)[1].strip()
                elif bullet.startswith("副标题："):
                    slide_data["subtitle"] = bullet.split("：", 1)[1].strip()
                else:
                    slide_data["note"] = bullet
            slides.append({
                "layout_id": "cover",
                "theme": "tech",
                "data": slide_data,
            })
            continue

        if number == 3:
            toc_items = []
            for idx, raw_item in enumerate(numbered, start=1):
                match = re.match(r"^(.+?)\s*[—–-]\s*(.+)$", raw_item)
                if match:
                    name, desc = match.group(1).strip(), match.group(2).strip()
                else:
                    name, desc = raw_item, ""
                item = {"num": f"{idx:02d}", "name": name}
                if desc:
                    item["desc"] = desc
                toc_items.append(item)
            slide_data["title"] = title
            if subtitle:
                slide_data["subtitle"] = subtitle
            slide_data["items"] = toc_items
            slides.append({
                "layout_id": "toc",
                "theme": "tech",
                "data": slide_data,
            })
            continue

        if number in {7, 11, 15, 19}:
            table = parse_table(lines)
            slide_data["title"] = title
            if subtitle:
                slide_data["subtitle"] = subtitle
            slide_data["headers"] = table["headers"]
            slide_data["rows"] = table["rows"]
            slides.append({
                "layout_id": "table",
                "theme": "tech",
                "data": slide_data,
            })
            continue

        if number == 20:
            slide_data["title"] = title
            if subtitle:
                slide_data["subtitle"] = subtitle
            slide_data["bullets"] = bullets
            slides.append({
                "layout_id": "ending",
                "theme": "tech",
                "data": slide_data,
            })
            continue

        slide_data["title"] = title
        if subtitle:
            slide_data["subtitle"] = subtitle
        slide_data["items"] = bullets or numbered
        slides.append({
            "layout_id": "content-col",
            "theme": "tech",
            "data": slide_data,
        })

    return slides


def load_design_system(base_path: Path) -> Dict[str, Any]:
    """加载设计系统主配置和所有布局、主题。"""
    ds_path = base_path / "design-system"
    with open(ds_path / "design-system.json", "r", encoding="utf-8") as f:
        main_config = json.load(f)

    layouts = {}
    for layout_id, layout_info in main_config["layouts"].items():
        layout_file = layout_info["file"]
        with open(ds_path / layout_file, "r", encoding="utf-8") as f:
            layouts[layout_id] = json.load(f)

    themes = {}
    for theme_id, theme_info in main_config["themes"].items():
        theme_file = theme_info["file"]
        with open(ds_path / theme_file, "r", encoding="utf-8") as f:
            themes[theme_id] = json.load(f)

    return {
        "main": main_config,
        "layouts": layouts,
        "themes": themes
    }


def generate_css_variables(theme: Dict[str, Any], presentation_defaults: Dict[str, Any]) -> str:
    """从主题生成 CSS 变量声明。"""
    colors = theme.get("colors", {})
    typography = theme.get("typography", {})
    presentation_typography = presentation_defaults.get("typography", {})
    slide_padding = presentation_defaults.get("slidePadding", {})
    slide_size = presentation_defaults.get("slideSize", {})
    component_defaults = presentation_defaults.get("componentDefaults", {})
    card_defaults = component_defaults.get("card", {})
    content_defaults = component_defaults.get("content", {})
    lines = []
    for key, value in colors.items():
        lines.append(f"  --{key}: {value};")
    title_size = presentation_typography.get("sectionTitle", typography.get("titleSize", {}).get("default", 44))
    heading_size = presentation_typography.get("cardTitle", typography.get("headingSize", {}).get("default", 28))
    body_size = presentation_typography.get("body", typography.get("bodySize", {}).get("default", 20))
    table_body_size = presentation_typography.get("tableBody", body_size)
    table_header_size = presentation_typography.get("tableHeader", heading_size)
    lines.append(f"  --slide-title-size: {title_size}px;")
    lines.append(f"  --slide-heading-size: {heading_size}px;")
    lines.append(f"  --slide-body-size: {body_size}px;")
    lines.append(f"  --slide-table-body-size: {table_body_size}px;")
    lines.append(f"  --slide-table-header-size: {table_header_size}px;")
    lines.append(f"  --slide-cover-title-size: {presentation_typography.get('coverTitle', 96)}px;")
    lines.append(f"  --slide-cover-subtitle-size: {presentation_typography.get('coverSubtitle', 40)}px;")
    lines.append(f"  --slide-subtitle-size: {presentation_typography.get('subtitle', 26)}px;")
    lines.append(f"  --slide-footer-size: {presentation_typography.get('footer', 20)}px;")
    lines.append(f"  --slide-padding-x: {slide_padding.get('x', 80)}px;")
    lines.append(f"  --slide-padding-y: {slide_padding.get('y', 72)}px;")
    lines.append(f"  --slide-width: {slide_size.get('width', 1920)}px;")
    lines.append(f"  --slide-height: {slide_size.get('height', 1080)}px;")
    lines.append(f"  --slide-card-padding-x: {card_defaults.get('paddingX', 36)}px;")
    lines.append(f"  --slide-card-padding-y: {card_defaults.get('paddingY', 28)}px;")
    lines.append(f"  --slide-card-radius: {card_defaults.get('radius', 12)}px;")
    lines.append(f"  --slide-content-stack-gap: {content_defaults.get('stackGap', 8)}px;")
    lines.append(f"  --slide-bullet-width: {content_defaults.get('bulletWidth', 50)}px;")
    lines.append(f"  --slide-subtitle-indent: {content_defaults.get('subtitleIndent', 50)}px;")
    return ":root {\n" + "\n".join(lines) + "\n}"


def generate_layout_css(layout: Dict[str, Any]) -> str:
    """从布局配置生成 CSS。"""
    css = layout.get("css", {})
    lines = []
    for selector, props in css.items():
        lines.append(f"    {selector} {{")
        for prop, value in props.items():
            lines.append(f"      {prop}: {value};")
        lines.append("    }")
    return "\n".join(lines)


def generate_html(layout: Dict[str, Any], theme: Dict[str, Any], data: Dict[str, Any]) -> str:
    """从 Mustache 模板生成 HTML。循环先处理，再用数据替换变量。"""
    template = layout.get("html", "")

    def render_fragment(fragment: str, context: Dict[str, Any]) -> str:
        """递归处理 section，再替换标量变量。"""
        rendered = fragment

        while True:
            match = SECTION_RE.search(rendered)
            if not match:
                break

            section_name = match.group(1)
            section_block = match.group(2)
            section_value = context.get(section_name, [])
            replacement = ""

            if isinstance(section_value, list):
                rendered_items = []
                for item in section_value:
                    child_context = dict(context)
                    child_context["."] = item
                    if isinstance(item, dict):
                        child_context.update(item)
                    rendered_items.append(render_fragment(section_block, child_context))
                replacement = "".join(rendered_items)
            elif isinstance(section_value, dict):
                child_context = dict(context)
                child_context.update(section_value)
                child_context["."] = section_value
                replacement = render_fragment(section_block, child_context)
            elif section_value:
                replacement = render_fragment(section_block, context)

            rendered = rendered[:match.start()] + replacement + rendered[match.end():]

        def replace_var(match: re.Match[str]) -> str:
            key = match.group(1)
            value = context.get(key, "")
            if key == ".":
                value = context.get(".", "")
            return "" if value is None else str(value)

        return VAR_RE.sub(replace_var, rendered)

    return render_fragment(template, data)


def split_card_text(text: str) -> dict[str, str]:
    """把单行正文拆成标题和说明，优先按中文标点切分。"""
    if not isinstance(text, str):
        return {"title": str(text)}

    cleaned = text.strip()
    if not cleaned:
        return {"title": ""}

    separators = ["：", ":", "，", ",", "；", ";", "。", "—", "–", "-"]
    for separator in separators:
        if separator not in cleaned:
            continue

        head, tail = cleaned.split(separator, 1)
        head = head.strip()
        tail = tail.strip(" ：:，,；;。—–-")

        if head and tail:
            return {"title": head, "subtitle": tail}

    return {"title": cleaned}


def normalize_content_col_items(items: list[Any]) -> list[dict[str, Any]]:
    """把 content-col 的字符串项转成两层卡片数据。"""
    normalized: list[dict[str, Any]] = []

    for item in items:
        if isinstance(item, dict):
            normalized.append(item)
            continue

        normalized.append(split_card_text(str(item)))

    return normalized


def get_slide_base_css(presentation_defaults: Dict[str, Any]) -> str:
    """获取所有布局共享的基础 CSS。"""
    return """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
      background: #0b0f14;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .slide {
      width: var(--slide-width, 1920px);
      height: var(--slide-height, 1080px);
      background: var(--bg);
      padding: var(--slide-padding-y, 72px) var(--slide-padding-x, 80px);
      overflow: hidden;
    }
"""


def build_html_file(layout_id: str, layout: Dict[str, Any], theme: Dict[str, Any], data: Dict[str, Any], presentation_defaults: Dict[str, Any]) -> str:
    """构建完整的 HTML 文件内容。"""
    css_vars = generate_css_variables(theme, presentation_defaults)
    layout_css = generate_layout_css(layout)
    layout_class = layout_id

    if layout_id.startswith("cards-left-") or layout_id.startswith("cards-top-"):
        layout_class = f"{layout_id} cards"
    elif layout_id.startswith("grid-cols-"):
        layout_class = f"{layout_id} grid"

    html_content = generate_html(layout, theme, data)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{data.get('title', layout.get('name', layout_id))}</title>
  <style>
{css_vars}
{get_slide_base_css(presentation_defaults)}
{layout_css}
  </style>
</head>
<body>
  <div class="slide {layout_class}">
{html_content}
  </div>
</body>
</html>"""


def main():
    ds = load_design_system(BASE_PATH)
    presentation_defaults = ds["main"].get("presentationDefaults", {})

    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    clear_generated_files(SLIDES_DIR, "*.html")

    content_json_path = find_spec_json_path()
    if content_json_path:
        slides = load_content_json(content_json_path)
        if not slides:
            print(f"内容 JSON 为空: {content_json_path}")
            sys.exit(1)

        for i, slide in enumerate(slides):
            layout_id = slide["layout_id"]
            theme_id = slide["theme"]
            data = dict(slide["data"])
            if layout_id == "content-col" and isinstance(data.get("items"), list):
                data["items"] = normalize_content_col_items(data["items"])

            layout = ds["layouts"].get(layout_id)
            theme = ds["themes"].get(theme_id)

            if not layout:
                print(f"Layout not found: {layout_id}")
                continue
            if not theme:
                print(f"Theme not found: {theme_id}")
                continue

            html = build_html_file(layout_id, layout, theme, data, presentation_defaults)

            filename = f"slide-{i+1:02d}-{layout_id}.html"
            filepath = SLIDES_DIR / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Generated: {filename}")

        print(f"\nDone! {len(slides)} slides generated to {SLIDES_DIR}/")
        return

    outline_path = find_outline_path()
    if outline_path:
        slides = parse_outline_slides(outline_path)

        for i, slide in enumerate(slides):
            layout_id = slide["layout_id"]
            theme_id = slide["theme"]
            data = dict(slide["data"])
            if layout_id == "content-col" and isinstance(data.get("items"), list):
                data["items"] = normalize_content_col_items(data["items"])

            layout = ds["layouts"].get(layout_id)
            theme = ds["themes"].get(theme_id)

            if not layout:
                print(f"Layout not found: {layout_id}")
                continue
            if not theme:
                print(f"Theme not found: {theme_id}")
                continue

            html = build_html_file(layout_id, layout, theme, data, presentation_defaults)

            filename = f"slide-{i+1:02d}-{layout_id}.html"
            filepath = SLIDES_DIR / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Generated: {filename}")

        print(f"\nDone! {len(slides)} slides generated to {SLIDES_DIR}/")
        return

    # 幻灯片数据
    slides = [
        {
            "layout_id": "cover",
            "theme": "tech",
            "data": {
                "title": "ppt-skill AI 协作经验分享",
                "subtitle": "实习项目汇报",
                "page": 1,
                "total": 20
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "背景",
                "page": 2,
                "total": 20,
                "cards": [
                    {"title": "AI 当打字机", "subtitle": "写课程设计、写论文，先让它产出一个 Word"},
                    {"title": "说一步做一步", "subtitle": "从 0 写 Web 课程设计，反复调整很多遍"},
                    {"title": "不是协作", "subtitle": "进公司后才发现，这不算真正的 AI 协作"},
                ]
            }
        },
        {
            "layout_id": "toc",
            "theme": "tech",
            "data": {
                "title": "目录",
                "page": 3,
                "total": 20,
                "items": [
                    {"num": "01", "name": "需求怎么对"},
                    {"num": "02", "name": "边界怎么定"},
                    {"num": "03", "name": "效率怎么提"},
                    {"num": "04", "name": "版本怎么管"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "需求怎么对 - 问题",
                "page": 4,
                "total": 20,
                "cards": [
                    {"title": "上下文丢失", "subtitle": "“当前阶段目标”被 AI 直接忽略"},
                    {"title": "原意偏移", "subtitle": "“验证能力”被理解成“专门做自我介绍 PPT”"},
                    {"title": "口头对齐失效", "subtitle": "你以为在对齐，其实 AI 根本没理解"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "需求怎么对 - 原因",
                "page": 5,
                "total": 20,
                "cards": [
                    {"title": "上下文有限", "subtitle": "你没说的背景，AI 不知道"},
                    {"title": "信息传递损耗", "subtitle": "想的、说的、理解的，常常不是一回事"},
                    {"title": "理解≠真理解", "subtitle": "说理解了，不等于真的理解对了"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "需求怎么对 - 解决方式",
                "page": 6,
                "total": 20,
                "cards": [
                    {"title": "需求说明", "subtitle": "先看有没有抓住产品层面的目标"},
                    {"title": "需求分析", "subtitle": "再看技术方案判断有没有偏"},
                    {"title": "设计分析", "subtitle": "确认系统怎么组织、怎么落地"},
                ]
            }
        },
        {
            "layout_id": "cards-left-1-right-2",
            "theme": "tech",
            "data": {
                "title": "需求对齐 - 案例",
                "page": 7,
                "total": 20,
                "leftCards": [
                    {"title": "问题", "subtitle": "理解成“专门工具”，最后往错误方向改"},
                ],
                "rightCards": [
                    {"title": "解决", "subtitle": "用需求说明、需求分析、设计分析逐条验证"},
                    {"title": "结果", "subtitle": "最后确定 HTML 渲染方案"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "边界怎么定 - 问题",
                "page": 8,
                "total": 20,
                "cards": [
                    {"title": "太死不行", "subtitle": "创意类任务框太死，结果千篇一律"},
                    {"title": "太松不行", "subtitle": "严谨任务框太松，AI 容易放飞自我"},
                    {"title": "真正要的", "subtitle": "结果稳定 + 留有调整空间"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "边界怎么定 - 原因",
                "page": 9,
                "total": 20,
                "cards": [
                    {"title": "无法一次定准", "subtitle": "准备得再充分，也会遇到没想到的情况"},
                    {"title": "AI 不主动提醒", "subtitle": "规则不合理，AI 也照着做"},
                    {"title": "持续校准", "subtitle": "边界不是一次性设计，是不断校准的过程"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "边界怎么定 - 解决方式",
                "page": 10,
                "total": 20,
                "cards": [
                    {"title": "硬约束划范围", "subtitle": "必须保持一致的内容先定好"},
                    {"title": "从 MVP 开始", "subtitle": "先跑基础结构，再边跑边调"},
                    {"title": "人来拍板", "subtitle": "人工调边界，AI 在边界内做事"},
                ]
            }
        },
        {
            "layout_id": "cards-left-1-right-2",
            "theme": "tech",
            "data": {
                "title": "边界怎么定 - 案例",
                "page": 11,
                "total": 20,
                "leftCards": [
                    {"title": "问题", "subtitle": "组件模板写死，内容换了样式也差不多"},
                ],
                "rightCards": [
                    {"title": "解决", "subtitle": "从 MVP 一点点放开，多轮迭代"},
                    {"title": "效果", "subtitle": "用户提建议，AI 能改更多属性"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "效率怎么提 - 问题",
                "page": 12,
                "total": 20,
                "cards": [
                    {"title": "AI 当打字机", "subtitle": "需要反馈后继续改的任务，纯文字描述效率低"},
                    {"title": "原地打转", "subtitle": "十几轮对话都不一定能解决一个问题"},
                    {"title": "验证缺失", "subtitle": "AI 看不见结果，人也看不见推理过程"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "效率怎么提 - 原因",
                "page": 13,
                "total": 20,
                "cards": [
                    {"title": "无验证回路", "subtitle": "没有高效反馈机制"},
                    {"title": "细节丢失", "subtitle": "两个人隔着文字来回转述"},
                    {"title": "能力受限", "subtitle": "纯文字模型天然做不了视觉任务"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "效率怎么提 - 解决方式",
                "page": 14,
                "total": 20,
                "cards": [
                    {"title": "建立验证回路", "subtitle": "生成 → 可视化验证 → 反馈 → 修正"},
                    {"title": "视觉任务用识图模型", "subtitle": "AI 直接看图，不靠文字描述"},
                    {"title": "核心", "subtitle": "AI 不只生成内容，还能看图、读文件"},
                ]
            }
        },
        {
            "layout_id": "cards-left-1-right-2",
            "theme": "tech",
            "data": {
                "title": "效率怎么提 - 案例",
                "page": 15,
                "total": 20,
                "leftCards": [
                    {"title": "问题", "subtitle": "安全字数上限难校准，反复口头反馈"},
                ],
                "rightCards": [
                    {"title": "解决", "subtitle": "AI 生成后直接看图反馈"},
                    {"title": "效果", "subtitle": "一次调整就能处理"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "版本怎么管 - 问题",
                "page": 16,
                "total": 20,
                "cards": [
                    {"title": "AI 不主动 commit", "subtitle": "你不提，它就不做"},
                    {"title": "过程无存档", "subtitle": "出问题只能从头来"},
                    {"title": "影响很大", "subtitle": "协作过程没有存档点"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "版本怎么管 - 原因",
                "page": 17,
                "total": 20,
                "cards": [
                    {"title": "无保存点概念", "subtitle": "工作流本身没有存档机制"},
                    {"title": "上下文压缩", "subtitle": "前面说过的，后面可能忘掉"},
                    {"title": "习惯缺失", "subtitle": "人自己不重视，AI 更不会坚持"},
                ]
            }
        },
        {
            "layout_id": "content-col",
            "theme": "tech",
            "data": {
                "title": "版本怎么管 - 解决方式",
                "page": 18,
                "total": 20,
                "cards": [
                    {"title": "建立可恢复性机制", "subtitle": "每个阶段结尾建立存档点"},
                    {"title": "系统提示词规范", "subtitle": "帮 AI，也帮自己记住该做的事"},
                    {"title": "核心", "subtitle": "不是“记得 commit”，而是让过程可恢复"},
                ]
            }
        },
        {
            "layout_id": "cards-left-1-right-2",
            "theme": "tech",
            "data": {
                "title": "版本怎么管 - 案例",
                "page": 19,
                "total": 20,
                "leftCards": [
                    {"title": "问题", "subtitle": "误删文件，整个开发目录没了"},
                ],
                "rightCards": [
                    {"title": "解决", "subtitle": "每个阶段建立存档点（commit + 文档）"},
                    {"title": "坚持", "subtitle": "先改文档，再改代码"},
                ]
            }
        },
        {
            "layout_id": "ending",
            "theme": "tech",
            "data": {
                "title": "谢谢观看",
                "page": 20,
                "total": 20
            }
        },
    ]

    for i, slide in enumerate(slides):
        layout_id = slide["layout_id"]
        theme_id = slide["theme"]
        data = dict(slide["data"])
        if layout_id == "content-col" and isinstance(data.get("items"), list):
            data["items"] = normalize_content_col_items(data["items"])

        layout = ds["layouts"].get(layout_id)
        theme = ds["themes"].get(theme_id)

        if not layout:
            print(f"Layout not found: {layout_id}")
            continue
        if not theme:
            print(f"Theme not found: {theme_id}")
            continue

        html = build_html_file(layout_id, layout, theme, data, presentation_defaults)

        filename = f"slide-{i+1:02d}-{layout_id}.html"
        filepath = SLIDES_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {filename}")

    print(f"\nDone! {len(slides)} slides generated to {SLIDES_DIR}/")


if __name__ == "__main__":
    main()
