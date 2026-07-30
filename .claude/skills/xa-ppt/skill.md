# xa-ppt-skill

通过自然语言生成图片嵌入式 PPT。AI 负责理解需求、生成大纲、选择布局、匹配主题、生成 HTML；Python 脚本负责渲染截图和组装 PPT。

---

## 工作流程

```
用户描述需求（自然语言）
       │
       ▼
AI 生成结构化大纲 → 用户确认
       │
       ▼
AI 选择布局 + 匹配主题
       │
       ▼
AI 生成 HTML（每页一个文件）
       │
       ▼
Python 脚本截图 → 组装 PPT
       │
       ▼
输出 .pptx
```

当前这份页面级中间规格文件的主名是 `deck-spec.json`，旧名 `presentation-content.json` 只作为兼容别名保留给脚本回退使用。

### 第一步：理解需求，生成大纲

用户说"做一个微服务架构的技术分享 PPT"，AI 需要：

1. 提取主题：技术分享 → 主题 `tech`
2. 识别内容结构：概述、对比、核心组件、总结
3. 生成大纲，每页包含：
   - 布局建议
   - 内容要点
   - 页码

**示例大纲：**
```json
{
  "title": "微服务架构技术分享",
  "theme": "tech",
  "slides": [
    { "page": 1, "layout": "cover", "title": "微服务架构", "subtitle": "技术分享" },
    { "page": 2, "layout": "toc", "title": "目录", "items": ["概述", "架构对比", "核心组件", "部署策略"] },
    { "page": 3, "layout": "content-col", "title": "什么是微服务", "content": ["服务拆分原则", "独立部署", "故障隔离"] },
    { "page": 4, "layout": "cards-left-1-right-2", "title": "架构对比", "left": ["单体部署"], "right": ["微服务", "云原生"] },
    { "page": 5, "layout": "grid-cols-2", "title": "核心组件", "cards": ["服务拆分", "API网关", "服务通信", "容器化"] },
    { "page": 6, "layout": "timeline", "title": "技术演进", "nodes": ["单体时代", "微服务", "云原生"] },
    { "page": 7, "layout": "ending", "title": "谢谢观看" }
  ]
}
```

**重要：必须先让用户确认大纲后再生成 HTML。**

### 第二步：选择布局

根据内容结构选择布局：

| 内容结构 | 推荐布局 |
|----------|----------|
| 封面 | `cover` |
| 结尾 | `ending` |
| 目录 | `toc` |
| 横向单行要点 | `content-row` |
| 纵向单列要点 | `content-col` |
| A/B 对比、传统 vs 改进 | `comparison` |
| 核心观点、章节结论 | `hero-statement` |
| 流程、步骤、管线 | `process` |
| 上下分栏对比 | `cards-top-*-bottom-*` |
| 左右分栏对比 | `cards-left-*-right-*` |
| 2×2 网格 | `grid-cols-2` |
| 3×2 网格 | `grid-cols-3` |
| 时间线 | `timeline` |
| 表格 | `table` |

当内容明显是在讲“对比、结论、流程”时，优先用这些专用布局，不要继续把它们压进 `content-col`。

### 本次回流约定（必须遵守）

1. 需要表达对比、方法、结论、案例时，优先 `comparison`、`process`、`hero-statement`、`table`，不要为了省事继续压进 `content-col`。
2. 卡片、面板、流程卡这类布局，内部文字必须保持垂直居中，卡片主体要吃满所在容器，文字仍然左对齐。
3. 表格必须占满正文区域，`table-shell`、`table`、`tbody`、`tr` 要形成完整的伸展链路，不能只缩在上半部分。
4. `hero-statement` 不是固定三段式，长标题优先通过放宽宽度解决，不要第一反应就缩字号或强行拆更多行。
5. 生成结束后如果出现 `output/images/resources` 之类的临时资源缓存，必须清理掉，它们不是交付产物。

### 本次回流复盘

这次暴露出来的核心问题，不是“组件不够多”，而是“布局约束和内容类型没有绑定好”。如果把不同类型的内容都塞进同一套固定格子里，最终就会变成看起来都差不多，稍微加长一点又容易溢出。

后续默认遵守这三个判断：

1. 先判断这页是在讲对比、流程、结论、表格还是案例，再决定是不是该直接用专用布局。
2. 容器边界可以固定，但容器内部不能写死成单一填充模板；正文区域允许在设计系统约束内调整宽度、行数和对齐。
3. 任何页面只要出现卡片偏上、表格缩在上方、hero 过早换行、临时资源残留，都视为需要回滚检查的信号，不允许靠临时补丁“糊过去”。

### 第三步：匹配主题

根据内容语义匹配合适的主题：

| 关键词 | 主题 |
|--------|------|
| 技术、架构、代码、开发、AI、服务器、网络、微服务、容器 | `tech` |
| 商务、汇报、介绍、计划、总结、年度 | `simple` |
| 极简、纯展示、艺术 | `minimal` |
| 默认 | `simple` |

---

## 布局详解（20种）

所有布局的 HTML 结构相同，差异仅在 CSS 类名和内容结构。

### HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{布局ID} 布局预览</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    :root {
      --bg: #FFFFFF;
      --title: #1A1A1A;
      --text: #4A4A4A;
      --accent: #0066CC;
      --muted: #999999;
      --surface: #F5F5F5;
    }

    body {
      font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
      background: #f0f0f0;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px;
    }

    h2 {
      color: #333;
      margin-bottom: 20px;
      font-size: 24px;
    }

    .slide-preview {
      width: 640px;
      height: 360px;
      border: 1px solid #ddd;
      overflow: hidden;
    }

    .slide.{layoutClass} {
      background: var(--bg);
      width: 1920px;
      height: 1080px;
      padding: 60px;
      display: flex;
      flex-direction: column;
      transform: scale(0.33);
      transform-origin: top left;
    }
  </style>
</head>
<body>
  <h2>{布局名称}</h2>
  <div class="slide-preview">
    <div class="slide {layoutClass}">
      <!-- 内容 -->
    </div>
  </div>
</body>
</html>
```

---

### 1. cover（封面）

```html
<div class="slide cover">
  <div>
    <h1>微服务架构</h1>
    <h2>技术分享</h2>
  </div>
</div>
```

```css
.slide.cover {
  display: flex;
  align-items: center;
  justify-content: center;
}
.slide.cover h1 {
  font-size: 88px;
  color: var(--title);
  text-align: center;
  font-weight: bold;
}
.slide.cover h2 {
  font-size: 44px;
  color: var(--muted);
  text-align: center;
  margin-top: 24px;
  font-weight: normal;
}
```

---

### 2. ending（结尾）

```html
<div class="slide ending">
  <h1>谢 谢 观 看</h1>
</div>
```

```css
.slide.ending {
  background: var(--bg);
  padding: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.slide.ending h1 {
  font-size: 88px;
  color: var(--title);
  font-weight: bold;
  text-align: center;
}
```

---

### 3. toc（目录）

```html
<div class="slide toc">
  <div class="slide-header">
    <h1>目 录</h1>
  </div>
  <div class="slide-body">
    <div class="line"><span class="num">01</span> 概述</div>
    <div class="line"><span class="num">02</span> 服务拆分</div>
    <div class="line"><span class="num">03</span> API 网关</div>
    <div class="line"><span class="num">04</span> 容器化部署</div>
  </div>
  <div class="slide-footer">1 / 5</div>
</div>
```

```css
.slide.toc {
  background: var(--bg);
  padding: 60px;
  display: flex;
  flex-direction: column;
}
.slide.toc .slide-header {
  height: 80px;
  display: flex;
  align-items: flex-end;
}
.slide.toc .slide-header h1 {
  font-size: 64px;
  color: var(--title);
  border-bottom: 3px solid var(--accent);
  margin: 0;
  width: 100%;
}
.slide.toc .slide-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.slide.toc .slide-body .line {
  flex: 1;
  display: flex;
  align-items: center;
  font-size: 56px;
  color: var(--text);
}
.slide.toc .slide-body .line .num {
  color: var(--accent);
  font-weight: bold;
  width: 100px;
  flex-shrink: 0;
}
.slide.toc .slide-footer {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 20px;
  color: var(--muted);
}
```

---

### 4. content-row（横向正文）

```html
<div class="slide content-row">
  <div class="slide-header">
    <h1>微服务特点</h1>
  </div>
  <div class="slide-body">
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 独立部署</div>
        <div class="sub">各服务独立发布</div>
      </div>
    </div>
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 水平扩展</div>
        <div class="sub">按需扩展服务</div>
      </div>
    </div>
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 技术多样</div>
        <div class="sub">语言/框架可选</div>
      </div>
    </div>
  </div>
  <div class="slide-footer">1 / 5</div>
</div>
```

```css
.slide.content-row {
  background: var(--bg);
  padding: 60px;
  display: flex;
  flex-direction: column;
}
.slide.content-row .slide-header {
  padding-bottom: 20px;
}
.slide.content-row .slide-header h1 {
  font-size: 64px;
  color: var(--title);
  border-bottom: 3px solid var(--accent);
  margin: 0;
  width: 100%;
}
.slide.content-row .slide-body {
  flex: 1;
  display: flex;
  flex-direction: row;
  gap: 40px;
  padding: 20px 0;
}
.slide.content-row .card {
  flex: 1;
  background: var(--surface);
  padding: 24px 30px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.slide.content-row .line {
  display: flex;
  flex-direction: column;
  font-size: 48px;
  color: var(--text);
}
.slide.content-row .line .main {
  display: flex;
  align-items: center;
}
.slide.content-row .line .bullet {
  color: var(--accent);
  width: 50px;
  flex-shrink: 0;
}
.slide.content-row .line .sub {
  font-size: 28px;
  color: var(--muted);
  margin-left: 50px;
  margin-top: 6px;
}
.slide.content-row .slide-footer {
  padding-top: 20px;
  font-size: 20px;
  color: var(--muted);
  text-align: right;
}
```

---

### 5. content-col（纵向正文）

```html
<div class="slide content-col">
  <div class="slide-header">
    <h1>微服务架构概述</h1>
  </div>
  <div class="slide-body">
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 微服务</div>
        <div class="sub">一种分布式架构风格</div>
      </div>
    </div>
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 单体架构</div>
        <div class="sub">传统集中式架构模式</div>
      </div>
    </div>
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 服务拆分</div>
        <div class="sub">按业务领域边界划分</div>
      </div>
    </div>
  </div>
  <div class="slide-footer">1 / 5</div>
</div>
```

```css
.slide.content-col {
  background: var(--bg);
  padding: 60px;
  display: flex;
  flex-direction: column;
}
.slide.content-col .slide-header {
  padding-bottom: 20px;
}
.slide.content-col .slide-header h1 {
  font-size: 64px;
  color: var(--title);
  border-bottom: 3px solid var(--accent);
  margin: 0;
  width: 100%;
}
.slide.content-col .slide-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px 0;
}
.slide.content-col .card {
  background: var(--surface);
  padding: 20px 30px;
  border-radius: 12px;
}
.slide.content-col .line {
  display: flex;
  flex-direction: column;
  font-size: 48px;
  color: var(--text);
}
.slide.content-col .line .main {
  display: flex;
  align-items: center;
}
.slide.content-col .line .bullet {
  color: var(--accent);
  width: 50px;
  flex-shrink: 0;
}
.slide.content-col .line .sub {
  font-size: 28px;
  color: var(--muted);
  margin-left: 50px;
  margin-top: 6px;
}
.slide.content-col .slide-footer {
  padding-top: 20px;
  font-size: 20px;
  color: var(--muted);
  text-align: right;
}
```

---

### 6. cards-top-1-bottom-2（上下卡片 上1下2）

```html
<div class="slide cards">
  <div class="slide-header">
    <h1>架构演进</h1>
  </div>
  <div class="slide-body">
    <div class="row cards-1">
      <div class="card">
        <div class="line">
          <div class="main"><span class="bullet">▸</span> 单体架构</div>
          <div class="sub">传统集中式架构</div>
        </div>
      </div>
    </div>
    <div class="row cards-2">
      <div class="card">
        <div class="line">
          <div class="main"><span class="bullet">▸</span> 微服务</div>
          <div class="sub">分布式架构</div>
        </div>
      </div>
      <div class="card">
        <div class="line">
          <div class="main"><span class="bullet">▸</span> 云原生</div>
          <div class="sub">容器化部署</div>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer">1 / 5</div>
</div>
```

```css
.slide.cards {
  background: var(--bg);
  padding: 60px;
  display: flex;
  flex-direction: column;
}
.slide.cards .slide-header {
  padding-bottom: 20px;
}
.slide.cards .slide-header h1 {
  font-size: 64px;
  color: var(--title);
  border-bottom: 3px solid var(--accent);
  margin: 0;
  width: 100%;
}
.slide.cards .slide-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.slide.cards .card {
  background: var(--surface);
  padding: 20px 30px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
}
.slide.cards .line {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
  font-size: 40px;
  color: var(--text);
}
.slide.cards .line .main {
  display: flex;
  align-items: center;
}
.slide.cards .line .bullet {
  color: var(--accent);
  width: 40px;
  flex-shrink: 0;
}
.slide.cards .line .sub {
  font-size: 24px;
  color: var(--muted);
  margin-left: 40px;
  margin-top: 6px;
}
.slide.cards .slide-footer {
  padding-top: 20px;
  font-size: 20px;
  color: var(--muted);
  text-align: right;
}
.slide.cards .row {
  display: flex;
  gap: 20px;
}
.slide.cards .row.cards-1 {
  flex: 1;
}
.slide.cards .row.cards-2 {
  flex: 1;
}
.slide.cards .row.cards-2 .card {
  width: 50%;
}
```

**关键：`.row` 有 `flex: 1`（填满高度）；多卡片行 `.card` 用 `width: 50%` 而不是 `flex: 1`。**

---

### 7. cards-top-1-bottom-3（上下卡片 上1下3）

和 cards-top-1-bottom-2 结构相同，区别：
- `.row.cards-3 .card { width: 33%; }`
- `.row.cards-3 { flex: 1; }`

---

### 8. cards-top-2-bottom-1（上下卡片 上2下1）

和 cards-top-1-bottom-2 结构相同，区别：
- 第一行 `.row.cards-2 .card { width: 50%; }`
- 第二行 `.row.cards-1 { flex: 1; }`（单卡片行不需要 width）

---

### 9. cards-top-2-bottom-3（上下卡片 上2下3）

和 cards-top-1-bottom-2 结构相同，区别：
- `.row.cards-2 .card { width: 50%; }`
- `.row.cards-3 .card { width: 33%; }`

---

### 10. cards-top-3-bottom-1（上下卡片 上3下1）

和 cards-top-1-bottom-2 结构相同，区别：
- `.row.cards-3 .card { width: 33%; }`
- `.row.cards-1 { flex: 1; }`

---

### 11. cards-top-3-bottom-2（上下卡片 上3下2）

和 cards-top-1-bottom-2 结构相同，区别：
- `.row.cards-3 .card { width: 33%; }`
- `.row.cards-2 .card { width: 50%; }`

---

### 12. cards-left-1-right-2（左右卡片 左1右2）

```html
<div class="slide cards">
  <div class="slide-header">
    <h1>架构对比</h1>
  </div>
  <div class="slide-body">
    <div class="left">
      <div class="card">
        <div class="line">
          <div class="main"><span class="bullet">▸</span> 单体架构</div>
          <div class="sub">传统架构模式</div>
        </div>
      </div>
    </div>
    <div class="right">
      <div class="card">
        <div class="line">
          <div class="main"><span class="bullet">▸</span> 微服务</div>
          <div class="sub">分布式架构</div>
        </div>
      </div>
      <div class="card">
        <div class="line">
          <div class="main"><span class="bullet">▸</span> 云原生</div>
          <div class="sub">容器化部署</div>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer">1 / 5</div>
</div>
```

```css
.slide.cards {
  background: var(--bg);
  padding: 60px;
  display: flex;
  flex-direction: column;
}
.slide.cards .slide-header {
  padding-bottom: 20px;
}
.slide.cards .slide-header h1 {
  font-size: 64px;
  color: var(--title);
  border-bottom: 3px solid var(--accent);
  margin: 0;
  width: 100%;
}
.slide.cards .slide-body {
  flex: 1;
  display: flex;
  gap: 20px;
}
.slide.cards .left,
.slide.cards .right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.slide.cards .card {
  background: var(--surface);
  padding: 20px 30px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1;
  width: 100%;
}
.slide.cards .line {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
  font-size: 32px;
  color: var(--text);
}
.slide.cards .line .main {
  display: flex;
  align-items: center;
}
.slide.cards .line .bullet {
  color: var(--accent);
  width: 32px;
  flex-shrink: 0;
}
.slide.cards .line .sub {
  font-size: 20px;
  color: var(--muted);
  margin-left: 32px;
  margin-top: 4px;
}
.slide.cards .slide-footer {
  padding-top: 20px;
  font-size: 20px;
  color: var(--muted);
  text-align: right;
}
```

**关键：`.left` 和 `.right` 都是 `flex: 1`（各50%宽度）；`.card` 有 `flex: 1` 和 `width: 100%`（填满所在列）。**

---

### 13. cards-left-1-right-3（左右卡片 左1右3）

和 cards-left-1-right-2 结构相同。

---

### 14. cards-left-2-right-1（左右卡片 左2右1）

和 cards-left-1-right-2 结构相同。

---

### 15. cards-left-2-right-3（左右卡片 左2右3）

和 cards-left-1-right-2 结构相同。

---

### 16. cards-left-3-right-1（左右卡片 左3右1）

和 cards-left-1-right-2 结构相同。

---

### 17. cards-left-3-right-2（左右卡片 左3右2）

和 cards-left-1-right-2 结构相同。

---

### 18. grid-cols-2（网格布局 2列2行）

```html
<div class="slide grid cols-2">
  <div class="slide-header">
    <h1>核心组件</h1>
  </div>
  <div class="slide-body">
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 服务拆分</div>
        <div class="sub">按领域划分</div>
      </div>
    </div>
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> API 网关</div>
        <div class="sub">统一入口</div>
      </div>
    </div>
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 服务通信</div>
        <div class="sub">HTTP/gRPC</div>
      </div>
    </div>
    <div class="card">
      <div class="line">
        <div class="main"><span class="bullet">▸</span> 容器化</div>
        <div class="sub">Docker</div>
      </div>
    </div>
  </div>
  <div class="slide-footer">1 / 5</div>
</div>
```

```css
.slide.grid {
  background: var(--bg);
  padding: 60px;
  display: flex;
  flex-direction: column;
}
.slide.grid .slide-header {
  padding-bottom: 20px;
}
.slide.grid .slide-header h1 {
  font-size: 64px;
  color: var(--title);
  border-bottom: 3px solid var(--accent);
  margin: 0;
  width: 100%;
}
.slide.grid .slide-body {
  flex: 1;
  display: grid;
  gap: 40px;
  padding: 20px 0;
}
.slide.grid.cols-2 {
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
}
.slide.grid.cols-3 {
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
}
.slide.grid .card {
  background: var(--surface);
  padding: 24px 30px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.slide.grid .line {
  display: flex;
  flex-direction: column;
  font-size: 48px;
  color: var(--text);
}
.slide.grid .line .main {
  display: flex;
  align-items: center;
}
.slide.grid .line .bullet {
  color: var(--accent);
  width: 50px;
  flex-shrink: 0;
}
.slide.grid .line .sub {
  font-size: 28px;
  color: var(--muted);
  margin-left: 50px;
  margin-top: 6px;
}
.slide.grid .slide-footer {
  padding-top: 20px;
  font-size: 20px;
  color: var(--muted);
  text-align: right;
}
```

---

### 19. grid-cols-3（网格布局 3列2行）

和 grid-cols-2 结构相同，区别是 `.slide-body` 用 `cols-3` 类。

---

### 20. timeline（时间线）

```html
<div class="slide timeline">
  <div class="slide-header">
    <h1>技术演进</h1>
  </div>
  <div class="slide-body">
    <div class="timeline-container">
      <div class="node">
        <div class="node-dot"></div>
        <div class="node-title">单体时代</div>
        <div class="node-desc">集中式架构</div>
      </div>
      <div class="node">
        <div class="node-dot"></div>
        <div class="node-title">微服务</div>
        <div class="node-desc">分布式部署</div>
      </div>
      <div class="node">
        <div class="node-dot"></div>
        <div class="node-title">云原生</div>
        <div class="node-desc">容器化编排</div>
      </div>
    </div>
  </div>
  <div class="slide-footer">1 / 5</div>
</div>
```

```css
.slide.timeline {
  background: var(--bg);
  padding: 60px;
  display: flex;
  flex-direction: column;
}
.slide.timeline .slide-header {
  padding-bottom: 20px;
}
.slide.timeline .slide-header h1 {
  font-size: 64px;
  color: var(--title);
  border-bottom: 3px solid var(--accent);
  margin: 0;
  width: 100%;
}
.slide.timeline .slide-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px 0;
}
.slide.timeline .timeline-container {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 0 5%;
  position: relative;
}
.slide.timeline .timeline-container::before {
  content: "";
  position: absolute;
  top: 36px;
  left: 5%;
  right: 5%;
  height: 4px;
  background: var(--accent);
  z-index: 0;
}
.slide.timeline .node {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 25%;
  position: relative;
  z-index: 1;
}
.slide.timeline .node-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent);
  margin-bottom: 24px;
}
.slide.timeline .node-title {
  font-size: 48px;
  color: var(--title);
  font-weight: bold;
  margin-bottom: 12px;
}
.slide.timeline .node-desc {
  font-size: 28px;
  color: var(--muted);
}
.slide.timeline .slide-footer {
  padding-top: 20px;
  font-size: 20px;
  color: var(--muted);
  text-align: right;
}
```

---

### 21. table（表格）

```html
<div class="slide table">
  <div class="slide-header">
    <h1>架构对比</h1>
  </div>
  <div class="slide-body">
    <table>
      <tr>
        <th>名称</th>
        <th>微服务</th>
        <th>单体</th>
        <th>说明</th>
      </tr>
      <tr>
        <td>部署方式</td>
        <td>独立部署</td>
        <td>统一部署</td>
        <td>-</td>
      </tr>
      <tr>
        <td>扩展方式</td>
        <td>水平扩展</td>
        <td>垂直扩展</td>
        <td>-</td>
      </tr>
      <tr>
        <td>更新方式</td>
        <td>局部更新</td>
        <td>整体更新</td>
        <td>-</td>
      </tr>
    </table>
  </div>
  <div class="slide-footer">1 / 5</div>
</div>
```

```css
.slide.table {
  background: var(--bg);
  padding: 60px;
  display: flex;
  flex-direction: column;
}
.slide.table .slide-header {
  padding-bottom: 20px;
}
.slide.table .slide-header h1 {
  font-size: 64px;
  color: var(--title);
  border-bottom: 3px solid var(--accent);
  margin: 0;
  width: 100%;
}
.slide.table .slide-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.slide.table table {
  flex: 1;
  width: 100%;
  border-collapse: collapse;
  font-size: 32px;
}
.slide.table th {
  background: var(--accent);
  color: #fff;
  padding: 20px 24px;
  text-align: left;
  font-weight: bold;
}
.slide.table td {
  background: var(--surface);
  color: var(--text);
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}
.slide.table tr:last-child td {
  border-bottom: none;
}
.slide.table tr {
  flex: 1;
}
.slide.table tr td,
.slide.table tr th {
  flex: 1;
  vertical-align: middle;
}
.slide.table .slide-footer {
  padding-top: 20px;
  font-size: 20px;
  color: var(--muted);
  text-align: right;
}
```

---

## 主题配置

根据选定的主题，CSS 变量使用对应的值：

### tech（科技风格）
```css
:root {
  --bg: #0D1117;
  --title: #FFFFFF;
  --text: #58A6FF;
  --accent: #58A6FF;
  --muted: #8B949E;
  --surface: #161B22;
}
```

### simple（简约商务）
```css
:root {
  --bg: #FFFFFF;
  --title: #1A1A1A;
  --text: #4A4A4A;
  --accent: #0066CC;
  --muted: #999999;
  --surface: #F5F5F5;
}
```

### minimal（极简）
```css
:root {
  --bg: #FAFAFA;
  --title: #000000;
  --text: #333333;
  --accent: #000000;
  --muted: #AAAAAA;
  --surface: #FFFFFF;
}
```

---

## CSS 核心规范

**必须遵守以下规范，否则页面无法正确渲染：**

### 1. 填满（flex: 1）

- `.slide-body` 有 `flex: 1`，占据 header 之后的所有可用高度
- `.row`（cards-top）有 `flex: 1`，各行平均分配高度
- `.card`（cards-left）有 `flex: 1` 和 `width: 100%`，卡片填满所在列
- `.card`（cards-top 单卡片行）不需要额外设置，依赖父级 `.row { flex: 1 }`
- `.card`（cards-top 多卡片行）用 `width: 50%` 或 `33%`，**不用** `flex: 1`

### 2. padding 统一

- 页面容器：`.slide { padding: 60px; }`
- header 下边框：`.slide-header h1 { border-bottom: 3px solid var(--accent); margin: 0; width: 100%; }`
- header padding：`padding-bottom: 20px`（不是 margin-bottom）
- footer padding：`padding-top: 20px`

### 3. 卡片 width: 100%

- **所有 `.card` 必须有 `width: 100%`**
- 多卡片行中用 `width: 50%` 或 `width: 33%` 控制单卡宽度

### 4. cards-left 两列宽度

- `.left` 和 `.right` 都是 `flex: 1`（各 50%）
- gap 通过父级 `.slide-body { gap: 20px; }` 控制

### 5. 文字垂直居中

- `.line { height: 100%; justify-content: center; }`
- `.line .main { display: flex; align-items: center; }`
- 对于 `comparison`、`process`、`cards-*`、`grid-*`、`table`、`hero-statement`，先保证容器满高，再让文字栈回到视觉中心；不要只靠上边距假装居中。

### 6. 序号和标题对齐

- toc 的 `.line .num { width: 100px; flex-shrink: 0; }`
- 子弹符号：`.bullet { width: 32-50px; flex-shrink: 0; }`

---

## 自检清单

生成 HTML 后逐项检查：

- [ ] `.slide-body { flex: 1 }` 存在
- [ ] `.card { width: 100% }` 存在（cards-left 所有 card，cards-top 单卡 card）
- [ ] cards-top 多卡片行 `.card { width: 50% }` 或 `{ width: 33% }`（不用 flex: 1）
- [ ] cards-left `.left` 和 `.right` 都有 `flex: 1`
- [ ] `.slide-header { padding-bottom: 20px }` 存在
- [ ] `.slide-footer { padding-top: 20px }` 存在
- [ ] `.slide-header h1 { border-bottom: 3px solid var(--accent); margin: 0; width: 100%; }` 存在
- [ ] 字号符合布局定义（h1: 64px，cardTitle: 32-48px，sub: 20-28px）
- [ ] 颜色变量正确（使用 CSS 变量，不是硬编码）
- [ ] 每页不超过 5 个要点
- [ ] 页面数量 4-8 页
- [ ] comparison/process/cards/grid 的卡片内容垂直居中
- [ ] table 没有只缩在上半部分
- [ ] hero 长标题按预期宽度换行，不靠缩字号凑
- [ ] `output/images/resources` 等临时资源缓存已清理

---

## 文件输出

生成的所有 HTML 文件保存到 `output/` 目录，命名格式：

```
output/
├── slide-01-cover.html
├── slide-02-toc.html
├── slide-03-content-col.html
├── slide-04-cards-left-1-right-2.html
├── slide-05-grid-cols-2.html
├── slide-06-timeline.html
└── slide-07-ending.html
```

---

## 调用渲染脚本

生成完所有 HTML 后，执行：

```bash
python scripts/run_pipeline.py --allow-warn
```

或者先单独渲染、再打包：

```bash
python src/render.py
python src/build_pptx.py
```

默认推荐先用 `--allow-warn` 跑完整流程；当你想把 warning 视为失败时，改用：

```bash
python scripts/run_pipeline.py --stop-on-warn
```

截图输出到 `output/images/`，PPT 输出到 `output/presentation.pptx`。
