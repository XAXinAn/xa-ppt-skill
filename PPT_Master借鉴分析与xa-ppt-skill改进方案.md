# PPT Master 借鉴分析与 xa-ppt-skill 改进方案

> 用途：本文用于向后续 GPT / Agent 说明 PPT Master 与当前 xa-ppt-skill 的关系、当前生成质量问题，以及建议的改进路线。
>
> 结论先行：两者在输入层都支持“自然语言需求 + 可选参考资料”。PPT Master 真正值得借鉴的，不是重新定义输入，而是它在页面表达、整套 deck 质量、阶段质量门、产物追踪和恢复机制上的工程化做法。

---

## 1. 两个项目的定位

### 1.1 当前 xa-ppt-skill

当前项目的核心路线是：

```text
自然语言 / 参考资料
        ↓
AI 理解需求、生成大纲
        ↓
用户确认大纲
        ↓
选择主题与布局
        ↓
presentation-content.json
        ↓
HTML 页面
        ↓
Playwright 截图
        ↓
PNG 图片嵌入 PPTX
```

当前技术定位是：

> 通过组件—布局—主题设计系统，生成视觉稳定的图片嵌入式 PPT。

主要文件：

- `.claude/skills/xa-ppt/skill.md`：AI 工作流和页面生成规则；
- `design-system/design-system.json`：设计系统主配置；
- `design-system/themes/`：主题；
- `design-system/layouts/`：布局；
- `presentation-content.json`：AI 生成的页面级中间产物；
- `src/generate_html.py`：根据页面数据生成 HTML；
- `src/render.py`：使用 Playwright 渲染 PNG；
- `src/build_pptx.py`：将 PNG 组装为 PPTX；
- `scripts/validate_design_system.py`：设计系统配置校验。

### 1.2 PPT Master

PPT Master 的默认路线是：

```text
自然语言 / 参考资料 / 可选模板
        ↓
源材料转换与事实提取
        ↓
Strategist：叙事、页面结构、设计规划
        ↓
design_spec.md + spec_lock.md
        ↓
Executor：逐页生成 SVG
        ↓
SVG 质量检查与视觉审阅
        ↓
SVG → DrawingML / 原生 PPTX
        ↓
备注、旁白、动画、转场等后处理
        ↓
最终 PPTX
```

PPT Master 的核心定位是：

> 从资料或主题生成原生可编辑 PowerPoint，同时管理模板、素材、视觉审阅、PPTX 原生增强和交付质量。

### 1.3 两者的共同点

两者输入层没有本质差异：

- 都接受自然语言需求；
- 都可以接受参考资料；
- 都由 AI 负责需求理解、内容规划和页面设计；
- 都需要先规划页面，再执行生成；
- 都需要渲染和视觉审阅；
- 最终都输出 PPTX。

真正的差异发生在输入之后：

| 维度 | xa-ppt-skill | PPT Master |
|---|---|---|
| 页面中间语言 | HTML/CSS | 受约束 SVG |
| 最终 PPT 对象 | 整页 PNG 图片 | DrawingML 原生文字、形状、图表等 |
| 设计系统 | Theme → Layout → Component | Brand / Layout / Deck / Chart / Icon |
| 规划合同 | 需求文档 + presentation-content.json | design_spec.md + spec_lock.md |
| 输出生命周期 | 固定 output 目录 | sources / analysis / output / validation / exports / backup |
| 质量检查 | 设计系统校验为主 | 设计、页面、图表、视觉、PPTX package 多级校验 |
| 已有 PPTX | 当前主要支持重新生成 | 明确区分 Generate / Fill / Enhance / Create Template |
| 旁白和动画 | 当前较少 | 独立 sidecar 和 PPTX 后处理 |

---

## 2. 当前 xa-ppt-skill 的优点

以下内容应该保留，不应因为借鉴 PPT Master 而推翻：

### 2.1 设计系统已经有统一入口

`design-system/design-system.json` 已经集中管理：

- 主题和主题匹配规则；
- 布局注册表；
- 画布尺寸；
- 字号系统；
- 卡片 padding 和圆角；
- 对齐规则；
- 渲染默认值；
- guardrails；
- regressionRules。

这是正确的“单一配置来源”方向。

### 2.2 AI 和 Python 的职责已经分开

当前规则已经把职责拆为：

```text
AI：需求理解、大纲、主题、布局、页面内容、HTML
Python：HTML 生成、截图、PPTX 组装
```

这个边界清楚，适合继续发展。

### 2.3 已经有大纲确认机制

当前 `skill.md` 已经规定：

```text
AI 生成大纲 → 用户确认 → 生成 HTML
```

这比直接一次性生成整份 PPT 更可靠，应该进一步强化为“页面 roster 锁定”。

### 2.4 已经有设计系统回流意识

当前文档已经规定：

- 字号问题回流到 typography；
- 间距问题回流到 componentDefaults；
- 白边问题回流到 screenshotTarget；
- 对齐问题回流到 alignment；
- 不只在单页临时修复。

这与 PPT Master 的“方法级问题应修复权威规则”理念一致。

### 2.5 当前视觉风格具有稳定性

当前生成结果整体表现为：

- 深色科技主题一致；
- 标题、页码、卡片边界稳定；
- 页面尺寸和截图边界明确；
- 表格、目录、时间线等基础结构可用；
- 不容易出现严重错位。

当前主要问题不是基础排版失败，而是“整套 deck 的表达质量和变化不足”。

---

## 3. 从生成质量角度看，当前主要问题

当前输出总览位于：

```text
E:\develop\xa-ppt-skill\output\contact-sheet.png
```

从整套页面观察，当前主要问题有以下几类。

### 3.1 页面结构重复

大量页面使用 `content-col`：

```text
标题
副标题
若干纵向卡片
页码
```

单页看没有明显错误，但连续多页会形成“统一模板页面堆叠”的感觉。

问题不是布局不好，而是：

> 复杂内容没有被转换成更适合它的视觉结构。

例如：

- 对比内容仍然使用普通卡片；
- 流程内容没有转换为流程图；
- 层级关系没有转换为架构图；
- 数字结论没有使用 KPI 或图表；
- 核心观点没有使用大字页或视觉锚点。

### 3.2 内容仍然偏文字卡片化

当前设计系统已经有 card、table、timeline，但多数内容仍然通过文字卡片表达。

这会让 PPT 更像“结构化文档”，而不是“演示文稿”。

高质量演示文稿通常需要：

- 先给结论，再给证据；
- 用图示表达关系；
- 用数字表达规模或变化；
- 用对比表达差异；
- 用时间线表达过程；
- 用图片、引用或大字页形成节奏变化。

### 3.3 缺少页面级表达目标

当前页面数据主要描述“放哪些内容”，还没有明确描述：

- 这一页的任务是什么；
- 观众看完应该记住什么；
- 应该突出什么；
- 为什么选择这个布局；
- 这一页和前后页是什么关系。

### 3.4 缺少整套 deck 级质量检查

当前 `scripts/validate_design_system.py` 已经可以检查设计系统配置，但还没有系统检查：

- 同一布局是否连续出现过多次；
- 页面整体是否过于重复；
- 是否存在连续纯文字页；
- 是否存在连续表格页；
- 页面密度是否有变化；
- 是否形成章节节奏；
- 是否有明确的视觉高潮和总结。

### 3.5 质量规则主要是配置级，而不是内容级

当前已能检查：

- 字号；
- 画布；
- padding；
- 对齐；
- 截图目标。

但还缺少：

- 字符数；
- 行数；
- 卡片数量；
- 标题长度；
- 文字溢出；
- 页面视觉占用率；
- 视觉锚点；
- 布局和内容类型是否匹配。

---

## 4. PPT Master 对 PPT 质量最值得借鉴的原则

## 4.1 页面应该服务于表达任务

不能只问：

```text
这一页使用哪个 layout？
```

还应该问：

```text
这一页要让观众在 5 秒内理解什么？
哪种视觉形式最适合表达这个观点？
```

建议为每页增加：

```json
{
  "purpose": "这一页在整套 PPT 中的任务",
  "takeaway": "观众看完后应该记住的结论",
  "visual_mode": "comparison",
  "density": "medium",
  "emphasis": ["核心词一", "核心词二"]
}
```

这些字段不会改变 `presentation-content.json` 作为中间产物的定位，只是让页面执行数据更完整。

## 4.2 按内容形状选择视觉形式

建议把内容类型与页面类型建立更明确的映射：

| 内容形状 | 推荐视觉形式 |
|---|---|
| 3–5 个并列概念 | 卡片、横向列表、图标网格 |
| A/B 差异 | Comparison 双栏、左右对照 |
| 按时间发生的事件 | Timeline |
| 有顺序的步骤 | Process、Numbered Steps、Pipeline |
| 层级关系 | Layered Architecture、Tree |
| 中心向外扩散 | Hub-Spoke、Mind Map |
| 数字和指标 | KPI、Chart、Data Story |
| 复杂关系 | Relationship Diagram、Network |
| 单一核心观点 | Hero Statement、Quote |
| 人物或案例 | Image + Text、Profile Cards |
| 高密度事实 | Table、Data Story |

“有 4 个要点”不应该自动等于“4 张普通卡片”。

## 4.3 页面需要视觉锚点

除封面、目录、结尾和纯引用页外，正文页至少应有一个视觉锚点：

- 大数字；
- 流程线；
- 对比结构；
- 时间轴；
- 架构图；
- 图片；
- 图表；
- 高亮结论；
- 独特构图。

视觉锚点的作用是让观众先看到结构，再阅读文字。

## 4.4 需要管理整套 PPT 的节奏

建议建立 deck-level 规则：

```text
同一布局连续不超过 2–3 页
连续页面避免完全相同的卡片结构
每个章节至少有一个视觉变化页
每 3–5 页至少出现一次数据、对比、流程、图片或大字观点
```

这不是强制所有 PPT 套固定模板，而是避免：

```text
标题 + 四张卡片
标题 + 四张卡片
标题 + 四张卡片
标题 + 四张卡片
```

## 4.5 先删内容和换表达，再缩小字号

内容超载时的优先级应该是：

```text
删除次要内容
→ 拆页
→ 换布局
→ 改成图示
→ 最后才缩小字号
```

内容不足时，也不应该简单增加空卡片，而可以改为：

- 一个大观点；
- 一个大数字；
- 一张引用页；
- 一个简洁流程；
- 一张图片；
- 一个章节过渡页。

---

## 5. 建议增加的页面表达类型

当前已有 `cover`、`ending`、`toc`、`content-row`、`content-col`、卡片组合、网格、时间线和表格。

不建议一次性增加几十个布局，建议优先增加以下 8 类高价值表达：

本轮 P1 优先先补三类最容易提升整套 deck 观感的页面：

1. `comparison`：A/B 对比、改进前后、传统与新方案；
2. `hero-statement`：核心观点、章节结论、必须记住的一句话；
3. `process`：步骤、流程、管线、方法论。

### 5.1 Hero Statement

用于核心观点或章节结论：

```text
真正的问题不是 AI 不够聪明，
而是协作过程没有被定义。
```

### 5.2 Comparison

用于传统与改进、A 与 B、问题与方案：

```text
传统方式        改进方式
口头沟通        文档化契约
一次性生成      分阶段验证
无法恢复        有存档点
```

### 5.3 KPI / Data Story

用于强调数字和指标：

```text
93%
审批通过率

但高通过率并不代表低风险
```

### 5.4 Process / Pipeline

用于表达步骤和方法：

```text
定义 → 规划 → 生成 → 检查 → 修正 → 留痕
```

### 5.5 Architecture / Layered Structure

用于技术架构和层级关系：

```text
应用层
服务层
数据层
基础设施层
```

### 5.6 Image + Text Split

用于人物、案例、品牌和产品介绍：

```text
左侧大图
右侧核心结论 + 三条事实
```

### 5.7 Quote / Statement

用于观点、用户原话和具有情绪的内容。

### 5.8 Chart Insight

图表不只是展示数据，还要同时给出明确结论：

```text
图表 + 一句结论 + 一个关键标记
```

---

## 6. xa-ppt-skill 的具体改进方案

## 6.1 P0：保留现有技术路线，先提升稳定性和质量

这一阶段不改变：

```text
HTML → PNG → 图片型 PPTX
```

### 本次优先落地的三项

为了先把当前链路做稳，本次实现优先覆盖下面三项：

1. `presentation-content.json` 校验：先把顶层结构、页面编号、布局存在性和布局约束校验起来；
2. deck 重复检查：先抓连续重复布局、content-col 过度集中和明显的页面结构单一化；
3. manifest：先把每次生成的输入、输出和摘要信息固定下来，方便追踪和回溯。

### P0-1：扩展页面中间数据

在 `presentation-content.json` 的每页增加：

```json
{
  "page": 4,
  "layout_id": "comparison",
  "theme": "tech",
  "purpose": "说明两种协作方式的差异",
  "takeaway": "AI 协作需要明确的验证机制",
  "visual_mode": "comparison",
  "density": "medium",
  "emphasis": ["验证机制"],
  "data": {}
}
```

### P0-2：增加页面内容校验

新增：

```text
schemas/presentation-content.schema.json
scripts/validate_presentation_content.py
```

至少检查：

- `layout_id` 是否存在；
- `theme` 是否存在；
- `data` 是否为对象；
- 页面编号是否连续；
- 页面总数是否一致；
- 卡片数量是否满足布局约束；
- 表格列数是否一致；
- 标题是否为空；
- 文字是否超过安全长度。

### P0-3：增加 deck-level 质量检查

新增：

```text
scripts/review_deck_quality.py
```

检查：

- 同一布局连续出现次数；
- 各布局使用比例；
- 连续纯文字页；
- 连续表格页；
- 每页字符数量；
- 每页卡片数量；
- 视觉模式是否有变化；
- 是否存在视觉锚点；
- 章节之间是否有节奏变化。

建议规则：

```text
同一布局连续超过 3 页：警告
content-col 占全 deck 超过 60%：警告
连续两页 layout 和结构完全相同：警告
正文页没有 visual_mode：警告
正文页没有视觉锚点：警告
```

### P0-4：完善渲染质量检查

修改 `src/render.py`，增加：

- 单次运行复用一个浏览器实例；
- 等待字体加载完成；
- 等待图片加载完成；
- 每页截图状态记录；
- PNG 尺寸检查；
- 空白页检查；
- 页面边界检查。

### P0-5：增加 PPTX 交付检查

新增：

```text
scripts/validate_pptx.py
```

检查：

- PPTX 是否能够重新打开；
- 页数是否正确；
- 每页是否存在图片；
- 图片是否铺满页面；
- PPTX 文件是否为空或异常；
- 图片数量是否与页面数量一致。

### P0-6：解决文档和实现的双重事实来源

当前 `skill.md` 内部包含大量布局说明，而真实布局又位于 `design-system/layouts/`。

建议：

```text
skill.md
只负责 AI 工作流、硬规则和执行顺序

 design-system.json
负责设计系统主配置

layouts/*.json
负责布局 HTML、CSS、字段约束

docs/*.md
负责说明和示例
```

布局清单应由 JSON 作为唯一事实来源，避免“文档写 20 种、实际注册 21 种”这类漂移。

### P0-7：增加 HTML 内容转义

`src/generate_html.py` 当前通过字符串替换写入 HTML。普通文本字段应默认进行 HTML 转义，避免参考资料中的 `<`、`&` 或 HTML 片段破坏页面。

建议区分：

```text
text 字段：自动转义
trusted_html 字段：显式允许 HTML
```

---

## 6.2 P1：增强 deck 级视觉质量

### P1-1：增加 Contact Sheet 自动生成

新增：

```text
scripts/generate_contact_sheet.py
```

统一生成整套 PPT 总览，用于检查：

- 页面重复；
- 色彩一致性；
- 页面密度；
- 标题变化；
- 章节节奏；
- 空白页和异常页。

### P1-2：增加资源清单

如果开始正式使用图片、图标和图表，可以增加：

```text
assets/
├── images/
├── icons/
└── assets-manifest.json
```

记录：

- 素材来源；
- 素材用途；
- 图片比例；
- 是否已经准备完成；
- 是否重复使用；
- 版权或出处。

### P1-3：完善图片和图示布局

不要求一开始复制 PPT Master 的全部图片后端和图标库，而是先增加明确的图片角色：

- hero image；
- background image；
- case image；
- portrait；
- diagram image；
- decorative image。

图片必须服务于页面观点，而不是只用作装饰。

### P1-4：增加 Speaker Notes

把备注独立保存：

```text
notes/
├── slide-01.md
├── slide-02.md
└── slide-03.md
```

再在 PPTX 输出阶段写入 PowerPoint 备注。

### P1-5：增加运行快照和恢复

建议为每次生成保存：

```text
output/runs/<run_id>/
├── input-snapshot/
├── presentation-content.json
├── slides/
├── images/
├── validation/
└── presentation.pptx
```

记录每个阶段：

```json
{
  "stages": {
    "content": "passed",
    "html": "passed",
    "render": "failed",
    "pptx": "pending"
  }
}
```

恢复时只从失败阶段继续。

---

## 6.3 P2：模板和品牌复用

当前的：

```text
themes/
layouts/
```

可以在实际出现企业复用需求后升级为：

```text
design-system/
├── brands/
├── layouts/
├── decks/
└── components/
```

职责分别是：

- Brand：颜色、字体、Logo、身份；
- Layout：品牌无关的页面结构；
- Deck：季度汇报、技术分享、产品发布等固定场景；
- Component：卡片、时间线、代码块、引用、架构节点等。

模板应显式指定，不要根据品牌名或风格描述模糊匹配本地模板。

---

## 6.4 P3：原生或混合式 PPTX

只有当产品目标从“视觉稳定的图片型 PPT”升级为“PowerPoint 中可编辑的 PPT”时，才进入这一阶段。

建议提供三种模式：

```text
image   HTML → PNG → PPTX，当前稳定路线
native  结构化内容 → 原生文字、形状、表格、图表
hybrid  文字和结构原生，复杂背景和装饰保留图片
```

优先原生化：

1. 标题；
2. 正文；
3. 卡片矩形；
4. 表格；
5. 简单图表；
6. 页码和页脚。

不建议一开始直接复制 PPT Master 的完整 SVG → DrawingML 管线。

---

## 7. 推荐的目标流水线

在保留当前技术路线的前提下，目标流程可以是：

```text
自然语言 / 参考资料
        ↓
AI 需求理解、大纲和设计分析
        ↓
用户确认页面 roster
        ↓
presentation-content.json
        ↓
内容 Schema 校验
        ↓
语义布局校验
        ↓
HTML 页面生成
        ↓
HTML 和内容密度校验
        ↓
Playwright 批量渲染
        ↓
PNG 尺寸、空白和边界检查
        ↓
Contact Sheet 视觉审阅
        ↓
PPTX 组装
        ↓
PPTX 交付检查
        ↓
最终 exports/
```

每次运行同时产生：

```text
manifest.json
validation/
backup/
```

一键执行建议优先使用：

```bash
python scripts/run_pipeline.py --allow-warn
```

如果希望 warning 直接中止流程，使用：

```bash
python scripts/run_pipeline.py --stop-on-warn
```

---

## 8. 推荐的实施顺序

### 第一阶段：稳定当前链路

优先实现：

1. `presentation-content.json` schema；
2. 页面内容校验；
3. deck-level 重复布局检查；
4. manifest；
5. HTML/PNG/PPTX 交付检查；
6. Playwright 单浏览器批量渲染；
7. 文本 HTML 转义；
8. `skill.md` 和 JSON 的单一事实来源。

### 第二阶段：提升视觉表达

再实现：

1. Hero Statement；
2. Comparison；
3. KPI / Data Story；
4. Process / Pipeline；
5. Architecture；
6. Image + Text；
7. Quote；
8. Chart Insight；
9. Contact Sheet 自动审阅；
10. 视觉锚点和页面节奏规则。

### 第三阶段：增强复用能力

之后再考虑：

1. Brand / Layout / Deck；
2. 图片和图标资源 manifest；
3. Speaker Notes；
4. 运行快照和恢复；
5. 多画布格式。

### 第四阶段：增强可编辑性

最后再评估：

1. 原生文字；
2. 原生形状；
3. 原生表格；
4. 原生图表；
5. 混合式 PPTX；
6. 已有 PPTX 填充和增强。

---

## 9. 不建议直接照搬 PPT Master 的部分

### 9.1 不要立即切换 SVG

当前 HTML/CSS 路线已经具备稳定性和视觉表达能力，直接切换 SVG 会引入较高转换成本。

### 9.2 不要一开始复制完整资源库

11,600+ 图标、76 个图表模板和大量示例并不是当前质量瓶颈。

当前优先级是：

```text
页面表达正确
→ 页面节奏合理
→ 质量可检查
→ 失败可恢复
```

### 9.3 不要一开始实现所有 PPTX 路线

先把新建图片型 PPT 做稳，再根据真实需求增加：

- Fill Native PPTX；
- Enhance Native PPTX；
- Create Template。

### 9.4 不要把所有规则塞进 skill.md

推荐保持：

```text
skill.md              AI 流程和硬规则
设计系统 JSON          配置和注册
layouts/*.json        布局实现
schemas/*.json        数据约束
scripts/*.py          执行与检查
docs/*.md             原理说明
```

---

## 10. 给后续 GPT / Agent 的执行要求

后续 GPT 处理本项目时，应遵循以下判断：

1. 不要把 `presentation-content.json` 当成用户原始输入，它是 AI 规划后的中间执行产物；
2. 不要因为参考 PPT Master 就立即把 HTML 流程改成 SVG；
3. 首先提升页面表达质量、整套 deck 节奏和质量检查；
4. 任何视觉问题优先判断是单页问题还是设计系统问题；
5. 同类页面连续重复时，应优先调整页面表达形式，而不是继续套 `content-col`；
6. 页面必须有明确的 `purpose`、`takeaway` 和 `visual_mode`；
7. 正文页应尽量具备视觉锚点；
8. 内容超载时先删减、拆页或换图示，最后才缩小字号；
9. 布局实现的唯一事实来源是 `design-system/layouts/` 和 `design-system.json`；
10. 生成前后都应该保留可验证、可恢复的运行状态。

---

## 11. 最终结论

PPT Master 对 xa-ppt-skill 的最大质量借鉴意义，不是“生成更多页面”或“使用更复杂技术”，而是：

> 让每一页有明确表达任务，让整套 PPT 有视觉节奏，让质量问题可以被检查和修复。

当前最推荐的改进方向是：

```text
保留：HTML → PNG → 图片型 PPTX

增强：
页面表达目标
→ 语义化布局选择
→ 视觉锚点
→ 页面节奏
→ 内容密度控制
→ deck-level 视觉审阅
→ 可追踪和可恢复的生成状态
```

这样可以在不推翻当前技术路线的前提下，把 xa-ppt-skill 从“能生成 PPT”提升为“能稳定生成质量更高的演示文稿系统”。
