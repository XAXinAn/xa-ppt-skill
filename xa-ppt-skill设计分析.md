# xa-ppt-skill 设计系统详细设计

## 1. 设计理念

```
约束边界内，AI 自由发挥
```

| 层级 | 定义什么 | AI 能做什么 |
|------|----------|-------------|
| 主题 | 颜色、字体范围、规则 | 具体的样式值、装饰选择 |
| 布局 | 区域结构 | 区域内的具体排版 |
| 组件 | 可用元素 | 元素的具体样式、组合方式 |

---

## 2. 主题定义 (Theme)

### 2.1 主题配置结构

```json
{
  "id": "tech",
  "name": "科技风格",
  "description": "适合技术分享、架构展示",

  "colors": {
    "background": "#0D1117",
    "title": "#FFFFFF",
    "heading": "#E6EDF3",
    "text": "#58A6FF",
    "accent": "#58A6FF",
    "accentSecondary": "#79C0FF",
    "muted": "#8B949E",
    "divider": "#30363D",
    "surface": "#161B22"
  },

  "typography": {
    "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif",
    "titleSize": { "min": 36, "max": 48, "default": 44 },
    "headingSize": { "min": 24, "max": 32, "default": 28 },
    "bodySize": { "min": 16, "max": 24, "default": 20 },
    "smallSize": { "min": 14, "max": 18, "default": 16 }
  },

  "spacing": {
    "unit": 8,
    "containerPadding": 80,
    "sectionGap": 40,
    "elementGap": 16
  },

  "rules": [
    "背景必须使用深色",
    "标题必须醒目，与背景形成强对比",
    "强调色用于关键信息",
    "内容保持简洁，每页不超过 5 个要点",
    "禁止使用超过 3 种颜色"
  ],

  "forbidden": [
    "不要使用浅色背景",
    "不要使用黑体、宋体以外的装饰字体",
    "不要堆砌文字"
  ]
}
```

### 2.2 内置主题

#### tech（科技风格）
```json
{
  "id": "tech",
  "colors": {
    "background": "#0D1117",
    "title": "#FFFFFF",
    "heading": "#E6EDF3",
    "text": "#58A6FF",
    "accent": "#58A6FF",
    "accentSecondary": "#79C0FF",
    "muted": "#8B949E",
    "divider": "#30363D",
    "surface": "#161B22"
  }
}
```

#### simple（简约商务）
```json
{
  "id": "simple",
  "colors": {
    "background": "#FFFFFF",
    "title": "#1A1A1A",
    "heading": "#333333",
    "text": "#4A4A4A",
    "accent": "#0066CC",
    "accentSecondary": "#3399FF",
    "muted": "#999999",
    "divider": "#E5E5E5",
    "surface": "#F5F5F5"
  }
}
```

#### minimal（极简）
```json
{
  "id": "minimal",
  "colors": {
    "background": "#FAFAFA",
    "title": "#000000",
    "heading": "#222222",
    "text": "#333333",
    "accent": "#000000",
    "accentSecondary": "#555555",
    "muted": "#AAAAAA",
    "divider": "#DDDDDD",
    "surface": "#FFFFFF"
  }
}
```

---

## 3. 布局定义 (Layout)

### 3.1 布局配置结构

```json
{
  "id": "title-content",
  "name": "标题+内容",
  "description": "最常用的布局，适合单主题展开",

  "zones": {
    "HEADER": {
      "position": "top",
      "height": "18%",
      "elements": ["h1", "h2"]
    },
    "BODY": {
      "position": "below-header",
      "elements": ["paragraph", "list", "code", "image", "quote"]
    }
  },

  "constraints": {
    "HEADER": {
      "align": "left",
      "paddingBottom": 24,
      "border": { "type": "line", "color": "accent", "width": 2 }
    },
    "BODY": {
      "align": "left",
      "paddingTop": 32
    }
  },

  "rules": [
    "HEADER 占据顶部区域",
    "BODY 占据剩余空间",
    "内容左对齐"
  ]
}
```

### 3.2 布局分类

按语义分为五类：

| 类型 | 布局 | 说明 |
|------|------|------|
| 封面 | `cover` | 大标题居中，无内容，无页码 |
| 结尾 | `ending` | 结束页，无内容，无页码 |
| 目录 | `toc` | 目录页，列出章节 |
| 正文 | `content-row` | 横向单行卡片 |
| 正文 | `content-col` | 纵向单列卡片 |
| 正文 | `cards-top-1-bottom-2` | 上下卡片，上1下2 |
| 正文 | `cards-top-1-bottom-3` | 上下卡片，上1下3 |
| 正文 | `cards-top-2-bottom-1` | 上下卡片，上2下1 |
| 正文 | `cards-top-2-bottom-3` | 上下卡片，上2下3 |
| 正文 | `cards-top-3-bottom-1` | 上下卡片，上3下1 |
| 正文 | `cards-top-3-bottom-2` | 上下卡片，上3下2 |
| 正文 | `cards-left-1-right-2` | 左右卡片，左1右2 |
| 正文 | `cards-left-1-right-3` | 左右卡片，左1右3 |
| 正文 | `cards-left-2-right-1` | 左右卡片，左2右1 |
| 正文 | `cards-left-2-right-3` | 左右卡片，左2右3 |
| 正文 | `cards-left-3-right-1` | 左右卡片，左3右1 |
| 正文 | `cards-left-3-right-2` | 左右卡片，左3右2 |
| 正文 | `grid` | 网格布局（2列/3列，固定2行） |
| 正文 | `timeline` | 时间线布局 |
| 正文 | `table` | 表格布局 |

---

#### cover（封面）
```
┌────────────────────────────────────┐
│                                     │
│           微服务架构                 │  ← h1: 88px
│           技术分享                   │  ← h2: 44px (可选)
│                                     │
└────────────────────────────────────┘
```

```json
{
  "id": "cover",
  "type": "cover",
  "name": "封面",
  "zones": {
    "center": {
      "position": "center"
    }
  },
  "typography": {
    "h1": { "size": 88, "weight": "bold" },
    "h2": { "size": 44, "weight": "normal" }
  },
  "footer": { "visible": false }
}
```

#### ending（结尾）
```
┌────────────────────────────────────┐
│                                     │
│           谢 谢 观 看                │  ← h1: 72px
│                                     │
└────────────────────────────────────┘
```

```json
{
  "id": "ending",
  "type": "ending",
  "name": "结尾",
  "zones": {
    "center": {
      "position": "center"
    }
  },
  "typography": {
    "h1": { "size": 72, "weight": "bold" }
  },
  "footer": { "visible": false }
}
```

#### toc（目录）
```
┌────────────────────────────────────┐
│  SLIDE_HEADER: 目 录               │  ← 80px
│  ════════════════════════          │
│  01  概述                          │
│  02  服务拆分                      │  ← line: flex:1
│  03  API 网关                      │
│  04  容器化部署                    │
│  05  总结                          │
│                              1/5  │  ← footer: 50px
└────────────────────────────────────┘
```

```json
{
  "id": "toc",
  "type": "toc",
  "name": "目录",
  "padding": 60,
  "zones": {
    "slide-header": {
      "height": 80,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "elements": ["line"],
      "distribution": "flex-fill"
    },
    "slide-footer": {
      "height": 50,
      "align": "right"
    }
  },
  "typography": {
    "h1": { "size": 64 },
    "line": { "size": 56 },
    "footer": { "size": 20 }
  },
  "constraints": {
    "lineCount": { "min": 2, "max": 8 }
  }
}
```

#### timeline（时间线）
```
┌────────────────────────────────────┐
│  页面标题                           │  ← header
│  ════════════════════════          │
│                                     │
│  ●───────────●───────────●         │  ← 时间线
│                                     │
│  单体时代    微服务     云原生      │
│  集中式      分布式      容器化      │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "timeline",
  "type": "content",
  "name": "时间线",
  "padding": 60,
  "zones": {
    "slide-header": {
      "height": 80,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "elements": ["timeline"],
      "distribution": "center"
    },
    "slide-footer": {
      "height": 50,
      "align": "right"
    }
  },
  "typography": {
    "h1": { "size": 64 },
    "nodeTitle": { "size": 48 },
    "nodeDesc": { "size": 28 },
    "footer": { "size": 20 }
  },
  "constraints": {
    "nodeCount": { "min": 3, "max": 5 }
  }
}
```

#### table（表格）
```
┌────────────────────────────────────┐
│  页面标题                           │  ← header
│  ════════════════════════          │
│  ┌───────┬───────┬───────┬─────┐  │
│  │ 名称  │ 微服务│ 单体  │ 说明│  │
│  ├───────┼───────┼───────┼─────┤  │
│  │ 部署  │ 独立  │ 统一  │     │  │
│  │ 扩展  │ 水平  │ 垂直  │     │  │
│  │ 更新  │ 局部  │ 整体  │     │  │
│  └───────┴───────┴───────┴─────┘  │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "table",
  "type": "content",
  "name": "表格",
  "padding": 60,
  "zones": {
    "slide-header": {
      "height": 80,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "elements": ["table"]
    },
    "slide-footer": {
      "height": 50,
      "align": "right"
    }
  },
  "typography": {
    "h1": { "size": 64 },
    "th": { "size": 32 },
    "td": { "size": 28 },
    "footer": { "size": 20 }
  },
  "constraints": {
    "columns": { "min": 2, "max": 5 },
    "rows": { "min": 2, "max": 6 }
  }
}
```

#### content-row（横向正文）
```
┌────────────────────────────────────┐
│  页面标题                           │  ← header
│  ════════════════════════          │
│  ┌───────┐ ┌───────┐ ┌───────┐    │
│  │ ▸ 要点│ │ ▸ 要点│ │ ▸ 要点│    │  ← 横向排列
│  │   描述│ │   描述│ │   描述│    │
│  └───────┘ └───────┘ └───────┘    │
│                              1/5   │  ← footer
└────────────────────────────────────┘
```

```json
{
  "id": "content-row",
  "type": "content",
  "name": "横向正文",
  "padding": 60,
  "zones": {
    "slide-header": {
      "height": 80,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "elements": ["card"],
      "direction": "row",
      "distribution": "flex-fill"
    },
    "slide-footer": {
      "height": 50,
      "align": "right"
    }
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 48 },
    "cardSub": { "size": 28 },
    "footer": { "size": 20 }
  },
  "constraints": {
    "cardCount": { "min": 3, "max": 5 }
  }
}
```

#### content-col（纵向正文）
```
┌────────────────────────────────────┐
│  页面标题                           │  ← header
│  ════════════════════════          │
│  ┌─────────────────────────────┐   │
│  │ ▸ 要点1                      │   │
│  │   描述                        │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ ▸ 要点2                      │   │  ← 纵向排列
│  │   描述                        │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ ▸ 要点3                      │   │
│  │   描述                        │   │
│  └─────────────────────────────┘   │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "content-col",
  "type": "content",
  "name": "纵向正文",
  "padding": 60,
  "zones": {
    "slide-header": {
      "height": 80,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "elements": ["card"],
      "direction": "col",
      "justifyContent": "space-between",
      "padding": "20px 0"
    },
    "slide-footer": {
      "height": 50,
      "align": "right"
    }
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 48 },
    "cardSub": { "size": 28 },
    "footer": { "size": 20 }
  },
  "constraints": {
    "cardCount": { "min": 3, "max": 5 }
  }
}
```

#### grid-cols-2（网格布局 2列2行）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 服务拆分│  │ ▸ API网关 │       │
│  │   DDD    │  │  统一入口  │       │
│  └───────────┘  └───────────┘       │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 容器化  │  │ ▸ 编排    │       │
│  │   Docker │  │   K8s    │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "grid-cols-2",
  "type": "content",
  "name": "网格布局-2列2行",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "grid",
      "gridTemplateColumns": "repeat(2, 1fr)",
      "gridTemplateRows": "repeat(2, 1fr)",
      "gap": 40,
      "padding": "20px 0"
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "24px 30px",
    "borderRadius": 12,
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "center"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 48 },
    "cardSub": { "size": 28 },
    "footer": { "size": 20 }
  }
}
```

#### grid-cols-3（网格布局 3列2行）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────┐  ┌───────┐  ┌───────┐   │
│  │▸ 服务 │  │▸ API  │  │▸服务  │   │
│  │  拆分 │  │  网关  │  │  通信 │   │  ← 3列
│  └───────┘  └───────┘  └───────┘   │
│  ┌───────┐  ┌───────┐  ┌───────┐   │
│  │▸ 容器化│  │▸ 编排  │  │▸ 监控  │   │
│  └───────┘  └───────┘  └───────┘   │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "grid-cols-3",
  "type": "content",
  "name": "网格布局-3列2行",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "grid",
      "gridTemplateColumns": "repeat(3, 1fr)",
      "gridTemplateRows": "repeat(2, 1fr)",
      "gap": 40,
      "padding": "20px 0"
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "24px 30px",
    "borderRadius": 12,
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "center"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 48 },
    "cardSub": { "size": 28 },
    "footer": { "size": 20 }
  }
}
```

#### cards-top-1-bottom-2（上下卡片 上1下2）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌─────────────────────────────┐   │
│  │ ▸ 单体架构                   │   │  ← 上排1个
│  │   传统集中式架构             │   │
│  └─────────────────────────────┘   │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 微服务  │  │ ▸ 云原生  │       │  ← 下排2个
│  │   分布式  │  │   容器化  │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-top-1-bottom-2",
  "type": "content",
  "name": "上下卡片-上1下2",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "top-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "bottom-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "width": "100%"
  },
  "cardMulti": {
    "width": "50%",
    "flex": "none"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 40 },
    "cardSub": { "size": 24 },
    "footer": { "size": 20 }
  }
}
```

#### cards-top-1-bottom-3（上下卡片 上1下3）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌─────────────────────────────┐   │
│  │ ▸ 开发框架                   │   │  ← 上排1个
│  │   Spring Boot / Django       │   │
│  └─────────────────────────────┘   │
│  ┌─────────┐ ┌─────────┐ ┌──────┐ │
│  │ ▸ 容器化│ │ ▸ 编排  │ │▸ 监控│ │  ← 下排3个
│  │   Docker│ │   K8s   │ │Prom. │ │
│  └─────────┘ └─────────┘ └──────┘ │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-top-1-bottom-3",
  "type": "content",
  "name": "上下卡片-上1下3",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "top-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "bottom-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "width": "100%"
  },
  "cardTriple": {
    "width": "33%",
    "flex": "none"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-top-2-bottom-1（上下卡片 上2下1）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 单体部署│  │▸ 微服务部署│      │  ← 上排2个
│  │   整体打包│  │   独立发布 │       │
│  └───────────┘  └───────────┘       │
│  ┌─────────────────────────────┐   │
│  │ ▸ 云原生部署                 │   │  ← 下排1个
│  │   容器化 + Kubernetes        │   │
│  └─────────────────────────────┘   │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-top-2-bottom-1",
  "type": "content",
  "name": "上下卡片-上2下1",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "top-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "bottom-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "width": "100%"
  },
  "cardMulti": {
    "width": "50%",
    "flex": "none"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 40 },
    "cardSub": { "size": 24 },
    "footer": { "size": 20 }
  }
}
```

#### cards-top-2-bottom-3（上下卡片 上2下3）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 单体架构│  │▸ 分层架构 │       │  ← 上排2个
│  │   整体部署│  │   模块化  │       │
│  └───────────┘  └───────────┘       │
│  ┌─────────┐ ┌─────────┐ ┌──────┐ │
│  │ ▸ 微服务│ │ ▸ 容器化 │ │▸ 编排│ │  ← 下排3个
│  │   服务拆分│ │   Docker│ │  K8s │ │
│  └─────────┘ └─────────┘ └──────┘ │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-top-2-bottom-3",
  "type": "content",
  "name": "上下卡片-上2下3",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "top-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "bottom-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "width": "100%"
  },
  "cardMulti": {
    "width": "50%",
    "flex": "none"
  },
  "cardTriple": {
    "width": "33%",
    "flex": "none"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-top-3-bottom-1（上下卡片 上3下1）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌─────────┐ ┌─────────┐ ┌──────┐ │
│  │ ▸ 服务拆分│ │ ▸ API网关│ │▸服务通信││ ← 上排3个
│  │   DDD  │ │  统一入口 │ │HTTP/gRPC││
│  └─────────┘ └─────────┘ └──────┘ │
│  ┌─────────────────────────────┐   │
│  │ ▸ 云原生部署                 │   │  ← 下排1个
│  │   容器化 + Kubernetes        │   │
│  └─────────────────────────────┘   │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-top-3-bottom-1",
  "type": "content",
  "name": "上下卡片-上3下1",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "top-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "bottom-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "width": "100%"
  },
  "cardTriple": {
    "width": "33%",
    "flex": "none"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-top-3-bottom-2（上下卡片 上3下2）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌─────────┐ ┌─────────┐ ┌──────┐ │
│  │ ▸ 服务拆分│ │ ▸ API网关│ │▸服务通信││ ← 上排3个
│  │   DDD  │ │  统一入口 │ │HTTP/gRPC││
│  └─────────┘ └─────────┘ └──────┘ │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 容器化  │  │ ▸ 编排    │       │  ← 下排2个
│  │   Docker │  │   K8s    │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-top-3-bottom-2",
  "type": "content",
  "name": "上下卡片-上3下2",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "top-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "bottom-row": {
      "display": "flex",
      "gap": 20,
      "flex": 1
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "width": "100%"
  },
  "cardTriple": {
    "width": "33%",
    "flex": "none"
  },
  "cardMulti": {
    "width": "50%",
    "flex": "none"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-left-1-right-2（左右卡片 左1右2）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 单体架构│  │ ▸ 微服务  │       │
│  │   传统架构│  │ ▸ 云原生  │       │  ← 左1右2
│  │           │  │   分布式  │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-left-1-right-2",
  "type": "content",
  "name": "左右卡片-左1右2",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "gap": 20
    },
    "left-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "right-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "flex": 1,
    "width": "100%"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-left-1-right-3（左右卡片 左1右3）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 统一架构│  │ ▸ 独立部署 │       │
│  │   整体视图│  │ ▸ 技术多样 │       │  ← 左1右3
│  │           │  │ ▸ 故障隔离 │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-left-1-right-3",
  "type": "content",
  "name": "左右卡片-左1右3",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "gap": 20
    },
    "left-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "right-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "flex": 1,
    "width": "100%"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-left-2-right-1（左右卡片 左2右1）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 单体部署│  │ ▸ 微服务  │       │
│  │ ▸ 统一发布│  │   独立部署 │       │  ← 左2右1
│  │   整体更新│  │   架构    │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-left-2-right-1",
  "type": "content",
  "name": "左右卡片-左2右1",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "gap": 20
    },
    "left-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "right-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "flex": 1,
    "width": "100%"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-left-2-right-3（左右卡片 左2右3）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 单体架构│  │ ▸ 微服务  │       │
│  │ ▸ 分层架构│  │ ▸ 容器化  │       │  ← 左2右3
│  │   模块化  │  │ ▸ 编排    │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-left-2-right-3",
  "type": "content",
  "name": "左右卡片-左2右3",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "gap": 20
    },
    "left-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "right-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "flex": 1,
    "width": "100%"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-left-3-right-1（左右卡片 左3右1）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 服务注册│  │           │       │
│  │ ▸ 负载均衡│  │ ▸ 云原生  │       │  ← 左3右1
│  │ ▸ 熔断器  │  │   架构   │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-left-3-right-1",
  "type": "content",
  "name": "左右卡片-左3右1",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "gap": 20
    },
    "left-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "right-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "flex": 1,
    "width": "100%"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

#### cards-left-3-right-2（左右卡片 左3右2）
```
┌────────────────────────────────────┐
│  页面标题                           │
│  ════════════════════════          │
│  ┌───────────┐  ┌───────────┐       │
│  │ ▸ 后端框架│  │ ▸ 容器    │       │
│  │ ▸ 前端框架│  │ ▸ 编排    │       │  ← 左3右2
│  │ ▸ 数据库  │  │           │       │
│  └───────────┘  └───────────┘       │
│                              1/5   │
└────────────────────────────────────┘
```

```json
{
  "id": "cards-left-3-right-2",
  "type": "content",
  "name": "左右卡片-左3右2",
  "padding": 60,
  "zones": {
    "slide-header": {
      "paddingBottom": 20,
      "elements": ["h1"],
      "border": { "type": "line", "color": "accent" }
    },
    "slide-body": {
      "flex": 1,
      "display": "flex",
      "gap": 20
    },
    "left-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "right-column": {
      "flex": 1,
      "display": "flex",
      "flexDirection": "column",
      "gap": 20
    },
    "slide-footer": {
      "paddingTop": 20,
      "align": "right"
    }
  },
  "card": {
    "background": "surface",
    "padding": "20px 30px",
    "borderRadius": 12,
    "flex": 1,
    "width": "100%"
  },
  "typography": {
    "h1": { "size": 64 },
    "cardTitle": { "size": 32 },
    "cardSub": { "size": 20 },
    "footer": { "size": 20 }
  }
}
```

---

## 4. 组件定义 (Component)

### 4.1 组件类型

| 类型 | 组件 | 说明 |
|------|------|------|
| 文本 | `h1`, `h2`, `h3` | 标题层级 |
| 文本 | `p` | 段落 |
| 文本 | `text` | 短文本/标签 |
| 列表 | `ul`, `ol` | 无序/有序列表 |
| 代码 | `code`, `pre` | 内联/块级代码 |
| 媒体 | `img` | 图片 |
| 媒体 | `chart` | 图表占位 |
| 引用 | `quote` | 引用块 |
| 布局 | `divider` | 分隔线 |
| 布局 | `card` | 卡片容器 |
| 布局 | `flex` | 弹性容器 |
| 布局 | `grid` | 网格容器 |

### 4.2 组件样式约束

#### h1
```json
{
  "tag": "h1",
  "size": "36-48px",
  "weight": "bold",
  "color": "title",
  "margin": "0 0 16px 0"
}
```

#### ul（列表）
```json
{
  "tag": "ul",
  "style": "none",
  "itemGap": "12-20px",
  "itemIndent": "20-24px",
  "itemBullet": {
    "tech": "▸ 或 ●",
    "simple": "— 或 •",
    "minimal": "·"
  }
}
```

#### quote
```json
{
  "tag": "blockquote",
  "padding": "20px 24px",
  "borderLeft": "4px solid accent",
  "background": "surface",
  "fontStyle": "italic",
  "color": "heading"
}
```

#### card
```json
{
  "tag": "div",
  "background": "surface",
  "padding": "24-32px",
  "borderRadius": "8-12px",
  "border": "1px solid divider"
}
```

---

## 5. 饱满度保障机制

排版饱满 = 内容占据页面主要区域，留白合理。

### 5.1 饱满度定义

```
┌────────────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│  ← 上方留白 ≤ 10%
│░░░  标  题  内  容  占  满  ░░░░░░░░│
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│  ← 下划线装饰
│                                     │
│  ▸ 要点1                            │  ← 内容左对齐
│  ▸ 要点2       ▸ 要点3              │  ← 要点均匀分布
│  ▸ 要点4                            │
│                                     │
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│  ← 下方留白 ≤ 10%
└────────────────────────────────────┘
```

### 5.2 布局比例约束

```json
{
  "layout": "title-content",
  "fullness": {
    "HEADER": {
      "height": "15-20%",
      "contentMinHeight": "80%"     // 标题内容至少占 HEADER 的 80%
    },
    "BODY": {
      "marginTop": "max 8%",        // BODY 顶部留白不超过 8%
      "marginBottom": "max 8%",     // BODY 底部留白不超过 8%
      "contentMinHeight": "70%"     // 内容占据 BODY 至少 70%
    }
  }
}
```

### 5.3 边距约束

```json
{
  "spacing": {
    "containerPadding": {
      "horizontal": { "min": 60, "max": 100 },
      "vertical": { "min": 40, "max": 80 }
    }
  }
}
```

| 边距类型 | 约束范围 | 说明 |
|----------|----------|------|
| 左边距 | 60-100px | 不能太少显得拥挤 |
| 右边距 | 60-100px | 与左边距对称 |
| 上边距 | 40-80px | 配合 HEADER 高度 |
| 下边距 | 40-80px | 配合 BODY 内容 |

### 5.4 字号下限约束

```json
{
  "typography": {
    "bodySize": { "min": 18, "default": 22 },
    "listItemSize": { "min": 18, "default": 20 },
    "quoteSize": { "min": 20, "default": 24 }
  }
}
```

字号不能小于 18px，避免内容太单薄。

### 5.5 内容填充规则

```json
{
  "fullness": {
    "contentRules": [
      "BODY 区域必须有实际内容",
      "列表至少 2 项，最多 5 项",
      "每项文字不少于 4 个字",
      "要点使用视觉标记（如 ▸、●、—）",
      "卡片必须有标题 + 描述内容",
      "代码块必须有至少 3 行"
    ],
    "forbidden": [
      "禁止只有标题没有内容",
      "禁止单行孤零零的要点",
      "禁止留大片空白"
    ]
  }
}
```

### 5.6 视觉分布引导

```json
{
  "layout": "title-content",
  "visualDistribution": {
    "vertical": {
      "HEADER": { "align": "bottom", "grow": false },
      "BODY": { "align": "top", "grow": true }
    },
    "horizontal": {
      "items": { "align": "left", "maxWidth": "90%" }
    }
  }
}
```

| 规则 | 说明 |
|------|------|
| HEADER 贴顶 | 标题靠上，不居中漂浮 |
| BODY 贴标题 | 内容紧跟标题，不留大片空白 |
| 要点均匀分布 | 用 `gap` 控制要点间距 |
| 避免居中漂浮 | 内容左对齐，不左右居中 |

### 5.7 饱满度自检清单

AI 生成 HTML 后检查：

- [ ] 布局比例符合约束（HEADER 15-20%）
- [ ] 边距在允许范围内（左右 60-100px）
- [ ] 字号不小于下限（18px）
- [ ] BODY 区域有实际内容
- [ ] 列表有 2-5 项
- [ ] 没有大片留白
- [ ] 内容左对齐，不漂浮

### 5.8 填充不足时的补救措施

```javascript
function ensureFullness(slide) {
  const body = slide.querySelector('[data-zone="BODY"]');
  const contentRatio = getContentHeight(body) / body.clientHeight;
  
  if (contentRatio < 0.7) {
    // 补救措施
    if (hasOnlyList()) {
      // 列表项太少 → 拆分为更细的要点
      expandListItems(slide);
    }
    if (fontSizeUnderLimit()) {
      // 字号太小 → 适当增大
      increaseFontSize(slide);
    }
    if (hasLargeGaps()) {
      // 间距太大 → 减小间距或增加内容
      adjustSpacing(slide);
    }
  }
}
```

---

## 6. 主题 × 布局 × 组件 配合

### 6.1 布局选择规则

| 内容类型 | 推荐布局 |
|----------|----------|
| 封面页 | `cover` |
| 结尾页 | `ending` |
| 目录页 | `toc` |
| 横向单行要点 | `content-row` |
| 纵向单列要点 | `content-col` |
| 上下分栏（对比） | `cards-top-*-bottom-*` |
| 左右分栏（对比） | `cards-left-*-right-*` |
| 网格2×2 | `grid-cols-2` |
| 网格3×2 | `grid-cols-3` |
| 时间线 | `timeline` |
| 表格 | `table` |

### 6.2 主题匹配规则

```json
{
  "rules": [
    {
      "condition": ["技术", "架构", "系统", "代码", "开发", "AI", "服务器", "网络", "微服务", "容器"],
      "theme": "tech"
    },
    {
      "condition": ["商务", "汇报", "介绍", "计划", "总结", "年度"],
      "theme": "simple"
    },
    {
      "condition": ["极简", "纯展示", "艺术"],
      "theme": "minimal"
    },
    {
      "condition": "默认",
      "theme": "simple"
    }
  ]
}
```

### 6.3 页面类型示例

```
┌─────────────────────────────────────────────────┐
│  封面页 (cover)                                  │
│  - 大标题居中，无内容                            │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  目录页 (toc)                                    │
│  - 章节列表                                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  正文页 (content-row)                            │
│  - 标题 + 横向单行卡片                           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  正文页 (content-col)                            │
│  - 标题 + 纵向单列卡片                           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  对比页 (cards-top-1-bottom-2)                  │
│  - 上1下2 上下分栏对比                           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  对比页 (cards-left-1-right-2)                   │
│  - 左1右2 左右分栏对比                           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  网格页 (grid-cols-3)                            │
│  - 3列2行网格布局                               │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  时间线页 (timeline)                             │
│  - 时间线展示                                   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  表格页 (table)                                  │
│  - 表格数据展示                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  结尾页 (ending)                                 │
│  - 谢谢观看                                      │
└─────────────────────────────────────────────────┘
```

---

## 7. 完整配置结构

```json
{
  "designSystem": {
    "version": "1.0",
    
    "themes": {
      "tech": { ... },
      "simple": { ... },
      "minimal": { ... }
    },
    
    "layouts": {
      "cover": { ... },
      "ending": { ... },
      "toc": { ... },
      "content-row": { ... },
      "content-col": { ... },
      "cards-top-1-bottom-2": { ... },
      "cards-top-1-bottom-3": { ... },
      "cards-top-2-bottom-1": { ... },
      "cards-top-2-bottom-3": { ... },
      "cards-top-3-bottom-1": { ... },
      "cards-top-3-bottom-2": { ... },
      "cards-left-1-right-2": { ... },
      "cards-left-1-right-3": { ... },
      "cards-left-2-right-1": { ... },
      "cards-left-2-right-3": { ... },
      "cards-left-3-right-1": { ... },
      "cards-left-3-right-2": { ... },
      "grid-cols-2": { ... },
      "grid-cols-3": { ... },
      "timeline": { ... },
      "table": { ... }
    },
    
    "components": {
      "h1": { ... },
      "h2": { ... },
      "ul": { ... },
      "ol": { ... },
      "p": { ... },
      "code": { ... },
      "pre": { ... },
      "img": { ... },
      "quote": { ... },
      "divider": { ... },
      "card": { ... }
    },
    
    "themeMatchRules": [ ... ],
    
    "layoutSelectRules": [ ... ]
  }
}
```

---

## 8. AI 生成 HTML 的指导原则

1. **读取主题配置** → 知道颜色范围、字号范围、规则
2. **分析内容结构** → 选择合适的布局
3. **匹配主题** → 根据关键词选择主题
4. **生成 HTML** → 组合组件，应用主题约束
5. **自检** → 确保符合主题规则

### 自检清单

- [ ] 背景色符合主题
- [ ] 字号在允许范围内
- [ ] 颜色不超过 3 种
- [ ] 每页不超过 5 个要点
- [ ] 没有使用禁止的样式

---

## 9. 目录结构

```
xa-ppt-skill/
├── design-system/
│   ├── design-system.json       # 完整配置
│   ├── themes/
│   │   ├── tech.json
│   │   ├── simple.json
│   │   └── minimal.json
│   ├── layouts/
│   │   ├── title-content.json
│   │   ├── title-subtitle-content.json
│   │   ├── two-column.json
│   │   ├── grid-2x2.json
│   │   ├── center.json
│   │   └── fullscreen.json
│   └── components/
│       └── components.json
├── .claude/
│   └── skills/
│       └── xa-ppt/
│           └── skill.md
├── src/
│   ├── render.py
│   └── build_pptx.py
├── output/
└── requirements.txt
```
## 10. 本次实现约束

为了保证生成结果可重复、可验证，本次代码修复遵循以下约束：

1. 以仓库根目录作为所有输入输出的基准路径，不依赖启动时的当前工作目录
2. 生成 HTML、渲染图片、组装 PPT 三个阶段都只消费本阶段刚生成的产物
3. 模板渲染器需要支持一层以上的嵌套 section，以覆盖表格这类结构化布局

## 11. 设计系统回流约定

后续如果再遇到类似问题，默认先改设计系统主配置，再改布局文件。

1. 版式尺寸统一改 `design-system.json` 的 `presentationDefaults`
2. 渲染边界统一改 `renderingDefaults`
3. 具体布局只保留少量例外，不再重复写一套自己的基线值
4. 若再出现字号不统一、截图白边、文字偏上、案例页没有“垂直居中 + 左对齐”等问题，优先更新 `regressionRules` 与 `scripts/validate_design_system.py`，再修单页布局
